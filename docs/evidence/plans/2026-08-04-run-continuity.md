# Plan — run continuity

**Spec:** [`…-design.md`](../specs/2026-08-04-run-continuity-design.md) ·
**Brief:** [`…-brief.md`](../specs/2026-08-04-run-continuity-brief.md)

Eight tasks. This run is **inline** (no subagents — the operator's standing
instruction for this session), so the fan-out groups below describe dependency
order rather than concurrency, and every self-review is declared as weaker
evidence than a fresh reviewer's.

## Contents

- Dependency graph
- T1 — the `run` block
- T2 — `references/continuity.md`
- T3 — wire the doctrine into the stages
- T4 — the outer surfaces
- T5 — the four guards
- T6 — the negative self-tests
- T7 — version, changelog, recomputed counts
- T8 — the global rule
- Definition of done, whole plan

## Dependency graph

```
T1 ──┐
T2 ──┼─→ T3 ──→ T4 ──→ T5 ──→ T6 ──→ T7 ──→ T8
     │
     └─ (T1 and T2 touch disjoint files and may run in either order)
```

`depends:` — T3:[T2] · T4:[T3] · T5:[T1,T2,T3] · T6:[T5] · T7:[T6] · T8:[]

T8 depends on nothing mechanically and is last **on purpose**: it is the only
task that writes outside this repository, so it never blocks the repository work
and is the single human-confirmed step.

## T1 — the `run` block

**Files:** `plugins/task-pipeline/skills/task-pipeline/pipeline.schema.json`,
`plugins/task-pipeline/skills/task-pipeline/pipeline.example.json`

Add `"run": { "$ref": "#/definitions/run" }` to the schema's top-level
`properties`, and the `run` definition to `definitions`, both **verbatim from the
spec** → *Contract 1*. Add the `run` object to the example at top level beside
`release`, with `"mode": "off"`.

**DoD:** `npm test` green; `python3 -c "import json;json.load(open(...))"` parses
both files; `grep -c '"mode": "off"' pipeline.example.json` → 1.

## T2 — `references/continuity.md`

**File:** `plugins/task-pipeline/skills/task-pipeline/references/continuity.md`
(new)

Write the file to the spec's heading list, **in that exact order**, with a
`## Contents` list that repeats those headings verbatim minus `Contents` — the
validator compares the two literally and fails on order alone. Each section says
what the spec's section table requires. Both contractual sentences appear
verbatim:

- `never announce that the context is nearly spent without one of those signals`
- `Claude Code only`

Ends with a `Rationalizations` table, house style: the excuse an agent will
actually reach for, beside the reality.

**DoD:** `npm test` green — which at this point already exercises four existing
guards on the new file (reachability is not yet satisfiable, so T3 completes it);
the Contents-vs-headings guard passes; no line begins with `>`.

## T3 — wire the doctrine into the stages

**Files:** `SKILL.md`, `references/stages.md`, `references/grill.md`,
`references/build.md`, `templates/brief.md` (all under
`plugins/task-pipeline/skills/task-pipeline/`)

1. `SKILL.md` — doctrine table row, references-list line, and the *How to run*
   step-1 preflight block naming the run mode beside the model decision.
2. `references/grill.md` — the autonomy sweep gains a `run-wide loop` row.
3. `templates/brief.md` — the matching row in its autonomy table.
4. `references/build.md` — one sentence scoping *Continuous execution* to within
   a stage-5 execution and pointing at `continuity.md`. **Do not weaken the
   existing paragraph**; it keeps its force.
5. `references/stages.md` — stage-0 detail names the run-mode decision.

**DoD:** `npm test` green, including the reachability guard now satisfied for
`continuity.md`; `grep -l continuity.md` returns all five files.

## T4 — the outer surfaces

**Files:** `README.md`, `references/portability.md`,
`cursor/rules/task-pipeline.mdc`, `CONTRIBUTING.md`, `docs/DOCMAP.md`

1. `README.md` — the doctrine map gains the `continuity.md` row. (Guard counts
   are **T7's**, not this task's — same file, different task, run sequentially.)
2. `references/portability.md` — manifest rows for the loop mode and the context
   rule, homed at `references/continuity.md`.
3. `cursor/rules/task-pipeline.mdc` — the loop-mode default-off line and the
   context evidence rule. **Self-contained, no relative links.**
4. `CONTRIBUTING.md` — the new invariants, each citing its guard as
   ``*(guard: `<literal>`)*`` with a literal that appears in `test/validate.py`.
   Written **after** T5 defines the literals, or the citation guard fails →
   **this sub-step moves to T5's tail.**
5. `docs/DOCMAP.md` — the new propagation row for *a change to the config
   contract* (REQ-011).

**DoD:** `npm test` green; the README-map and manifest guards pass for
`continuity.md`; the Cursor rule contains no `](.`-shaped relative link.

## T5 — the four guards

**File:** `test/validate.py` (plus `CONTRIBUTING.md`'s citation sub-step from T4)

Add G1–G4 as blocks in the file's existing style — a comment naming the failure
each prevents, then the check, then `fail(...)` — using the **exact fail-message
literals** from the spec's guard table. G4 carries its destination table and its
exclusion list in the comment.

**DoD:** `npm test` green on a clean tree; each guard **watched failing once**
against a hand-planted defect, then restored — the planting done in python, never
`sed -i`; `CONTRIBUTING.md`'s citations all resolve.

## T6 — the negative self-tests

**Files:** `.github/workflows/validate.yml`, `test/negatives.py`

Five `- name: Negative self-test — …` steps per the spec's table. Raise
`MIN_EXPECTED` from 63 to the count the workflow then defines.

**DoD:** `npm run test:all` green; `grep -c "name: Negative self-test"` equals
`MIN_EXPECTED`; no step contains the literal `sed -i`.

## T7 — version, changelog, recomputed counts

**Files:** `package.json`, `.claude-plugin/marketplace.json`,
`plugins/task-pipeline/.claude-plugin/plugin.json`, `CHANGELOG.md`,
`SKILL-CARD.md`, `README.md`, `evals/RESULTS.md`

Four-way sync to **1.11.0**. A `## v1.11.0` CHANGELOG section written as *what
changed and why it mattered*. Every stated guard count **read from the workflow**,
never typed from memory — the compute-never-restate guard enforces it.

**DoD:** `npm run test:all` green; the four-way guard passes; the guard-count
guard passes against all three living documents.

## T8 — the global rule

**File:** `~/.claude/CLAUDE.md` — **outside this repository**

Append the section from the spec → *Contract 6*. **Show the operator the exact
addition and get confirmation before writing** (REQ-009). Nothing else in that
file is touched.

**DoD:** the operator confirmed; `grep -c "Контекст сессии — правило порога"
~/.claude/CLAUDE.md` → 1. **No repository guard covers this** — acceptance records
it as verified by eye, and says so.

## Definition of done, whole plan

`npm run test:all` green; all four new guards seen failing once; 13 of 13 REQ
traceable to a change; the branch integrated per the brief (PR into `main`,
because this changes a public contract); nothing left in the carry-over ledger
without a home.
