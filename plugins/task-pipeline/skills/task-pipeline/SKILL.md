---
name: task-pipeline
description: "Use when work changes the repository: feature, fix, refactor, migration, integration, audit, PR review; фича, баг, интеграция, аудит. Runs a substantial task through gated stages to acceptance; 'waves'/'волнами' closes the board. Not for questions or one-line edits; 'без пайплайна' opts out."
license: MIT
compatibility: "Doctrine runs on any agent. The bundled scripts need python3; the run needs git. Missing either degrades, never blocks — the graph verbs and seeded gates go unused, and the run says so."
---

# task-pipeline

Self-contained orchestrator. Runs a task through **gated stages**, each carrying its
own built-in doctrine; no companion plugin is required. No stage advances until its
gate passes, and the whole run uses one model, confirmed before it starts.

**Proportional, then autonomous.** Stage 0 is a **gap check** before it is an
interview: the brief is built from the request, the files and the harvest, and a
question is asked only for a **material unknown** the sources cannot answer. A
complete brief yields ZERO intake questions; what the request or the project already
decided is recorded, never re-negotiated. When the change is also small (R1 risk, at most five
files, no public contract, no user-facing change, no deploy), the run **takes the short
path by default** and says so in one line: brief in the run ledger, build with tests,
one verification, docs and handoff, a retro entry only for a new lesson
([`references/stage-00-intake.md`](references/stage-00-intake.md) → Phase 1d, which
also names the triggers that bring a skipped stage back). Anything larger runs the
full flow, with the interview, where gaps remain, as ONE batch that pre-resolves
stages 1→10: every MATERIAL question skipped at stage 0 comes back as an interruption
later.

**Config contract: [`pipeline.schema.json`](pipeline.schema.json).** A pipeline is an
ordered list of stages, each with `skills[]` and a `gate {type, check}`; the schema
imposes no stages, skills or gate assignments.
[`pipeline.example.json`](pipeline.example.json) is the copy-and-rewrite example of
this plugin's default flow (stage 0 plus the 1→10 stages below) and an optional
`release` block.

**Two layers, and only one is replaceable.** The **KERNEL** is what every unit of
work carries in any pipeline: its **scope**, its **evidence**, its **deps** and a
**resume** point. The kernel is invariant. The **PROFILE** is the stage list, and a
project replaces it wholesale. **The stage numbers belong to the SELECTED profile,
never to the kernel:** a minimal three-stage profile has no "stage 7", and a rule
keyed on a global stage number is a rule about the default profile. A custom profile
may drop stages, never a kernel field. Each gate has a **type**: `auto` (the orchestrator verifies the
`check`), `judgment` (a named judge rules, recorded as judgement, never as a
measurement; `references/gates.md` → *The judgment gate*) or `manual` (an explicit go).
**The
default profile's gates are `auto`; a gate is `manual` only where the operator's
`pipeline.json` says so, and a standing operator authorization naming the act counts
as the go.** In `skills[]`, `task-pipeline:<name>` is this skill's own doctrine
(`references/<name>.md`) and `host:<name>` the host project's own command
(`references/conventions.md`).

## Prerequisites: none required

Every stage's doctrine ships inside this skill, and **no stage blocks on an install**:
stage 1 falls back to web search, the wiki and the code graph are recommendations.
Which reference owns which stage:
[`references/doctrine-map.md`](./references/doctrine-map.md). **Precedence:** on a
CUSTOM profile the **kernel wins**; `references/stages.md` is the **default
profile's** normative gate set; the kernel is normative for all; another skill set on stages 2/4/5/6 is
`references/companion-skills.md`.

**super-ux is the preferred provider for ANY user-facing task**, and **the stage-3
gate checks the ARTIFACT, not the package**: valid scenarios covering the change, from
super-ux, an equivalent provider or the inline fallback in
`references/companion-skills.md`, pass. The ABSENCE of any scenario artifact stops the
gate; a missing tool is reported as the NAMED check that was not done, never as a
failed task.

**The grill is built in** (`references/grill.md`) and produces the **REQ spine**: the
request as an addressable list, each row naming how it is verified, which stages 3–5
trace to and **stage 10 accounts for every one of**. **Harvest before you ask**
(`references/knowledge-sources.md`): stage 0 pulls what the project already knows,
writes the source ledger, and checks every answer against it; the operator outranks a
document **but only out loud**.

**Three artifacts close a run and they converge:** stage 9 syncs the docs, the wiki
and the code graph, and the graph↔docs divergence check is the gate over them where a
graph exists (`references/knowledge-graph.md`). **Documentation is a deliverable with a
gate** (`references/documentation.md`): `docs/DOCMAP.md`, the Doc Loop at any stage,
the propagation matrix at stage 9, and *"docs in sync"* as a command with an exit code.

**The run teaches the next run, and the list stays short**
(`references/retrospective.md`). Stage 10's last act, **in this order and the order is
load-bearing**: stamp the run, then prune, then write the entry (`references/learned.md`
rule 21). The floor stage 0 reads in full (standing instructions plus run stamps) has
a **byte budget**: `scripts/retro_budget.py check` prints its bytes and bytes/4 tokens
at stage 0, and gate 10 fails over budget until `migrate` moves the narrative to the
archive, verbatim and hash-proved.

## How to run

1. Restate the task in one line, track each stage from 0 (host task tool or a prose
   checklist, for resume), then emit the **preflight block** once: the model decision
   (`references/model-tiering.md`: recommend the most capable model as advice, the
   operator confirms or overrides, the choice — inherited verbatim by plan, stages and
   subagents), the run mode (`pipeline.json` → `run.loop`,
   `references/continuity.md`; absent means off, and the mode never collapses a
   `manual` gate) and the optional companions: super-ux for UI tasks, context7,
   wiki-update, graphify (`references/companion-skills.md`).
2. **Run stage 0.** Harvest, then the gap check, then the proportional decision
   (`references/stage-00-intake.md`). **Entered from super-ux** (a validated
   `docs/ux/` chain or a `docs/ux/plans/…` fix plan exists)? Check `/ux-lint` green,
   confirm scope in one line and skip to the first stage with real work.
3. Walk the stages on the model confirmed at preflight; don't re-ask it per stage.
   **The SELECTED profile is compiled once, at preflight, and only ITS declared
   stages and gates run**: a custom profile with three stages runs three, and no
   hidden stage 0, 7 or 10 is injected. What a custom profile does NOT escape is the
   KERNEL: dropping stages never drops the evidence gate. And an unknown MANDATORY
   capability blocks the compile: a `must_understand` capability this runtime lacks is
   refused, never run with the capability silently absent. **A platform rather than a change?** Stage 2 cuts it into modules
   (`references/decomposition.md`) and stages 3→10 run per module
   (`references/stages.md` → *The program loop*). **The whole board?**
   `/task-pipeline waves` (`references/waves.md`). **Releases:**
   `references/iteration.md`; findings are triaged when found, and the iteration stops
   at its finish line: exit checks green on the artefact and one round with no new
   blocking finding (two for an R3 or flagship node), or the budget spent
   (`references/finish-line.md`).
4. Do **not** advance until the stage **gate** passes (`references/stages.md`). For
   `auto`, verify the `check` yourself; for `judgment`, record the ruling as judgement;
   for `manual`, cite the operator's go or the standing authorization naming this act.
   **Loops stop:** an R1 node certifies with one blind tier and a clean round ends a
   node unless it is R3 or flagship; the certification ceiling parks the node with its
   evidence and moves on; no tier re-runs on unchanged input; the review loop caps at
   three rounds (`references/certification.md`, `references/loop-guard.md`).
5. **Cross-cutting rules fire at any stage** (the Doc Loop, the loop guard, the
   audit's exit, the finish line, the frozen REQ list, the carry-over ledger, and
   what counts as evidence), and every gate prints `holds: N` across all eight residue
   classes; stage 10 does not close while this run's residue is live
   (`references/residue.md`). Their long form is
   [`references/gates.md`](references/gates.md) → *Cross-cutting, at every stage*.

## What to read, and when

At entry read **this file only**; its stage table below is the stage index. Each
stage's detail is read **when that stage starts** (`references/stages.md` routes it,
one section at a time; never preload all details). The rest loads on its trigger:

| Reference | Read when |
|---|---|
| `references/grill.md` | the gap check leaves a material unknown |
| `references/knowledge-sources.md` | a source needs more than its ledger row: the code graph, the wiki, a lesson store, a carried-in claim, a stale row |
| `references/companion-skills.md` | a user-facing task (the provider rule), a substituted skill set, or a companion is missing |
| `references/continuity.md` | `run.loop` is armed, a context-budget signal arrives, or a run resumes |
| `references/model-tiering.md` | the operator overrides the model, or a stage map differs |
| `references/gates.md` | you write or change a check, a gate's verdict is disputed, or a judgment gate runs |

## Stages (gates and routes in `references/stages.md`)

All stages run on the **one model confirmed at preflight**.

| # | Stage | Gate | Type |
|---|---|---|---|
| 0 | Intake grill — **mandatory** | source ledger written with its `Contradictions:` line; `docs/DOCMAP.md` answered and intent reconciled against as-built; the retro floor read in full, its bytes printed; autonomy sweep covered; UI: `surface_class` recorded; brief locked and confirmed | auto |
| 1 | Docs study | contracts grounded on fetched docs | auto |
| 2 | Brainstorm + decompose | design approved; UI verdict recorded; every REQ answered; **the queue is an artifact** — a work graph validates and its coverage names no unserved REQ; platform: module map approved | auto |
| 3 | Spec | committed + reviewed; UI: chain validated, linter green, scenarios and `SCR-` traced; COPY and VISUAL are a parallel layer after UX, and where both ran their convergence check is recorded; VISUAL is checked by its director record | auto |
| 4 | Plan | parallel-ready, DoD per task; **every edge names what it carries** — the fake-edge test run and its `Edges:` count computed; **`scripts/plan_audit.py` clean** — every live node's packet survives a cold reader, and no two unordered nodes edit one file | auto |
| 5 | Dev | tasks DONE, TDD green per task, branch integrated per the brief; a fanned-out group gets **one convergence check over all its diffs together** before the first worktree lands | auto |
| 6 | Tests | full suite green, new and changed code covered, every new check probed both ways and asserted on its exit code; **a web surface is checked in a browser, not in the diff** — where a browser channel is connected; absent, the weaker claim is recorded; a gated surface's contact sheet passes | auto |
| 7 | Lint + deploy | lint clean and suite green before deploy; deploy needs a go, or the brief's specific standing authorization | auto |
| 8 | Post-deploy | clean boot or an honest degradation report; **a deployed web target is opened, not curled** — a `200` proves the server answered and nothing else; where no browser channel is connected, the weaker claim is recorded | auto |
| 9 | Docs + wiki | every stale row of the stage-0 source ledger updated; the propagation matrix walked for every change type this run produced; the documentation gate green with its ratchets printed; docs, wiki and the code graph synced and checked against each other | auto |
| 10 | **Acceptance** | the ladder walk ran and its absences became REQ rows; every REQ accounted for with evidence from a check seen failing once; no unresolved ledger row; **every repository clean, pushed and pointed at**; the hand-back written and the environment given back; the retrospective written **last**, in order and within its byte budget | auto |

**Every gate above is the short form**; the long form is
[`references/stages.md`](references/stages.md). CUSTOM profiles use their own declared
doctrine; matching numeric ids do not select default details. **Several
repositories?** A submodule is finished when its parent says so:
[`references/acceptance.md`](references/acceptance.md) → *A project of several
repositories*.

## Model: ask once, at preflight

Recommend **the most capable reasoning model available**, a tier resolved at runtime,
**never a hardcoded id** (`references/model-tiering.md` → *Mechanic*). Record the
answer in the brief; stage-5 subagents are pinned to it.

## Degradation

- **No python3** → the work-graph verbs and the seeded gate scripts cannot run: the queue degrades to a prose plan, the gates to checklists — said out loud, never silently.
- **No git** → no worktree isolation and no commit-addressed evidence: the run records the weaker claim instead of pretending to the stronger one.
- **No browser channel** → a web surface is verified by reading the diff, and the close-out records that as the weaker claim it is.

## Bring your own skills

The stages above are the **example** flow. A host copies `pipeline.example.json` →
`pipeline.json`, defines its own stages (any count), points each `skills[]` at what its
environment resolves, sets each `gate.type` (`auto`/`judgment`/`manual`) and toggles its
own `release` block. `pipeline.schema.json` is the only contract.

## References

Most references are routed from `references/doctrine-map.md` by stage. The rest are
routed by prose: `stages.md`, `learned.md` (cited where a rule binds) and `probing.md`
(from `gates.md`). Beside this file: the config contracts, and the family's
task/context contract, `execution-packet.schema.json` and `execution-result.schema.json`
with their examples, validated dependency-free by `scripts/packet.py` (an unknown
mandatory version, a ref without its digest, or an unbound decision is rejected; a stale
result re-plans instead of landing). `scripts/context_packets.py compile|verify` maps an
audit report onto parent tasks: ids derived from finding ids, never positional, and any
row it cannot map blocks the compile.

## Triggers

The description is the short form. The full trigger list it carried until 1.98.0,
moved here verbatim, still routes to this skill:

"Use when work changes the repository — feature, fix, bug, refactor, migration, integration, rewrite, adoption or hardening; фича, фикс, баг, рефактор, миграция, интеграция, доработать, починить, внедрить, перевести — or a finding that lands in it: audit/аудит, bug hunt/проверь ошибки, production check/проверь прод, PR review/ревью PR — or on 'run this through the pipeline'/'прогони по конвейеру', 'the full cycle'/'полный цикл', /task-pipeline. Runs a substantial task through gated stages: intake grill, docs, brainstorm, spec, plan, build, tests, deploy, post-deploy, docs/wiki, acceptance. 'waves'/'волнами'/'release iteration'/'итерация релиза' closes the board; 'checkup'/'чекап' lists unconfirmed releases; 'setup' audits docs. Not for: answering a question, explaining, a typo, a one-line edit, a rename, recon that lands nothing — say 'no pipeline'/'без пайплайна' to opt out."

Added in 1.102.3 (hub board row B-84), each a repository change that runs through the
stages: 'write tests'/'напиши тесты', 'cut a release'/'зарелизь'/'выпусти релиз',
'remove dead code'/'удали мёртвый код'.
