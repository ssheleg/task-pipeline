# Stages — detail & gates

For each stage: what it does, what to invoke, artifacts, and the **GATE** that
must pass before advancing. Each gate is tagged with its **type** — `auto` (the
orchestrator verifies the check itself, pass/fail) or `manual` (wait for the
operator's explicit go). These stages (0 intake + 1→10) are the plugin's
**example** flow, encoded in `pipeline.example.json` against the universal contract
`pipeline.schema.json`; a host project replaces it with its own
stages/agents/types (see SKILL.md → *Bring your own skills*).

## 0 — Intake grill — MANDATORY
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
  ledgers, **the retro's standing instructions** (`docs/superpowers/retro.md`, read
  **in full** — they are capped at ten and they bind this run; stamp each one as it
  fires, [`retrospective.md`](retrospective.md)), the **knowledge wiki** if one is
  installed
  ([obsidian-wiki](https://github.com/ar9av/obsidian-wiki) — recommended,
  never required), and any **other repo or hosted doc system the project names as
  its docs**. Write the **source ledger** into the brief (a row per source, or an
  explicit "none found"; the graph's row carries its build date). It is retrieval
  scoped by the task's own nouns, not a read of everything — and it is what makes
  phase 2's answers checkable instead of merely confident.
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
- **UI early-detect:** one branch of the grill is always "does this touch a
  user-facing surface (web/mobile/CLI/TUI)?". If yes → surface **super-ux**
  now (use it if installed; otherwise give the install line — see SKILL.md
  *Prerequisites*); this arms the stage-3 UX track.
- **Artifact:** lock the resolved decisions into a **task brief** committed at
  `docs/superpowers/specs/YYYY-MM-DD-<topic>-brief.md` (scope, users/UI verdict,
  constraints, assumptions, explicitly-deferred items, done-criteria) **plus the
  autonomy sweep's per-stage answers and the model decision**. Seed it from
  the skill's `templates/brief.md` skeleton — but only when absent, never
  overwrite an existing brief. Stages 2–4 build on this brief; stages 5–10 read
  its autonomy section instead of asking. Where the session produced them, also:
  an updated `CONTEXT.md` (terms written as they resolved) and any ADRs under
  `docs/adr/` — see `grill.md` → *Domain awareness*.
- **GATE (manual):** shared understanding reached — **the source ledger is written
  (every source consulted, or an explicit "none found")**, every detected branch has
  a recorded answer or an explicit deferral, **every answer that contradicted a
  harvested source has a recorded resolution** (which governs, and whether the doc
  is now stale), no open contradictions, **every
  autonomy-sweep row is answered or explicitly marked "stop and ask here"**, the
  **REQ table is written and every row names its check**, the carry-over ledger is
  seeded, the model decision is recorded, and the operator confirms the brief. Stop when a
  re-scan surfaces no new branches (don't grill past diminishing returns;
  reversible calls can be deferred with a note). Only then start stage 1.

## 1 — Docs study
- **What:** ground every external library / API / SDK the task touches on the
  *current* docs, before locking any contract.
- **Invoke:** `context7` MCP (`resolve-library-id` → `get-library-docs`, scope by
  `topic`) or the `context7-docs` skill. Web-search fallback for libs context7
  can't resolve.
- **GATE (auto):** every contract the design will lock is grounded in fetched docs,
  not recall. Unresolvable libraries are flagged in the spec.

## 2 — Brainstorm + decompose
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
- **GATE (manual):** the user approves the design, the UI verdict is recorded,
  **every REQ is answered by the design** — a requirement the design doesn't
  address is either covered now or explicitly dropped by the operator, with the
  drop recorded in the carry-over ledger — **and, for a platform, the module map is
  approved**: brick criteria met or excepted in writing, dependency graph acyclic,
  build order topological, every REQ mapped to exactly one module, cross-module
  contracts named with their owner.

## 3 — Spec — with UX track for user-facing tasks
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
- **Spec:** write the approved design to
  `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` and commit it. Lock all
  shared contracts (types, schemas, signatures, file layout). For UI tasks the
  spec **embeds the UX layer**: links the validated scenario IDs, the flows and
  `SCR-` screens, the CJM stages the feature serves, and the UX
  patterns/principles from super-ux that apply (`best-practices.md`,
  `ux-design-principles.md`, `component-guidelines.md`).
- **GATE (manual):** spec committed **and** user-reviewed; **every section carries
  `covers: REQ-…` and every REQ appears in at least one section**; for UI tasks
  additionally: the super-ux chain (foundation → flows → screens → scenarios) is
  designed, validated and approved; scenarios validated in `docs/ux/scenarios.md`;
  the linter passes; every user-facing spec requirement traces to a scenario ID
  (or an explicit v1-mode/tiny-project waiver by the operator). **With Figma on:
  the canonical record names one file, and every `screens.md` frame link carries
  that same `:fileKey`** — a string match, not a judgement; a differing key means
  the run drew in a second file nobody will open. No plan (stage 4)
  starts before this — the chain comes BEFORE interface.

## 4 — Plan
- **How it runs: [`planning.md`](planning.md)** — built into this skill →
  `docs/superpowers/plans/YYYY-MM-DD-<topic>.md` (same slug as the brief and the
  spec). Zero-context tasks, exact
  paths, complete code in every step, TDD steps with expected output, DoD each,
  dependency graph + parallel groups, non-overlapping file ownership, and the
  Global Constraints block copied verbatim from the spec.
- **GATE (auto):** **set equality — the REQ ids in the brief equal the union of
  `Implements:` across plan tasks.** A non-empty difference fails the gate and is
  reported as the explicit list of dropped requirements; this is the seam where
  scope leaks silently, so the check is mechanical, not a judgement call. Plus:
  every spec requirement maps to a task; no placeholders; names and
  types consistent across tasks; every task carries a verifiable DoD; parallel-group
  tasks share no files. For UI tasks: every task building user-facing behavior
  names the scenario ID(s) and `SCR-` screen(s) it implements, and its DoD
  includes satisfying them **and** updating the affected super-ux layers in the
  same change (super-ux *same-change* rule).

## 5 — Dev
- **How it runs: [`build.md`](build.md)** — built into this skill: isolate the
  workspace (native worktree tool first, git fallback, baseline tests), keep a
  ledger under `.task-pipeline/build/<plan>/` so a compacted context can resume,
  then one fresh implementer subagent per task with a file-based brief and report,
  a review after every task ([`review.md`](review.md)), and a five-round fix loop
  with an explicit breaker. TDD per task ([`tdd.md`](tdd.md)): failing test →
  watch it fail → minimal impl → watch it pass → commit. Pin subagents to the
  run's confirmed model (`model-tiering.md`). The plan's parallel groups fan out
  **only** when each implementer gets its own worktree; otherwise sequential.
- **Integration closes the stage:** sync with the base branch, re-run the full suite
  on the result, land it the project's way (merge, or a PR — outward, so it needs a
  go), remove the worktree. Stages 7–9 act on the integrated result, so a branch the
  operator chose to leave unmerged is recorded as such.
- **GATE (auto):** all plan tasks DONE (three review verdicts per task: spec
  compliance, **REQ satisfied**, code quality); every finding fixed or parked with a
  ruling; **every parked finding and implementer concern harvested into the
  carry-over ledger** — nothing stays only in the scratch workspace, which is
  deleted; no task left BLOCKED; full test suite green; branch integrated per the brief's policy (or the operator's
  "leave it" recorded).

## 6 — Tests
- **What:** consolidate test coverage for the change: confirm new functionality
  has tests (written test-first in stage 5), update/repair existing tests the
  change touched, and add edge-case + failure-path tests per DoD.
- **Invoke:** the host test runner (see `conventions.md` → *Lint + test*); the
  built-in [`tdd.md`](tdd.md) cycle for any uncovered gap — failing test first,
  same as stage 5.
- **GATE (auto):** the **full** suite is green (not just the new tests); new/changed code
  is covered; no `skip`/`xfail` smuggling a red suite past the gate. Never advance
  to deploy on a red or partial run.

## 7 — Lint + deploy
- Read host conventions (`conventions.md`): run the linter; fix failures. The suite
  is already green from stage 6 — re-run it if code changed since. For UI projects,
  the **super-ux linter** (`python3 docs/ux/lint.py` / `/ux-lint`) is part of lint —
  it must pass too (no UX drift merges). Then deploy per the project's convention;
  if the project defines release automation (`pipeline.json` → `release`, toggle
  on), that is what "deploy" runs here.
- **GATE (manual):** lint clean (host linter **and**, for UI projects, the super-ux
  linter) **and** suite green **before** deploy, **and no REQ is still `open`** — a
  `partial` ships only with the operator's explicit acceptance. A gap is cheapest to
  close before it ships, and the operator is already present at this gate. Deploy is outward → explicit
  operator go. Respect deploy-from-main rules if the project mandates them.

## 8 — Post-deploy
- Tail deploy logs / health-check per conventions. Confirm clean boot, no error
  spike, live subsystems healthy.
- **GATE (auto):** clean boot confirmed, or an **honest degradation report** with next
  steps — never silent success.

## 9 — Docs + wiki
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
- **GATE (auto):** docs in sync with code; every stale row in the source ledger
  either updated or carried over with its edit; UI: super-ux layers current +
  linter green; wiki synced (or absent and recommended once); **the code graph
  refreshed where one exists, or the reason it wasn't written into the carry-over
  ledger** (absent and recommended once is fine); dangling links fixed.

## 10 — Acceptance
- **What:** the closing stage — go back to the brief and account for **every**
  requirement. Doctrine: [`acceptance.md`](acceptance.md). Every earlier gate asks
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
  `docs/superpowers/specs/YYYY-MM-DD-<topic>-acceptance.md` — one row per REQ,
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
  written to `docs/superpowers/retro.md` — one file per project, not per run. The
  pipeline's gates are good at *this* run and blind across runs: the same class of
  failure can be caught, fixed and forgotten five times and nothing in the flow
  notices it is the same one. So, in this order: **prune first** (every standing
  instruction against its three retirement triggers — it became a check, its
  surface is gone, it hasn't fired in five run stamps — and the list held to its cap
  of ten, every deletion logged), **stamp the run**, then **write an entry only if
  the run diverged** (symptom · the stage it surfaced at · the stage that *owned* it
  · root cause · fix, mechanical before instruction before expiring note · the check
  that catches it next time). Every run prunes and stamps; a retro left empty after
  a messy run is the failure the file exists to stop. Stage 0 reads the standing
  instructions in full next time, which is why the cap is not negotiable.
- **GATE (manual):** the ladder walk ran and its absences became REQ rows before
  the table was written; **the retrospective is written — prune before entry, the
  list at or under its cap with every deletion logged, the run stamped, and the
  counts printed beside this verdict**; **every repository is closed — the parent included:
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
