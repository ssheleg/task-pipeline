---
description: "Run a task through task-pipeline's gated stages (intake grill → docs → brainstorm → spec → plan → build → tests → deploy → post-deploy → docs/wiki → acceptance). Also: `waves` — close the whole board in waves; `iteration` — the release loop around the waves; `setup` — audit the docs you already have; `checkup` — what has shipped unverified, with no task running."
argument-hint: "<one-line task> | waves | iteration | setup | checkup"
---
Run the task below through the `task-pipeline` skill: read its `SKILL.md` and follow
it. This page points into the skill; it is not a second copy of the run order.

Task: $ARGUMENTS

- **Resume, never restart blindly.** If `.task-pipeline/run.md` or a pipeline task
  list exists for this task, continue from the first incomplete stage.
- **No task given?** Ask for it in one line. That is the only stop this page adds;
  every other stop, and what is not one, is in `SKILL.md`.
- **Proportional.** Stage 0's gap check decides: a small change takes the short path
  and says so in one line; anything larger runs the full flow
  (`references/stage-00-intake.md` → Phase 1d).
- **Modes**, each with what it ends on:
  - `waves`: the whole board, until it is empty or every remaining node is parked
    with its reason (`references/waves.md`).
  - `iteration`: the release loop around the waves, until the release ships, its
    post-release check is read and the next pool is handed back
    (`references/iteration.md`).
  - `setup`: an audit of the documentation the project already has, until its plan
    file is written and its findings are filed (`references/setup.md`).
  - `checkup`: what has shipped with no person confirming it, with no task in
    flight; it prints every section, zeros included, and writes nothing
    (`references/exposure.md` → *`/task-pipeline checkup`*).
- **Close** with the hand-back: what is blocked on the operator first, then what
  changed, what was found and what could not be confirmed.
