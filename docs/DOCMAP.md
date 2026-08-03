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
| A stage's id, name or gate type | `pipeline.example.json`, `SKILL.md` table, `references/stages.md`, that stage's doctrine file | `test/validate.py` — cross-surface comparison |
| A new or changed guard | `test/validate.py`, a negative self-test in `.github/workflows/validate.yml`, `CONTRIBUTING.md` → *The invariants*, `test/negatives.py` floor | `npm run test:all` + the invariant-count review |
| A user-visible capability, install path or stage | `README.md`, `CHANGELOG.md`, `SKILL-CARD.md`, the four version manifests, `cursor/rules/task-pipeline.mdc` | `test/validate.py` — blurb/final-stage and four-way version checks |
| A reference file's headings | that file's `## Contents` list | `test/validate.py` — Contents-vs-headings comparison |
| A number stated in a living document | recompute it | `test/validate.py` — guard-count comparison |
| Anything a run got wrong | `docs/superpowers/retro.md` (prune → stamp → entry, with commits) | `review` — no check can decide whether a run diverged |

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

| Ratchet | Where | Current | Set on |
|---|---|---|---|
| Standing instructions | `docs/superpowers/retro.md` | 2 of a hard cap of 10 | 2026-08-03 |
| Models exercised by the eval suite | `evals/RESULTS.md` | **0 of 3** | 2026-08-03 |
| Dated eval runs recorded | `evals/RESULTS.md` | **0** | 2026-08-03 |

The bottom two are the honest state of this skill's behavioural evidence, printed
here so a green structural suite is never read as "the skill is known to work".

## Navigation

- Every `references/*.md` is linked **directly** from `SKILL.md` — one level deep, so
  a partial read never hides a file behind another file.
- Every reference over 100 lines opens with a `## Contents` list, and the list is
  compared against that file's own headings rather than trusted.
- A section-qualified citation names a section that exists; the link checker proves
  the file resolves, the citation guard proves the pointer is not false.
- Indexes link and never restate a rule.
