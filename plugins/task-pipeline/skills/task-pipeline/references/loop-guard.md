# Loop guard — breaking churn, cross-cutting

Any stage that can repeat can also **churn**: a later pass undoing what an earlier
pass in the same run already did, two shapes alternating, the same file rewritten
round after round with no new information. Churn looks like progress and consumes
a run.

This file is the detector and the break protocol. It binds every repeating loop in
the pipeline: the stage-5 fix loop, a stage re-entered after a failed gate, the
per-module program loop ([`decomposition.md`](decomposition.md)), and any
audit → fix → audit cycle.

**This file governs loops that *change* things.** A loop that *looks* for things —
pass after pass over one corpus — fails differently: it does not oscillate, it
**converges**, quietly spending each pass on the previous pass's own edits while the
finding count stays healthy. That has its own detector and its own exit (rotate the
axis, don't push harder): [`audit.md`](audit.md) → *Every pass changes the axis*.
Both can bind one run. Use this file's trips for edits, that file's crossover for
searches.

## Contents

- Bookkeeping — the thing that makes detection mechanical
- Detection — any one of these trips the guard
- The review loop — a cap that measures rather than stops
- The break protocol
- When to stop and hand back
- Rationalizations

## Bookkeeping — the thing that makes detection mechanical

You cannot detect churn from memory, especially after compaction. Every repeating
pass appends one line to the run's ledger (`.task-pipeline/build/<plan>/progress.md`
for stage 5; `.task-pipeline/run.md` for stage-level and program-level loops —
**seeded at stage 0** from [`../templates/run.md`](../templates/run.md)):

```
touch: <file> — pass <N> (<stage|round|module>) — reason: <finding id / gate item>
```

One line per file per pass. The reason must name **what forced the edit** — a
finding id, a failed gate item, an operator instruction. "Cleanup", "polish" and
"while I was there" are not reasons; they are churn with better manners.

**This ledger was required here from the day the file shipped and written by no run
until 2026-08-10.** The detection below calls itself mechanical; with no ledger it had
no input at all, so the guard sat on rung 1 while every reader took it for rung 3
([`gates.md`](gates.md) → *Axis B*). It is now seeded at stage 0 and named in that
stage's gate — which is the whole difference between a rule and a rule that runs.

## Detection — any one of these trips the guard

1. **Revert-oscillation.** An edit restores something an earlier pass in this run
   deliberately removed, or re-removes what an earlier pass added. Shape A → B → A.
2. **Repeat touch without new information.** The same file is edited in two
   consecutive passes and the second pass's `reason` is the same finding/gate item
   as the first — the fix did not fix it, or the two passes disagree about what
   "fixed" means.
3. **Finding resurrection.** A finding whose text (normalized) matches one already
   marked ADDRESSED or parked-with-ruling in this run comes back.
4. **Gate ping-pong.** The same stage is re-entered for the third time on the same
   artifact, or two adjacent stages hand work back and forth (spec ⇄ plan,
   plan ⇄ build) more than twice.
5. **Cross-loop contradiction.** A pass in one loop edits a file that a *different*
   loop (another task, another module) already closed in this run — two owners for
   one file.

Caps that trip the guard by themselves: **5 fix rounds** per task
([`build.md`](build.md)), **2 re-entries** per stage per artifact, **3 passes** per
module in the program loop, and **3 review rounds** per artifact — which is not a stop
but a measurement, below.

## The review loop — a cap that measures rather than stops

The caps above govern loops that **edit**. A review loop does both: the reader finds,
the run fixes, the reader reads again. It had no cap at all until 2026-08-10, and this
repository's own run stamps say what that cost — **ten rounds, ten, eight, four,
three** — against a stated ceiling of two re-entries per stage. Nothing tripped,
because a review round was named in no cap.

**A flat cap would have been the wrong fix.** Every one of those runs recorded *"none
from my probes"* beside its count: the reader was still finding real defects on round
nine. Stopping at two would have shipped them.

So the cap is a **decision point**. Default **3 rounds** per artifact, recorded in
`pipeline.json` → `run.review.maxRounds`. On reaching it, stop reviewing and print the
pair [`audit.md`](audit.md) already defines — new findings, and findings caused by this
run's own fixes — per round:

```
review cap reached — 3 rounds — artifact: test/validate.py
  round 1: 12 new · 0 self-inflicted
  round 2:  5 new · 1 self-inflicted
  round 3:  1 new · 3 self-inflicted
```

- **Self-inflicted ≥ new** — the axis is exhausted ([`audit.md`](audit.md) → *Every
  pass changes the axis*). Stop. Every remaining finding becomes a board row with its
  evidence ([`backlog.md`](backlog.md)); none is dropped.
- **New > self-inflicted** — the reader is still paying. Continuing is then the
  operator's call, made with the numbers in hand rather than out of fatigue.

**The pair is the whole point.** A round count alone says how tired everyone is; the
pair says whether the loop still produces anything. Measured on one file once, the
guard's shapes and the run's own prose disagreed — one still paying, one exhausted —
so a single number would have stopped the half that was working and continued the half
that was not.

**Rounds are counted from the ledger, never from memory**: distinct `pass N` values on
`touch:` lines at the review stage. A round that finds nothing ends the loop by
definition and needs no counting.

## The break protocol

When the guard trips, **stop editing immediately**. Do not dispatch another fix, do
not "just try one more thing". Then, in this order:

1. **Freeze and name it.** Write the oscillation down in the ledger and to the
   operator: shape **A** vs shape **B**, one line each, plus who is asking for each
   (a finding, the plan's text, the spec, a gate check, an operator instruction) and
   the evidence for each — `file:line`, the failing command, the review verdict.
2. **Find the layer that owns the conflict.** Churn almost always means a decision
   is being re-litigated at the wrong altitude:
   - two findings disagree → the **review rubric** decides
     ([`review.md`](review.md)); if it genuinely doesn't, it's a spec question;
   - a finding contradicts the plan → the **operator** decides which governs
     (never dismiss the finding, never fix against the plan silently);
   - the plan contradicts the spec → back to **stage 4** with the evidence;
   - the spec is ambiguous or wrong → back to **stage 3**, and if the ambiguity was
     an unresolved intake question, say so — that is a stage-0 miss worth recording;
   - two modules claim the same file or entity → back to **decomposition**: the cut
     is wrong.
   **Never resolve a higher-layer conflict inside a lower loop.** Patching code to
   satisfy two contradictory requirements is how a run burns its remaining budget.
3. **Re-plan the check.** Replace whatever ad-hoc verification was running with an
   explicit ordered checklist: every disputed item, one line each, in dependency
   order, with a single owner and a single verification command per item. Write it
   to the ledger before touching anything.
4. **Go in order, one at a time.** Verify item 1 → if it fails, fix only item 1 →
   re-verify only item 1 → commit → item 2. No parallel edits, no bundled fixes, no
   opportunistic cleanup in the same commit. The point is that each change has one
   reason and one proof.
5. **Re-check the whole list once** at the end, in the same order. If a later item
   broke an earlier one, that pair is the real conflict — escalate it per step 2
   instead of looping again.
6. **Record the ruling.** Ledger line: `loop-guard: <A vs B> — ruling: <what governs
   and why> — items: <N> verified in order`. The final review reads it.

## When to stop and hand back

If step 2 lands on "the operator decides", or a cap is hit a second time after a
re-planned pass, **stop and report BLOCKED** with: the two shapes, the evidence, the
history of passes, and your recommendation. That is a complete, honest hand-back —
far cheaper than a third round of the same argument.

## Rationalizations

| Excuse | Reality |
|---|---|
| "One more pass and it converges" | Two passes with the same reason already proved it doesn't. The disagreement is above the code. |
| "The reviewer is still finding things, so keep going" | Then say so with the pair: new versus self-inflicted, per round. If new still leads, that is an argument. Ten rounds with nobody counting is not. |
| "I'll just revert to what worked" | That is the oscillation, not the exit. Name A and B first. |
| "The reviewer keeps changing its mind" | Different findings on the same lines mean the requirement is ambiguous. That's a spec question. |
| "Tidying while I'm in the file" | Untracked edits are what make churn invisible. One reason per change, in the ledger. |
| "Logging the loop is bureaucracy" | Detection needs a record; after compaction the ledger is the only memory that survives. |
| "It's faster than escalating" | A run that spends its budget re-deciding a spec question delivers nothing. Escalation costs one message. |
