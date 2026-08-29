---
name: task-pipeline
description: "Use when work changes the repository — feature, fix, refactor, migration, integration, rewrite, adoption or hardening; фича, фикс, рефактор, миграция, интеграция, доработать, починить, внедрить, перевести — or when the output is a finding that lands in it: audit/аудит, bug hunt/проверь ошибки, production check/проверь прод, PR review/ревью PR — or on 'run this through the pipeline' / 'прогони по конвейеру', 'full cycle, the full cycle' / 'полный цикл', /task-pipeline. Runs a substantial task through an intake grill, docs study, brainstorm, spec, plan, build, tests, deploy, post-deploy, docs/wiki sync and acceptance with explicit gates. 'checkup' / 'чекап' reports unconfirmed releases; 'setup' audits existing docs. Not for: answering a question, explaining code, a typo or a one-line edit — say 'без пайплайна' / 'quick' to opt out."
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
| 0, 9 · The documentation system | `references/documentation.md` |
| any stage · The canons, and where each is enforced | [`evidence-docs`](../evidence-docs/SKILL.md) — the sibling skill in this plugin |
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
| 5–8 · how a node is CLOSED — three blind readings at three distances, all three required | `references/certification.md` |
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

**Optional bridge.** An equivalent skill set the operator already runs can be mapped
onto stages 2/4/5/6 in `pipeline.json` → `skills[]`. That is a **substitution, never a
requirement**: the built-in doctrine is normative, the gates in `references/stages.md`
still govern, and nothing detects, recommends or waits for an external provider.

**super-ux — recommended for ANY user-facing task**, and the one thing that can stop a
gate. The moment a task implies an interface (web / mobile / CLI / TUI), the
WHY→UI→scenario chain runs through `/ux` and its linter, which belongs in the host's
CI so UX drift cannot merge. **Not installed on a UI task? The stage-3 spec gate
stops** — offer the install and wait (`references/companion-skills.md`).

**The grill is built in and mandatory** (`references/grill.md`). No "clear enough task"
exemption and no stage 1 without a committed, operator-confirmed brief. It produces the
**REQ spine** — the request as an addressable list, each row naming how it is verified —
which stages 3–5 trace to, stage 4 set-compares against, and **stage 10 accounts for
every one of**, turning the pipeline from a funnel into a circle.

**Harvest before you ask** (`references/knowledge-sources.md`). Stage 0 opens by
pulling what the project already knows about *this* task, writes the source ledger
into the brief, and then interviews **against** it — so the operator outranks any
document, **but only out loud**, and an override is a recorded decision rather than
an undetected divergence. That ledger is also stage 9's work list. Which sources,
and the two ways the retro is read — standing instructions in full because they
bind this run, the log queried because nothing caps it — are in
`references/knowledge-sources.md` and `references/retrospective.md`.

**Three artifacts close a run, not two — and they are a convergence, not a sequence.**
Stage 9 syncs the docs, the wiki **and the code graph**. None consumes another; all three
consume the same change, and the **graph↔docs divergence check is the gate over their
convergence** — the only thing that compares two of the three against each other, which
is why it is not optional where a graph exists. A stale graph is a false premise
**carrying the authority of a machine**: a wrong doc gets argued with, a wrong graph gets
believed (`references/knowledge-graph.md`, `references/audit.md`).

**Documentation is a deliverable, and it has a gate** (`references/documentation.md`).
Stage 0 answers the four questions that make docs a *system* into `docs/DOCMAP.md`;
from then the **Doc Loop** fires whenever anything is settled, at **any** stage rather
than only at stage 9, the stage-9 sweep walks the **propagation matrix** — the harvest
ledger names what you *read*, the matrix names what you *owe* — and *"docs in sync"*
becomes a command with an exit code.

**The run teaches the next run, and the list stays short**
(`references/retrospective.md`). Every gate is good at *this* run and blind across
runs, so one class of failure can be caught, fixed and forgotten five times with
nothing noticing it is the same one. Stage 10's last act, **in this order and the
order is load-bearing**: stamp the run, then prune, then write the entry — a
retirement trigger counts firings across the last five stamps, so a prune placed
ahead of the stamp reads a counter its own stage has not written yet. The cap, the
triggers and what an entry must carry are in `references/retrospective.md`; why
the order cannot be swapped is `references/learned.md` rule 21.

Stage 0 reads those standing instructions in full, which is why the prune is a gate
criterion and not a good intention: a rule nobody reads to the end is worse than no
rule, because everyone believes it is covered.

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
- **The design destination**, when the project designs in Figma: *which* file, in
  which team — a stage-0 decision, never a stage-3 side effect. Left to drawing
  time the question is answered by whoever is holding the brush, and the answer is
  usually *create a new file* — which is how a project ends up with three files
  called some variation of "Design", each with real work in it and no way to tell
  which one the team opens.

## How to run

1. Restate the task in one line. Create a **TaskList: one task per stage, starting
   with stage 0** (survives context loss; lets you resume). Then run the
   **companion preflight** (`references/companion-skills.md`): the stage doctrine
   is built in, so this only checks the *optional* companions (super-ux for UI
   tasks, context7, wiki-update, graphify) and emits ONE block covering them
   **and the model decision** (`references/model-tiering.md`): recommend
   the most capable model available, let the operator confirm or override, record
   it. Ask once, here. **The same block carries the run mode**
   (`references/continuity.md`): read `pipeline.json` → `run.loop`; where it is
   recorded, arm it and print the job id and the cancel command — the config is
   the authorization, so re-asking rebuilds the habit it exists to retire. Where
   it is **absent, the mode is off**; recommend it in one line and move on.
   Silence arms nothing, and the mode never collapses a `manual` gate.
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
5. **The cross-cutting rules fire at any stage**, not only here — the Doc Loop, the
   loop guard, the audit's exit, the frozen REQ list, the carry-over ledger, and
   what counts as evidence, and **every gate prints `holds: N`** — what this run left
   running, across all eight classes, enumerated by class and never by a single
   tool — and stage 10 does not close while this run's residue is live and
   unaccounted (`references/residue.md`). The rest are in
   [`references/gates.md`](references/gates.md) → *Cross-cutting, at every stage*.

## Stages (detail in `references/stages.md`)

All stages run on the **one model confirmed at preflight** (default: the most
capable available — see `references/model-tiering.md`).

| # | Stage | Gate | Type |
|---|---|---|---|
| 0 | Intake grill — **mandatory** | source ledger written with its `Contradictions:` line; `docs/DOCMAP.md` answered and intent reconciled against as-built; the retro read in full; autonomy sweep covered; brief locked and confirmed | manual |
| 1 | Docs study | contracts grounded on fetched docs | auto |
| 2 | Brainstorm + decompose | design approved; UI verdict recorded; every REQ answered; **the queue is an artifact** — a work graph validates and its coverage names no unserved REQ; platform: module map approved | manual |
| 3 | Spec | committed + reviewed; UI: chain validated, linter green, scenarios and `SCR-` traced; COPY and VISUAL are a parallel layer after UX, and where both ran their convergence check is recorded | manual |
| 4 | Plan | parallel-ready, DoD per task; **every edge names what it carries** — the fake-edge test run and its `Edges:` count computed | auto |
| 5 | Dev | tasks DONE, TDD green per task, branch integrated per the brief; a fanned-out group gets **one convergence check over all its diffs together** before the first worktree lands | auto |
| 6 | Tests | full suite green, new and changed code covered, every new check probed both ways and asserted on its exit code; **a web surface is checked in a browser, not in the diff** | auto |
| 7 | Lint + deploy | lint clean and suite green before deploy; deploy needs a go, or the brief's specific standing authorization | manual |
| 8 | Post-deploy | clean boot or an honest degradation report; **a deployed web target is opened, not curled** — a `200` proves the server answered and nothing else | auto |
| 9 | Docs + wiki | every stale row of the stage-0 source ledger updated; the propagation matrix walked for every change type this run produced; the documentation gate green with its ratchets printed; docs, wiki and the code graph synced and checked against each other | auto |
| 10 | **Acceptance** | the ladder walk ran and its absences became REQ rows; every REQ accounted for with evidence from a check seen failing once; no unresolved ledger row; **every repository clean, pushed and pointed at**; the hand-back written and the environment given back; the retrospective written **last**, and in order | manual |

**Every gate above is the short form**, and the long form is the point of
[`references/stages.md`](references/stages.md) — one section per stage. What the
ladder walk is, which eight environment classes stage 10 enumerates, what makes an
edge fake, why a `200` is not a working page: all there, none here.

**Several repositories?** A submodule is finished when its parent says so — the
work can be committed, pushed and green while a clone of the parent still gets the
commit before it, and neither repository looks wrong alone. The two commands that
prove it, and the two-command fix whose second half gets forgotten, are in
[`references/acceptance.md`](references/acceptance.md) → *A project of several
repositories*.

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

The stages above are the **example** flow. A host project owns its pipeline: copy
`pipeline.example.json` → `pipeline.json`, define its **own** stages (any count),
point each `skills[]` at what its environment resolves, set each `gate.type`
(`auto`/`manual`) to fit its process, and toggle its own `release` block. The
framework ships no fixed stage count and no opinion on which gates are manual —
`pipeline.schema.json` is the only contract.

## References

Every reference is routed from the **Built-in doctrine** table above, keyed by
the stage that sends you there — one home for that mapping rather than two. The
two config contracts sit beside this file: `pipeline.schema.json` (the universal
stages + release contract) and `pipeline.example.json` (this plugin's default
flow as config).
