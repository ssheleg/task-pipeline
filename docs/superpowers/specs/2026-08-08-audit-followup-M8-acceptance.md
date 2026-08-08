# Acceptance — `audit-followup` · M8 `prune-order-sweep`

**Branch:** `feat/prune-order-sweep` → `main` · **Version:** `v1.24.0`
**REQ:** REQ-013, added mid-M1 by R-003's sibling sweep.

## Ladder walk

| Seam | Finding | Became |
|---|---|---|
| L2→L3 | Rule 21 stated a contract (*stamp before prune*) in `references/retrospective.md` and in no other surface. The contract existed; its **propagation** did not | fixed across every surface in this change |
| L3→L4 | No guard covered contract *agreement* — only contract *citation*. Every rule-16…21 guard has that shape | the order guard, comparing against the doctrine derived at check time |
| L5→L6 | The guard's own first version had two blind spots (ordered lists; then-sequences without "first") and a third that was blind to the wording **this release introduced** | found by probing, fixed, re-probed |
| L6→L7 | `SKILL-CARD.md` — the page a reviewer reads before trusting the skill — still said the eval suite was *"Never executed"* and counted 26 reference files against 28 | fixed in this change |

**Two passes. New findings: 4 · self-inflicted: 1** (the guard's blindness to its own new
wording). Below the crossover, so the axis was not rotated.

## REQ coverage

| ID | Status | Evidence |
|---|---|---|
| REQ-013 | `verified` | The order guard exists and was watched failing against a planted defect in **all four** shapes, each restored to green — P1 adjacent enumeration, P2 `first…then`, P3 ordered list, P4 bare `…then…`. Three negative self-tests added to `.github/workflows/validate.yml`; the negatives floor raised to match the workflow's own count. `npm run test:all` exit **0** |

## Surfaces corrected

`SKILL.md` ×2 · `references/acceptance.md` ×3 · `references/stages.md` ×3 ·
`references/companion-skills.md` · `references/knowledge-sources.md` ·
`templates/retro.md` · `templates/README.md` · `commands/task-pipeline.md` ·
`cursor/rules/task-pipeline.mdc` · `docs/DOCMAP.md` · `README.md` ×2 · `CLAUDE.md` —
and, in M1's close-out, this project's own `docs/superpowers/retro.md` header and two
pages in the operator's wiki. **One rule, stated on every file above; exactly one of them —
`references/retrospective.md` — had been updated.** The count is deliberately not written
here: it depends on whether you count files or occurrences, and this run produced two
different numbers from two definitions before settling on the list.

## What the operator should look at

**The measured false-positive spread, because it is the argument against the obvious
check.** The intuitive predicate — *both act words in one paragraph* — returns 32 hits on
this corpus and 22 of them are false, including `retrospective.md`'s own correct prose.
Shipping that would have made the gate noise inside one release. The shipped predicate
returns 8, all true, and its scope is written into the guard as a comment: prose *about*
the dependency is deliberately out of scope, and that is a stated blind spot rather than
an unnoticed one.

**The guard was blind to the wording this very release introduced.** Its first ordered-list
pattern required a list item to open with a bare act word; the fix wrote `2. **Then
prune.**`, which opens with "Then". A probe caught it. A green would not have.

## The review found what the gates did not

`Claude Code Review` on PR #10 confirmed **three of five candidates**, and one of them was
a real defect in the guard this module exists to ship:

1. **The surface count disagreed with itself** across `CONTRIBUTING.md`, `CHANGELOG.md`,
   the PR body and this document — nine, ten, twelve-by-enumeration, fourteen, fifteen.
   The class this PR fixes, committed in the PR's own prose. Resolved by deleting the
   number everywhere and keeping the list.
2. **The guard's `SCOPE` comment said "three shapes"** while listing and implementing
   four — the same drift, inside the guard written to catch drift.
3. **The P3 ordered-list branch had a proven false-negative path.** It scanned the whole
   file and compared only the first pair, so a violating list placed *after* a correct one
   was never examined; it also skipped the history exemption the prose shapes get, so a
   numbered list narrating the old order would have blocked a legitimate commit.

Finding 3 was labelled a nit and is not one by this repository's own rubric: a guard with
a known false-negative path is what [`gates.md`](../../../plugins/task-pipeline/skills/task-pipeline/references/gates.md)
calls a decoration that reports success. It was fixed, and all four scenarios were probed:
history lead-in → exempt · violation after a correct list → fires · two unrelated lists →
silent · plain violation → fires.

A second review pass on the fixes confirmed six more, of which **three were new**: a
live defect in the shipped `evidence-docs` navigator (`prune first, cap of ten` in a table
cell — a shape with **no pair to compare**, which every pairwise check misses by
construction), this document's own gate verdict contradicting the ledger it summarises,
and a 225-character line in `CHANGELOG.md` against this repo's ~80-character rule.

**The uncomfortable part:** none of this came from a stage. It came from a bot the
repository happens to run on pull requests. Carry-over row 8.

## Axis arithmetic, and where this stopped

`test/validate.py` was edited three times for the same reason, which is
[`loop-guard.md`](../../../plugins/task-pipeline/skills/task-pipeline/references/loop-guard.md)'s
trigger. Run, the two axes separate — and lumping them would have given the wrong answer:

| Axis | New findings | Self-inflicted | Verdict |
|---|---|---|---|
| the guard's shapes | 5 | 0 | **still paying** — P5 caught a live defect in the shipped skill |
| this run's own prose (counts, wrapping, the verdict) | 3 | 3 | **exhausted** — the fix is not another pass, it is deleting the numbers |

**The stop rule, written down rather than felt.** The guard's `SCOPE` comment now states
what it does **not** cover — inflected forms, lists whose items are separated by blank
lines, and any statement of the order naming neither act. Invariant 34 points at that
comment instead of restating the shape count, so the two cannot disagree. Any further
widening is a ledger row, not a fourth pass on this module. A review finding that arrives
after this merge is carried, not chased — that is what rotating the axis means here.

## Gate verdict

```
GATE 10 acceptance (M8): PASS — 1/1 REQ verified against a check seen failing five ways
  carry-over: 8 rows · 6 open · 0 unresolved · row 4 closed by this module
             (rows 7 and 8 were ADDED by this module — the ledger grew, and it says so)
  guards: 123 negative self-tests (floor raised 120 → 123)
  abstained: 0 · unmeasured: behavioural evidence, still 0 blind runs
```
