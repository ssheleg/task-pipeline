---
description: Run a task through task-pipeline — an intake grill that expands the request, then docs → brainstorm → spec → plan → build → tests → deploy → post-deploy → docs/wiki.
argument-hint: <one-line task description>
---
Use the `task-pipeline` skill to run the task below through all gated stages —
**stage 0 intake grill** → docs study → brainstorm → spec → plan → subagent
build → tests → lint/deploy → post-deploy → docs/wiki. The **intake grill is
mandatory** — never skip it: interview the operator one question at a time (with a
recommended answer each, exploring the codebase before asking) until every decision
branch is resolved, the **autonomy sweep** is covered (what would otherwise stop
stages 1→9: docs sources, branch/tracker policy, test and lint commands, deploy
target and authorization, log locations, docs/wiki targets) and the brief is locked
— so the rest runs autonomously. For any user-facing task, recommend/use
**super-ux**. Honor every stage gate by its type (`auto` = verify yourself;
`manual` = wait for explicit go). Confirm the **model once at preflight** —
recommend the most capable one the environment offers, never a hardcoded id — then
run the whole pipeline on it without re-asking.

Task: $ARGUMENTS

Idempotent entry — inspect state first, never restart blindly:
- If a pipeline TaskList from a previous run already exists for this task,
  **resume** from the first incomplete stage instead of starting over.
- Otherwise, begin at stage 0 (intake grill). If no task is given above, the
  grill's first question asks the operator for the task in one line.
