# task-pipeline

[![npm](https://img.shields.io/npm/v/task-pipeline-skill)](https://www.npmjs.com/package/task-pipeline-skill)
[![validate](https://github.com/ssheleg/task-pipeline/actions/workflows/validate.yml/badge.svg)](https://github.com/ssheleg/task-pipeline/actions/workflows/validate.yml)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Full-cycle task delivery pipeline orchestrator for **Claude Code**. One skill that
runs any substantial task through an up-front **intake grill** + **9 gated stages** —
with every stage's doctrine **built in**: no companion plugin required.

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

## Everything is built in — zero required dependencies

The doctrine each stage runs on ships inside the skill. Nothing to install for it,
nothing to resolve at preflight, no version skew with someone else's repo, and no
stage that can fail because a plugin is missing:

| Stage | Built-in doctrine |
|---|---|
| 0 Intake grill | [`references/grill.md`](plugins/task-pipeline/skills/task-pipeline/references/grill.md) — interview loop, domain awareness, autonomy sweep |
| 2 Brainstorm | [`references/brainstorm.md`](plugins/task-pipeline/skills/task-pipeline/references/brainstorm.md) — approaches, YAGNI, the no-code-before-approval gate |
| 3 Spec | [`references/spec.md`](plugins/task-pipeline/skills/task-pipeline/references/spec.md) — UX-track order, locked contracts, global constraints, self-review |
| 4 Plan | [`references/planning.md`](plugins/task-pipeline/skills/task-pipeline/references/planning.md) — zero-context tasks, parallel groups, no placeholders |
| 5 Build | [`references/build.md`](plugins/task-pipeline/skills/task-pipeline/references/build.md) + [`review.md`](plugins/task-pipeline/skills/task-pipeline/references/review.md) — isolation, ledger, subagent loop, review rubric, fix loop |
| 5–6 TDD | [`references/tdd.md`](plugins/task-pipeline/skills/task-pipeline/references/tdd.md) — the iron law, red/green/refactor, the suite gate |

**Ported, not depended on.** Stage 0 is adapted from
[Matt Pocock's `grilling` / `grill-with-docs`](https://github.com/mattpocock/skills)
and stages 2–6 from the corresponding skills in
[obra/superpowers](https://github.com/obra/superpowers) — both MIT, both credited in
[LICENSE](LICENSE) → *Third-party*. Nothing at runtime reaches for either.

**Optional bridge:** if you already run an equivalent skill set, map it onto stages
2/4/5/6 in your `pipeline.json` → `skills[]`. That's a substitution, never a
requirement — the gates still govern, and nothing detects, recommends or waits for
an external provider.

## Intake grill (stage 0) — mandatory

Inspired by [Matt Pocock's grill-me](https://github.com/mattpocock/skills). Before
any technical work, task-pipeline interviews you relentlessly — one question per
turn, each with a recommended answer, exploring the codebase before asking — until
every decision branch is resolved and locked into a **task brief**. There is no
"clear enough task" exemption: no stage-1 work starts without a committed,
confirmed brief.

**Built in — nothing to install.** The full doctrine ships inside the skill
([`references/grill.md`](plugins/task-pipeline/skills/task-pipeline/references/grill.md)):
no companion skill, no resolution step, no fallback path, no version skew. Adapted
from [Matt Pocock's grill-with-docs](https://github.com/mattpocock/skills) (MIT —
see [LICENSE](LICENSE) → *Third-party*).

**Domain awareness.** While exploring, the grill reads the project's own
`CONTEXT.md` / `docs/adr/` and holds you to them — calling out terms that conflict
with the glossary, replacing overloaded words with a canonical one, stress-testing
relationships against concrete edge cases, and surfacing where the code contradicts
what you just said. Resolved terms are written into `CONTEXT.md` as they land;
decisions that are hard to reverse, surprising without context **and** the result of
a real trade-off get an ADR. Both files are created lazily.

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

**None for the pipeline itself** — the doctrine for every stage ships inside the
skill (see *Everything is built in* above).

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

`references/companion-skills.md` separates what's built in (stages 0, 2, 3, 4, 5, 6
— nothing to install) from the short optional list: **super-ux** (required only for
user-facing tasks — install line surfaced on the spot), **context7** (docs stage),
**wiki-update** (stage 9). A single preflight block prints which are ready, which to
install, and the model recommendation, so you arm the whole run in one exchange.

## Portability

Stages 6–9 read the host project's `CLAUDE.md` conventions (tests / lint / deploy /
docs / wiki) with detection fallbacks, so the skill works in any repo. The
canonical artifact layout each stage writes to is fixed in
[`references/artifacts.md`](plugins/task-pipeline/skills/task-pipeline/references/artifacts.md).

## По-русски

**task-pipeline** — оркестратор полного цикла доставки задачи для Claude Code:
один скилл проводит любую существенную задачу через **интейк-грил + 9 гейтованных
стадий** (изучение доков → брейншторм → спека → план → сборка сабагентами →
тесты → линт/деплой → пост-деплой проверка логов → синк доков/вики). **Доктрина
каждой стадии встроена в скилл — обязательных зависимостей нет.**

- **Всё внутри — ставить нечего.** Стадии 0, 2, 3, 4, 5 и 6 работают по
  `references/{grill,brainstorm,spec,planning,build,review,tdd}.md`: нет
  компаньон-плагина, нет резолва на префлайте, нет рассинхрона версий с чужим репо
  и нет стадии, которая падает из-за отсутствующего плагина. Портировано (не
  зависимость): стадия 0 — из [grill-with-docs Мэтта
  Покока](https://github.com/mattpocock/skills), стадии 2–6 — из соответствующих
  скиллов [obra/superpowers](https://github.com/obra/superpowers); оба MIT, оба
  указаны в `LICENSE` → *Third-party*. Опциональный мост: если у вас уже стоит
  эквивалентный набор скиллов, его можно подставить на стадии 2/4/5/6 через
  `pipeline.json` → `skills[]` — это замена, а не требование.
- **Грил на входе (стадия 0) — обязателен.** Одна строка задачи («сделай фичу X»)
  недостаточна для автономной работы, поэтому стадию нельзя пропустить: пайплайн
  «допрашивает» оператора — по одному вопросу за ход, с рекомендованным ответом,
  изучив код до вопроса — пока все ветки решений не закрыты и не зафиксированы в
  брифе. Ни одна стадия 1+ не стартует без закоммиченного подтверждённого брифа.
  **Грил встроен в скилл** — ставить нечего: вся доктрина лежит в
  `references/grill.md`, без компаньонов, резолва и фолбэков. Портировано из
  [grill-with-docs Мэтта Покока](https://github.com/mattpocock/skills) (MIT, см.
  `LICENSE` → *Third-party*).
- **Доменная осознанность на гриле.** Пайплайн читает `CONTEXT.md` / `docs/adr/`
  проекта и держит оператора в рамках его же языка: ловит термины, конфликтующие с
  глоссарием, заменяет размытые слова каноничными, проверяет отношения конкретными
  краевыми сценариями, вскрывает расхождения между кодом и только что сказанным.
  Разрешённый термин сразу пишется в `CONTEXT.md`; решение, которое трудно
  откатить, неочевидно без контекста и стало результатом реального компромисса,
  получает ADR. Файлы создаются лениво.
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
