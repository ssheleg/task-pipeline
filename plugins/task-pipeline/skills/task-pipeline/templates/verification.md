# Verification — <project>

> **Append-only.** One row per REQ, written by stage 8 when the change ships. Nobody
> edits a row except to fill `Human` — and filling it is the one thing in this
> repository a machine may not do.
>
> This is not a second coverage table. The coverage table says *an automated check
> passed at the moment of the run*. It says nothing about whether anybody **looked**
> after it shipped, nor whether it still works N releases later, and it dies with its
> run. This file is the column that outlives it.

## Producer — what wrote the rows below

Computed, never typed, and every field prints even when it cannot be resolved:

```bash
python3 scripts/graph.py producer      # from the project root
```

```text
actor: unavailable: TASK_PIPELINE_ACTOR is not set by this harness
model: unavailable: TASK_PIPELINE_MODEL is not set by this harness
runtime: unavailable: TASK_PIPELINE_RUNTIME is not set by this harness
skill: task-pipeline@1.69.0
config: sha256:3bb638e189c9ef46
commit: fbd8a67e6988a0893f273eb37bd9a075a036c223
trace: unavailable: TASK_PIPELINE_TRACE is not set by this harness
```

**Paste one such block per run, above the rows that run wrote.** Without it, two runs six
months apart under different generations of this doctrine leave rows nobody can tell
apart — so a defect traced to a doctrine change cannot be scoped to the runs that carried
it. `skill`, `config` and `commit` resolve from the tree; `actor`, `model`, `runtime` and
`trace` are the harness's to export, and each says so by name when unset, because a field
that vanishes when unavailable is indistinguishable from one nobody checked.

**A field is never deleted and never guessed.** `model` in particular is not inferred:
naming a vendor id in a shipped skill is forbidden here, and inferring the wrong one is
worse than saying nothing.

## Contents

- [Staleness — a row is true about the tree it OBSERVED](#staleness--a-row-is-true-about-the-tree-it-observed)
- the ledger itself — one row per REQ, appended by stage 8
- [What `Human` means, and what it does not](#what-human-means-and-what-it-does-not)

## Staleness — a row is true about the tree it OBSERVED

`Observed at` is the commit the check ran against. Without it a row verified at commit A
reads `verified` after commit B forever, and the ledger tracks rows nobody ever confirmed
while having no notion of a row the tree has since **overtaken**. Those are the same
failure from two ends, and only one end was instrumented.

`scripts/exposure.sh` reports four states, and it is a **disclosure**: no floor, no
direction, never a target — for the same reason the `Human` column has none.

| State | Condition | What it means |
|---|---|---|
| **current** | 0 commits behind `HEAD` | the row still speaks about this tree |
| **behind** | N commits / M days behind | *not trusted for the current tree until re-observed* |
| **unresolvable** | the commit does not resolve here | rebase, squash or shallow clone — same marker |
| **unanchored** | no commit recorded | nothing can say what it saw |

**State zero prints out loud.** `current 12 · behind 0 · unresolvable 0 · unanchored 0` is
a measurement; printing nothing when everything is fresh is what makes freshness
indistinguishable from a check that never looked.

**Invalidation is not deletion.** An overtaken row is not wrong — it is true about the tree
it observed, and it stays. Re-observing appends a **new** row; it does not edit the old
one. Four things overtake a row, and naming which one applies is the note's job: a **code**
change in what it covers, a **dependency** change, an **environment** change, and a
**policy** change — the last being the rule under which the evidence was accepted.

| REQ | What | Run | Shipped in | Observed at | Auto | Human | Note |
|---|---|---|---|---|---|---|---|
| REQ-001 | CSV export from a report | `2026-07-28-export` | v1.4.0 | `5f21ac3` | pass | 2026-07-30 | opened the deployed page, exported, opened the file |
| REQ-004 | XLSX export | `2026-07-28-export` | v1.4.0 | `5f21ac3` | pass | **never** | — |
| REQ-007 | Export respects active filters | `2026-07-28-export` | v1.4.0 | `5f21ac3` | partial | **never** | CSV path only |

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
