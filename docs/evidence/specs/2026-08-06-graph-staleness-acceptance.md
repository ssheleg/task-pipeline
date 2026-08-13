# Acceptance — graph-staleness

Brief: [`2026-08-06-graph-staleness-brief.md`](2026-08-06-graph-staleness-brief.md) ·
Merged as `2ce6ecc` on `main` (PR #7) · **not tagged**, by operator decision

## The ladder walk — run before the table

Each REQ walked bottom-up through its rungs. Findings ordered by seam, and every
absence turned into a row **before** the coverage table below.

| Seam | Finding | Became |
|---|---|---|
| doctrine → its own examples | the three worked-example rows omitted the marker the rule two lines below requires; the `unresolvable` row invented a second spelling | fixed + guard + 2 negatives |
| doctrine → its portable copies | R-003's sweep found the same drift in the design doc, the Cursor rule and the config — four spellings inside the release that introduced the marker | fixed, one canonical string |
| guard → the text it parses | the new marker guard compared **per line**, and the doctrine wraps at ~80 columns, so it matched nothing in `README.md`/`stages.md` and printed a pass | found by probing, not reading; whitespace-normalised |
| artifact → its renderer | a blank line silently ends a GFM table; hit **five** times in this run, plus three pre-existing in the v1.12.0/v1.13.0 ledgers | hygiene **check 7** + negative; all eight fixed, none baselined |
| gate → its own floor | check 7 shipped with `HYGIENE_FLOOR_7` undeclared and printed `ok … (floor )` over three real hits | undeclared floor is now a failure + negative |
| prose → a number that changes | the guard count hand-corrected three times in one run | prose stopped restating it; the guard's negative rewritten to introduce rather than edit |
| process → the gate's exit code | one commit+push ran after a red hygiene gate because the exit code did not gate the next command | recorded in the CHANGELOG and the retro |

## Coverage — every REQ accounted for

| id | Status | Evidence |
|---|---|---|
| REQ-001 | verified | `references/knowledge-graph.md` → *Measure the lag*; guard asserts the three command literals — `npm test` green, negative *"the measured-lag rule must keep its commands"* PASS |
| REQ-002 | verified | three states named; negative *"a graph that cannot be measured needs its own state"* PASS |
| REQ-003 | verified | `knowledge-sources.md:97` cites the section, carries no second copy of the commands |
| REQ-004 | verified | `templates/brief.md:34` shows the measured row; negative *"the seeded brief must not ship a bare build date"* PASS |
| REQ-005 | verified | `stages.md` stage-0 harvest **and** its `GATE (manual)`; negative *"stage 0's own section must state the measured lag"* PASS |
| REQ-006 | verified | `pipeline.example.json` stage-0 `gate.check`; negative *"stage 0's config gate must require the measured lag"* PASS |
| REQ-007 | verified | the stage-9 guard extended in place (`test/validate.py`), no second guard for the class — R-003 satisfied |
| REQ-008 | verified | 9 negatives added; floor 95 → **104**; `npm run test:all` → *all 104 guards provably reject their planted defect* |
| REQ-009 | verified | `README.md` + `cursor/rules/task-pipeline.mdc`; 0 relative links in the rule; no live surface still says *"with its build date"* |
| REQ-010 | verified | CHANGELOG v1.15.0 section; four-way sync + `SKILL-CARD.md` all read 1.15.0 — the sync guard is green |
| REQ-011 | verified | `references/portability.md` manifest row |
| REQ-012 | verified | `CONTRIBUTING.md` invariant 30, citing `never requires it — a run passes intake quoting a`, which `test/validate.py` actually prints |
| REQ-013 | **deferred** | tag + npm release. **Operator decision, recorded**: a concurrent session's *canons* work targets the same v1.15.0, so one tag covers both halves. Carry-over rows 9 and 10 |

**12 of 13 verified with evidence, 1 deferred by an explicit operator decision.**
Nothing is unknown, and no *"done"* is claimed without a command behind it. The
counts beside this verdict: carry-over **10 rows · 6 closed · 4 open**.

## The closing question

*Here is what you asked for:* the stage-0 ledger row states a measured lag instead of
a build date, degrades honestly when the stamp is missing, and refuses to be trusted
until refreshed — without touching the refresh cadence.

*Here is what shipped:* that, plus five things the run found on the way — a marker
with four spellings, a guard that was green because it never looked, a table-splitting
defect that had been rendering three old ledgers broken since the day they were
written, a gate that judged against an undeclared floor, and a count that stopped
being restated at all.

*Here is what is deferred:* the tag and the npm release, waiting on the concurrent
half so `v1.15.0` means both. And `gh` needs re-authenticating — a human step.

*What is missing?* — operator's call.
