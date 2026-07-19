# Changelog

## v0.3.0 — 2026-07-18

- **Machine-readable pipeline config** — new universal contract `pipeline.schema.json` (JSON Schema):
  a pipeline is an ordered list of stages, each with `skills[]` (the skills/agents that run it) and a
  `gate {type, check}`. The framework ships the schema plus a copy-and-rewrite `pipeline.example.json`
  (encoding the plugin's own default superpowers flow); it imposes no specific stages, skills, or gate
  assignments.
- **Bring your own skills / stages** — copy `pipeline.example.json` → `pipeline.json` in your project
  and rewrite it: its own stages (any count), each run by your own skills/agents via `skills[]`, with
  its own gate types. Nothing about the stage set, the skills, or which gates are manual is fixed.
- **Typed gates** — every gate declares a `type`: `auto` (orchestrator verifies the check, pass/fail)
  or `manual` (wait for explicit operator go). Surfaced in SKILL.md's run loop, the example stage
  table (new **Type** column), and each `**GATE (auto|manual):**` line in stages.md.
- Validator extended: `test/validate.py` checks the schema is well-formed and the example conforms —
  a dependency-free shape check (≥1 stage, unique `state`, non-empty `skills[]`, `gate.type ∈
  {auto,manual}` + non-empty `check`), plus a full `jsonschema` pass when the library is installed.

## v0.2.0 — 2026-07-18

- Added a dedicated **Tests** stage (new stage 6, model Opus) between Dev and
  Lint/deploy: writes tests for new functionality, updates/repairs existing tests
  touched by the change, and adds edge-case + failure-path coverage.
- Hard **full-suite-green gate before deploy** — the deploy stage now requires both
  lint clean and the whole suite green; never advances on a red or partial run.
- Pipeline grew 8 → 9 stages; deploy/post-deploy/docs renumbered 7/8/9. Model
  tiering: Fable 1–4, Opus 5–6, inherit 7–9. Docs/tables/references synced.
- Added a real `/task-pipeline` slash command (`commands/task-pipeline.md`);
  `install.sh` now installs it to `~/.claude/commands/` alongside the skill so the
  command works for the plain-skill path too.
- Validator hardened: enforces marketplace↔plugin.json **version sync** and the
  presence of the command file.

## v0.1.0 — 2026-07-18

Initial release.

- Thin orchestrator skill that runs a task through 8 gated stages (docs study →
  brainstorm → spec → plan → subagent build → lint/deploy → post-deploy log check
  → docs/wiki sync), built on the [superpowers](https://github.com/obra/superpowers) skills.
- Hybrid distribution: Claude Code plugin/marketplace + plain `~/.claude/skills` copy.
- Soft per-stage model tiering (Fable stages 1–4, Opus stage 5, inherit 6–8) — reminder only.
- Generic-portable: stages 6–8 read the host project's `CLAUDE.md` conventions with detection fallbacks.
- Structural validator (`test/validate.py`); spec + plan under `docs/superpowers/`.
