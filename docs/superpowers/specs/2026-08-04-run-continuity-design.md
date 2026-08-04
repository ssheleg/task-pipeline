# Design — run continuity

**Run:** `run-continuity` · 2026-08-04 · brief:
[`…-brief.md`](2026-08-04-run-continuity-brief.md) · 13 REQ rows

Locks every contract stage 5 implements. A zero-context implementer reads this
file and nothing else.

## Contents

- The problem, in one paragraph
- Contract 1 — the `run` block
- Contract 2 — `references/continuity.md`
- Contract 3 — the surface edits
- Contract 4 — the four guards
- Contract 5 — the negative self-tests
- Contract 6 — the global rule
- Global constraints
- REQ → contract map
- Self-review

## The problem, in one paragraph

Two rules the operator repeats by hand every run. The first — *walk the task list
one item per iteration without asking permission between items* — **already exists**
as doctrine, at [`build.md`](../../../plugins/task-pipeline/skills/task-pipeline/references/build.md),
and does not work, for two compounding reasons: it lives inside stage 5 so no other
stage hears it, and prose cannot survive the turn boundary — on Claude Code only a
scheduled re-invocation can. The second — *near the end of the context window, stop
starting new work, make the ledgers true, and continue* — does not exist at all, and
its absence shows up as the opposite failure: the run announcing that context is
nearly spent while the window is largely free, because an estimate was presented as
a measurement. The two are one mechanism: **the loop is what makes the context rule
necessary**, since without a loop the run stops at the turn boundary anyway.

## Contract 1 — the `run` block

Added to `pipeline.schema.json` under `properties`, beside `stages` and `release`.
**`loop` only** — `contextBudget` is deliberately absent (brief → D-4a).

```json
"run": {
  "$ref": "#/definitions/run"
}
```

And in `definitions`:

```json
"run": {
  "type": "object",
  "additionalProperties": true,
  "description": "Optional run-wide pacing. Omit the object and every field defaults OFF: silence arms nothing and authorises nothing, the same floor deploy authorization uses. There is deliberately no context-budget field — the threshold is not measurable from inside a run, so a field accepting a percentage would validate a number that can never be honoured; that rule is unconditional doctrine in references/continuity.md instead.",
  "properties": {
    "loop": {
      "type": "object",
      "required": ["mode"],
      "additionalProperties": true,
      "description": "Whether the run advances item-by-item without a discretionary check-in. NEVER collapses a manual gate or an outward action — a generic flag is not a specific authorization.",
      "properties": {
        "mode": {
          "enum": ["off", "interval"],
          "description": "off (the default when absent) = the run pauses between items as it always did. interval = the run is armed with the harness's own loop primitive and advances one item per fire."
        },
        "interval": {
          "type": "string",
          "pattern": "^[0-9]+[smhd]$",
          "description": "Required when mode is 'interval'. Must divide its unit cleanly (5m, 10m, 2h — not 7m or 90m); a value that does not is rounded to the nearest that does, and the rounding is stated out loud. Pick the shortest interval longer than a typical item."
        },
        "command": {
          "type": "string",
          "description": "How the harness arms it, e.g. '/loop'. Harness-specific and therefore project-recorded rather than assumed: on a harness with no loop primitive this field is omitted and the mode degrades to prose discipline plus the ledger, said out loud."
        }
      }
    }
  }
}
```

**`pipeline.example.json`** gains, at the top level beside `release`:

```json
"run": {
  "loop": { "mode": "off", "interval": "5m", "command": "/loop" }
}
```

Explicitly `off`, carrying the two fields it would use when on — the example
**demonstrates** the default instead of relying on its absence (REQ-010).

## Contract 2 — `references/continuity.md`

New file. Over 100 lines, therefore a `## Contents` list that matches its `## `
headings **exactly and in order** (the validator compares them literally).

**Headings, in this order:**

```
## Contents
## The limit, before the capability
## Part 1 — the loop
## Arming it on Claude Code
## Other harnesses, and honest degradation
## What one iteration means
## Parked at a manual gate
## Part 2 — the context budget
## The evidence rule
## What happens at the signal
## The flush is not a new document
## Rationalizations
```

**Two sentences are contractual** — the clause guard (Contract 4, G3) checks for
these substrings **after normalising whitespace**, so they must appear verbatim
apart from line breaks:

**Amended at stage 5, from measuring the guard before shipping it.** The first
sentence is 74 characters and wraps at the file's 80-column style, so a
line-oriented search finds nothing and would reject correctly formatted prose.
This repository has already paid for that lesson once — the citation guard
normalises whitespace because six wrapped citations were reported as defects.
G3 normalises the same way, and its negative self-test therefore plants a
**deletion**, never a re-wrap.

1. `never announce that the context is nearly spent without one of those signals`
2. `Claude Code only`

**What each section must establish:**

| Section | Must say |
|---|---|
| The limit, before the capability | The mode never collapses a `manual` gate or an outward act; default is off; silence arms nothing. Placed first, following `hooks.md`'s precedent |
| Part 1 — the loop | On: no discretionary check-in anywhere in the run — stage-5 plan tasks, `auto` gates, the per-module program loop, the acceptance→retro tail. Stops only at a `manual` gate, a `BLOCKED` it cannot resolve, a genuine ambiguity, or completion. It **extends** `build.md`'s stage-5 rule to the run; it does not replace or weaken it |
| Arming it on Claude Code | `/loop <interval> <invocation>`; the interval must divide its unit cleanly and a rounding is stated; the job is **session-only** and **auto-expires after 7 days**, both said when arming, because a loop that dies quietly on day eight is worse than one never armed; where `run.loop.mode` is `interval` the preflight arms it and prints the job id and the cancel command, since the config **is** the recorded authorization |
| Other harnesses, and honest degradation | `/loop` is `Claude Code only`. No primitive → the mode is prose discipline plus the ledger, and the run says it is unarmed rather than implying it is |
| What one iteration means | One item taken to its gate. **The scheduler enqueues only while the harness is idle, never mid-query — so a fixed interval cannot interrupt an unfinished item.** The build ledger is the *second* line, for a fire that lands after a context loss: `Task <N>: complete` is the only DONE marker. Doctrine must not claim the ledger is what makes the interval safe |
| Parked at a manual gate | A fixed interval firing into a `manual` gate is a nag, and a nagged operator learns to ignore the loop. The run **cancels its own loop job** on parking and prints the re-arm command beside the gate |
| Part 2 — the context budget | Near the end of the window: finish the item in flight, **start no new one**, make the ledgers true, then continue. Not stop. Crossing the boundary mid-item is what loses work |
| The evidence rule | The rule fires **only** on a harness signal — a compaction warning, a `PreCompact` hook — or the operator saying so. No tool returns the number, so an estimate presented as a measurement is the failure `learned.md` rule 8 names. Contains sentence 1 verbatim |
| What happens at the signal | The four acts in order, and the one prohibition: do not begin an item you cannot finish inside the remaining window |
| The flush is not a new document | It makes existing artifacts true — build ledger, carry-over ledger, the brief's REQ statuses, the TaskList. A summary written for the compactor is a fourth copy of the truth that nobody updates |
| Rationalizations | The excuse/reality table every doctrine file ends with |

## Contract 3 — the surface edits

Walked from `docs/DOCMAP.md`'s propagation matrix, row *a new document, rule or
guard*, plus the new row this run adds (REQ-011).

| File | Edit |
|---|---|
| `SKILL.md` | Doctrine table: a row `run-wide · Continuity (the loop + the context budget)` → `references/continuity.md`. References list: one line. *How to run* step 1: the preflight block names the run mode beside the model decision |
| `references/stages.md` | Stage-0 detail names the run-mode decision; a pointer to `continuity.md` |
| `references/grill.md` | Autonomy sweep gains a `run-wide loop` row: mode, interval, and what it does not collapse |
| `references/build.md` | The *Continuous execution* paragraph gains one sentence naming its scope (within a stage-5 execution) and pointing at `continuity.md` for the run-level mode. **The existing rule is not weakened** |
| `templates/brief.md` | Autonomy table gains the matching `run-wide loop` row |
| `README.md` | The doctrine map gains the row; the guard counts are recomputed |
| `references/portability.md` | The manifest gains rows for the loop mode and the context rule, homed at `references/continuity.md` |
| `cursor/rules/task-pipeline.mdc` | The rule changes how an agent behaves in a foreign project, so it is in scope — add the loop-mode default-off line and the context evidence rule. Self-contained, **no relative links** |
| `CONTRIBUTING.md` | *The invariants* gains the new ones, each citing its guard as `*(guard: \`<literal>\`)*` where the literal appears in `test/validate.py` |
| `docs/DOCMAP.md` | New propagation row: **a change to the config contract** (REQ-011) |
| `SKILL-CARD.md` | Guard counts recomputed |
| `CHANGELOG.md` | A `## v1.11.0` section: what changed and why it mattered |
| `package.json`, `.claude-plugin/marketplace.json`, `plugins/task-pipeline/.claude-plugin/plugin.json`, `CHANGELOG.md` heading | Four-way version sync → **1.11.0** |

## Contract 4 — the four guards

Each is a block in `test/validate.py` in the file's existing style: a comment
explaining the failure it prevents, then the check, then `fail(...)`. The **fail
message literals below are contractual** — `CONTRIBUTING.md` cites them and a guard
asserts the citation resolves.

| id | Guard | Fail message contains | REQ |
|---|---|---|---|
| G1 | The `run` block exists in the schema **and** the example sets `loop.mode` explicitly | `pipeline.example.json: no explicit run.loop.mode` | 001, 010 |
| G2 | The continuity reach guard — `SKILL.md`, `references/grill.md`, `references/build.md`, `references/stages.md` and `templates/brief.md` must each name `continuity.md` | `does not name continuity.md — a run-wide rule no stage has heard of` | 003, 004 |
| G3 | The continuity clause guard — both contractual sentences present in `references/continuity.md` | `references/continuity.md: missing the contractual clause` | 005, 006, 013 |
| G4 | The seeded-template link guard — copy each `templates/*.md` into a scratch tree at the destination its doctrine seeds it to, and resolve every relative link from there | `resolves only from templates/, not from the destination it is seeded to` | 012 |

**G4's destination table** is the contract, not a guess:

| Template | Seeded to |
|---|---|
| `brief.md`, `carryover.md` | `docs/superpowers/specs/` |
| `retro.md`, `retro-archive.md` | `docs/superpowers/` |
| `context.md` | repository root |
| `adr.md` | `docs/adr/` |
| `docmap.md`-family (`docmap.md`, `decisions.md`, `open-questions.md`) | `docs/` |
| `routing-rule.md`, `hooks.example.json`, `docgate.sh`, `README.md` | not seeded as documents — excluded, and the exclusion is written in the guard's comment |

G4 fixes the defect it was born from: `templates/carryover.md`'s
`../references/audit.md` becomes a link that resolves from
`docs/superpowers/specs/`.

## Contract 5 — the negative self-tests

One `- name: Negative self-test — …` step per guard in
`.github/workflows/validate.yml`, plus one extra for G3's second clause. **Five
new steps**, taking the workflow from 63 to **68**. Every corruption is planted in
**python, never `sed -i`** — the validator rejects `sed -i` and the workflow's own
guard rejects a test that contains the literal.

| Step | Plants |
|---|---|
| G1 | `pipeline.example.json` with `run.loop.mode` deleted |
| G2 | `references/build.md` with every mention of `continuity.md` stripped |
| G3a | `references/continuity.md` with the evidence sentence removed |
| G3b | `references/continuity.md` with `Claude Code only` removed |
| G4 | `templates/brief.md` with a `../references/audit.md`-shaped link planted |

`test/negatives.py` → `MIN_EXPECTED` rises **63 → 68**. The three living documents
that state a guard count (`README.md`, `SKILL-CARD.md`, `evals/RESULTS.md`) are
updated to whatever the workflow then defines — the existing compute-never-restate
guard enforces the derivation, so the number is read from the workflow, not typed.

## Contract 6 — the global rule

`~/.claude/CLAUDE.md` gains one section, **shown as a diff and confirmed before it
is written** (REQ-009). It is the context half only — the loop half is
project-recorded and does not belong in a global file.

```markdown
## Контекст сессии — правило порога

- **Не объявляю контекст исчерпанным без сигнала.** Процент израсходованного
  контекста мне не виден: нет инструмента, который его возвращает. Правило
  срабатывает ТОЛЬКО от наблюдаемого события — предупреждение харнеса о близкой
  компактификации, сработавший `PreCompact`, или твои слова. Без такого события
  фраза «контекст почти исчерпан, начни новую сессию» — выдача оценки за
  измерение, и она запрещена.
- **Сработал сигнал — не останавливаюсь, а уплотняюсь:** доделываю то, что уже
  начато, **новую задачу не начинаю**, привожу в правду то, что переживёт
  компактификацию (леджеры, статусы, план), и иду дальше.
- Уплотнение — это не новый документ-саммари, а обновление уже существующих
  артефактов. Четвёртая копия правды, которую никто не поддерживает, хуже, чем
  её отсутствие.
```

## Global constraints

- Line-wrap prose at ~80 characters.
- Never let a wrapped line begin with `>` — it becomes a blockquote.
- No vendor model ids anywhere in the shipped skill.
- `npm test` after every file group; `npm run test:all` before the tag.
- Corrupt files in **python, never `sed -i`**.
- R-002 binds: any batch of edits returning an error gets **every** edit in that
  batch re-verified, not only the one that errored.

## REQ → contract map

| REQ | Contract |
|---|---|
| 001 | Contract 1 · G1 |
| 002 | Contract 2 · the existing reach/README/manifest guards engage automatically |
| 003 | Contract 3 (SKILL.md, grill.md, brief.md) · G2 |
| 004 | Contract 3 (build.md, stages.md) · G2 |
| 005 | Contract 2 sentence 1 · G3a |
| 006 | Contract 2 sentence 2 · G3b |
| 007 | Contract 5 |
| 008 | Contract 3 (README, portability, cursor, CONTRIBUTING, SKILL-CARD, CHANGELOG, four-way sync) |
| 009 | Contract 6 |
| 010 | Contract 1 (example) · G1 |
| 011 | Contract 3 (DOCMAP row) |
| 012 | Contract 4 G4 |
| 013 | Contract 2 (*Parked at a manual gate*) · G3 |

## Self-review

- **Every REQ maps to a contract** — the table above, 13 of 13.
- **No placeholders.** Every guard has its literal, every template its
  destination, every file its edit.
- **Names are consistent** across contracts: `run.loop.mode`, `continuity.md`,
  G1–G4.
- **Nothing is weakened.** `build.md`'s continuous-execution rule keeps its force
  and gains a scope; the deploy floor is restated, not relaxed.
- **One honest gap, stated rather than hidden:** REQ-009 lands outside the
  repository and no guard here can prove it. Acceptance will mark it verified by
  eye, not by check.
