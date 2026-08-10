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
| `docs/superpowers/retro.md` — **one per project** | **Standing instructions** (max **10**) · **Run stamps** (one line each) | stage 0, **in full** — both are bounded by construction |
| the same file's **Recent log** | entries from the last five run stamps — narrative, and capped by nothing | stage 0, **queried** by the task's nouns. It said *in full* until 2026-08-10, when it measured **74%** of the file: an uncapped section inside a binding source is what makes the capped part get skimmed |
| `docs/superpowers/retro/YYYY-QN.md` — the archive | every entry and every retirement ever written, append-only | **queried** by the task's nouns; never read end to end |

Seed the archive from [`../templates/retro-archive.md`](../templates/retro-archive.md).

Every run writes a **stamp** and runs the **prune**. Only a run that *diverged*
writes an entry. A retro that is empty after a messy run is the exact failure this
file exists to stop.

## Contents

- Write the entry only for a divergence — and name the layer that owned it
- Every lesson carries its commit
- Rotation — the archive is how pruning stops losing things
- Three grades of fix — take the highest one that can work
- Stamp first, then prune, then write
- The prune — mandatory, and it runs after the stamp
- The loop closes at stage 0
- Where a lesson goes when it is not about this project
- Publishing the insight — the skill learns from every project that runs it
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

**Every SHA must resolve.** This is [`learned.md`](learned.md) rule 14 — *a
document may not send a reader to something absent* — applied to history, and it is
mechanical: the project's documentation gate runs `git rev-parse --verify --quiet
<sha>^{commit}` over every backticked SHA in the retro and its archive
([`gates.md`](gates.md)).

## Rotation — the archive is how pruning stops losing things

At the prune, entries older than the last five run stamps **move** to
`docs/superpowers/retro/YYYY-QN.md`. Moving is not deleting.

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
printf '%s · %s\n' "$(date +%F)" "$(git rev-parse --short HEAD)" >> docs/superpowers/retro.md
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
tail -n 200 docs/superpowers/retro.md | grep -c "$RULE_ID"

# ...OR in the last 60 days, whichever comes first — see below for why both
git log -1 --format=%cd --date=short -S"$RULE_ID" -- docs/superpowers/retro.md
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
grep -m1 -oE '`[0-9a-f]{7,}`' docs/superpowers/retro.md # newest stamped commit
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
```

A pruned list that nobody prints is a list that quietly grows back.

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
