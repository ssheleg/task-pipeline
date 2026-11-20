report: checkup-healer · project task-pipeline · 2026-11-20 · spec · status proposed

# Spec: `/task-pipeline checkup --healer` and the `healer-report/1` contract

Date: 2026-11-20. Owner: this repository. Asked by: the agents database, board
request `1ace85b7` (design D-86, «лекарь (перепроверщик)»), deadline 2026-12-04.
This file is the contract the caller can build against now; the mode itself ships
in a later release (see *Delivery*).

## Objective

A healer session re-verifies what already landed in a project, with no task in
flight, and leaves a machine-readable report that the Fabric CEO harness starts and
the process manager reads. It reuses what exists: `checkup` (the unconfirmed list,
`references/exposure.md`) and the blind verifier tiers unit, seam and product
(`references/certification.md`, eight-key tier reports). Nothing new decides a
verdict; the mode only chooses what to re-read and writes one report.

## What the mode does

1. **Scope.** Takes `--since <git-rev|date>` (default: the last healer report's
   `head`, else the last 24 h of commits on the default branch) and computes the
   changed units: the commits, their merged PRs, and the run ledgers that shipped
   them. A project with no commits in the window writes a report with
   `status: "idle"` and stops; it never invents work.
2. **Checkup first.** Runs the existing `checkup` read (exposure line, abandoned
   runs, open board rows by computed priority) and copies its counts into the
   report unchanged.
3. **Blind re-verification.** For each changed unit, spawns the `verifier-unit`,
   `verifier-seam` and `verifier-product` tiers blind (diff, requirement and check
   only; no author notes). The tier runs on a different model family than the
   unit's author when the harness offers one; when it does not, the report says
   `cross_family: false` for that unit instead of claiming it.
4. **Regression to task.** A tier finding at severity `blocker`, or one that makes
   something that worked before false, becomes a board row in `backlog.md` with
   `Source: healer <date>` and a branch `healer/<date>-<row>` with a failing test
   that reproduces it, opened as a draft PR. Never a commit to the default branch,
   never a merge, never a release: those stay with the project's own pipeline.
5. **Report.** Writes `.task-pipeline/healer/<UTC timestamp>.json` (and prints the
   path as the last stdout line). Exit 0 whatever was found; exit 1 only when the
   report could not be written or a source could not be read, with the source named.
   A threshold on regressions would be a target, the same reason `exposure.sh`
   exits 0.

## `healer-report/1`

```json
{
  "schema": "healer-report/1",
  "project": "task-pipeline",
  "repository": {"remote": "origin", "branch": "main", "head": "<sha>"},
  "window": {"since": "<sha|date>", "until": "<sha>", "commits": 7},
  "started_at": "2026-11-21T00:30:00+01:00",
  "finished_at": "2026-11-21T00:41:12+01:00",
  "status": "clean | regressions | idle | partial",
  "checkup": {"exposure_line": "...", "unconfirmed": 3, "abandoned_runs": 0,
              "open_rows": 12},
  "rechecked": [
    {"unit": "<sha or PR #>", "tiers": ["unit", "seam", "product"],
     "cross_family": true, "verdicts": {"unit": "pass", "seam": "pass",
     "product": "risk"}, "evidence": ["<command> -> <what it printed>"]}
  ],
  "regressions": [
    {"id": "B-123", "unit": "<sha>", "tier": "seam", "severity": "blocker",
     "what": "one sentence", "evidence": ["<command> -> <output excerpt>",
     "<path>:<line>"], "branch": "healer/2026-11-21-B-123", "pr": 175}
  ],
  "open_tasks": [{"id": "B-120", "priority": 1, "source": "healer 2026-11-20"}],
  "not_examined": [{"unit": "<sha>", "why": "no check runs offline"}],
  "degraded": []
}
```

Rules the reader can rely on:

- Every field is present; `[]` is an answer, a missing key is a defect.
- `status: "partial"` whenever `not_examined` or `degraded` is non-empty: a
  report that could not look somewhere never reads as `clean`.
- `evidence` items are commands with what they printed, or `path:line`; a claim
  without one is dropped by the writer, as `certify` drops it today.
- No secret, token, personal data or private path outside the repository appears
  in the report; paths are repository-relative.

## What the caller owns, not this mode

Scheduling (00:30 Europe/Warsaw after the 23:00 hosted checks, after a release,
after a merge in balanced and optimize modes, on the process manager's signal),
placement (Studio, MacBook only under green load, cloud services through their own
CI), concurrency (at most 2 healers on the MacBook, 6 on Studio, one per project)
and the order of projects. The mode is one project per run and holds no global
state, so the caller can enforce all of that without the skill knowing.

## Delivery

- Contract: this file, on branch `feat/checkup-healer-contract`, 2026-11-20.
- Mode, schema file `schemas/healer-report-1.json`, validator guard with a
  negative self-test, doctrine in `references/exposure.md` and the command's
  argument hint: release v1.106.0, target 2026-11-27, through this repository's
  pipeline (PR, nightly checks at 23:00, tag, npm).
- Out of scope: auto-merging a healer PR, a healer that edits the default branch,
  and any cross-project state.

## Open questions, decided here

| Question | Decision | Why |
|---|---|---|
| New command or mode | Mode of `checkup` | A second command costs every surface a command touches (`exposure.md`). |
| Where the report lives | `.task-pipeline/healer/` in the project | The process manager reads files the project keeps; no new service. |
| Exit code on regressions | 0 | A threshold becomes a target; the report carries the count. |
| Model family | Prefer a different family, report when not | The harness picks models; the skill names tiers, never vendor ids. |
