# task-pipeline

[![npm](https://img.shields.io/npm/v/task-pipeline-skill)](https://www.npmjs.com/package/task-pipeline-skill)
[![validate](https://github.com/ssheleg/task-pipeline/actions/workflows/validate.yml/badge.svg)](https://github.com/ssheleg/task-pipeline/actions/workflows/validate.yml)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Full-cycle task delivery pipeline orchestrator for **Claude Code**. One skill that
runs any substantial task through an up-front **intake grill** + **9 gated stages** —
built on the [superpowers](https://github.com/obra/superpowers) skills.

## What it does

`intake grill → docs study → brainstorm → spec → plan → subagent build → tests →
lint/deploy → post-deploy log check → docs/wiki sync`

It **grills you first, always**: stage 0 is mandatory — a one-line task ("make me
feature X") is expanded, one question at a time, into a locked brief, and the grill
also sweeps stages 1→9 for anything that would stop the run later. Each stage gates
the next. Every gate is typed — **auto** (the orchestrator verifies it, pass/fail)
or **manual** (waits for your go). One model, confirmed before the run starts.

| # | Stage | Gate | Type |
|---|---|---|---|
| 0 | Intake grill — **mandatory** | shared understanding + autonomy sweep; brief locked | manual |
| 1 | Docs study | contracts grounded on current docs | auto |
| 2 | Brainstorm | design approved; UI verdict recorded | manual |
| 3 | Spec | committed + reviewed; UI: super-ux chain validated, linter green | manual |
| 4 | Plan | parallel-ready, DoD per task | auto |
| 5 | Dev | tasks DONE, TDD green per task | auto |
| 6 | Tests | full suite green, new code covered | auto |
| 7 | Lint + deploy | lint clean + suite green before deploy | manual |
| 8 | Post-deploy | clean boot / honest degradation | auto |
| 9 | Docs + wiki | docs + wiki synced | auto |

These stages (0 intake + 1→9) are the plugin's **example** flow. It's a machine-readable config
([`pipeline.example.json`](plugins/task-pipeline/skills/task-pipeline/pipeline.example.json))
against a universal contract
([`pipeline.schema.json`](plugins/task-pipeline/skills/task-pipeline/pipeline.schema.json)):
a host project copies the example to `pipeline.json` and rewrites it with its own
stages (any count), its own `skills[]`, and its own `auto`/`manual` gate types —
"bring your own skills". The framework bakes in no fixed stages.

## Intake grill (stage 0) — mandatory

Inspired by [Matt Pocock's grill-me](https://github.com/mattpocock/skills). Before
any technical work, task-pipeline interviews you relentlessly — one question per
turn, each with a recommended answer, exploring the codebase before asking — until
every decision branch is resolved and locked into a **task brief**. There is no
"clear enough task" exemption: no stage-1 work starts without a committed,
confirmed brief.

**The stage is required; the provider is not.** It runs through the `grill-me` /
`grilling` skill when that chain resolves, otherwise through the orchestrator's own
grill loop — both implement the same **grill contract**, neither is a downgrade.

**Autonomy comes from the sweep.** Beyond the task itself, the grill pre-resolves
everything that would otherwise interrupt stages 1→9: which external libs need docs,
branch and task-tracker policy, the test command and what "green" means, the lint
command, the deploy target and its **authorization**, where logs and health live,
which docs and runbooks to update, and the model. Each gets an answer or an explicit
"stop and ask me here" — an unasked question is a scheduled interruption. Deploy
authorization has a hard floor: a standing go counts only if it names the target and
the preconditions.

## UX track (user-facing tasks) — super-ux recommended

The moment a task touches any user-facing surface (web / mobile / CLI / TUI — a
screen, command, or visible behavior), [super-ux](https://github.com/ssheleg/super-ux)
is the **recommended** workflow, detected early in the stage-0 grill. If it's
installed, task-pipeline uses it; if not, it gives you the install line on the spot.
The spec stage runs it **before any plan is written**: `/ux` (setup check) →
`ux-foundation` (personas, JTBD, **customer journey maps**, user stories) →
`ux-flows` (user flows + `screens.md` UI map, Figma frames) → `ux-scenarios`
(usage scenarios validated against the base, ux-contract v4) → `/ux-lint` (must pass). The
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

**Any agent via the skills CLI (Cursor, Codex, OpenCode, 70+ — not Claude Code,
use the plugin above):**
```
npx skills add ssheleg/task-pipeline --agent cursor --agent codex --global
```
(one repeated `--agent` per agent; never include `claude-code` while the plugin is
installed — the plain copy shadows it)

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
| Any agent (skills CLI) | `npx skills update task-pipeline --global --yes`; to add: repeated `--agent <name>` (never `claude-code` when the plugin is installed) |
| Cursor | skills CLI (above) with `--agent cursor`, or re-copy the `.mdc` per project |
| npm | `npx task-pipeline-skill@latest` / `npx github:ssheleg/task-pipeline` (ephemeral — always latest) |
| Plain skill | `git pull && ./install.sh --force` |

## Use

Say *"run this through the pipeline"* / *"полный цикл"* / *"прогони по конвейеру"*,
or `/task-pipeline`. The skill creates a per-stage TaskList and walks the gates.

## Model policy

**One model, confirmed once, at preflight.** The default recommendation is *the most
capable reasoning model the environment offers* — currently the latest Opus
generation, but that's a **tier, not a string**. Model ids go stale as generations
ship, and you may be on another provider entirely, so nothing is hardcoded: the
pipeline resolves the top tier available at runtime and stage configs use
provider-agnostic tokens (`default` / `inherit`).

You confirm or override it (per-stage overrides welcome) before stage 0 — then it
**stops asking**. A skill can't switch the main-loop model; `/model` is yours.
Stage-5 subagents are pinned to the confirmed model automatically. If the
recommended tier isn't available, the pipeline says which one it's using and
continues — a reminder, never a block.

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
install line surfaced on the spot), **grill-me** (a swappable provider for the
mandatory stage-0 grill — its absence never blocks, the built-in loop runs the same
contract), **context7** (docs stage), **wiki-update** (stage 9). A single preflight
block prints which are ready, which to install, and the model recommendation, so you
arm the whole run in one exchange.

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

- **Грил на входе (стадия 0) — обязателен.** Одна строка задачи («сделай фичу X»)
  недостаточна для автономной работы, поэтому стадию нельзя пропустить: пайплайн
  «допрашивает» оператора — по одному вопросу за ход, с рекомендованным ответом,
  изучив код до вопроса — пока все ветки решений не закрыты и не зафиксированы в
  брифе. Ни одна стадия 1+ не стартует без закоммиченного подтверждённого брифа.
  Идея взята из [grill-me Мэтта Покока](https://github.com/mattpocock/skills).
  **Обязательна стадия, а не скилл:** грил идёт через `grill-me`/`grilling`, если
  цепочка резолвится, иначе — через собственный грил-цикл оркестратора; оба
  реализуют один и тот же контракт грилла, второй — не деградация.
- **Автономию даёт свип по стадиям.** Помимо самой задачи грил заранее закрывает
  всё, что иначе остановит стадии 1→9: внешние библиотеки и где их доки, политику
  веток и трекер задач, команду тестов и что значит «зелено», команду линта, цель
  деплоя и **авторизацию на него**, где живут логи/health, какие доки и раннбуки
  обновлять, и модель. По каждому пункту — либо ответ, либо явное «здесь
  остановись и спроси»; незаданный вопрос = запланированное прерывание. У
  авторизации деплоя жёсткий пол: постоянное «go» засчитывается, только если
  названы цель и предусловия.
- Ни одна стадия не стартует, пока не пройден гейт предыдущей; деплой требует
  зелёного полного прогона тестов и явного «go» оператора.
- **UX-трек (super-ux рекомендуется):** как только задача трогает интерфейс
  (web/mobile/CLI/TUI), [super-ux](https://github.com/ssheleg/super-ux) —
  рекомендуемый воркфлоу, детектится ещё на гриле; если установлен — используется,
  если нет — сразу даётся строка установки. Стадия спеки гоняет `/ux` →
  `ux-foundation` (персоны, JTBD, CJM) → `ux-flows` (флоу + `screens.md` — карта
  экранов) → `ux-scenarios` (сценарии, ux-contract v4) → `/ux-lint` (линтер должен
  быть зелёным) до написания плана; спека включает ID сценариев, `SCR-` экраны,
  стадии CJM и UX-паттерны.
  Сценарии — до интерфейса.
- **Модель — одна на прогон, подтверждается один раз до старта.** Рекомендация по
  умолчанию — *самая мощная reasoning-модель, доступная в окружении* (сейчас это
  последнее поколение Opus, но это **тир, а не строка**). Идентификаторы моделей
  устаревают, и провайдер может быть другой, поэтому ничего не захардкожено:
  актуальный топ-тир определяется в рантайме, а в конфиге стадий стоят
  провайдер-агностичные токены (`default` / `inherit`). Оператор подтверждает или
  переопределяет (можно по стадиям) — дальше пайплайн больше не переспрашивает.
  Сабагенты стадии 5 пинятся на подтверждённую модель автоматически.
- Стадии 6–9 читают конвенции хост-проекта из `CLAUDE.md` (тесты / линт /
  деплой / доки / вики), поэтому скилл работает в любом репозитории.

Запуск: скажите *«полный цикл»* / *«прогони по конвейеру»* или `/task-pipeline
<задача>`. Установка — см. раздел Install выше (плагин, `npx skills add
ssheleg/task-pipeline`, `npx task-pipeline-skill` / `npx
github:ssheleg/task-pipeline` или `./install.sh`).

## License

MIT © 2026 ssheleg.
