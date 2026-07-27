---
name: task-pipeline
description: "Use when running a substantial task through the full end-to-end delivery pipeline — an up-front intake grill that expands the request into a complete brief, then docs study, brainstorm, spec, plan, subagent-driven build, test suite, lint/deploy, post-deploy log check, and docs/wiki sync — as gated stages built on the superpowers skills. Use when the user wants to run a task through the pipeline, asks for the full cycle / полный цикл / прогони по конвейеру, invokes /task-pipeline, or starts any substantial feature, fix, or build that should follow the disciplined cycle rather than ad-hoc coding. The intake grill is mandatory — it front-loads every decision, including the per-stage autonomy sweep, so stages 1→9 run without mid-flight questions; recommends super-ux for any user-facing task; confirms one model up front (most capable available, never a hardcoded id); reads host-project conventions for deploy/docs/wiki so it stays project-agnostic."
---

# task-pipeline

Thin orchestrator. Runs a task through **gated stages**, each built on an
existing skill. Keeps the main thread disciplined: no stage advances until its
gate passes; the whole run uses one model, confirmed before it starts.

**Grill first, then run autonomously.** A one-line task ("make me feature X") is
never enough to finish without a human in the loop. Stage 0 is **mandatory**: a
relentless, one-question-at-a-time interview that resolves every decision branch
*and* sweeps stages 1→9 for anything that would stop the run later — then locks
the answers into a brief. Autonomy is bought there or not at all; every question
skipped at stage 0 comes back as an interruption at stage 6.

**Config contract: [`pipeline.schema.json`](pipeline.schema.json).** A pipeline is
a machine-readable config — an ordered list of stages, each with `skills[]` (the
skills/agents that run it) and a `gate {type, check}`. The schema is the universal
contract; it imposes **no** specific stages, skills, or gate assignments.
[`pipeline.example.json`](pipeline.example.json) is a **copy-and-rewrite example**
that encodes this plugin's own default flow (stage 0 intake + the 1→9 stages
tabled below) and an optional, toggleable `release` block. Any project replaces it
wholesale — any number of stages, run by its own skills/agents, with its own gate
types (see *Bring your own skills*). Each gate has a **type**: `auto` (the
orchestrator verifies the `check` itself, pass/fail) or `manual` (wait for an
explicit operator go); which stages are manual is the operator's call.

## Prerequisite

Requires the **superpowers** skills. Preflight: confirm `superpowers:brainstorming`,
`superpowers:writing-plans`, `superpowers:subagent-driven-development`,
`superpowers:using-git-worktrees`, `superpowers:test-driven-development` resolve.
If missing → tell the operator to install from **https://github.com/obra/superpowers**
(`/plugin marketplace add obra/superpowers` → `/plugin install superpowers@superpowers`)
and stop.

**super-ux — recommended for ANY user-facing task.** The moment a task implies a
user interface (web / mobile / CLI / TUI — a screen, a command, a visible
behavior; the stage-0 grill detects this early), super-ux is the recommended
workflow for the WHY→UI→scenario chain (`/ux`, `ux-foundation`, `ux-flows`,
`ux-scenarios`, `/ux-lint`).
- **Already installed?** (does `/ux` or `super-ux:ux-foundation` resolve) → **use
  it**: `/ux` at intake, then the stage-3 UX track walks its traced chain —
  `ux-foundation` (personas, JTBD, CJM, stories) → `ux-flows` (user flows +
  `screens.md`, Figma frames when on) → `ux-scenarios` (traced scenarios) → the
  `/ux-lint` linter (`docs/ux/lint.py`) must pass. Wire that linter into the host
  CI/pre-commit so UX drift can't merge.
- **Not installed?** → recommend it and give the install line right away:
  ```
  /plugin marketplace add ssheleg/super-ux
  /plugin install super-ux@super-ux
  ```
  (or `npx skills add ssheleg/super-ux`). For UI tasks the spec gate **requires**
  it — install before stage 3, otherwise stop and ask the operator to install.

**Stage 0 is MANDATORY — the stage, not any particular skill.** Every run grills
before it builds; there is no "clear enough task" exemption and no starting stage 1
without a committed, operator-confirmed brief (the one sanctioned bypass is the
entry-from-super-ux short-circuit). What *is* swappable is the **provider**:
- **`grill-me` / `grilling`** when the chain resolves — install:
  `/plugin marketplace add alirezarezvani/claude-skills` →
  `/plugin install engineering-advanced-skills@claude-code-skills` (upstream origin:
  `npx skills add mattpocock/skills`). It usually ships `disable-model-invocation:
  true`, so ask the operator to run `/grill-me`; and it typically delegates to
  `/grilling` — if that doesn't resolve, the chain is dangling, use the loop.
- **the orchestrator's own grill loop** otherwise — a compliant implementation of
  the same **grill contract**, not a degradation.

Either way the grill must satisfy the contract in `references/stages.md` → 0,
including the **autonomy sweep**: it pre-resolves what would otherwise stop stages
1→9 mid-flight (test/lint/deploy commands, branch policy, log locations, docs
targets, the model decision, deploy authorization). Autonomy is bought here or not
at all — an unasked question is a scheduled interruption.

## How to run

1. Restate the task in one line. Create a **TaskList: one task per stage, starting
   with stage 0** (survives context loss; lets you resume). Then run the
   **companion preflight** (`references/companion-skills.md`): detect which
   companion skills resolve and emit ONE block covering both the companions —
   install the required/recommended ones (superpowers always; super-ux for UI
   tasks) — **and the model decision** (`references/model-tiering.md`): recommend
   the most capable model available, let the operator confirm or override, record
   it. Ask once, here.
2. **Run stage 0 (Intake grill) — always, no exceptions.** Grill until shared
   understanding is reached, the autonomy sweep is covered and the brief is locked
   (`references/stages.md` → 0). Do not touch stage 1 before the brief is
   committed and confirmed. **Entered from super-ux?**
   (a validated `docs/ux/` chain and/or a `docs/ux/plans/…` fix plan already
   exists — super-ux's `/ux` hands off here) → don't re-grill or rebuild the UX
   chain: just check it's OK (`/ux-lint` green), confirm scope in one line, and
   skip ahead to the first stage with real work (see `references/stages.md` → 0).
3. Walk stages 1→9 on the model confirmed at preflight. **Don't re-ask about the
   model at every boundary** — only when the operator recorded a per-stage override
   map and the next stage's entry differs (`references/model-tiering.md`).
4. Do **not** advance until the stage **gate** passes (`references/stages.md`).
   Honor the gate **type**: for `auto`, verify the gate's `check` yourself and
   stop/return on fail; for `manual`, present the result and **wait for the
   operator's explicit "continue"/go** — an auto gate never substitutes for a
   required manual approval.
5. Cross-cutting, every stage: **answer from the brief's autonomy section rather
   than asking again** — it was grilled precisely so you wouldn't have to; task
   tracker + conventional commits per host conventions; worktree isolation for the
   build; honest degradation (never claim a failed/skipped step succeeded);
   outward/irreversible actions (deploy, publish, repo create) need explicit
   operator go — or a **specific** standing authorization recorded in the brief
   (named target + preconditions; a vague "do everything" is not one).

## Stages (detail in `references/stages.md`)

All stages run on the **one model confirmed at preflight** (default: the most
capable available — see `references/model-tiering.md`).

| # | Stage | Invoke | Gate | Type |
|---|---|---|---|---|
| 0 | Intake grill — **mandatory** | `grill-me` / `grilling` if the chain resolves, else the built-in grill loop (same contract) | shared understanding reached; autonomy sweep covered; brief locked + confirmed | manual |
| 1 | Docs study | `context7` (resolve-library-id → get-library-docs) / `context7-docs` | contracts grounded on fetched docs | auto |
| 2 | Brainstorm | `superpowers:brainstorming` + **UI detection** | design approved; UI verdict recorded | manual |
| 3 | Spec | **UI → super-ux chain first** (`/ux` → `ux-foundation` CJM → `ux-flows` screens → `ux-scenarios` → `/ux-lint`), then spec `docs/superpowers/specs/…-design.md` | committed + reviewed; UI: chain validated, linter green, scenarios/`SCR-` traced | manual |
| 4 | Plan | `superpowers:writing-plans` → `docs/superpowers/plans/…md` | parallel-ready, DoD per task | auto |
| 5 | Dev | `superpowers:using-git-worktrees` + `superpowers:subagent-driven-development` (TDD) | tasks DONE, TDD green per task | auto |
| 6 | Tests | host test runner + `superpowers:test-driven-development` | full suite green; new/changed code covered | auto |
| 7 | Lint + deploy | host lint → deploy per host convention | lint clean + suite green before deploy; deploy needs a go (or the brief's specific standing authorization) | manual |
| 8 | Post-deploy | tail deploy logs / health-check | clean boot or honest degradation report | auto |
| 9 | Docs + wiki | host module docs/runbook rules → `wiki-update` | docs synced, wiki synced | auto |

## Model — ask once, at preflight

Default recommendation: **the most capable reasoning model the environment
offers** (currently the latest Opus generation — read that as a tier, not a
string). **Never hardcode a model id**: generations ship, tiers get renamed, and
the operator may be on another provider entirely — resolve the top tier available
at runtime. Stage configs use provider-agnostic tokens (`default` / `inherit`).

> 🧠 **Model for this run:** recommended **`<top tier available>`**. You're on
> `<current>`. `/model <id>` to switch, or "keep current", or name per-stage
> overrides. *(Reminder only — if that tier isn't available, say which one you're
> using and continue.)*

Record the answer in the brief; don't re-ask per stage. Stage-5 subagents are
pinned to the confirmed model automatically. Detail: `references/model-tiering.md`.

## Bring your own skills

The stages above (stage 0 intake + 1→9) are the **example** flow (grill +
superpowers + a super-ux UX track for user-facing tasks + host conventions). A
host project owns its pipeline: copy `pipeline.example.json` → `pipeline.json`,
then define its **own** stages (any count), point each stage's `skills[]` at the
skills/agents its environment resolves, set each `gate.type` (`auto`/`manual`) to
fit its process, and configure/toggle its own `release` block. The framework ships
no fixed stage count and no opinion on which gates are manual or whether release
automation is on — `pipeline.schema.json` is the only contract.

## References

- `pipeline.schema.json` — the universal pipeline config contract (stages + release)
- `pipeline.example.json` — this plugin's default flow (stage 0 + 1→9) + release, as config
- `references/stages.md` — per-stage detail + exact gate criteria + gate types
- `references/model-tiering.md` — model map, ids, the `/model` reminder mechanic, override
- `references/conventions.md` — how stages 6–9 read the host project's CLAUDE.md
- `references/companion-skills.md` — companion skills, install lines, preflight recommendation
- `references/artifacts.md` — the canonical document/artifact layout per stage
