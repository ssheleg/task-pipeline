# Continuity — how a run keeps going

Two rules about pacing, in one file because they are two halves of one mechanism.
The loop is what lets a run walk a task list without asking permission between
items. The context budget is what stops that loop from starting an item it cannot
finish. **Neither is useful without the other**, and a run that has the first
without the second fails in a specific, expensive way: it begins task nine with
almost no window left, loses the middle of it, and re-derives what it already did.

## Contents

- The limit, before the capability
- Part 1 — the loop
- Arming it on Claude Code
- Other harnesses, and honest degradation
- What one iteration means
- Parked at a manual gate
- Part 2 — the context budget
- The evidence rule
- What happens at the signal
- The flush is not a new document
- Rationalizations

## The limit, before the capability

**The loop mode collapses discretionary check-ins. It collapses nothing else.**

- A `manual` gate still waits for an explicit operator go. Always.
- An outward or irreversible act — deploy, publish, opening a PR, creating or
  editing a shared design file — still needs its own authorization. A recorded
  loop mode is a **generic** flag, and a generic flag is not a specific
  authorization; that floor is set in [`grill.md`](grill.md) and this file does
  not lower it.
- **Default off.** Absent config and absent instruction, the mode is off. Silence
  arms nothing, exactly as silence authorizes no deploy.

The mode's whole content is the removal of *"should I continue?"* between items
the operator already asked for. Anything beyond that is a different decision,
taken separately.

## Part 1 — the loop

**On, the run advances one item per iteration and does not ask between items.**
This spans the whole run, not one stage:

- the plan's tasks at stage 5;
- the boundary between stages whose gate is `auto`;
- the per-module program loop when the brief was a platform;
- the acceptance → retro tail, which is where runs most often stall one step from
  finished.

It stops for exactly four things: a `manual` gate, a block it cannot resolve, a
genuine ambiguity the brief does not answer, and completion.

**This extends [`build.md`](build.md); it does not replace it.** That file's
*Continuous execution* rule governs the inside of a stage-5 execution — do not
check in between the tasks of a plan you were told to execute. It is unconditional
and stays that way. What it cannot do is reach the other nine stages, or survive
the boundary between one agent turn and the next. This file is that reach.

**Where it is recorded:** `pipeline.json` → `run.loop`. A project sets it once and
is never asked again — which is the entire point. A mode that has to be requested
every run is not a mode, it is a habit the operator maintains by hand.

## Arming it on Claude Code

```
/loop <interval> <the invocation that continues the run>
```

The interval **must divide its unit cleanly** — `5m`, `10m`, `2h` are fine; `7m`
gives uneven gaps and `90m` cannot be expressed at all. A value that does not
divide cleanly is rounded to the nearest one that does, **and the rounding is said
out loud** before it is used.

Pick **the shortest interval that is longer than a typical item.** Shorter buys
nothing: the scheduler cannot deliver faster than the item finishes.

Two properties of the armed job must be stated when arming it, because both are
silent failures otherwise:

- **The job is session-only.** It is not written to disk and it dies with the
  session.
- **It auto-expires after seven days**, firing one last time. A loop that quietly
  stops on day eight is worse than one that was never armed, because the operator
  believes work is still moving.

Where `run.loop.mode` is `interval`, the **preflight arms it** and prints the job
id and the cancel command. Arming is not a new decision at that point — the config
is the recorded authorization, and re-asking would rebuild the habit the config
exists to retire.

## Other harnesses, and honest degradation

`/loop` is **Claude Code only**, in the same way the `PreToolUse` contract in
[`hooks.md`](hooks.md) is. This file names the limit rather than pretending the
mechanism is universal.

On a harness with no loop primitive, the mode degrades to what prose can do: the
discipline in [`build.md`](build.md) plus the build ledger, which is genuinely
useful and genuinely weaker. **Say which one you are running.** A run that reports
itself as looping while nothing is scheduled is claiming a capability it does not
have, and the operator finds out by discovering that nothing happened.

## What one iteration means

One item, taken to its gate.

**A fixed interval cannot interrupt an unfinished item.** The scheduler enqueues
only while the harness is idle — never mid-query. This is the reason the interval
form is safe, and it is worth stating precisely, because the plausible-sounding
alternative explanation is wrong.

**The build ledger is the second line, not the first.** It covers a different
case: a fire that lands after a context loss, where the controller no longer
remembers what it finished. There, `Task <N>: complete` in
`.task-pipeline/build/<plan>/progress.md` is the only DONE marker that counts, and
a task carrying one is never re-dispatched ([`build.md`](build.md)).

Do not write, and do not believe, that the ledger is what makes the interval safe.
Someone will eventually remove the ledger on the strength of that sentence, and
the protection they think they are keeping is in the scheduler.

## Parked at a manual gate

A fixed interval firing into a `manual` gate is a nag. Five minutes later it fires
again, and again, and the operator — who is reading the thing the gate asked them
to read — learns to ignore the loop. That is the same failure as a rule nobody
reads to the end: everyone believes it is covered.

**So the run cancels its own loop job when it parks**, and prints the re-arm
command beside the gate. The go and the re-arm are then one act. This is also the
honest accounting: while the run waits for a person, nothing is looping, and the
job list should agree with that.

**Verify the cancel by listing the jobs, never by the cancel's own reply.** A
teardown call will happily accept an id that was never scheduled and report
success, which leaves the real job running while the transcript says it stopped.
List afterwards and read the list. This is one instance of a named class —
[`gates.md`](gates.md) → *False success*, rule 1 — and a loop is
exactly where breaking it goes unnoticed, because the symptom is a message
arriving on time.

## Part 2 — the context budget

Near the end of the context window, the run does **not** stop and it does not
start anything new:

1. **Finish the item in flight.** A half-finished item is the expensive state.
2. **Start no new item.** An item begun in this window loses its own middle.
3. **Make the ledgers true** (below).
4. **Continue.** Compaction is a normal event, not the end of the run.

The failure this prevents is not running out of room — that is survivable. It is
crossing the boundary *in the middle of something*, so the work either vanishes or
gets done twice.

## The evidence rule

**The rule fires only on evidence**, and there are exactly two admissible kinds:

- **A signal from the harness** — a warning that compaction is near, a `PreCompact`
  hook firing, an explicit low-context notice.
- **The operator saying so.**

Absent both, the threshold has not been observed, and you **never announce that
the context is nearly spent without one of those signals**. No tool returns the
remaining percentage. An estimate from transcript length or how much has been read
is a guess, and presenting a guess as a measurement is precisely the failure
[`learned.md`](learned.md) names — compute, never restate.

This cuts both ways, and the second direction is the one that actually goes wrong:
a run that keeps volunteering *"context is nearly exhausted, start a new session"*
against a mostly-empty window trains the operator to disregard the one time it is
true.

## What happens at the signal

The four acts above, in order, and one prohibition: **do not begin an item you
cannot finish inside what is left.** When the next item is plainly too large,
say so and take the smaller thing that fits — closing a ledger, writing a decision
that is already settled, updating a REQ status.

If the project has recorded that it must not cross a compaction mid-stage, stop at
the stage boundary instead and hand off. That is a project answer, not a default:
the default is to continue.

## The flush is not a new document

Flushing means **making the artifacts that already exist true**:

- the build ledger — every completed task carrying its `complete` line;
- the carry-over ledger — everything deferred, dropped or half-done;
- the brief's REQ statuses;
- the task list.

It does **not** mean writing a summary for the compactor. A summary is a fourth
copy of the truth, it is written once, nobody updates it, and the next run reads
it as current. The artifacts above are read by later stages anyway; making them
right costs nothing extra and pays twice.

## Rationalizations

| Excuse | Reality |
|---|---|
| "The operator obviously wants it to keep going, I'll just loop" | Default off. Silence arms nothing — the same floor deploy authorization uses. Ask once at preflight, or read `run.loop`. |
| "The mode is on, so I can push the deploy through" | The mode collapses check-ins, never gates or outward acts. A generic flag is not a specific authorization. |
| "I'll tell it to keep going and it will" | On Claude Code, prose does not survive the turn boundary. Either a job is scheduled or the run stops; say which. |
| "A one-minute interval is closest to no pause" | The interval must be longer than a typical item, or every fire lands on work already in progress and buys nothing. |
| "The ledger protects me from mid-task fires" | The scheduler not firing mid-query protects you. The ledger covers context loss. Confusing them is how the real protection gets deleted. |
| "It's still looping while we wait for approval" | A loop firing into a manual gate is a nag, and a nagged operator stops reading. Cancel on parking, re-arm with the go. |
| "Context feels tight, I should warn them" | Feels is not evidence. Without a harness signal or the operator's word, the warning is a guess wearing the clothes of a measurement. |
| "I'll write a handoff summary before compaction" | Update the ledgers instead. A summary is a copy of the truth that nobody maintains. |
| "One more task will fit" | If it does not fit, its middle is what you lose — and half a task is the most expensive state there is. |
