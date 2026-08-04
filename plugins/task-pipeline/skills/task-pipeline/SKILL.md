---
name: task-pipeline
description: "Runs a substantial task through a full delivery pipeline: an intake grill that expands the request into a locked brief, then docs study, brainstorm, spec, plan, subagent build, tests, lint/deploy, post-deploy check, docs/wiki sync and acceptance — gated stages whose doctrine ships inside this skill (no required companions). Use when work changes the repository — a feature, fix, refactor, migration, integration, rewrite, adoption or hardening; фича, фикс, рефактор, миграция, интеграция, доработать, починить, внедрить — or on 'run this through the pipeline' / 'прогони по конвейеру', 'the full cycle' / 'полный цикл', /task-pipeline. Not for: answering a question, explaining or reading code, a typo or a one-line edit — say 'без пайплайна' / 'quick' to opt out. The grill is mandatory and front-loads every decision, so stages 1→10 run without mid-flight questions; documentation is a deliverable with its own gate; recommends super-ux for user-facing work; confirms one model up front, never a hardcoded id."
license: MIT
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
plugin, nothing to resolve at preflight and no version skew with someone else's
repo. Stages 1 and 6–9 additionally run the *host's own* commands and optional
tools, and **no stage blocks on an install** — stage 1 falls back to web search, the
wiki and the code graph are recommendations. The **one** exception is deliberate and
named: on a user-facing task the stage-3 UX track requires super-ux, and the spec
gate stops until it is installed.

| Stage | Built-in doctrine |
|---|---|
| 0 + 9 + any settled decision · The documentation system | [`references/documentation.md`](references/documentation.md) |
| 6–10 + any check you write · Gates | [`references/gates.md`](references/gates.md) |
| any agent-time enforcement · Hooks | [`references/hooks.md`](references/hooks.md) |
| 0 Knowledge harvest (pre-grill) | [`references/knowledge-sources.md`](references/knowledge-sources.md) |
| 0 + 9 The code graph (graphify — recommended, never required) | [`references/knowledge-graph.md`](references/knowledge-graph.md) |
| 0 Intake grill | [`references/grill.md`](references/grill.md) |
| 2 Brainstorm | [`references/brainstorm.md`](references/brainstorm.md) |
| 2 Decompose (platforms only) | [`references/decomposition.md`](references/decomposition.md) |
| 3 Spec | [`references/spec.md`](references/spec.md) |
| 4 Plan | [`references/planning.md`](references/planning.md) |
| 5 Build (worktree, subagents, fix loop) | [`references/build.md`](references/build.md) + [`references/review.md`](references/review.md) |
| 5–6 TDD + suite gate | [`references/tdd.md`](references/tdd.md) |
| 10 Acceptance (REQ close-out) | [`references/acceptance.md`](references/acceptance.md) |
| 10 Retrospective (the run's last act) | [`references/retrospective.md`](references/retrospective.md) |
| 10 + any audit (what's *missing*) | [`references/audit.md`](references/audit.md) |
| **first run in a project** (new or existing) | [`references/adoption.md`](references/adoption.md) |
| **first run · the entry audit** (offered once) | [`references/setup.md`](references/setup.md) |
| **what travels with the bundle vs stays in a project** | [`references/portability.md`](references/portability.md) |
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
question: pull what the project already knows about this task from the code, the
**code graph** if one is built
([`references/knowledge-graph.md`](references/knowledge-graph.md) — graphify;
recommended, never required),
`CLAUDE.md`, `CONTEXT.md`/ADRs, **the decision register**, `docs/` + `docs/ux/`,
past pipeline briefs, **the retro's standing instructions, run stamps and recent
log** — `docs/superpowers/retro.md`, read in full because they *bind* this run and
are bounded by construction, while the archive under `docs/superpowers/retro/` is
**queried** by the task's nouns
([`references/retrospective.md`](references/retrospective.md)) —
the **knowledge wiki** if one is installed
([obsidian-wiki](https://github.com/ar9av/obsidian-wiki) — recommended, never
required) and any **other repo or hosted doc system the project names as its
docs**. Write the source ledger into the brief, then interview *against* it: every
answer that touches a source is checked against that source, and the operator
outranks any document — but only out loud, so an override is a recorded decision
instead of an undetected divergence. The same ledger is stage 9's work list.

**Three artifacts close a run, not two.** Stage 9 syncs the docs, the wiki **and the
code graph** (`/graphify . --update`) — the graph is what the *next* run's harvest
queries first, so a stale one is a false premise carrying the authority of a
machine. Refreshing it also buys the **graph↔docs divergence check**: a hub no
document names, an edge the docs deny, a doc naming a module the graph no longer
has. Doc-side findings are fixed at stage 9; absences become REQ rows at stage 10
([`references/knowledge-graph.md`](references/knowledge-graph.md),
[`references/audit.md`](references/audit.md)).

**Documentation is a deliverable, and it has a gate**
([`references/documentation.md`](references/documentation.md)). Stage 0's harvest
reads what the project knows; a second phase asks the four questions that make it a
*system* — where settled things live, what each fact's single home is, what a change
of type X obliges, and what proves it — and writes them to `docs/DOCMAP.md`. From
then on the **Doc Loop** fires whenever anything is settled, at **any** stage, not
only at stage 9; the stage-9 sweep walks the **propagation matrix** (the harvest
ledger names what you *read*, the matrix names what you *owe*); and *"docs in sync"*
stops being an assertion and becomes a command with an exit code. Governance is a
by-product: the run already produces decisions, so recording one is transcription
plus a stable id, never a second act of thinking.

**The run teaches the next run — and the list stays short.** Every gate is good at
*this* run and blind across runs, so the same class of failure can be caught, fixed
and forgotten five times with nothing noticing it is the same one. The last act of
stage 10 is therefore the **retrospective**
([`references/retrospective.md`](references/retrospective.md), written to
`docs/superpowers/retro.md`): **prune first** — every standing instruction checked
against its retirement triggers (it became a check · its surface is gone · it hasn't
fired in five runs), the list held to a hard cap of **ten**, every deletion logged —
then stamp the run, then write an entry **only if the run diverged** (symptom, the
stage that *owned* it, root cause, fix, and the check that catches it next time).
Stage 0 reads those standing instructions in full, which is exactly why the prune is
a gate criterion and not a good intention: a rule nobody reads to the end is worse
than no rule, because everyone believes it is covered.

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
   tasks, context7, wiki-update, graphify) and emits ONE block covering them
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
5. Cross-cutting, every stage: **when anything is settled — scope, a contract, a
   name, a policy, a vocabulary — run the Doc Loop
   (`references/documentation.md`) before the run moves on**: reserve the id,
   record it, resolve the question it answers, propagate by the matrix, commit
   with the ids. A decision that lives only in the spec dies with the spec, and one
   that lives only in the conversation was never made;
   **answer from the brief's autonomy section rather
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
   so drawing in one is publishing — and above all *creating* one, which needs a
   named team and never happens while a recorded file resolves**) need explicit
   operator go — or a **specific** standing authorization recorded in the brief
   (named target + preconditions; a vague "do everything" is not one).

## Stages (detail in `references/stages.md`)

All stages run on the **one model confirmed at preflight** (default: the most
capable available — see `references/model-tiering.md`).

| # | Stage | Invoke | Gate | Type |
|---|---|---|---|---|
| 0 | Intake grill — **mandatory** | built in: [`references/knowledge-sources.md`](references/knowledge-sources.md) (harvest) → [`references/grill.md`](references/grill.md) (interview) | source ledger written; **the documentation inventory answered into `docs/DOCMAP.md`** — registers, single homes, the propagation matrix, the gate command — and **intent reconciled against as-built**, every divergence resolved ([`references/documentation.md`](references/documentation.md)); the retro read in full and its archive queried; shared understanding reached; autonomy sweep covered; brief locked + confirmed | manual |
| 1 | Docs study | `context7` (resolve-library-id → get-library-docs) / `context7-docs` | contracts grounded on fetched docs | auto |
| 2 | Brainstorm + decompose | built in: [`references/brainstorm.md`](references/brainstorm.md) + **UI detection** + [`references/decomposition.md`](references/decomposition.md) for platforms | design approved; UI verdict recorded; every REQ answered; platform: module map approved | manual |
| 3 | Spec | built in: [`references/spec.md`](references/spec.md) — **UI → super-ux chain first** (`/ux` → `ux-foundation` CJM → `ux-flows` screens → `ux-scenarios` → `/ux-lint`), then spec `docs/superpowers/specs/…-design.md` | committed + reviewed; UI: chain validated, linter green, scenarios/`SCR-` traced | manual |
| 4 | Plan | built in: [`references/planning.md`](references/planning.md) → `docs/superpowers/plans/…md` | parallel-ready, DoD per task | auto |
| 5 | Dev | built in: [`references/build.md`](references/build.md) (worktree → subagent per task → review loop → integrate) + [`references/tdd.md`](references/tdd.md) | tasks DONE, TDD green per task, branch integrated per the brief; **anything generated passes its own checks, and local infrastructure does not publish the host's default ports** ([`references/learned.md`](references/learned.md)) | auto |
| 6 | Tests | host test runner + built-in [`references/tdd.md`](references/tdd.md) + [`references/learned.md`](references/learned.md) | full suite green; new/changed code covered; **every new check probed both ways and asserted on its exit code**, and the suite run once against a cold environment | auto |
| 7 | Lint + deploy | host lint → deploy per host convention | lint clean + suite green before deploy; deploy needs a go (or the brief's specific standing authorization) | manual |
| 8 | Post-deploy | tail deploy logs / health-check | clean boot or honest degradation report | auto |
| 9 | Docs + wiki | host module docs/runbook rules → `wiki-update` ([obsidian-wiki](https://github.com/ar9av/obsidian-wiki), recommended) → `/graphify . --update` ([`references/knowledge-graph.md`](references/knowledge-graph.md), recommended) | every stale row of the stage-0 source ledger updated; **the propagation matrix walked for every change type this run produced** — the ledger names what you read, the matrix names what you owe — every settled thing recorded with an id, every answered question resolved, and **the documentation gate green with its ratchet counts printed**; docs synced; wiki synced; **the code graph refreshed where one exists** and checked against the docs (a hub no doc names, a doc naming a node the graph lost); **every number computed rather than restated, every named command or file resolvable** ([`references/learned.md`](references/learned.md)); the carry-over count printed beside the verdict | auto |
| 10 | **Acceptance** | built in: [`references/audit.md`](references/audit.md) (ladder walk) → [`references/acceptance.md`](references/acceptance.md) (coverage table) → [`references/retrospective.md`](references/retrospective.md) (retro: prune, stamp, entry) | ladder walk ran, its absences became REQ rows; every REQ accounted for with evidence from a check seen failing once; ledger has no unresolved row; **axis rotation recorded** (new findings vs self-inflicted, rule 1 of [`references/learned.md`](references/learned.md)), **every closure verified against the artefact rather than the document describing it**, **each correction swept across its class**, **every deferral a printed ratchet rather than a TODO**; **in a multi-repository project, every repository is clean, pushed and pointed at** (below); operator signs off; **every check this close-out leans on — the documentation gate included — has been seen failing once against a planted defect, and its ratchet counts are printed beside the verdict**; **the retrospective written last — prune before entry, list at or under its cap, every deletion and every entry carrying its commit, entries older than five stamps rotated into the archive, run stamped with its commit, counts printed** | manual |


### Stage 10 in a project of several repositories

**A submodule is finished when its parent says so.** A parent repository records each submodule as
a pointer to one commit, and moving the submodule does not move the pointer. So the work is
committed, pushed, its CI is green and its own roadmap says done — and anyone who clones the parent
gets the commit **before** the change. Nothing looks wrong in either repository on its own; the
disagreement exists only between them, which is why it survives every check that runs inside one.

Stage 10 does not close until:

```bash
git submodule status          # no line begins with '+'  (a '+' is the missing bump)
git -C <each repo> status --porcelain && git -C <each repo> log @{u}..HEAD --oneline
```

report nothing — for the parent as well as every submodule. Where
[agent-sync](https://github.com/ssheleg/agent-sync) is installed, `/agent-sync finish` runs
exactly this plus *no lease left held*, and `--gates` adds the project's own gate commands.

The fix, when it fails, is two commands and the second is the one that gets forgotten:

```bash
git -C <submodule> push
git add <submodule> && git commit -m "chore: bump <name> submodule — <why>"
```

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
- `references/knowledge-graph.md` — the code graph (graphify): install line, stage-0 reach queries, the stage-9 refresh, the graph↔docs divergence check
- `references/grill.md` — the built-in stage-0 grill: loop, domain awareness, autonomy sweep
- `references/acceptance.md` — the built-in stage-10 close-out: REQ coverage, evidence, sign-off
- `references/retrospective.md` — stage 10's last act: the project retro (`docs/superpowers/retro.md`), the three grades of fix, the mandatory prune and its cap of ten
- `references/documentation.md` — cross-cutting: the doc inventory, registers and ids, SSOT, the Doc Loop, supersede semantics, the propagation matrix, intent vs as-built
- `references/gates.md` — cross-cutting: the two axes, the promotion ladder, gate anatomy, the probe recipe, ratchet floors, where a gate runs
- `references/hooks.md` — agent-time enforcement: the PreToolUse contract, the fail-open hazard, placement, and the Claude-Code-only limit
- `references/audit.md` — cross-cutting: the L0→L7 ladder and its seams (what was never written), axis rotation, ratchets, proven checks
- `references/learned.md` — cross-cutting: fifteen rules earned by failure on a real multi-repository build, each with the incident behind it, its check and its exit criterion; plus the two that no check can decide
- `references/brainstorm.md` — stage 2: design dialogue, approaches, UI detection, hard gate
- `references/spec.md` — stage 3: UX track order, the spec contract, self-review, review gate
- `references/planning.md` — stage 4: zero-context plan format, parallel groups, no placeholders
- `references/build.md` — stage 5: isolation, ledger, subagent task loop, fix loop, final review
- `references/review.md` — the review rubric, diff packages and the three reviewer prompts
- `references/tdd.md` — stages 5–6: the iron law, red/green/refactor, the suite gate
- `references/stages.md` — per-stage detail + exact gate criteria + gate types
- `references/model-tiering.md` — model map, ids, the `/model` reminder mechanic, override
- `references/setup.md` — the entry audit: seven passes over the docs you already
  have, offered once, output as a fix plan; plus the inward check for rules that
  belong upstream
- `references/portability.md` — the manifest of workflow decisions and their homes
  inside the bundle, and the boundary against a project's own answers
- `references/adoption.md` — the first run in a project: greenfield seeding, and the
  brownfield walkthrough whose third step baselines the ratchets at today
- `references/conventions.md` — how stages 6–10 read the host project's CLAUDE.md
- `references/companion-skills.md` — companion skills, install lines, preflight recommendation
- `references/artifacts.md` — the canonical document/artifact layout per stage
- `templates/` — skeletons seeded into the host project: `brief.md` (stage 0),
  `carryover.md` (seeded at 0, appended by every stage, read in full at 10),
  `context.md` and `adr.md` (format references the grill writes lazily)
