# Stages — detail & gates

For each stage: what it does, what to invoke, artifacts, and the **GATE** that
must pass before advancing.

## 1 — Docs study (Fable)
- **What:** ground every external library / API / SDK the task touches on the
  *current* docs, before locking any contract.
- **Invoke:** `context7` MCP (`resolve-library-id` → `get-library-docs`, scope by
  `topic`) or the `context7-docs` skill. Web-search fallback for libs context7
  can't resolve.
- **GATE:** every contract the design will lock is grounded in fetched docs, not
  recall. Unresolvable libraries are flagged in the spec.

## 2 — Brainstorm (Fable)
- **Invoke:** `superpowers:brainstorming`. One question at a time; 2–3 approaches +
  a recommendation; design presented in sections.
- **UI detection (mandatory check):** decide whether the task touches any
  user-facing surface (web, mobile, CLI, TUI — new feature, new screen/command,
  or a change to user-visible behavior). Record the verdict; it arms the UX
  track in stage 3.
- **GATE:** the user approves the design **and** the UI verdict is recorded.

## 3 — Spec (Fable) — with UX track for user-facing tasks
- **UX track (runs FIRST when stage 2 flagged UI; skip entirely otherwise).**
  Requires the **super-ux** skills (`/plugin marketplace add ssheleg/super-ux` →
  `/plugin install super-ux@super-ux`, or `npx skills add ssheleg/super-ux`);
  if missing on a UI task → tell the operator to install and stop.
  1. `/ux` (super-ux entry) — inspects/repairs `docs/ux/` setup in the host project.
  2. `ux-foundation` — the WHY layer: personas, Jobs to Be Done, **customer
     journey maps (CJM)**, user stories with Given/When/Then acceptance
     criteria. Create if missing; update if the feature shifts who/why.
  3. `ux-scenarios` — draft the feature's usage scenarios and validate them
     against the existing base per the super-ux format contract
     (`scenario-format.md`, ux-contract v2): IDs, statuses, `Traces:` to
     foundation stories/journey stages, edge/error states enumerated.
- **Spec:** brainstorming writes the design to
  `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` and commits it. Lock all
  shared contracts (types, schemas, signatures, file layout). For UI tasks the
  spec **embeds the UX layer**: links the validated scenario IDs and the CJM
  stages the feature serves, and states which UX patterns/guides from super-ux
  apply (per-scenario quality bars, error/empty/loading states, traceability).
- **GATE:** spec committed **and** user-reviewed; for UI tasks additionally:
  scenarios validated in `docs/ux/scenarios.md`, CJM/foundation coverage in
  `docs/ux/foundation.md` (or explicit v1-mode/tiny-project waiver by the
  operator), and every user-facing spec requirement traces to a scenario ID.
  No plan (stage 4) starts before this — scenarios come BEFORE interface.

## 4 — Plan (Fable)
- **Invoke:** `superpowers:writing-plans` →
  `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`. Zero-context tasks, exact
  paths, TDD steps, DoD each, dependency graph + parallel groups, non-overlapping
  file ownership.
- **GATE:** every spec requirement maps to a task; no placeholders; parallel-group
  tasks share no files. For UI tasks: every task building user-facing behavior
  names the scenario ID(s) it implements, and its DoD includes satisfying them.

## 5 — Dev (Opus)
- **Invoke:** `superpowers:using-git-worktrees` (isolate) →
  `superpowers:subagent-driven-development` (or `superpowers:executing-plans`).
  TDD per task (failing test → minimal impl → green → commit). Pin subagents to Opus.
- **GATE:** all plan tasks DONE (two-stage review: spec compliance, then code
  quality); full test suite green.

## 6 — Tests (Opus)
- **What:** consolidate test coverage for the change: confirm new functionality
  has tests (written test-first in stage 5), update/repair existing tests the
  change touched, and add edge-case + failure-path tests per DoD.
- **Invoke:** the host test runner (see `conventions.md` → *Lint + test*);
  `superpowers:test-driven-development` for any uncovered gap.
- **GATE:** the **full** suite is green (not just the new tests); new/changed code
  is covered; no `skip`/`xfail` smuggling a red suite past the gate. Never advance
  to deploy on a red or partial run.

## 7 — Lint + deploy (host model)
- Read host conventions (`conventions.md`): run the linter; fix failures. The suite
  is already green from stage 6 — re-run it if code changed since. Then deploy per
  the project's convention.
- **GATE:** lint clean **and** suite green **before** deploy. Deploy is outward →
  explicit operator go. Respect deploy-from-main rules if the project mandates them.

## 8 — Post-deploy (host model)
- Tail deploy logs / health-check per conventions. Confirm clean boot, no error
  spike, live subsystems healthy.
- **GATE:** clean boot confirmed, or an **honest degradation report** with next
  steps — never silent success.

## 9 — Docs + wiki (host model)
- Update host module docs / runbooks per the project's self-update rules, in the
  **same change**. Then sync knowledge to the wiki (`wiki-update` skill).
- **GATE:** docs in sync with code; wiki synced; dangling links fixed.
