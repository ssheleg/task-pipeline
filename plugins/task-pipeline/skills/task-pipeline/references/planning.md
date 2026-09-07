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
- Execution packets

## Audience

Assume a skilled developer who knows nothing about this codebase, this domain or
this toolset, has questionable taste, and will read **only their own task**.
Everything they need is in that task: exact paths, complete code, exact commands,
expected output. DRY. YAGNI. TDD. Frequent commits.

For independently dispatched agents, "that task" includes the resolved context
packet in [Execution packets](#execution-packets): relevant program/module
constraints, versioned interfaces, decisions and source digests travel with it.
Do not assume the executor has read a plan header or inherited the planning chat.
Planning may hand off at plan-ready without claiming implementation is complete.

Path: `<artifacts>/plans/YYYY-MM-DD-<topic>.md` — same `<topic>` slug as the
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

**Then run the fake-edge test over what you just drew.** Keep dependencies that
carry data, an enforceable control condition, or resource ordering. Mere sequence
is not enough. Test each edge before assigning a parallel group:

1. Write every task as a box.
2. Draw an arrow between each pair you were about to order.
3. Ask what fails if B starts before A: missing output, unmet approval/control
   condition, or conflicting ownership of a mutable resource?
4. Keep a justified edge and write its kind plus concrete payload/condition in
   the `Carries` cell: `data: schema v2`, `control: review accepted`, or
   `resource: release write lease on shared registry`.
5. Remove an edge only if none of those reasons applies. No data payload alone
   does not make an edge fake. Do not remove approval or ownership constraints.
6. Nodes without incoming dependencies are candidates for group A; capability
   and resource checks still determine whether they can start together.

**The stated dependency is reviewable.** An empty `Carries` cell requests a reason,
not automatic deletion. Keep a justified dependency, remove accidental ordering,
and leave an unresolved dependency blocked until its condition is understood.
There is no target number of edges to remove.

**File ownership is exclusive within a group.** No two tasks in the same parallel
group write the same file — that is the rule that makes stage-5 fan-out safe.
Sequential integration/glue tasks sit *between* groups.

**Distinct is not the same as independent.** Two tasks with different names, in
different directories, that both write one shared registry — or both take the
same fixed scratch path — are one task with a race in it. The check is what they
*touch*, never what they are called.

### This pipeline is a static graph, and that is a decision

The stage list is fixed before the run starts, and stays fixed. It could have
been otherwise: a run that reads its own findings and invents its next stage is
a real design, and it is the one this pipeline refuses.

**The reason is auditability.** A graph that decides its own shape while running
produces a shape nobody drew, so *"here is the pipeline"* and *"here is what this
run did"* stop being the same document — and every claim stage 10 makes becomes
unfalsifiable from the outside. That is the same failure the evidence canons name
when a number is restated rather than computed.

Two places the run *does* discover structure, both bounded and both recorded:
the **module map** cut at stage 2 ([`decomposition.md`](decomposition.md)), which
is committed as a file before any module is built, and the **carry-over ledger**,
which grows but never reorders a stage. Discovery that lands in a committed
artifact is not a dynamic graph; discovery that changes what runs next, silently,
is.

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

**Spec:** <artifacts>/specs/YYYY-MM-DD-<topic>-design.md

## Global constraints

<the spec's project-wide requirements — version floors, dependency limits, naming
and copy rules, platform requirements — one line each, exact values copied
verbatim from the spec. Every task's requirements implicitly include this section.>

## Execution order

| Group | Tasks | Runs after | Carries |
|---|---|---|---|
| A | 1, 2 | — | — |
| B | 3 | A | <kind: payload, control condition or resource ordering B requires> |

---
```

**The `Carries` cell is required on every edge and empty only on group A.**
Record `data`, `control` or `resource` and its concrete condition. An unexplained
edge blocks dispatch until justified or removed after review; never delete an
approval/resource edge merely because it carries no file or value.

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
5. **Parallel safety and the fake-edge test:** no two tasks in the same group write
   the same file **or share any other mutable target**; every `depends:` points at a
   task that produces the input or establishes the required condition, and every edge's `Carries` cell is
   filled. Count retained edges by kind and record removed edges with reasons.
   Zero removals is valid when every original dependency is justified.
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
- Edges: <n> declared, <n> data, <n> control, <n> resource, <n> removed with reasons
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
consistent across tasks; parallel-group tasks share no files **or other mutable
target**; each task has a verifiable DoD. **Every edge in the *Execution order*
table has a non-empty `Carries` cell, and the `Edges:` line of the self-review is
computed** — each retained edge names data, control or resource semantics. An
unexplained edge blocks the gate until justified or safely removed. UI tasks carry their scenario IDs and `SCR-` screens. Verify all
of it yourself and stop on failure — this gate has no operator in it.

## Execution packets

Size independent-executor tasks with [`decomposition.md`](decomposition.md) →
Executor-sized tasks and context. Keep parent findings/features as containers;
dispatch only leaves with resolved material decisions and budgeted primary context.


Use this contract when research, intake, specification and planning happen in one
agent, while other agents execute individual tasks, or when a host pipeline owns
dispatch. It is an artifact and workflow contract. It does not claim that the
bundled graph CLI is a distributed scheduler or that it implements the fields
below as commands.

### Roles and boundaries

The planning agent harvests sources, resolves material decisions, produces the
program/module model, specifications, task packets and their dependencies. It may
finish at **plan-ready**. That state means the plan is available for execution;
it does not mean the requested product is implemented.

An executor receives one task and its resolved context. It does not restart
intake or independently redesign settled interfaces. If the packet conflicts with
source reality, it returns a change proposal with evidence to the planner rather
than silently editing a shared plan. A reviewer evaluates the produced artifact;
an integrator reconciles compatible outputs and owns the final delivery boundary.
These are roles, not hardcoded models or host-specific subagent names.

### The context closure a task must carry

Persist a program brief and decisions, a module/interface map, shared contracts,
and one task packet per independently reviewable deliverable. Each packet names:

- Stable task, program and module IDs; its requirement and finding IDs.
- The relevant program constraints and module boundaries, as explicit inputs.
- Decisions with provenance, rationale, rejected alternatives and change triggers.
- Every consumed/produced interface, including its version and responsible task.
- Source repository, base revision and digests for the files/inputs it relies on.
- Files to read, files permitted to change, new files explicitly marked Create,
  and shared mutable resources. A directory name is not a complete ownership claim.
- Concrete implementation sequence, invariants and edge cases; exact code where
  a signature or algorithm must be settled, without pretending speculative code
  was tested against a future tree.
- Acceptance checks, required evidence type, scope exclusions and rollback.
- Output/return format, reviewer/integrator destination and context budget.

A linked file is useful only if the receiving agent can fetch it at the recorded
revision. Resolve required links before dispatch; a missing required contract
blocks dispatch, while optional context is labelled optional. Do not silently
truncate required constraints to fit a token budget. Produce a smaller coherent
task or move background material to retrievable references.

Priority, dependency readiness, context completeness and implementation status
are separate fields. An urgent row can be blocked; a detailed packet can still
depend on an unfinished contract. Never translate either into "ready" by prose.

### Dispatch, retries and changed inputs

Before dispatch, verify the packet's inputs and predecessor outputs against their
current digests. Changed relevant input makes the packet stale until it is
reconciled; an unrelated file change need not invalidate the whole program.
Record a new packet revision rather than rewriting the executor's historical input.

The host adapter must establish one execution attempt: task ID, packet revision,
attempt ID, owner, resource scope, expiry/heartbeat when applicable, and a fencing
token for takeover. A file lock protecting JSON writes is not an execution lease.
If the host cannot provide this boundary, serialize execution and state the
limitation; do not run independent workers that merely read the same ready list.

An executor returns output artifacts, changed-file digests, base/produced revisions,
checks with PASS/FAIL/NOT_RUN/TEST_ERROR, remaining risks and the attempt token.
Completion is accepted only for the current attempt and expected input revision.
Duplicate results are idempotent; a late stale worker cannot close a newer attempt.
Do not equate an agent's final message with an accepted business result.

Dependencies may carry data, a control/approval condition, or a resource ordering
constraint. Name the kind and reason. A dependency cannot be discarded solely
because it has no data payload. Dispatch a task only after all its declared
prerequisites are satisfied, and check overlapping write sets separately.

### Portable host integration

Keep the packet independent of Claude Code, Codex or any provider's conversation
format. Each adapter maps dispatch, artifact access, cancellation, progress and
result receipts to actual host capabilities. Record the capabilities used.
Fresh agents and resumed agents receive the same required context closure.

For an external platform, map both schemas explicitly: a stage list is not a work
graph, a handoff message is not an execution lease, and an artifact path is not
proof that a remote worker can read it. Until the adapter and its failure tests
exist, label integration proposed/manual rather than supported.

### UI task annex

For a UI outcome, attach the scenario/screen/state IDs, selected flow and visual
direction revision, component reuse/modify/create decisions, semantic token roles,
approved or explicitly provisional content, keyboard/accessibility expectations,
responsive/native behavior, and local asset provenance. Include only the portion
needed for this leaf. A non-UI task does not need this annex.

Keep behavior, its visual presentation and relevant states together when they
form one independently verifiable outcome. Do not split every screen into HTML,
CSS and interaction jobs. A changed flow, component contract or design revision
refreshes the affected packets; the executor does not guess which screenshot or
style discussion was authoritative. Preserve the existing family artifact paths.

### Audit to executable backlog

Every finding has a disposition and a task or a recorded reason for not acting.
Separate common enabling contracts from per-finding repairs; link each task to
the program/module/interface context it consumes. Build the graph, verify its
closure, and partition runnable tasks by disjoint write sets. Include input drift,
missing context, duplicate dispatch, late completion, multiple prerequisites,
cancellation and failure recovery in acceptance. A cold reader must understand
why the change exists and how its result fits the system without the original chat.

Store the packet set with the plan. Planning is complete when the declared scope
is covered, required inputs resolve, dependencies are acyclic and readiness is
reported honestly. Delivery remains a separate state with its own evidence.
