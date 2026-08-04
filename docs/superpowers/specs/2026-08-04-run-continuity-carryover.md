# Carry-over ledger — run-continuity

> **Append-only.** Any stage may add a row; nobody edits or deletes one. Committed
> to `docs/superpowers/specs/YYYY-MM-DD-<topic>-carryover.md` beside the brief, and
> read in full by stage 10 (acceptance).
>
> **The rule: deferred out loud is forgotten.** If it isn't written here, it wasn't
> deferred — it was lost. That covers everything said in passing: "we'll do that
> later", "good enough for now", a `DONE_WITH_CONCERNS` from an implementer, a
> reviewer's non-blocking finding, a requirement the operator agreed to drop.

| # | Stage | What | Why it isn't done | REQ | Where it lives now |
|---|---|---|---|---|---|
| 2 | 5 Dev | T8 — the context rule in `~/.claude/CLAUDE.md` — is written and shown but **not applied**: it needs the operator's explicit word, and a loop fire is not one | blocked on a human by design (REQ-009); a generic signal is not a specific authorization | REQ-009 | **resolved** — operator ruled "до конца на автомате" against the shown diff; applied 2026-08-04 at `~/.claude/CLAUDE.md:85`. Verified by eye, not by a check: no guard in this repository can see that file |
| 3 | 9 Docs | `graphify-out/` not refreshed — last built 2026-08-01, and this run changed four files it indexes (`pipeline.schema.json`, `pipeline.example.json`, `test/validate.py`, `test/negatives.py`) | graphify's semantic pass requires subagent dispatch; this session carries a standing instruction not to call the Agent tool. A partial run would shrink the graph and graphify's own shrink-guard would refuse the write — fail-safe, but not an update | — | next run: `/graphify . --update` in a session without the no-subagent constraint. **A stale graph is a false premise carrying the authority of a machine** — stage 0 of the next run must not trust it until refreshed |
| 4 | 9 Docs | Obsidian wiki `projects/task-pipeline/` not synced — last synced at v1.6.1, now four releases behind (v1.7.0-v1.11.0) | deferred to protect the remaining context for stage 10, which is mandatory and cannot be deferred | — | next session: `wiki-update`. Named here so it is a ratchet, not a forgotten step |
| 1 | 1 Docs | `templates/carryover.md` ships `../references/audit.md`, which breaks the moment the template is seeded where its own doctrine says to seed it (`docs/superpowers/specs/`). Present since `2a6ff89` (v1.1.0); no prior run seeded the template verbatim, so nobody hit it | found mid-run, fix belongs to stage 5 | REQ-012 | REQ-012, this run |

## Columns

- **Stage** — where it surfaced, so acceptance knows how far it travelled.
- **What** — the concrete thing not done. "Error handling" is not an entry;
  "`export.ts` swallows a failed write instead of surfacing it" is.
- **Why it isn't done** — scope call, blocked, deliberate deferral, out of budget.
  "Forgot" is a legitimate and useful answer here.
- **REQ** — the requirement it belongs to, or `—` if it's outside the REQ spine.
- **Where it lives now** — issue id, backlog, `dropped` (with the operator's
  agreement), or `unresolved`. **`unresolved` blocks the stage-10 gate**: an item
  with no home is exactly the thing that gets forgotten, so acceptance refuses to
  close on it.

## This ledger is a ratchet, not a TODO list

A TODO is invisible until somebody opens the file. **A ratchet is a named, counted
set that may only shrink, and it is printed beside every gate verdict:**

```
GATE 6 tests: PASS — full suite green (247 tests)
  carry-over: 4 open (was 6) · unresolved: 0 · audit findings deferred: 2
```

That one line is the whole mechanism. Without it, `PASS` reads as *verified*; with
it, `PASS` reads as *"green, and here is exactly what was not looked at"* — which
is the true statement.

- **Print the counts at every gate**, not only at stage 10. A number nobody sees
  until the end is a number nobody acts on.
- **The set may only shrink.** If it grew, the run log gets one sentence saying why.
  A ratchet that grows silently is a TODO with a better name.
- **A finding class that appears twice stops belonging here** and becomes a check in
  the host's lint or CI ([`audit.md`](../../../plugins/task-pipeline/skills/task-pipeline/references/audit.md) → *A class that
  repeats twice becomes a gate*). This ledger is for what cannot be automated, not
  for what nobody automated.

## Notes

- Adding a row costs one line and never blocks a stage — that is the point. The
  ledger is cheap precisely so nobody is tempted to keep it in their head.
- Rows referencing a REQ feed that REQ's final status: an open carry-over row
  means the requirement is at best `partial`, never `verified`.
