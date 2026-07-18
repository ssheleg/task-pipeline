# task-pipeline

Full-cycle task delivery pipeline orchestrator for **Claude Code**. One skill that
runs any substantial task through **8 gated stages** — built on the
[superpowers](https://github.com/obra/superpowers) skills.

## What it does

`docs study → brainstorm → spec → plan → subagent build → lint/deploy →
post-deploy log check → docs/wiki sync`

Each stage gates the next; each names the model to use.

| # | Stage | Model | Gate |
|---|---|---|---|
| 1 | Docs study | Fable | contracts grounded on current docs |
| 2 | Brainstorm | Fable | design approved |
| 3 | Spec | Fable | committed + reviewed |
| 4 | Plan | Fable | parallel-ready, DoD per task |
| 5 | Dev | Opus | tasks DONE, tests green |
| 6 | Lint + deploy | host | green before deploy |
| 7 | Post-deploy | host | clean boot / honest degradation |
| 8 | Docs + wiki | host | docs + wiki synced |

## Prerequisite

**superpowers** — https://github.com/obra/superpowers

```
/plugin marketplace add obra/superpowers
/plugin install superpowers@superpowers
```

## Install

**Plugin (recommended):**
```
/plugin marketplace add ssheleg/task-pipeline
/plugin install task-pipeline@task-pipeline
```

**Plain skill:**
```
git clone https://github.com/ssheleg/task-pipeline
cd task-pipeline && ./install.sh
```
(copies the skill into `~/.claude/skills/task-pipeline`)

## Use

Say *"run this through the pipeline"* / *"полный цикл"* / *"прогони по конвейеру"*,
or `/task-pipeline`. The skill creates a per-stage TaskList and walks the gates.

## Model tiering

Stages 1–4 → Fable, stage 5 → Opus, 6–8 → inherit. **Reminders only** — a skill
can't switch the main-loop model; `/model` is the operator's. Stage-5 subagents are
pinned to Opus automatically.

## Portability

Stages 6–8 read the host project's `CLAUDE.md` conventions (lint / deploy / docs /
wiki) with detection fallbacks, so the skill works in any repo.

## License

MIT © 2026 ssheleg.
