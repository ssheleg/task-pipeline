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
- **GATE:** the user approves the design.

## 3 — Spec (Fable)
- brainstorming writes the design to
  `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` and commits it. Lock all
  shared contracts (types, schemas, signatures, file layout).
- **GATE:** spec committed **and** user-reviewed.

## 4 — Plan (Fable)
- **Invoke:** `superpowers:writing-plans` →
  `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`. Zero-context tasks, exact
  paths, TDD steps, DoD each, dependency graph + parallel groups, non-overlapping
  file ownership.
- **GATE:** every spec requirement maps to a task; no placeholders; parallel-group
  tasks share no files.

## 5 — Dev (Opus)
- **Invoke:** `superpowers:using-git-worktrees` (isolate) →
  `superpowers:subagent-driven-development` (or `superpowers:executing-plans`).
  TDD per task (failing test → minimal impl → green → commit). Pin subagents to Opus.
- **GATE:** all plan tasks DONE (two-stage review: spec compliance, then code
  quality); full test suite green.

## 6 — Lint + deploy (host model)
- Read host conventions (`conventions.md`): run linter + tests; fix failures; then
  deploy per the project's convention.
- **GATE:** lint + tests green **before** deploy. Deploy is outward → explicit
  operator go. Respect deploy-from-main rules if the project mandates them.

## 7 — Post-deploy (host model)
- Tail deploy logs / health-check per conventions. Confirm clean boot, no error
  spike, live subsystems healthy.
- **GATE:** clean boot confirmed, or an **honest degradation report** with next
  steps — never silent success.

## 8 — Docs + wiki (host model)
- Update host module docs / runbooks per the project's self-update rules, in the
  **same change**. Then sync knowledge to the wiki (`wiki-update` skill).
- **GATE:** docs in sync with code; wiki synced; dangling links fixed.
