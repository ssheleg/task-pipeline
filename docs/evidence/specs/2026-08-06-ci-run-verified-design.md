# Design — a CI run is checked by reading it

covers: REQ-001 REQ-002 REQ-003 REQ-004

## The gap, stated as the class

`gates.md` → *False success*: **an actor's own reply is not evidence about the
world**, and the test is *what does it print when it did not look?*

"CI green on the tagged commit" prints nothing when it did not look. It is a line in
`release.verify` that an agent can satisfy by believing it. The only method the
bundle offers today is `conventions.md`'s *"CI: the workflow run."* — a place, not a
procedure and not a verdict.

**Tonight supplied the evidence.** `validate` was `completed/failure` on `0d32d85`
and on the `v1.15.0` tag. The failure was correct: the repository's own *Every v* tag
must be contained in main* guard, firing on a tag that was not yet an ancestor of
`main` — the exact defect v1.6.1 built it for. **The guard worked and nothing obliged
anyone to read it.** A guard nobody reads is a fail-open hook with extra steps.

## The method — named commands, so a verdict is earned

Two paths, because one credential problem must not end the check. Both were run
against this repository while writing this.

```bash
# authenticated
gh run list --branch <branch> --limit 1 \
  --json databaseId,name,status,conclusion,headSha
gh run view <databaseId> --log-failed        # only when conclusion != success
```

```bash
# unauthenticated fallback — public repos, no token
curl -s "https://api.github.com/repos/<owner>/<repo>/commits/<sha>/check-runs"
```

**`gh auth status` is not the credential check.** Tonight it reported an invalid
token while `gh api user` returned the login — a cached verdict standing in for a
live one, which is this bundle's own subject. Probe with a live call.

## Three states — and the third is the point

| State | Condition | What the stage records |
|---|---|---|
| **concluded** | a run exists for this sha and `status == completed` | the conclusion, the run id, and — when it is not `success` — the **quoted failing step** |
| **in progress** | a run exists and has not finished | wait and re-read. An unfinished run is not a pass, and "it was still running when I looked" is a report, not a verdict |
| **no run found** | no workflow run for this sha | say so **out loud**. A repository with no CI is a legitimate state and not a green one — `dormant`, in the vocabulary of *Progressive arming* |

The third state is the whole reason this is written down. A method that reports only
failures is indistinguishable, on a silent day, from a method nobody ran.

## Reading the log is part of the check, not a follow-up

A conclusion says *that* it failed. Tonight only the log said **what**: the guard's
name, the orphan tag, and the fix in one line — *"merge or cherry-pick the tagged
commit into main"*. A bare "CI failed" hands the next reader a search problem that
the log had already solved. So the rule is: **on any non-success conclusion, read the
failing step's log and quote the line that names the failure.**

## Where it binds — every stage that pushes

The incident hit twice, at two different stages: the merge (7) and the docs push (9).
Binding it to stage 8 alone would have caught neither.

- **Stage 7** — before tagging, the merge's run is concluded and read.
- **Stage 8** — the run the deploy or tag triggered, in the same breath as the deploy
  logs it already checks.
- **Stage 9** — the docs push triggers CI like any other push, and this stage is the
  one that habitually ends a run.

The gates **cite** `conventions.md`; they do not restate the commands
([`documentation.md`](../../../plugins/task-pipeline/skills/task-pipeline/references/documentation.md)
canon 3 — one home per fact).

## It reports; it does not block

Stage 8's gate already reads *"clean boot confirmed, or an honest degradation report
with next steps — never silent success"*, and that shape is exactly right here. A red
run that the operator has seen and ruled on is a decision; a red run nobody printed
is the failure. Blocking would also make a repository **without** CI cheaper to ship
from than one with it — the same argument that kept the staleness marker
non-blocking in v1.15.0.

## Rejected, recorded so it is not re-derived

- **Restating the commands at each of stages 7, 8 and 9.** Three copies, one drift.
- **`gh` only.** Tonight's token died mid-run; a method with a single path stops at
  the first credential problem, which is when it is needed most.
- **Failing the gate on any red run.** See above — and stage 8 already owns the
  honest-degradation shape.
- **A script (`templates/ci-verdict.sh`).** Same ladder argument as v1.15.0's
  measured lag: rung 2 now, with the promotion trigger written down — promote the
  first time a run is observed closing a stage with an unread CI verdict.

## Self-review

- **Every command named here was run against this repository before it was written
  down:** `gh run list … --json` returned `{"conclusion":"success", …}` for `main`;
  `gh run view 31062300483 --log-failed` returned the failing step; the
  unauthenticated `check-runs` call returned `validate completed success`.
- **Read back against the brief's `Decisions locked`:** D-1 (one home) — *Where it
  binds*. D-2 (three states) — the table. D-3 (read the log) — its own section.
  D-4 (two paths) — *The method*. D-5 (reports, not blocks) — its own section.
  D-6 (stages 7/8/9) — *Where it binds*. D-7 (v1.16.0) — the manifests. No decision
  is contradicted.
- **Read back against the alternatives stage 2 rejected:** all four recorded above
  with reasons.
- **Cost checkpoint, printed and not decided:** surfaces touched **8** (8 at intake)
  · REQ rows **9** (9 at intake) · guards **104 → to be measured, not estimated**;
  last release taught that an estimate written down as a fact is what invariant 13
  exists to catch.
