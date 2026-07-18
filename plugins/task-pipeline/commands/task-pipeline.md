---
description: Run a task through the full 9-stage task-pipeline (docs → brainstorm → spec → plan → build → tests → deploy → post-deploy → docs/wiki).
argument-hint: <one-line task description>
---
Use the `task-pipeline` skill to run the task below through all **nine gated
stages** — docs study → brainstorm → spec → plan → subagent build → tests →
lint/deploy → post-deploy → docs/wiki. Honor every stage gate (never advance a
red gate) and emit the per-stage model reminder when the recommended model
differs from the current one.

Task: $ARGUMENTS

If no task is given above, ask the operator for the task in one line before
starting stage 1.
