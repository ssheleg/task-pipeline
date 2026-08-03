# Spec — default-on routing + the adoption track

**Brief:** [`2026-08-03-default-routing-adoption-brief.md`](2026-08-03-default-routing-adoption-brief.md).
Every section carries `covers:`. This spec locks only what the brief left open:
exact section names, exact wording, the config shape, and the guard names.

## 1. `references/adoption.md` — the section contract · covers: REQ-001

Sections, in this order (the Contents guard compares the list to them):

```
Contents
Two entry conditions
A new project — the seed is the whole of it
An existing project — the register starts today
  (sub) Step 1 · Inventory
  (sub) Step 2 · Seed what is missing
  (sub) Step 3 · Baseline the ratchets  ← the step that decides adoption
  (sub) Step 4 · Build the propagation matrix
  (sub) Step 5 · Record the adoption itself
  (sub) Step 6 · Arm the gate
  (sub) Step 7 · Several agents — add the leases
Why history is not back-filled
What good looks like the day after
Rationalizations
```

**The load-bearing rule, stated once and cited by the walkthrough:** a gate that is
red on adoption day gets switched off on day two (`references/learned.md` rules 9 and 10). Therefore step 3 is not optional and not last.

## 2. Ratchet floors — the kinds · covers: REQ-002

The two floors are **different kinds**, and the comment block in
`templates/docgate.sh` must say which is which:

| Floor | Kind | Adoption value |
|---|---|---|
| `PROP_FLOOR` | **id threshold** — an entry whose number is ≥ the floor must have propagated; everything older is a counted backlog | the **next free id** |
| `RESIDUE_FLOOR` | **count** — how many unmarked citations of retired decisions are tolerated | **today's measured number** |

Both may only fall. Raising either is a decision.

## 3. The description — vocabulary and boundary · covers: REQ-003

The description keeps its shape (capability → `Use when …`, ≤1024 chars) and gains:

- **work verbs, RU + EN:** feature · fix · refactor · migration · integration ·
  rewrite · adopt · harden · фича · фикс · рефактор · миграция · интеграция ·
  доработать · починить · внедрить · перевести;
- **an explicit exclusion clause**, verbatim shape:
  `Not for: answering a question, explaining or reading code, a typo or a one-line
  edit — say "без пайплайна" / "quick" to opt out of the cycle for a task that would
  otherwise qualify.`

**Rule:** default-on widens *inside* the boundary, never through it. The exclusions
are the same three the `NOTRIG` evals encode; the two must not drift.

## 4. The routing rule in the operator's global config · covers: REQ-005

A new subsection under the existing skills rules, holding: the default (repo-changing
work routes through the pipeline when it is installed), the exclusion list from §3,
both escape phrases, and the reason the rule lives there rather than in the skill —
**a description cannot force selection; an instruction can.**

## 5. agent-sync — the binding patch · covers: REQ-006

The config example must **validate against `pipeline.schema.json`**:

| Was | Must be |
|---|---|
| `"id": "0"` (string) | `"id": 0` (integer) |
| `"title": "…"` | `"name": "…"` |
| *(absent)* | `"state": "intake" \| "spec" \| "plan" \| "dev" \| "docs-wiki" \| "acceptance"` — **required** |
| `task-pipeline:artifacts` at stage 9 | `task-pipeline:documentation`, `task-pipeline:gates` |
| gate text that replaces the pipeline's | gate text that **extends** it — agent-sync's clause appended to, never instead of, the stage's own |

`agent-sync.example.json` → `guardedFiles` gains `docs/DOCMAP.md` and
`docs/superpowers/retro.md`, with a one-line reason each.

## 6. Version floor · covers: REQ-007

`companion-skills.md`'s agent-sync row states **≥ 1.3.0**, because `finish` — the
command the stage-10 close-out names — did not exist before it.

## 7. Dogfooding this repository · covers: REQ-008

`docs/DOCMAP.md` records D5 (decision home = `CHANGELOG.md` + `docs/superpowers/specs/`,
no second register), the SSOT rows this repo actually has, its propagation matrix,
its gate commands (`npm test`, `npm run test:all`) and its ratchets. A seeded
`scripts/check-docs.sh` runs green with floors baselined at today.

## 8. New guards · covers: REQ-001, REQ-003, REQ-004

| Guard | Fails when |
|---|---|
| `adoption-walkthroughs` | `references/adoption.md` lacks either the greenfield or the brownfield walkthrough, or never names the ratchet baseline step |
| `description-exclusions` | the description has no exclusion clause, or names an exclusion the eval suite does not encode |
| *(existing, extended)* `evals` | the suite loses a category or an exclusion row |

Each needs a negative self-test watched failing (`CONTRIBUTING.md` → *Adding or
changing doctrine*).

## Self-review

Every REQ appears in a section: 001 §1 §8 · 002 §2 · 003 §3 §8 · 004 §8 · 005 §4 ·
006 §5 · 007 §6 · 008 §7 · 009 (stage 10, no contract to lock). No section covers
nothing. Names consistent with the files they touch.
