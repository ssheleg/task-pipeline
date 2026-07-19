---
name: task-pipeline
description: "Orchestrates a task through the full end-to-end delivery pipeline — docs study, brainstorm, spec, plan, subagent-driven build, test suite, lint/deploy, post-deploy log check, and docs/wiki sync — as nine gated stages built on the superpowers skills. Use when the user wants to run a task through the pipeline, asks for the full cycle / полный цикл / прогони по конвейеру, invokes /task-pipeline, or starts any substantial feature, fix, or build that should follow the disciplined cycle rather than ad-hoc coding. Reminds which model to switch to per stage; reads host-project conventions for deploy/docs/wiki so it stays project-agnostic."
---

# task-pipeline

Thin orchestrator. Runs a task through **9 gated stages**, each built on an
existing skill. Keeps the main thread disciplined: no stage advances until its
gate passes; each stage names the model to use.

**Config contract: [`pipeline.schema.json`](pipeline.schema.json).** A pipeline is a machine-readable
config — an ordered list of stages, each with `skills[]` (the skills/agents that run it) and a
`gate {type, check}`. The schema is the universal contract; it imposes **no** specific stages, skills,
or gate assignments. [`pipeline.example.json`](pipeline.example.json) is a **copy-and-rewrite example**
(it happens to encode this plugin's own default superpowers flow). `test/validate.py` checks the
example against the schema. The 9 stages tabled below are that example — **any project replaces them
wholesale**: any number of stages, run by its own skills/agents, with its own gate types (see *Bring
your own skills*). Each gate has a **type**: `auto` (the orchestrator verifies the check itself,
pass/fail) or `manual` (wait for an explicit operator go); which stages are manual is the operator's
call, not the plugin's.

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
3. Do **not** advance until the stage **gate** passes (`references/stages.md`). Honor the gate
   **type** from `pipeline.json`: for `auto`, verify the gate's `check` yourself and stop/return on
   fail; for `manual`, present the result and **wait for the operator's explicit "continue"/go** — an
   auto gate never substitutes for a required manual approval.
4. Cross-cutting, every stage: task tracker + conventional commits per host
   conventions; worktree isolation for the build; honest degradation (never claim a
   failed/skipped step succeeded); outward/irreversible actions (deploy, publish,
   repo create) need explicit operator go.

## Stages (source: `pipeline.json`; detail in `references/stages.md`)

| # | Stage | Model | Invoke (skills) | Gate | Type |
|---|---|---|---|---|---|
| 1 | Docs study | Fable | `context7` (resolve-library-id → get-library-docs) / `context7-docs` | contracts grounded on fetched docs | auto |
| 2 | Brainstorm | Fable | `superpowers:brainstorming` | design approved by user | manual |
| 3 | Spec | Fable | brainstorming writes `docs/superpowers/specs/…-design.md` | committed + user-reviewed | manual |
| 4 | Plan | Fable | `superpowers:writing-plans` → `docs/superpowers/plans/…md` | parallel-ready, DoD per task | auto |
| 5 | Dev | **Opus** | `superpowers:using-git-worktrees` + `superpowers:subagent-driven-development` (TDD) | tasks DONE, TDD green per task | auto |
| 6 | Tests | **Opus** | host test runner + `superpowers:test-driven-development` | full suite green; new/changed code covered | auto |
| 7 | Lint + deploy | host | host lint → deploy per host convention | lint clean + suite green before deploy; deploy needs go | manual |
| 8 | Post-deploy | host | tail deploy logs / health-check | clean boot or honest degradation report | auto |
| 9 | Docs + wiki | host | host module docs/runbook rules → `wiki-update` | docs synced, wiki synced | auto |

## Bring your own skills

The stages and their `Invoke` skills above are just the **example** (superpowers + host conventions).
To run a **different** project: copy `pipeline.example.json` → `pipeline.json` in that project and
rewrite it — define the stages it actually has, run each by your own skills/agents (any names your
environment resolves) via `skills[]`, and set each `gate.type` (`auto`/`manual`) to fit its process.
Validate it against `pipeline.schema.json` (any JSON-Schema tool, or drop it where `test/validate.py`
looks). Nothing about the stage set, the skills, or which gates are manual is fixed — the framework
ships only the contract (`pipeline.schema.json`) and a worked example.

## Model reminder (emit at a boundary when recommended ≠ current)

> ⏸ **Stage N (`<stage>`) recommends `<model>` (`<id>`).** You're on `<current>`.
> Switch: `/model <id>` — then say "continue". *(Reminder only — override if you
> don't have that model.)*

## References

- `pipeline.schema.json` — the universal config contract (stage → skills[] → gate{type, check})
- `pipeline.example.json` — a copy-and-rewrite example config (this plugin's own default flow)
- `references/stages.md` — per-stage detail + exact gate criteria for the example flow
- `references/model-tiering.md` — model map, ids, the `/model` reminder mechanic, override
- `references/conventions.md` — how stages 6–9 read the host project's CLAUDE.md
