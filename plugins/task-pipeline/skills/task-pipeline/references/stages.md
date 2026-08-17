# Stages — detail & gates

For each stage: what it does, what to invoke, artifacts, and the **GATE** that
must pass before advancing. Each gate is tagged with its **type** — `auto` (the
orchestrator verifies the check itself, pass/fail) or `manual` (wait for the
operator's explicit go). These stages (0 intake + 1→10) are the plugin's
**example** flow, encoded in `pipeline.example.json` against the universal contract
`pipeline.schema.json`; a host project replaces it with its own
stages/agents/types (see SKILL.md → *Bring your own skills*).

## The run checklist — printed, not remembered

Complex workflows lose steps silently. **The run says where it is**, at two boundaries
and only two — task start and iteration close ([`progress.md`](progress.md)):

```
task-pipeline vX.Y.Z · <topic> · module <id> «<name>» (N of M)
  0 ✓  1 ✓  2 ✓  3 ▶  4 ·  5 ·  6 ·  7 ·  8 ·  9 · 10 ·
  ███████░░░░░░░░░░░░░░░░░░░  gates 3/11 · now 3 Spec · manual
  board B-NNN · carry-over N rows · exposure N never · unlooked N
```

The rail's positions come from the project's own `pipeline.json`, never from the count
below — those eleven are this plugin's example flow. Each glyph is read from the
verdict its gate wrote to `.task-pipeline/run.md`, and from nothing else: a rail
written from memory is a summary that is confidently wrong exactly where it is trusted
at a glance.

The checklist below is what that rail summarises. This section said *"copy it, tick
it"* until 2026-08-10 — an instruction with no gate behind it, which is the same
failure it was written to prevent, one level up.

```
Pipeline progress
- [ ]  0  Intake — harvest + doc inventory + reconcile, grill, REQ table, brief locked
- [ ]  1  Docs study — every contract grounded on fetched docs, not recall
- [ ]  2  Brainstorm — design approved, UI verdict recorded, every REQ answered
- [ ]  3  Spec — committed, reviewed, every section covers: REQ-…
- [ ]  4  Plan — REQ set equality holds, no placeholders, groups share no files
- [ ]  5  Dev — tasks DONE, three verdicts each, suite green, branch integrated
- [ ]  6  Tests — full suite green, new checks probed both ways
- [ ]  7  Lint + deploy — clean, and the deploy authorization is specific
- [ ]  8  Post-deploy — clean boot, or an honest degradation report
- [ ]  9  Docs — matrix walked, registers written, docs gate green with ratchets printed
- [ ] 10  Acceptance — ladder walk first, every REQ with evidence, retro written last
```

Each line is a **gate**, not a task: an unchecked box means the gate did not pass,
never that the work was skipped quietly.

## Contents

- The run checklist — printed, not remembered
- 0 — Intake grill — MANDATORY
- 1 — Docs study
- 2 — Brainstorm + decompose
- 3 — Spec — with UX track for user-facing tasks
- 4 — Plan
- 5 — Dev
- 6 — Tests
- 7 — Lint + deploy
- 8 — Post-deploy
- 9 — Docs + wiki
- 10 — Acceptance
- The program loop — a platform, one brick at a time
- Cross-cutting — the Doc Loop
- Cross-cutting — the loop guard
- Cross-cutting — the audit

## 0 — Intake grill — MANDATORY
- **Freedom: medium** — the interview adapts to the answers; its two phases and their order do not ([`gates.md`](gates.md) → *Axis C*).
- **Stage 0 is not optional and not skippable.** There is no "small enough task"
  exemption, no "the request was already clear" exemption, no starting stage 1
  "while the operator thinks". The only sanctioned bypass is the
  entry-from-super-ux short-circuit below, and even that still requires a scope
  confirmation and a record of what was adopted vs skipped. A run that reaches
  stage 1 without a committed, operator-confirmed brief is a **failed run** —
  stop and go back.
- **Entry-from-super-ux short-circuit (check FIRST).** task-pipeline is often
  launched *from* super-ux — its `/ux` action menu offers "execute autonomously
  via the task-pipeline plugin" once the UX chain (and often a
  `docs/ux/plans/…` fix plan) is already built. Before grilling, detect that:
  if `docs/ux/` already holds a validated chain (foundation → flows → screens →
  scenarios) and/or a fresh fix plan, **do not re-run the grill or the stage-3
  UX track from scratch.** Instead: (1) run a quick check — `/ux-lint`
  (`docs/ux/lint.py`) green, chain present, plan (if any) readable; (2) confirm
  the scope with the operator in ONE line; (3) skip to the first stage that
  still has real work (usually stage 4 Plan if a UX fix plan already exists, or
  stage 3 Spec to formalize it). Record what was adopted vs skipped. If the
  check finds drift/gaps, fall back to the normal flow for the missing parts
  only.
- **What (normal entry):** the operator's one-line task is almost never enough to
  run autonomously. Before anything else, **grill the operator** to expand that
  one line into a complete, unambiguous brief — resolve every decision branch
  up front so stages 1→10 need no further human input beyond the manual gates.
  This is input expansion, not design: turn "make me feature X" into locked
  answers for scope, users, constraints, data, edge cases, done-criteria.
- **Phase 1 — harvest the knowledge sources FIRST**
  ([`knowledge-sources.md`](knowledge-sources.md)). Before the first question:
  query what the project already knows about this task — code, **the code graph**
  when one is built ([`knowledge-graph.md`](knowledge-graph.md): `graphify query` /
  `affected` / `god-nodes` answer *reach*, which is what grep cannot), `CLAUDE.md`,
  `CONTEXT.md`/ADRs, `docs/` + `docs/ux/`, past pipeline briefs and carry-over
  ledgers, **the retro's standing instructions and run stamps** (`<artifacts>/retro.md`,
  read **in full** — ten standing rows and ten stamps, both bounded **by a cap**, and they bind this
  run; stamp each instruction as it fires. Its *Recent log* is **queried** by the
  task's nouns, not read: uncapped narrative inside a binding source is what makes the
  capped part get skimmed, [`retrospective.md`](retrospective.md)), the **knowledge wiki** if one is
  installed
  ([obsidian-wiki](https://github.com/ar9av/obsidian-wiki) — recommended,
  never required), and any **other repo or hosted doc system the project names as
  its docs**. Write the **source ledger** into the brief (a row per source, or an
  explicit "none found"; **the graph's row carries its measured lag — commits and
  days behind `HEAD`, the signal that measured it, and `⚠ not trusted for reach
  until refreshed` on anything but `current`**
  ([`knowledge-graph.md`](knowledge-graph.md) → *Measure the lag*; a build date is
  the graph's own reply about itself, not a measurement of it). It is retrieval
  scoped by the task's own nouns, not a read of everything — and it is what makes
  phase 2's answers checkable instead of merely confident.
- **Phase 1b — the documentation inventory**
  ([`documentation.md`](documentation.md)). Four questions, answered before the
  interview and written to `docs/DOCMAP.md` (seeded from
  [`../templates/docmap.md`](../templates/docmap.md), **only when absent**): where
  do settled things live, what is each fact's single home, what does a change of
  type X oblige, and what proves it. A project with no answers gets them seeded —
  registers, the matrix and `scripts/check-docs.sh` — and the seeding is itself
  recorded as the register's first entry. **One decision home per project:** an
  existing `docs/adr/` *is* the register and is recorded as such, never duplicated.
  The gate is seeded so that it exits `0` on its own seeds; a project that starts
  red learns on day one that the gate is noise.
- **Phase 1b+ — offer the entry audit, once** ([`setup.md`](setup.md)). When
  `docs/DOCMAP.md` is absent or its regime line predates the project's last release,
  ask whether to audit the documentation that already exists **before** building on
  it. Record the answer — including a refusal — in the brief's autonomy sweep and
  never ask again. `audit.md`'s ladder runs at the *end* over the change; this runs
  at the *start* over what is already there.
- **Phase 1c — reconcile intent against as-built.** Git says how it *should* be;
  the run record says how it *turned out*. Read both for the area you are about to
  touch and resolve every divergence — the document is stale, the record is wrong,
  or they genuinely disagree and that is a decision. There is no fourth option, and
  starting on an unresolved divergence means building against a system that does
  not exist.
- **Phase 1d — the short-path triage: printed, proposed, never taken silently.** This
  pipeline's own boundary exempts a typo, a one-line fix and a mechanical rename — and
  nothing measured that until 2026-08-10, so the exemption depended on an agent
  remembering it while eleven stages and four manual gates stood in front of a
  one-paragraph edit. Three questions, each with something behind it:

  ```
  1. files the request names, resolved        git ls-files -- <paths>       -> N
  2. any of them a public contract            the version-synced surfaces,
                                              pipeline.schema.json, the
                                              command, the README           -> yes/no
  3. behaviour a user or a caller observes changes                          -> yes/no
  ```

  Few files, no contract, no observable change ⇒ **propose** the short path: stages 1,
  2, 3 and 4 marked `⊘` with the triage answer as the reason, and 5→10 running
  unchanged. **Propose, never take.** The answer goes in the brief's autonomy sweep and
  silence takes the full flow — the same floor deploy authorization uses. The glyph is
  what makes it safe: a skipped stage is printed on the rail **with its reason**
  ([`progress.md`](progress.md)), and a skip nobody can see is indistinguishable from a
  stage that was never entered.
- **How it runs: [`grill.md`](grill.md)** — the full doctrine, built into this
  skill (nothing to install). In short: one question per turn, a recommended
  answer with each, explore the codebase before asking, depth-first through the
  decision tree, contradictions reconciled on the spot; **every answer that touches
  a harvested source is checked against it** — the operator outranks any document,
  but only out loud, and the losing side is logged for the stage-9 doc update; plus
  **domain awareness**
  (challenge terms against `CONTEXT.md`, sharpen fuzzy language, stress-test with
  concrete scenarios, cross-reference the code, record ADRs for hard-to-reverse
  calls) and the **autonomy sweep** that pre-resolves every stage-1→10 blocker.
  Deploy authorization has a hard floor there: a standing go counts only when it
  names the target and the preconditions.
- **The run mode is settled here too** ([`continuity.md`](continuity.md)): does
  the run advance item-by-item with no check-in between items, and on what
  interval? Read `pipeline.json` → `run.loop` first — a recorded mode is the
  answer and is not re-asked; **absent, it is off**. It buys pacing, never
  authorization: no loop mode collapses a `manual` gate or an outward act. The
  same file carries the other half of pacing — the context budget, which fires
  only on a harness signal or the operator's word, never on an estimate.
- **UI early-detect:** one branch of the grill is always "does this touch a
  user-facing surface (web/mobile/CLI/TUI)?". If yes → surface **super-ux**
  now (use it if installed; otherwise give the install line — see SKILL.md
  *Prerequisites*); this arms the stage-3 UX track.
- **Artifact:** lock the resolved decisions into a **task brief** committed at
  `<artifacts>/specs/YYYY-MM-DD-<topic>-brief.md` (scope, users/UI verdict,
  constraints, assumptions, explicitly-deferred items, done-criteria) **plus the
  autonomy sweep's per-stage answers and the model decision**. Seed it from
  the skill's `templates/brief.md` skeleton — but only when absent, never
  overwrite an existing brief. Stages 2–4 build on this brief; stages 5–10 read
  its autonomy section instead of asking. Where the session produced them, also:
  an updated `CONTEXT.md` (terms written as they resolved) and any ADRs under
  `docs/adr/` — see `grill.md` → *Domain awareness*.
- **GATE (manual):** shared understanding reached — **the source ledger is written
  (every source consulted, or an explicit "none found")** and **its `Contradictions:`
  line is written under it** — the harvest is a fan-out that converges on one brief, and
  nothing else compares the sources *with each other*; `Contradictions: none` is the
  answer most runs give and writing it is the point
  ([`knowledge-sources.md`](knowledge-sources.md)), **where a code graph
  exists its row carries the measured lag and the signal it was measured with — a
  bare build date does not satisfy this, because it is the graph's own reply rather
  than a measurement of it** ([`knowledge-graph.md`](knowledge-graph.md) →
  *Measure the lag*), **the documentation
  inventory is answered into `docs/DOCMAP.md`** with its registers, single homes,
  a non-empty propagation matrix and the gate command, **the regime is recorded**,
  **intent and as-built are reconciled with every divergence resolved**, the retro's
  in-force sections are read in full and its archive queried, every detected branch has
  a recorded answer or an explicit deferral, **every answer that contradicted a
  harvested source has a recorded resolution** (which governs, and whether the doc
  is now stale), no open contradictions, **every
  autonomy-sweep row is answered or explicitly marked "stop and ask here"**, the
  **REQ table is written and every row names its check**, the carry-over ledger is
  seeded, **`.task-pipeline/run.md` exists and the header block has been printed**
  ([`progress.md`](progress.md)), the model decision is recorded, and the operator
  confirms the brief. Stop when a
  re-scan surfaces no new branches (don't grill past diminishing returns;
  reversible calls can be deferred with a note). Only then start stage 1.
- **The verification ledger is read.** `<artifacts>/verification.md` — the harvest
  quotes **how many rows sit at `never`**, because that is the project's standing
  exposure and stage 0 is where it is cheapest to look ([`verification.md`](verification.md)).
- **The run ledger is seeded and the header block is printed** — in that order, before
  the first grill question. `.task-pipeline/run.md` from
  [`../templates/run.md`](../templates/run.md) is the record **two** mechanisms already
  depended on and no run had ever written: [`loop-guard.md`](loop-guard.md) calls its
  own churn detection mechanical and reads the `touch:` lines, and
  [`progress.md`](progress.md) derives the rail and the iteration counter from the
  `stage:` and `iter:` lines. The header goes out before the interview because a run
  that announces its position only at the end announced it to nobody.
- **The board is read, or seeded.** `<artifacts>/backlog.md` ([`backlog.md`](backlog.md)) — its **open count is quoted in the brief**, measured by a command at the top of the run rather than inherited from the last run's report. Absent ⇒ seeded from the template and said so; an empty board and no board are the same thing to work on, and only one of them can be appended to.

## 1 — Docs study
- **Freedom: medium** — which sources to fetch is judgement; grounding contracts on fetched docs is not ([`gates.md`](gates.md) → *Axis C*).
- **What:** ground every external library / API / SDK the task touches on the
  *current* docs, before locking any contract.
- **Invoke:** the `context7` MCP — `context7:resolve-library-id` → `context7:query-docs`,
  scoped by topic or the `context7-docs` skill. Web-search fallback for libs context7
  can't resolve.
- **GATE (auto):** every contract the design will lock is grounded in fetched docs,
  not recall. Unresolvable libraries are flagged in the spec.

## 2 — Brainstorm + decompose
- **Freedom: high** — many designs are valid — this is the open field, and the only fixed thing is the gate ([`gates.md`](gates.md) → *Axis C*).
- **How it runs: [`brainstorm.md`](brainstorm.md)** — built into this skill. Read
  the brief first (stage 0 already answered scope/constraints/done-criteria), then
  explore the codebase, scope-check for decomposition, one question at a time, 2–3
  approaches with a recommendation, design presented in sections and approved
  section by section. **Hard gate:** no code, no scaffolding, no implementation
  skill before the operator approves the design — including on "obviously simple"
  tasks.
- **UI detection (mandatory check):** decide whether the task touches any
  user-facing surface (web, mobile, CLI, TUI — new feature, new screen/command,
  or a change to user-visible behavior). Record the verdict; it arms the UX
  track in stage 3.
- **Decomposition (platforms only): [`decomposition.md`](decomposition.md).** If
  the brief describes a platform rather than a change — several independent
  capabilities, several surfaces that could ship separately, REQs no single
  deliverable satisfies — cut it into **modules** before any spec is written, and
  commit the module map (`specs/<topic>-modules.md`): what each module delivers,
  the entities it owns, what it depends on, the contracts it exposes, its REQs and
  its status, in build order with the walking skeleton first. Single-module work
  records `single module: <name>` in the design and moves on — a skipped
  decomposition is a decision, never an omission.
- **Where the queue is a work graph, it is WRITTEN here**
  ([`work-graph.md`](work-graph.md)): `.task-pipeline/graph.json`, carrying the frozen REQ
  ids so `serves` resolves, one node per unit of work with its owner and what it touches,
  and an edge per dependency **naming what it hands over**. Then
  `python3 scripts/graph.py validate` — a graph that does not validate is not a queue, and
  `next` refuses to walk one. The reason to prefer it over a prose plan is measured, not
  aesthetic: a 400-node graph and a 4-node graph produce the same 27-byte frontier, so the
  cost of knowing what is next does not grow with the programme.
- **The queue exists here, so the loop arms here** ([`continuity.md`](continuity.md) →
  *Part 1a*). Where `run.loop.arm` is `after-decomposition` and the map holds more than
  one module, arm the mode at the close of this stage and print one line: the mode, and
  either the job id and its cancel command (`interval`) or the delay chosen and why
  (`dynamic`). Arming collapses no gate and authorizes no outward act; it decides only
  that the run does not stop to ask *"shall I take the next one?"*. Single-module work
  arms nothing and says so — a loop with one item is a timer.
- **GATE (manual):** the user approves the design, the UI verdict is recorded, **the
  queue is an artifact rather than a recollection** — where it is a work graph,
  `graph.py validate` exits 0 and `graph.py coverage` names any requirement no node serves,
  **every REQ is answered by the design** — a requirement the design doesn't
  address is either covered now or explicitly dropped by the operator, with the
  drop recorded in the carry-over ledger — **and, for a platform, the module map is
  approved**: brick criteria met or excepted in writing, dependency graph acyclic,
  build order topological, every REQ mapped to exactly one module, cross-module
  contracts named with their owner — **and the loop's arming state is printed**:
  armed with its queue and pacing, or not armed with the reason.

## 3 — Spec — with UX track for user-facing tasks
- **Freedom: medium** — what the contract says is judgement; which contracts must be locked is a list ([`gates.md`](gates.md) → *Axis C*).
- **How it runs: [`spec.md`](spec.md)** — built into this skill: the UX-track order,
  what the spec must lock (types, schemas, signatures, file layout, the **Global
  Constraints** block stages 4–5 depend on), the self-review pass and the operator
  review gate.
- **UX track (runs FIRST when stage 2 flagged UI; skip entirely otherwise).**
  Requires the **super-ux** skills. If missing on a UI task → give the install
  line and stop (see SKILL.md *Prerequisites*: `/plugin marketplace add
  ssheleg/super-ux` → `/plugin install super-ux@super-ux`, or `npx skills add
  ssheleg/super-ux`). super-ux builds a traced chain — walk it top-down (see its
  `system-map.md`):
  0. **Destination first, when Figma is on.** The brief already names the team/org
     and the file; `docs/ux/foundation.md` → *Design tooling* is the canonical
     record. Confirm it **resolves** before drawing. **Never create a file while a
     recorded one resolves; if it doesn't resolve, stop and ask — never create a
     replacement** (that is the duplicate, and it hides a permissions problem).
     A creation happens at most once, in the named team, and its URL is written to
     the canonical record before the first frame.
  1. `/ux` (the only super-ux entry) — reports which `docs/ux/` layers exist,
     repairs the skeleton, records the Figma on/off choice, recommends the next
     action. Never make the operator pick skills.
  2. `ux-foundation` → `docs/ux/foundation.md` — the **WHY**: personas, Jobs to
     Be Done, **customer journey maps (CJM)**, user stories (Given/When/Then).
  3. `ux-flows` → `docs/ux/flows.md` + `docs/ux/screens.md` — the **HOW + UI
     map**: task analysis, user-flow diagrams (branches, error paths), every
     screen + state with wireframe and (Figma on) a Figma frame link.
  4. `ux-scenarios` → `docs/ux/scenarios.md` — the **WHAT** (source of truth for
     behavior): scenarios validated against the scenario-format contract super-ux
     itself ships (`scenario-format.md` — read its current version there, never
     pin one here) — IDs, statuses, `Traces:` to stories/journey stages/flows,
     edge/error states enumerated.
  5. **Run the super-ux linter** (`/ux-lint` or `python3 docs/ux/lint.py`) — it
     must pass: no drift, no orphans, no broken traces or stale Figma links.
  These skills are **idempotent** — reuse and extend existing `docs/ux/` layers,
  never rebuild from scratch. If the chain already exists and is validated (e.g.
  the task entered from super-ux), just verify (linter green) and embed it into
  the spec; only build the parts that are missing.
- **COPY track — how it sounds.** Every string a product's user will read is written
  through super-ux's `copywriting`, against the brand pack (`docs/brand/voice.md`,
  `terminology.md`, `facts.md`). No pack ⇒ `/brand-init` **before** the first string,
  not after: a voice reverse-engineered from copy already written is a description of
  what happened, not a decision. In scope: interface strings, errors, empty states,
  the landing, pricing, the user-facing changelog. **Out of scope, and saying so is
  what keeps the track honest:** commit messages, PR descriptions, code comments, a
  developer README, internal docs. Running a brand pack over a line in a contributors'
  changelog is the fastest way to teach an agent to route around the track.
- **VISUAL track — how it looks.** Where the task has a visual surface, the visual
  layer goes through `sheleg-design` ([`companion-skills.md`](companion-skills.md)):
  tokens and themes, typography and rhythm, motion and how it degrades to rest, the
  boundary with Figma (tokens as variables, never raw values carried across). Not
  through it: a purely structural change — what sits where is the UX track's — text,
  a backend, an internal script.
- **Each track's refusal is a sentence, never a silence.** *"Без дизайна" / "as is"*
  ends the visual track; *"без бренда" / "draft"* ends the copy track. Either one is
  the operator's to make and costs nothing — but it is **recorded in the brief and
  said out loud in the close-out**, because a track skipped silently and a track that
  ran are the same thing in a transcript. This is the `⊘` rule one layer up: a skip
  nobody can see is indistinguishable from work that happened.
- **Three tracks, three questions, and they do not substitute for each other.** super-ux
  decides what the interface must **do**; `copywriting` how it **sounds**;
  `sheleg-design` how it **looks**. Until 2026-08-10 this stage named only the first,
  so a run designed a flow, then wrote its strings by taste and picked its values at the
  keyboard — and every gate in the pipeline reported green over both.
- **Two of the three are a parallel layer, and the third is their only real dependency.**
  COPY and VISUAL both consume the UX track's scenarios; **neither consumes the other**.
  Copy is written against the brand pack and the scenarios, not against tokens; the visual
  is built from the frame and the style pack, not from strings. Writing them in a line —
  which this file did until 2026-08-15 — teaches a run to wait for a result that never
  arrives. The order is `UX → { COPY ∥ VISUAL }`, and the only thing crossing each of
  those two arrows is **the scenario set**.
- **Their convergence needs a check, and it has a real contradiction to catch.** Both land
  on the same screen, so the failure is not that one is wrong: it is that each is right
  alone and they disagree together. Before the spec is committed, compare the two outputs
  and record the answer:
  1. **A string the layout has no room for** — a label, an error or an empty state longer
     than the frame's element, at the frame's own width.
  2. **A state one track has and the other does not** — copy for an empty state the design
     never drew, or a loading state drawn with no string.
  3. **Two names for one thing** — the design system's component name against the
     terminology file's noun, where a user reads both.
  4. **A tone the visual contradicts** — a calm, plain register on a screen whose motion
     and colour say urgency.
  `Tracks converge: clean` is the answer most runs write, and writing it is the point —
  a check whose silence is indistinguishable from not having run is not evidence. This is
  the same rule the harvest applies at stage 0 and the build applies to a fanned-out group
  at stage 5 ([`build.md`](build.md) §4.2a); one shape, three places.
- **Spec:** write the approved design to
  `<artifacts>/specs/YYYY-MM-DD-<topic>-design.md` and commit it. Lock all
  shared contracts (types, schemas, signatures, file layout). For UI tasks the
  spec **embeds the UX layer**: links the validated scenario IDs, the flows and
  `SCR-` screens, the CJM stages the feature serves, and the UX
  patterns/principles from super-ux that apply (`best-practices.md`,
  `ux-design-principles.md`, `component-guidelines.md`).
- **GATE (manual):** the **`## Self-review` section written and committed with
  computed values** — every check the spec names resolving or marked `review`, the
  brief's decisions and stage 2's rejected options read back with no unresolved
  contradiction, and the cost delta printed; spec committed **and** user-reviewed; **every section carries
  `covers: REQ-…` and every REQ appears in at least one section**; for UI tasks
  additionally: the super-ux chain (foundation → flows → screens → scenarios) is
  designed, validated and approved; scenarios validated in `docs/ux/scenarios.md`;
  the linter passes; every user-facing spec requirement traces to a scenario ID
  (or an explicit v1-mode/tiny-project waiver by the operator). **With Figma on:
  the canonical record names one file, and every `screens.md` frame link carries
  that same `:fileKey`** — a string match, not a judgement; a differing key means
  the run drew in a second file nobody will open. **Every user-facing string went
  through the COPY track or the refusal is recorded**, and **the visual layer went
  through the VISUAL track or the refusal is recorded** — a recorded refusal passes
  this gate and an unmentioned one does not, which is the only difference that matters.
  **Where both tracks ran, their convergence check is recorded** — findings with the
  ruling, or `Tracks converge: clean`; a screen where each track is right alone and they
  disagree together is the defect neither track's own review can see.
  No plan (stage 4)
  starts before this — the chain comes BEFORE interface.

## 4 — Plan
- **Freedom: low** — the task format is prescribed and the REQ set-comparison is mechanical ([`gates.md`](gates.md) → *Axis C*).
- **How it runs: [`planning.md`](planning.md)** — built into this skill →
  `<artifacts>/plans/YYYY-MM-DD-<topic>.md` (same slug as the brief and the
  spec). Zero-context tasks, exact
  paths, complete code in every step, TDD steps with expected output, DoD each,
  dependency graph + parallel groups, non-overlapping file ownership, and the
  Global Constraints block copied verbatim from the spec.
- **GATE (auto):** the **`## Self-review` section written with computed values**,
  every command, path and file a DoD names resolving; **set equality — the REQ ids in the brief equal the union of
  `Implements:` across plan tasks.** A non-empty difference fails the gate and is
  reported as the explicit list of dropped requirements; this is the seam where
  scope leaks silently, so the check is mechanical, not a judgement call. Plus:
  every spec requirement maps to a task; no placeholders; names and
  types consistent across tasks; every task carries a verifiable DoD; parallel-group
  tasks share no files **or other mutable target**; **every edge in the *Execution
  order* table carries a non-empty `Carries` cell and the self-review's `Edges:`
  line is computed** — an arrow whose payload nobody can name is a fake edge and
  the wait behind it is free to give away ([`planning.md`](planning.md)).
  For UI tasks: every task building user-facing behavior
  names the scenario ID(s) and `SCR-` screen(s) it implements, and its DoD
  includes satisfying them **and** updating the affected super-ux layers in the
  same change (super-ux *same-change* rule).

## 5 — Dev
- **Freedom: low** — TDD order, worktree isolation and 'a subagent never writes the register' are the narrow bridge ([`gates.md`](gates.md) → *Axis C*).
- **How it runs: [`build.md`](build.md)** — built into this skill: isolate the
  workspace (native worktree tool first, git fallback, baseline tests), keep a
  ledger under `.task-pipeline/build/<plan>/` so a compacted context can resume,
  then one fresh implementer subagent per task with a file-based brief and report,
  a review after every task ([`review.md`](review.md)), and a five-round fix loop
  with an explicit breaker. TDD per task ([`tdd.md`](tdd.md)): failing test →
  watch it fail → minimal impl → watch it pass → commit. Pin subagents to the
  run's confirmed model (`model-tiering.md`). The plan's parallel groups fan out
  **only when all three hold** — the tasks share no `depends:`, their file ownership
  is exclusive per the plan, and each implementer gets its own worktree; otherwise
  sequential. A group that did fan out gets **one convergence check over all its
  reports and diffs together, before the first worktree is integrated**
  ([`build.md`](build.md) §4.2a) — a per-task review reads one diff and cannot see a
  contradiction that exists only between two of them.
- **Web front end? The task's own surface is checked in a browser, not in the diff.**
  Where a browser channel is connected — `playwright` **or** `chrome-devtools`, either
  one, whichever answers first (**how**: [`browser.md`](browser.md); which:
  [`companion-skills.md`](companion-skills.md)): after a
  task that changes a rendered surface, load it, take a snapshot and read the
  console and the network log **before the task is marked DONE** — a component can be
  correct and land under a fixed header, and a review of the diff cannot see that.
  **What the look finds is fixed in this task, or parked with the ruling the GATE below
  requires — never parked silently** — a browser finding filed without a ruling is the
  diff-review verdict wearing a screenshot; the look was worth taking only if it can
  still change the code or is on record as deliberately not doing so. Absent, say the surface was verified by reading
  the diff and treat it as the weaker claim it is. Stage 6 repeats this over the whole tree; this one catches it while the
  implementer that wrote it is still dispatched. The matrix pointed this companion at
  stages 5–6 from the day it was added and **this stage had never named it** — found by
  the guard comparing the two, not by a reader.
- **Integration closes the stage:** sync with the base branch, re-run the full suite
  on the result, land it the project's way (merge, or a PR — outward, so it needs a
  go), remove the worktree. Stages 7–9 act on the integrated result, so a branch the
  operator chose to leave unmerged is recorded as such.
- **GATE (auto):** **the hygiene gate green in diff mode after every task**
  (`references/build.md`) — six checks over what that task changed, no floor, and a
  finding fixed in-task or carried over with a reason; all plan tasks DONE (three review verdicts per task: spec
  compliance, **REQ satisfied**, code quality); **every group that fanned out ran its
  convergence check before its first worktree was integrated, and logged a line either
  way** ([`build.md`](build.md) §4.2a); every finding fixed or parked with a
  ruling; **every parked finding and implementer concern harvested into the
  carry-over ledger** — nothing stays only in the scratch workspace, which is
  deleted; no task left BLOCKED; full test suite green; branch integrated per the brief's policy (or the operator's
  "leave it" recorded).

## 6 — Tests
- **Freedom: low** — green means the full suite, and no skip smuggles a red one past ([`gates.md`](gates.md) → *Axis C*).
- **What:** consolidate test coverage for the change: confirm new functionality
  has tests (written test-first in stage 5), update/repair existing tests the
  change touched, and add edge-case + failure-path tests per DoD.
- **Invoke:** the host test runner (see `conventions.md` → *Lint + test*); the
  built-in [`tdd.md`](tdd.md) cycle for any uncovered gap — failing test first,
  same as stage 5.
- **GATE (auto):** **the hygiene gate green over the whole tree**, its six counts
  printed beside their floors; the **full** suite is green (not just the new tests); new/changed code
  is covered; no `skip`/`xfail` smuggling a red suite past the gate. Never advance
  to deploy on a red or partial run. **The carry-over count is printed beside this
  verdict** — a ratchet nobody prints is a TODO with a better name
  ([`audit.md`](audit.md)) — **and so are the disclosures**, `abstained` and
  `unlooked` ([`gates.md`](gates.md) → *Disclosures*): what the run declined to claim,
  and what a check never looked at. Neither has a floor and neither may be targeted; a
  target on an abstention count is an instruction to guess.
- **Web front end? Then the surface is checked in a browser, not in the diff.**
  A passing suite proves the code does what its assertions say. It does not prove the
  page rendered — a component can be correct and land under a fixed header, a request
  can 404 while every unit test mocks it, and a console error costs nothing at test
  time. Where a browser channel is connected — `playwright` **or** `chrome-devtools`,
  either one ([`browser.md`](browser.md) is the four commands this sentence means;
  [`companion-skills.md`](companion-skills.md) is which channel):
  load the surface, take a snapshot, and read **the console and the network log**
  before calling it green. Absent, say the surface was verified **by reading the
  diff** — that is a weaker claim and the close-out records it as one, rather than
  letting "tests pass" stand in for "it renders". This is the `L6→L7` seam of
  [`audit.md`](audit.md)'s ladder: *is there an executed observable a user reaches?*
- **A browser test suite does not discharge the look, and does not become it.** A
  project whose CI runs `playwright test` has an *asserted* browser — it proves what
  someone thought to assert, on the paths someone thought to write. It cannot report
  the console error nobody asserted on, the bundle that 404s past a route nobody
  visits, or the element that moved four pixels under a header. So a green spec suite
  counts where every other test counts, inside **the suite half of the GATE above**;
  the look stays what it already is here — **recommended, never a gate**, and reported
  in the words the gate gives it. What the pair buys is that they fail differently: a
  run that answers *the surface was checked* by pointing at its spec suite has answered
  a different question. Where the suite is the thing that changed, the look is what
  proves it runs against a page that renders.
- **What the look finds is fixed here.** A rendering defect found at stage 6 is a
  stage-6 finding: fix it, look again, then call the stage green. Filing it to the
  board and advancing is how a run reports *checked in a browser* for a page it has
  seen to be broken — so if it does leave unfixed, the reason is on record and the
  close-out carries it, exactly as a parked finding does.

## 7 — Lint + deploy
- **Freedom: low** — outward and irreversible — the authorization floor is exact or the stage stops ([`gates.md`](gates.md) → *Axis C*).
- Read host conventions (`conventions.md`): run the linter; fix failures. The suite
  is already green from stage 6 — re-run it if code changed since. For UI projects,
  the **super-ux linter** (`python3 docs/ux/lint.py` / `/ux-lint`) is part of lint —
  it must pass too (no UX drift merges). Then deploy per the project's convention;
  if the project defines release automation (`pipeline.json` → `release`, toggle
  on), that is what "deploy" runs here. **No runbook, or one too thin to act on?
  Write it first** ([`deploy-targets.md`](deploy-targets.md)) — a deploy performed
  from inference about the project is one nobody can repeat or roll back, and the
  operator is standing at this gate anyway. That reference also carries the CLI
  verbs per target for when the runbook names a platform you have to recall.
- **GATE (manual):** lint clean (host linter **and**, for UI projects, the super-ux
  linter) **and** suite green **before** deploy, **and no REQ is still `open`** — a
  `partial` ships only with the operator's explicit acceptance. A gap is cheapest to
  close before it ships, and the operator is already present at this gate. **The
  carry-over count is printed beside this verdict.** Deploy is outward → explicit
  operator go. Respect deploy-from-main rules if the project mandates them. **Before
  tagging, the CI verdict for what was just pushed is READ, not assumed**
  ([`conventions.md`](conventions.md) → *The CI verdict*) — a tag on a commit whose
  run nobody read is how a red `main` ships.
- **The independent reader is dispatched by this stage, and read by its output**
  ([`review.md`](review.md) → *The independent reader*). On any change that adds or
  widens a check, the run dispatches a reader — a subagent it can watch, a bot whose
  **verdict** it then reads, or a person — and records exactly one of three states
  beside the verdict: `reader: N findings`, `reader: none found`, or `reader: NO READER
  — <why>`. The third is printed, never omitted; a requested reader and a reading are
  different facts that look identical afterwards. Four pull requests of check work once
  merged on a bot's `skipping` with nobody noticing, which is why this is a stage rather
  than a hope.
- **The review loop that lives here has a cap, and the cap is a measurement**
  ([`loop-guard.md`](loop-guard.md) → *The review loop*). **3 rounds** per artifact by
  default (`pipeline.json` → `run.review.maxRounds`); at the cap the run stops reviewing
  and prints new-versus-self-inflicted per round, and either the numbers end it or the
  operator continues it out loud. This stage's loop was capped by nothing until
  2026-08-10 and ran ten rounds twice in one programme, against a stated ceiling of two
  re-entries per stage — the ceiling simply did not name a review round. Every finding
  left open at the cap leaves as a board row with its evidence, never as a shrug.

## 8 — Post-deploy
- **Freedom: medium** — where the logs live varies; 'clean boot or an honest degradation report' does not ([`gates.md`](gates.md) → *Axis C*).
- Tail deploy logs / health-check per conventions. Confirm clean boot, no error
  spike, live subsystems healthy. **All three of the verification trio, not one of
  them** ([`deploy-targets.md`](deploy-targets.md) → *The verification trio*):
  deployment/process state, runtime logs, and a health-check request from outside.
  Where deploy happens in CI, verify the **deploy** job and not only the build —
  a green build beside a skipped deploy is the commonest way a run reports success
  while nothing shipped.
- **A deployed web target is opened, not curled.** A `200` proves the server
  answered; it says nothing about whether the page rendered, whether a bundle 404'd,
  or whether the console filled with errors on load — all three ship green past a
  health check. Where a browser channel is connected — `playwright` **or**
  `chrome-devtools`, either one ([`browser.md`](browser.md)) — load the deployed URL and read
  the console and the network log; quote what you read, not that you looked
  ([`companion-skills.md`](companion-skills.md)). Absent → say the check was an HTTP
  response only, which is the honest name for it.
- **Read the CI verdict for the deploy's own commit** ([`conventions.md`](conventions.md)
  → *The CI verdict*): the run's conclusion quoted, the **failing step's log quoted**
  on anything but `success`, and one of the three states stated — including **`no run
  found`**, out loud, because a project without CI is a legitimate state and not a
  green one.
- **GATE (auto):** clean boot confirmed, or an **honest degradation report** with next
  steps — never silent success. **The CI verdict is one of the reported facts, with
  its run id** — "CI is green" written without a command behind it prints the same
  whether it looked or not ([`gates.md`](gates.md) → *False success*).
- **Write the verification row.** One line per REQ this run shipped, into
  `<artifacts>/verification.md` ([`verification.md`](verification.md)) — the run,
  the tag or commit it went out in, what the gate said, and `Human: never` unless the
  operator confirmed during the run. The verification above already happened; this is
  the only step that makes it answerable **later**, and `never` is a fact rather than a
  failure — the count has no floor and may never be given a target.

## 9 — Docs + wiki
- **Freedom: low** — the matrix walk and the gate are mechanical; what a doc says is not this stage's call ([`gates.md`](gates.md) → *Axis C*).
- **The propagation sweep runs first** ([`documentation.md`](documentation.md)).
  The ledger below names the documents you **read**; the matrix in `docs/DOCMAP.md`
  names the documents you **owe**. They are not the same list, and the gap between
  them is where documentation rots — the document nobody read is exactly the
  document nobody updated. Walk the matrix row for **every** change type this run
  produced. Every settled thing gets an id in the register, every answered question
  is flipped to `Resolved→<id>`, and every document named in a
  `Consequences / affects:` line cites its decision.
- **Then run the documentation gate** (`bash scripts/check-docs.sh`, or whatever
  `docs/DOCMAP.md` → *Gates* names) and print its **ratchet counts** beside the
  verdict, so "green" reads as *"green, and here is exactly what was not looked
  at"* ([`gates.md`](gates.md)). A check that skipped says so.
- **The stage-0 source ledger is the work list** ([`knowledge-sources.md`](knowledge-sources.md)
  → *Close the loop*): every source the harvest read gets updated if this run
  changed or disproved it. What was worth reading at stage 0 and is wrong now is
  the next run's false premise.
- Update host module docs / runbooks per the project's self-update rules, in the
  **same change**. For UI tasks, confirm the super-ux layers were updated in this
  change and the linter is green (super-ux *same-change* + *no-drift* rules).
- **Sync the knowledge wiki** — `wiki-update` when
  [obsidian-wiki](https://github.com/ar9av/obsidian-wiki) is installed (detect:
  `~/.obsidian-wiki/config`, or the skill resolves). Not installed → recommend it
  once with its install line and continue; a missing wiki never blocks the gate.
  Distil the knowledge (decisions, seams, why), not a diff summary.
- **Refresh the code graph** — `/graphify . --update` when one exists
  ([`knowledge-graph.md`](knowledge-graph.md)). The close-out has **three**
  artifacts, not two: docs, wiki, graph. The graph is the source the *next* run's
  harvest queries first, so a stale one is a false premise carrying the authority of
  a machine — a wrong doc gets argued with, a wrong graph gets believed. Incremental
  and model-free for code; a run that deleted code legitimately rebuilds smaller
  (`--force`).
- **Then check the graph against the docs** — the cheap half of the divergence sweep
  (`graphify god-nodes`; any doc naming a module the graph no longer has). A hub no
  doc names, or an edge the docs deny, is either a leak in the code or a lie in the
  docs; a doc naming a node that no longer exists is a stale ledger row found
  mechanically. Doc-side findings are fixed here; **absences go to stage 10's ladder
  walk as REQ rows** ([`audit.md`](audit.md)).
- **Docs living in another repository** are outward: propose the edit, get an
  explicit go, then open a PR there. No go → the exact edit goes in the carry-over
  ledger.
- **GATE (auto):** **the hygiene gate green**, counts printed; **the propagation matrix walked for every change type this run
  produced**, with every settled thing recorded under an id and every answered
  question resolved; **the documentation gate green, its ratchet counts printed and
  any skip stated** — this is what replaced the unfalsifiable *"docs in sync with
  code"*, which named no artefact and no command; every stale row in the source
  ledger either updated or carried over with its edit; the **as-built record
  written and reconciled**; UI: super-ux layers current + linter green; wiki synced
  (or absent and recommended once); **the code graph
  refreshed where one exists, or the reason it wasn't written into the carry-over
  ledger** (absent and recommended once is fine); dangling links fixed; **the CI
  verdict read for this stage's own push** ([`conventions.md`](conventions.md) →
  *The CI verdict*) — this stage pushes like any other and is the one that habitually
  ends a run, so an unread red here is a red `main` nobody is coming back to; **the
  carry-over count printed beside this verdict**.

## 10 — Acceptance
- **Freedom: medium** — the walk and the evidence rule are fixed; whether it is what was asked for is the operator's ([`gates.md`](gates.md) → *Axis C*).
- **What:** the closing stage — go back to the brief and account for **every**
  requirement. Doctrine: [`acceptance.md`](acceptance.md).
- **Every REQ this run shipped has a verification row, and every row names a REQ some
  brief carries.** Both directions: a shipped feature that entered no ledger and a
  ledger row about nothing are different failures ([`verification.md`](verification.md)).
- **The ledger's open rows are resolved onto the board.** Every carry-over row still
  `open` leaves with a `B-NNN` id on `<artifacts>/backlog.md`, and the ledger row
  is updated to name it ([`backlog.md`](backlog.md)). Both directions, because they are
  different failures: a ledger row pointing at an id nobody issued, and a board row
  traceable to nothing. Measured before this was built: across the ledgers in
  this repository, **twenty-four rows sat `open` with no home at all** — deferred out
  loud and filed nowhere. The first count said sixteen across six ledgers; it read the
  status column by position and was wrong wherever a ledger carried two of them. Then the board's priority is re-derived, because `age` moved while the
  run was happening. Every earlier gate asks
  "is this artifact good?"; none asks "does this still contain everything that was
  asked for?" The loss happens on the seams between stages, and this is where it
  surfaces.
- **Runs last**, after docs and wiki — those are deliverables too, and a REQ may
  name them.
- **The ladder walk runs FIRST** ([`audit.md`](audit.md)). The REQ table can only
  find what was named and lost; it cannot find what was never named, because a
  comparison needs two sides and an absence has one. So before the table: walk each
  REQ bottom-up through its rungs (decision → spec section → contract **and its
  failure behavior** → task → change → executed test → surface/docs), check the
  seam at each step, and order the findings **by seam, not by file**. On UI work
  designed visually, the frame is a **second, parallel statement of the same
  surface**: read it against the spec section that covers its `SCR-` id and against
  what shipped. The super-ux linter proves a frame link exists, is named right and
  is not stale — it cannot read the picture, so a frame promising a limit, a meter
  or a tier nobody built passes every lint there is. An absence
  becomes a **new REQ row with its check** and *then* the table is written;
  appending after the table is how acceptance goes green over a gap. Findings that
  belong to a lower layer go back to that layer (spec → stage 3, plan → stage 4).
  Record the pass's two counts — new findings, and findings caused by this run's
  own fixes — so the next pass can tell whether the axis is exhausted.
- **How it runs:** built in. Read the brief's REQ table, the carry-over ledger in
  full, the plan's task statuses, git log, the final suite output, stage-8 notes and
  stage-9 doc changes (plus `docs/ux/scenarios.md` + `/ux-lint` for UI tasks). Write
  `<artifacts>/specs/YYYY-MM-DD-<topic>-acceptance.md` — one row per REQ,
  status `verified` / `partial` / `deferred` / `dropped`, each with **evidence** (a
  passing test name, `file:line`, a command and its output, or a scenario ID).
  "Done" without evidence is not done: downgrade to `partial` and say so rather
  than upgrading the claim.
- Then ask the operator the closing question out loud, list in hand: *here's what
  you asked for, here's what shipped, here's what's deferred and where it lives —
  what's missing?* Ask it even when the table is green; the operator holds context
  the brief never captured, and this is the cheapest moment in the run to hear it.
- **Several repositories: a submodule is finished when its parent says so.** A
  parent records each submodule as a **pointer to one commit**, and moving the
  submodule does not move the pointer — so the work is committed, pushed, CI green
  and done in its own roadmap, while a clone of the parent still gets the commit
  before it. Neither repo looks wrong alone; the disagreement lives between them,
  which is why it survives every check that runs inside one. Before closing, this
  reports nothing **for the parent as well as every submodule**:
  `git submodule status` (no line starting `+`), plus `git -C <repo> status
  --porcelain` and `git -C <repo> log @{u}..HEAD --oneline` per repo. With
  [agent-sync](https://github.com/ssheleg/agent-sync) installed,
  `/agent-sync finish` runs exactly that. The fix is two commands and the second is
  the forgotten one: `git -C <submodule> push`, then
  `git add <submodule> && git commit`.
- **The retrospective is the run's last act** ([`retrospective.md`](retrospective.md)),
  written to `<artifacts>/retro.md` — one file per project, not per run. The
  pipeline's gates are good at *this* run and blind across runs: the same class of
  failure can be caught, fixed and forgotten five times and nothing in the flow
  notices it is the same one. So, in this order: **stamp the run first** (one line,
  with its commit — and the only thing that makes the next step computable), **then
  prune** (every standing instruction against its three retirement triggers — it
  became a check, its surface is gone, it hasn't fired in five run stamps or in sixty days — and the
  list held to its cap of ten, every deletion logged **in the archive, with the
  commit that retired it**), then **write an entry only if
  the run diverged** (symptom · the stage it surfaced at · the stage that *owned* it
  · root cause · fix, mechanical before instruction before expiring note · the check
  that catches it next time). Every run stamps and prunes; a retro left empty after
  a messy run is the failure the file exists to stop. Stage 0 reads the standing
  instructions in full next time, which is why the cap is not negotiable.
- **GATE (manual):** the ladder walk ran and its absences became REQ rows before
  the table was written; **the hand-back is written** — the request quoted as it was
  GIVEN, where the run stands against it, what was solved with its evidence, what
  surfaced that nobody asked for, every decision still waiting **asked here with
  options rather than listed**, and the ambiguity count computed from the four
  registers with its ids ([`progress.md`](progress.md) → *The hand-back*) — a run
  that cannot say what happened has not finished, it has stopped; **the environment is
  given back** — all eight classes enumerated, everything this run started ended and
  verified by re-enumerating rather than by the teardown's reply, an earlier run of
  this project ended only when **provably spent**, an item this project does not own
  reported rather than ended, and the result written as a `holds:` line
  ([`residue.md`](residue.md)); **every disclosure printed beside the verdict** — `abstained` (what the run declined
  to claim) and `unlooked` (what a check never looked at), neither a ratchet, neither
  with a floor, neither ever a target ([`gates.md`](gates.md) → *Disclosures*); **the
  retrospective is written — stamped first, then pruned, then the entry; the
  list at or under its cap, every deletion logged in the archive with its commit,
  entries older than five run stamps rotated into `<artifacts>/retro/` **and the
  stamp table itself held to ten — at the eleventh the oldest stamp rotates whole into
  the same archive, and both counts print beside the verdict** (the stamp table is read
  in full at stage 0, so *one line per run* is a slope the prune has to stop), the run
  stamped with its commit, every SHA in either file resolvable, and the
  counts printed beside this verdict**; **where `pipeline.json` → `retro.publish` is
  set, the skill-level insight is published as an issue on the skill's repository —
  its body printed in full first, the printed string and the sent string being one
  string, and the five redaction rules applied
  ([`retrospective.md`](retrospective.md) → *What may leave the project*). Absent, the
  step does not exist and is not asked about: publishing to another repository is an
  outward act and silence authorizes none. **Either way the verdict carries a `publish:`
  line** — the issue url, `0 (configured, nothing insight-grade)`, or `not configured
  (N insight-grade entries stayed local)`: an unarmed path and one with nothing to say
  are otherwise indistinguishable, which is how this instruction went unread for eight
  releases** ([`retrospective.md`](retrospective.md) → *`publish:` is a line in the
  verdict*)**; **the documentation gate has been seen
  failing once against a planted defect and its ratchet counts are printed**
  ([`gates.md`](gates.md)); **every repository is closed — the parent included:
  `git submodule status` shows no `+`, each repo clean and pushed**; **every check this gate leans on has been seen failing
  once against a planted defect** (an unproven check's green is not evidence);
  every REQ has a status (none `unknown`); every `verified`
  carries evidence; every `partial` names what's missing and where it's tracked;
  every `deferred`/`dropped` has the operator's agreement and, for `deferred`, a
  tracker entry; no carry-over row left `unresolved`, and the ledger's counts are
  printed with the verdict; the operator answers the
  closing question and signs off. Manual by design — an automated check can prove
  the table is well-formed, only the person who asked can confirm it is what they
  asked for.

## The program loop — a platform, one brick at a time

When stage 2 produced a **module map** ([`decomposition.md`](decomposition.md)),
stages 0–2 have run once for the whole platform and the rest of the pipeline runs
**per module**, in build order:

```
module N → 3 spec (dossier) → 4 plan → 5 build → 6 tests → 7 lint+deploy
         → 8 post-deploy → 9 docs+wiki → 10 acceptance → map status: done
         → module N+1 (back to 3)
```

- **No re-grilling, no re-decomposing per module.** New information that changes the
  map goes back to stage 2 as an explicit, operator-approved map revision — never a
  quiet edit mid-module.
- **Each module's spec is a full dossier** (`spec.md`): architecture, entities,
  contracts in and out, business rules, edge and failure cases, UI/Figma chain when
  it has a surface.
- **Deploy cadence is the brief's call** (autonomy sweep): per module, or once after
  several. Decide it up front, not per module.
- **Update the module map's status in the same commit as that module's acceptance.**
  The map is the resume point after a lost context.
- **Program done** when every row is `done` or `deferred` with an agreed home, the
  cross-module contracts are covered by tests that cross the seam, and a final
  acceptance covers the platform's whole REQ table — not module by module.

## Cross-cutting — the Doc Loop

A decision is not made at stage 9. It is made the moment something is settled —
in the grill, in the brainstorm's approved design, in the spec's locked contract,
in a ruling on a review finding at stage 5 — and every one of those is a stage that
can lose it.

- **It fires at any stage**, and the seven steps live in
  [`documentation.md`](documentation.md): orient and reconcile → reserve the id and
  record → resolve the question it answers → propagate by the matrix → adjust scope
  → record as-built → commit with the ids.
- **Step 7 is part of the loop, not after it.** A decision recorded and uncommitted
  is a decision that survives exactly as long as the working tree.
- **Reserve before you mint.** Reading *"Next free ID"* is not reserving it, and a
  second agent reading it in the same minute gets the same number.

## Cross-cutting — the loop guard

Any stage can be re-entered and any loop can churn: a pass undoing what an earlier
pass decided, two shapes alternating, the same file rewritten with no new
information. [`loop-guard.md`](loop-guard.md) is the detector and the break
protocol, and it binds every repeating loop here — the stage-5 fix loop, a stage
re-entered after a failed gate, the program loop above, any audit → fix → audit
cycle.

- **Every repeating pass logs one line per touched file** (`touch: <file> — pass N —
  reason: <finding id / gate item>`) to the run ledger. Detection is mechanical, not
  a feeling, and the ledger is what survives compaction.
- **Trips on:** revert-oscillation (A→B→A); the same file edited twice for the same
  reason; a finding already ADDRESSED or parked coming back; a stage entered a third
  time for one artifact; two loops editing one file. Hard caps: 5 fix rounds per
  task, 2 re-entries per stage per artifact, 3 passes per module.
- **On a trip: stop editing.** Name shapes A and B with their evidence, escalate to
  the layer that owns the conflict (rubric → operator → plan → spec → module map),
  re-plan the check as an ordered one-item-per-line checklist, then go through it in
  order, one commit per item. Never settle a higher-layer conflict inside a lower
  loop, and never adjudicate before the cap.

## Cross-cutting — the audit

The loop guard governs loops that **change** things. A loop that **looks** for
things fails the other way: it converges, spending pass after pass on its own last
pass's edits while the finding count stays healthy. [`audit.md`](audit.md) is that
method and that exit — the L0→L7 ladder, the seam questions, the axis-rotation
crossover, and the rule that a green from a check nobody has watched fail is worth
nothing.

- It runs **at stage 10 before the coverage table** (the only place that can find a
  requirement nobody ever wrote), **per module** in the program loop, and as the
  whole task when the request is itself an audit.
- **A finding class seen twice becomes a script**, not a third ledger row.
- **Whatever can't be fixed now becomes a ratchet** — a named, counted set that may
  only shrink, printed beside every gate verdict, so "green" never reads as
  "verified".
