# Run ledger — `.task-pipeline/run.md`

> **One file per run.** Seeded at stage 0, appended by every stage, never rewritten.
> Two readers depend on it and neither can work from the agent's memory: the skill's
> `references/loop-guard.md` reads the `touch:` lines to detect churn mechanically, and
> its `references/progress.md` reads the `stage:` verdicts and the `iter:` count to
> print the rail.
>
> **This file is the run's memory after a compaction.** Everything else about the
> run's position lives in a context window that will not survive one.

Run: `<topic>` · started `<YYYY-MM-DD>` · module map: `<path or "none">`

## Lines

Append-only. Three shapes, and nothing else belongs here:

```
stage: <id> <name> — gate <auto|manual> — verdict <pass|fail|skip> — <ISO-8601>
iter:  <N> — item <B-NNN or task id> — closed at gate <stage id>
touch: <file> — pass <N> (<stage|round|module>) — reason: <finding id / gate item>
```

- **`stage:`** — written when a gate **returns**, not when the stage is entered. The
  rail's `✓` is derived from this line and from nothing else; a glyph set from memory
  is a summary that is confidently wrong exactly when it matters.
- **`iter:`** — one line per iteration closed. The progress line's counter is
  `grep -c '^iter:'`, never a number anyone remembers.
- **`touch:`** — one line per file per pass, and the reason names **what forced the
  edit**: a finding id, a failed gate item, an operator instruction. *"Cleanup"*,
  *"polish"* and *"while I was there"* are not reasons; they are churn with better
  manners.

A `skip` verdict carries its reason on the same line — a skipped stage and a stage
never entered look identical from outside, and they mean opposite things.

## Log

```
stage: 0 Intake — gate manual — verdict pass — 2026-08-10T11:14Z
iter:  1 — item B-025 — closed at gate 0
stage: 1 Docs study — gate auto — verdict pass — 2026-08-10T11:31Z
touch: src/export.ts — pass 1 (stage 5) — reason: TASK-3
touch: src/export.ts — pass 2 (stage 5) — reason: F-014
touch: src/export.ts — pass 3 (stage 5) — reason: F-014
```

The last two lines are a **trip**: the same file, two consecutive passes, the same
reason. `references/loop-guard.md` → *Detection* item 2 — the fix did not fix it, or
the two passes disagree about what *fixed* means. Stop editing and run the break
protocol; do not dispatch a fourth pass.

## Why it is not the build ledger

`.task-pipeline/build/<plan>/progress.md` covers **one stage** — stage 5's tasks, and
whether a task was already dispatched (`references/build.md`). This file
covers **the run**: stage verdicts, iterations, and every repeating pass anywhere in
the pipeline, including the loops between stages that the build ledger cannot see.

Keeping them separate is deliberate. A run that has no stage-5 work still loops, still
re-enters stages and still needs a rail — and it would have no ledger at all if the
run's memory lived inside the build directory that stage 5 deletes.

## What closes it, and what survives it

**This file is git-ignored** — `.task-pipeline/` is, and this lives inside it. It is
the run's working memory, not its record: it exists to survive a **compaction**, which
is a different problem from surviving the run.

So stage 10 **reads it and copies out what outlives the run** — the pass counts and
any loop-guard ruling go into the acceptance file and the retro stamp, which are
committed. What is not carried out is gone when the directory is cleared, and that is
the correct outcome for a `touch:` line whose finding has been closed.

Never treat it as evidence in a later run. A file that is not in git cannot be quoted
at a commit, and a claim nobody can navigate to is the thing this repository's
documentation canon exists to refuse.
