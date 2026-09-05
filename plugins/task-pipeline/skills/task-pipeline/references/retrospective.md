# Retrospective — the run teaches the next run, and the list stays short

The last act of stage 10, after the coverage table and before the run is called
done. It exists because the pipeline's gates are good at *this* run and blind
across runs: the same class of failure can be caught, fixed and forgotten five
times, and nothing in the flow notices it is the same one.

**The cap here is not a general rule about doctrine files.** It applies because these
instructions are read *in full* every run. [`learned.md`](learned.md) →
*What leaves this file, and why there is no cap* is the other case: a file entered by
citation, where the index must be right rather than the length short, and where a rule
retires on two triggers that are not counts. Proposing this cap for that file is a
recurring idea, and it is answered there with the measurement rather than an opinion.

**Two artifacts, and the split is the point.** A file that is read *in full* every
run may not contain anything that grows without limit — otherwise the cap that
justifies reading it protects one section while the file below it doubles.

| Artifact | Parts | How it is read |
|---|---|---|
| `docs/evidence/retro.md` — **one per project** | **Standing instructions** (max **10**) · **Run stamps** (max **10**, oldest rotate out) | stage 0, **in full** — both are bounded by a **cap**, which *one line each* never was |
| the same file's **Recent log** | narrative entries, **uncapped by design** — the heading said *entries from the last five run stamps* until 2026-08-20 while the section held 25 going back nine days, a bound in a heading that nothing enforced | stage 0, **queried** by the task's nouns. It said *in full* until 2026-08-10, when it measured **74%** of the file: an uncapped section inside a binding source is what makes the capped part get skimmed |
| `docs/evidence/retro/YYYY-QN.md` — the archive | every entry and every retirement ever written, append-only | **queried** by the task's nouns; never read end to end |

Seed the archive from [`../templates/retro-archive.md`](../templates/retro-archive.md).

Every run writes a **stamp** and runs the **prune**. Only a run that *diverged*
writes an entry. A retro that is empty after a messy run is the exact failure this
file exists to stop.

## Contents

- Write the entry only for a divergence — and name the layer that owned it
- Every lesson carries its commit
- Never amend a commit a record already names
- The stamp table is capped at ten, and *one line per run* was never a cap
- `publish:` is a line in the verdict, not a silence
- Rotation — the archive is how pruning stops losing things
- Three grades of fix — take the highest one that can work
- Stamp first, then prune, then write
- The prune — mandatory, and it runs after the stamp
- When the prune cannot run, say so — it is not the same as nothing to prune
- A fix to one call site closes a call site, not a class
- The loop closes at stage 0
- Where a lesson goes when it is not about this project
- Publishing the insight — the skill learns from every project that runs it
- The improvement iteration — what happens to a published insight next
- What may leave the project — the redaction list
- Rationalizations

## Write the entry only for a divergence — and name the layer that owned it

An entry is owed when the run did not go as planned: a gate reopened, a stage was
re-entered, a fix broke something it wasn't touching, an estimate was wrong by a
factor, the operator had to intervene where the brief said they wouldn't.

Required fields, and none of them is optional:

| Field | The rule |
|---|---|
| **Symptom** | what actually happened, in one line, with the evidence (a command, a `file:line`, the gate that reopened) |
| **Surfaced at** | the stage where it became visible |
| **Owned by** | the stage that *let it through* — usually an earlier one. A finding belongs to the layer that owns it; recording it against the stage that tripped over it is how the same defect returns |
| **Root cause** | why the pipeline permitted it. "The agent was careless" is not a cause — it is the absence of one, and it produces no fix |
| **Fix** | one of the three grades below |
| **The check** | what would have caught this the first time. If the honest answer is "nothing yet", that is the fix, and it is grade 1 |
| **Commit** | the short SHA of the change that fixed it |

## Every lesson carries its commit

A standing instruction carries **two** SHAs — `Commit` (the change that introduced
it) and `Fired at` (the last run in which it fired) — and every log entry and every
retirement carries one.

**Why a SHA and not a `file:line`.** A line number rots at the next edit, and then
the evidence points at something that has moved or gone; the reader is left with a
claim and no way to check it. A commit is immutable and carries the diff, the
message and the parent, so `git show <sha>` reconstructs the entire incident two
months later — which is exactly when the same class comes back and somebody needs
to know whether this was already understood.

**Every SHA must resolve — and resolving is not enough.** This is
[`learned.md`](learned.md) rule 14 — *a document may not send a reader to something
absent* — applied to history, and it is mechanical: the documentation gate runs
`git rev-parse --verify --quiet <sha>^{commit}` over every backticked SHA in the retro
and its archive ([`gates.md`](gates.md)).

**But a commit that was amended away still resolves on the machine that amended it**,
and exists in no clone. The gate therefore also requires each SHA to be **reachable
from `HEAD`** — `git merge-base --is-ancestor <sha> HEAD` — because that is the
question a reader two months from now is actually asking, and the weaker one passes
for as long as the object survives locally.

## Never amend a commit a record already names

Measured 2026-08-16, twice in one close-out and twenty minutes apart. The sequence is
seductive because each step is right on its own: stamp the run with its commit → the
stamp is part of the run, so fold it in with `--amend` → the amend mints a new SHA →
the stamp now names a commit that will never reach the remote.

The rule is one line and it is absolute: **once a file names a SHA, that commit is
frozen.** A correction goes in a *follow-up commit*, never a second amend — amending to
repair a stamp is the loop that produced the problem, and the second attempt lands in the
same place as the first.

Practically, that makes the order:

1. commit the work;
2. **then** stamp, in a commit of its own, naming the commit from step 1;
3. prune and write the entry in that same second commit, or a third.

The stamp costs one line and one commit. A run that folds it back into the work to keep
the history tidy is trading a reader's ability to find the incident for the appearance of
tidiness — and the reader is the entire reason the stamp exists.

## The stamp table is capped at ten, and *one line per run* was never a cap

Measured 2026-08-10: standing instructions **~1 234 tok** behind a cap of ten, run stamps
**~2 099 tok over 27 rows** behind nothing. Both are read in full at stage 0 and both
were described as *bounded by construction*. One line per run is a **slope**: at a
hundred runs the stamp table alone is ~7 800 tokens of a floor the doctrine believes is
bounded.

This is the same shape the 2026-08-10 audit found in the narrative log and moved out of
the floor — and it left the neighbour in the same file, with the same property, because
the neighbour's growth is *tidy*. A tidy slope is still a slope.

**The cap is ten and the trigger is why.** The cold rule reads *the last five run
stamps*; ten is that with a margin, so a stamp rotating out can never be one the trigger
needed. At the eleventh, the oldest row moves — whole, with its verdict and its retro
column — into `docs/evidence/retro/YYYY-QN.md` under `## Run stamps`, append-only,
like every other rotation. **The count is printed at the prune**, beside the standing
instructions' own count, so a table that stops rotating is visible rather than merely
large.

## `publish:` is a line in the verdict, not a silence

Reported from another project, and the report is about this file: an operator asked, after
many runs, why nothing had ever been published.

The floor is right and does not move — publishing is opt-in per project, off by default,
because an outward act taken from a generic flag is an outward act nobody authorized. The
gap is what happens next. A project with no configuration produces, run after run,
retrospective entries carrying lessons about **the skill**, and the mechanism reports
nothing, because it was never armed. **An unarmed mechanism and a mechanism with nothing
to say are indistinguishable from the outside** — [`gates.md`](gates.md)'s false success,
applied to this bundle's own learning path. In the reporting project several runs had
produced skill-level lessons over months; the count of published insights was zero and no
gate had ever mentioned it.

Stage 10 prints ratchets and two disclosures — what the run declined to claim, and what a
check never looked at. Publishing is neither, so its absence is not observable at the only
moment anyone is reading.

**So stage 10's block carries one line for publication:**

```
publish: <issue url>                       — opened this run
publish: 0 (configured, nothing insight-grade)
publish: not configured (N insight-grade entries stayed local)
```

It arms nothing and authorizes nothing; it makes the silence legible. A count of zero
beside *configured* is a fine answer. A **blank** where configuration is absent is how an
instruction went unread for eight releases.

**The failure mode survived its own fix, in a quieter form.** This section once said
*"open an issue upstream"* while naming no repository, no trigger and no authorization,
and every reader took it as done. The mechanism that replaced it is correct — and until
this line existed it still had no way to say it never ran.

## Rotation — the archive is how pruning stops losing things

At the prune, entries older than the last five run stamps **move** to
`docs/evidence/retro/YYYY-QN.md`. Moving is not deleting.

- The archive is **append-only**, and a retirement writes its line **there**, with
  the trigger that retired it and the commit.
- A retired rule that comes back as a real failure is a grade-1 fix — **with its
  history attached**, which is the whole return on having archived it.
- Nothing is ever removed from the archive to keep it tidy. It is not read in full,
  so its size costs nothing; its completeness is what it is for.

## Three grades of fix — take the highest one that can work

**Grade 1 — mechanical.** A test, a lint rule, a gate criterion, a CI step, a hook.
The check *is* the memory: nothing has to be read, remembered or pruned later. Log
it as `landed` and move on — it never becomes a standing instruction and never
costs a slot.

**Grade 2 — a standing instruction.** A rule an agent must read, for the cases no
check can decide (a judgement, a precedence, a "ask before X"). It costs one of the
ten slots and it is **only accepted with its retirement trigger written at birth**
(below).

**Grade 3 — a note with an expiry.** For something still being understood. Maximum
**two runs**. At the second stamp it is promoted to grade 1 or 2, or deleted. A note
with no expiry is how a file becomes unreadable one honest line at a time.

Prefer grade 1 whenever a check can decide it. This is the same law as
[`audit.md`](audit.md) → *A class that repeats twice becomes a gate, not a note*: a
rule that could have been a check gets read twice and obeyed once.

## Stamp first, then prune, then write

`learned.md` rule 21. This order used to be *prune first*, and that was a **deadlock**, not a
preference: the cold trigger below reads *the last five run stamps*, and the stamp was written after
the prune. The trigger read a counter the same stage produced later, so on any list it had never run
on real data — and it stays unreadable for exactly as long as nobody stamps.

Measured on a real project: last entry five days old; stamps per day 33, 20, 26, **3, 0** — the zero
on a day with 107 commits — and the list sitting at **10 of 10**. Every run arrived at a stage that
opened with a full list, an unusable trigger and a mandatory deletion. It was not skipped out of
laziness; its first step could not be performed, and the cheap step that would have made it
performable was queued behind it.

**The stamp is one line and costs nothing.** It is also the only thing that makes the prune
computable, which is why it goes first:

```bash
printf '%s · %s\n' "$(date +%F)" "$(git rev-parse --short HEAD)" >> docs/evidence/retro.md
```

## The prune — mandatory, and it runs after the stamp

A lesson that lands in a cluttered file is a lesson nobody will reach — so the prune still runs
before the entry is written. It runs *after* the stamp, because it reads it.

Every row carries its own trigger in a **`Retire when`** column, written at birth —
a rule whose retirement condition is decided later is a rule the prune can only
argue about. Check **every** standing instruction against three triggers:

| Trigger | Test | Then |
|---|---|---|
| **It became a check** | the rule is now enforced by a test, lint, gate or hook | delete it — the check is the memory, and keeping both means it is read twice and obeyed once |
| **Its surface is gone** | resolve every path, command, stage and tool it names; any that no longer exists | delete it — it now describes a system nobody is running |
| **It went cold** | it has not fired in the last **five run stamps** — **or** in the last **sixty days**, whichever comes first | delete it: five runs without firing is the evidence it was situational, and the calendar is the unit that still moves when the stamp counter has stopped |

**Each trigger is a command, not a judgement.** A retirement condition nobody can run is a
condition nobody applies, which is how a list reaches ten and stops being read:

```bash
# became a check — the rule's own words appear in something that runs
grep -rl "$RULE_KEYWORD" scripts/ test/ .github/workflows/ Makefile* 2>/dev/null

# surface is gone — every path, command and tool it names, resolved
grep -oE '`[^`]+`' <<<"$RULE_TEXT" | tr -d '`' | while read -r t; do
  [ -e "$t" ] || command -v "$t" >/dev/null || echo "MISSING: $t"; done

# went cold — fired in none of the last five stamps
tail -n 200 docs/evidence/retro.md | grep -c "$RULE_ID"

# ...OR in the last 60 days, whichever comes first — see below for why both
git log -1 --format=%cd --date=short -S"$RULE_ID" -- docs/evidence/retro.md
```

Anything the first two print is a deletion; a zero from the third **or** a last-fired date more
than sixty days old is a deletion. What survives all three stays, and the run states the counts
rather than the conclusion (`learned.md` rule 19 — an empty result and an unrun command look
identical).

**Why the cold trigger needs two units, and it is not belt-and-braces.** A run stamp is written by
a run *of this pipeline*. Where a project ships some of its work another way, the stamp counter
stops while the work does not — so "the last five stamps" can span an arbitrary amount of change,
and a rule sits unexamined for exactly as long as the pipeline goes unused. Measured on this
repository: **ten consecutive releases, `v1.16.0` through `v1.23.0`, carry no stamp at all.** Over
that stretch the trigger was not strict or lenient; it was **unreadable**, and a list capped at ten
with an unreadable retirement condition fills up and stops being pruned.

The wall-clock alternative fires on elapsed time, which nothing can stall. Keep both: the stamp
count is the better signal when the pipeline is in use, and the date is the one that still works
when it is not.

**The stamp gap is itself a number worth printing.** A retro whose newest stamp is far behind the
repository's newest release is telling you the retro is describing a smaller world than the one
that shipped — the same failure `learned.md` rule 16 records for a work-list. State it beside the
retro counts:

```bash
git tag --sort=-v:refname | head -1                    # newest release
grep -m1 -oE '`[0-9a-f]{7,}`' docs/evidence/retro.md # newest stamped commit
```

Then the cap: **ten standing instructions, hard.** At eleven you do not get to keep
them all — the oldest never-fired one goes. "But all of them matter" is precisely
the state in which the list stopped being read, and the ninth stale rule is what
discredits the two that are load-bearing.

**Every deletion writes one line in the archive** — id, date, which trigger fired,
and the commit. Silent deletion is forbidden: the record is what survives, the
instruction is what leaves.

**Print the counts beside the gate verdict**, the same way the carry-over ledger
does ([`audit.md`](audit.md) → *What can't be fixed now becomes a ratchet, never a TODO*):

```
GATE 10 acceptance: PASS — 14/14 REQ verified
  carry-over: 0 unresolved · retro: 7 standing (was 9) · retired 3 · added 1
  abstained: 2 · unlooked: 3
  holds: 10 — none — enumerated 8/8 classes
```

A pruned list that nobody prints is a list that quietly grows back.

## When the prune cannot run, say so — it is not the same as nothing to prune

The prune retires a standing instruction against its triggers, and the cold trigger counts
run stamps. Meeting a list whose rows carry **no id and no retirement condition**, the
honest behaviour was undefined — so a careful run printed counts and stopped while a
careless one could delete nine rules, and both looked like *the prune ran*.

- **Backfill first, once.** On meeting rows with no id, the prune's first act is to mint
  ids and propose a retirement condition per row **from the row's own text**, printed for
  the operator to accept. One pass, and the trigger works forever after.
- **`blocked` is a named outcome**, printed like any other: what could not be evaluated
  and why. An undefined case is where the spread between two runs lives.
- **A hard cap plus an unrunnable retirement condition is a deadlock.** Either the cap
  yields until the backfill is done, or the backfill is a precondition of enforcing it —
  but not both, and the file says which.

## A fix to one call site closes a call site, not a class

- **A fix other call sites will need is exported before it is used.** The test is
  mechanical: if the same defect could exist in a second file, the fix does not stay
  private to the first.
- **Closing a defect includes a census of its siblings, by BEHAVIOUR rather than by a list
  of names** — *every script that spawns a browser*, found by searching for the spawn, not
  by remembering the five. A list of names is how the previous pass missed four of them.
- **The entry states how many call sites the class had and how many were fixed.** *Fixed*
  and *fixed in one of five* currently read identically, and only one of them closes a row.

## The loop closes at stage 0

The standing instructions are an **instruction source**, not background reading:
[`knowledge-sources.md`](knowledge-sources.md) reads them in full at the harvest —
they are short by construction — and records the file as a ledger row. Every
instruction that actually *fires* during the run gets its **last-fired date and
commit stamped** as it fires. That stamp is the only thing that makes the cold-rule
honest; without it "five runs without firing" is a guess, and the prune becomes a
mood.

**The archive is queried at the same moment**, by the task's own nouns. It is the
one source that answers *"have we been bitten by this class before?"* — and that
question is worth asking precisely when the in-force list says nothing, because a
rule that was retired for going cold is exactly the rule about to be re-learned.

## Where a lesson goes when it is not about this project

A lesson that would be true in any repository does not belong in one project's
retro — it belongs in the pipeline's own doctrine
([`learned.md`](learned.md), which is exactly that list, earned the same way). A local
file that accumulates universal rules is a fork of the skill that nobody named.

**This said *"open an issue upstream"* for eight releases and named no repository, no
trigger and no authorization** — an instruction on rung 1 that everybody read as done.
The rest of this section is the mechanism.

## Publishing the insight — the skill learns from every project that runs it

**One job: stop a lesson dying in the repository that learned it.**

A retro entry is written per project and read by that project's next stage 0. The
pipeline itself never sees it. So a defect in the **skill** — a gate that loops, a
doctrine promising what nothing enforces, a rule firing on the wrong shape — is
rediscovered independently in every project and fixed in none of them.

**Opt-in, per project, off by default** — `pipeline.json` → `retro.publish`:

```json
"retro": {
  "publish": {
    "repo": "ssheleg/task-pipeline",
    "label": "retro-insight",
    "redact": "strict"
  }
}
```

Absent, nothing is published, and nothing is asked. **Silence arms nothing** — the same
floor deploy authorization uses, and for the same reason: this is an **outward act**,
and an outward act taken from a generic flag is an outward act nobody authorized
([`continuity.md`](continuity.md) → *The limit, before the capability*).

**The body is printed in full before the issue is opened, every time.** Not a summary
of it, not its title — the string that will be sent. The operator standing at stage
10's manual gate is already reading; showing them what leaves the machine costs one
block and is the only moment anyone can stop it.

```
── would open issue ──────────────────────────────────────────
repo:  ssheleg/task-pipeline
label: retro-insight
title: [retro] a queue is not a diagnosis
<the whole body, verbatim>
──────────────────────────────────────────────────────────────
opening…  → #24
```

**No `gh`, no network, no permission?** Print the body, say the issue was **not**
opened, and carry the exact text in the carry-over ledger. That is the honest
degradation; a second transport is not.

## The improvement iteration — what happens to a published insight next

Publishing is half a loop. An issue that is opened and never triaged is a lesson
that cost a run and bought nothing, and a tracker full of those teaches everyone
that publishing is where findings go to be filed.

**The loop, and every arrow in it is somebody's obligation:**

```
a run diverges → a retro entry → retro.publish → an issue on the skill
                                                        ↓
   a board row ← measured against the tree ← triaged in a later cycle
        ↓
   doctrine + the guard that proves it → a release → the next run reads it
```

**Resolve what you worked, let the rest accumulate — visibly.** At the close of a
cycle that consumed published issues:

- **An issue closes when the behaviour changed**, not when the lesson was
  understood (that is R-006, and it applies to issues exactly as it applies to
  findings). The closing comment names **where** it landed — a file and a line —
  and the guard that now holds it. A close with no address is a close nobody can
  audit.
- **An issue nobody worked stays open.** It is not triaged into silence, not
  relabelled, not closed as stale. The pile is the queue, and its depth is the
  honest measure of how far behind the doctrine is.
- **Nothing is deleted.** A closed issue keeps its number, and the number is what
  the CHANGELOG and the retro entry point at. Deleting one severs both, and the
  cost lands on whoever next asks *why is this rule here*.

**Where the queue comes from at the start of a cycle**, in this order: open issues
published by any project running this skill, then the board's open rows by computed
priority, then the open-questions register. A run that finishes its brief early
takes the top of that list rather than inventing work — and a run that *cannot*
take it says so, which is a fuller queue rather than a quiet one.

**The measurement that keeps this honest.** Print, at the close: issues consumed,
issues resolved with an address, issues left open. Three numbers, no floor, no
target, and the third one rising is information rather than a failure — it means
the projects running this skill are finding more than one cycle can absorb, which
is what you want them to do.

## What may leave the project — the redaction list

An issue is a **public artefact in someone else's repository**. What travels is the
*class*; what stays is everything that identifies where it happened.

| Goes | Stays |
|---|---|
| the class of failure, stated in the abstract | the file, the function, the line it happened in |
| which stage owned it and which stage surfaced it | the repository, organisation, branch or commit |
| the doctrine or guard that missed it, by its name **in this skill** | any host path, absolute or relative |
| the fix by grade, and the check that would catch it | the code, the config values, the data |
| whether an existing standing instruction fired | any person, company, customer or product name |

Five rules, numbered so a reader can point at one:

1. **No host paths.** Only paths inside task-pipeline itself — `references/…`,
   `templates/…`, `test/validate.py`. An absolute path names a machine.
2. **No host identifiers**: repository, organisation, branch, commit, tag, issue or PR
   number belonging to the project the run happened in.
3. **No code, no configuration values, no data** — not a snippet, not a redacted
   snippet. A shape can be described in a sentence.
4. **No names**: person, company, customer, employer, product.
5. **The title states the class, not the incident** — *"a queue is not a diagnosis"*,
   never *"our export job looped"*.

**The printed text and the sent text are one string.** Redacting after the print, or
printing a cleaned-up version of what is actually sent, is the false-success shape this
bundle names outright ([`gates.md`](gates.md) → *False success*): a mechanism reporting
on itself rather than on what it did.

**When in doubt the rule is subtraction, not judgement.** An insight that survives
losing a detail is still an insight; a detail that leaks cannot be recalled from an
index. If removing it makes the entry incomprehensible, the entry was about the project
and not about the skill — keep it local.

## Rationalizations

| Excuse | Reality |
|---|---|
| "Nothing really went wrong this run" | Then the stamp says so in one line and you are done in ten seconds. The runs that "went fine" are where a repeated class hides — it never cost enough to remember. |
| "I'll write the retro later, with a clear head" | Later is when you remember the outcome and not the seam. The cause is legible for about an hour after the run. |
| "Don't delete it, it might still be useful" | That sentence is the entire failure mode. Every rule kept "just in case" spends attention that the load-bearing ones needed, and the file stops being read at all. |
| "Pruning loses knowledge" | The Log keeps the incident forever; only the *instruction* leaves. If it recurs you get a grade-1 fix with its own history attached. |
| "The list is at eleven but they're all important" | Then one of them is doctrine and belongs in `CLAUDE.md`, one has become a check, and one has not fired in a year. Ten is the budget precisely because ranking is uncomfortable. |
| "I'll note it as a reminder for next time" | A note is grade 3 and expires in two runs. If it is worth remembering it is worth a check or a slot; if it is worth neither, it was never going to be read. |
