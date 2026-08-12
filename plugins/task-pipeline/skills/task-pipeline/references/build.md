# Build — stage 5, built in

Executing the plan: an isolated workspace, one fresh implementer subagent per task,
a review after each task, a whole-branch review at the end. Built into this skill;
nothing to install.

> Ported from the `using-git-worktrees` and `subagent-driven-development` skills in
> [obra/superpowers](https://github.com/obra/superpowers) (MIT — see `LICENSE` →
> *Third-party*), rewritten for this pipeline: no external scripts, the ledger
> lives under `.task-pipeline/`, and model choice defers to the run's single
> confirmed model ([`model-tiering.md`](model-tiering.md)).

**Why subagents:** each task goes to an agent with a constructed context — its
brief, its interfaces, the global constraints, nothing else. It never inherits the
session's history, so it stays focused; your context stays free for coordination.

**Continuous execution:** don't check in between tasks. The operator asked for the
plan to be executed — execute it. Stop only for BLOCKED you can't resolve, a
genuine ambiguity, or completion. "Should I continue?" between tasks is noise.

**Scope, so this is not mistaken for the run-wide mode:** the rule above governs
the *inside* of this stage and is unconditional — it holds whether or not a loop
is armed. What it cannot do is reach the other nine stages, or survive the
boundary between one agent turn and the next; on a harness where prose does not
carry across that boundary, only a scheduled re-invocation does.
[`continuity.md`](continuity.md) owns that half, is recorded in `pipeline.json` →
`run.loop`, and is **off unless recorded**. The two never disagree: one is a
stage's internal discipline, the other is the run's pacing.

**Narration:** at most one short line between tool calls. The ledger and the tool
results are the record.

**No subagents available?** (a harness without them, or a plan so small that
dispatching costs more than it saves) — run the same loop inline: same isolation,
same ledger, same TDD per task, and after each task review your own diff against
the rubric in [`review.md`](review.md) before moving on. What changes is who does
the work; the gates, the artifacts and the review discipline do not. Say plainly
that the run is inline, since a self-review is weaker evidence than a fresh
reviewer's.

## Contents

- 1. Isolation
- 2. Workspace and ledger
- 3. Models
- 4. The task loop
- 4a. A screen is the frame, implemented
- 5. Final whole-branch review
- 6. Integrate, then finish
- GATE (auto)
- Rationalizations

## 1. Isolation

Work never starts on `main`/`master` without the operator's explicit consent
(the stage-0 brief usually records the branch policy — read it, don't re-ask).

**Detect existing isolation first:**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" && pwd -P)
git rev-parse --show-superproject-working-tree   # non-empty ⇒ submodule, not a worktree
```

- `GIT_DIR != GIT_COMMON` and **not** a submodule → you are already in a linked
  worktree. Do not create another. Report the path and branch, go to *Setup*.
- Otherwise you are in a normal checkout. Honor the brief's worktree preference; if
  none was recorded, ask once before creating one.

**Creating one — native tool first.** If the harness offers a worktree tool
(`EnterWorktree`, a `/worktree` command, a `--worktree` flag), use it: it owns
placement, branch creation and cleanup. Reaching for raw `git worktree add` when a
native tool exists creates state the harness can't see or clean up.

**Git fallback**, only when there is no native tool:

```bash
# both scratch roots MUST be ignored before anything is created
git check-ignore -q .worktrees || printf '.worktrees/\n' >> .gitignore
git check-ignore -q .task-pipeline || printf '.task-pipeline/\n' >> .gitignore
git diff --quiet .gitignore || git commit -m "chore: ignore build scratch dirs" .gitignore
git worktree add ".worktrees/$BRANCH" -b "$BRANCH"
```

Directory priority: an explicit operator preference → an existing `.worktrees/` →
an existing `worktrees/` → default `.worktrees/`. An unignored worktree directory
commits the entire tree into the repo — verify before creating. If creation fails
on a sandbox permission error, say so plainly and work in place.

**Setup + baseline.** Install dependencies the way the project does (`npm install`,
`cargo build`, `pip install -r requirements.txt`, `poetry install`, `go mod
download`), then run the test command from the brief's autonomy sweep. A dirty
baseline makes every later failure ambiguous: report failures and let the operator
decide whether to proceed.

## 2. Workspace and ledger

Conversation memory does not survive compaction. A controller that lost its place
re-dispatches completed tasks — the most expensive failure this stage has.
**Track progress in a file, not only in todos.**

- Each plan owns a git-ignored workspace: `.task-pipeline/build/<plan-basename>/`
  at the repo root. Everything for THIS plan lives there — ledger, task briefs,
  implementer reports, review packages. Another plan's directory is never yours to
  read or write. `.task-pipeline/` must be git-ignored — the isolation step above
  adds and commits it; if you skipped that step, do it now, in its own commit, so
  scratch files never land in a task's diff.
- Ledger: `<workspace>/progress.md`, first line = its identity:
  `# build ledger — plan: <plan file path>`.
- **Resuming:** a task with a `Task <N>: complete` line is DONE — never
  re-dispatch it; resume at the first task without one. A task whose last line is a
  fix round is mid-loop: continue at the next round. A ledger naming a different
  plan belongs to that plan — leave it and start your own.
- After compaction, trust the ledger and `git log` over your recollection: the
  commits it names exist even when your context no longer remembers them.

Read the plan **once**, note its context and Global Constraints, create a todo per
task.

**Pre-flight conflict scan.** Before Task 1, scan the plan for tasks that
contradict each other or the Global Constraints, and for anything the plan mandates
that the review rubric ([`review.md`](review.md)) treats as a defect. Present
everything you find as **one batched question** — each finding beside the plan text
that mandates it, asking which governs. Clean scan → proceed silently.

## 3. Models

**Default: the run's one confirmed model** ([`model-tiering.md`](model-tiering.md))
for every subagent — implementers, reviewers, fixers. Pin it explicitly on each
dispatch; an omitted model silently inherits the session's and defeats whatever the
operator recorded.

**Deviate only from the operator's recorded override map.** If the stage-0 brief
carries per-stage or per-role overrides, apply them: mechanical transcription tasks
(the plan carries the complete code, 1–2 files) can take a cheaper tier, while
integration, design and review work stays on the confirmed model. No map recorded →
no deviation, and never a silent downgrade. Turn count beats token price: the
cheapest tier routinely takes 2–3× the turns on multi-step work and costs more
overall.

**Two moments deserve more capability than the run's default** — both are
*recommendations you state out loud*, never silent switches:

- **The final whole-branch review.** If the run is on a tier below the most capable
  one available, say so and offer to run this one review there; if the operator
  declines or the tier doesn't exist, run it on the confirmed model and note it.
- **Fix-loop rounds 4–5.** One tier above the implementer that got stuck, when the
  environment has one and the override map or the operator allows it; otherwise
  say so and rely on fresh eyes alone.

## 4. The task loop

Everything you paste into a dispatch prompt — and everything a subagent prints back
— stays in your context for the rest of the session. **Hand artifacts over as
files.**

### 4.1 Dispatch the implementer

Record `BASE=$(git rev-parse HEAD)` before dispatching; the review package and the
fix-round diffs need it.

**Write the task brief to a file** — extract the task's full text from the plan to
`<workspace>/task-<N>-brief.md`. The brief is the single source of requirements;
exact values (numbers, strings, signatures, test cases) live **only** there.
Include the task's `Implements:` ids **with each REQ's one-line statement quoted
verbatim** — an implementer who sees only an instruction optimises the
instruction; one who sees the requirement behind it catches the case the
instruction didn't cover.

The dispatch prompt contains exactly five things:

1. One line on where this task fits in the project.
2. The brief path — "read this first; it is your requirements, use its values
   verbatim".
3. Interfaces and decisions from earlier tasks the brief can't know.
4. Your resolution of any ambiguity you spotted in the brief.
5. The report path (`<workspace>/task-<N>-report.md`) and the report contract.

Never paste accumulated history ("state after tasks 1–3") into later dispatches.
Never make a subagent read the whole plan. If an earlier task parked a finding in
the area this task touches, carry a pointer to that ledger line.

Record the implementer's agent identity: fix rounds 1–3 resume it.

**Implementer contract** (put this in the prompt):

> Read `<brief path>` first — it is your requirements. Work TDD, and no production
> code exists before a test you **watched fail**: write the failing test → run it
> and confirm it fails for the right reason → write the minimal code that passes →
> run it and confirm it passes, with the rest of the suite still green → commit.
> Assert on real behavior, never on mock behavior. **Any step with a side effect
> outside your own diff — a command that moves, deletes, publishes, migrates,
> restarts or cancels something — is confirmed by re-reading the state it changed,
> never by the command's own reply; record each one in the report as a
> `verified-by:` line carrying the command you ran to confirm and its output.**
> Commit as you go, conventional commits. When done, self-review your diff, then write the full report to
> `<report path>`:
> what you built, the files touched, the commits, the test command and its
> output, decisions you made, anything you're unsure about. Return **only**:
> status (`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`), the
> commit range, a one-line test summary, and your concerns. Ask before starting
> if anything in the brief is ambiguous — questions are cheaper than rework.

### 4.1a Decisions settled inside a task — and who may write them down

The report above already asks for *"decisions you made"*, and stage 5 settles more
of them than any other stage: an interface picked between two tasks, a ruling on a
review finding, a constraint discovered in the code. Every one is a Doc Loop trigger
([`documentation.md`](documentation.md)) — and this is the one stage where running
that loop naively breaks something.

**A subagent never writes the register.** Not a style rule; the same physical
argument as §4.2 below, one level up:

- The register is **append-only shared state**. Two implementers appending in two
  worktrees conflict on the one file a project cannot afford to hand-merge, and the
  loser's entry is the one that quietly disappears.
- An **id cannot be reserved from inside an isolated branch.** Reserving *is* an
  arbitration between concurrent writers, and a worktree is by construction unable
  to see the other writers ([`documentation.md`](documentation.md) → *Registers are
  shared state*).

So the route is fixed: a decision settled in a task goes into the **implementer
report**, and into the **carry-over ledger** if it outlives the task — and the
**orchestrator runs the Doc Loop after integration**, on the base branch, as a
single writer. Nothing is lost and nothing collides.

**What that costs, said out loud:** between the ruling and the entry there is a
window in which the decision exists only in a report. That is exactly why the gate
below harvests every report and parked finding into the ledger **before the scratch
workspace is deleted** — the ledger is what survives the window.

### 4.2 Parallel groups — when fan-out is allowed

The plan's parallel groups ([`planning.md`](planning.md)) describe what *may* run
concurrently. Whether it actually does is this stage's call, and the constraint is
physical: **two implementers writing one working tree corrupt each other's state.**

- **Default: sequential.** One implementer at a time, review after each. Correct for
  every group, and always correct when the tasks are small.
- **Fan out only when all three hold:** the tasks are in the same group (no
  `depends:` between them), their file ownership is exclusive per the plan, and
  **each implementer gets its own isolated worktree**. Then dispatch them together,
  review each one against its own diff, and integrate the worktrees back to the
  build branch one at a time, running the suite after each merge.
- **Any conflict on integration** means the plan's file ownership was wrong: stop
  fanning out, finish the group sequentially, and record it in the ledger.
- Never fan out the fix loop — a task under repair belongs to one implementer.

### 4.3 Handle the report

| Status | Action |
|---|---|
| `DONE` | **Run the hygiene gate in diff mode first** (below), then build the review package and dispatch the task review ([`review.md`](review.md)). |
| `DONE_WITH_CONCERNS` | Read the concerns first. Correctness or scope → resolve before review. Observations ("this file is getting large") → **append to the carry-over ledger**, then proceed. A concern that stays only in the report dies with the workspace. |
| `NEEDS_CONTEXT` | Supply exactly what's missing, re-dispatch. |
| `BLOCKED` | Diagnose: missing context → re-dispatch with it; needs more reasoning → a more capable model; too large → split the task; the plan itself is wrong → escalate to the operator. |

### The hygiene gate — after every task, before the review

A subagent's own report is not evidence about the text it left behind. Run the
seeded gate over **what this task changed**, before the reviewer sees it:

```bash
HYGIENE_BASE=<the commit recorded before dispatching> bash scripts/check-hygiene.sh
```

Diff mode has **no floor**: this task wrote it, this task fixes it. Six checks — a
half-resolved merge, a stub that outlived the task, a fence left open, a file
"shortened" while being rewritten, a **block duplicated by a retried edit**, and a
section opened and abandoned.

The fifth is why the gate runs here rather than only at stage 6. A batch of edits
where one applied twice, or never applied at all, is the incident behind standing
instruction R-002 — and it is invisible in a status report. Found one task later it
costs a re-dispatch; found eight tasks later it is fixed by an agent that no longer
remembers the code.

**The hygiene gate reads what the task wrote; it cannot see what the task did.**
A file the task moved, a job it cancelled, a service it restarted, a record it
migrated — none of that is in the diff, and the implementer's report is not evidence
about it either. Before the review, read back the report's `verified-by:` lines:
every side-effecting step must carry the command that **confirmed** the state, not
the command that caused it. A step with no such line is unverified, not done
([`gates.md`](gates.md) → *False success*).

**The gate never edits. Fixing is yours.** A finding is repaired inside the same
task, or it becomes a carry-over row with a reason — never a silent pass. A gate
whose findings nobody acts on is a slower way of ignoring them.

**Never** ignore an escalation, and never re-dispatch the same model with the same
prompt after a BLOCKED. If the implementer says it's stuck, something must change.
If the implementer asks a question — before or mid-task — answer it completely; do
not rush it into implementation.

### 4.4 Review the task

Every task gets a review with **all three** verdicts — spec compliance, **REQ
satisfied**, and code quality. The implementer's self-review never substitutes for
it. Rubric, inputs, prompt templates and how to build the diff package:
[`review.md`](review.md).

The REQ verdict is the one the other two can't produce: a task can meet every line
of its brief and still miss the requirement it was written to deliver. A ❌ there
enters the fix loop like any Important finding.

A review may report **"cannot verify from diff"** items — requirements that live in
unchanged code or span tasks. They don't block the review, but you resolve each one
yourself before completing the task; you hold the cross-task context the reviewer
lacks. A confirmed gap becomes a failed spec review and enters the fix loop.

### 4.5 The fix loop

Triggered by: spec ❌, any Critical or Important finding, or a "cannot verify" item
you confirmed as a real gap.

Two routes leave before the loop starts:

- **Minor findings** never enter it. Record each in the ledger
  (`Task <N>: minor (deferred): <one-liner>`) and point the final review at that
  list. A roll-up nobody reads is a silent discard.
- **A finding class that shows up a second time stops being a finding and becomes a
  check.** Two tasks flagged for the same mechanical defect — the same missing
  failure path, the same magic value, the same naming slip — means every later task
  will produce it too. Add it to the host's lint or check script now, in its own
  commit, instead of writing the third instance into the ledger
  ([`audit.md`](audit.md) → *A class that repeats twice becomes a gate*).
- **A finding that conflicts with what the plan mandates** is the operator's
  call: present the finding beside the plan text and ask which governs. Don't
  dismiss the finding because the plan mandated it; don't fix against the plan
  without asking.

Everything else loops. One round = one fix dispatch + one scoped re-review.
**Five rounds maximum per task.**

**The loop guard runs alongside the counter** ([`loop-guard.md`](loop-guard.md)):
log every repeat touch (`touch: <file> — round N — reason: <finding id>`) and trip
*before* the cap when a fix undoes an earlier fix, when the same file returns for
the same reason, or when a finding already ADDRESSED reappears. A tripped guard is
not another round: stop, name the two shapes, escalate to the layer that owns the
conflict, then re-check in a planned order.

- **Rounds 1–3:** resume the original implementer with the open findings verbatim —
  its context is intact. If the harness can't message a live subagent, dispatch a
  fresh one with the brief path, the report path and the findings; the report file
  is the persistent memory either way.
- **Rounds 4–5:** fresh implementer, one tier up if available, framed as: "a prior
  implementer attempted this task N times; you own it now — read the report file
  for what was tried." A loop that survives three resumes usually means the
  implementer can't see its own problem.
- **Every round:** the implementer fixes, re-runs the tests covering the amended
  code, appends its fix report to the same report file, returns the short contract.
  Before re-dispatching the reviewer, confirm the fix report names the covering
  tests, the command run and the output.
- **The re-review is scoped** to the fix diff (`FIX_BASE`..`HEAD`, where `FIX_BASE`
  is the head the previous review saw). It verdicts each finding ADDRESSED / NOT
  ADDRESSED and flags new breakage in the fix diff only. New Critical/Important
  breakage joins the open list; out-of-scope observations go to the ledger as
  deferred minors — they never extend the loop.
- **Ledger, every round:**
  `Task <N>: fix round <R>/5 (<X> addressed, <Y> open — <one-liners>; commits <a7>..<b7>)`

**In a subagent run, never fix findings yourself in the controller session** —
controller fixes skip review and pollute the context you need for coordination. In a
declared inline run you do fix them, and you still review the fix diff against the
rubric before closing the round.

**The breaker.** If round 5's re-review still leaves findings open, stop
dispatching and adjudicate each one yourself:

- **Reviewer wrong or the point contestable** → park it:
  `Task <N>: parked — <finding> — ruling: <why the code stands>`.
- **Real, but nothing downstream builds on it** → park it the same way, with a
  ruling saying it's real and deferred.
- **Real and load-bearing** (a later task builds on it, or it exposes a plan defect)
  → **STOP**. Append `Task <N>: BLOCKED — <reason>` and report to the operator with
  the finding, the plan text it collides with, and the fix history. Parking a
  structural failure lets every dependent task build on it.

Adjudicate **only at the cap**. Adjudicating earlier to end a loop is pre-judging
with a nicer name. Every adjudication is a ledger line; silent discards are
forbidden.

### 4.6 Complete the task

When the review is clean — or every open finding is parked with a ruling at the cap
— append:

- `Task <N>: complete (commits <base7>..<head7>, review clean)`, or
- `Task <N>: complete (commits <base7>..<head7>, <K> parked)`

Mark the todo complete, move on. Never start the next task while Critical/Important
findings are neither fixed nor parked-with-ruling at the cap.

## 4a. A screen is the frame, implemented

When Figma is connected, a screen is not *informed by* the design file — it **is** the
frame, in code. Values, structure and composition all come from the file, and the order
of authority is fixed:

| Question | Answer comes from |
|---|---|
| what the screen **does** — states, errors, empties | `super-ux`'s scenarios |
| what it is **made of** — elements, hierarchy, layout, tokens | **the frame** |
| how it **looks and moves** where the frame is silent | `sheleg-design` |

`sheleg-design` runs **after** the file, never instead of it. It owns rhythm, motion and
motion's degradation to stillness — the things a frame does not carry. Put it first and
it invents what was already decided.

**Five things this makes concrete.**

1. **The composition is compared, not recalled.** A frame has a node tree
   (`get_metadata`). Every node has a counterpart in the screen, and nothing is present
   that the frame does not have. A missing element is incomplete; an invented one is a
   divergence, not an improvement.
2. **Layout is read, not eyeballed.** Auto-layout direction, gaps, padding and
   constraints come from `get_design_context`. From a screenshot they are recovered
   approximately, and approximate is indistinguishable from exact in a report.
3. **A component with a Code Connect mapping is not rewritten.** If
   `get_code_connect_map` names a code component for that node, the screen uses it.
   Reimplementing it is a silent fork of the design system.
4. **A token names its variable.** A raw hex or px where the file has a variable is a
   token that has quietly split in two. `get_variable_defs` is the canon; a screenshot
   is a way to *look*, never a way to *know*.
5. **The frame is a contract at its own width.** It is one width and said nothing about
   the others, so behaviour at other breakpoints — and states the frame does not draw,
   like error, empty and loading — is a **decision that gets recorded**, not guessed.
   Without this the rule is either unfollowable or vacuous.

**When there is no frame for a screen — build it, name it, offer to draw it.**

Figma is a recommendation like the graph and the wiki: its absence is named and never
blocks. So the screen is built from `sheleg-design`'s style pack, the spec records
*"no frame — source: sheleg-design"*, and the run **offers to draw the missing screens**
into the file the brief already named. Concretely: which screens, where they land, what
they are drawn from — so the operator sees the size before saying go.

Drawing happens **only on an explicit go**, into the recorded destination, never into a
new file. And whatever is drawn is **marked as coming from implementation** — its own
page or a naming convention that says so. A designer opening the file must be able to
tell what a person decided from what a run generated; an unmarked generated frame is the
same false confidence as an unproven green.

**Deviation is a line, not a silence.** Where the implementation must differ — a
platform constraint, an accessibility floor, a breakpoint — write what and why.
Otherwise *"built from the frame"* and *"built to look like it"* read identically.

## 5. Final whole-branch review

After the last task: build a package over `MERGE_BASE`..`HEAD`
(`git merge-base "$BASE_BRANCH" HEAD`, where `$BASE_BRANCH` is the base recorded in
the stage-0 brief — never a hardcoded `main`), dispatch the whole-branch review
([`review.md`](review.md) → *Prompt — final whole-branch review*; on the run's model, escalation offered
out loud per *Models* above), and point it at the
ledger's deferred-minor and parked lines so it can triage what must be fixed before
merge.

If it returns findings, dispatch **ONE** fix subagent with the complete list — not
one fixer per finding; per-finding fixers each rebuild context and re-run suites.
Then exactly **one** scoped re-review of the fix wave. Adjudicate residuals as in
the breaker: park with rulings, or stop on load-bearing ones. There is no second
fix wave.

## 6. Integrate, then finish

The work is in a worktree on its own branch; stages 7–9 lint, deploy and document
the **integrated** result. Close that gap here, honoring the branch policy recorded
in the stage-0 brief:

1. **Sync with the base branch** (rebase or merge, whichever the project uses) and
   re-run the full suite on the result. A branch that was green in isolation and red
   after integration is red — fix it here, not at stage 7.
2. **Land it the project's way:** merge into the base branch, or open a PR when the
   project requires review. Opening a PR is outward-facing — do it only with the
   operator's go or the brief's specific standing authorization.
3. **Never force-push a shared branch**, and never land on `main` when the brief put
   it off-limits.
4. **Remove the worktree** once merged (`git worktree remove <path>`, or the native
   tool that created it), and delete this plan's workspace
   (`rm -rf .task-pipeline/build/<plan-basename>`) — git history is the record now.
   Sibling directories belong to other plans; leave them.

If the operator's policy is "leave the branch, I'll merge it myself", stop after
step 1, say exactly where the branch is and what state it's in, and record that
stages 7–9 run against an unintegrated branch.

## GATE (auto)

All plan tasks DONE with all three review verdicts (spec compliance, REQ satisfied,
code quality); the full test suite green; every open finding either fixed or parked
with a ruling; **every parked finding and implementer concern harvested into the
carry-over ledger** — the workspace is deleted, so nothing may stay only there;
no task left BLOCKED; the branch integrated per the brief's policy — or the
operator explicitly told you to leave it, and that is recorded. **Every decision a
task settled has run the Doc Loop after integration, written by the orchestrator on
the base branch** (§4.1a — a subagent never writes the register), or is sitting in
the ledger with its entry still owed. Verify it yourself;
a red suite or an unresolved BLOCKED does not advance to stage 6.

## Rationalizations

| Excuse | Reality |
|---|---|
| "Close enough on spec compliance" | The reviewer found spec gaps ⇒ not done. Fix, or hit the cap and adjudicate. Those are the only exits. |
| "I'll fix it myself, dispatching is overhead" | In a subagent run, controller fixes skip review and pollute your context — resume the implementer. (Inline runs are the declared exception, and still review the fix diff.) |
| "One more round will converge" | Past the cap, rounds don't converge — the failure is structural. Adjudicate and route. |
| "The fix was small, skip the re-review" | Unreviewed fixes are how regressions land. Every round ends with a scoped re-review. |
| "This finding is obviously wrong, drop it" | You adjudicate at the cap, in writing. Silent discards are forbidden. |
| "Ledger bookkeeping is overhead" | The ledger is what survives compaction. Without one, controllers re-run entire completed task sequences. |
| "Two implementers in parallel will be faster" | One working tree, two writers = corrupted state. Parallel needs one worktree each. |
| "I'll paste the earlier tasks so it has context" | A fresh subagent needs its task, its interfaces and the constraints. Pasted history is pure cost. |
| "Stage 7 can merge the branch" | Stage 7 lints and deploys what is integrated. An unmerged branch means lint, deploy and docs all ran against something that is not what ships. |
