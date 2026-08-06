# Carry-over ledger — graph-staleness

Append-only. Seeded at stage 0, read in full at stage 10. A row is added the moment
something is deferred, never at the end from memory.

| # | Stage | What | Why deferred | Owner | Resolution |
|---|---|---|---|---|---|
| 1 | 0 | The `always \| major \| manual` cadence mode in `pipeline.schema.json` | rejected at intake, not deferred — `major` manufactures the state the doctrine warns about (a graph confidently wrong between releases, read first by the next harvest). Recorded so it is not re-derived | — | **closed at intake** — decision D-1 |
| 2 | 0 | Promoting the staleness measurement from doctrine (rung 2) to a script (rung 3) | `gates.md` Axis B: a rule starts as prose and is promoted when broken. This one has never been broken because it has never existed | next run that observes it fail | open — retire-when written into the doctrine itself |

Counts printed beside every gate verdict: **2 rows · 1 closed · 1 open (deferred by
decision, with its promotion trigger recorded)**.
