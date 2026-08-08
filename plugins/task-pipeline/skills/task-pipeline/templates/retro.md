# Pipeline retrospective — <project>

One file per project, not per run. Written as the **last act of stage 10**:
**stamp first, then prune**, then write an entry **only if the run diverged**.
The order is load-bearing: the cold-retirement trigger reads the stamp this stage
writes, so a prune ahead of it can never run on real data (`learned.md` rule 21).
Doctrine: `references/retrospective.md`.

**What stage 0 reads in full:** *Standing instructions*, *Run stamps* and *Recent
log* — all three are bounded by construction, which is why the cap is not
negotiable. The **archive** (`docs/superpowers/retro/YYYY-QN.md`) is *queried* by
the task's nouns and never read end to end.

## Standing instructions (max 10 — in force right now)

Every row is a rule an agent must follow, that **no check can decide**. A rule a
check *can* decide is not written here: it is written as the check (grade 1).
No row is accepted without its **retire-when** trigger, written at birth.

Two SHA columns, and they are not bookkeeping: a `file:line` rots at the next edit,
while `git show <sha>` reconstructs the whole incident months later. Every SHA here
must resolve — the documentation gate runs `git rev-parse --verify` over all of
them.

| id | Born | Commit | Instruction | Because | Retire when | Last fired | Fired at |
|---|---|---|---|---|---|---|---|
| R-001 | 2026-05-04 · `<topic>` | `<sha>` | … | … (one line; links the archive entry) | … (e.g. "the export path is covered by a test") | 2026-06-18 | `<sha>` |

Retire on **any** of: it became a check · every path/command it names is gone · it
has not fired in the last five run stamps, or in the last sixty days. At eleven rows, the oldest never-fired
row goes — the cap is not negotiable, ranking is.

## Recent log — entries from the last five run stamps (newest first)

Older entries and every retirement **move** to `docs/superpowers/retro/YYYY-QN.md`
at the prune. Moving is not deleting: the archive is append-only and holds the
incident forever, so pruning the in-force list costs no knowledge. This section
stays short precisely so that reading it in full at stage 0 stays cheap.

### 2026-05-04 · `<topic>` · gate 6 reopened twice

- **Symptom:** … (one line + evidence — a command, a `file:line`, the gate)
- **Surfaced at:** stage 6 · **Owned by:** stage 4 (the plan never named the check)
- **Root cause:** … (why the pipeline permitted it — "the agent was careless" is
  not a cause; it is the absence of one, and it produces no fix)
- **Fix:** grade 1 (mechanical) — … / grade 2 → `R-00N` / grade 3, expires in
  2 runs
- **The check:** … (what catches this the first time, from now on)
- **Commit:** `<sha>` — the change that fixed it
- **Upstream?** … (a lesson true in any repo belongs in the skill's own
  `references/learned.md` — open an issue and say so here)

### Retirements

One line each, newest first. A retirement is a record, not a section — so it is a
list item. A heading promises a body, and a heading with nothing under it is the
shape the hygiene gate's check 6 exists to find.

- 2026-05-04 · retired R-000 — became a check (`npm run lint:paths`) · `<sha>`

## Run stamps

One line per run, appended at stage 10. This is what makes "five runs" countable
— without it the cold-rule is a guess and the prune becomes a mood.

| Date | Topic | Commit | Verdict | Retro |
|---|---|---|---|---|
| 2026-05-04 | `<topic>` | `<sha>` | 14/14 verified | 1 entry · 7 standing (was 9) · retired 3 · added 1 |
| 2026-05-02 | `<topic>` | `<sha>` | 9/9 verified | no divergence · 9 standing · retired 0 |

The `Commit` column is what turns a stamp from a date into a navigable point in
history: `git show <sha>` is the run, and `git log <sha>..HEAD` is everything that
happened since a rule last fired.
