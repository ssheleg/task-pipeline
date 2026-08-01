# Pipeline retrospective — <project>

One file per project, not per run. Written as the **last act of stage 10**:
prune first, then stamp, then write an entry **only if the run diverged**.
Doctrine: `references/retrospective.md`.

Stage 0 reads *Standing instructions* in full, every run — which is why the list
has a hard cap of **ten**.

## Standing instructions (max 10 — in force right now)

Every row is a rule an agent must follow, that **no check can decide**. A rule a
check *can* decide is not written here: it is written as the check (grade 1).
No row is accepted without its **retire-when** trigger, written at birth.

| id | Born | Instruction | Because (incident) | Retire when | Last fired |
|---|---|---|---|---|---|
| R-001 | 2026-05-04 · `<topic>` | … | … (one line, links the log entry) | … (e.g. "the export path is covered by a test") | 2026-06-18 |

Retire on **any** of: it became a check · every path/command it names is gone · it
has not fired in the last five run stamps. At eleven rows, the oldest never-fired
row goes — the cap is not negotiable, ranking is.

## Log — problem → cause → fix (newest first)

Retirements are logged here too, one line each: *silent deletion is forbidden; the
record stays, the instruction leaves.*

### 2026-05-04 · `<topic>` · gate 6 reopened twice

- **Symptom:** … (one line + evidence — a command, a `file:line`, the gate)
- **Surfaced at:** stage 6 · **Owned by:** stage 4 (the plan never named the check)
- **Root cause:** … (why the pipeline permitted it — "the agent was careless" is
  not a cause; it is the absence of one, and it produces no fix)
- **Fix:** grade 1 (mechanical) — … / grade 2 → `R-00N` / grade 3, expires in
  2 runs
- **The check:** … (what catches this the first time, from now on)
- **Upstream?** … (a lesson true in any repo belongs in the skill's own
  `references/learned.md` — open an issue and say so here)

### 2026-05-04 · retired R-000 — became a check (`npm run lint:paths`)

## Run stamps

One line per run, appended at stage 10. This is what makes "five runs" countable
— without it the cold-rule is a guess and the prune becomes a mood.

| Date | Topic | Verdict | Retro |
|---|---|---|---|
| 2026-05-04 | `<topic>` | 14/14 verified | 1 entry · 7 standing (was 9) · retired 3 · added 1 |
| 2026-05-02 | `<topic>` | 9/9 verified | no divergence · 9 standing · retired 0 |
