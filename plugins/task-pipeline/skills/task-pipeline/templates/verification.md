# Verification — <project>

> **Append-only.** One row per REQ, written by stage 8 when the change ships. Nobody
> edits a row except to fill `Human` — and filling it is the one thing in this
> repository a machine may not do.
>
> This is not a second coverage table. The coverage table says *an automated check
> passed at the moment of the run*. It says nothing about whether anybody **looked**
> after it shipped, nor whether it still works N releases later, and it dies with its
> run. This file is the column that outlives it.

| REQ | What | Run | Shipped in | Auto | Human | Note |
|---|---|---|---|---|---|---|
| REQ-001 | CSV export from a report | `2026-07-28-export` | v1.4.0 | pass | 2026-07-30 | opened the deployed page, exported, opened the file |
| REQ-004 | XLSX export | `2026-07-28-export` | v1.4.0 | pass | **never** | — |
| REQ-007 | Export respects active filters | `2026-07-28-export` | v1.4.0 | partial | **never** | CSV path only |

## Columns

- **REQ** — the id from the run's brief. The brief's REQ table is the spine; a row here
  whose id is in no brief is a row about nothing.
- **What** — copied from the brief, not re-worded. *"Check REQ-004"* sends a human to
  look something up; *"XLSX export"* sends them to the feature.
- **Run** — the brief's topic slug, so the context is one file away.
- **Shipped in** — the tag or commit that carried it. Where a project does not tag,
  the commit, and the same value every row of that run carries.
- **Auto** — what the run's own gate said: `pass` · `partial` · `none`. Copied from the
  coverage table rather than re-derived; where the two disagree the coverage table wins
  and the disagreement is a finding. A coverage verdict of **`review`** — *no check can
  decide this* — becomes `none`, because this column records what a machine established
  and there the honest answer is *nothing*.
- **Human** — a date, or the literal **`never`**. Nothing else. *"soon"*, *"mostly"* and
  *"looks fine"* are how a column stops being answerable, and this is the only column in
  the pipeline that a machine may not fill on your behalf.
- **Note** — what the human actually did. *"opened the deployed page and exported"* is a
  note; *"checked"* is not, and six weeks later nobody can tell those two apart.

## `never` is a fact, not a failure

A row sitting at `never` is not a defect and not a debt to be paid down before the next
release. It is **what is true**, printed where somebody can act on it. The moment
`never` becomes something to avoid writing, this file starts lying and the pipeline
loses the only signal it has about the world outside its own checks.

That is why nothing here has a floor, a target, or a direction. Count them, print them,
and let the number be what it is.

## How rows arrive

1. **Stage 8** writes one row per REQ the run shipped, immediately after the deploy
   verification it already performs — `Human` starts at `never` unless the operator
   confirmed during the run, in which case the note says what they did.
2. **A human, later** — fills `Human` with the date they looked, and the note with what
   they looked at. This is the only edit any row ever receives.
3. **Nothing else writes here.** Not stage 10, not a script, not a release job.
