## Fix cycles 6–8 of the release iteration — #125, branch `iter1/M-5-N-1` (2026-10-13)

Rounds 6 and 7 failed on `lessons.py rebuild`. Cycle 7, under the loop guard, changed the
design rather than the guard. Round 8 failed on identity. Cycle 8 made every checkout of a
project count before one decides, discovered worktrees, and keyed memory ids by
`(project, classKey)`; see `identity_controls`, `low_controls` and negatives 459–463. This branch merges `origin/main` (v1.94.1, #126) without
rewriting history. The fixes are recorded in the CHANGELOG under *Unreleased*. The branch is
pushed but not merged, and no version or publication is claimed.

- **Rebuild:** `lessons.py rebuild` never loses what it cannot re-derive. Unread or
  unresolved origins are carried per `(project, retro)` with their memory ids, and only
  `--prune-carried` removes them. The tests are `carry_forward_controls` and
  `partial_rebuild_controls` in `test/lessons_test.py`, plus negatives 454–458.
- **F2–F5:** documentation drifts in `continuity.md`, the `graph.py` docstring and
  `stages.md`. The authority rule now has one home, guarded by `test/release_approval_test.py`.
- **F6:** the merge notice is accurate when the family index was set aside.
- **New rules:** a parallel-work check before each cycle (`iteration.md` → *The cycle*), and
  background-dispatch command hygiene (`build.md` §4.1).

Next task: run round 9 of verification on #125's head. The release order with v1.94.1 is the
coordinator's.

## Release repair candidate — v1.94.1 (2026-10-13)

The immutable v1.94.0 tag reached accepted main but its release failed the
missing-retrospective-declaration guard; publication was skipped. This patch
records both unstamped versions and synchronizes metadata without changing the
accepted skill payload. The earlier candidate notes below are historical.

[Repair packet](evidence/runs/2026-10-13-release-1941/README.md) owns current
source, checks, unpublished local-tag handling and the exact next task. Independent
audit, safe-disk full validation on the accepted local tag, normal integration and
release/readback remain separate gates. No completed stage-10 stamp is claimed.

## Release candidate — v1.94.0 (2026-10-13)

Five version surfaces now name v1.94.0 for the accepted release-iteration feature
and its independent fixes. This is a release candidate, not a publication claim.
Published release remains v1.93.3 until an exact-SHA release run and npm payload
readback prove otherwise. R30 owner gates merged through PR120 at9fb9cfb after genuine candidate checks.
The final feature PR112 still governs main integration.

Next: review this metadata diff, integrate via the feature branch, run the required
checks on PR112's final head, then tag the normally merged source. Verify annotated
tag, every release job, npm payload and installed copies before closing the hub pins.
Historical verification rows below retain their original observations.

# Start here — task-pipeline

## Current source state — 2026-10-13

Published release remains **v1.93.3**. The accepted feature branch is
[`feat/release-iteration` at its PR119 merge](https://github.com/ssheleg/task-pipeline/commit/3596355ae56bd067a243bd5d17a8d40aeec292a0).
PR114 and PR115–119 are merged into that feature; PR112 is the pending route to
`main`. No new version or publication is claimed for these changes.
[Verification](evidence/verification.md) · [board](evidence/backlog.md) · [CHANGELOG](../CHANGELOG.md).

The accumulated implementation contains the release-iteration loop, risk-based
certification rounds, lossless lesson index operations, wave planning and graph
synchronization, run-scoped memory-unavailable markers and complete plain-skill
installers. The later corrections preserve graph state on refusals, require a
supported locking backend, record watched waits without inventing an executor,
and provide a release-authority source locator without treating it as a grant.
The body headroom change relocates existing obligations to an explicit stage-0
reference; it does not remove them.

PR119's initial hosted run failed the graph-conditional reference invariant.
The corrected exact candidate passed all jobs, including all eight negative
shards, in the [source-bound receipt](evidence/runs/2026-10-13-feature-integration.json).
Its earlier [local full gate](evidence/runs/2026-10-13-l3-graph-waits-full.json)
remains bound to that earlier source; it is not a new full run at the merge SHA.
The [R07–R16 map](evidence/runs/2026-10-13-r07-r16-acceptance.md) records remaining
live-service and consumer-migration limits. Checkpoint/handoff fixtures are not
a live Observatory exchange. Legacy packet reads remain because the named
consumer still has legacy packets; a Fabric format rename is not assumed.

**Exact next task:** integrate the separately reviewed R30 owner-validator
correction, freeze the accumulated release candidate, run its required local and
hosted gates, and merge PR112 normally. Then version, publish, verify the registry
payload and update the hub pin and installations with source readback. Keep
publication, native discovery and model task quality as separate acceptance.
The lessons directory ownership remains in hub B-181 and `state-json.md`.

## Historical release notes

The sections below preserve observations at their stated releases. Their
then-pending next actions do not override the current task above. Historical
verification rows are not silently re-stamped from newer test results.

## v1.93.3 (shipped, #113), a patch to wave 2

Findings from a re-certification reading of v1.93.2 and an independent observer
(CHANGELOG `v1.93.3`, verification section *Shipped state — v1.93.3*):

- The seven wave-2 commit references that a clone cannot follow are backticked again and
  declared in `docs/evidence/retro.md` (`docgate:known-dead`, reason and
  `git fetch origin pull/109/head` beside it).
- `stage_checkpoint.py handoff` keys a retry on memory events only, so a `gate:` line no
  longer turns a retry into a replacing offer.
- R13 gained `scripts/backlog_sources.py` + `test/backlog_sources_test.py`; R16 gained
  `test/release_approval_test.py`. CI's validate job now also runs these two and
  `memory_nudge_test.py`, which was in `npm test` but not in CI.

**Done:** #113 merged and the `v1.93.3` tag points at its merge commit `52fa75d`. Left from it: the hub re-pins 1.93.3 instead of 1.93.2 in wave 5.

## Wave 2 (shipped as v1.93.2; its branch is deleted, its commits are under `pull/109/head`)

Driven by the sshlg-skills waves run: plan
[`docs/evidence/plans/2026-10-11-integration-waves.md`](https://github.com/ssheleg/sshlg-skills/blob/waves/2026-10-11-integration/docs/evidence/plans/2026-10-11-integration-waves.md)
(Wave 2, R07–R16).

At its original pre-release cut, wave 2 was versioned **1.93.0** and its
verification rows were recorded at `never`. That was a candidate observation:
v1.93.0 and v1.93.1 published nothing; the payload subsequently shipped as
v1.93.2, as stated in this section heading and CHANGELOG.

- **R07 test temp residue.** `tp-b80` (`test/validate.py`), `tp-stage-ckpt` and 15 files
  with bare `mkdtemp` clean up after themselves. A validator check now refuses a test
  file that makes temp state with no cleanup (plant `test/negatives/453-…`); writing it
  found and fixed two leaks in `test/validate.py` itself.
- **R08 / HK-05 / #91.** The 433 negative self-tests and 15 property checks are files
  in `test/negatives/` (the hub plan said `test/negatives.json`; each check is a shell
  script, so it ships as a directory, every file byte-checked against the YAML-parsed
  `run` value it came from); `validate.yml` went from 507,836 to 12,181 bytes; the `negatives`
  job runs `test/negatives.py --shard N/8` on an eight-value matrix. All eight shards
  passed locally on `941bed8`, pre-squash (438 plants rejected, 15 property checks printed, none
  dormant). On CI the eight shards took 3m29s–6m45s (row `R08-ci`), and B-100 is
  closed.
- **R09 budget.** Description 909 → 890 chars; body 4736 → 4646 of 4750 tokens. B-120
  closed with the auditor's reading.
- **R10 ledgers.** The verification headers read "released"; the merged branches
  `feat/wave-mode` and `fix/no-stamp-1912` are deleted.
- **R11** Observatory checkpoint/handoff and the memory nudge · **R13**
  `backlog-sources.json` · **R14** namespaced packet id · **R15** Fabric contract
  fixture · **R16** release approval mode.

PR [#109](https://github.com/ssheleg/task-pipeline/pull/109): run `38242485458` green —
the slowest shard 6m45s and the whole run 6m50s, where the one job had taken 90–111 min.
Verification row `R08-ci` holds the numbers. B-100 is closed with them.

The hub (ssheleg/sshlg-skills) re-pins task-pipeline in wave 5, which closes B-160. The family rows B-154 and HK-05 live in the
sshlg-skills board and close there, at the wave-5 re-pin.

The previous page (the 2026-09-07 Sherlock audit branch) is history:
[that revision](https://github.com/ssheleg/task-pipeline/blob/aea2e14561b3ed3a20ce05fcfa7c08e7b9ae74ab/docs/HANDOFF.md).
