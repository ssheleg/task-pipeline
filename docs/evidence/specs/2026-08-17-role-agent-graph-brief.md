# Brief — task-pipeline as a role-based agent graph

**Status:** stage 0, grill open. Not locked. No REQ table yet — it is written when
the grill closes, and stage 1 does not start before this file is committed and
confirmed.

**Request, as given** (2026-08-17, operator, verbatim intent):

> More advanced work graph — agents work dynamically and more autonomously, but do
> what was intended: they do not invent and do not lie. Where something is unknown
> they decide from what the skills and instructions already know, or they ask the
> operator. The grill runs through the **product funnel**, including what behaviour
> the user is expected to have. Docs only by our rule. The plan is decomposed into
> tasks, and the detailed decomposition is done by **separate agents, one per
> top-level plan item**. A **manager** agent moderates; a **business analyst** grills
> further where needed; a **UX** agent checks the product scenarios and funnels are
> right; a **UI** agent checks the design is described or drawn and proposes
> **mockups before any markup work** where there is no Figma — and more mockups
> generally. More separate agents each taking one concrete task, a manager agent that
> checks, each with its own role, correct orchestration and correctly described loops
> inside the pipeline. Subagents wherever they buy speed.
>
> A feature is built **only if it is clear why it exists and its function is fully
> understood**. Otherwise it goes to the backlog, and into the grill if needed.
>
> The loop does not start by itself: typing `/loop` with "take the backlog and walk
> every task, one per iteration, no pauses, each through task-pipeline" works, but
> the agent never arms it on its own. The loop exists so that an agent that stalls
> mid-backlog wakes itself and continues. The backlog is **dynamic** — solving a task
> may add new ones; after each task, re-prioritise, then take the next one or park it.
> After every task, check against the **release goal** and the backlog.

---

## Source ledger — what the project already knows about this task

Written before the first grill question, per `references/knowledge-sources.md`.
Every row was read in this checkout on 2026-08-17.

| Source | What it already answers | Bearing on this task |
|---|---|---|
| `references/build.md` | subagent per task at stage 5, isolated worktrees, implementer / reviewer / fixer, dispatch-prompt hygiene, "a subagent never writes the register" | **The subagent machinery exists.** What is missing is *product* roles, not execution roles |
| `references/decomposition.md` (148 ln) | cutting a platform into modules at stage 2, the module map, cross-module contracts, its own manual gate | Decomposition exists **one level up**. Per-plan-item detailed decomposition by an agent each is new |
| `references/planning.md` | fan-out, edges and their payloads, the fake-edge test | The graph vocabulary exists; roles do not sit on it yet |
| `references/continuity.md` (312 ln) | **the loop already has doctrine** — Part 1a: the queue is stage 2's and the loop arms at the close of stage 2; "where nothing is recorded, nothing arms"; arming on Claude Code; what one iteration means; parked at a manual gate | The mechanism is not missing. See the finding below |
| `references/grill.md` (274 ln) | the intake grill, one question per turn, the autonomy sweep | The **product funnel** is not among its axes |
| `references/documentation.md` | the Doc Loop, the propagation matrix, `docs/DOCMAP.md` | "docs only by our rule" is already this |
| `references/companion-skills.md` | `super-ux`, `sheleg-design`, `copywriting` detection and fallbacks | **The family already owns UX and UI.** A new UX/UI role must dispatch to them or say why not |
| `references/portability.md` (143 ln) | the workflow/project boundary — *"How does the pipeline behave?"* → bundle; *"What did we decide here?"* → project | Governs whether role agents may be Claude-Code-specific |
| `references/model-tiering.md` | per-stage model overrides | A role graph wants per-role tiers |
| `docs/evidence/retro.md` | **six standing instructions bind this run**, notably `R-005` (an independent reader on any new or widened check before merge) and `R-008` (enumerate the defect's shapes before writing the fix) | Both apply directly: this adds checks and changes gates |
| `docs/evidence/backlog.md` | 45 rows, **0 open** | Nothing here competes for the slot |
| `docs/evidence/verification.md` | 129 lines carrying `never`; the ledger reaches v1.68.0 as of 2026-08-17 | Stage 8 rows for this work land here |
| `plugins/task-pipeline/.claude-plugin/plugin.json` | declares `name, displayName, description, version, author, homepage, repository, license, keywords` — **no `agents` key**, and no `agents/` directory | Role agents as plugin agents would be new here |
| `make-skill` plugin | ships `agents/skill-auditor.md`, and it resolves in this harness as `make-skill:skill-auditor` | **Precedent exists in this family**, and it was used in this session's audit |
| umbrella `pipeline.json` → `run.loop` | `mode: dynamic`, `queue: module-map`, `arm: after-decomposition` — and **`command` deliberately absent**, with a recorded note (B-25, 2026-08-13) | See the finding below |
| `graphify-out/graph.json` | present, built at `ccd03a40`, 1 commit behind HEAD | Available for reach questions at stage 2 |

### One finding the harvest settles before the grill opens

**The loop is not broken and nothing needs building for it to arm.** The umbrella's
`pipeline.json` records `run.loop.mode: dynamic` and *deliberately omits* `command`,
with the reason written in the config itself:

> *"`command` is deliberately ABSENT: this harness has a loop primitive, and this run
> does not use it — the queue advances within the session rather than across
> scheduled wakeups, so the mode is prose discipline plus the build ledger and says
> so rather than implying it is armed by a timer."*

So the operator's complaint — *"if I don't type `/loop` myself, the agent never starts
one"* — is a **recorded decision from 2026-08-13 that no longer matches what the
operator wants**, not a defect. That changes the work: this is a decision to revisit
in the grill and a config change, not a feature to build. Whether the doctrine's
default should also change is a separate question, and it is a `portability.md`
question: *"how does the pipeline behave?"* → bundle.

---

## Grill — closed decisions

Seven resolved. Each was asked with a recommendation and checked against the ledger.

| # | Question | Decision | Consequence |
|---|---|---|---|
| G-1 | Where do role agents live? | **Plugin `agents/` + honest degradation.** Where a host has no subagent primitive the main thread plays the role in sequence and says so | New `agents/` surface in the plugin manifest. Precedent: `make-skill` ships `agents/skill-auditor.md` and it resolves in this harness |
| G-2 | UX and UI roles vs `super-ux` / `sheleg-design` | **Dispatchers, not second opinions.** The UX role runs super-ux's checks and reports; the UI role runs sheleg-design and proposes mockups | Keeps one home per fact. No UX or design doctrine enters this bundle |
| G-3 | Loop auto-arming | **Arms on recorded intent.** `run.loop.command` gets recorded in the projects that want it; stage 2's close arms it and prints the job id and cancel command | Revisits the 2026-08-13 decision explicitly. *«Where nothing is recorded, nothing arms»* survives |
| G-4 | The role set | **Wider than proposed** — see below | This is a program, not a change. Stage 2 cuts it |
| G-5 | «Understood, or backlog» | **Both** — stage 0 flags and records the doubt, stage 2's gate refuses to leave with it unresolved | Two places state one rule, so one of them must be the home and the other must cite it (`documentation.md`) |
| G-6 | Where the product funnel comes from | **`super-ux` is mandatory for any user-facing feature** | This adds a **second** gate-stopping dependency. Today there is exactly one. Recorded as a deliberate cost |
| G-7 | Where the release goal lives | **`pipeline.json` → `release.goal`**, printed beside the queue on every loop iteration | A project answer, per `portability.md`. Drift from the goal becomes visible rather than remembered |

### G-4 in full — the roles the operator named

Beyond manager / BA / UX / UI / decomposer:

- **Verifier** — accepts the agents' work when a task closes. Compares what came out
  against what was asked, names what is *not* done, lists blockers, and decides whether
  the run can continue by re-planning around them. Where it can, **it triggers the
  backlog re-plan and the cycle continues**; where it cannot, it stops. This is the
  role that makes the loop autonomous rather than merely repeating.
- **Researcher** and **market analyst** — so a hypothesis the operator states can be
  researched rather than assumed. Research runs through **`prowl`**.
- **Project** — reads **Sentry** where connected: check the bugs there, and either
  propose them into the backlog or solve them. Offer to connect it where absent.

### What the harvest already settles about those

| Named | Actual state on this machine | Consequence |
|---|---|---|
| «offer to install prowl-cli» | **Already installed** — `prowl-cli@prowl` v0.2.0 enabled, skill `prowl-cli` present; `prowl@prowl` and `prowl-brand@prowl-brand` too | Nothing to install. What may be missing is the token, and `~/DATA/0xDEV` (the Prowl project itself) carries `docs/ENV_REFERENCE.md` |
| «prowl MCP may not work» | `prowl` MCP has connected and disconnected repeatedly in this session | The research role must degrade to `prowl-cli` and say which it used — never claim a source it did not reach |
| Sentry | **No Sentry MCP configured anywhere** — `settings.json → mcpServers` holds only `meta-ads` | The project role is a capability for host projects, absent here. It must degrade, not block |
| The visualiser | Nothing exists | A **local server, a page, a live task graph, tabs per Claude Code instance** is a separate installable product, not a task-pipeline reference file |

---

| G-8 | Where does the visualiser live? | **A separate family member, shipped last.** A new repo + plugin, optional and recommended, reading the run ledger this pipeline already writes | Keeps a Node server and web assets out of a bundle that is prose and python. It visualises a graph that does not exist yet, so building it first would draw a picture of something unbuilt |
| G-9 | What is the walking skeleton? | **Work graph + verifier + loop.** The smallest thing that actually turns end to end without a human between iterations | Every other role plugs into a graph that already turns. Roles-first would leave the autonomy arriving last |
| G-10 | Sentry, with none connected anywhere | **Split the role.** The `project` role keeps its other duties; a separate **bug-analyst** role owns error and log intake — Sentry **and** production logs, database logs, wherever else they land. Its first job is to find out *how* they are collected, build the collection, and then use it regularly | Broader than Sentry and therefore useful in a project that has none. Degrades honestly where nothing is reachable, like the browser, graph and wiki already do |

### The role set, closed — thirteen

Ten product roles, on top of the three execution roles `build.md` already ships.

| # | Role | Owns | Dispatches to |
|---|---|---|---|
| 1 | **manager** | moderates the graph: who runs next, what is blocked, when a stage may close | — |
| 2 | **business analyst** | a second grill where the brief is thin; the *why* behind a feature | `grill.md` |
| 3 | **UX** | the product scenarios and funnels are right | `super-ux` |
| 4 | **UI** | design is described or drawn; **mockups before any markup** where there is no Figma | `sheleg-design` |
| 5 | **decomposer** | one per top-level plan item — the detailed cut below it | `decomposition.md`, `planning.md` |
| 6 | **verifier** | accepts a closed task: what is done, what is not, the blockers, and whether a re-plan lets the run continue | triggers the backlog re-plan |
| 7 | **researcher** | turning an operator's hypothesis into evidence | `prowl` / `prowl-cli` |
| 8 | **market analyst** | the market half of the same question | `prowl` / `prowl-cli` |
| 9 | **project** | the project's own standing duties | — |
| 10 | **bug-analyst** | error and log intake: Sentry, production logs, database logs. **First find out how they are collected, then build the collection, then use it regularly** | degrades where nothing is reachable |
| — | implementer / reviewer / fixer | already shipped | `build.md` |

---

## REQ table — the brief's frozen list

Adding is free. Removing needs the operator. Every row names how it is verified.
Stage 2 assigns each row to exactly one module; the module column is its proposal,
not yet its gate.

| REQ | What must be true | Verified by | Module |
|---|---|---|---|
| REQ-001 | A **work graph** is a named artifact with a schema: nodes carry `id`, `title`, `owner` (a role), `status`, `blocked_by`; edges carry a payload | the schema file exists and `npm test` validates an example against it | 1 |
| REQ-002 | **Every node names its owning role.** A node with no owner fails the gate | planted node without `owner` → gate red | 1 |
| REQ-003 | `planning.md`'s **fake-edge test** applies to graph edges — an arrow whose payload nobody can name is removed | planted payload-free edge → gate red | 1 |
| REQ-004 | The graph is **written at stage 2** and is the queue the loop advances | `references/work-graph.md` states it; stage-2 gate criterion names it | 1 |
| REQ-005 | A **verifier** role exists as `agents/verifier.md`, discovered by convention | `claude plugin validate --strict` green; the agent resolves by name. **Amended 2026-08-17:** this said *declared in `plugin.json`*, and declaring it fails `--strict` with `agents: Invalid input`. The family's own working example — `make-skill`, which ships `agents/skill-auditor.md` and resolves — declares no `agents` key at all. The reversal was recorded only in a test comment until the wave-2 convergence check said so | 1 |
| REQ-006 | At a task's close the verifier emits a verdict naming: what is done, **what is not**, the blockers, and a re-plan proposal | a fixture asserts all four fields present | 1 |
| REQ-007 | Where the verifier can continue, it **triggers the backlog re-plan** and the graph advances; where it cannot, it stops and names why | fixture on both branches | 1 |
| REQ-008 | `run.loop.command` recorded → **stage 2's close arms the loop**, printing the job id and the cancel command | fixture over a config with and without it | 1 |
| REQ-009 | **Where nothing is recorded, nothing arms** — the existing limit survives the change | fixture: absent config arms nothing | 1 |
| REQ-010 | `pipeline.json` gains `release.goal`, and the loop **prints it beside the queue every iteration** | fixture on the printed line | 1 |
| REQ-011 | The backlog is **dynamic**: rows added during a task enter it, and it is **re-prioritised after every task** before the next is taken | fixture over a backlog mutated mid-run | 1 |
| REQ-012 | A task that does not serve the release goal is **parked with that as the reason**, not silently skipped | fixture asserts the reason is recorded | 1 |
| REQ-013 | Ten role agents ship as `agents/*.md`, each with one gate it owns and one artifact it writes | file per role; `claude plugin validate --strict` green | 2 |
| REQ-014 | Where the host has **no subagent primitive**, the main thread plays the role in sequence **and says so** | the degradation is stated in `portability.md`'s manifest and in the role doctrine | 2 |
| REQ-015 | The **UX** role dispatches to `super-ux` and holds no scenario doctrine of its own | grep: no scenario/funnel doctrine in the role file | 2 |
| REQ-016 | The **UI** role dispatches to `sheleg-design`, and **proposes mockups before any markup work** where no Figma resolves | the rule is a stage-3 gate criterion | 2 |
| REQ-017 | A **decomposer** is dispatched **per top-level plan item**, in parallel | `build.md`'s fan-out rules apply; a fixture asserts one dispatch per item | 2 |
| REQ-018 | Each role declares its **model tier**, never a vendor id | the no-hardcoded-model guard already in `validate.py` covers the new files | 2 |
| REQ-019 | **«Understood, or backlog»** — stage 0 flags and records the doubt | `grill.md` states it; a fixture asserts the recorded field | 3 |
| REQ-020 | The same rule is a **hard gate at stage 2**: the run cannot leave with it unresolved | stage-2 gate criterion; planted unresolved doubt → gate red | 3 |
| REQ-021 | The rule has **one home and one citation**, never two statements | `documentation.md`'s single-home check | 3 |
| REQ-022 | The grill runs the **product funnel** — including the behaviour expected of the user | `grill.md` gains the axis; a fixture asserts it is asked | 3 |
| REQ-023 | `super-ux` becomes a **gate-stopping dependency for any user-facing feature** | `companion-skills.md` records it as the second such dependency, with its cost | 3 |
| REQ-024 | A **researcher** and a **market analyst** role run through `prowl`, and **degrade to `prowl-cli`** where the MCP is unreachable — never claiming a source they did not reach | fixture on both paths; the used source is named in the output | 4 |
| REQ-025 | A **bug-analyst** role reads Sentry, production logs and database logs; where none is reachable it **says so once, offers the connection, and the run continues** | fixture: absent everything → one disclosure, no block | 4 |
| REQ-026 | The bug-analyst's first act is to **establish how logs are collected** and record it, before reading any | the role file states the order; a fixture asserts the recorded finding | 4 |
| REQ-027 | Findings become **backlog rows or fixes**, never a report nobody files | fixture asserts a row id or a task | 4 |
| REQ-028 | A **visualiser** ships as a separate family member: a local server, a live task graph, tabs per agent instance, reading the ledger this pipeline writes | its own repo, plugin and gate — a separate release | 5 |
| REQ-029 | Every new or widened check gets an **independent reader before merge** | standing instruction `R-005`, and the run says who read it | all |
| REQ-030 | Before each fix, **the defect's shapes are enumerated** and the fix says which it covers | standing instruction `R-008` | all |

### Deferred, in the carry-over ledger the moment it was said

| Item | Why deferred | Home |
|---|---|---|
| The visualiser (REQ-028) | it draws a graph that does not exist until module 1 ships | module 5, its own repo |
| Connecting a Sentry MCP | no project here reports to Sentry; the role degrades instead | board row after this program |
| Per-role model tiers beyond the default | `model-tiering.md` already carries the mechanism | module 2 |

---

## Stage 0 gate — MANUAL, and it is open

The brief is written, the ledger is above it, ten decisions are recorded and the REQ
table is frozen at thirty rows. **Stage 1 does not start until the operator confirms
this brief.**

Two things the operator should weigh before confirming:

1. **This is a program, not a task** — five modules, one of which is a separate
   installable product. The walking skeleton is module 1 and it is the only one that
   makes the pipeline autonomous; modules 2–5 add breadth to a thing that already turns.
2. **REQ-023 adds the second gate-stopping dependency this pipeline has ever had.**
   Today `super-ux` blocks only the stage-3 spec on a UI task. Making it block *any*
   user-facing feature is a real narrowing, and `portability.md` treats it as a cost
   rather than a free win. It is what was asked for and it is recorded as deliberate.

---

## Stage 1 — docs study. Gate: `auto`, verified

*Every contract the design locks, grounded on a fetched doc or a measurement — never
on recall. Run 2026-08-17.*

| Contract | How it was grounded | What it says |
|---|---|---|
| **Plugin agent frontmatter** | fetched `code.claude.com/docs/en/plugins-reference` | `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation` — and **`hooks`, `mcpServers`, `permissionMode` are rejected for plugin-shipped agents, for security**. `isolation`'s only legal value is `"worktree"` |
| **How a role is invoked** | same fetch | `<plugin>:<agent>` in the @-mention typeahead, once enabled. So the roles resolve as `task-pipeline:verifier` and so on |
| **The family's own reading was current** | compared the fetch against `make-skill/references/host-capabilities.md`, *read 2026-08-03, Claude Code 2.1.212* | **identical on fields and rejections.** Two weeks old and still true — checked rather than assumed |
| **What an agent costs** | `claude plugin details make-skill@make-skill` | **~110 always-on tokens** for `skill-auditor`, ~600 on-invoke. The family's `~100` estimate holds against a measurement |
| **What it lands on** | `claude plugin details` across all eight members | the family costs **~8,445 always-on tokens in every session**. Ten roles = **+13%**; seven = **+9%** |
| **The loop's config vocabulary** | read `pipeline.schema.json` → `definitions.run` | `mode` is `off` \| `interval` \| `dynamic`, `mode` is **required**, and the object's absence defaults everything OFF — *"silence arms nothing and authorises nothing"* |
| **`prowl-cli`** | read the installed `prowl-cli` v0.2.0 skill | `@prowl-ai/cli`, Node 18+, `PROWL_API_KEY`, 448 tools, documented exit codes, and a section named *"Tiers, and the downgrade that is not a refusal"* — which is exactly REQ-024's shape |

### Three findings that change the design

**1. Not every role earns an agent, and the rule is already written.**
`host-capabilities.md`: *"A subagent earns its always-on cost when the work is
**voluminous and separable** — because its output is a summary while its reading stays
in its own context. It does not earn it when the main thread needs the intermediate
detail anyway."* By that rule the **manager** and the **verifier** are the two that do
**not** qualify: deciding who runs next and acting on a verdict are the main thread's
own work, and shipping them as agents pays 220 tokens a session to move a decision
out of the context that has to make it. Stage 2 decides this per role; the budget is
not the argument, the rule is.

**2. `continuity.md` documents the older half of the loop.** Its *«Arming it on
Claude Code»* section describes only `/loop <interval> <invocation>` and its
constraints — intervals must divide cleanly, session-only, seven-day expiry. The
schema already defines `dynamic` as *"the harness schedules its own next"*, and the
umbrella's config already records `mode: dynamic`. So the vocabulary is complete and
one section is behind it. **New REQ, and adding is free.**

**3. Two of this stage's own measurements were wrong before they were right.** The
first family total read **~2,634** because the parser stopped at a thousands
separator, and a second attempt reproduced it. The real figure is **~8,445**, and the
consequence flipped with it — the roles cost **+13%**, not the +42% the wrong number
implied. Recorded because the design was one step from being argued from it.

### REQ added at this stage

| REQ | What must be true | Verified by | Module |
|---|---|---|---|
| REQ-031 | `continuity.md` documents the **dynamic** loop mode beside the interval one: self-paced wake-ups, no fixed tick, and what one iteration means in it | the section exists and names both modes; a fixture asserts the schema's three `mode` values are each described | 1 |

**Gate verdict: PASS.** Every contract the design will lock is fetched or measured,
the family's own prior reading was re-checked rather than trusted, and the two
mis-measurements are recorded rather than quietly corrected.

---

## Stage 2 — brainstorm + decompose. Gate: `manual`, OPEN

### The design, in one idea

**The graph lives on disk. A script computes the frontier. The main thread reads the
frontier, never the graph.**

Everything else follows from that sentence, and it is the answer to *«правильно с
точки зрения контекста»*. A work graph for a real release is hundreds of nodes; a
model that reads it each iteration spends its context re-reading what it already
walked. A script that answers *«which nodes are runnable right now»* costs nothing
until it runs and returns three lines. `host-capabilities.md` says `scripts/` is the
one Claude-Code capability that **travels** — it lives inside the skill directory, so
every channel ships it.

So the loop's iteration is:

```
frontier = scripts/graph.py next        # small, deterministic, portable
dispatch each frontier node to its owner role
verifier closes the node                # reads the diff; returns a verdict
scripts/graph.py close <id> --verdict   # re-plans, re-prioritises, prints the goal
```

The model never holds the graph. It holds the frontier, the release goal, and the
last verdict — bounded, per iteration, regardless of programme size.

### Two rules decide agent vs doctrine, and the first is hard

**Rule 1 — a role that must talk to the operator cannot be an agent.** Not a
preference: the `Agent` tool's own contract states *"the agent's final report is not
shown to the user — relay what matters."* A subagent's output reaches the dispatcher,
never the human. Any role whose job includes asking a question **is main-thread work**
or it silently stops being able to do its job.

**Rule 2 — an agent earns its ~110 always-on tokens when the reading is voluminous and
the answer is small** (`host-capabilities.md`, and it says the inverse too: not when
the main thread needs the intermediate detail anyway).

| Role | Talks to operator? | Reads | Returns | Verdict |
|---|---|---|---|---|
| **manager** | yes — it asks for the go at a manual gate | the frontier (small) | which node next (small) | **doctrine** — small in, small out, and it *is* the orchestration |
| **business analyst** | **yes — a grill is a conversation** | the brief and its sources | questions, and the answers | **doctrine**, by rule 1. An agent cannot grill |
| **project** | yes | undefined | undefined | **deferred** — see below |
| **UX** | no — it reports | super-ux's whole chain: scenarios, flows, `/ux-lint` output | a verdict and its findings | **agent** |
| **UI** | no | the pack layer, the existing design, Figma state | mockup proposals, a verdict | **agent** |
| **decomposer** | no | one top-level plan item and its context | a task cut | **agent**, and **N in parallel** — the reason it is a role at all |
| **verifier** | no | the closed task's diff, its REQ rows, the gate output | done · not-done · blockers · re-plan | **agent** — the main thread needs the *verdict*, not the diff |
| **researcher** | no | prowl's tool output | findings | **agent** |
| **market analyst** | no | the same | findings | **agent** |
| **bug-analyst** | no | Sentry, production logs, database logs | findings, as backlog rows | **agent** |

**Seven agents (~770 tok, +9% on the family's ~8,445), three doctrine.**

### The `project` role is deferred, and that is a finding

It was named as *«does other things too»* and those things were never stated. A role
with no bounded job is a name, not a role — it would ship ~110 tokens a session to
hold a description nobody can act on. **Filed to the board rather than built**, and it
costs nothing to add once its job is written down.

### The graph's own shape

| Field | On a node | Why it exists |
|---|---|---|
| `id`, `title` | both | addressable, citable |
| `owner` | a role name | REQ-002 — a node with no owner fails the gate, because an unowned node is one nobody dispatches |
| `status` | `pending` · `running` · `done` · `blocked` · `parked` | `parked` is the verifier's *«blocker, continue around it»* |
| `blocked_by` | node ids | what makes the frontier computable at all |
| `serves` | a REQ id, or a clause of the release goal | REQ-012 — a node that serves neither is parked **with that as the reason** |
| `evidence` | filled at close | the ledger row's other half; empty means the node is not done |

Edges carry a payload and `planning.md`'s **fake-edge test** applies unchanged: an
arrow whose payload nobody can name is removed rather than drawn.

---

## The module map — every REQ in exactly one module

| M | Module | REQ | Ships |
|---|---|---|---|
| **1** | **Walking skeleton** — the graph artifact, its schema, `scripts/graph.py`, the verifier agent, and the dynamic loop mode | 001–012, 031 | the pipeline turns without a human between iterations |
| 2 | The role layer — six more agents, three doctrine roles, the degradation | 013–018 | breadth on a graph that already turns |
| 3 | The gates — understood-or-backlog, the funnel axis, super-ux as a dependency | 019–023 | quality on every run, agents or not |
| 4 | External intake — prowl research, the bug-analyst's collection system | 024–027 | evidence from outside the repository |
| 5 | The visualiser — separate repo, separate plugin, reads the ledger | 028 | a picture of a graph that by then exists |
| — | Cross-cutting: `R-005` independent reader, `R-008` enumerate the shapes | 029–030 | binds every module |

**Walking skeleton first, and it is module 1 by construction:** the verifier is what
closes an iteration, the graph is what it re-plans, and the loop is what carries it to
the next one. Modules 2–5 each plug into a graph that already turns; none of them can
be demonstrated before it does.

### Cross-module contracts

| Contract | Owner | Consumers |
|---|---|---|
| the graph schema and `scripts/graph.py`'s output shape | M1 | M2 dispatches by `owner`; M5 renders it |
| the verifier's four-field verdict | M1 | M3's gates read it; M5 shows it |
| the role-agent frontmatter convention | M2 | M4's three roles are built to it |
| the backlog row shape a finding becomes | M4 | the board, and M1's re-plan |

### Deferred to later modules, in the carry-over ledger

| Item | Why | Home |
|---|---|---|
| the `project` role | no bounded job stated | board row, not a module |
| per-role model tiers beyond the default | `model-tiering.md` already carries the mechanism | M2 |
| connecting a Sentry MCP | nothing here reports to Sentry; the role degrades | board row |

---

## Stage 2 gate — MANUAL, and it is open

What the operator is being asked to approve:

1. **The design**: graph on disk, frontier by script, main thread reads neither the
   graph nor the diffs. This is what makes it correct on context rather than merely
   parallel.
2. **Seven agents, not ten** — two by a hard constraint (a subagent cannot ask you
   anything), one deferred for having no stated job.
3. **The module map**, with module 1 as the walking skeleton.
4. **Arming the loop at this gate's close**, per `continuity.md` Part 1a — which
   needs `run.loop.command` recorded in `pipeline.json` first, and that is the change
   that answers the original complaint.

---

## Stage 2's close — the loop is NOT armed, and that is the decision

`continuity.md` Part 1a arms the recorded mode at this point. What is recorded in
this repository's own `pipeline.json` is:

```json
"loop": { "mode": "interval", "interval": "15m", "command": "/loop" }
```

Armed 2026-08-08 by operator instruction. **Arming it would pace the very build that
replaces it** — fifteen-minute gaps inserted into the module whose REQ-031 exists to
document the self-paced mode instead. So nothing is armed here, and the reason is
recorded rather than the step being skipped quietly. Module 1 changes the record
first (REQ-008), and the loop arms on the new mode at the close of the module that
earns it.

Second finding from the same file: `release` **already exists** here — `enabled`,
`trigger`, `steps`, `verify`. So REQ-010's `release.goal` is a **field on a block that
is already there**, not a new structure. Cheaper than the brief assumed.

---

## Stage 3 — spec, module 1. Gate: `manual`

### The three tracks, declined and recorded rather than silent

`super-ux` · `copywriting` · `sheleg-design` run on user-facing work. Module 1 has no
product interface: it is a schema, a script, an agent definition and doctrine, read by
an agent and by the operator in a terminal.

| Track | Verdict | Why |
|---|---|---|
| UX (`super-ux`) | **declined** | no product surface, no funnel, no user path. `ux-flows` owns how users move through a product; a frontier printer has no users |
| COPY (`copywriting`) | **declined** | the family's own routing block excludes developer READMEs, internal docs and CLI output for developers. This is all three |
| VISUAL (`sheleg-design`) | **declined** | module 1 has no visual layer. Module 5 does, and it runs the track then |

Recorded, per the stage-3 rule that a declined track is never silent.

### Contract 1 — the graph artifact

**Location:** `.task-pipeline/graph.json`. That directory is already this pipeline's
run-state home (`build.md` writes `.task-pipeline/run.md` there), so the graph joins
an existing convention rather than inventing one.

**Schema:** `graph.schema.json`, beside `pipeline.schema.json`, same style.

```json
{
  "goal": "<echoed from pipeline.json release.goal at creation>",
  "nodes": [
    { "id": "N-001", "title": "…", "owner": "decomposer",
      "status": "pending", "blocked_by": [], "serves": "REQ-004",
      "evidence": null }
  ],
  "edges": [ { "from": "N-001", "to": "N-002", "payload": "the task cut" } ]
}
```

**Invariants the schema and the script both enforce** — each one is a REQ:

| Invariant | REQ | Failure |
|---|---|---|
| every node has an `owner` that is a known role | 002 | a node nobody dispatches |
| every edge has a non-empty `payload` | 003 | `planning.md`'s fake edge, drawn anyway |
| every node `serves` a REQ id or a goal clause | 012 | work that serves neither, done silently |
| no cycles | — | a frontier that never empties |
| `status: done` requires non-null `evidence` | 006 | a node called done by assertion |

### Contract 2 — `scripts/graph.py`

Stdlib-only python, like every other script in this bundle, so it travels to every
channel. **Exit codes are the contract**, per standing instruction `R-004` — the next
command is conditional on them, never sequenced after them.

| Command | Prints | Exit |
|---|---|---|
| `next` | the frontier: `id · owner · title`, one per line, **and nothing else** | `0` runnable nodes exist · `3` graph complete · `4` every remaining node blocked |
| `close <id> --verdict <path>` | the re-planned frontier count and the goal line | `0` closed · `1` verdict malformed or evidence missing |
| `add --title --owner --serves [--blocked-by …]` | the new id | `0` · `1` invalid owner or unknown `serves` |
| `park <id> --reason <text>` | confirmation | `0` · `1` no reason given |
| `validate` | every violated invariant, one per line | `0` clean · `1` any violation |
| `goal` | the release goal, one line | `0` · `3` none recorded |

**`next` prints the frontier and nothing else** because that output is what enters the
model's context every iteration. Anything else printed there is paid for on every
turn of every loop.

### Contract 3 — the verifier's verdict

JSON, so `close` consumes it without the model transcribing it:

```json
{ "node": "N-007",
  "done":     ["what was asked and is now true"],
  "not_done": ["what was asked and is not"],
  "blockers": [{ "what": "…", "blocks": ["N-009"], "can_continue_around": true }],
  "replan":   { "possible": true, "add": [], "park": ["N-009"], "why": "…" },
  "evidence": ["the command and its output that proves each `done` row"] }
```

**All six keys required.** `done` without `evidence` is refused by `close` — REQ-006,
and the reason the field exists at all.

### Contract 4 — the loop, dynamic

`run.loop.mode: "dynamic"`, `interval` dropped (the schema already calls it meaningless
there). `command` stays: it is how *this* harness arms it, and it is project-recorded
rather than assumed.

- **arms** at the close of stage 2 when the queue holds more than one item (unchanged)
- **prints on arming**: the job id and the cancel command (unchanged)
- **each iteration prints**: the release goal, then the frontier — REQ-010
- **where nothing is recorded, nothing arms** — REQ-009, unchanged and re-asserted

### Contract 5 — `release.goal`

A string on the existing `release` block. `graph.py goal` reads it; every iteration
prints it; a node that `serves` neither it nor a REQ is parked with that as the
reason — REQ-012.

### What module 1 does NOT lock

The verifier ships as `agents/verifier.md` (REQ-005), and the **role-agent frontmatter
convention** is module 2's contract. Module 1 writes one agent to the shape the fetched
reference gives; module 2 generalises it across six more. Naming that boundary here is
what stops module 1 inventing a convention module 2 then has to change.

### Stage 3 gate — MANUAL

Five contracts locked, three tracks declined with reasons, and the boundary to module 2
named. What is being approved is the shape of the artifacts, not yet a line of code.

---

## Stage 4 — plan, module 1. Gate: `auto`

Seven tasks. Every module-1 REQ appears in **exactly one** `Implements:` line, and
their union is module 1's REQ set — the comparison this gate performs.

### T-1 — the graph schema
**Implements:** REQ-001
**Does:** `graph.schema.json` beside `pipeline.schema.json` — node shape (`id`,
`title`, `owner`, `status`, `blocked_by`, `serves`, `evidence`), edge shape
(`from`, `to`, `payload`), the `goal` echo.
**DoD:** an example graph validates; a node missing `owner` and an edge missing
`payload` are both rejected **by the schema alone**, before any script runs.

### T-2 — `graph.py validate`, and the invariants a schema cannot express
**Implements:** REQ-002, REQ-003
**Does:** the checks JSON Schema cannot state — `owner` is a **known role**, no
cycles, `status: done` implies non-null `evidence`, every `serves` resolves.
**DoD:** each invariant watched refusing its own planted violation; `validate` exits
`1` on any, `0` clean. Per `R-008`, the plan names the shapes each defect can take
before the fix is written: an unknown owner, a *misspelt* known owner, an owner that
was valid before a role was removed.

### T-3 — the walk and the mutation verbs
**Implements:** REQ-011, REQ-012
**Does:** `next`, `add`, `park`, `goal`. `next` prints the frontier **and nothing
else**. `add` is how a task run adds work mid-flight — the dynamic backlog. `park`
requires `--reason` and refuses without one.
**DoD:** a graph mutated mid-walk re-prioritises on the next `next`; a node serving
neither a REQ nor a goal clause is parked **carrying that as its reason**, and a
fixture reads the reason back.

### T-4 — the verifier agent
**Implements:** REQ-005, REQ-006
**Does:** `agents/verifier.md` to the fetched frontmatter contract, **discovered by
convention rather than declared**; the six-key verdict shape.
**DoD:** `claude plugin validate --strict` green; the agent resolves as
`task-pipeline:verifier`; a verdict missing any of the six keys is refused.

### T-5 — `close` consumes a verdict and re-plans
**Implements:** REQ-007
**Does:** `close <id> --verdict <path>`: refuse `done` without `evidence`, apply
`replan.add` / `replan.park`, print the new frontier count and the goal.
**DoD:** both branches fixtured — `replan.possible: true` advances the graph;
`false` stops and the printed reason is the verdict's own `why`.

### T-6 — the loop, dynamic, and the goal it prints
**Implements:** REQ-008, REQ-009, REQ-010
**Does:** `pipeline.json` → `run.loop.mode: dynamic`, `interval` dropped, `command`
kept; `release.goal` added to the block that already exists.
**DoD:** a config with `command` arms and prints the job id and the cancel command;
a config without arms nothing; every iteration prints the goal above the frontier.

### T-7 — the doctrine
**Implements:** REQ-004, REQ-031
**Does:** `references/work-graph.md` (new, reachable from `SKILL.md`); the stage-2
gate criterion naming the graph as the queue; `continuity.md`'s dynamic-mode section
beside the interval one.
**DoD:** `npm test` green — the reference is reachable, the stage table still matches
across its three compared surfaces, and a fixture asserts all three `mode` values are
described.

### The graph of the plan itself — every edge names its payload

| From | To | Payload |
|---|---|---|
| T-1 | T-2 | the schema `validate` validates against |
| T-1 | T-4 | the node shape the verdict's `node` field references |
| T-2 | T-3 | the invariants the mutation verbs must not break |
| T-3 | T-5 | the `close` verb `--verdict` extends |
| T-4 | T-5 | the six-key verdict JSON `close` consumes |
| T-3 | T-6 | the frontier print the iteration prints beneath the goal |
| T-3, T-5, T-6 | T-7 | the behaviour the doctrine documents |

`planning.md`'s fake-edge test applied: seven edges, seven payloads, none removed.

### Waves — what runs in parallel

| Wave | Tasks | Why together |
|---|---|---|
| 1 | **T-1** | everything reads the schema |
| 2 | **T-2 · T-4 · T-6** | three independent readers of the schema; T-6 touches only config |
| 3 | **T-3** | needs T-2's invariants |
| 4 | **T-5** | needs T-3's verb and T-4's verdict |
| 5 | **T-7** | documents what waves 1–4 built |

Five waves, seven tasks, maximum width three. `build.md`'s rule applies to wave 2:
a fanned-out group gets **one convergence check over all its diffs together** before
the first worktree lands, because a per-task review cannot see a contradiction that
exists only between two of them.

### Gate: the set comparison

| | |
|---|---|
| module 1's REQ in the brief | 001 002 003 004 005 006 007 008 009 010 011 012 031 — **13** |
| union of the seven `Implements:` | 001 · 002 003 · 011 012 · 005 006 · 007 · 008 009 010 · 004 031 — **13** |
| difference | **none, in either direction** |

**Gate verdict: PASS.**
