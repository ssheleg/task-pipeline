# Prioritisation — what to do next, and why that and not the other thing

**Load this when** the task was not named, when the next row comes off the backlog, when
the operator asks what to work on, or when a run is about to spend a day on something and
nobody has checked that it is the most valuable day available.

`backlog.md` owns the **board** — what a row is, where it lives, how it closes. This owns
the **order** the rows come off it.

## Contents

- The default, and its one exception
- 1. The impact ladder
- 2. Confidence and Ease
- 3. The order, and why it is not a product
- 4. Research before scoring, not after
- Effort does not rank a finding, but the fixer needs a cost rule
- 5. Where the human goes
- 6. Two models in one family, and why both are right

## The default, and its one exception

**Every run assumes a backlog exists and that this task competes with it.** A task arriving
with no stated priority is not priority-free; it is unranked, which is a different and
worse thing.

**The exception is the operator, and it is absolute.** When they name the task, that is the
task. The most this file authorises is **one line** — *"`BL-14` scores higher: a checkout
error affecting paying users. Say the word and I switch; otherwise starting yours now"* —
and then starting theirs. Not a second ask, not a hedge, not a silent substitution. An
operator who knows what they are doing is the most reliable prioritiser in the system, and
an agent that argues with them twice has made itself expensive to use.

## 1. The impact ladder

Impact is the rung, not a feeling. The ladder exists so a bug and a feature can be compared
at all — without it, "impact" is scored per-item by whoever is looking, and every item is
somebody's priority.

| Rung | What it means | Test |
|---|---|---|
| **I5** | the product does not work for someone **right now** | data loss, an outage, a broken purchase, a blocked signup |
| **I4** | a product or business metric moves | revenue, activation, retention, traffic, conversion |
| **I3** | it works, and the experience degrades | crash-free rate, error rate, latency, a rough edge people hit |
| **I2** | our own speed | debt, tooling, tests, anything that changes how fast the next thing ships |
| **I1** | polish | nobody's metric moves; it is better and that is all |

Two rules that carry most of the value:

- **An unmeasured claim of I4 is I3 until it is measured.** "This will lift conversion" is
  a hypothesis; the rung is what the evidence supports, and the gap goes in Confidence.
- **Blocking is not a rung, it is a multiplier on someone else.** A task nobody can proceed
  past inherits the highest rung it blocks. State whose work it blocks, or it is not
  blocking — it is just old.

## 2. Confidence and Ease

Both are 1–3, both are judgement, and both are written down **as** judgement — small
integers a reader can disagree with, in the row, next to the rung.

**Confidence** — how sure are we that doing this produces the effect claimed?

| | |
|---|---|
| **C3** | measured, or the mechanism is obvious and the change is local |
| **C2** | reasoned from something real — a trace, a ticket, one user |
| **C1** | a guess we believe. Fine to hold, not fine to hide |

**Ease** — how cheap is it, including the parts nobody counts?

| | |
|---|---|
| **E3** | within a run, one surface, reversible |
| **E2** | a few surfaces, or one that needs coordination |
| **E1** | crosses repositories, needs a migration or a credential, or cannot be undone cheaply |

Ease counts the **whole** cost: the migration, the review, the rollback, the second
repository. An E3 that turns out to need a credential from a person who is asleep was an E1
and the estimate was the defect.

## 3. The order, and why it is not a product

```
sort by   I    descending          the ladder dominates
then by   C × E descending          1..9 within the rung
then by   age  descending           the tie-break, oldest first
```

**Classic ICE multiplies I × C × E, and this deliberately does not.** Multiplying lets a
trivial certain easy win outrank a hard uncertain critical one — `I1×C3×E3 = 9` beats
`I5×C1×E1 = 5` — and shipping the 9 while the 5 waits is precisely the failure this file
exists to prevent. It is also the failure that feels most productive from inside: a
stream of small completed things while the thing that matters sits.

So the ladder is a **gate**, not a factor. `C × E` orders within a rung and never across
one.

**What age may and may not do.** It breaks ties, and past **30 days** the row is reported
as one the queue has been lying about — surfaced in the run's output, not silently
promoted. Age never lifts a row across a rung: a polish item that has waited a year is
still polish, and letting it climb is how a queue ends up sorted by patience.

**`prio` in `backlog.md` is not replaced.** That formula (`sev × blast + age_bonus`) ranks
*findings against each other* and stays the board's own column. This file's ordering is
what runs when findings and product work compete in **one** list — the finding's rung comes
from the ladder above, and `sev × blast` is evidence for it, not a substitute.

## 4. Research before scoring, not after

**A row is scored from what it touches, never from its title.** "Fix the login redirect"
is E3 by its name and E1 once you find it crosses an auth library, a cookie domain and a
cached edge rule. Scoring first and discovering second produces an order that was wrong
before the first task started.

So, before an order is emitted:

1. **Fan out one researcher per candidate row** — same rules as `build.md` §4.2: fresh
   context each, given the row and nothing else, no shared working tree because they write
   nothing.
2. **Each returns four things and no opinion**: what it touches (`file:line`, services,
   external systems), what it depends on and what depends on it, what is already
   *measured* about the claimed effect, and what would have to be true for it to be wrong.
3. **Score after they return.** The rung comes from the evidence, `C` from what the
   researcher could and could not confirm, `E` from the surfaces they found.
4. **Emit the ordered list once**, with the three numbers and one line of why per row.

A researcher that comes back with "seems fine, medium effort" has returned nothing. The
four fields are the contract; anything else is a subagent that spent context to guess.

**Do not fan out to score two rows.** The dispatch costs more than reading them.

## Effort does not rank a finding, but the fixer needs a cost rule

The existing rule — **the finder may not rank by effort** — is about the finder, and it
holds. It says nothing about the moment somebody decides what to do with the row, and the
silence there was read as *cost never enters*, which is not what anyone means.

So the split, stated rather than inferred:

- **The finder** still may not rank by effort. What a fix costs is not a property of the
  defect.
- **The fixer**, at the point of deciding, weighs remedy cost against **measured harm** —
  not against the finding's stated severity. Severity is the finder's estimate of what
  could happen; harm is what did.
- **Where the harm measures zero the row is not deleted.** It is priced as *latent* and
  carries its measurement, so the next reader inherits the number rather than the alarm.
  A row deleted for measuring zero takes the measurement with it and the next audit
  re-derives the same alarm from the same mechanism.
- **Where the path is irreversible, cost loses.** A cheap guard on something that cannot
  be undone ships whether or not the failure has been observed — the asymmetry is the
  whole reason to have a rule instead of a judgement.

## 5. Where the human goes

The operator is a **scarce, high-value input**, and the failure mode is spending them one
question at a time.

- **Ask at the start, or in a batch at a boundary. Never after each task.** If the whole
  queue needs one decision, ask it before the queue starts.
- **A blocked row does not stop the run.** When something needs a person: first satisfy
  yourself that you are actually right and it is actually blocked — most "I need input"
  is an unread file — then write the question **into the row**, mark it `needs-operator`,
  and take the next row that is not blocked by the same answer.
- **The question in the row is answerable without context.** What was tried, what is
  needed, and what happens under each answer. A question that requires re-reading the run
  to understand is a question that waits another day.
- **Batch the answers back.** The operator returns to a list of questions with their
  consequences, not to a transcript.

The measure of this section: **how much of the queue moved while nobody was watching**, and
whether the things that stopped genuinely could not proceed.

## 6. Two models in one family, and why both are right

`seo-aeo-audit` triages on impact, irreversibility, uncertainty and coordination, and states
that **effort is recorded and never ranks**.
This file makes Ease rank. That is not a contradiction and the difference is the queue:

| | an **audit** | a **backlog** |
|---|---|---|
| the list is | everything that is wrong | everything that could be done |
| letting effort rank means | a blocker gets skipped for being hard, and the audit lies by omission | the queue self-selects toward value per day |
| so effort | is recorded and never ranks | ranks, inside the rung |

An audit must be complete before it is ordered; a backlog is ordered because it will never
be complete. Reach for the wrong one and the symptom is recognisable: an audit that
quietly dropped its hardest finding, or a backlog where nothing small ever ships.
