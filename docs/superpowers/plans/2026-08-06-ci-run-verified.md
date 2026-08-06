# Plan — a CI run is checked by reading it

Design: [`../specs/2026-08-06-ci-run-verified-design.md`](../specs/2026-08-06-ci-run-verified-design.md)
Brief: [`../specs/2026-08-06-ci-run-verified-brief.md`](../specs/2026-08-06-ci-run-verified-brief.md)

Executed inline, ordered by dependency: the method first, then the gates that cite it,
then the guards that read both, then the negatives that prove the guards. Sequential,
so no two tasks share a file.

| # | Task | Implements | Files owned | DoD |
|---|---|---|---|---|
| T1 | The method in its one home: both command paths, the three states, the read-the-log rule, the promotion trigger | REQ-001 REQ-002 | `references/conventions.md` | both command literals and all three state names present; `npm test` green |
| T2 | Stages 7, 8 and 9 cite it; none restates the commands | REQ-003 | `references/stages.md` | each section names the rule; a guard rejects a second copy of the commands |
| T3 | The config half — stage-8 gate check and `release.verify` | REQ-004 | `pipeline.example.json` | valid JSON; the stage-8 check and the verify list both require the read verdict |
| T4 | Guards over T1–T3 | REQ-003 REQ-004 | `test/validate.py` | all `fail(` above the verdict block; `npm test` green |
| T5 | One negative per guard, each proved plant-first (R-001); floor raised to the **measured** count | REQ-005 | `.github/workflows/validate.yml`, `test/negatives.py` | `npm run test:negatives` green at the new floor |
| T6 | Public surfaces | REQ-006 | `README.md`, `cursor/rules/task-pipeline.mdc` | rule self-contained, 0 relative links |
| T7 | Release record + four-way sync + card | REQ-007 | `CHANGELOG.md`, `package.json`, `.claude-plugin/marketplace.json`, `plugins/task-pipeline/.claude-plugin/plugin.json`, `SKILL-CARD.md` | sync guard green |
| T8 | The decision gets a home; the invariant cites a printed literal | REQ-008 | `references/portability.md`, `CONTRIBUTING.md` | the cited literal appears in a single string in `test/validate.py` |
| T9 | Ship it — **and verify this run's own pushes with the new method** | REQ-009 | — (git, CI) | PR merged, tag `v1.16.0`, `npm view` == 1.16.0, and every run conclusion quoted in the acceptance |

**Set equality (stage-4 gate):** brief REQ ids = {001…009}; union of `Implements:` =
{001…009}. Difference: **∅**.

## Self-review

- Every REQ maps to exactly one task; no task invents a requirement.
- No placeholders; every DoD names a command or a file a check can read.
- File ownership disjoint by construction — tasks run in sequence.
- **Every path above resolves in the tree today** — verified before this plan was
  committed, not asserted.
- **Numbers are measured at the end, not estimated here.** Last release's plan wrote
  *"guards 95 → 97"* and shipped 104; invariant 13 caught it three times. This plan
  states the guard count as *"the measured count"* and fills it in at stage 10.
