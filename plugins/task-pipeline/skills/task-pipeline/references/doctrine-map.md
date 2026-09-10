# The doctrine map — which reference owns which stage

Split out of `SKILL.md` on 2026-09-10, when its body measured 5429 tokens against the
house budget of 5000. Nothing here is new: it is the table that says where each stage's
built-in doctrine lives, so an agent loads the one file the stage needs instead of
carrying the whole index in every turn.

The rule the table serves stays in `SKILL.md`: every stage's doctrine ships inside this
skill, no stage blocks on an install, and the single deliberate exception is the stage-3
UX track on a user-facing task.

## Contents

- [Which reference owns which stage](#which-reference-owns-which-stage)

## Which reference owns which stage

| Stage | Built-in doctrine |
|---|---|
| 0, 9 · The documentation system | `references/documentation.md` |
| any stage · The canons, and where each is enforced | [`evidence-docs`](../../evidence-docs/SKILL.md) — the sibling skill in this plugin |
| 6–10 · Gates | `references/gates.md` |
| 7–8 · Deploy targets | `references/deploy-targets.md` |
| any stage · Hooks | `references/hooks.md` |
| 0 Knowledge harvest (pre-grill) | `references/knowledge-sources.md` |
| 0, 9 The code graph (graphify — recommended, never required) | `references/knowledge-graph.md` |
| 0 Intake grill | `references/grill.md` |
| 2 Brainstorm | `references/brainstorm.md` |
| 2 Decompose (platforms only) | `references/decomposition.md` |
| 3 Spec | `references/spec.md` |
| 4 Plan | `references/planning.md` |
| the queue the loop walks | `references/work-graph.md` |
| 5–8 · how a **work-graph node** is CLOSED — three blind readings at three distances, all three required (ceiling 3); a **prose-plan task** closes through `review.md` instead — one reviewer, five-round cap | `references/certification.md` |
| 5 Build (worktree, subagents, fix loop) | `references/build.md` + `references/review.md` |
| 5–6 TDD + suite gate | `references/tdd.md` |
| 5, 6, 8 The browser — the look, the spec suite, and the difference | `references/browser.md` |
| 10 Acceptance (REQ close-out) | `references/acceptance.md` |
| 10 Retrospective (the run's last act) | `references/retrospective.md` |
| 10 + any audit (what's *missing*) | `references/audit.md` |
| **first run in a project** (new or existing) | `references/adoption.md` |
| **first run · the entry audit** (offered once) | `references/setup.md` |
| **what travels with the bundle vs stays in a project** | `references/portability.md` |
| any repeating loop | `references/loop-guard.md` |
| run-wide · what the run **leaves running and leaves behind** — every gate, and stage 10 | `references/residue.md` |
| run-wide · what the run **prints about itself** — the rail, the iteration line | `references/progress.md` |
| run-wide · how a run keeps going (the loop mode + the context budget) | `references/continuity.md` |
| run-wide · the work-list **between** runs, and the order it comes off | `references/backlog.md` + `references/prioritisation.md` |
| run-wide · whether a **human** ever confirmed what shipped, and when | `references/verification.md` |
| run-wide · how much unconfirmed work has piled up, and what to look at first | `references/exposure.md` |
| any stage · Where each artifact belongs | `references/artifacts.md` |
| preflight · Companion skills and their fallbacks | `references/companion-skills.md` |
| 6–10 · How the host project's CLAUDE.md is read | `references/conventions.md` |
| preflight · Model map, ids and the override | `references/model-tiering.md` |
