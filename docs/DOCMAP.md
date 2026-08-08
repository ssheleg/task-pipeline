# Doc map — task-pipeline

The four questions of [`references/documentation.md`](../plugins/task-pipeline/skills/task-pipeline/references/documentation.md),
answered for **this** repository. Written by the brownfield walkthrough in
[`references/adoption.md`](../plugins/task-pipeline/skills/task-pipeline/references/adoption.md),
applied to the skill that ships it.

## Regime

`governed` — since 2026-08-03, run `default-routing-adoption`. Governance scales by
**volume**, never by dropping rules: this repository has few decisions and they are
long-lived, so its register is a changelog rather than a table of ids.

## Registers

| Register | File | ID scheme | Append-only? | Guarded? |
|---|---|---|---|---|
| Decisions | `CHANGELOG.md` (what changed **and why it mattered**) + `docs/superpowers/specs/` (the design record per run) | version headings `vX.Y.Z` + dated run slugs | yes — a released section is never rewritten | no (single maintainer) |
| Open questions | none | — | — | — |
| Lessons | `docs/superpowers/retro.md` — standing instructions capped at ten | `R-NNN` | pruned, never silently | no |

**No `docs/DECISIONS.md` is created here, deliberately.** One decision home per
project: the CHANGELOG already carries every decision with its reason and its
commit, and a second register would be the fork the SSOT rule exists to prevent.
Seeding one would make this map's first act a violation of the rule it publishes.

## Single source of truth

| Fact | Home | Everything else |
|---|---|---|
| The stage list, its ids, names and gate types | `pipeline.example.json` | `SKILL.md`'s table and `references/stages.md` are compared against it mechanically |
| Each stage's doctrine | `references/<stage>.md` | `SKILL.md` links, never restates |
| The enforced invariants | `test/validate.py` | `CONTRIBUTING.md` → *The invariants* describes them; the code decides |
| What a release changed | `CHANGELOG.md` | `README.md` describes the current state, not the history |
| Risk posture and registry entry | `SKILL-CARD.md` | — |
| Behavioural evidence | `evals/RESULTS.md` | never restated as "tested" anywhere else |

## Propagation matrix

Three true rows beat twenty imported ones. Extended when a new class appears.

| Change type | Update these | Checked by |
|---|---|---|
| **A new document, rule or guard** — the change type this repository makes most often | `SKILL.md` (doctrine table + references list) · `README.md`'s map · `references/portability.md`'s manifest · `cursor/rules/task-pipeline.mdc` when it changes how an agent behaves · `CONTRIBUTING.md` when it adds an enforced invariant · `templates/README.md` when it is a template | `test/validate.py` — the reach guard, the manifest guard and the invariant-citation guard; the Cursor rule is **`review`**, because no check can decide whether a change alters agent behaviour in a foreign project |
| A stage's id, name or gate type | `pipeline.example.json`, `SKILL.md` table, `references/stages.md`, that stage's doctrine file | `test/validate.py` — cross-surface comparison |
| **A change to the config contract** (`pipeline.schema.json`) — added 2026-08-04, run `run-continuity`, when the matrix was walked for a schema change and had no row for one | `pipeline.example.json` (the example must **demonstrate** the new field, not merely permit it), `SKILL.md`'s config paragraph, `README.md`, and the schema's own `description` — which is where the reason a field is **absent** has to live, or the next contributor adds it back as an oversight | `test/validate.py` — the example is validated against the schema, plus the guard that the example sets the field explicitly |
| A new or changed guard | `test/validate.py`, a negative self-test in `.github/workflows/validate.yml`, `CONTRIBUTING.md` → *The invariants*, `test/negatives.py` floor | `npm run test:all` + the invariant-count review |
| A user-visible capability, install path or stage | `README.md`, `CHANGELOG.md`, `cursor/rules/task-pipeline.mdc`, and **every** version surface — `package.json`, `.claude-plugin/marketplace.json`, `plugins/task-pipeline/.claude-plugin/plugin.json`, the top `CHANGELOG.md` heading, `SKILL-CARD.md`'s Version row | `test/validate.py` — blurb/final-stage plus the version-sync check, which enforces all five and caught this row calling them "the four version manifests" on 2026-08-08 |
| A reference file's headings | that file's `## Contents` list | `test/validate.py` — Contents-vs-headings comparison |
| A number stated in a living document | recompute it, or delete it | `test/validate.py` — **the claim registry**: one row per claim class, each naming the pattern that recognises the claim, the command that computes the truth, and the incident that earned the row. Reads digits **and** word forms; a quoted number is a citation and exempt; every class prints `ok`/`dormant` beside the verdict. A count of an enumeration inside one sentence is not computable from outside it — those are **deleted**, not gated |
| Anything a run got wrong | `docs/superpowers/retro.md` (stamp → prune → entry, with commits) | `review` — no check can decide whether a run diverged |

## Gates

| Gate | Command | When | Blocking? |
|---|---|---|---|
| Structure + doctrine | `npm test` | before every commit | yes |
| The guards' own proof | `npm run test:all` | before every tag | yes |
| Eval suite shape | `python3 evals/run.py` | when the suite changes | yes |
| Behavioural evals | manual, per model | before promoting a version | **not automated** — see `evals/RESULTS.md` |

**No `scripts/check-docs.sh` is seeded here.** The walkthrough's step 2 says *seed
what is missing* — and what was missing was this map, not another script. `npm test`
already resolves every relative link, checks every section-qualified citation, and
computes every stated count over the same markdown. A second gate over one corpus is
a duplicate, and a duplicate that disagrees is worse than either half.

## Ratchets

| Ratchet | Home — the one place its value lives | Read it with |
|---|---|---|
| Standing instructions (hard cap 10) | `docs/superpowers/retro.md` → *Standing instructions* | `grep -cE '^\| R-[0-9]+' docs/superpowers/retro.md` |
| Dated eval runs, and the blind/self-observed split | `evals/RESULTS.md` → *Ratchet* | `python3 evals/run.py` |
| Structural guards proven against a planted defect | `.github/workflows/validate.yml` | `npm run test:all` |
| Which claim classes are armed vs dormant | `test/validate.py` → the claim registry | `npm test` — printed beside the verdict |
| Carry-over rows of a run | that run's `…-carryover.md` | the run's own gate verdicts |

**This table names homes and commands, never values.** It used to carry the numbers,
and on 2026-08-08 all three had gone stale — it claimed two standing instructions
against four in the retro, and zero dated eval runs against the one `evals/run.py`
counts. A ratchet copied into a second document is two ratchets, and the copy nobody
runs is the one people read. Canon 3, applied to this map itself.

The behavioural rows are the honest state of this skill's evidence, pointed at from
here so a green structural suite is never read as "the skill is known to work".

## Navigation

- Every `references/*.md` is linked **directly** from `SKILL.md` — one level deep, so
  a partial read never hides a file behind another file.
- Every reference over 100 lines opens with a `## Contents` list, and the list is
  compared against that file's own headings rather than trusted.
- A section-qualified citation names a section that exists; the link checker proves
  the file resolves, the citation guard proves the pointer is not false.
- Indexes link and never restate a rule.
