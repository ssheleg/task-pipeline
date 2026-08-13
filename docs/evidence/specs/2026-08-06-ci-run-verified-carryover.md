# Carry-over ledger — ci-run-verified

Append-only. Seeded at stage 0, read in full at stage 10.

| # | Stage | What | Why | Owner | Resolution |
|---|---|---|---|---|---|
| 1 | 5 | The negatives floor lagged the workflow on `main`: `MIN_EXPECTED = 104` while `validate.yml` carried **108** | four canon self-tests landed in v1.15.0 without raising the floor. Second recorded instance — the floor's own comment records the first (20 against 34) — so `audit.md`'s class-seen-twice rule made it a guard rather than a note | — | **closed** — guard + negative; floor now equals the measured count |
| 2 | 5 | Two negative self-tests reached the wrong guard, and one plant was inert | the isolating-plant discipline (`skills/probe-every-guard-branch-separately`): "stage 7 stops citing" was rejected by the citation-resolvability guard, "a second copy" by the Contents-list guard, and the stage-8 config plant left a second `The CI verdict` occurrence behind so the guard never saw a change. **R-001 — doubt the probe first** — is what separated a bad plant from a missing guard | — | **closed** — all five re-probed with isolating plants, each watched firing its own message |
| 3 | 6 | `python3 test/negatives.py` failed 20, then 4, then passed 114 twice | the failing runs coincided with leftover scratch copies from this run's own **manual** probing in `/tmp`. Not reproducible on a clean `/tmp` (two consecutive full passes), and the mechanism was **not** established — `df` shows 39 GiB free and one copy is 10 MB, so disk pressure is ruled out but nothing else is. Recording the observation rather than a guessed cause | next run that sees it | **open** — CI is the independent check; if it reproduces there, the suite is order-sensitive and that is a defect in the harness, not in a guard → `B-006`|
| 4 | 9 | The code graph and the wiki are still not refreshed — carried over from the v1.15.0 run and now two releases deep | one refresh after both releases is one refresh; the graph's own ledger row states the lag out loud, which is the mechanism v1.15.0 shipped working on its author | next run, before its stage 0 trusts the graph | **open** → `B-007`|

Counts printed beside every gate verdict: **4 rows · 2 closed · 2 open**.
