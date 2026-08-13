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
- "Done" is a claim, and it names what makes it true
- Every number is borrowed
- Absent is a word, never a zero
- The `holds:` line — what the run is still holding
- The observation beside the claim
- The run's own lifecycle
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
can be checked against `<artifacts>/backlog.md`; *"next up: the export fix"*
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

**At the close of an iteration, and again at stage 10.** This is *not* the pair named
three sections above: *The two boundaries, and only those two* governs the **rail**, and
its pair is task start and iteration close. The hand-back shares one and adds the run's
end — a rail at task start has nothing to report, and a run that ends without a hand-back
is the case this section exists for. A reader resolving *"both boundaries"* against the
other section wrote one at task start, where TASK is the only field with content. The run
writes a hand-back with **four sections and two lists**. It is a gate criterion **at stage
10**, not a good intention: this file already carried one instruction with no gate behind
it (*"copy it, tick it"*), and the v1.37.0 audit found no run had ever obeyed it.

**The iteration-close instance has no gate, and that is a weakness rather than an
oversight** — an iteration boundary has no verdict to hang a criterion on. It is
therefore the very shape the sentence above indicts, written inside it. What keeps it
from being *"copy it, tick it"* is the run ledger: the iteration line already lands there,
and the hand-back lands beside it, so a later audit has something to read. Where a project
keeps no ledger, the iteration hand-back is prose discipline, and the run says which of
the two it is running.

```
── hand-back · <topic> · iteration <n> ───────────────────────────
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

**Where there is no brief** — `checkup`, `setup`, a short path — TASK quotes the
operator's own sentence instead, marked as such. An unquotable TASK is a run that cannot
say what it was asked, which is worth its own line.

**Where it lands.** The narrative goes to the operator; the trace goes to the run
ledger as a `hand:` line ([`../templates/run.md`](../templates/run.md)). Without it the
hand-back is a gate criterion with no artefact — a reader proved that of v1.43.0's
first draft: every guard could check the instruction was still written, none could
check a run obeyed it, and an audit a year later could reach no verdict either way.
`grep -c '^hand:'` against `grep -c '^iter:'` is what makes the difference readable.

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

| Source | What it means | Read by |
|---|---|---|
| open `OQ-####` rows ([`documentation.md`](documentation.md)) | a question raised and never answered | `grep -cE '^\| OQ-[0-9]+' docs/OPEN_QUESTIONS.md` — **no file prints `— no register`, never `0`** |
| carry-over rows whose home is unsettled | deferred into nothing ([`../templates/carryover.md`](../templates/carryover.md): `open`, `unresolved`, or a bare `backlog`) | `grep -cEi '\\|[[:space:]]*(open\\|unresolved\\|backlog)[[:space:]]*\\|' <ledger>` |
| REQ rows whose check is `review` rather than a command | shipped on judgement, unverifiable by a machine | the brief's REQ table, *Verified by* column. The count `spec.md` prints is **checks**, not REQ rows — different units, and quoting one for the other is a borrowed number that does not fit |
| source-ledger rows with **no source** | the run built on the absence of a document | the brief's ledger, rows whose *Source* cell is empty or parenthesised. `knowledge-sources.md` writes them `(none for X)` while `templates/brief.md` writes `none found`, so **a grep for either string alone returns a false zero** |

The `Read by` column is the point of the table. Without it, *"each read by a command"* is a
claim the section makes about itself and cannot keep — and one of the four greps would
have returned zero for searching a string the source ledger's own doctrine never writes.

Each prints its count **and its ids**. A count with no ids is a number nobody can act on,
and **zero prints as zero** — silence and "I looked and found none" are the two states
this file exists to keep apart.

**One of the four is structurally zero at the gated boundary.** Stage 10's own gate
already requires that no carry-over row is left unresolved, so there that count is zero
**because a sibling clause compelled it**, not because the run looked. At an iteration
close it is a real measurement. Print it either way, and at stage 10 print *why* it is
zero — a number that had no choice is not evidence.

**Why these four and not a fifth.** Every one is already written down by an earlier stage,
so the hand-back reports rather than re-derives, and a run cannot quietly decide that
nothing was unclear. Where a project keeps no open-questions register, that row prints
`— no register` rather than `0`: an absent register and an empty one are different facts,
and the second is the one worth acting on.

## "Done" is a claim, and it names what makes it true

Every disclosure in this bundle answers *what does it print when it did not look?*
That question is asked of **checks**. It has to be asked of the run's own sentences
too, because the sentence reaches the operator and the check does not.

**A completion claim names what makes it true, or it is not a completion claim.**
`done: the export writes UTF-8` is a claim. `done: the export writes UTF-8 —
`test_export_encoding` green at 5f21ac3` is a report. The difference is not
politeness; it is whether anyone can disagree with you.

Three ways a run reports something it did not do, none of them requiring an
intention to mislead:

| The shape | What was actually true | What to write instead |
|---|---|---|
| **The plan reported as the outcome** — "added the retry" after writing the code and before running anything | the edit landed | `done` names the executed test, or the item is not `done` |
| **The reply reported as the result** — a deploy, a teardown, a cancel, an API call that returned success | the call was accepted | re-read the state; the second look is the evidence, the reply is not |
| **The part reported as the whole** — "tests pass" after running the file you touched | that file's tests pass | say which suite, or run the full one |

**And the honest negative is a result.** *"Not done — the fixture needs a
credential I do not have"* is a complete, useful report. *"Done (with a small
caveat)"* for the same situation is not. A run that cannot finish something says
so at the boundary it reached, names what would unblock it, and moves to the next
item — `deferred` and `partial` exist as statuses precisely so that stopping does
not have to be dressed up as finishing.

**The status vocabulary is closed for the same reason.** Stage 10 takes
`verified`, `partial`, `deferred`, `dropped` — and `unknown` fails the gate
([`acceptance.md`](acceptance.md)). A fifth word invented at write-time is how a
run reports a state nobody agreed to read.

## Every number is borrowed

| Field | Its home |
|---|---|
| `board B-NNN` | `<artifacts>/backlog.md` ([`backlog.md`](backlog.md)) |
| `carry-over N rows` | the run's carry-over ledger, as printed beside every gate verdict |
| `exposure N never` | `<artifacts>/verification.md` ([`exposure.md`](exposure.md)) |
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

## The `holds:` line — what the run is still holding

Beside every gate verdict the run prints `holds: N` — the environment it has not
given back. It lands in the ledger as a `holds:` line
([`../templates/run.md`](../templates/run.md)), one per gate that found anything,
and one at stage 10 whatever the count.

```
holds: 5 — 2 (worktree: build-csv-export, this run; container: pg-test, this run) — enumerated 8/8 classes
holds: 10 — none — enumerated 7/8 classes, unlooked: containers (no docker on this host)
```

Three things make the line worth writing rather than a habit:

- **It names the class and the owner, not just a number.** *"2"* tells the next
  run nothing; *"worktree, this run"* tells it what to end and what to leave.
- **It records how many classes were enumerated.** `8/8` and `7/8, unlooked:
  containers` are different facts, and a run without container tooling must print
  the second rather than a clean zero it did not earn.
- **`SURFACED: 0` is checked against what the run filed.** A run that opened a board
  row, a carry-over row, an open question or a retro entry has provably surfaced
  something; reporting zero contradicts its own artefacts, and that disagreement is
  computable from the `Source` column every board row carries. The residual belongs
  in the same sentence: a run can surface something, file it nowhere, report zero,
  and **nothing will notice** — this check kills the silent zero, not the blind spot.
- **It is a disclosure, never a ratchet.** No floor, no direction, no target. A
  build stage legitimately holding a worktree and a database prints `2` and
  passes; a run that tears its database down to make the number tidy and brings
  it back up next stage has spent time making a measurement lie.

Doctrine, including the eight classes and what must **not** be torn down:
[`residue.md`](residue.md).

## The observation beside the claim

A `stage:` verdict is written by the agent. Since v1.51.0 the ledger also carries

```
gate:  <stage id> — command "<cmd>" — exit <N> — <ISO-8601>
```

written by `hooks/gate-observer.sh` and by nothing else: the **observed** exit code
of the command the project declared in `pipeline.json` → the tests stage's
`gate.command`. The rail does not read it — a glyph still comes from the verdict —
but the stage-7 release gate requires the claim and the observation to agree.

The reason is the one this whole file is about, arriving one level down. A rail
written from memory is a summary that is confidently wrong exactly when it matters;
a gate that reads a verdict typed by the agent it constrains is the same shape
again, and it looks like enforcement while being a mirror.

## The run's own lifecycle

Three moments the rail cannot show, recorded by `hooks/run-lifecycle.sh` as

```
event: <compact|session-end|subagent> — <detail> — <ISO-8601>
```

The rail reads none of them; `checkup` reads `session-end`, which is how an
abandoned run stops being invisible. Before this the ledger simply stopped at
whatever stage the session died on — and a stopped ledger is indistinguishable
from a run still in progress, which is the exact shape *absent is a word, never a
zero* exists to refuse.

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
