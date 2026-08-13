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

## Contents

- Lines
- Log
- Why it is not the build ledger
- What closes it, and what survives it

## Lines

Append-only. These shapes, and nothing else belongs here (the list is the count — a written one drifts, and this one already had):

```
stage: <id> <name> — gate <auto|manual> — verdict <pass|fail|skip> — <ISO-8601>
iter:  <N> — item <B-NNN or task id> — closed at gate <stage id>
touch: <file> — pass <N> (<stage|round|module>) — reason: <finding id / gate item>
hand:  <N|10> — task "<quoted>" — done <n> — surfaced <n> — decisions <n> — amb <n> (<ids or "— no register">)
holds: <stage id> — <n> (<class: what, owner>; … or "none") — enumerated <n>/8 classes, <unlooked: classes not enumerable>
gate:  <stage id> — command "<cmd>" — exit <N> — <ISO-8601>
event: <compact|session-end|subagent> — <detail> — <ISO-8601>
```

- **`stage:`** — written when a gate **returns**, not when the stage is entered. The
  rail's `✓` is derived from this line and from nothing else; a glyph set from memory
  is a summary that is confidently wrong exactly when it matters.
- **`gate:`** — written by `hooks/gate-observer.sh`, never by an agent. It is the
  only line here that records what a command **did** rather than what somebody
  concluded: the exit code of the stage's declared `gate.command`, observed. The
  `stage:` line above it is the agent's claim, and the release gate requires the
  two to agree — without this, a gate reads a claim written by the party it
  constrains and confirms an assertion with itself. Absent where the project
  declares no command, and the release gate then degrades to the claim alone.

- **`event:`** — written by `hooks/run-lifecycle.sh`, the three moments this file
  otherwise cannot show. `compact` marks the boundary the ledger exists *because
  of* — without it a resumed run cannot tell a compaction from nothing happening.
  `session-end` marks a run whose session ended without reaching acceptance, which
  is what `/task-pipeline checkup` looks for and what was previously invisible: the
  ledger simply stopped, and a stopped ledger looks exactly like a run still in
  progress. `subagent` records one finishing, so the `hand:` count below has
  something to be checked against other than itself.

  **It never writes a `hand:` line.** That shape carries `done`, `surfaced`,
  `decisions` and `amb` — judgements only the agent holds, and a hook filling them
  in would fabricate the evidence the line exists to provide.

- **`iter:`** — one line per iteration closed. The progress line's counter is
  `grep -c '^iter:'`, never a number anyone remembers.
- **`hand:`** — one per hand-back, at an iteration's close and at stage 10
  (`references/progress.md` → *The hand-back*, inside the skill). The
  narrative goes to the operator; **this line is the trace it leaves**, and it exists
  because v1.43.0 shipped a gate criterion with no artefact behind it: every guard could
  check that the instruction was still written, and none could check that a run obeyed
  it. A later audit reads `grep -c '^hand:'` against `grep -c '^iter:'` and the two
  should agree, plus one for stage 10.
  **`amb` prints its ids or `— no register`, never a bare `0` with nothing beside it.**
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
event: compact — auto — 2026-08-10T11:58Z
event: subagent — general-purpose — 2026-08-10T12:00Z
gate:  6 — command "npm test" — exit 0 — 2026-08-10T12:02Z
stage: 6 Tests — gate manual — verdict pass — 2026-08-10T12:03Z
hand:  3 — task "add CSV export to the orders table" — done 2 — surfaced 1 — decisions 1 — amb 2 (OQ-0007, ledger row 4)
holds: 5 — 2 (worktree: build-csv-export, this run; container: pg-test, this run) — enumerated 8/8 classes
holds: 10 — none — enumerated 7/8 classes, unlooked: containers (no docker on this host)
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
