---
name: task-pipeline
description: "Runs a substantial task through a full delivery pipeline: an intake grill that locks the request into a brief, then docs study, brainstorm, spec, plan, subagent build, tests, lint/deploy, post-deploy check, docs/wiki sync and acceptance. Use when work changes the repository — a feature, fix, refactor, migration, integration, rewrite, adoption or hardening; фича, фикс, рефактор, миграция, интеграция, доработать, починить, внедрить, перевести — or when the output is a finding that lands in it: audit/аудит, bug hunt/проверь ошибки, production check/проверь прод, PR review/ревью PR — or on 'run this through the pipeline' / 'прогони по конвейеру', 'the full cycle' / 'полный цикл', /task-pipeline. Two modes need no task at all: 'checkup' / 'чекап' reports what shipped unconfirmed and what to look at first; 'setup' audits existing documentation. Not for: answering a question, explaining code, a typo or a one-line edit — say 'без пайплайна' / 'quick' to opt out."
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
| run-wide · the work-list **between** runs, and how its priority is computed | `references/backlog.md` |
| run-wide · whether a **human** ever confirmed what shipped, and when | `references/verification.md` |
| run-wide · how much unconfirmed work has piled up, and what to look at first | `references/exposure.md` |
| any stage · Where each artifact belongs | `references/artifacts.md` |
| preflight · Companion skills and their fallbacks | `references/companion-skills.md` |
| 6–10 · How the host project's CLAUDE.md is read | `references/conventions.md` |
| preflight · Model map, ids and the override | `references/model-tiering.md` |

**Optional bridge.** An equivalent skill set the operator already runs (e.g.
`superpowers:brainstorming` / `writing-plans` / `subagent-driven-development` /
`using-git-worktrees` / `test-driven-development`) can be mapped onto stages 2/4/5/6
in `pipeline.json` → `skills[]`. That is a **substitution, never a requirement**: the
built-in doctrine is normative, the gates in `references/stages.md` still govern, and
nothing detects, recommends or waits for an external provider.

**super-ux — recommended for ANY user-facing task**, and the one thing that can stop a
gate. The moment a task implies an interface (web / mobile / CLI / TUI — the stage-0
grill detects it early), the WHY→UI→scenario chain runs through `/ux`,
`ux-foundation`, `ux-flows`, `ux-scenarios` and the `/ux-lint` linter, which belongs in
the host's CI so UX drift cannot merge. **Not installed on a UI task? The stage-3 spec
gate stops** — offer `/plugin marketplace add ssheleg/super-ux` and
`/plugin install super-ux@super-ux` (or `npx skills add ssheleg/super-ux`) and wait.
Details: `references/companion-skills.md`.

**The grill is built in and mandatory** (`references/grill.md`). No "clear enough task"
exemption, no stage 1 without a committed, operator-confirmed brief; the one sanctioned
bypass is the entry-from-super-ux short-circuit, and even that demands a scope
confirmation. It produces the **REQ spine** — the request as an addressable list, each
row naming how it is verified. Stages 3–5 trace to those ids, stage 4's gate is a
mechanical set-comparison against them, and **stage 10 accounts for every one**, which
is what turns the pipeline from a funnel into a circle.

**Harvest before you ask** (`references/knowledge-sources.md`). Stage 0 opens by
pulling what the project already knows about *this* task — the code and its graph,
`CLAUDE.md`, `CONTEXT.md`/ADRs, the decision register, `docs/` and `docs/ux/`, past
briefs, the wiki, and whatever else the project names as its docs. **The retro is read
two ways and the difference matters:** its standing instructions and run stamps are
read **in full** because they bind this run and are bounded by construction; its recent
log and archive are **queried** by the task's nouns, because nothing caps them
(`references/retrospective.md`). Write the source ledger into the brief and interview
*against* it: every answer touching a source is checked against it, and the operator
outranks any document — **but only out loud**, so an override is a recorded decision
rather than an undetected divergence. That ledger is also stage 9's work list.

**Three artifacts close a run, not two — and they are a convergence, not a sequence.**
Stage 9 syncs the docs, the wiki **and the code graph** (`/graphify . --update`). None of
the three consumes another; all three consume the same change, and the **graph↔docs
divergence check is the gate over their convergence** rather than an extra nicety. That is
why it is not optional where a graph exists: it is the only thing that compares two of the
three outputs against each other. The graph is what the next run's harvest queries
first, so a stale one is a false premise **carrying the authority of a machine** —
a wrong doc gets argued with, a wrong graph gets believed. Refreshing it buys the
graph↔docs divergence check; doc-side findings are fixed at stage 9, absences become
REQ rows at stage 10 (`references/knowledge-graph.md`, `references/audit.md`).

**Documentation is a deliverable, and it has a gate** (`references/documentation.md`).
A second stage-0 phase asks the four questions that make docs a *system* — where
settled things live, each fact's single home, what a change of type X obliges, what
proves it — and writes them to `docs/DOCMAP.md`. From then the **Doc Loop** fires
whenever anything is settled, at **any** stage rather than only at stage 9; the stage-9
sweep walks the **propagation matrix** (the harvest ledger names what you *read*, the
matrix names what you *owe*); and *"docs in sync"* becomes a command with an exit code.

**The run teaches the next run, and the list stays short**
(`references/retrospective.md`). Every gate is good at *this* run and blind across
runs, so one class of failure can be caught, fixed and forgotten five times with
nothing noticing it is the same one. Stage 10's last act: **stamp the run first** — the
only thing that makes the next step computable — **then prune** every standing
instruction against its retirement triggers, hold the list to a hard cap of **ten**,
log every deletion, and write an entry **only if the run diverged** (symptom, the stage
that *owned* it, root cause, fix, and the check that catches it next time).

Stage 0 reads those standing instructions in full, which is exactly why the prune is
a gate criterion and not a good intention: a rule nobody reads to the end is worse
than no rule, because everyone believes it is covered. **The order is load-bearing,
not stylistic** — one retirement trigger counts firings across the last five run
stamps, so a prune placed ahead of the stamp reads a counter its own stage writes
afterwards and can never run on real data (`references/learned.md` rule 21).

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
   rotate it, don't look harder** (`references/audit.md`); **every gate
   prints `holds: N` — what this run left running** across the eight classes
   (background shells, monitors, scheduled loops, coordination leases, worktrees,
   containers, scratch files, remote state), enumerated **by class and never by a
   single tool**, and stage 10 does not close while this run's residue is live and
   unaccounted (`references/residue.md`); and remember that a
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

| # | Stage | Gate | Type |
|---|---|---|---|
| 0 | Intake grill — **mandatory** | source ledger written **with its `Contradictions:` line** — the harvest converges on one brief and nothing else compares the sources with each other; **the documentation inventory answered into `docs/DOCMAP.md`** — registers, single homes, the propagation matrix, the gate command — and **intent reconciled against as-built**, every divergence resolved ([`references/documentation.md`](references/documentation.md)); the retro read in full and its archive queried; shared understanding reached; autonomy sweep covered; brief locked + confirmed | manual |
| 1 | Docs study | contracts grounded on fetched docs | auto |
| 2 | Brainstorm + decompose | design approved; UI verdict recorded; every REQ answered; platform: module map approved | manual |
| 3 | Spec | committed + reviewed; UI: chain validated, linter green, scenarios/`SCR-` traced; **COPY and VISUAL are a parallel layer after UX, and where both ran their convergence check is recorded** — a label the layout has no room for is right in each track and wrong on the screen ([`references/stages.md`](references/stages.md)) | manual |
| 4 | Plan | parallel-ready, DoD per task; **every edge names what it carries** — the fake-edge test run, its `Edges:` count computed, and no arrow left whose payload nobody can name ([`references/planning.md`](references/planning.md)) | auto |
| 5 | Dev | tasks DONE, TDD green per task, branch integrated per the brief; **a fanned-out group gets one convergence check over all its diffs together before the first worktree lands** — a per-task review cannot see a contradiction that exists only between two of them ([`references/build.md`](references/build.md) §4.2a); **anything generated passes its own checks, and local infrastructure does not publish the host's default ports** ([`references/learned.md`](references/learned.md)) | auto |
| 6 | Tests | full suite green; new/changed code covered; **every new check probed both ways and asserted on its exit code**, and the suite run once against a cold environment ; **on a web front end the surface is checked in a browser, not in the diff** — a green suite cannot see a component that renders under a fixed header, a request that 404s past its mock, or a console error — and a browser **test suite** is the other half of the pair, never a substitute for the look (`playwright` or `chrome-devtools`, either one — **how**: [`references/browser.md`](references/browser.md), which channel: [`references/companion-skills.md`](references/companion-skills.md); absent → say *verified by reading the diff* and record it as the weaker claim it is) | auto |
| 7 | Lint + deploy | lint clean + suite green before deploy; deploy needs a go (or the brief's specific standing authorization) | manual |
| 8 | Post-deploy | clean boot or honest degradation report; **a deployed web target is opened, not curled** — a `200` proves the server answered and says nothing about a 404'd bundle or a console full of errors on load (`playwright` or `chrome-devtools`, either one, [`references/browser.md`](references/browser.md); absent → call it an HTTP response, which is its honest name) | auto |
| 9 | Docs + wiki | every stale row of the stage-0 source ledger updated; **the propagation matrix walked for every change type this run produced** — the ledger names what you read, the matrix names what you owe — every settled thing recorded with an id, every answered question resolved, and **the documentation gate green with its ratchet counts printed**; docs synced; wiki synced; **the code graph refreshed where one exists** and checked against the docs (a hub no doc names, a doc naming a node the graph lost); **every number computed rather than restated, every named command or file resolvable** ([`references/learned.md`](references/learned.md)); the carry-over count printed beside the verdict | auto |
| 10 | **Acceptance** | ladder walk ran, its absences became REQ rows; every REQ accounted for with evidence from a check seen failing once; ledger has no unresolved row; **axis rotation recorded** (new findings vs self-inflicted, rule 1 of [`references/learned.md`](references/learned.md)), **every closure verified against the artefact rather than the document describing it**, **each correction swept across its class**, **every deferral a printed ratchet rather than a TODO**; **in a multi-repository project, every repository is clean, pushed and pointed at** (below); **the hand-back is written** — the request quoted as given, progress against it, what was solved, what surfaced unasked, waiting decisions asked here, and the ambiguity count computed ([`references/progress.md`](references/progress.md)); **the environment is given back** — all eight classes enumerated, what this run started ended and verified by re-enumerating rather than by the teardown's reply, an earlier run of this project ended only when **provably spent**, anything this project does not own reported rather than ended, written as a `holds:` line (`references/residue.md`); operator signs off; **every check this close-out leans on — the documentation gate included — has been seen failing once against a planted defect, and its ratchet counts are printed beside the verdict**; **the retrospective written last, and in order — the run stamped with its commit FIRST (the cold-retirement trigger reads that stamp), then the prune with the list at or under its cap and every deletion logged, then the entry; every deletion and every entry carrying its commit, entries older than five stamps rotated into the archive, counts printed** ; **every disclosure printed beside the verdict** — `abstained` (what the run declined to claim) and `unlooked` (what a check never looked at), neither a ratchet, neither with a floor, neither ever a target ([`references/gates.md`](references/gates.md) → *Disclosures*) | manual |


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

Every reference is routed from the **Built-in doctrine** table above, keyed by
the stage that sends you there — one home for that mapping rather than two. The
two config contracts sit beside this file: `pipeline.schema.json` (the universal
stages + release contract) and `pipeline.example.json` (this plugin's default
flow as config).
