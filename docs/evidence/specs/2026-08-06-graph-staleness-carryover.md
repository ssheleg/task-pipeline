# Carry-over ledger — graph-staleness

Append-only. Seeded at stage 0, read in full at stage 10. A row is added the moment
something is deferred, never at the end from memory.

| # | Stage | What | Why deferred | Owner | Resolution |
|---|---|---|---|---|---|
| 1 | 0 | The `always \| major \| manual` cadence mode in `pipeline.schema.json` | rejected at intake, not deferred — `major` manufactures the state the doctrine warns about (a graph confidently wrong between releases, read first by the next harvest). Recorded so it is not re-derived | — | **closed at intake** — decision D-1 |
| 2 | 0 | Promoting the staleness measurement from doctrine (rung 2) to a script (rung 3) | `gates.md` Axis B: a rule starts as prose and is promoted when broken. This one has never been broken because it has never existed | next run that observes it fail | open — retire-when written into the doctrine itself → `B-008`|
| 3 | 5 | The distrust marker written four ways inside the release that introduced it | closed in this change, not deferred — review found one, **R-003** found the other three, and `audit.md`'s class-seen-twice rule turned it into a guard rather than a third ledger row | — | **closed** — guard + 2 negatives |
| 4 | 5 | That guard was green because it compared per line, and the doctrine wraps at ~80 columns | closed in this change — found by probing it with a planted wrapped defect, not by re-reading it | — | **closed** — whitespace-normalised, probe recorded |
| 5 | 5 | A blank line inside a GFM table, twice in this run (carry-over ledger, brief) | closed as a mechanism, not a row — `audit.md`: a class seen twice becomes a check. Hygiene **check 7**; its first armed pass found 3 more in the v1.12.0/v1.13.0 ledgers, all fixed rather than baselined | — | **closed** — check + negative |
| 6 | 5 | Check 7 shipped with `HYGIENE_FLOOR_7` undeclared and printed `ok … (floor )` over 3 real hits | closed in this change — the gate reporting a pass it never computed, on the release about that. An undeclared floor is now a failure, not a zero | — | **closed** — refusal + negative |
| 7 | 5 | The guard count restated in three living documents, hand-corrected three times | closed by taking the guard's other option — *derive or delete*. The prose now names the command instead of the number, and the guard's own negative was rewritten to introduce a count rather than edit one | — | **closed** |
| 8 | 9 | The code graph not refreshed and the wiki not synced in this change | a concurrent session committed `1c508d4` (the ten canons) onto this branch three seconds after the merge landed, targeting **the same v1.15.0**. Building the graph now indexes a tree that is on no branch's tip for long, and the doc set changes again when canons reaches `main` — one refresh after both halves land is one refresh, two is one wasted and one stale in between | next run, before its stage 0 trusts the graph | open — **and the graph's own row will say so**: `built 3944593 — N commits behind HEAD, signal: built_at_commit (exact) — ⚠ not trusted for reach until refreshed`, which is this release working on its own author → `B-007`|
| 9 | 7 | The tag `v1.15.0` and the npm release | operator decision, not an omission: `main` carries this half, the canons half is in flight under the same version, and one tag over both is what makes the version mean something | operator, once canons lands | open → `B-012`|
| 10 | 7 | `gh` CLI unusable — the token went invalid mid-run (401 after a successful `gh pr create`) | credentials are a human step by design; merge and push still work over SSH, which is how `main` was reached | operator — `gh auth login -h github.com` | open → `B-013`|

Counts printed beside every gate verdict: **10 rows · 6 closed · 4 open (1 deferred by
decision with its promotion trigger recorded, 2 awaiting the concurrent half, 1 human
credential step)**.
