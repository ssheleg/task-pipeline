# task-pipeline — Design Spec

> **Historical snapshot (v0.1.0, 8 stages).** Superseded by later releases: the
> live design is a stage-0 intake grill + 9 gated stages with typed auto/manual
> gates, a super-ux UX track, and toggleable release automation. Source of truth
> now: `plugins/task-pipeline/skills/task-pipeline/SKILL.md`, `pipeline.example.json`,
> and `CHANGELOG.md`. Kept as a dated design record — do not use for current shape.

- **Date:** 2026-07-18
- **Status:** approved (v0.1.0; superseded)
- **Owner:** ssheleg
- **Repo (target):** `ssheleg/task-pipeline` (GitHub, public, MIT)

## 1. Problem

Every non-trivial task follows the same disciplined delivery pipeline: docs study
→ brainstorm → spec → plan → subagent-driven development → lint/deploy →
post-deploy log check → docs/wiki update. Today this lives only as prose in a
personal `CLAUDE.md`. There is no installable skill that **orchestrates** the
whole cycle with gates between stages and a per-stage model recommendation. The
pieces exist (`superpowers:*`, `context7`, `wiki-update`) but nothing chains them.

## 2. Goal

A single **thin orchestrator skill**, `task-pipeline`, distributed as its own
public GitHub repo, installable as a Claude Code plugin (marketplace) or as a
plain skill directory. It drives a task through all 8 stages, gating each
transition and reminding the operator which model to switch to. **Generic-portable**:
stages 6–8 read the host project's conventions instead of hard-coding any project.

Non-goals (YAGNI): no vendoring of superpowers logic; no automatic model switching
(impossible for the main loop); no project-specific hard-coding; no runtime state
file (session TaskList is enough).

## 3. Locked decisions

| Decision | Choice |
|---|---|
| Distribution | Hybrid — marketplace manifest + usable as a plain `~/.claude/skills/` copy |
| superpowers dependency | Reference (thin orchestrator); hard prerequisite, checked at start |
| Model tiering | Boundary reminders — soft `/model` recommendation per stage |
| Scope | Generic-portable — stages 6–8 read host `CLAUDE.md` conventions |
| Name / visibility | `task-pipeline` / public |

## 4. Repository layout

```
task-pipeline/
├── .claude-plugin/marketplace.json
├── plugins/task-pipeline/
│   ├── .claude-plugin/plugin.json
│   └── skills/task-pipeline/
│       ├── SKILL.md
│       └── references/{stages.md,model-tiering.md,conventions.md}
├── docs/superpowers/{specs,plans}/
├── test/validate.py
├── install.sh
├── README.md
└── LICENSE
```

Plain-skill install copies `plugins/task-pipeline/skills/task-pipeline/` into
`~/.claude/skills/task-pipeline/`. Same tree serves both distribution modes.

## 5. Manifest contracts

Name-consistency invariant (validated): `marketplace.plugins[0].name` ==
`plugin.json.name` == skill dir name == `SKILL.md` frontmatter `name` ==
`"task-pipeline"`. Exact JSON in the built manifests.

## 6. Skill behaviour

1. Preflight — confirm superpowers skills installed; if missing, point to
   `https://github.com/obra/superpowers` and stop.
2. Create a TaskList — one task per stage (resumability).
3. Run 8 gated stages; between stages, model check → soft `/model` reminder; do
   not advance until the stage gate passes.

| # | Stage | Model | Invokes | Gate |
|---|---|---|---|---|
| 1 | Docs study | Fable | context7 / context7-docs | contracts grounded on fetched docs |
| 2 | Brainstorm | Fable | superpowers:brainstorming | design approved |
| 3 | Spec | Fable | brainstorming writes spec | committed + reviewed |
| 4 | Plan | Fable | superpowers:writing-plans | parallel-ready, DoD each |
| 5 | Dev | Opus | using-git-worktrees + subagent-driven-development (TDD) | tasks DONE, tests green |
| 6 | Lint+deploy | host | host lint/test → deploy | green before deploy; deploy needs go |
| 7 | Post-deploy | host | tail logs / health-check | clean boot or honest degradation |
| 8 | Docs+wiki | host | module docs/runbook → wiki-update | docs synced, wiki synced |

Cross-cutting: task tracker + conventional commits; worktree isolation; honest
degradation; outward/irreversible actions need explicit go.

## 7. Model tiering

Stages 1–4 → Fable 5 (`claude-fable-5`); stage 5 → Opus 4.8 (`claude-opus-4-8`);
stages 6–8 → inherit. Reminder, not a hard block. A skill can't change the
main-loop model; only `/model` (operator) can. Stage-5 subagents are pinned to
Opus by the orchestrator.

## 8. Validation (test contract)

`test/validate.py` (stdlib only, exit 0 = pass): both manifests parse; marketplace
source resolves to a dir with `.claude-plugin/plugin.json`; SKILL.md exists with
non-empty frontmatter `name`+`description`; name-consistency holds; three
`references/*.md` exist; `README.md` + `LICENSE` exist. Prints `PASS:` / `FAIL:`.

## 9. Install

Prereq: superpowers — `https://github.com/obra/superpowers`. Plugin:
`/plugin marketplace add ssheleg/task-pipeline` → `/plugin install task-pipeline@task-pipeline`.
Plain: `git clone … && ./install.sh`.

## 10. Open questions

None blocking. Marketplace name == plugin name == `task-pipeline` (accepted).
