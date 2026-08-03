# Acceptance — `default-routing-adoption`

Ladder walk first, then the table. Counts printed beside the verdict.

## Ladder walk — by seam, not by file

| Seam | Verdict |
|---|---|
| L0→L1 requirement rests on a recorded decision | ✓ every REQ traces to D1–D5 in the brief |
| L1→L2 decision reached the spec | ✓ spec §§1–8, each carrying `covers:` |
| L2→L3 contract **and its failure behaviour** | ✓ each guard has the message it prints and the reason |
| L3→L4 every contract has a task | ✓ nine tasks, `Implements:` set-equal to the REQ ids |
| L4→L5 the DoD landed in the tree | ✓ verified per task, not assumed |
| L5→L6 an executed observable | ✓ 55 guards, the two new ones watched failing against planted defects |
| L6→L7 a user can reach it | ✓ `adoption.md`, README section, the routing rule in the operator's config |
| L7→L0 does the shipped surface satisfy the requirement's **statement** | **partial — and it was agreed**: the request said *"любая задача … стартует через него"*; what shipped routes work that **changes the repository** and excludes questions, explanations and one-line edits. The narrowing was raised before the brief was locked and accepted at gate 0 |

### Absences found (new rows, written before the table)

| # | Absence | Disposition |
|---|---|---|
| A-1 | No eval checks the routing rule **as a rule** — `TRIG-04` proves a plain refactor should trigger, but nothing exercises "the global instruction is present, therefore this routes". The rule's own enforcement is untested | new carry-over row → next run |
| A-2 | The wiki was not synced this run | carry-over → next run |

**Counts:** new findings 2 · caused by this run's own fixes 0. The axis is not
exhausted; a second pass would still be reading, not repairing itself.

## Coverage

| REQ | Status | Evidence |
|---|---|---|
| REQ-001 adoption.md | **verified** | file present, both walkthroughs, guard `adoption-walkthroughs` probed (removed *An existing project* → exit 1) |
| REQ-002 floor kinds | **verified** | comment block names id-threshold vs count; both seeded shapes still exit 0 under `npm test` |
| REQ-003 vocabulary + boundary | **verified** | description 1013/1024, `Not for:` clause + both opt-out phrases; guard probed |
| REQ-004 evals match | **verified** | 15 evals, 5 categories, `evals/run.py` exit 0; TRIG-04 and NOTRIG-04 added |
| REQ-005 routing rule | **verified** | `~/.claude/CLAUDE.md` — boundary, exclusions, both escape phrases, and why the rule lives there |
| REQ-006 agent-sync patch | **verified** | `jsonschema.validate` PASS against `pipeline.schema.json`; guardedFiles +2; shipped as 1.4.3 |
| REQ-007 version floor | **verified** | `companion-skills.md` states ≥ 1.3.0 and why |
| REQ-008 dogfood | **verified** | `docs/DOCMAP.md` records the real gate and refuses a second; no `scripts/check-docs.sh` created. The check was revised at stage 5 (C-4) and **the operator agreed to the revision at this gate on 2026-08-03** |
| REQ-009 run recorded | **verified** | `evals/RESULTS.md` — one dated run, scoped honestly as self-observed rather than blind |

**Nine REQs · 9 verified · 0 partial · 0 unknown.** One check was revised mid-run and the revision carries the operator's explicit agreement, recorded rather than assumed.

## Carry-over at close

`open: 3 · accepted: 1 · resolved: 2 · unresolved: 0`

C-1 evals never executed · C-2 the rule binds only where that config is read ·
C-3 **closed** (agent-sync pulled before editing) · C-4 **closed** (operator agreed to the revised REQ-008 check) ·
A-1 the routing rule is itself untested · A-2 wiki not synced.

## The closing question

Here is what you asked for: any task routes through the pipeline unless told
otherwise, wider keywords, tutorials for a new and an existing project, and an audit
of the agent-sync seam.

Here is what shipped: routing default-on for repo-changing work with a stated
boundary and a tested opt-out; the vocabulary widened in both languages; an adoption
doctrine with both walkthroughs, dogfooded on this repository; agent-sync's binding
fixed and released.

Here is what is deferred: the behavioural evals have still never been run against a
model, so the coexistence protection is stated rather than measured; and the routing
rule's own enforcement has no test.

**What is missing?**
