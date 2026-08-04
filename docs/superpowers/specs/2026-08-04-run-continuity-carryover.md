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
