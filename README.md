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

**Any agent via the skills CLI (Claude Code, Cursor, Codex, 70+ agents):**
```
npx skills add ssheleg/task-pipeline
```

**npm installer (no clone needed):**
```
npx github:ssheleg/task-pipeline          # straight from GitHub
npx task-pipeline-skill                   # from the npm registry
```
(package is `task-pipeline-skill` — the unscoped `task-pipeline` name is taken
on npm; installs the same skill + `/task-pipeline` command into `~/.claude`,
idempotent, `--force` to overwrite)

**Plain skill:**
```
git clone https://github.com/ssheleg/task-pipeline
cd task-pipeline && ./install.sh
```
(copies the skill into `~/.claude/skills/task-pipeline` and the `/task-pipeline`
command into `~/.claude/commands/`; idempotent — rerun skips existing installs,
`./install.sh --force` overwrites)

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

## По-русски

**task-pipeline** — оркестратор полного цикла доставки задачи для Claude Code:
один скилл проводит любую существенную задачу через **9 гейтованных стадий**
(изучение доков → брейншторм → спека → план → сборка сабагентами → тесты →
линт/деплой → пост-деплой проверка логов → синк доков/вики), построенных на
скиллах [superpowers](https://github.com/obra/superpowers).

- Ни одна стадия не стартует, пока не пройден гейт предыдущей; деплой требует
  зелёного полного прогона тестов и явного «go» оператора.
- Каждая стадия напоминает, какую модель включить (`/model`): 1–4 — Fable,
  5–6 — Opus, 7–9 — наследуется. Это только напоминание — модель переключает
  оператор.
- Стадии 6–9 читают конвенции хост-проекта из `CLAUDE.md` (тесты / линт /
  деплой / доки / вики), поэтому скилл работает в любом репозитории.

Запуск: скажите *«полный цикл»* / *«прогони по конвейеру»* или `/task-pipeline
<задача>`. Установка — см. раздел Install выше (плагин, `npx skills add
ssheleg/task-pipeline`, `npx task-pipeline-skill` / `npx
github:ssheleg/task-pipeline` или `./install.sh`).

## License

MIT © 2026 ssheleg.
