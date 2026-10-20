---
description: "Run a task through task-pipeline's gated stages (intake grill → docs → brainstorm → spec → plan → build → tests → deploy → post-deploy → docs/wiki → acceptance). Also: `waves` — close the whole board in waves; `iteration` — the release loop around the waves; `setup` — audit the docs you already have; `checkup` — what has shipped unverified, with no task running."
argument-hint: "<one-line task> | waves | iteration | setup | checkup"
---
Run the task below through the `task-pipeline` skill. **Read its `SKILL.md` and follow
it**; this page is a pointer, not a second copy of the run order (until 1.98.0 it was a
13 KB restatement read on top of `SKILL.md` before any work).

Task: $ARGUMENTS

- **Resume, never restart blindly.** If `.task-pipeline/run.md` or a pipeline task
  list exists for this task, continue from the first incomplete stage.
- **No task given?** Ask for it in one line.
- **Proportional.** Stage 0's gap check decides: a small change takes the short path
  and says so in one line; anything larger runs the full flow
  (`references/stage-00-intake.md` → Phase 1d).
- **Modes.** `waves`: the whole board (`references/waves.md`). `iteration`: the
  release loop around the waves (`references/iteration.md`). `setup`: audit the
  documentation the project already has (`references/setup.md`). `checkup`: what has
  shipped with no person confirming it, with no task in flight
  (`references/verification.md`).
