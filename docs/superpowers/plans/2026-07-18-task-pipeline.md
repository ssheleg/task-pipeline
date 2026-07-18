# task-pipeline — Implementation Plan

- **Date:** 2026-07-18
- **Spec:** docs/superpowers/specs/2026-07-18-task-pipeline-design.md

Single-implementer authoring build; TDD gate = `test/validate.py` (structural).
Red first (validator fails before files exist) → green after each task.

## Tasks

### T1 — Manifests
- Files: `.claude-plugin/marketplace.json`, `plugins/task-pipeline/.claude-plugin/plugin.json`.
- DoD: valid JSON; `plugins[0].source` → `./plugins/task-pipeline`; names all `task-pipeline`.

### T2 — Skill + references
- Files: `plugins/task-pipeline/skills/task-pipeline/SKILL.md` + `references/{stages,model-tiering,conventions}.md`.
- DoD: frontmatter `name`+`description`; 8-stage table; references present and linked.

### T3 — Packaging
- Files: `README.md`, `LICENSE` (MIT), `install.sh` (copies skill dir → `~/.claude/skills/task-pipeline`).
- DoD: install docs for both modes; prereq → obra/superpowers.

### T4 — Validator (test)
- File: `test/validate.py` per spec §8. Run `python3 test/validate.py` → PASS.
- DoD: exit 0, `PASS: task-pipeline structure valid`.

### T5 — Release
- Commits (spec, plan, build) → `gh repo create ssheleg/task-pipeline --public --source=. --remote=origin --push`.
- DoD: public repo on GitHub, `main` pushed, validator green.

## Human steps
- Post-release (optional): `/plugin marketplace add ssheleg/task-pipeline` to smoke-test plugin install.
