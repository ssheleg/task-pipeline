# Stages — detail & gates

For each stage: what it does, what to invoke, artifacts, and the **GATE** that
must pass before advancing. Each gate is tagged with its **type** — `auto` (the
orchestrator verifies the check itself, pass/fail) or `manual` (wait for the
operator's explicit go). These stages (0 intake + 1→9) are the plugin's
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
  up front so stages 1→9 need no further human input beyond the manual gates.
  This is input expansion, not design: turn "make me feature X" into locked
  answers for scope, users, constraints, data, edge cases, done-criteria.
- **How it runs: [`grill.md`](grill.md)** — the full doctrine, built into this
  skill (nothing to install). In short: one question per turn, a recommended
  answer with each, explore the codebase before asking, depth-first through the
  decision tree, contradictions reconciled on the spot; plus **domain awareness**
  (challenge terms against `CONTEXT.md`, sharpen fuzzy language, stress-test with
  concrete scenarios, cross-reference the code, record ADRs for hard-to-reverse
  calls) and the **autonomy sweep** that pre-resolves every stage-1→9 blocker.
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
  overwrite an existing brief. Stages 2–4 build on this brief; stages 5–9 read
  its autonomy section instead of asking. Where the session produced them, also:
  an updated `CONTEXT.md` (terms written as they resolved) and any ADRs under
  `docs/adr/` — see `grill.md` → *Domain awareness*.
- **GATE (manual):** shared understanding reached — every detected branch has a
  recorded answer or an explicit deferral, no open contradictions, **every
  autonomy-sweep row is answered or explicitly marked "stop and ask here"**, the
  model decision is recorded, and the operator confirms the brief. Stop when a
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

## 2 — Brainstorm
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
- **GATE (manual):** the user approves the design **and** the UI verdict is recorded.

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
  1. `/ux` (the only super-ux entry) — reports which `docs/ux/` layers exist,
     repairs the skeleton, records the Figma on/off choice, recommends the next
     action. Never make the operator pick skills.
  2. `ux-foundation` → `docs/ux/foundation.md` — the **WHY**: personas, Jobs to
     Be Done, **customer journey maps (CJM)**, user stories (Given/When/Then).
  3. `ux-flows` → `docs/ux/flows.md` + `docs/ux/screens.md` — the **HOW + UI
     map**: task analysis, user-flow diagrams (branches, error paths), every
     screen + state with wireframe and (Figma on) a Figma frame link.
  4. `ux-scenarios` → `docs/ux/scenarios.md` — the **WHAT** (source of truth for
     behavior): scenarios validated per the format contract (`scenario-format.md`,
     ux-contract v4) — IDs, statuses, `Traces:` to stories/journey stages/flows,
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
- **GATE (manual):** spec committed **and** user-reviewed; for UI tasks
  additionally: the super-ux chain (foundation → flows → screens → scenarios) is
  designed, validated and approved; scenarios validated in `docs/ux/scenarios.md`;
  the linter passes; every user-facing spec requirement traces to a scenario ID
  (or an explicit v1-mode/tiny-project waiver by the operator). No plan (stage 4)
  starts before this — the chain comes BEFORE interface.

## 4 — Plan
- **How it runs: [`planning.md`](planning.md)** — built into this skill →
  `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`. Zero-context tasks, exact
  paths, complete code in every step, TDD steps with expected output, DoD each,
  dependency graph + parallel groups, non-overlapping file ownership, and the
  Global Constraints block copied verbatim from the spec.
- **GATE (auto):** every spec requirement maps to a task; no placeholders; names and
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
- **GATE (auto):** all plan tasks DONE (two-stage review: spec compliance, then code
  quality); every finding fixed or parked with a ruling; no task left BLOCKED; full
  test suite green; branch integrated per the brief's policy (or the operator's
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
  linter) **and** suite green **before** deploy. Deploy is outward → explicit
  operator go. Respect deploy-from-main rules if the project mandates them.

## 8 — Post-deploy
- Tail deploy logs / health-check per conventions. Confirm clean boot, no error
  spike, live subsystems healthy.
- **GATE (auto):** clean boot confirmed, or an **honest degradation report** with next
  steps — never silent success.

## 9 — Docs + wiki
- Update host module docs / runbooks per the project's self-update rules, in the
  **same change**. For UI tasks, confirm the super-ux layers were updated in this
  change and the linter is green (super-ux *same-change* + *no-drift* rules). Then
  sync knowledge to the wiki (`wiki-update` skill).
- **GATE (auto):** docs in sync with code; UI: super-ux layers current + linter
  green; wiki synced; dangling links fixed.
