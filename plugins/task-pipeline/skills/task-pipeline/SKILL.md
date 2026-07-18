---
name: task-pipeline
description: "Orchestrates a task through the full end-to-end delivery pipeline — docs study, brainstorm, spec, plan, subagent-driven build, test suite, lint/deploy, post-deploy log check, and docs/wiki sync — as nine gated stages built on the superpowers skills. Use when the user wants to run a task through the pipeline, asks for the full cycle / полный цикл / прогони по конвейеру, invokes /task-pipeline, or starts any substantial feature, fix, or build that should follow the disciplined cycle rather than ad-hoc coding. Reminds which model to switch to per stage; reads host-project conventions for deploy/docs/wiki so it stays project-agnostic."
---

# task-pipeline

Thin orchestrator. Runs a task through **9 gated stages**, each built on an
existing skill. Keeps the main thread disciplined: no stage advances until its
gate passes; each stage names the model to use.

## Prerequisite

Requires the **superpowers** skills. Preflight: confirm `superpowers:brainstorming`,
`superpowers:writing-plans`, `superpowers:subagent-driven-development`,
`superpowers:using-git-worktrees`, `superpowers:test-driven-development` resolve.
If missing → tell the operator to install from **https://github.com/obra/superpowers**
(`/plugin marketplace add obra/superpowers` → `/plugin install superpowers@superpowers`)
and stop.

## How to run

1. Restate the task in one line. Create a **TaskList: one task per stage** (survives
   context loss; lets you resume).
2. Walk stages 1→8. Before each: **model check** (see `references/model-tiering.md`) —
   if recommended ≠ current, emit the reminder block and wait for the operator to `/model`.
3. Do **not** advance until the stage **gate** passes (`references/stages.md`).
4. Cross-cutting, every stage: task tracker + conventional commits per host
   conventions; worktree isolation for the build; honest degradation (never claim a
   failed/skipped step succeeded); outward/irreversible actions (deploy, publish,
   repo create) need explicit operator go.

## Stages (detail in `references/stages.md`)

| # | Stage | Model | Invoke | Gate |
|---|---|---|---|---|
| 1 | Docs study | Fable | `context7` (resolve-library-id → get-library-docs) / `context7-docs` | contracts grounded on fetched docs |
| 2 | Brainstorm | Fable | `superpowers:brainstorming` | design approved by user |
| 3 | Spec | Fable | brainstorming writes `docs/superpowers/specs/…-design.md` | committed + user-reviewed |
| 4 | Plan | Fable | `superpowers:writing-plans` → `docs/superpowers/plans/…md` | parallel-ready, DoD per task |
| 5 | Dev | **Opus** | `superpowers:using-git-worktrees` + `superpowers:subagent-driven-development` (TDD) | tasks DONE, TDD green per task |
| 6 | Tests | **Opus** | host test runner + `superpowers:test-driven-development` | full suite green; new/changed code covered |
| 7 | Lint + deploy | host | host lint → deploy per host convention | lint clean + suite green before deploy; deploy needs go |
| 8 | Post-deploy | host | tail deploy logs / health-check | clean boot or honest degradation report |
| 9 | Docs + wiki | host | host module docs/runbook rules → `wiki-update` | docs synced, wiki synced |

## Model reminder (emit at a boundary when recommended ≠ current)

> ⏸ **Stage N (`<stage>`) recommends `<model>` (`<id>`).** You're on `<current>`.
> Switch: `/model <id>` — then say "continue". *(Reminder only — override if you
> don't have that model.)*

## References

- `references/stages.md` — per-stage detail + exact gate criteria
- `references/model-tiering.md` — model map, ids, the `/model` reminder mechanic, override
- `references/conventions.md` — how stages 6–9 read the host project's CLAUDE.md
