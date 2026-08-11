# Progress — saying which pipeline this is, and where in it

**One job: make the run's position a printed fact instead of something the operator
reconstructs from the last thing that scrolled past.**

A pipeline that never says where it is has one specific failure, and it is not
confusion — it is that **a stage looks done because nothing printed**.
[`stages.md`](stages.md) opens with a checklist for exactly that reason and then marks
it *"copy it, tick it"*: an instruction with no gate behind it, which is rung 1
behaving like rung 3 ([`gates.md`](gates.md) → *Axis B*). This file is that checklist
promoted to something the run must emit.

**Boundary.** This file decides **what is printed and when**. It decides nothing about
what is true: every number on the block has a home somewhere else and is read from
there. A progress line that computes its own counts is the fourth copy of the truth,
and [`continuity.md`](continuity.md) already says what happens to those — nobody
maintains them and the next run reads them as current.

---

## Contents

- The two boundaries, and only those two
- The header block
- The iteration line
- The rail is computed, never eleven
- What each glyph means
- The hand-back — what the operator reads when you stop
- Every number is borrowed
- Absent is a word, never a zero
- The run ledger this reads from
- Rationalizations

## The two boundaries, and only those two

**Task start** and **iteration close**. Nothing else.

An iteration is already defined — *one item taken to its gate*
([`continuity.md`](continuity.md) → *What one iteration means*) — and that definition
is what makes this cheap. Printing per agent turn would put a bar above every tool
call, and a block that appears fifty times a run is a block nobody reads, including
the one time it says something.

Between the two boundaries the run prints whatever it normally prints. This file adds
no narration.

## The header block

Emitted **once, before stage 0's first question**, and again whenever the module
changes:

```
task-pipeline v1.34.0 · pipeline-audit · module P1 «the progress print» (1 of 4)
  0 ✓  1 ✓  2 ✓  3 ▶  4 ·  5 ·  6 ·  7 ·  8 ·  9 · 10 ·
  ███████░░░░░░░░░░░░░░░░░░░  gates 3/11 · now 3 Spec · manual
  board B-028 · carry-over 0 rows · exposure 99 never · unlooked 0
```

Four lines, and each one answers a question an operator otherwise has to ask:

| Line | Answers |
|---|---|
| 1 | *which skill, which version, which programme, which module of how many* |
| 2 | *which stages are closed, which one is live* |
| 3 | *how far along, what is running now, will it stop for me* |
| 4 | *what is queued, what is deferred, what nobody has confirmed* |

**The module segment is omitted when there is no module map.** A task that stage 2
never decomposed has no module, and printing `(1 of 1)` turns an absence into a claim
— the shape [`audit.md`](audit.md) is built around. Where stage 2 recorded `single
module: <name>` ([`decomposition.md`](decomposition.md)), print that phrase instead.

## The iteration line

Emitted at the **close** of every iteration, one line:

```
▶ pipeline-audit · P1 (1/4) · 5 Dev auto · iter 3 · gates 5/11 · next B-025
```

**`next` cites a `B-NNN`, never a description.** That rule is
[`continuity.md`](continuity.md)'s and it is the reason this line exists at all:
*"next up is X"* was already the one sentence in a loop that no gate reads. A board id
can be checked against `docs/superpowers/backlog.md`; *"next up: the export fix"*
cannot.

**Nothing queued is `next —`, printed.** A loop that reaches an empty board says so;
omitting the field is indistinguishable from forgetting it.

## The rail is computed, never eleven

The stage ids on the rail come from the project's `pipeline.json` → `stages[]`. They
are **not** the eleven in [`../pipeline.example.json`](../pipeline.example.json), which
is this plugin's *example* flow — a host project replaces it with its own stages
(`SKILL.md` → *Bring your own skills*).

A bar reading `gates 5/11` in a project with six stages is a false success in the
purest form the pipeline has: a summary that is confidently wrong about the thing it
summarises, printed in the place designed to be trusted at a glance.

So the rail carries **no stage count of its own**. Read the array, print what is in it.
Six stages give six positions.

## What each glyph means

| Glyph | Means | Written when |
|---|---|---|
| `✓` | the stage's **gate passed** | the gate's own verdict was recorded |
| `▶` | in flight | the stage was entered and its gate has not returned |
| `·` | not entered | — |
| `✗` | entered, gate returned a failure | the verdict said so |
| `⊘` | skipped, **with the reason on the same run's record** | the short path, or a stage the brief excluded |

**`✓` means the gate passed — not that the stage was walked.** This is the whole
integrity of the block. A rail is a summary, and a summary is the easiest artefact in
a run to write from memory rather than from the record; a glyph set by recollection is
[`gates.md`](gates.md)'s *false success* with a nicer typeface. Derive each glyph from
the verdict the gate wrote, in the run ledger, and from nothing else.

**`⊘` may never be silent.** A skipped stage with no recorded reason is exactly what a
`·` looks like from outside, and the two mean opposite things.

## The hand-back — what the operator reads when you stop

The rail says **where** the run is. It does not say what happened, and a reader who was
away cannot reconstruct that from a glyph. Measured on this project: a fourteen-iteration
session where the operator returned to a one-line rail each time and had to ask.

**At both boundaries** — the close of an iteration and the close of stage 10 — the run
writes a hand-back with **four sections and two lists**. It is a gate criterion at stage
10, not a good intention: this file already carried one instruction with no gate behind
it (*"copy it, tick it"*), and the v1.37.0 audit found no run had ever obeyed it.

```
── hand-back · <topic> · iteration 3 ─────────────────────────────
TASK        the request as it was GIVEN, quoted from the brief — not
            as it looks now that you understand it
PROGRESS    where the run stands against that request: gates passed,
            what remains, and the board id it is heading for
DONE        what was solved this iteration, each with its evidence
SURFACED    what came up that nobody asked for — findings, corrections,
            things that turned out to be other than assumed

DECISIONS WAITING  <n>   each as a question with options, asked HERE
AMBIGUITIES        <n>   computed, below
```

**TASK is quoted, never paraphrased.** A run that restates the request in its own words
after eight iterations has rewritten it, and the operator cannot see that happen. The
quote is the one line the drift shows against.

**SURFACED is the section that earns the hand-back.** Everything else is recoverable from
the artefacts; what a run *learned by accident* is recoverable from nothing. A run that
found a stale claim, corrected a number, or discovered a rule was never enforced puts it
here even when it was fixed in passing — especially then.

**DECISIONS WAITING are asked, not listed.** A question parked in a report is a question
the operator answers days later, if at all. Ask it at the boundary, with options and a
recommendation, in the same breath as the report. If there are none, the field prints
`0` — [`gates.md`](gates.md)'s rule about absence applies here too.

### AMBIGUITIES are computed from four registers the run already keeps

Not judgement, and not a prompt to think harder — an unbounded *"is anything unclear?"*
becomes a ritual sentence within three runs. Four sources, each read by a command:

| Source | What it means |
|---|---|
| open `OQ-####` rows ([`documentation.md`](documentation.md)) | a question raised and never answered |
| carry-over rows with no home | deferred into nothing |
| REQ rows whose check is `review` rather than a command | shipped on judgement, unverifiable by a machine |
| source-ledger rows reading *none found* | the run built on the absence of a document |

Each prints its count **and its ids**. A count with no ids is a number nobody can act on,
and **zero prints as zero** — silence and "I looked and found none" are the two states
this file exists to keep apart.

**Why these four and not a fifth.** Every one is already written down by an earlier stage,
so the hand-back reports rather than re-derives, and a run cannot quietly decide that
nothing was unclear. Where a project keeps no open-questions register, that row prints
`— no register` rather than `0`: an absent register and an empty one are different facts,
and the second is the one worth acting on.

## Every number is borrowed

| Field | Its home |
|---|---|
| `board B-NNN` | `docs/superpowers/backlog.md` ([`backlog.md`](backlog.md)) |
| `carry-over N rows` | the run's carry-over ledger, as printed beside every gate verdict |
| `exposure N never` | `docs/superpowers/verification.md` ([`exposure.md`](exposure.md)) |
| `unlooked N` | the gate's own disclosure ([`gates.md`](gates.md) → *Disclosures*) |
| `gates N/M` | the run ledger's verdict rows, and `pipeline.json` → `stages[]` |

**None of these is recomputed here.** If a number on the block disagrees with the
number beside a gate verdict, the block is wrong — that direction, always, because the
gate looked and the block quoted.

This also settles what the block is *not*: it is neither a ratchet nor a disclosure of
its own ([`gates.md`](gates.md) → *Ratchets*, *Disclosures*). It sets no floor and
carries no target. It is a **restatement with a citation**, and the citation is the
only reason a restatement is allowed here at all.

## Absent is a word, never a zero

Where a value does not exist, print the word:

```
board — · carry-over 0 rows · exposure — · unlooked 0
```

`exposure —` says *no verification ledger in this project*. `exposure 0` says *nothing
is unconfirmed*, which is the opposite claim, and it is the same inversion
[`exposure.md`](exposure.md) refuses when it prints `never checked` rather than
`0 days`. A zero standing in for an absence is how a project learns it is safe.

`carry-over 0 rows` **is** a real zero and prints as one: the ledger exists and holds
nothing.

## The run ledger this reads from

`.task-pipeline/run.md`, seeded at stage 0 from
[`../templates/run.md`](../templates/run.md), one file per run.

It already had a second owner before this file existed:
[`loop-guard.md`](loop-guard.md) names it as the record that makes churn detection
**mechanical**, and calls it the only memory that survives compaction. It was never
written by any run — the detector had no input, and the guard was doctrine wearing a
script's clothes. One file serves both readers: the guard reads the `touch:` lines,
this block reads the verdict rows and the iteration counter.

Three kinds of line, appended, never rewritten:

```
stage: 3 Spec — gate manual — verdict pass — 2026-08-10T14:02Z
iter:  3 — item B-025 — closed at gate 6
touch: test/validate.py — pass 2 (stage 7) — reason: F-014
```

**The counter is a count of `iter:` lines, not a number the agent remembers.** After a
compaction the agent's memory of "iteration 3" is gone and the file's is not, which is
the entire argument for keeping it on disk rather than in the reply.

## Rationalizations

| The excuse | What is actually true |
|---|---|
| "The operator can see the stages scroll by" | They can see that *something* printed. A stage that ended silently and a stage that never started look identical in a transcript, which is the failure `stages.md`'s checklist was written for and never enforced. |
| "A progress bar is decoration" | Then delete the numbers and keep the bar. The objection is really to the bar; the four borrowed counts are the payload, and they are the ones nobody prints today. |
| "I know which stage I'm on, I'll write the rail from memory" | Then the rail is a claim about the run rather than a reading of it, and it will be right until the run it most matters on. Derive it from the verdicts. |
| "There's no module map, I'll put (1 of 1)" | An undecomposed task has no module. `(1 of 1)` is an invented denominator, and a reader cannot tell it from a real one. |
| "Printing it every iteration is noise" | One line. The block is four, and it appears at task start. If that is noise, the run is emitting far worse elsewhere. |
| "The ledger is bureaucracy, I'll count iterations in my head" | Your head does not survive compaction. That is not a hypothetical here — it is why `loop-guard.md` asked for this file in the first place. |
