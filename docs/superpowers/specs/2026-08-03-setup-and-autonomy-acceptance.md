# Acceptance — `setup-and-autonomy`

Ladder walk first, then the table.

## Ladder walk — by seam

| Seam | Verdict |
|---|---|
| L0→L1 REQ rests on a recorded decision | ✓ D1–D5 in the brief; REQ-010/011 added at gate 0 with the finding that prompted them |
| L1→L2 decision reached the doctrine | ✓ setup.md, portability.md, routing-rule.md, and four edits |
| L2→L3 contract **and its failure behaviour** | ✓ every guard names what it prints and why |
| L3→L4 contract → task | ✓ eleven REQs, all built |
| L4→L5 DoD landed | ✓ verified per REQ, not assumed |
| L5→L6 executed observable | ✓ 59 guards; three new ones watched failing against planted defects |
| L6→L7 reachable | ✓ README section, `/task-pipeline setup`, stage-0 offer, SKILL.md rows |
| L7→L0 satisfies the **statement** | ✓ the operator asked how workflow decisions stay portable; the answer is a guarded manifest plus an inward check, not a promise |

### Absences found (before the table)

| # | Absence | Disposition |
|---|---|---|
| A-1 | The **inward** check is judgemental and has no mechanical half — nothing flags a standing instruction that names no path, command or person | carry-over → a candidate guard next run |
| A-2 | `setup` has never been run end-to-end against a real foreign project; it is doctrine, not yet an observed procedure | carry-over → run it on a host project |

**Counts:** new 2 · self-inflicted 0.

## Coverage

| REQ | Status | Evidence |
|---|---|---|
| REQ-001 setup.md | **verified** | seven passes, finding shape, fix-plan output; guard probed |
| REQ-002 offered once | **verified** | stage-0 phase 1b+ in `stages.md`; sweep rows in both tables, parity guard green |
| REQ-003 command branch | **verified** | `/task-pipeline setup` documented in the command and README |
| REQ-004 self-currency | **verified** | `companion-skills.md` §*Is this skill itself current?*, launcher form, three staleness signals; guard probed |
| REQ-005 escalation | **verified** | cost-of-being-wrong in both sweep tables |
| REQ-006 terms | **verified** | `docmap.md` *Terms* table; **declared terms only**, which is what keeps the false-positive budget at zero |
| REQ-007 UX at stage 2 | **verified** | `brainstorm.md` §*User paths are a design output* + gate clause; guard probed |
| REQ-008 guards | **verified** | 59 of 59, three new with negative self-tests |
| REQ-009 released | **verified** | 1.10.0 on npm, catalogue 0.17.0, plugin refreshed, shadows pruned |
| REQ-010 portability manifest | **verified** | 18 rows, every path resolves inside the bundle; probe pointed one outside → exit 1 |
| REQ-011 routing rule travels | **verified** | `templates/routing-rule.md` ships; `setup` offers it; probe deleted it → exit 1. **C-2 of the previous run closes** |

**Eleven REQs · 11 verified · 0 unknown.**

## Carry-over at close

`open: 5 · resolved: 1 · unresolved: 0` — C-1 evals unrun · C-2 routing rule untested
as a rule · C-3 **closed** (term check made deterministic, so the false-positive budget
never applied) · C-4 wiki · A-1 inward check has no mechanical half · A-2 setup unrun
on a foreign project.

## The closing question

You asked how to keep every workflow decision inside the skill so nothing is stranded
in one project. The answer shipped as a **guarded manifest** — eighteen rows, every
path resolving inside the bundle, a probe pointing one outside turning the build red —
plus the **inward** check that asks of a project's own rules whether they would be
true in a repository nobody has seen.

Deferred: that inward check is judgement, not machinery, and `setup` has not yet been
run against a foreign project.

**What is missing?**
