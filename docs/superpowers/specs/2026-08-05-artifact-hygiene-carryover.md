# Carry-over ledger — artifact hygiene

Seeded at stage 0, appended by **every** stage the moment something is deferred,
dropped or left half-done, read in full at stage 10. Deferred out loud is forgotten;
a row here is the only form of deferral this run recognises.

The **count of unresolved rows is printed beside every gate verdict**, so a green
gate never reads as "nothing was set aside".

## Rows

| id | Raised at | What | Why deferred | Resolution | State |
|---|---|---|---|---|---|
| C-001 | 0 | The placeholder check must tell *using* a placeholder from *naming* one. Measured: 32 hits across 16 files here, mostly legitimate doctrine prose (A1) | Needs a real definition and a measurement, which is stage 2's job — specifying it at stage 0 would be guessing | — | open, owned by stage 2 |
| C-002 | 0 | Checks 5 and 6 have no measured false-positive rate yet (A2) | `gates.md` requires a detector be measured before it ships; the measurement needs their definitions first | — | open, owned by stage 2 |
| C-003 | 0 | Per-task execution must stay fast or agents will skip it (A3) | A budget cannot be set before the checks exist | — | open, owned by stage 5 |
| C-004 | 0 | The `spec-plan-quality` run is parked at its stage-0 gate on branch `spec-plan-quality`, commit `dd3155e` | Sequenced behind this run on the operator's call | Unpark at stage 10 and hand it the hygiene line for its `## Self-review` section | open, owned by stage 10 |

## Counts

- Rows: 4
- Unresolved: 4
- Closed: 0
