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
pages in the operator's wiki. **Fifteen statements of one rule; one of them had been
updated.**

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

## Gate verdict

```
GATE 10 acceptance (M8): PASS — 1/1 REQ verified against a check seen failing four ways
  carry-over: 6 rows · 0 unresolved · row 4 closed by this module
  guards: 123 negative self-tests (floor raised 120 → 123)
  abstained: 0 · unmeasured: behavioural evidence, still 0 blind runs
```
