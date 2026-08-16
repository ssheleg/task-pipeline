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
- A row that says work exists names where it lives
- Priority is computed, not assigned
- A decision is not debt — `waived`
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

## A row that says work exists names where it lives

**`open` claims nothing exists yet. `parked` claims something does — and then has to say
where.** The status cell of a parked row carries a branch or a commit:

```
| B-043 | The exposure command … | 2026-08-14 run | 1 | 0 | 1 | 1.0 | parked — feat/exposure |
| B-044 | The migration script … | 2026-08-15 run | 2 | 0 | 2 | 1.5 | parked — a1b2c3d |
```

The rule exists because a row read as ready-to-merge for two days while its artifacts had
already been deleted. It said *"built and parked … held at `scratchpad/b29-exposure/`"* —
a session-scoped temp directory. When a run finally went to land it, nothing on disk, in
git history, in a stash or in a dangling object held any of it. **A board cannot tell a
claim about a filesystem from a claim about a repository**, and that row was the first
kind while reading like the second.

So:

- **A scratchpad, `/tmp`, or any per-session directory is not a home.** Work that lives
  only there is not parked, it is unwritten — say `open` and describe what is wanted, not
  what supposedly exists.
- **Uncommitted work in a working tree is not parked either.** Another agent's checkout,
  a stash, an unpushed branch on one machine: none of them survives the question *"can
  somebody else pick this up?"*, which is the only question the board is answering.
- **The ref is checkable and that is the point.** `git rev-parse` either resolves it or it
  does not, so a row that has quietly expired can be found before somebody plans around
  it.

**A prose detector was tried first and discarded.** Matching *"parked"*, *"is built"*,
*"ready to merge"* in the description cell fired on **three rows out of 187 and all three
were false** — two closed rows narrating this very incident and the row that asked for
this rule. A check whose every current hit is wrong teaches evasion, and this repository
throws that shape away rather than tuning it. What is gated is the **status cell**, which
is never prose.

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

## A decision is not debt — `waived`

`open` is work not done. `dropped` is an idea abandoned. Neither fits a deliberate **no**
that could be revisited, and putting one in `open` has a cost that only shows up later:
**a decision accrues age exactly like debt, and eventually outranks real work.**

Measured in this family on 2026-08-16. Two rows recorded deliberate decisions on
2026-08-06 — one waiving a UX chain in favour of fixtures, one keeping a skill an audit
because another router carries the design-time rule. They sat `open`. The moment the age
term started being computed they reached the **top** of the board at 2.67 each, and the
next run spent itself re-deriving two decisions that were correct when made and are still
correct.

So:

```
| B-NNN | … | … | 1 | 7 | 3 | — | waived — revisit: <the condition, and how to measure it> |
```

- **Not counted open.** It is not queued work and must not appear as any.
- **No priority.** The cell reads `—`; ranking a decision puts it above things to do.
- **`revisit:` is mandatory.** A waiver with no trigger is a row nobody will reconsider,
  and the trigger must be something a later run can **measure** — *"the command surface
  grows past what the fixtures describe"* is checkable; *"if it becomes a problem"* is not.
- **Still disclosed every run.** A waiver that becomes invisible is how a decision outlives
  the reason for it. It is printed beside the verdict, never counted in it.

**And the revisit condition is re-derived when the row is touched**, like any other claim
([`knowledge-sources.md`](knowledge-sources.md)). Both of the rows above were re-measured
before being waived — 8 commands with 0 uncovered by fixtures, and a router that still
states the rule — because a waiver resting on a condition nobody has checked since 2026 is
the same expired claim in a quieter voice.

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
