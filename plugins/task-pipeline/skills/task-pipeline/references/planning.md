# Plan — stage 4, built in

Turning the spec into an implementation plan a **zero-context implementer** can
execute task by task without reading the spec, the chat, or the rest of the plan.
Built into this skill; nothing to install.

> Ported from the `writing-plans` skill in
> [obra/superpowers](https://github.com/obra/superpowers) (MIT — see `LICENSE` →
> *Third-party*), extended with the dependency graph, parallel groups and
> file-ownership rules this pipeline's stage-5 subagent build depends on.

## Contents

- Audience
- Before writing tasks
- Task right-sizing
- Plan header — required
- Task structure — required
- No placeholders
- Self-review — before handing off
- This stage settles nothing — and that is a rule, not an omission
- GATE (auto)

## Audience

Assume a skilled developer who knows nothing about this codebase, this domain or
this toolset, has questionable taste, and will read **only their own task**.
Everything they need is in that task: exact paths, complete code, exact commands,
expected output. DRY. YAGNI. TDD. Frequent commits.

Path: `docs/superpowers/plans/YYYY-MM-DD-<topic>.md` — same `<topic>` slug as the
brief and the spec.

## Before writing tasks

**Scope check.** A plan covers exactly **one** spec — for a decomposed platform,
one module's dossier ([`decomposition.md`](decomposition.md)). If the spec in front
of you covers several independent subsystems, the decomposition was missed at stage
2: say so and go back there for a module map, rather than inventing the split here.
Whatever this plan covers must produce working, testable software on its own.

**Map the file structure.** List every file that will be created or modified and
what each one owns. This is where decomposition gets locked in:

- One clear responsibility per file; clear boundaries, defined interfaces.
- Files that change together live together. Split by responsibility, not by
  technical layer.
- Follow the existing codebase's patterns. Don't unilaterally restructure — but if
  a file you're modifying has grown unwieldy, planning its split is fair.

**Draw the dependency graph.** Which task needs what from which. Then group tasks
into **parallel groups** in topological order, and tag each task
`depends: [task ids]`.

**File ownership is exclusive within a group.** No two tasks in the same parallel
group write the same file — that is the rule that makes stage-5 fan-out safe.
Sequential integration/glue tasks sit *between* groups.

## Task right-sizing

A task is the smallest unit that carries its own test cycle and is worth a fresh
reviewer's gate. Fold setup, configuration, scaffolding and docs into the task
whose deliverable needs them. Split only where a reviewer could meaningfully reject
one task while approving its neighbor. Every task ends with an independently
testable deliverable.

Each **step** inside a task is one action, 2–5 minutes: write the failing test →
run it and watch it fail → minimal implementation → run it and watch it pass →
commit.

## Plan header — required

```markdown
# <Feature> — implementation plan

> **For agentic workers:** execute this plan task-by-task under the task-pipeline
> stage-5 build doctrine — isolated workspace, one implementer per task, a review
> with all three verdicts after each (spec compliance, REQ satisfied, code
> quality). Steps use `- [ ]` checkboxes.

**Goal:** <one sentence>

**Architecture:** <2–3 sentences>

**Tech stack:** <key technologies>

**Spec:** docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md

## Global constraints

<the spec's project-wide requirements — version floors, dependency limits, naming
and copy rules, platform requirements — one line each, exact values copied
verbatim from the spec. Every task's requirements implicitly include this section.>

## Execution order

| Group | Tasks | Runs after |
|---|---|---|
| A | 1, 2 | — |
| B | 3 | A |

---
```

## Task structure — required

````markdown
### Task N: <component>

**Depends:** [task ids, or —]

**Implements:** REQ-003, REQ-007 — *(the brief's requirement ids this task
delivers, or `—` for pure glue/infrastructure tasks. Quote each REQ's one-line
statement under the DoD so the zero-context implementer sees the intent, not just
the instruction.)*

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test_file.py`

**Interfaces:**
- Consumes: <what this task uses from earlier tasks — exact signatures>
- Produces: <what later tasks rely on — exact names, parameter and return types.
  The implementer sees only this task; this block is how they learn the names
  neighboring tasks use.>

**Definition of done:** <observable, verifiable conditions — tests green, behavior
demonstrated, docs updated in this same change>

- [ ] **Step 1: write the failing test**

```python
def test_specific_behavior():
    assert function(input) == expected
```

- [ ] **Step 2: run it and confirm it fails**

Run: `pytest tests/path/test_file.py::test_specific_behavior -v`
Expected: FAIL — `NameError: name 'function' is not defined`

- [ ] **Step 3: minimal implementation**

```python
def function(value):
    return expected
```

- [ ] **Step 4: run it and confirm it passes**

Run: `pytest tests/path/test_file.py::test_specific_behavior -v`
Expected: PASS

- [ ] **Step 5: commit**

```bash
git add tests/path/test_file.py src/path/file.py
git commit -m "feat: <what changed>"
```
````

For UI tasks, every task that builds user-facing behavior names the **scenario
ID(s)** and `SCR-` screen(s) it implements, and its DoD includes satisfying them
**and** updating the affected super-ux layers in the same change.

## No placeholders

These are plan failures. Never write them:

- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" without the actual test code
- "Similar to Task N" — repeat the code; tasks get read out of order
- A step that says what to do without showing how (code steps need code blocks)
- References to types, functions or methods no task defines

## Self-review — before handing off

A checklist you run yourself, inline. No subagent:

1. **REQ coverage — set equality, not a feeling.** Collect every `Implements:` id
   across all tasks and compare it to the brief's REQ table. The two sets must be
   **equal**: a REQ with no task is scope silently lost; an `Implements:` id that
   isn't in the brief is either a typo or work nobody asked for. Print the
   difference and fix it before anything else — this seam is where scope leaks.
2. **Spec coverage:** walk each spec requirement. Point at the task that implements
   it. A requirement with no task → add the task.
3. **Placeholder scan:** search the plan for every pattern above. Fix.
4. **Name and type consistency:** signatures, property names and types used in
   later tasks match what earlier tasks defined. `clearLayers()` in Task 3 and
   `clearFullLayers()` in Task 7 is a bug, not a style difference.
5. **Parallel safety:** no two tasks in the same group write the same file; every
   `depends:` points at a task that really produces what's consumed.
6. **DoD present and verifiable** on every task.
7. **Every command, path and file a DoD names resolves.** Walk each task's
   *Definition of done* and its steps and check the targets exist — a DoD that says
   `npm run lint:paths` when no such script exists is an instruction the implementer
   cannot follow and a check the acceptance cannot run.
   [`learned.md`](learned.md) rule 14 has said *every target resolvable* since
   v1.4.0 and fired only at stage 9 — four stages after the target is written here.
8. **Run the hygiene gate** over what this stage wrote and record its counts below.

**R-003 asked of this file, and answered:** `spec.md`'s items 8 and 9 — reading
decisions back, and printing the cost — deliberately do **not** appear here. This
stage settles nothing (see below), so it has no decisions to contradict and no scope
of its own to grow. Its sibling's item 7 does belong, reworded for DoDs.

### The `## Self-review` section — committed, not asserted

Identical in shape to `spec.md`'s, so one habit covers both stages. Last section
before the gate; every line a **computed number, not a tick**.

```markdown
## Self-review

- REQ coverage: <n> in brief, <n> covered, difference <set or ∅>
- Named checks: <n> named, <n> resolve, <n> marked `review`
- Decisions: checked against <the brief's D-table> and <stage 2's rejected options> — <verdict>
- Cost: <surfaces>/<guards>/<REQ> now, <…> at stage 2 — <proportionate | grown, and why>
- Hygiene: <n> checks, <n> findings, <n> open
- Placeholders: <n> · Ambiguity: <n> found, <n> resolved inline
```

## This stage settles nothing — and that is a rule, not an omission

Planning **translates** decisions; it does not make them. So unlike stages 2, 3, 5
and 10 there is no Doc Loop trigger here ([`documentation.md`](documentation.md)),
and the reason is worth stating, because an unstated exclusion is indistinguishable
from a gap.

The consequence is the working rule: **if writing the plan forces a choice, the
choice belongs to a lower layer.** A contract that turns out underspecified goes
back to stage 3 and is recorded there; a scope question goes back to the operator.
A decision first made while sequencing tasks is a decision nothing downstream will
ever find, because nobody reads a plan after the build.

## GATE (auto)

**Set equality first:** the REQ ids in the brief equal the union of `Implements:`
across the plan's tasks. A non-empty difference fails the gate and is reported as
the explicit list of dropped (or invented) requirements — this seam is where scope
leaks, so the check is mechanical, never a judgement call.

Then: every spec requirement maps to a task; no placeholders; names and types
consistent across tasks; parallel-group tasks share no files; each task has a
verifiable DoD. UI tasks carry their scenario IDs and `SCR-` screens. Verify all of
it yourself and stop on failure — this gate has no operator in it.
