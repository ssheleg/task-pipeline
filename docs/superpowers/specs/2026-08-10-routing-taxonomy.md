# Routing taxonomy — which kinds of request this skill can be reached by

Measured 2026-08-10 at `8db58aa` (v1.38.0). This is a **measurement**, not a pipeline
run: it counts what the routing surfaces say and does not change them. Every verdict
below comes from a command's output.

> **Scope, stated so a verdict here is not quoted past it.** This measures the
> **vocabulary** — the words in `SKILL.md`'s description, the two no-task modes, the
> exclusion clause, the presence of doctrine, and the eval suite's `query` strings. It
> does **not** measure whether a model routes a given sentence, which is the only thing
> that would settle it. That measurement is board row `B-002`: **zero blind eval runs on
> zero of three models.** Read every "unrouted" below as *nothing names it*, never as
> *it was observed failing*.

---

## 1. What the routing surface actually says

`SKILL.md` frontmatter, **956 of the 1024-character limit** — 68 chars of headroom:

```
TRIGGERS   work changes the repository — a feature, fix, refactor, migration,
           integration, rewrite, adoption or hardening; фича, фикс, рефактор,
           миграция, интеграция, доработать, починить, внедрить — or on
           'run this through the pipeline' / 'прогони по конвейеру',
           'the full cycle' / 'полный цикл', /task-pipeline

MODES      'checkup' / 'чекап' — what has shipped without a person confirming it
           'setup'            — audits the documentation a project already has

EXCLUSIONS answering a question, explaining or reading code, a typo or a
           one-line edit — say 'без пайплайна' / 'quick' to opt out
```

**Every one of the eight trigger nouns is build-shaped.** They name work that adds or
changes product code. Nothing in the list names work whose output is a *finding*.

## 2. The taxonomy, measured

`✓` the class is named · `—` it is not · `!` a surface points the other way.

The **eval** column counts only cases that test *routing* — category `should_trigger`
with a query that does **not** already say "run this through the pipeline". A prompt
carrying the invocation tests obedience, not reach; those ids are marked `(expl.)` and
do not count.

| # | Request class | Example | Trigger | Mode | Doctrine in the bundle | Eval | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | Feature build | «добавь X» | ✓ | — | `stages.md` | **TRIG-03** · TRIG-01 (expl.) | routed |
| 2 | Defect fix | «починить» | ✓ | — | `stages.md` | — · INSTR-06 (expl.) | named, untested |
| 3 | Refactor | «рефактор» | ✓ | — | `stages.md` | — · AMB-01 is `ambiguous` | named, untested |
| 4 | Migration | «миграция» | ✓ | — | `stages.md` | — · TRIG-02 (expl.) | named, untested |
| 5 | Integration | «интеграция» | ✓ | — | `stages.md` | — | named, untested |
| 6 | Rewrite | «перепиши» | ✓ | — | `stages.md` | **TRIG-04** | routed |
| 7 | Adoption | «внедрить» | ✓ | — | `adoption.md` | — | named, untested |
| 8 | Hardening | «харденинг» | ✓ | — | `stages.md` | — · INSTR-07 (expl.) | named, untested |
| 9 | Docs audit | «проверь документацию» | — | ✓ `setup` | `setup.md` | **TRIG-06** | routed |
| 10 | Unverified sweep | «что накопилось непроверенного» | — | ✓ `checkup` | `exposure.md` | **TRIG-05** | routed |
| 11 | **Think it through** | «продумай фичу» | — | — | partial — stages 2–3 exist, **no stop-early contract** | — | **unrouted** |
| 12 | **Audit as the task** | «сделай аудит» | — | ! `setup` = docs only | **yes** — `audit.md:350` says an audit may *be* the whole task | — | **doctrine orphaned** |
| 13 | **Bug hunt** | «проверь ошибки» | — | — | **none** | — | **unrouted, no home** |
| 14 | **Production check** | «проверь продакшен» | — | — | partial — stage 8 in-run; `deploy-targets.md:114` has the commands | — | **unrouted** |
| 15 | **Logs / observability** | «посмотри логи» | — | — | **not a harvest source** (§3) | — | **no input path** |
| 16 | **Open a PR** | «сделай PR» | — | — | inside stage 7 only — `stages.md:400`, `conventions.md:125` | — | **unrouted** |
| 17 | **Review a PR** | «проверь PR» | — | — | `review.md` — bound to stage 7 of a run | — | **unrouted** |
| 18 | Dependency upgrade | «обнови зависимости» | — | — | none specific | — | **unrouted** |
| 19 | Incident / hotfix | «упало в проде, срочно» | — | — | short-path triage (`stages.md:143`) is the nearest thing | — | **unrouted** |
| 20 | Performance | «ускорь экспорт» | — | — | none specific | — | **unrouted** |
| 21 | Flaky test | «тест мигает» | — | — | none specific (`B-006` is one instance) | — | **unrouted** |
| 22 | Add tests to existing code | «покрой тестами» | — | — | `tdd.md` — bound to stages 5–6 | — | **unrouted** |
| 23 | Release / version bump | «выпусти релиз» | — | — | `conventions.md` release block | — | **unrouted** |
| 24 | Question about code | «что делает этот regex» | — | — | — | NOTRIG-01/03/05 | excluded **on purpose** |
| 25 | Typo / one-liner | «поправь опечатку» | — | — | — | NOTRIG-02 | excluded **on purpose** |

**Counts, and the second one is the sharper of the two.**

- **10 of 25** classes are named by a trigger word or a mode. 13 are not; 2 are excluded
  deliberately and correctly.
- **The suite tests implicit routing with four cases.** Six are `should_trigger`; two of
  those (`TRIG-01`, `TRIG-02`) already carry the invocation. Of the four that remain,
  two are the no-task modes. So **build work is routed-and-tested by exactly two
  cases** — `TRIG-03` (a feature, in English) and `TRIG-04` (a rewrite, in Russian).
  Six of the eight build nouns are **named but never tested without being told**.
- **Thirteen classes have no eval query of any kind.** The single near-hit is `INSTR-07`
  — "harden the auth middleware, **and review it properly**" — a review inside a build
  task, and an explicit invocation besides.

The gap between *named* and *tested* matters here more than usual: `AMB-01` ("clean up
the error handling in the payments module") is filed `ambiguous` on purpose, which is
the project admitting it does not know how that sentence should route. That is one
sentence away from «проверь ошибки».

## 3. Two findings that are not "a missing word"

### 3a. The exclusion clause points away from work the bundle has doctrine for

`Not for: … explaining or reading code`. Classes 12–17 all *begin* by reading — an
audit, a bug hunt, a production check, a PR review. The sentence that keeps the pipeline
off a question also keeps it off findings-shaped work, and `audit.md:350` explicitly
says an audit may be the whole task. **Doctrine and routing disagree, and the routing
surface is the one an agent reads first.**

This is the shape v1.38.0 named as `F-01` — `setup` and `checkup` were invisible in
every browsable surface while fully documented. Same class, one layer up: the rule
exists, the **name you would say out loud** does not.

### 3b. Runtime observability is not a source

`knowledge-sources.md` ledgers **ten** sources — code, code graph, host agent docs,
domain docs, decision register, task register, product/UX docs, pipeline history, retro
(+archive), wiki, other doc repos, hosted doc systems. All of them are **written
artefacts**. Logs, traces, error trackers and dashboards appear nowhere in it; the only
runtime reads in the whole bundle are `artifacts.md:144` (stage-8 notes, explicitly *"in
the run, not a committed file"*) and `deploy-targets.md:78,114` (a per-platform log
command inside the runbook).

So «сходи посмотри логи» has no row to be. A run cannot cite what it saw in production
as a source, cannot date it, and cannot mark it stale — which is the whole contract the
other ten sources are held to.

## 4. Companions are bound to stages, never to request classes

`companion-skills.md` maps **stage → doctrine** and **skill → the stage it serves**:
super-ux at stage 3, sheleg-design at stage 3, context7 at stage 1, Figma at stage 3,
obsidian-wiki at stages 0 and 9. Correct, and it answers *"I am at stage 3, what do I
reach for?"*

It never answers the question an operator actually opens with: *"I want an audit / a bug
hunt / a PR review — what runs, and what does it pull in?"* A request class has no row,
so nothing binds «проверь ошибки» to `systematic-debugging`, «сделай аудит» to
`audit.md`'s ladder, or «проверь PR» to `review.md`'s reviewer contract.

## 5. What this measurement did not look at

- **Whether a model routes any of these sentences.** Vocabulary is not behaviour; see
  the scope note and `B-002`.
- **The other routers' vocabularies** (`super-ux`, `copywriting`, `sheleg-design`,
  `make-skill`, `agent-sync`) — a class unrouted here may be correctly owned elsewhere,
  and this pass did not check theirs.
- **The host's global `CLAUDE.md`**, which carries its own copy of the boundary and was
  read once, not diffed against this table.

Filed as `B-046` … `B-051`.
