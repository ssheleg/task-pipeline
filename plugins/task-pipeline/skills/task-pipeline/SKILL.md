---
name: task-pipeline
description: "Orchestrates a task through the full end-to-end delivery pipeline — docs study, brainstorm, spec, plan, subagent-driven build, test suite, lint/deploy, post-deploy log check, and docs/wiki sync — as nine gated stages built on the superpowers skills. Use when the user wants to run a task through the pipeline, asks for the full cycle / полный цикл / прогони по конвейеру, invokes /task-pipeline, or starts any substantial feature, fix, or build that should follow the disciplined cycle rather than ad-hoc coding. Reminds which model to switch to per stage; reads host-project conventions for deploy/docs/wiki so it stays project-agnostic."
---

# task-pipeline

Thin orchestrator. Runs a task through **gated stages**, each built on an
existing skill. Keeps the main thread disciplined: no stage advances until its
gate passes; each stage names the model to use.

**Config contract: [`pipeline.schema.json`](pipeline.schema.json).** A pipeline is
a machine-readable config — an ordered list of stages, each with `skills[]` (the
skills/agents that run it) and a `gate {type, check}`. The schema is the universal
contract; it imposes **no** specific stages, skills, or gate assignments.
[`pipeline.example.json`](pipeline.example.json) is a **copy-and-rewrite example**
that encodes this plugin's own default flow (the 9 stages tabled below). Any
project replaces it wholesale — any number of stages, run by its own skills/agents,
with its own gate types (see *Bring your own skills*). Each gate has a **type**:
`auto` (the orchestrator verifies the `check` itself, pass/fail) or `manual` (wait
for an explicit operator go); which stages are manual is the operator's call.

## Prerequisite

Requires the **superpowers** skills. Preflight: confirm `superpowers:brainstorming`,
`superpowers:writing-plans`, `superpowers:subagent-driven-development`,
`superpowers:using-git-worktrees`, `superpowers:test-driven-development` resolve.
If missing → tell the operator to install from **https://github.com/obra/superpowers**
(`/plugin marketplace add obra/superpowers` → `/plugin install superpowers@superpowers`)
and stop.

For **user-facing tasks** (web/mobile/CLI/TUI) the spec stage additionally requires
the **super-ux** skills (`ux-foundation`, `ux-scenarios`, `/ux`) —
**https://github.com/ssheleg/super-ux**. Check only when stage 2 flags UI; if
missing then → tell the operator to install and stop.

## How to run

1. Restate the task in one line. Create a **TaskList: one task per stage** (survives
   context loss; lets you resume).
2. Walk stages 1→9. Before each: **model check** (see `references/model-tiering.md`) —
   if recommended ≠ current, emit the reminder block and wait for the operator to `/model`.
3. Do **not** advance until the stage **gate** passes (`references/stages.md`).
   Honor the gate **type**: for `auto`, verify the gate's `check` yourself and
   stop/return on fail; for `manual`, present the result and **wait for the
   operator's explicit "continue"/go** — an auto gate never substitutes for a
   required manual approval.
4. Cross-cutting, every stage: task tracker + conventional commits per host
   conventions; worktree isolation for the build; honest degradation (never claim a
   failed/skipped step succeeded); outward/irreversible actions (deploy, publish,
   repo create) need explicit operator go.

## Stages (detail in `references/stages.md`)

| # | Stage | Model | Invoke | Gate | Type |
|---|---|---|---|---|---|
| 1 | Docs study | Fable | `context7` (resolve-library-id → get-library-docs) / `context7-docs` | contracts grounded on fetched docs | auto |
| 2 | Brainstorm | Fable | `superpowers:brainstorming` + **UI detection** | design approved; UI verdict recorded | manual |
| 3 | Spec | Fable | **UI → super-ux first** (`/ux` → `ux-foundation` CJM → `ux-scenarios`), then spec `docs/superpowers/specs/…-design.md` | committed + reviewed; UI: scenarios validated + CJM traced | manual |
| 4 | Plan | Fable | `superpowers:writing-plans` → `docs/superpowers/plans/…md` | parallel-ready, DoD per task | auto |
| 5 | Dev | **Opus** | `superpowers:using-git-worktrees` + `superpowers:subagent-driven-development` (TDD) | tasks DONE, TDD green per task | auto |
| 6 | Tests | **Opus** | host test runner + `superpowers:test-driven-development` | full suite green; new/changed code covered | auto |
| 7 | Lint + deploy | host | host lint → deploy per host convention | lint clean + suite green before deploy; deploy needs go | manual |
| 8 | Post-deploy | host | tail deploy logs / health-check | clean boot or honest degradation report | auto |
| 9 | Docs + wiki | host | host module docs/runbook rules → `wiki-update` | docs synced, wiki synced | auto |

## Model reminder (emit at a boundary when recommended ≠ current)

> ⏸ **Stage N (`<stage>`) recommends `<model>` (`<id>`).** You're on `<current>`.
> Switch: `/model <id>` — then say "continue". *(Reminder only — override if you
> don't have that model.)*

## Bring your own skills

The 9 stages above are the **example** flow (superpowers + a super-ux UX track for
user-facing tasks + host conventions). A host project owns its pipeline: copy
`pipeline.example.json` → `pipeline.json`, then define its **own** stages (any
count), point each stage's `skills[]` at the skills/agents its environment
resolves, and set each `gate.type` (`auto`/`manual`) to fit its process. The
framework ships no fixed stage count and no opinion on which gates are manual —
`pipeline.schema.json` is the only contract.

## References

- `pipeline.schema.json` — the universal pipeline config contract
- `pipeline.example.json` — this plugin's default 9-stage flow, as config
- `references/stages.md` — per-stage detail + exact gate criteria + gate types
- `references/model-tiering.md` — model map, ids, the `/model` reminder mechanic, override
- `references/conventions.md` — how stages 6–9 read the host project's CLAUDE.md
