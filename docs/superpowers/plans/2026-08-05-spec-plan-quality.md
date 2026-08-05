# Spec and plan quality — implementation plan

> **For agentic workers:** execute task-by-task under the task-pipeline stage-5
> build doctrine — one implementer per task, a review after each (spec compliance,
> REQ satisfied, code quality). Steps use `- [ ]` checkboxes.
> Statuses: `DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`.

**Goal:** wire four stranded rules into the stages that must obey them, add the one
genuinely missing checkpoint, and make both self-reviews leave a committed trace of
computed numbers.

**Architecture:** additive edits to two doctrine files plus `learned.md`'s stage map
and two gate-criteria lines, backed by three guards that check the files carry the
items — the only thing checkable from inside this repository.

**Tech stack:** markdown doctrine, Python 3 (`test/validate.py`), GitHub Actions YAML.

**Spec:** `docs/superpowers/specs/2026-08-05-spec-plan-quality-design.md`

## Global constraints

- Prose wraps at ~80 columns; no wrapped line begins with `>`.
- `npm test` green after **every** task; `npm run test:all` before any tag.
- **The hygiene gate runs in diff mode after every task** (v1.12.0).
- Corrupt fixtures in **Python**, never `sed -i`. Unique `rm -rf`-guarded scratch dirs.
- R-001 plant-landing proof; R-002 batch re-verification; **R-003 sibling sweep** —
  `spec.md` and `planning.md` are siblings.
- Every reference over 100 lines keeps `## Contents` in step with its headings.

## Execution order

| Group | Tasks | Runs after |
|---|---|---|
| A | 1 (spec.md), 2 (planning.md), 3 (learned.md + stages.md) | — |
| B | 4 (guards + negative tests) | A |
| C | 5 (propagation + version) | B |

Group A's three tasks touch disjoint files and could run in parallel; **R-003 makes
1 and 2 sequential in practice** — an item added to one is a question asked of the
other, and that question cannot be asked concurrently.

---

### Task 1: spec.md — four new self-review items and the section

**Depends:** — · **Implements:** REQ-001, REQ-002, REQ-003, REQ-004

**Files:** Modify `plugins/task-pipeline/skills/task-pipeline/references/spec.md`

**Interfaces:** Produces the `## Self-review` six-line shape that task 2 reuses
verbatim.

**Definition of done:** items 7–10 present under the existing six; the
`## Self-review` shape documented; `## Contents` still matches the headings;
`npm test` green; hygiene gate green in diff mode.

- [ ] **Step 1: run** `npm test` and `bash …/hygiene.sh` → baseline green.
- [ ] **Step 2: append items 7–10** exactly as spec contract 2 words them.
- [ ] **Step 3: add the `## Self-review` required-shape block** (contract 1).
- [ ] **Step 4: run** `npm test` → PASS, and `HYGIENE_BASE=HEAD bash …/hygiene.sh` → exit 0.
- [ ] **Step 5: commit** `docs(spec-doctrine): the spec reads its checks and its decisions back`.

---

### Task 2: planning.md — two new items and the same section

**Depends:** [1] · **Implements:** REQ-005, REQ-006

**Files:** Modify `plugins/task-pipeline/skills/task-pipeline/references/planning.md`

**Interfaces:** Consumes task 1's `## Self-review` shape — **identical wording**, so
one habit covers both files.

**Definition of done:** items 7–8 present; the same section shape; `## Contents`
in step; `npm test` green; hygiene gate green.

- [ ] **Step 1: re-read task 1's items** and ask R-003's question: does either of
      spec.md's new items also belong here? *(Item 7 does, reworded for DoDs; items
      8–9 do not — planning settles nothing, which `planning.md` already states.)*
- [ ] **Step 2: append items 7–8** and the section shape.
- [ ] **Step 3: run** `npm test` → PASS; hygiene diff → exit 0.
- [ ] **Step 4: commit** `docs(plan-doctrine): a DoD may not name a command that does not exist`.

---

### Task 3: learned.md's stage map and the two gate criteria

**Depends:** — · **Implements:** REQ-007, REQ-008

**Files:** Modify `references/learned.md`, `references/stages.md`

**Definition of done:** rule 14 listed at stages 3 and 4 as well as 9; §3 and §4
gate criteria name the section; `npm test` green.

- [ ] **Step 1: run** `npm test` → baseline.
- [ ] **Step 2: add the two stage-map rows** (spec contract 4).
- [ ] **Step 3: extend §3 and §4 gate criteria** (spec contract 5).
- [ ] **Step 4: run** `npm test` → PASS.
- [ ] **Step 5: commit** `docs(doctrine): rule 14 binds the stages that write the targets`.

---

### Task 4: three guards and their negative self-tests

**Depends:** [1, 2, 3] · **Implements:** REQ-009

**Files:** Modify `test/validate.py`, `.github/workflows/validate.yml`,
`test/negatives.py`

**Definition of done:** each guard **watched failing** on a planted defect whose
landing was asserted first; `python3 test/negatives.py` green; `MIN_EXPECTED`
recomputed by counting the workflow.

- [ ] **Step 1: plant first** — delete item 7 from a scratch copy of `spec.md`, run
      `npm test`, confirm it **passes** (the guard does not exist yet).
- [ ] **Step 2: write the three guards**, placed **above** `validate.py`'s
      `if errors: … sys.exit(1)` block — v1.12.0 learned that the hard way.
- [ ] **Step 3: re-run the plant** → FAIL, naming the file.
- [ ] **Step 4: add three negative self-tests**, each with a unique
      `rm -rf`-guarded `/tmp/` directory.
- [ ] **Step 5: recount** `grep -c '      - name: Negative self-test' .github/workflows/validate.yml`
      and set `MIN_EXPECTED` to that number.
- [ ] **Step 6: run** `python3 test/negatives.py` → green.
- [ ] **Step 7: commit** `test(validate): three guards for the read-backs, each probed`.

---

### Task 5: propagation and version

**Depends:** [4] · **Implements:** REQ-010, REQ-011

**Files:** `CHANGELOG.md`, `README.md`, `CONTRIBUTING.md`,
`references/portability.md`, `cursor/rules/task-pipeline.mdc`, `package.json`,
`.claude-plugin/marketplace.json`,
`plugins/task-pipeline/.claude-plugin/plugin.json`, `SKILL-CARD.md`,
`evals/RESULTS.md` (stated guard counts).

**Definition of done:** four-way sync at 1.13.0; every stated guard count
recomputed; Cursor rule self-contained with **0 relative links**;
`npm run test:all` green.

- [ ] **Step 1: run** `npm run test:all` → baseline.
- [ ] **Step 2: write the CHANGELOG section** — the diagnosis, and that the cost
      checkpoint prints rather than decides.
- [ ] **Step 3: bump the four manifests**; update the other surfaces; recompute
      every stated guard count rather than editing it by hand.
- [ ] **Step 4: run** `npm run test:all` → green; `grep -c "](\.\./\|](\./" cursor/rules/task-pipeline.mdc` → 0.
- [ ] **Step 5: commit** `docs: the read-back across every surface; v1.13.0`.

## No placeholders

Every task names exact files, exact commands and exact expected outcomes. Nothing
says "similar to task N", "add error handling", or "TBD".

## Self-review

- **REQ coverage: 11 in brief, 11 covered, difference ∅.** Union of `Implements:`
  = {001,002,003,004,005,006,007,008,009,010,011}.
- **Named checks: 6 named, 6 resolve.** `npm test`, `npm run test:all`,
  `python3 test/negatives.py`, `bash …/hygiene.sh`, `grep -c` on the workflow,
  `grep -c` on the Cursor rule — every one run at least once in this session.
- **Decisions:** read back against the brief's D1–D5 and the spec's *does not do*
  list. No contradiction. D3 said the checkpoint prints; no task makes it decide.
  `grill.md` is touched by no task.
- **Cost: 10 surfaces / 3 guards / 11 REQ** now; at stage 2 the estimate was 8/3/11.
  The two extra are `SKILL-CARD.md` and `evals/RESULTS.md`, which state guard counts
  a new guard changes — propagation, not scope growth. **Proportionate.**
- **Hygiene: 6 checks, 0 findings, 0 open.**
- **Parallel safety:** group A's tasks write disjoint files; 1 and 2 are sequenced by
  R-003, not by a file conflict.
- **Dependency truth:** task 2 consumes task 1's section shape; task 4 consumes all
  three files; task 5 consumes task 4's guard count.
- **DoD present and verifiable** on all 5 tasks.
- **Placeholders: 0 · Ambiguity: 0.**
