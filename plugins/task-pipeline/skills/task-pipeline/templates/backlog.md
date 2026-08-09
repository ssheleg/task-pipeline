# Backlog — <project>

> **The board.** One per project, at `docs/superpowers/backlog.md`. Unlike the
> carry-over ledger, this file is **mutable**: priority is re-derived, state changes,
> rows close. What may never happen silently is a row *disappearing* — a closed row is
> marked closed, with the commit that closed it.
>
> **This is the file a loop iteration reads at the top and re-prioritises at the
> bottom.** `continuity.md` requires the work-list to be re-measured every iteration;
> this is the list.

| id | What | Source | Size | Sev | Blast | Age | Prio | State | Home |
|---|---|---|---|---|---|---|---|---|---|
| B-001 | `export.ts` has no size guard on the write path | `2026-07-28-export` / 5 Review | S | 2 | 1 | 12 | **2** | open | — |
| B-002 | XLSX export path | `2026-07-28-export` / 5 Dev | M | 1 | 2 | 12 | 2 | open | LIN-483 |
| B-003 | REQ-007 bulk export | `2026-07-28-export` / 2 Brainstorm | L | 1 | 1 | 12 | 1 | dropped | operator 2026-07-28 |

## Columns

- **id** — `B-NNN`, issued in order, **never reused and never closed up**. A gap is
  evidence a row left; the *Closed* section below says which and why.
- **What** — the concrete thing. *"Error handling"* is not a row; *"`export.ts`
  swallows a failed write instead of surfacing it"* is. Same bar as the ledger.
- **Source** — the run and stage that surfaced it, so a reader can find the context
  without asking. A row with no source is a wish somebody typed.
- **Size** — `S` / `M` / `L`. Not hours: an estimate in hours is a number that will be
  quoted back as a commitment.
- **Sev**, **Blast**, **Age** — the three inputs to priority, each stated so the
  priority can be recomputed by anyone. `Sev` 1–3 (annoyance / wrong behaviour /
  data-or-money). `Blast` 1–3 (one file / one module / crosses a seam). `Age` in days
  since the row was written.
- **Prio** — **computed, never assigned**: `Sev × Blast + age_bonus`, where
  `age_bonus` is `1` past 14 days and `2` past 30. The formula is repeated here on
  purpose — the inputs are in this table, so a reader checks the arithmetic rather than
  trusting the ranking. Full doctrine: the skill's `references/backlog.md`.
- **State** — `open` · `in-flight` · `closed` · `dropped`. `dropped` needs the
  operator's agreement and the date they gave it.
- **Home** — an issue id where a tracker exists, `—` where this file *is* the tracker.

## Closed

Rows leave the table above only into this list, one line each, with the commit.

<!-- - **B-000 · What it was** — closed by `<commit>` on <date> -->

*None yet.* Stated rather than omitted: an empty list and a missing list look the same
from outside, and only one of them means nothing has closed.

## How rows arrive

1. **Stage 0** seeds this file when it is absent, and reads it when it is present.
2. **Any stage, mid-run** — the moment something is said aloud and not done. Same rule
   as the carry-over ledger: *deferred out loud, or lost.*
3. **Stage 10** — every carry-over row that is unresolved arrives here with a real id,
   and the ledger row is updated to name it. Unresolved means either home `backlog` —
   the value that used to point nowhere — or still `open`. A row in either shape with no
   id on this board is the dangling pointer this file exists to resolve, and the gate
   refuses it.
