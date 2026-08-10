# Retro archive — <project> · <YYYY>-Q<N>

**Append-only. Queried, never read in full.** The in-force list
(`docs/superpowers/retro.md`) is capped at ten and read whole at stage 0; this file
is where entries and retirements go when they age out, so pruning stops losing
things. Doctrine: `references/retrospective.md`.

Stage 0's harvest **queries** this file by the task's nouns — it is the source that
answers *"have we been bitten by this class before?"*. It is never read end to end;
that is what the cap on the in-force list is for.

**Every entry carries a commit.** A `file:line` rots at the next edit; a SHA carries
the diff, the message and the parent forever, and `git show <sha>` reconstructs the
whole incident two months later when the class comes back. Every SHA here must
resolve — the documentation gate checks it.

## Entries

### <YYYY-MM-DD> · `<topic>` · <one-line symptom>

- **Symptom:** … (with evidence — a command, a `file:line`, the gate that reopened)
- **Surfaced at:** stage <N> · **Owned by:** stage <M> (the stage that let it
  through — usually an earlier one)
- **Root cause:** … ("the agent was careless" is not a cause; it is the absence of
  one, and it produces no fix)
- **Fix:** grade 1 (mechanical) — … / grade 2 → `R-00N` / grade 3, expires in 2 runs
- **The check:** … (what catches this the first time, from now on)
- **Commit:** `<sha>` — the change that fixed it (a real short SHA, and it must
  resolve: the gate runs `git rev-parse --verify` over every one)
- **Upstream?** … (a lesson true in any repository belongs in the skill's own
  `references/learned.md` — open an issue and say so here)

## Retirements

One line each. Silent deletion is forbidden: the record stays, the instruction
leaves. A retired rule that returns as a real failure is a grade-1 fix — **with its
history attached**, which is what this section is for.

| Date | id | Instruction | Trigger that retired it | Commit |
|---|---|---|---|---|
| <YYYY-MM-DD> | R-000 | … | became a check (`npm run lint:paths`) | `<sha>` |

## Run stamps

Rotated out of `retro.md` when its live table passes ten. Append-only, whole rows —
the cold trigger reads the last five in the live file, so a stamp here is one it no
longer needs. Moving is not deleting: a stamp that leaves `retro.md` and appears
nowhere is history destroyed, not archived.

| Date | Topic | Commit | Verdict | Retro |
|---|---|---|---|---|
