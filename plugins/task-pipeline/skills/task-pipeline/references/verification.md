# The verification ledger — the column a machine may not fill

**One job: record whether a human ever looked at what shipped, and when.**

Stage 8 already performs the verification trio, reads the CI verdict and opens the
rendered page ([`stages.md`](stages.md) → *8 — Post-deploy*). All of it is **per run**,
and none of it accumulates. Ask a project *"which features has nobody confirmed since
they shipped?"* and before this file the honest answer was: nobody knows, and no
artifact could be consulted.

**Boundary, so this is not a second coverage table.**
[`acceptance.md`](acceptance.md)'s table says *an automated check passed at the moment of
the run*. Three things it does not say, and each is why this file exists:

- whether anybody **looked** after it shipped;
- whether it still works N releases later;
- anything at all about previous runs — it is per-run and dies with its run.

---

## Contents

- Why it keys to the brief, not to the coverage table
- `never` is a fact
- A ledger records two different things, and most record only one
- What stage 8 writes and what stage 10 refuses
- Rationalizations

## Why it keys to the brief, not to the coverage table

The obvious spine is the coverage table — it already carries one row per REQ with a
verdict. Measured before building on it: **ten acceptance files in this repository, and
the first REQ-bearing table differs in nearly every one.** Ladder walks and coverage
tables share a file with different columns, because `acceptance.md` fixes the shape in
prose and prose does not hold a shape across ten runs.

The brief's REQ table does: **eight of nine briefs here carry machine-readable
`| REQ-NNN |` rows**, and the ninth was fixed the day this was measured. So the ledger
keys to the brief, and the coverage table remains what it always was — the run's own
verdict, quoted into the `Auto` column and never re-derived.

That the coverage table has no template and has already drifted is a real finding with a
real cost, and it is on the board rather than fixed here: a run that widens its own scope
to fix everything it touches finishes nothing.

## `never` is a fact

A `never` is not a defect, not a debt, and **not a number to drive down**. It is what is
true about the world, written where somebody can act on it.

The moment `never` becomes a thing to avoid writing, the column stops describing
reality — and this is the pipeline's only signal about the world outside its own checks.
So the count has **no floor, no direction, and may never be given a target**, exactly
like the disclosures in [`gates.md`](gates.md). A project with forty `never` rows is not
failing; it is a project that now knows something it could not previously ask.

## A ledger records two different things, and most record only one

**What confirmed it** and **whether a person looked** are separate facts. The first is
evidence: a command, a CI run id, a fixture name. The second is the `Human` axis, and it is
the one the exposure line is defined over.

A ledger may carry either or both, and most carry only the first. Measured across this
family on 2026-08-16 — nine repositories, **ten** header shapes, **815** rows:

| what the state column can say | rows | repositories |
|---|---|---|
| whether a **person** looked (`Human`) | **126** | 1 |
| a date and what was watched (`Last verified`) | 180 | 1 |
| `verified` — by a person **or** a command, indistinguishable | 391 | 4 |
| nothing: the ledger records evidence and carries no state column | 118 | 3 |

So **`never` is measurable in one repository of nine, over 15% of the rows**, and the exposure line — which this
doctrine defines over it — is undefined in the rest. That is not a defect in those
ledgers. Recording *what confirmed it* is the Auto job done properly, and a project that
never asks the human question is making a choice.

What is a defect is **doctrine that speaks as though the column were there**. So:

- **Where there is no state column, the exposure line says so** and prints no number.
  `templates/exposure.sh` reports `dormant` and names the column headings it looked for.
  A zero would be the reassuring answer to a question nobody asked.
- **A `verified` that cannot separate a person from a command may not be reported as
  human confirmation.** The script names the column it read, for exactly this reason.
- **Adding the column later never reaches backwards.** New rows start at `never`;
  retrospective statuses for work nobody actually checked are the failure the
  `evidence-docs` router exists to name, and a back-filled ledger is worse than an absent
  one because it answers the question wrongly instead of not at all.

## What stage 8 writes and what stage 10 refuses

**A coverage verdict of `review` becomes `none`.** *No check can decide this* is not
a pass; `Auto` records what a machine established, and there the honest answer is
nothing. The first seed wrote `pass` for four such rows — in the file whose whole
purpose is not to do that.

**Stage 8** writes one row per REQ the run shipped, right after the verification it
already does. `Human` starts at `never` unless the operator confirmed during the run.

**A REQ that spans two modules is stamped with the second, not the first.** Its criterion
is satisfied when the last part of it exists, and stamping the earlier release claims a
capability the project did not yet have. Caught by a reader on the first ledger this
skill ever seeded: one row said a file was named in the maps a release before that file
existed, and the row directly below it said when the file arrived. Two rows of one
table, disagreeing about the same date.

**Stage 10** refuses a REQ that shipped and has no row — and, in the other direction, a
row whose REQ appears in no brief. They are different failures: a shipped feature that
entered no ledger, and a ledger row about nothing. One direction alone finds one of them
([`learned.md`](learned.md) rule 2).

**Nothing else writes here.** Not a script, not the release job, and not stage 10 — a
file that several stages may write is a file whose rows nobody owns.

## Rationalizations

| The excuse | What is actually true |
|---|---|
| "The tests passed, that *is* verification" | The tests passed *at the moment of the run*, against the checks somebody thought to write. This column is about the world, and the world is where the checks were not looking. |
| "I'll fill `Human` in when I get to it" | Then the row says `never`, which is exactly correct until you do. The file is not asking you to lie faster. |
| "Forty `never` rows looks terrible" | It looks like what it is. The alternative is forty unverified features and no way to name them, which looked fine right up until it didn't. |
| "Stage 10 can fill it — it runs after the deploy" | Stage 10 is a machine. The single thing this column means is *a person looked*, and a machine writing it deletes the only information in the file. |
| "We tag rarely, so `Shipped in` is awkward" | Then it carries the commit, and every row of that run carries the same one. What it may not carry is nothing. |
