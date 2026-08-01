# Retrospective — the run teaches the next run, and the list stays short

The last act of stage 10, after the coverage table and before the run is called
done. It exists because the pipeline's gates are good at *this* run and blind
across runs: the same class of failure can be caught, fixed and forgotten five
times, and nothing in the flow notices it is the same one.

**Artifact:** `docs/superpowers/retro.md` — **one per project, not per run**,
committed. It has three parts and a hard size limit:

| Part | What's in it | Read by |
|---|---|---|
| **Standing instructions** | the rules currently in force — max **10** | stage 0, in full, every run |
| **Log** | problem → cause → fix → check, newest first, plus every retirement | a human, and stage 0 when the terms match |
| **Run stamps** | one line per run: date, topic, verdict | the prune (this is what makes "five runs" countable) |

Every run writes a **stamp** and runs the **prune**. Only a run that *diverged*
writes an entry. A retro that is empty after a messy run is the exact failure this
file exists to stop.

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

## The prune — mandatory, and it runs BEFORE the new entry is written

Prune first, then write. A lesson that lands in a cluttered file is a lesson nobody
will reach.

Check **every** standing instruction against three retirement triggers:

| Trigger | Test | Then |
|---|---|---|
| **It became a check** | the rule is now enforced by a test, lint, gate or hook | delete it — the check is the memory, and keeping both means it is read twice and obeyed once |
| **Its surface is gone** | resolve every path, command, stage and tool it names; any that no longer exists | delete it — it now describes a system nobody is running |
| **It went cold** | it has not fired in the last **five run stamps** | delete it — five runs without firing is the evidence that it was situational |

Then the cap: **ten standing instructions, hard.** At eleven you do not get to keep
them all — the oldest never-fired one goes. "But all of them matter" is precisely
the state in which the list stopped being read, and the ninth stale rule is what
discredits the two that are load-bearing.

**Every deletion writes one line in the Log** — id, date, which trigger fired.
Silent deletion is forbidden: the record is what survives, the instruction is what
leaves. A retired rule that comes back as a real failure is a grade-1 fix, and now
you have its history.

**Print the counts beside the gate verdict**, the same way the carry-over ledger
does ([`audit.md`](audit.md) → *ratchet, never TODO*):

```
GATE 10 acceptance: PASS — 14/14 REQ verified
  carry-over: 0 unresolved · retro: 7 standing (was 9) · retired 3 · added 1
```

A pruned list that nobody prints is a list that quietly grows back.

## The loop closes at stage 0

The standing instructions are an **instruction source**, not background reading:
[`knowledge-sources.md`](knowledge-sources.md) reads them in full at the harvest —
they are short by construction — and records the file as a ledger row. Every
instruction that actually *fires* during the run gets its **last-fired date
stamped** as it fires. That stamp is the only thing that makes the cold-rule honest;
without it "five runs without firing" is a guess, and the prune becomes a mood.

## Where a lesson goes when it is not about this project

A lesson that would be true in any repository does not belong in one project's
retro — it belongs in the pipeline's own doctrine
([`learned.md`](learned.md), which is exactly that list, earned the same way). Open
an issue upstream and say so in the entry. A local file that accumulates universal
rules is a fork of the skill that nobody named.

## Rationalizations

| Excuse | Reality |
|---|---|
| "Nothing really went wrong this run" | Then the stamp says so in one line and you are done in ten seconds. The runs that "went fine" are where a repeated class hides — it never cost enough to remember. |
| "I'll write the retro later, with a clear head" | Later is when you remember the outcome and not the seam. The cause is legible for about an hour after the run. |
| "Don't delete it, it might still be useful" | That sentence is the entire failure mode. Every rule kept "just in case" spends attention that the load-bearing ones needed, and the file stops being read at all. |
| "Pruning loses knowledge" | The Log keeps the incident forever; only the *instruction* leaves. If it recurs you get a grade-1 fix with its own history attached. |
| "The list is at eleven but they're all important" | Then one of them is doctrine and belongs in `CLAUDE.md`, one has become a check, and one has not fired in a year. Ten is the budget precisely because ranking is uncomfortable. |
| "I'll note it as a reminder for next time" | A note is grade 3 and expires in two runs. If it is worth remembering it is worth a check or a slot; if it is worth neither, it was never going to be read. |
