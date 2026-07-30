---
description: Run a task through task-pipeline — an intake grill that expands the request, then docs → brainstorm → spec → plan → build → tests → deploy → post-deploy → docs/wiki → acceptance.
argument-hint: "<one-line task description>"
---
Use the `task-pipeline` skill to run the task below through all gated stages —
**stage 0 intake grill** → docs study → brainstorm → spec → plan → subagent
build → tests → lint/deploy → post-deploy → docs/wiki → **acceptance**. **Every stage's doctrine is
built into the skill** (`references/{knowledge-sources,grill,brainstorm,decomposition,spec,planning,build,review,tdd,acceptance,loop-guard}.md`)
— no companion plugin is required for any of them. **Stage 0 opens with the
knowledge harvest, before the first question** (`references/knowledge-sources.md`):
pull what the project already knows about this task from the code, `CLAUDE.md`,
`CONTEXT.md`/ADRs, `docs/` + `docs/ux/`, past pipeline briefs, the **knowledge wiki**
if one is installed ([obsidian-wiki](https://github.com/ar9av/obsidian-wiki) —
recommended, never required; detect `~/.obsidian-wiki/config`) and any **other repo
or hosted doc system the project names as its docs**, then write the **source
ledger** into the brief. The **intake grill is
mandatory** (`references/grill.md`): interview the
operator one question at a time (with a recommended answer each, exploring the
codebase before asking) until every decision branch is resolved, **validating every
answer against the harvested sources** — the operator outranks any document, but
only out loud, and a doc the run proves stale is logged for the stage-9 update —
applying the
grill's **domain awareness** (challenge terms against `CONTEXT.md`, sharpen fuzzy
language, ADRs for hard-to-reverse calls) and covering the **autonomy sweep** (what
would otherwise stop stages 1→10: docs sources incl. doc repos and the wiki, branch/tracker
policy, test and lint commands, deploy target and authorization, log locations, docs/wiki targets, and for UI tasks whether the design is done visually in Figma or text-only, whether the Figma MCP is connected, and — if it isn't — whether to ship text-only or stop and connect it, since the UX chain degrades on its own and never blocks; **and with Figma on, the design destination: which team/org by name and which file** — the recorded one, a URL the operator gives, or creation in that named team explicitly authorized, written into the project's canonical record before the first frame, because a destination decided at drawing time is how a project ends up with three design files and no way to tell which is real. **Never create while a recorded file resolves; if it doesn't resolve, stop and ask — never create a replacement**) —
until the brief is locked — including the **REQ table**, the request as an addressable list where every row names how it is verified — so the rest runs autonomously and the final stage can account for all of it. The list is frozen: adding is free, removing needs the operator's agreement. Anything deferred goes into the carry-over ledger the moment it's said. For any user-facing task, recommend/use
**super-ux**. **If the brief describes a platform rather than a change**, stage 2 also cuts it into modules (`references/decomposition.md`) — module map committed, walking skeleton first, every REQ in exactly one module — and stages 3→10 then run per module, one brick at a time. **If any loop starts undoing an earlier pass** (same file edited twice for the same reason, a closed finding returning, a third entry into one stage), stop and run the loop guard (`references/loop-guard.md`): name both shapes, escalate to the layer that owns the conflict, re-plan the check as an ordered list, then go item by item. **The closing stage opens with the ladder walk** (`references/audit.md`): the REQ table finds what was named and lost, but a comparison needs two sides and an absence has one — so walk each REQ bottom-up through its rungs (decision → spec section → contract *and its failure behavior* → task → change → executed test → surface/docs), check the seam at each step, order findings by seam rather than by file, and turn every absence into a new REQ row **before** the coverage table is written. A green from a check nobody has watched fail against a planted defect is not evidence; a finding class seen twice becomes a script rather than a third ledger row; and the carry-over ledger's counts are printed beside every gate verdict, so "green" never reads as "verified". If a searching pass starts finding mostly what the previous pass's own fixes broke, the axis is exhausted — rotate it, don't look harder. **In a project of several repositories, stage 10 closes on the parent too:** a parent records each submodule as a pointer to one commit, and moving the submodule does not move the pointer — so the work can be committed, pushed and green while a clone of the parent still gets the commit before it. Neither repo looks wrong alone, which is why it survives every check that runs inside one. Require `git submodule status` with no line starting `+`, and every repo clean and pushed (`git -C <repo> status --porcelain`, `git -C <repo> log @{u}..HEAD`). The fix is two commands and the second gets forgotten: push the submodule, then `git add <submodule> && git commit`. Honor every stage gate by its type (`auto` = verify yourself;
`manual` = wait for explicit go). Confirm the **model once at preflight** —
recommend the most capable one the environment offers, never a hardcoded id — then
run the whole pipeline on it without re-asking.

Task: $ARGUMENTS

Idempotent entry — inspect state first, never restart blindly:
- If a pipeline TaskList from a previous run already exists for this task,
  **resume** from the first incomplete stage instead of starting over.
- Otherwise, begin at stage 0 (intake grill). If no task is given above, the
  grill's first question asks the operator for the task in one line.
