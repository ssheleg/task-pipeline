# task-pipeline

Full-cycle task delivery pipeline orchestrator for **Claude Code**. One skill that
runs any substantial task through an up-front **intake grill** + **9 gated stages** —
built on the [superpowers](https://github.com/obra/superpowers) skills.

## What it does

`intake grill → docs study → brainstorm → spec → plan → subagent build → tests →
lint/deploy → post-deploy log check → docs/wiki sync`

It **grills you first**: a one-line task ("make me feature X") is expanded, one
question at a time, into a locked brief — so the remaining stages run to the end
without mid-flight questions. Each stage gates the next; each names the model to
use. Every gate is typed — **auto** (the orchestrator verifies it, pass/fail) or
**manual** (waits for your go).

| # | Stage | Model | Gate | Type |
|---|---|---|---|---|
| 0 | Intake grill | Fable | shared understanding reached; brief locked | manual |
| 1 | Docs study | Fable | contracts grounded on current docs | auto |
| 2 | Brainstorm | Fable | design approved; UI verdict recorded | manual |
| 3 | Spec | Fable | committed + reviewed; UI: scenarios + CJM traced | manual |
| 4 | Plan | Fable | parallel-ready, DoD per task | auto |
| 5 | Dev | Opus | tasks DONE, TDD green per task | auto |
| 6 | Tests | Opus | full suite green, new code covered | auto |
| 7 | Lint + deploy | host | lint clean + suite green before deploy | manual |
| 8 | Post-deploy | host | clean boot / honest degradation | auto |
| 9 | Docs + wiki | host | docs + wiki synced | auto |

These stages (0 intake + 1→9) are the plugin's **example** flow. It's a machine-readable config
([`pipeline.example.json`](plugins/task-pipeline/skills/task-pipeline/pipeline.example.json))
against a universal contract
([`pipeline.schema.json`](plugins/task-pipeline/skills/task-pipeline/pipeline.schema.json)):
a host project copies the example to `pipeline.json` and rewrites it with its own
stages (any count), its own `skills[]`, and its own `auto`/`manual` gate types —
"bring your own skills". The framework bakes in no fixed stages.

## Intake grill (stage 0)

Inspired by [Matt Pocock's grill-me](https://github.com/mattpocock/skills). Before
any technical work, task-pipeline interviews you relentlessly — one question per
turn, each with a recommended answer, exploring the codebase before asking — until
every decision branch is resolved and locked into a **task brief**. That front-loads
all the human input so stages 1→9 run autonomously (only the built-in gates pause).
Uses the `grill-me` / `grilling` skill if installed; otherwise runs a built-in grill
loop (no hard dependency).

## UX track (user-facing tasks) — super-ux recommended

The moment a task touches any user-facing surface (web / mobile / CLI / TUI — a
screen, command, or visible behavior), [super-ux](https://github.com/ssheleg/super-ux)
is the **recommended** workflow, detected early in the stage-0 grill. If it's
installed, task-pipeline uses it; if not, it gives you the install line on the spot.
The spec stage runs it **before any plan is written**: `/ux` (setup check) →
`ux-foundation` (personas, JTBD, **customer journey maps**, user stories) →
`ux-scenarios` (usage scenarios validated against the base, ux-contract v2). The
spec then embeds the UX layer — scenario IDs, CJM stages served, applicable UX
patterns — and the plan's UI tasks carry scenario IDs in their DoD. Scenarios come
before interface.

## Prerequisites

**superpowers** — https://github.com/obra/superpowers

```
/plugin marketplace add obra/superpowers
/plugin install superpowers@superpowers
```

**super-ux** (only for user-facing tasks) — https://github.com/ssheleg/super-ux

```
/plugin marketplace add ssheleg/super-ux
/plugin install super-ux@super-ux
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

**Cursor:**
```
npx skills add ssheleg/task-pipeline --agent cursor --global   # global, or…
```
…or per project, copy `cursor/rules/task-pipeline.mdc` into the repo's
`.cursor/rules/`. Cursor has no global rules directory — use the skills CLI for a
global install, the `.mdc` for per-project, or paste it into Cursor Settings →
Rules. The rule is self-contained (no external links), so it works copied anywhere.

**Plain skill:**
```
git clone https://github.com/ssheleg/task-pipeline
cd task-pipeline && ./install.sh
```
(copies the skill into `~/.claude/skills/task-pipeline` and the `/task-pipeline`
command into `~/.claude/commands/`; idempotent — rerun skips existing installs,
`./install.sh --force` overwrites)

## Updating everywhere

Pick **one** channel per agent (running the plugin and the plain/skills-CLI copy
on the same Claude Code install yields a duplicate skill).

| Agent / channel | Update |
|---|---|
| Claude Code (plugin) | `claude plugin marketplace update task-pipeline` → `claude plugin update task-pipeline@task-pipeline` → restart |
| Any agent (skills CLI) | `npx skills add ssheleg/task-pipeline --agent <name> --global` (re-run overwrites); `--agent '*'` for all |
| Cursor | skills CLI (above) with `--agent cursor`, or re-copy the `.mdc` per project |
| npm | `npx task-pipeline-skill@latest` / `npx github:ssheleg/task-pipeline` (ephemeral — always latest) |
| Plain skill | `git pull && ./install.sh --force` |

## Use

Say *"run this through the pipeline"* / *"полный цикл"* / *"прогони по конвейеру"*,
or `/task-pipeline`. The skill creates a per-stage TaskList and walks the gates.

## Model tiering

Stages 0–4 → Fable, stages 5–6 → Opus, 7–9 → inherit. **Reminders only** — a skill
can't switch the main-loop model; `/model` is the operator's. Stage-5 subagents are
pinned to Opus automatically.

## Release automation (project-configurable, toggleable)

A pipeline config may declare an optional `release` block (see
[`pipeline.schema.json`](plugins/task-pipeline/skills/task-pipeline/pipeline.schema.json)):
a master `enabled` toggle, a `trigger`, project-defined `steps`, and `verify`
smoke-checks. It's **off unless a project turns it on**, and every project
configures its own. This repo's own instance is
[`.github/workflows/release.yml`](.github/workflows/release.yml) — armed per repo
by the `RELEASE_ENABLED` variable (unset = off), it validates the tag against the
manifests, cuts a GitHub release from the CHANGELOG, and smoke-tests `npx` from a
clean checkout. Copy and adapt it per project; nothing is hardcoded.

## Companion skills

`references/companion-skills.md` lists what powers each stage and how to install
it: **superpowers** (required), **super-ux** (required for user-facing tasks —
install line surfaced on the spot), **grill-me** (optional, enhances the stage-0
grill), **context7** (docs stage), **wiki-update** (stage 9). A preflight prints
which are ready and which to install so you can arm the full flow before work.

## Portability

Stages 6–9 read the host project's `CLAUDE.md` conventions (tests / lint / deploy /
docs / wiki) with detection fallbacks, so the skill works in any repo. The
canonical artifact layout each stage writes to is fixed in
[`references/artifacts.md`](plugins/task-pipeline/skills/task-pipeline/references/artifacts.md).

## По-русски

**task-pipeline** — оркестратор полного цикла доставки задачи для Claude Code:
один скилл проводит любую существенную задачу через **интейк-грил + 9 гейтованных
стадий** (изучение доков → брейншторм → спека → план → сборка сабагентами →
тесты → линт/деплой → пост-деплой проверка логов → синк доков/вики), построенных
на скиллах [superpowers](https://github.com/obra/superpowers).

- **Грил на входе (стадия 0):** одна строка задачи («сделай фичу X») недостаточна
  для автономной работы. Пайплайн сначала «допрашивает» оператора — по одному
  вопросу за ход, с рекомендованным ответом, изучив код до вопроса — пока все
  ветки решений не закрыты и не зафиксированы в брифе. Это выносит весь ввод
  человека вперёд, дальше стадии 1→9 идут автономно. Идея взята из
  [grill-me Мэтта Покока](https://github.com/mattpocock/skills); использует скилл
  `grill-me`/`grilling` если установлен, иначе — встроенный грил-цикл.
- Ни одна стадия не стартует, пока не пройден гейт предыдущей; деплой требует
  зелёного полного прогона тестов и явного «go» оператора.
- **UX-трек (super-ux рекомендуется):** как только задача трогает интерфейс
  (web/mobile/CLI/TUI), [super-ux](https://github.com/ssheleg/super-ux) —
  рекомендуемый воркфлоу, детектится ещё на гриле; если установлен — используется,
  если нет — сразу даётся строка установки. Стадия спеки гоняет `/ux` →
  `ux-foundation` (персоны, JTBD, CJM) → `ux-scenarios` (сценарии по ux-contract
  v2) до написания плана; спека включает ID сценариев, стадии CJM и UX-паттерны.
  Сценарии — до интерфейса.
- Каждая стадия напоминает, какую модель включить (`/model`): 0–4 — Fable,
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
