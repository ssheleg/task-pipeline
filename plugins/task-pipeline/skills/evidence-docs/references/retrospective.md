# Retrospective: pointer

The retrospective doctrine has one home:
[task-pipeline's `references/retrospective.md`](https://github.com/ssheleg/task-pipeline/blob/main/plugins/task-pipeline/skills/task-pipeline/references/retrospective.md).
With the task-pipeline plugin installed, the same file sits beside this skill at
`skills/task-pipeline/references/retrospective.md`. Until 1.98.0 this file was a
34.7 KB copy of it with no delta of its own; a copy is a second thing to keep true.

What evidence-docs relies on from it, in short:

- **One file per project**, `docs/evidence/retro.md`, written as stage 10's last act:
  stamp the run first, then prune, then write an entry only if the run diverged.
- **The floor stage 0 reads in full** (standing instructions, max ten rows; run stamps,
  max ten lines) stays under a 12 000-byte budget: a standing row at most 600
  characters, a stamp at most 300. `scripts/retro_budget.py check` measures it.
- **Every lesson carries its commit**, and every SHA must resolve from `HEAD`.
- **Each entry names its Class and its Cost**; recurrence is counted by class.
- **A universal rule is cited by its [`learned.md`](learned.md) number**, never
  restated; a lesson standing in two projects goes upstream in the same run.

evidence-docs-specific delta: none.
