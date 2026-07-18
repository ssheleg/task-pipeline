# task-pipeline

Full-cycle task delivery pipeline orchestrator for **Claude Code**. One skill that
runs any substantial task through **9 gated stages** — built on the
[superpowers](https://github.com/obra/superpowers) skills.

## What it does

`docs study → brainstorm → spec → plan → subagent build → tests → lint/deploy →
post-deploy log check → docs/wiki sync`

Each stage gates the next; each names the model to use.

| # | Stage | Model | Gate |
|---|---|---|---|
| 1 | Docs study | Fable | contracts grounded on current docs |
| 2 | Brainstorm | Fable | design approved |
| 3 | Spec | Fable | committed + reviewed |
| 4 | Plan | Fable | parallel-ready, DoD per task |
| 5 | Dev | Opus | tasks DONE, TDD green per task |
| 6 | Tests | Opus | full suite green, new code covered |
| 7 | Lint + deploy | host | lint clean + suite green before deploy |
| 8 | Post-deploy | host | clean boot / honest degradation |
| 9 | Docs + wiki | host | docs + wiki synced |

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
(copies the skill into `~/.claude/skills/task-pipeline` and the `/task-pipeline`
command into `~/.claude/commands/`)

## Use

Say *"run this through the pipeline"* / *"полный цикл"* / *"прогони по конвейеру"*,
or `/task-pipeline`. The skill creates a per-stage TaskList and walks the gates.

## Model tiering

Stages 1–4 → Fable, stages 5–6 → Opus, 7–9 → inherit. **Reminders only** — a skill
can't switch the main-loop model; `/model` is the operator's. Stage-5 subagents are
pinned to Opus automatically.

## Portability

Stages 6–9 read the host project's `CLAUDE.md` conventions (tests / lint / deploy /
docs / wiki) with detection fallbacks, so the skill works in any repo.

## License

MIT © 2026 ssheleg.
