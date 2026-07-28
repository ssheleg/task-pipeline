# Carry-over ledger — <topic>

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
| 1 | 5 Dev | XLSX export path | scope call — CSV first | REQ-004 | LIN-483 |
| 2 | 5 Review | `export.ts` lacks a size guard | minor, non-blocking | — | backlog |
| 3 | 2 Brainstorm | REQ-007 dropped: bulk export | operator agreed 2026-07-28 | REQ-007 | dropped |

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

## Notes

- Adding a row costs one line and never blocks a stage — that is the point. The
  ledger is cheap precisely so nobody is tempted to keep it in their head.
- Rows referencing a REQ feed that REQ's final status: an open carry-over row
  means the requirement is at best `partial`, never `verified`.
