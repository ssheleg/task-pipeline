# Artifact hygiene — implementation plan

> **For agentic workers:** execute this plan task-by-task under the task-pipeline
> stage-5 build doctrine — one implementer per task, a review after each (spec
> compliance, REQ satisfied, code quality). Steps use `- [ ]` checkboxes.
> Implementer statuses: `DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`.

**Goal:** ship `templates/hygiene.sh` — six measured checks for agent-introduced
defects — seeded, executed by `npm test`, probed by seven negative self-tests, and
wired into stages 5, 6 and 9.

**Architecture:** one portable bash script, sibling of `templates/docgate.sh`,
carrying that file's contracts. Two modes (diff at zero tolerance, tree behind
per-check floors). The validator's existing template guards are generalised to
iterate a list of gate scripts rather than being copied.

**Tech stack:** bash 3.2, POSIX grep/awk/sed, Python 3 for fixtures and for
`test/validate.py`.

**Spec:** `docs/superpowers/specs/2026-08-05-artifact-hygiene-design.md`

## Global constraints

- macOS bash 3.2: no `grep -P`, no `sed -i`, no `readarray`, no `mapfile`, no `${var,,}`.
- Portable set only: `grep -E/-c/-n/-l`, `awk`, `sed` (no `-i`), `while read`, `[ ]`, `case`.
- Corrupt fixtures in **Python**, never `sed -i`.
- Prose wraps at ~80 columns; no wrapped line begins with `>`.
- `npm test` green after **every** task, not only at the end.
- R-001: prove a plant landed in the parsed text before touching a silent check.
- R-002: any error in a batch → re-verify every edit in that batch.
- The script **never edits a file**. It reports `file:line` and exits non-zero.
- VERDICT block last; nothing runs after it.

## Execution order

| Group | Tasks | Runs after |
|---|---|---|
| A | 1 (script skeleton + checks 1–4) | — |
| B | 2 (checks 5–6), 3 (repository fixes) | A for 2; none for 3 |
| C | 4 (validator generalisation + scratch execution) | A, B |
| D | 5 (seven negative self-tests + floor) | C |
| E | 6 (doctrine wiring), 7 (propagation + version) | D |

---

### Task 1: script skeleton, contracts, and checks 1–4

**Depends:** —

**Implements:** REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-008

- REQ-001 — the file carries the full `docgate.sh` contract.
- REQ-002 — conflict markers. REQ-003 — placeholders as line-leading markers.
- REQ-004 — unterminated fence. REQ-005 — truncation stubs.
- REQ-008 — two modes with per-check floors, counts printed.

**Files:**
- Create: `plugins/task-pipeline/skills/task-pipeline/templates/hygiene.sh`

**Interfaces:**
- Produces: env contract `HYGIENE_BASE`, `HYGIENE_FLOOR_1..6`, `HYGIENE_EXCLUDE`;
  helper functions `err`, `ok`, `dormant`; variable `FAIL`; a `VERDICT` block that
  must remain last. Task 2 appends checks 5–6 **above** the VERDICT block.

**Definition of done:** `bash -n` clean; running it on this repository exits 0 and
prints six per-check counts; the header carries `SCOPE:`, the exit-code sentence,
the portability note and the ownership sentence; `npm test` still green.

- [ ] **Step 1: write the failing check** — create the file with only the header and
  VERDICT block, then assert the contract guard would reject a missing `SCOPE:`
  (guard arrives in task 4; here assert by eye and by `grep`).
- [ ] **Step 2: run** `bash -n templates/hygiene.sh` → expect clean parse.
- [ ] **Step 3: implement checks 1–4** using the exact patterns in the spec.
- [ ] **Step 4: plant one defect per check in `/tmp` and confirm each fires**, then
  remove them and confirm exit 0 on a clean tree.
- [ ] **Step 5: commit** `feat(hygiene): the gate skeleton and checks 1-4`.

---

### Task 2: checks 5 and 6

**Depends:** [1]

**Implements:** REQ-006, REQ-007

- REQ-006 — duplicated adjacent block, the R-002 mechanisation.
- REQ-007 — empty section, with fenced content counting as body.

**Files:**
- Modify: `templates/hygiene.sh` (insert **above** the VERDICT block)

**Interfaces:**
- Consumes: `err`, `ok`, `dormant`, `FAIL`, the file list from task 1.

**Definition of done:** both checks measured on this repository — check 5 reports 0,
check 6 reports 0 **after task 3's fixes** (2 before them, which is the evidence the
check works); planted defects fire for both; `npm test` green.

- [ ] **Step 1: write the plant** — a scratch file with an identical 3-line block
      repeated, and one with `## A` immediately followed by `## B`.
- [ ] **Step 2: run and confirm neither is caught yet** (the checks do not exist).
- [ ] **Step 3: implement check 5** (blocks of ≥3 non-blank lines, blank-separated,
      byte-identical and adjacent) **and check 6** (heading level *N* followed by a
      heading of level ≤ *N* with no body between — **fenced content counts as
      body**).
- [ ] **Step 4: run and confirm both plants are caught**; run on this repository and
      record the counts.
- [ ] **Step 5: commit** `feat(hygiene): checks 5 and 6 — the R-002 mechanisation`.

---

### Task 3: the two repository fixes

**Depends:** —

**Implements:** REQ-007

**Files:**
- Modify: `evals/RESULTS.md` — `## Runs` gains one line of body.
- Modify: `plugins/task-pipeline/skills/task-pipeline/templates/retro.md` — the
  retirement record becomes a **list item under a `### Retirements` heading that has
  a body**, because a one-line record is not a section.

**Interfaces:** none.

**Definition of done:** check 6 reports **0** on this repository once task 2 exists;
`npm test` green — the retro template is guarded, so this must not break it.

- [ ] **Step 1: run** `npm test` → expect PASS (baseline before touching a guarded template).
- [ ] **Step 2: edit both files.**
- [ ] **Step 3: run** `npm test` → expect PASS.
- [ ] **Step 4: commit** `fix(docs): two empty sections, one of them a template shape mistake`.

---

### Task 4: generalise the template guards and execute the gate

**Depends:** [1, 2]

**Implements:** REQ-001, REQ-011

**Files:**
- Modify: `test/validate.py` — the block that today validates `docgate.sh`.

**Interfaces:**
- Consumes: `templates/hygiene.sh` from tasks 1–2.
- Produces: a `GATE_SCRIPTS` list the guards iterate.

**Definition of done:** removing `SCOPE:` from **either** gate script fails
`npm test`; `npm test` executes `hygiene.sh` over the seeded scratch project and
requires exit 0; no guard logic is duplicated.

- [ ] **Step 1: plant** — delete the `SCOPE:` line from a copy of `hygiene.sh`, run
      `npm test`, confirm it **passes** (proving the guard does not yet cover it).
- [ ] **Step 2: generalise** the existing guard to iterate
      `GATE_SCRIPTS = ("docgate.sh", "hygiene.sh")`, and add the scratch execution.
- [ ] **Step 3: re-run the plant** → expect FAIL, with the message naming `hygiene.sh`.
- [ ] **Step 4: restore and run** `npm test` → expect PASS.
- [ ] **Step 5: commit** `test(validate): guards iterate the gate scripts instead of copying`.

---

### Task 5: seven negative self-tests and the floor

**Depends:** [4]

**Implements:** REQ-012

**Files:**
- Modify: `.github/workflows/validate.yml` — seven steps appended.
- Modify: `test/negatives.py` — `MIN_EXPECTED` recomputed.

**Interfaces:** consumes the guards from task 4.

**Definition of done:** `python3 test/negatives.py` green; `MIN_EXPECTED` equals the
counted number of `- name: Negative self-test` steps in the workflow, **computed by
running the count, not copied from this plan**.

- [ ] **Step 1: count** the existing steps: `grep -c '      - name: Negative self-test' .github/workflows/validate.yml`.
- [ ] **Step 2: add six check plants + one VERDICT-last plant**, each corrupting a
      scratch copy **in Python**, each asserting the validator or the gate rejects it.
- [ ] **Step 3: re-count and set** `MIN_EXPECTED` to the new number.
- [ ] **Step 4: run** `python3 test/negatives.py` → expect green.
- [ ] **Step 5: commit** `test(negatives): one probe per hygiene check, floor recomputed`.

---

### Task 6: doctrine wiring

**Depends:** [5]

**Implements:** REQ-009, REQ-010

**Files:**
- Modify: `references/build.md` — the gate runs in diff mode after each implementer
  reports `DONE`, before the review; a finding is fixed in-task or carried over;
  **the script never edits, the agent fixes**.
- Modify: `references/stages.md` — §5, §6, §9 gate criteria name it and its counts.
- Modify: `references/gates.md` — added as a worked example beside the doc gate.
- Modify: `references/artifacts.md` — the new template in the layout.
- Modify: `templates/README.md` — the new seeded file.

**Definition of done:** `npm test` green (Contents-vs-headings and reach guards);
every file that names the gate names it identically.

- [ ] **Step 1: run** `npm test` → baseline PASS.
- [ ] **Step 2: edit the five files.**
- [ ] **Step 3: run** `npm test` → expect PASS.
- [ ] **Step 4: commit** `docs(doctrine): the hygiene gate runs per task, and the agent fixes`.

---

### Task 7: propagation and version

**Depends:** [6]

**Implements:** REQ-013, REQ-014

**Files:**
- Modify: `CHANGELOG.md`, `README.md`, `CONTRIBUTING.md`,
  `references/portability.md`, `cursor/rules/task-pipeline.mdc`, `package.json`,
  `.claude-plugin/marketplace.json`,
  `plugins/task-pipeline/.claude-plugin/plugin.json`.

**Definition of done:** four-way version sync at `1.12.0`; `npm run test:all` green;
the Cursor rule stays self-contained with **no relative links**.

- [ ] **Step 1: run** `npm run test:all` → baseline.
- [ ] **Step 2: write the CHANGELOG section** — what changed and why it mattered,
      including that measurement rewrote two of the six definitions.
- [ ] **Step 3: bump all four manifests to 1.12.0**; update the other surfaces.
- [ ] **Step 4: run** `npm run test:all` → expect green.
- [ ] **Step 5: commit** `docs: hygiene gate across every surface; v1.12.0`.

## No placeholders

Every task above names exact files, exact commands and exact expected outcomes.
Nothing says "similar to task N", "add error handling", or "TBD".

## Self-review

- **REQ coverage — set equality.** Brief REQ ids: 001–014 (14). Union of
  `Implements:` across tasks: 001, 002, 003, 004, 005, 006, 007, 008, 009, 010, 011,
  012, 013, 014 (14). **Difference ∅.**
- **Named checks:** every DoD names a command that exists today — `bash -n`,
  `npm test`, `npm run test:all`, `python3 test/negatives.py`, `grep -c`. Verified by
  running each at least once in this session.
- **Parallel safety:** group B holds tasks 2 and 3; task 2 writes `hygiene.sh`, task 3
  writes `evals/RESULTS.md` and `templates/retro.md`. **No shared file.**
- **Dependency truth:** task 2 consumes helpers task 1 produces; task 4 consumes the
  script tasks 1–2 produce; task 5 consumes task 4's guards. Each `Depends:` points at
  a task that really produces what is consumed.
- **DoD present and verifiable** on all 7 tasks.
- **Decisions:** consistent with the spec's D1–D5 and with the brief. No contradiction.
