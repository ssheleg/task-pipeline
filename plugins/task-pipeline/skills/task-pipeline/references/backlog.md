# The board — the work-list that outlives a run

**One job: give the thing every loop already talks about a file to be.**
[`continuity.md`](continuity.md) says each iteration must re-measure the work-list, and
that *"next up is X"* at the end of an iteration is a claim about the board that no
gate reads. Until this file existed, there was no board — the claim had nothing to be
checked against.

**Boundary, so this does not become a second ledger.** The carry-over ledger
([`templates/carryover.md`](../templates/carryover.md)) records what **one run**
deferred and closes at that run's stage 10. The board is the **project's queue**: it
outlives runs, it is re-prioritised, and rows leave it only by closing. They meet at
exactly one seam, and that seam already existed as a dangling pointer.

---

## Contents

- The seam the ledger left open
- Seeded or picked up
- Priority is computed, not assigned
- What a loop iteration does with it
- Rationalizations

## The seam the ledger left open

The ledger's last column is *Where it lives now*, and one of its legal values is
`backlog` — a place the pipeline named and did not own. So the honest reading of a
finished run was: *"deferred, and filed somewhere nobody here can point at."*

**Stage 10 resolves it, on three triggers.** A row is unresolved if its home reads
`backlog` — the value that pointed nowhere — or `open`, which is what the rows in this
repository actually said, or `unresolved`, which
[`templates/carryover.md`](../templates/carryover.md) calls the canonical not-done value
and says outright blocks this gate. Each of the three was, at some point, described in
the doctrine and absent from the check; a reader found each by seeding the shape and
watching it pass. **The trigger list is the one part of this file that must be read
against the code, not beside it.**

- every unresolved ledger row has a board id, and that id exists on the board;
- every board row sourced from a ledger names the ledger row it came from.

One direction alone is not enough, and this repository has a rule about that
([`learned.md`](learned.md) rule 2): a ledger row pointing at a board id that was never
created and a board row invented with no source are **different failures**, and only a
pass in each direction finds both.

## Seeded or picked up

Stage 0's harvest reads `<artifacts>/backlog.md` when it exists — it is a source
in the ledger like any other, and its **open count is quoted in the brief**, because a
run that begins without knowing what is already queued will cheerfully re-discover it.

When the file is absent, stage 0 seeds it from
[`templates/backlog.md`](../templates/backlog.md) and says so in the brief. Seeding is
not a decision that needs asking: an empty board and no board are the same thing to
work on, and only one of them can be appended to.

**A picked-up board is re-measured, not recalled.** Its open count comes from a command
at the top of the run, not from what the last run's report said — the previous run is
precisely what invalidated that number ([`learned.md`](learned.md) rule 16).

## Priority is computed, not assigned

```
prio = sev × blast + age_bonus        sev, blast ∈ 1..3
                                      age_bonus = 1 past 14 days, 2 past 30
```

**The inputs live in the row and the formula lives here**, so a ranking can be checked
rather than trusted. That is the whole reason the number is built this way: a
hand-assigned priority is an opinion wearing a number's clothes, and the one thing
nobody can audit is the number that was simply typed.

Two consequences worth stating, because both are the point:

- **An old small thing eventually outranks a new medium thing.** That is deliberate. A
  row that has sat for a month is a row the queue has been lying about.
- **A row's priority changes without anyone touching it**, because age moves. The
  re-derivation at the end of an iteration is therefore not busywork — it is the only
  moment the board stops being stale.

`sev` and `blast` are judgement, and they are written down *as* judgement: two small
integers a reader can disagree with, rather than a ranking they can only accept.

## What a loop iteration does with it

At the **top** of an iteration, one command: count the open rows and read the top few.
At the **bottom**, re-derive `age` and `prio`, apply anything the iteration itself
added, and take the highest-priority row.

**A row added mid-iteration may outrank the row being worked on.** That is the case the
board exists for, and it is not a reason to abandon the current item: finish the item at
hand to its gate — `continuity.md` defines an iteration as *one item taken to its gate*
— then take the new top. Switching mid-item is how a loop ends with three half-finished
things and no gate passed on any of them.

**The report cites the file.** *"Next up: B-014"* is checkable; *"next up: the export
fix"* is not, and it is the one sentence in an iteration that no gate reads.

## Rationalizations

| The excuse | What is actually true |
|---|---|
| "The tracker is the backlog, this duplicates it" | Then the `Home` column carries the tracker id and this file is an index with the priority inputs visible. What it replaces is nothing; what it adds is a board an agent can read at 3am without credentials. |
| "I'll re-prioritise when it matters" | Age moves on its own. A board re-prioritised only when someone remembers is ranked by when they last remembered. |
| "The row is obvious, it doesn't need a source" | Six weeks later nobody can tell a finding from a passing thought, and the row is either done twice or dropped by whoever trusts it least. |
| "Priority is a judgement call, a formula can't capture it" | The formula does not replace the judgement — it *exposes* it. `sev` and `blast` are exactly where the judgement lives, and writing them down is what lets somebody argue with it. |
| "I'll drop the row, it's not worth a line in Closed" | Then the next run re-discovers it, re-decides it, and the decision is made twice by people who never met. A closed row costs one line. |
