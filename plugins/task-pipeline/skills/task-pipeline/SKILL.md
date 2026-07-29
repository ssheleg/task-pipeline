---
name: task-pipeline
description: "Use when running a substantial task through the full end-to-end delivery pipeline — an up-front intake grill that expands the request into a complete brief, then docs study, brainstorm, spec, plan, subagent-driven build, tests, lint/deploy, post-deploy log check, docs/wiki sync and acceptance — as gated stages whose doctrine is built entirely into this skill (no required companion skills). Triggers - 'run this through the pipeline' / 'прогони по конвейеру', 'the full cycle' / 'полный цикл', /task-pipeline, or any substantial feature, fix, or build that should follow the disciplined cycle rather than ad-hoc coding. The intake grill is mandatory - it front-loads every decision, including the per-stage autonomy sweep, so stages 1→10 run without mid-flight questions; recommends super-ux for user-facing work; confirms one model up front (most capable available, never a hardcoded id); reads host-project conventions for deploy/docs/wiki so it stays project-agnostic."
---

# task-pipeline

Self-contained orchestrator. Runs a task through **gated stages**, each carrying its
own built-in doctrine — no companion plugin required. Keeps the main thread
disciplined: no stage advances until its gate passes; the whole run uses one model,
confirmed before it starts.

**Grill first, then run autonomously.** A one-line task ("make me feature X") is
never enough to finish without a human in the loop. Stage 0 is **mandatory**: a
relentless, one-question-at-a-time interview that resolves every decision branch
*and* sweeps stages 1→10 for anything that would stop the run later — then locks
the answers into a brief. Autonomy is bought there or not at all; every question
skipped at stage 0 comes back as an interruption at stage 6.

**Config contract: [`pipeline.schema.json`](pipeline.schema.json).** A pipeline is
a machine-readable config — an ordered list of stages, each with `skills[]` (the
skills/agents that run it) and a `gate {type, check}`. The schema is the universal
contract; it imposes **no** specific stages, skills, or gate assignments.
[`pipeline.example.json`](pipeline.example.json) is a **copy-and-rewrite example**
that encodes this plugin's own default flow (stage 0 intake + the 1→10 stages
tabled below) and an optional, toggleable `release` block. Any project replaces it
wholesale — any number of stages, run by its own skills/agents, with its own gate
types (see *Bring your own skills*). Each gate has a **type**: `auto` (the
orchestrator verifies the `check` itself, pass/fail) or `manual` (wait for an
explicit operator go); which stages are manual is the operator's call. In the
example's `skills[]`, `task-pipeline:<name>` denotes this skill's own built-in
doctrine (`references/<name>.md`) and `host:<name>` denotes the host project's own
command for that job (`references/conventions.md`); everything else is a real skill
the environment resolves.

## Prerequisites — none required

**Every stage's doctrine ships inside this skill.** There is no required companion
plugin, nothing to resolve at preflight, no version skew with someone else's repo,
and no stage that can fail because a dependency is missing:

| Stage | Built-in doctrine |
|---|---|
| 0 Knowledge harvest (pre-grill) | [`references/knowledge-sources.md`](references/knowledge-sources.md) |
| 0 Intake grill | [`references/grill.md`](references/grill.md) |
| 2 Brainstorm | [`references/brainstorm.md`](references/brainstorm.md) |
| 2 Decompose (platforms only) | [`references/decomposition.md`](references/decomposition.md) |
| 3 Spec | [`references/spec.md`](references/spec.md) |
| 4 Plan | [`references/planning.md`](references/planning.md) |
| 5 Build (worktree, subagents, fix loop) | [`references/build.md`](references/build.md) + [`references/review.md`](references/review.md) |
| 5–6 TDD + suite gate | [`references/tdd.md`](references/tdd.md) |
| 10 Acceptance (REQ close-out) | [`references/acceptance.md`](references/acceptance.md) |
| 10 + any audit (what's *missing*) | [`references/audit.md`](references/audit.md) |
| any repeating loop | [`references/loop-guard.md`](references/loop-guard.md) |

**Optional bridge.** If the operator already runs an equivalent skill set (e.g.
`superpowers:brainstorming` / `writing-plans` / `subagent-driven-development` /
`using-git-worktrees` / `test-driven-development`), it can be mapped onto stages
2/4/5/6 in `pipeline.json` → `skills[]`. That is a **substitution, never a
requirement**: the built-in doctrine is normative, the gates in
`references/stages.md` still govern, and nothing detects, recommends or waits for
an external provider.

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

**The grill is built in — no companion skill, nothing to install.** Stage 0 ships
with this skill: the full doctrine lives in [`references/grill.md`](references/grill.md)
(interview loop, domain awareness, autonomy sweep, output). It is **mandatory** —
no "clear enough task" exemption, no starting stage 1 without a committed,
operator-confirmed brief. The one sanctioned bypass is the entry-from-super-ux
short-circuit, and even that demands a scope confirmation.

It also produces the **REQ spine**: the request as an addressable list of
requirements, each naming how it will be verified. Stages 3–5 trace to those ids,
stage 4's gate is a mechanical set-comparison against them, and **stage 10 accounts
for every one** — which is what turns the pipeline from a funnel into a circle.

**Harvest before you ask.** Stage 0 opens with a **knowledge harvest**
([`references/knowledge-sources.md`](references/knowledge-sources.md)), not a
question: pull what the project already knows about this task from the code,
`CLAUDE.md`, `CONTEXT.md`/ADRs, `docs/` + `docs/ux/`, past pipeline briefs, the
**knowledge wiki** if one is installed
([obsidian-wiki](https://github.com/ar9av/obsidian-wiki) — recommended, never
required) and any **other repo or hosted doc system the project names as its
docs**. Write the source ledger into the brief, then interview *against* it: every
answer that touches a source is checked against that source, and the operator
outranks any document — but only out loud, so an override is a recorded decision
instead of an undetected divergence. The same ledger is stage 9's work list.

Three things the grill does beyond clarifying the request:
- **Domain awareness.** It reads the project's own `CONTEXT.md` / `docs/adr/` and
  holds the operator to them — challenging terms that conflict with the glossary,
  sharpening overloaded words, stress-testing with concrete scenarios, and
  flagging where the code contradicts what was just said. Resolved terms are
  written to `CONTEXT.md` as they land; genuinely hard-to-reverse decisions get an
  ADR.
- **The autonomy sweep.** It pre-resolves what would otherwise stop stages 1→10
  mid-flight (test/lint/deploy commands, branch policy, log locations, docs
  targets, the model decision, deploy authorization). Autonomy is bought here or
  not at all — an unasked question is a scheduled interruption.

## How to run

1. Restate the task in one line. Create a **TaskList: one task per stage, starting
   with stage 0** (survives context loss; lets you resume). Then run the
   **companion preflight** (`references/companion-skills.md`): the stage doctrine
   is built in, so this only checks the *optional* companions (super-ux for UI
   tasks, context7, wiki-update) and emits ONE block covering them
   **and the model decision** (`references/model-tiering.md`): recommend
   the most capable model available, let the operator confirm or override, record
   it. Ask once, here.
2. **Run stage 0 — always, no exceptions.** It opens with the **knowledge harvest**
   (`references/knowledge-sources.md`): query the project's own sources — repo docs,
   ADRs, `docs/ux/`, past briefs, the wiki if installed, any doc repo the project
   names — for this task's terms, and write the **source ledger** into the brief
   before question one. Then grill until shared
   understanding is reached, **each answer checked against the harvest**, the
   autonomy sweep is covered, **the REQ table is
   written (one row per independently verifiable deliverable, each naming its
   check)** and the brief is locked
   (`references/stages.md` → 0). Do not touch stage 1 before the brief is
   committed and confirmed. **Entered from super-ux?**
   (a validated `docs/ux/` chain and/or a `docs/ux/plans/…` fix plan already
   exists — super-ux's `/ux` hands off here) → don't re-grill or rebuild the UX
   chain: just check it's OK (`/ux-lint` green), confirm scope in one line, and
   skip ahead to the first stage with real work (see `references/stages.md` → 0).
3. Walk stages 1→10 on the model confirmed at preflight. **Don't re-ask about the
   model at every boundary** — only when the operator recorded a per-stage override
   map and the next stage's entry differs (`references/model-tiering.md`).
   **Is the brief a platform rather than a change?** Then stage 2 also cuts it into
   modules (`references/decomposition.md`) and stages 3→10 run **per module** in
   build order, one brick at a time — stages 0–2 run once, and the module map's
   status column is the resume point (`references/stages.md` → *The program loop*).
4. Do **not** advance until the stage **gate** passes (`references/stages.md`).
   Honor the gate **type**: for `auto`, verify the gate's `check` yourself and
   stop/return on fail; for `manual`, present the result and **wait for the
   operator's explicit "continue"/go** — an auto gate never substitutes for a
   required manual approval.
5. Cross-cutting, every stage: **answer from the brief's autonomy section rather
   than asking again** — it was grilled precisely so you wouldn't have to;
   **anything deferred, dropped or left half-done goes into the carry-over ledger
   the moment it's said** — deferred out loud is forgotten; **never narrow the task
   silently** — the REQ list is frozen, adding is free, removing needs the
   operator's explicit agreement; **when a loop starts undoing an earlier pass —
   the same file edited twice for the same reason, a closed finding coming back, a
   third entry into one stage — stop and run the loop guard**
   (`references/loop-guard.md`): name the two shapes, escalate to the layer that
   owns the conflict, re-plan the check as an ordered list, then go through it one
   item at a time; **when a pass is *searching* rather than editing and starts
   finding mostly what the previous pass's own fixes broke, the axis is exhausted —
   rotate it, don't look harder** (`references/audit.md`), and remember that a
   green from a check nobody has watched fail is not evidence; task
   tracker + conventional commits per host conventions; worktree isolation for the
   build, integrated back per the brief's branch policy before stage 7; honest
   degradation (never claim a failed/skipped step succeeded);
   outward/irreversible actions (deploy, publish, repo create, opening a PR,
   **editing a shared design file — frames are read by designers and stakeholders,
   so drawing in one is publishing**) need explicit
   operator go — or a **specific** standing authorization recorded in the brief
   (named target + preconditions; a vague "do everything" is not one).

## Stages (detail in `references/stages.md`)

All stages run on the **one model confirmed at preflight** (default: the most
capable available — see `references/model-tiering.md`).

| # | Stage | Invoke | Gate | Type |
|---|---|---|---|---|
| 0 | Intake grill — **mandatory** | built in: [`references/knowledge-sources.md`](references/knowledge-sources.md) (harvest) → [`references/grill.md`](references/grill.md) (interview) | source ledger written; shared understanding reached; autonomy sweep covered; brief locked + confirmed | manual |
| 1 | Docs study | `context7` (resolve-library-id → get-library-docs) / `context7-docs` | contracts grounded on fetched docs | auto |
| 2 | Brainstorm + decompose | built in: [`references/brainstorm.md`](references/brainstorm.md) + **UI detection** + [`references/decomposition.md`](references/decomposition.md) for platforms | design approved; UI verdict recorded; every REQ answered; platform: module map approved | manual |
| 3 | Spec | built in: [`references/spec.md`](references/spec.md) — **UI → super-ux chain first** (`/ux` → `ux-foundation` CJM → `ux-flows` screens → `ux-scenarios` → `/ux-lint`), then spec `docs/superpowers/specs/…-design.md` | committed + reviewed; UI: chain validated, linter green, scenarios/`SCR-` traced | manual |
| 4 | Plan | built in: [`references/planning.md`](references/planning.md) → `docs/superpowers/plans/…md` | parallel-ready, DoD per task | auto |
| 5 | Dev | built in: [`references/build.md`](references/build.md) (worktree → subagent per task → review loop → integrate) + [`references/tdd.md`](references/tdd.md) | tasks DONE, TDD green per task, branch integrated per the brief | auto |
| 6 | Tests | host test runner + built-in [`references/tdd.md`](references/tdd.md) | full suite green; new/changed code covered | auto |
| 7 | Lint + deploy | host lint → deploy per host convention | lint clean + suite green before deploy; deploy needs a go (or the brief's specific standing authorization) | manual |
| 8 | Post-deploy | tail deploy logs / health-check | clean boot or honest degradation report | auto |
| 9 | Docs + wiki | host module docs/runbook rules → `wiki-update` ([obsidian-wiki](https://github.com/ar9av/obsidian-wiki), recommended) | every stale row of the stage-0 source ledger updated; docs synced; wiki synced | auto |
| 10 | **Acceptance** | built in: [`references/audit.md`](references/audit.md) (ladder walk) → [`references/acceptance.md`](references/acceptance.md) (coverage table) | ladder walk ran, its absences became REQ rows; every REQ accounted for with evidence from a check seen failing once; ledger has no unresolved row; operator signs off | manual |

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

The stages above (stage 0 intake + 1→10) are the **example** flow (this skill's
built-in doctrine + a super-ux UX track for user-facing tasks + host conventions). A
host project owns its pipeline: copy `pipeline.example.json` → `pipeline.json`,
then define its **own** stages (any count), point each stage's `skills[]` at the
skills/agents its environment resolves, set each `gate.type` (`auto`/`manual`) to
fit its process, and configure/toggle its own `release` block. The framework ships
no fixed stage count and no opinion on which gates are manual or whether release
automation is on — `pipeline.schema.json` is the only contract.

## References

- `pipeline.schema.json` — the universal pipeline config contract (stages + release)
- `pipeline.example.json` — this plugin's default flow (stage 0 + 1→10) + release, as config
- `references/knowledge-sources.md` — stage-0 phase 1: the source list, the wiki, the ledger, the stage-9 loop-back
- `references/grill.md` — the built-in stage-0 grill: loop, domain awareness, autonomy sweep
- `references/acceptance.md` — the built-in stage-10 close-out: REQ coverage, evidence, sign-off
- `references/audit.md` — cross-cutting: the L0→L7 ladder and its seams (what was never written), axis rotation, ratchets, proven checks
- `references/brainstorm.md` — stage 2: design dialogue, approaches, UI detection, hard gate
- `references/spec.md` — stage 3: UX track order, the spec contract, self-review, review gate
- `references/planning.md` — stage 4: zero-context plan format, parallel groups, no placeholders
- `references/build.md` — stage 5: isolation, ledger, subagent task loop, fix loop, final review
- `references/review.md` — the review rubric, diff packages and the three reviewer prompts
- `references/tdd.md` — stages 5–6: the iron law, red/green/refactor, the suite gate
- `references/stages.md` — per-stage detail + exact gate criteria + gate types
- `references/model-tiering.md` — model map, ids, the `/model` reminder mechanic, override
- `references/conventions.md` — how stages 6–10 read the host project's CLAUDE.md
- `references/companion-skills.md` — companion skills, install lines, preflight recommendation
- `references/artifacts.md` — the canonical document/artifact layout per stage
- `templates/` — skeletons seeded into the host project: `brief.md` (stage 0),
  `carryover.md` (seeded at 0, appended by every stage, read in full at 10),
  `context.md` and `adr.md` (format references the grill writes lazily)
