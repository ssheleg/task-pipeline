# Carry-over ledger — evidence-docs

> **Append-only.** Any stage may add a row; nobody edits or deletes one.

| # | Stage | What | Why it isn't done | REQ | Where it lives now |
|---|---|---|---|---|---|
| 1 | 6 Tests | The negative self-tests use **fixed `/tmp/<name>-copy` paths**, so two runs of `npm run test:all` at the same time overwrite each other's scratch. Observed this run: 13 guards reported "did not fire" while a concurrent session ran the same suite from the main checkout, and `/tmp/ci05-copy` — that session's scratch — sat in the way. After the collision cleared, all 112 passed unchanged | the runner's `copy_dir_of()` parses the literal path out of the workflow step to detect a no-op plant, so a `$$`-style unique path would leave it matching nothing. Making the scratch unique **and** keeping no-op detection is a design change, not a one-liner, and it is not what this run was for | — | **open** — sibling of the already-fixed "scratch reused across steps" class (R-003 territory), so it earns a mechanism rather than a third note. Next run in this repo, before any concurrent work is assumed safe |
| 2 | 9 Docs | Graph and wiki not refreshed for this change | the previous run's row 8 made the same call for the same reason — one refresh after the halves land beats two, one of them stale | — | **open** — next run's stage 0 must not trust the graph until refreshed |

Counts printed beside every gate verdict: **2 rows · 0 closed · 2 open**, both with a
named home and a trigger.
