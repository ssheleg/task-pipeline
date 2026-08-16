# Exposure — how much unverified work has piled up, and what to look at

**One job: turn the verification ledger into a number somebody can act on, without
pretending it is a probability.**

[`verification.md`](verification.md) records whether a person ever confirmed each shipped
REQ. This file turns that record into the line printed beside every verdict, and into the
list `/task-pipeline checkup` hands an operator.

---

## Contents

- Why it is not a probability
- The components, each named
- The check-list, and how it is ordered
- `/task-pipeline checkup`
- The seeded script
- What the loop does with it
- Rationalizations

## Why it is not a probability

The request that produced this file asked for *"the probability of an error"*. That is
not computable from these inputs, and a number presenting itself as `P(defect)` is the
false-success class this repository has spent its whole history removing: an estimate
wearing a measurement's clothes.

**So no percentage, ever** — the guard rejects a `%` on the exposure line. What ships is
a **vector with its components named**, and the reason is not fussiness: a single score
invites a threshold, and a threshold here is a target on `never`, which is the one thing
[`verification.md`](verification.md) says may never have one.

It could become a real probability later. `verification.md` is exactly the journal that
would make calibration possible after enough runs carry both a confirmation date and a
defect. Until then it is named honestly.

## The components, each named

```
exposure: N unverified · never checked · N releases carry one
```

**The example carries no numbers, deliberately.** It said `99 unverified` and
`31 releases since the last human confirmation` until 2026-08-10 — one figure lifted
from this repository's live count, which drifts, and one wording the code has never
printed. A worked example that disagrees with its own output teaches the wrong format
to every reader who trusts the doctrine over the terminal, and this one disagreed in
both directions at once.

- **unverified** — rows whose `Human` reads `never`.
- **since** — days since the newest `Human` date. When **no** row has ever been
  confirmed, this prints the literal **`never checked`**, not `0 days`: zero would read
  as *checked today*, which is the opposite of the truth and exactly the kind of quiet
  inversion this pipeline exists to prevent.
- **releases** — tags cut since that date, or since the first shipped row when there is
  no date. It is the component an operator feels: *"how much has gone out on top of
  something nobody looked at."*

Every component is derived from files in the repository. None is estimated.

## The check-list, and how it is ordered

The list is the deliverable — a number without it tells somebody they have a problem and
not where. Ordered by what the repository can defend:

1. **Oldest first**, by `Shipped in`. The longest-unconfirmed row is the one whose
   context is most gone, and whose author is least likely to remember it.
2. **Tie-broken by blast radius** where the board carries a row for it, reusing
   [`backlog.md`](backlog.md)'s own stated input rather than inventing a weight here.

No third factor. A ranking with an unstated input is the hand-assigned priority the board
already refuses.

## `/task-pipeline checkup`

A **mode of the command**, like `setup` — not a new command, because a second command
costs every surface a command touches and this repository has learned what that means.

**It runs with no task in flight, and that is the point.** Accumulated unverified work is
invisible *precisely because nobody is running a pipeline*; a check that only exists
inside a run can never say *"stop, fourteen things are unconfirmed."* So it takes no
brief, opens no grill, and writes nothing on its own.

It prints four sections, each read from a file this pipeline already keeps: the exposure
line and its check-list, the board's open rows by computed priority, the carry-over
ledgers' unresolved count, and the code graph's staleness where one exists.

**Where the operator asks it to file findings**, it appends board rows whose `Source`
names the checkup and its date — so a row a machine created is distinguishable from one a
run surfaced. It prints what it would add first. Never silently.

## The seeded script

[`../templates/exposure.sh`](../templates/exposure.sh) computes the line and the
check-list from the two files above, so a project gets the number without an agent in the
room. Seed it the way the gate is seeded:

```bash
cp <skill>/templates/exposure.sh  scripts/exposure.sh    # only if absent
chmod +x scripts/exposure.sh
```

**It exits 0 whatever the number is, and that is load-bearing.** A threshold here would
be a target on `never`, and this file has already said that column may never have one —
the moment *"unverified must be under ten"* exists, the cheapest way to satisfy it is a
date nobody earned. Exit 1 means the ledger is present and unreadable, which is a
different fact and deserves a different code.

Two of its behaviours exist because the alternative lies in the reassuring direction. A
project with no ledger prints `dormant:` rather than a clean zero, and a check-list that
cannot be built is a failure rather than an empty section under a non-zero count — the
first draft's `sort` died on a non-ASCII `What` column, printed its error to stderr, and
left a confident number above nothing at all.

## What the loop does with it

[`continuity.md`](continuity.md) has always required each iteration to re-measure the
work-list, and said that *"next up is X"* is a claim about the board that no gate reads.
[`backlog.md`](backlog.md) is that board; the exposure line is the other half of the same
measurement, and both are read at the top of an iteration and re-derived at the bottom.

An iteration that reports what it will do next **cites the file**: `B-014`, not *"the
export fix"*.

## Rationalizations

| The excuse | What is actually true |
|---|---|
| "Give me one number, I'll decide the threshold" | The threshold would be a target on `never`, and the column would start lying within a week. The components are one line; read them. |
| "A percentage is easier to communicate" | It is easier to communicate because it says more than is known. That is the whole objection. |
| "The check-list is long, just show the top three" | Then the fourth is never checked and nobody knows it exists. Print it all; the operator can stop reading. |
| "Checkup duplicates stage 8" | Stage 8 verifies **this run's** deploy. Checkup asks what has accumulated across all of them, which no stage is ever in a position to ask. |
| "We'll run checkup when something breaks" | After a break you know where to look. The list exists for before. |
