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
| REQ-005 | A **verifier** role exists as `agents/verifier.md`, declared in `plugin.json` | `claude plugin validate --strict` green; the agent resolves by name | 1 |
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
