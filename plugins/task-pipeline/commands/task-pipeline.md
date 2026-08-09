---
description: Run a task through task-pipeline — an intake grill that expands the request, then docs → brainstorm → spec → plan → build → tests → deploy → post-deploy → docs/wiki → acceptance.
argument-hint: "<one-line task description>"
---
Use the `task-pipeline` skill to run the task below through all gated stages —
**stage 0 intake grill** → docs study → brainstorm → spec → plan → subagent
build → tests → lint/deploy → post-deploy → docs/wiki → **acceptance**. **Every stage's doctrine is
built into the skill** (`references/{knowledge-sources,knowledge-graph,grill,brainstorm,decomposition,spec,planning,build,review,tdd,acceptance,retrospective,loop-guard}.md`)
— no companion plugin is required for any of them. **Stage 0 opens with the
knowledge harvest, before the first question** (`references/knowledge-sources.md`):
pull what the project already knows about this task from the code, **the code graph**
if one is built ([graphify](https://github.com/Graphify-Labs/graphify) —
`references/knowledge-graph.md`; recommended, never required; detect
`graphify-out/graph.json`; it answers *reach* — what calls this, what breaks if it
moves — which grep cannot), `CLAUDE.md`,
`CONTEXT.md`/ADRs, `docs/` + `docs/ux/`, past pipeline briefs, **the retro's standing
instructions** (`docs/superpowers/retro.md` — read in full, they bind this run;
`references/retrospective.md`), the **knowledge wiki**
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
would otherwise stop stages 1→10: docs sources incl. doc repos, the wiki and the code graph, branch/tracker
policy, test and lint commands, deploy target and authorization, log locations, docs/wiki/graph targets, and for UI tasks whether the design is done visually in Figma or text-only, whether the Figma MCP is connected, and — if it isn't — whether to ship text-only or stop and connect it, since the UX chain degrades on its own and never blocks; **and with Figma on, the design destination: which team/org by name and which file** — the recorded one, a URL the operator gives, or creation in that named team explicitly authorized, written into the project's canonical record before the first frame, because a destination decided at drawing time is how a project ends up with three design files and no way to tell which is real. **Never create while a recorded file resolves; if it doesn't resolve, stop and ask — never create a replacement**) —
until the brief is locked — including the **REQ table**, the request as an addressable list where every row names how it is verified — so the rest runs autonomously and the final stage can account for all of it. The list is frozen: adding is free, removing needs the operator's agreement. Anything deferred goes into the carry-over ledger the moment it's said, and **the board** (`docs/superpowers/backlog.md`, `references/backlog.md`) — the work-list between runs — is read at stage 0 with its open count quoted in the brief, or seeded when absent; **the verification ledger** (`docs/superpowers/verification.md`, `references/verification.md`) is read at stage 0 for how many rows sit at `never`, written at stage 8 with one row per shipped REQ, and required at stage 10 in both directions. For any user-facing task, recommend/use
**super-ux**. **If the brief describes a platform rather than a change**, stage 2 also cuts it into modules (`references/decomposition.md`) — module map committed, walking skeleton first, every REQ in exactly one module — and stages 3→10 then run per module, one brick at a time. **If any loop starts undoing an earlier pass** (same file edited twice for the same reason, a closed finding returning, a third entry into one stage), stop and run the loop guard (`references/loop-guard.md`): name both shapes, escalate to the layer that owns the conflict, re-plan the check as an ordered list, then go item by item. **The closing stage opens with the ladder walk** (`references/audit.md`): the REQ table finds what was named and lost, but a comparison needs two sides and an absence has one — so walk each REQ bottom-up through its rungs (decision → spec section → contract *and its failure behavior* → task → change → executed test → surface/docs), check the seam at each step, order findings by seam rather than by file, and turn every absence into a new REQ row **before** the coverage table is written. A green from a check nobody has watched fail against a planted defect is not evidence; a finding class seen twice becomes a script rather than a third ledger row; and every ledger row still `open`, `unresolved` or homed `backlog` leaves stage 10 with a board id and the board's priorities are re-derived (`references/backlog.md`); the carry-over ledger's counts are printed beside every gate verdict, so "green" never reads as "verified". If a searching pass starts finding mostly what the previous pass's own fixes broke, the axis is exhausted — rotate it, don't look harder. **The docs stage closes three artifacts, not two:** module docs, the wiki, **and the code graph** (`/graphify . --update` where `graphify-out/` exists — `references/knowledge-graph.md`), because the graph is what the next run's harvest queries first and a stale one is a false premise carrying the authority of a machine. Then check the graph against the docs: a hub `graphify god-nodes` reports that no document names is an undocumented seam; an edge the docs deny is a leak in the code or a lie in the docs; a doc naming a module the graph no longer has is stale. Doc-side findings are fixed there, absences become REQ rows in the closing stage. **In a project of several repositories, stage 10 closes on the parent too:** a parent records each submodule as a pointer to one commit, and moving the submodule does not move the pointer — so the work can be committed, pushed and green while a clone of the parent still gets the commit before it. Neither repo looks wrong alone, which is why it survives every check that runs inside one. Require `git submodule status` with no line starting `+`, and every repo clean and pushed (`git -C <repo> status --porcelain`, `git -C <repo> log @{u}..HEAD`). The fix is two commands and the second gets forgotten: push the submodule, then `git add <submodule> && git commit`. **The run's last act is the retrospective** (`references/retrospective.md` → `docs/superpowers/retro.md`, one file per project): **stamp the run first** (its commit is what makes the cold-retirement trigger computable), **then prune** — every standing instruction against its three retirement triggers (it became a check; the paths/commands it names are gone; it hasn't fired in five run stamps, or in sixty days — the calendar is the unit that still moves when the stamp counter has stopped), the list held to a hard cap of ten, every deletion logged as one line and never silent — then, only if the run diverged, write the entry: symptom with evidence, the stage it surfaced at, the stage that *owned* it, the root cause, the fix by grade (mechanical check > standing instruction > note that expires in two runs), and the check that catches it next time. Stage 0 reads those standing instructions in full, so the prune is a gate criterion, not a good intention: a rule nobody reads to the end is worse than no rule, because everyone believes it is covered. Honor every stage gate by its type (`auto` = verify yourself;
`manual` = wait for explicit go). Confirm the **model once at preflight** —
recommend the most capable one the environment offers, never a hardcoded id — then
run the whole pipeline on it without re-asking.

Task: $ARGUMENTS

Idempotent entry — inspect state first, never restart blindly:
- If a pipeline TaskList from a previous run already exists for this task,
  **resume** from the first incomplete stage instead of starting over.
- Otherwise, begin at stage 0 (intake grill). If no task is given above, the
  grill's first question asks the operator for the task in one line.

**`/task-pipeline setup`** — the entry audit instead of a feature. Runs seven passes
over the documentation this project already has, reports findings as `file:line` + the
minimal fix ordered by seam, and hands back a fix plan the pipeline can run. Offered
once at stage 0 when the doc map is absent or stale; run it directly any time.
Doctrine: `references/setup.md`.
