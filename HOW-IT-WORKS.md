# How task-pipeline works

**The living high-level view.** This file is rewritten with every release. It
explains the machine — what routes a request into it, what each stage refuses to
let past, and what makes any claim it prints believable. The README sells it and
tells you how to install it; this file tells you how it thinks.

> **Version 1.48.0.** The "What changed" section at the bottom carries the last
> few releases. Everything above it describes the pipeline as it is *now*, not as
> it was designed.

---

## The one-sentence version

A coding agent takes a substantial task, interrogates it into a complete brief,
then walks it through **ten gated stages** and refuses to advance until each
gate passes — closing by accounting for every requirement from a list rather than
from memory.

The reason it exists: agents write code well and judge *when to stop asking you
things* badly. Left alone, a substantial task becomes twenty interruptions, or a
confident build that skipped the tests and quietly delivered two thirds of what
you asked for.

---

## 1. How a request finds the pipeline

An agent choosing skills sees exactly one thing: the `description` field in
`SKILL.md`. It is capped at **1024 characters** and currently uses **1008** — that
headroom is the budget every future addition pays from, which is why it is
tracked as a board row rather than left to be discovered.

It is written in three parts, and the middle one was learned the hard way:

- **Work that changes the repository** — a feature, fix, refactor, migration,
  integration, rewrite, adoption or hardening, in English and Russian both.
- **Work whose *output* lands in the repository** — `audit`, `bug hunt`,
  `production check`, `PR review`. Before this clause existed, agents facing
  "проверь, нет ли ошибок" **quoted this skill's own exclusion line as their
  reason to refuse**. The measurement is in `evals/routing/RESULTS.md`.
- **What it is not for** — answering a question, explaining code, a typo, a
  one-line edit. The boundary runs in both directions on purpose: running ten
  stages for one character is the fastest way to teach an agent to route around
  the pipeline entirely.

Two modes need no task at all. `checkup` reports what has shipped without anyone
confirming it. `setup` audits the documentation a project already has.

**Honest limit:** this measures the *description's* discriminating power, not the
host's selection machinery. Three measured runs scored 7/10, 9/10 and 8/10 — and
one sample per query cannot separate an effect from noise, which the measurement
discovered about itself by being run twice.

---

## 2. Preflight — two things settled once

**Model.** The most capable tier the environment offers, named as a *tier*, never
as a vendor id. A hardcoded model id in shipped doctrine is a validator failure,
because it rots the moment the vendor ships a new one.

**Companions.** `super-ux`, `copywriting`, `sheleg-design`, `graphify`, the wiki.
The detection block prints once. A missing companion states its fallback and
**does not block** — the single exception being the stage-3 UX track on
user-facing work, where shipping without it is a decision someone has to make out
loud.

---

## 3. Stage 0 — where the run is won or lost

This is the heaviest stage and that is deliberate. Everything downstream is an
attempt to execute a brief; a bad brief cannot be rescued by good execution.

### The harvest runs before the first question

Pull what the project already knows about *this task*:

| Source | What it uniquely answers |
|---|---|
| the code | what is there |
| **the code graph** (`graphify-out/graph.json`) | **reach** — what calls this, what breaks if it moves. `grep` cannot answer this |
| `CLAUDE.md`, ADRs, `docs/`, `docs/ux/` | what was decided and why |
| **the retro, read in full** | the standing instructions that *bind this run* |
| the knowledge wiki | what past runs distilled |
| the board and the verification ledger | what is open, and what shipped unverified |

The output is a **source ledger** — a row per source, or an explicit *none found*.
An absent source that is never named looks identical to a source that was read.

### Then the grill, and it is mandatory

One question per turn, each with a recommended answer, exploring the codebase
before asking, until every decision branch is resolved.

- **Every answer is validated against the harvested sources.** The operator
  outranks any document — but only *out loud*, and a document the run proves stale
  is logged for stage 9 rather than silently ignored.
- **The autonomy sweep** pre-resolves what would otherwise stop stages 1→10: test
  and lint commands, branch and tracker policy, deploy target and authorization,
  where the logs live. Every question asked here is an interruption that does not
  happen later.
- **UI work adds the design surface** — Figma connected or text-only, and *which
  file*, named before the first frame. A destination decided at drawing time is
  how a project ends up with three design files and no way to tell which is real.

### The brief closes on the REQ table

The request as an **addressable list**, where every row names how it will be
verified. Frozen from here: adding is free, removing needs the operator. Anything
deferred enters the carry-over ledger the moment it is said, not at the end when
it has been forgotten.

---

## 4. Stages 1→10

| | Stage | What must be true to leave it | Gate |
|---|---|---|---|
| 1 | Docs study | every contract the design will lock is grounded on **fetched** docs, not recall | auto |
| 2 | Brainstorm + decompose | design approved, every REQ answered by it. A platform is cut into modules, **walking skeleton first**, every REQ in exactly one module | manual |
| 3 | Spec | contracts locked. User-facing work runs three tracks — what it **does**, how it **sounds**, how it **looks**. A declined track is recorded, never silent | manual |
| 4 | Plan | the REQ set-comparison holds: brief REQs == union of `Implements:` | auto |
| 5 | Build | TDD per task, a review after each, findings fixed or parked **with a ruling** | auto |
| 6 | Tests | the **full** suite green; a web surface checked in a browser, not in the diff | auto |
| 7 | Lint + deploy | the authorization is specific, and the CI verdict is **read** before any tag | manual |
| 8 | Post-deploy | the verification trio, not one of three; a verification row per shipped REQ | auto |
| 9 | Docs + wiki | **three** artifacts — module docs, the wiki, and the code graph | auto |
| 10 | Acceptance | the ladder walk first, then the table, then the retrospective | manual |

### Why the manual gates are where they are

`auto` means the agent verifies the check itself and proceeds. `manual` means it
waits for an explicit go. The four manual gates sit at the four places where a
wrong turn is expensive and hard to reverse: **what we are building** (2), **the
contracts** (3), **the outside world** (7), and **whether it is done** (10).
Everywhere else, stopping to ask costs more than it saves.

---

## 5. The three rules that fire at any stage

**The loop guard.** If a pass starts undoing an earlier one — the same file edited
twice for the same reason, a closed finding returning, a third entry into one
stage — editing stops. Name both shapes, escalate to the layer that owns the
conflict, re-plan as an ordered list, then go item by item. "Cleanup" and "polish"
are explicitly *not* valid reasons for an edit; every change needs one traceable
cause.

**The audit's exit.** If a searching pass starts finding mostly what the previous
pass's own fixes broke, the axis is exhausted. **Rotate the axis — do not look
harder.**

**Evidence.** A green from a check nobody has watched fail against a planted
defect is not evidence. A finding class seen twice becomes a script, not a third
ledger row.

---

## 6. The loop — walking a queue without asking permission

Recorded in `pipeline.json` → `run.loop`:

```
loop:
  mode:  off | interval | dynamic
  queue: module-map | plan-tasks | none
  arm:   preflight | after-decomposition
```

**A loop with no queue is a timer.** The queue belongs to stage 2 — the module map
or the plan's task list. Nothing third is invented. The loop arms at the *close of
stage 2*, when the mode is recorded and the queue holds more than one item.
Between items the goal is re-read, so tasks can be re-prioritised or moved to the
board as the run learns.

The rule that keeps this safe: **arming is the execution of a recorded decision,
not a fresh request. Where nothing is recorded, nothing arms.** Default off.
Silence arms nothing.

---

## 7. The hand-back — what a run says when it stops

Long iterations lose context. So at the end of every iteration, and at stage 10,
the run reports in a fixed shape:

```
TASK               the request AS IT WAS GIVEN, quoted from the brief
PROGRESS           where the run stands against that request
DONE               what was solved, each with its evidence
SURFACED           what came up that nobody asked for
DECISIONS WAITING  <n>   each as a question with options, asked HERE
AMBIGUITIES        <n>   computed from the registers, below
```

Three details carry the weight:

- `TASK` is **quoted, not paraphrased** — the paraphrase is exactly what drifts.
- `DECISIONS WAITING` are asked **here**, not deferred. A missing decision, a
  missing document or an ambiguity left standing is what turns into a large
  consequence three stages later.
- `AMBIGUITIES` is **computed from four registers that already exist** — not a
  fifth document nobody maintains.

It is traced by a `hand:` line in `.task-pipeline/run.md`, beside `stage:`,
`iter:`, `touch:` and `holds:`. That is what makes it a check rather than an intention.

---

## 8. Stage 10 — the close-out, in order

1. **The ladder walk, first.** The REQ table finds what was named and lost; it
   **cannot** find what was never named, because a comparison needs two sides and
   an absence has one. So every REQ is walked bottom-up — decision → spec section
   → contract *and its failure behaviour* → task → change → executed test →
   surface and docs — checking the seam at each step. Findings are ordered **by
   seam, not by file**. Every absence becomes a new REQ row *before* the table.
2. **The coverage table** — one row per REQ, each with evidence. Four statuses
   only: verified, partial, deferred, dropped. `unknown` fails the gate.
3. **The ledgers close.** Every carry-over row still open leaves with a board id,
   and priorities are re-derived. The counts print beside every gate verdict, so
   *green* never reads as *verified*.
4. **Several repositories? The parent closes too.** A submodule can be committed,
   pushed and green while a clone of the parent still gets the commit before it,
   and neither repo looks wrong alone.
5. **The retrospective is the run's last act**, in this order: stamp the run →
   prune every standing instruction against its retirement triggers (list held to
   ten, every deletion logged) → write an entry **only if the run diverged**.

---

## 9. Why you should believe anything it prints

This is the part most pipelines skip, and it is the reason this one is trustworthy
rather than merely tidy.

**Every guard is proven against a planted defect.** `npm run test:all` breaks the
thing each of the **309** checks is about, and requires that check to reject it. A
guard that has never been watched failing is not a guard; it is a comment.

**The neighbour probe.** A check has a *subject* — the rule it is about — and
*evidence* — the text it actually reads. When those differ, it goes green for
reasons unrelated to the rule and no ordinary probe can tell. So: break the
subject, plant the guard's **current** needle next door, and require it to still
fail. Six guards in one session were defeated this way — none of them by their own
probes, all of them by a reader.

**Disclosures are not ratchets.** Alongside every verdict the suite prints what it
*could not* look at — `unlooked: N`, listed by name; `abstained` where a check's
precondition was absent. No floor, no direction, **never a target**. A number that
becomes a target stops being a measurement.

**Corpora are discovered, not listed.** Three hand-written lists each missed a
shipped surface, and none of the misses was found by the guard holding the list. A
new surface joins a check by *existing*.

**The scaffold's own gate runs.** One guard executes `templates/docgate.sh` over a
scratch project seeded from the templates and requires exit `0`. A scaffold whose
gate rejects its own seeds teaches every new project that the gate is noise.

---

## 10. The improvement iteration

The pipeline improves itself on a loop, and the loop is mechanical rather than
aspirational:

```
a run diverges  →  retro entry  →  retro.publish  →  upstream issue
                                                          ↓
   board row  ←  measured against the tree  ←  triaged next cycle
       ↓
   doctrine change + a guard that proves it  →  release  →  the run reads it
```

- **`retro.publish`** turns a lesson that is bigger than one project into a GitHub
  issue on the skill itself. Six such insights arrived in a single day.
- **Issues are resolved, never deleted.** Ones we have worked through are closed
  with a comment naming what they changed. Ones we have not accumulate visibly and
  are picked up in the next cycle. The pile is the queue, and a deleted issue takes
  its number — the one the CHANGELOG points at — with it.
- **A finding closes when behaviour changes**, not when it is understood.
- **A board row is measured against the tree, not read.** Rows have been found
  already closed for two days, and rows whose text was true while the thing they
  described had moved.

---

## What changed, by version

### v1.48.0 — a screen is the frame implemented, and four mechanisms this project owed itself
Figma stops being an address and becomes the source: composition compared against the
node tree, layout read rather than eyeballed, Code Connect used rather than rewritten,
tokens naming their variables — with the honest boundary that a frame is one width, and
a no-frame branch that builds, names, offers to draw, and marks what it drew.
Plus a worktree per agent and a lease before any shared
register — measured at four version collisions in one session — the
SURFACED contradiction check DEC-0001 decided and nobody built, R-006 made readable, a
release path that runs its own suite, and a version guard that fails at the commit
rather than at the merge. Guards: 294 → 309.

### v1.47.1 — the fixes a reader found, which three releases shipped without
Three releases went out from another session while this branch was reviewed, and
each carried the same defects forward: the doc map forbidding the decisions register
shipping beside it, this file naming a version two releases stale, two absolute rules
invertible by an appended clause, a probe demanding PyYAML the harness disclaims, and
a probe that stopped reproducing its own hazard when its target string was quoted —
which leaves `main`'s own suite red. Every one was found and fixed before the first
of those releases; this is them arriving.

### v1.47.0 / v1.46.0 — shipped from another session
A green suite that cannot speak for an agent; and this branch's residue, completion
honesty, proportionate verification and improvement-iteration doctrine, which reached
main through the merge commit rather than through this branch's own release.

v1.46.0 was tagged from a commit carrying this branch's doctrine and none of the
three commits answering its reviewer. The doc map forbade the decisions register
shipping beside it; this file called itself the version it was written under; two
absolute rules were guarded by substring alone and inverted by an appended clause;
and a probe demanded PyYAML the harness disclaims. All four were found and fixed
before the release went out, and arrived after it.

### v1.46.0 — what a run leaves running, what "done" costs to say, what a check is for
Four rules the pipeline had been following by disposition rather than by doctrine.
**Residue**: eight classes of thing a run leaves running or leaves behind, enumerated
by class and never by one tool — the case that produced it was a task inventory
reporting *"No tasks found"* over a live, polling monitor. `holds: N` beside every
gate verdict, a fifth run-ledger line shape, and stage-10 criterion 13: end what this
run started, **report** what it did not. **Completion honesty**: *"done"* names what
makes it true, and the honest negative is a result. **Proportionate verification**:
the deliverable is the working result and the check is how you know — scaled to
`sev × blast`, never by cutting the floor. **The improvement iteration**: a published
issue resolves when behaviour changed and its close names the address; unworked ones
accumulate visibly rather than being triaged into silence. Guards: 275 → 291.

### v1.45.1 / v1.45.0 — shipped from another session while this branch was paused
The reference routing existed three times over and was cut to one home; the guard
count the self-test plants into was restored. Neither is this branch's work — they
are here because they hold the version numbers this branch was originally built
under, which is why it ships as 1.46.0.

### v1.44.0 — six lessons from other projects, and the guards that hold them
Six issues published by runs in other repositories were worked into doctrine:
seam testing at stage 6, `verified by` names that must resolve, a probe's green
being evidence only when the mutation is known to have landed, what a test case
consumes and why a timeout is unclassified, `publish:` as a line in the verdict
rather than a silence, and a ratchet's matcher being itself a check. Twelve new
guards; the suite reached 275. An independent review found eight further defects
in the implementation, all closed before merge.

### v1.43.0 — the hand-back
Long iterations lose the original request. Stage 10 and every iteration boundary
now report TASK / PROGRESS / DONE / SURFACED with decisions and ambiguities
counted, traced by a `hand:` line in the run ledger.

### v1.42.0 — the neighbour probe
Four consecutive releases had guards defeated by independent readers 15, 6, 6 and
8 times, and the trend did not decline. The class: a check answered by text that
is not its subject. The mechanism, with its honest limit stated as a number.

### v1.40.0 — the loop got a queue
`run.loop` previously said *how often* without ever naming *what* the loop walks.
The queue is stage 2's, and the loop arms on it.

### v1.39.0 — findings-shaped work got an entry
Audits, bug hunts, production checks and PR reviews produce output that lands in
the repository, but the routing surface pointed away from them — agents quoted the
exclusion clause as their reason to refuse.

---

## Where to read further

| You want | Read |
|---|---|
| install it, use it | [`README.md`](README.md) |
| change it | [`CONTRIBUTING.md`](CONTRIBUTING.md) — the invariants live there |
| why a release happened | [`CHANGELOG.md`](CHANGELOG.md) |
| the stage doctrine itself | `plugins/task-pipeline/skills/task-pipeline/references/` |
| what is open | [`docs/superpowers/backlog.md`](docs/superpowers/backlog.md) |
| what is genuinely unresolved | [`docs/OPEN_QUESTIONS.md`](docs/OPEN_QUESTIONS.md) |
