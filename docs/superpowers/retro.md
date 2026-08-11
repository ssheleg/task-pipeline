# Pipeline retrospective — task-pipeline

One file per project, not per run. Written as the **last act of stage 10**:
**stamp first, then prune, then write** an entry **only if the run diverged**.
The order is not style — the cold-retirement trigger reads the stamp this stage
writes, so a prune placed ahead of it can never run on real data
(`learned.md` rule 21). Doctrine: `references/retrospective.md`.

**What stage 0 reads in full:** *Standing instructions* and *Run stamps*. Both are
bounded by construction — ten rows and one line per run — which is why the cap is not
negotiable. The **Recent log** and the **archive**
(`docs/superpowers/retro/YYYY-QN.md`) are *queried* by the task's nouns and never read
end to end.

This said all three until 2026-08-10, and the claim that all three were bounded was
false: measured, the log was **10 937 of this file's 14 756 tokens** and nothing caps
its length. Reading nine narratives in full every run is not diligence — it is the
volume that makes an agent skim the ten rules that actually bind it.

## Standing instructions (max 10 — in force right now)

Every row is a rule an agent must follow, that **no check can decide**. A rule a
check *can* decide is not written here: it is written as the check (grade 1).
No row is accepted without its **retire-when** trigger, written at birth.

Every SHA here must resolve — the documentation gate runs `git rev-parse --verify`
over all of them.

| id | Born | Commit | Instruction | Because | Retire when | Last fired | Fired at |
|---|---|---|---|---|---|---|---|
| R-002 | 2026-08-03 · `doc-track-audit` | `096f0f0` | When a batch of edits returns **any** error, re-verify **every** edit in that batch before reporting the batch done — not only the one that errored. | Two edits were issued together; the second failed the read-before-write check and was retried, the first was silently never applied. It was reported as done, shipped in v1.7.0, and surfaced only in a post-release audit as a question the grill never asks with a field in the brief waiting for the answer. | the harness reports per-edit outcomes in a form a check can read, or the edits are issued one per message | 2026-08-08 | `68b4428` |
| R-003 | 2026-08-05 · `artifact-hygiene` | `13028e9` | When you fix a defect in one check, guard or detector, **immediately run that defect's definition against its siblings** before moving on — the same file's other checks, and the other files that do the same job. | `learned.md` rule 6 says *sweep the class, not the instance*, and this is its **third** recorded failure to be applied to itself. 2026-08-03 `enforcement-audit`: a fix scoped to references→README while the same class lived in six other places. 2026-08-03 `root-cause`: nine findings, one missing matrix row. 2026-08-05: check 2's false-positive class was solved, and check 4 — its immediate sibling, in the same file, written in the same hour — shipped with the identical bug and fired on this run's own documents. Two instances were worth notes; `audit.md` says a class seen twice becomes a mechanism rather than a third ledger row. | a check can compare sibling detectors for a shared false-positive class — which needs the classes to be named in a machine-readable form first | 2026-08-10 | `07e7824` |
| R-004 | 2026-08-06 · `graph-staleness` | `2ce6ecc` | When a gate runs, the **next command must be conditional on its exit code** — never a gate and a commit in one block separated by newlines. | The hygiene gate returned FAIL and the `git commit` and `git push` beneath it ran anyway, because they were separate lines rather than a chain. The gate was read and not obeyed, which is indistinguishable in the transcript from a gate that passed. `learned.md` rule 11 makes the gate *return* the right code; nothing made the caller *use* it. | a harness or wrapper refuses to run a mutating command after a non-zero gate in the same block | 2026-08-10 | `07e7824` |
| R-005 | 2026-08-08 · `audit-followup`/M8 | `5726f7f` | When a change adds or widens a **check**, get an independent reader on it before merge — your own probes only exercise the shapes you already thought of. | M8 probed its new guard in four shapes and shipped it with a proven false-negative path: the ordered-list branch scanned the whole file and compared only the first pair, so a violation after a correct list was never examined. Two PR review passes found that, plus a live defect in the shipped `evidence-docs` navigator that **no pairwise shape could see by construction** — a table cell naming one act. Five probes written by the author found neither. This is not R-001 (that one doubts a silent probe); this is the probe being confident and complete about the wrong set. | a second reader — human or agent — is dispatched by a stage rather than by the repository happening to run a bot on PRs | 2026-08-08 | `5726f7f` |
| R-006 | 2026-08-08 · `audit-followup`/M2 | `44bdf53` | A finding is closed when the **behaviour** changes. Reporting the gap — a `dormant` line, a printed `skip`, a note beside the verdict — is honest and is **not** a fix; say which one you did. | The claim registry's number-word map stopped at forty-nine while the guard count was 130, so a word form above the ceiling was skipped **in silence**. The fix shipped was: print the unread tokens. That is a real improvement and the gap was untouched — a word-form claim above fifty was still skipped, now with a note. It was recorded as addressed and the next review round reopened it, correctly. `gates.md` already says a `dormant` state must be printed; nothing said that printing it does not discharge the finding. | a close-out records, per finding, whether the behaviour or only the reporting changed — and a check can read that field | 2026-08-10 | `07e7824` |

Retire on **any** of: it became a check · every path/command it names is gone · it
has not fired in the last five run stamps, or in the last sixty days. At eleven
rows, the oldest never-fired
row goes — the cap is not negotiable, ranking is.

## Recent log — entries from the last five run stamps (newest first)

### 2026-08-11 · `hand-back` · the release built what it had just condemned

**Symptom.** A gate criterion was added requiring the run to write a hand-back at stage
10, argued for in a paragraph whose whole point was that an instruction with no gate
behind it is *"copy it, tick it"* — a rung-1 rule read as rung 3, which the v1.37.0 audit
had convicted. Seven guards shipped with it. **Every one read a doctrine file.** All they
could establish was that the instruction was still written down.

**Surfaced at:** stage 7, by R-005's fifth consecutive reader, which constructed a
conforming hand-back concealing a weakened test and showed that nothing in the repository
would notice — and that the same audit, run in a year, could reach no verdict either way,
because there would be no run records to check.

**The stage that owned it:** stage 3. The spec locked what the report must *contain* and
never asked where it *lands*. Every other artefact in this pipeline has an address; this
one had a format and a gate.

**Root cause.** A gate criterion is a claim about a run. A check that reads the doctrine
is a claim about the doctrine. The two look identical in a green suite, and the distance
between them is exactly the distance the v1.37.0 audit measured — except that audit could
work, because run records existed for it to read.

**Fixes by grade.**

1. *(mechanical)* The hand-back lands as a `hand:` line in the run ledger, its fourth
   declared shape. `grep -c '^hand:'` against `grep -c '^iter:'` makes a missing one
   readable, which is the least a later audit needs.
2. *(mechanical)* Ten more defects the same reader found — six in guards, four in the
   doctrine — including a bare `"hand-back"` substring that could not tell a gate
   *requiring* it from one *excusing* it, and four ambiguity sources whose commands did
   not exist, one of which would have grepped a string the source ledger never writes.
3. *(standing instruction)* **None added.** R-005 covers it, fired, and this is its fifth
   consecutive harvest.

**What is stated rather than fixed, and it is the honest half.** `SURFACED` has no
register behind it — the doctrine calls it the section that earns the hand-back precisely
*because* what a run learned by accident is recoverable from no artefact. So *"nothing
surfaced"* remains a quiet decision, and the ledger line records that a hand-back
happened, never that it was complete. No check in this repository can close that, and
saying so is the only thing that keeps the gate from being the decoration it was written
to replace.

**Six predicates were answered by their neighbours in this release, and all six were
caught by their own probes rather than by a reader** — the first release where that ratio
held. The neighbour-probe habit shipped in v1.42.0 is doing what it was written for.

### 2026-08-11 · `neighbour-probe` · the doctrine failed its own first use

**Symptom.** A section was written into `gates.md` telling a guard author to plant the
guard's **own evidence** next door and require the guard to still fail. Three probes
shipped implementing it. **One of them planted the needles of two retired predicates** —
proving the guards that used to exist were neighbour-answerable, and saying nothing at all
about the one that does.

**Surfaced at:** stage 7, by R-005's fourth consecutive reader. Not by the suite: the
probe fired, because a probe that plants *something* and watches the validator go red
looks identical to one that plants the right thing.

**The stage that owned it:** stage 3. The instruction was under-specified in the spec, not
mis-implemented in the build — *"plant the guard's own evidence"* has an obvious wrong
reading, and the run took it.

**Root cause.** A doctrine written to catch *a check answered by text that is not its
subject* was itself answered by a needle that was not its subject. The class is
scale-free: it applies to guards, to the probes that test guards, and to the doctrine that
specifies the probes. Each level was written by someone who had just understood the level
below and assumed that understanding transferred.

**What made it visible** was the same thing that made the six before it visible: a reader
who had not written any of it. Four releases, four readers, four harvests of this class —
fifteen, six, six, eight. The trend is not down.

**Fixes by grade.**

1. *(mechanical)* All eight closed, and each of the reader's plants replayed against the
   fixed guard until it failed. Two were guards whose **declared span was false** — the
   comment said one thing and the slice did another, which is worse than no comment.
2. *(mechanical)* The doctrine now says **which literal** to plant: the one the predicate
   matches today, read out of the guard rather than recalled. And a probe that only deletes
   must assert the neighbours it leans on, or a later edit demotes it silently.
3. *(standing instruction)* **None added.** R-005 already covers it and fired correctly.
   What this run adds is evidence about its yield at a fourth use — undiminished, which is
   itself the finding.

**Also fired: R-002.** A fix batch raised on its third edit and never wrote the file, so
three of four edits vanished. Caught only because the reader's defeats were replayed
afterwards and one still passed. The instruction exists for exactly this and it earned its
place again.

**The check that catches this class does not exist**, and after four releases of saying so
the honest addition is a number rather than a promise: **three guards of 253 have a
neighbour probe**, and which of the remaining 250 read a scoped span cannot be computed
from the code as written. That is `B-057`, and it is the work.

### 2026-08-10 · `stamp-cap` · the guard read a section, and stage 0 reads the file

**Symptom.** A cap guard written to stop a section growing inside the stage-0 floor was
defeated six ways by R-005's reader, each planted and watched printing `PASS`. The one
worth the entry: **the stamp shape this doctrine's own command writes.**
`retrospective.md` tells the agent to append a stamp with
`printf '%s · %s\n' "$(date +%F)" "$(git rev-parse --short HEAD)"`. That is prose, not a
table row. An agent obeying the shipped instruction literally produced forty stamps the
guard could not see, and the validator printed `PASS` with `unlooked: 0`.

**Surfaced at:** stage 7, by the reader. Not by the suite: both probes fired, because
both planted the shape their author had in mind.

**The stage that owned it:** stage 5 — the guard and its probes were written together,
from the same reading of the same file.

**Root cause.** The check's subject was *a section read in full at stage 0*; its evidence
was *rows under one heading*. Everything between those two — a second heading, a leading
space, a list, the doctrine's own prose form, a second file shipping the same table —
lives outside the evidence and inside the subject. This is the session's recurring class
stated at its sharpest: **a check answered by text that is not its subject, and blind to
subject that is not its text.**

**The instance that names the class best** is the row check, because it had already been
narrowed twice for exactly this and fell anyway: scoped past `run stamps`, it was defeated
by moving the standing instructions' `max 10` to the *other side of the `·`*. Positional
narrowing is not scoping.

**Fixes by grade.**

1. *(mechanical)* Both guards count by **predicate over a discovered corpus** — three
   stamp shapes including the doctrine's own, every file carrying a `## Run stamps`
   section, and the cap read from the segment that names the stamps.
2. *(mechanical)* Four surfaces that had never learned the rule now state it: the live
   section's intro, stage 10's prune, the scaffold, and the archive template — which had
   no destination section for a rotation the doctrine names.
3. *(standing instruction)* **None added.** `B-057` carries the mechanism, at priority 9
   and the top of the board: derive a probe's needle where a parser exists, and record for
   every guard the span it reads. Six instances in one session is a class for a script,
   not a rule for a person to remember.

**The check that catches it next time** does not exist yet, and that is the honest
statement: this was caught by a reader, for the third release running. `B-057` is the
attempt to stop needing one for this class.

### 2026-08-10 · `loop-mechanism` · a green validator is not a green suite, and it reached main

**Symptom.** `5a77053` was pushed straight to `main` with CI red. `validate
#31418912240` failed on one step: *Negative self-test (the example must set
run.loop.mode explicitly)* — a probe whose needle was the one-line
`"loop": { "mode": "off", … }` literal, which stopped matching the moment that block
grew a `queue` and an `arm`. Two commits later the probe was repaired and the merge
closed the red, so nothing shipped broken. What shipped was a window in which `main`
was red and the run did not know.

**Surfaced at:** stage 7 of the *next* release, reading the CI list for a tag — not by
the run that caused it.

**The stage that owned it:** stage 7 of the run that pushed. It ran `npm test` and
pushed on its verdict.

**Root cause.** `npm test` and `npm run test:all` answer different questions. The first
asks *does the validator pass over this tree*; the second asks *does every guard still
reject its planted defect*. A change that edits the shape a probe plants into breaks
only the second, and the doctrine's own words for it are already written: a guard nobody
has watched fail is a decoration, and a probe whose needle matches nothing is that
decoration's probe.

**The class, and this is its third instance in one session.** A plant keyed to
formatting tests the formatting. Three v1.39.0 plants swapped a phrase and left sibling
occurrences alive; `cl9` held a stale count; this one held a stale JSON literal.
`audit.md` says a class seen twice becomes a mechanism rather than a third ledger row —
so it is `B-057`, with the mechanism named: plant through the parser where one exists,
and check that a needle still occurs in the file it targets.

**Fixes by grade.**

1. *(mechanical)* The probe now plants through `json.load`/`json.dump` and asserts its
   own message rather than any non-zero exit — it would previously have counted an
   unrelated failure as success.
2. *(mechanical)* `B-057` carries the sweep: a needle-occurrence check over every probe.
3. *(standing instruction)* **None added.** R-004 already says the next command must be
   conditional on a gate's exit code; nothing said *which* gate. The rule that would
   have caught this is `npm run test:all` before a push that touches a guard or the text
   a probe plants into — and that is a check, not a standing instruction, which is why
   it goes to the board rather than to the cap of ten.

**The check that catches it next time:** the needle-occurrence sweep in `B-057`. Until
it exists, the honest statement is that this run found the incident by reading a CI list
it had no reason to read, which is luck wearing the clothes of diligence.

### 2026-08-10 · `findings-entry` · the guards were written by the person who wrote the defect

**Symptom.** Nine validator guards, written in one hour to hold a boundary this release
had just restated, were defeated **fifteen ways** by the independent reader R-005
requires — each way verified by planting the text and watching `npm test` print `PASS`.
Adding the six missing probes then found a sixteenth the reader had not.

**Surfaced at:** stage 7, by the reader. Not by the suite: the suite was green, 227 of
227, over guards that a presence test could satisfy without the rule saying anything.

**The stage that owned it:** stage 5. The guards and their probes were written together,
by the same reader of the same sentence, in the same hour — which is the exact condition
R-005 names.

**Root cause, and it is one sentence.** A check written to hold prose is tested against
the prose in front of its author. Three shapes recurred: a presence test over a whole
file proves a word exists, not that the rule says it; a corpus joined without its
categories lets a negative control certify coverage; and a regex over prose is one
innocent rewrite from dormancy — including the anti-dormancy sentinel added in this same
release, which was itself one synonym from dormant.

**The sharpest instance,** because it is about this repository's own honesty: the
eval-coverage guard joined every query regardless of category. Deleting all four findings
evals and mentioning the words in one `should_not_trigger` control certified *named and
untested* — the state the guard cites `B-046` for — as covered. A guard can be wrong in
the exact way it exists to prevent.

**Fixes by grade.**

1. *(mechanical)* All sixteen fixed: both cross-surface checks scoped to `## Routing`;
   eval coverage reads `should_trigger` only; the reading heuristic is a family adjacent
   to `code` and runs on all three surfaces; the locked-verb check reads the trigger
   half; classes are extracted as pairs with their count compared to the `/` count; four
   silent skips print in `unlooked`; three would-be-dormant regexes fail loudly.
2. *(mechanical)* Guards 227 → **233**. The false-positive budget stayed at zero: the
   reading heuristic was narrowed when it fired on `mapping code so a person can read
   it`, a sentence that excludes mapping.
3. *(standing instruction)* **None added.** R-005 already says this and already fired —
   it worked exactly as written, on its second use. A rule that fires and is obeyed does
   not need a sibling; it needs the run after it to keep dispatching the reader.

**The check that catches it next time** is the one that caught it this time — a reader
that is not the author, dispatched by a stage rather than by a repository happening to
run a bot. What this run adds is evidence about its yield: **fifteen findings from nine
guards, from a reader given one prompt and no other context.**

### 2026-08-10 · `skill-audit` · the doctrine was right and nobody could read it

**Symptom.** An audit measured this skill rather than reading it, and the finding was
not that any rule is wrong. It is that the **stage-0 reading floor was ~47 750 tokens**,
that the launch instruction was **one 1281-word paragraph carrying 25 obligations**, and
that the bundle spends **one `never` per 227 words** across 77 230 words. Volume is
itself an instruction, and the instruction it gives is *skim*.

**Surfaced at:** an audit the operator asked for, with fresh eyes. Not by a gate — every
gate here measures an artifact, and none measures whether the artifact was read.

**Owned by:** no stage, which is the finding. Nothing in eleven stages asks *is this
readable?* — the closest thing was a checklist marked *"copy it, tick it"*.

**Root cause.** Every release added correct doctrine to a file that was already being
skimmed, and each addition was individually justified. There is no mechanism anywhere
that pays a cost for length, so length was free and reading was not.

**Fix, by grade.**
1. *(mechanical)* The command file is eight headed sections. The retro's **narrative
   log** — 10 937 of its 14 756 tokens, and the one section nothing caps — is queried
   rather than read in full; the floor fell to ~36 950. A guard holds it, scoped to the
   **sentence**, because paragraph scope let the word *queried* one clause away cancel
   the check and both plants passed.
2. *(mechanical, and the one to keep)* **`test/probe.py`**. R-001 asked for it on
   2026-08-03 and named it as its own retirement condition; it was never built, and
   three probes failed in one day for want of it. Its third assertion — *the guard that
   fired is the guard under test* — **caught two of this release's own guards being too
   loose on its first use**, before either reached a reviewer.
3. *(mechanical)* Stage 7 now dispatches the reader and reads its **output**, with
   `NO READER` a printed state. `learned.md` rule 22 makes the silent no-op a named class.

**Retired: R-001**, its trigger met by the harness. First retirement in this project's
history, and it is the honest one — the rule said what would replace it, and that thing
now exists.

**Three findings reported and not fixed**, which R-006 exists to make me say plainly:
`stages.md` is still 13 161 tokens (B-043); 340 prohibitions still carry equal weight
(B-044); 92 hand-written counts still face 10 registered classes (B-045). Each is a
sweep, not an edit, and pretending otherwise in a close-out is the failure this file is
for.

**And the audit over-claimed, in the paragraph that measured everything else.** Its table
said `stages.md` was *"read in full at stage 0"*. Grepping the obligation returns only
the retro. Corrected in place, weaker and true — a measurement report is not exempt from
the rule it is measuring against.

**The check that catches it next time:** for the reading floor, the sentence-scoped
guard. For a probe that proves nothing, the harness. For *"the doctrine grew and nobody
paid for it"* — nothing, and that is the honest end: no check can decide whether a file
is worth its length.


### 2026-08-10 · `pipeline-audit` · the reader that did not read, and three probes wrong before their guards

**Symptom.** Four modules of guard work — 188 → 210 checks — reviewed by nobody. R-005
requires an independent reader on any change that adds or widens a check; this programme
was almost entirely that, four pull requests were opened for it, and the review app
reported **`skipping`** on every one. The instruction was followed to the letter and the
reading never happened.

**Surfaced at:** stage 10's ladder walk, reading the PR check states rather than assuming
them. Not by a gate — no gate asks whether the reader that was dispatched actually ran.

**Owned by:** stage 7. That is where the reader is supposed to read, and where "an
independent reader was requested" was allowed to stand in for "an independent reader
reported".

**Root cause, and R-005 wrote it down at birth.** Its own retirement condition says the
reader should be *"dispatched by a stage rather than by the repository happening to run a
bot on PRs"*. The bot is that dependency, and it declined. Board row B-003 has recorded
the same thing since 2026-08-08. The gap is not that the rule went unread — it is that
the rule's mechanism is a third party with no contract, and nothing checks its output.

**Fix, by grade.**
1. *(none mechanical, and saying so is the honest end.)* No check here can read a review
   that was never written. What the run can do it did: **REQ-023 is `partial` in the
   acceptance table, printed as `abstained: 1`, and named as a live instance of B-003.**
   R-006 exists for exactly this sentence — reporting a gap is honest and is not a fix.
2. *(no new standing instruction.)* A seventh row saying *"check that the reader
   actually read"* would be a variant of R-005, and a capped list stops being read the
   moment variants start joining it.

**What the run's own probes were worth, measured.** Three of them were wrong before their
guards were, and each failure was a different flavour of the same mistake — *the probe
planted where it was convenient rather than where the check reads*:

| The probe | Why it proved nothing |
|---|---|
| the ledger's line shapes | removed **one of three** `touch:` lines; the shape stayed shown and the guard was correctly silent |
| the CHANGELOG guard count | the release entry wrote the count without the colon the plant matches, so the decrement landed in an **already-released** section |
| the stage-3 track | deleted the SHOUTED spelling and left `visual track` in the refusal sentence — one spelling removed, the class intact |

**And one guard could not see the thing it was written for.** P4's check that makes the
doctrine's own worked issue obey its own redaction rules stayed silent against an
absolute path, a commit id and a foreign repository slug. Its fence scan matched ```` ``` ````
followed by a newline, and a ```` ```json ```` block one paragraph above made every later fence
pair with the wrong delimiter — so it never read the block at all. **Five scans across
four modules had the same defect.** R-003 fired: all five were swept in one change and
the earlier modules' probe harnesses were re-run to prove nothing broke.

**A live defect the new cross-file guard found before it found anything of mine.**
`companion-skills.md` had pointed `chrome-devtools` at **stages 5–6** since the row was
added, and stage 5 had never named it. Nothing compared the matrix's *"needed for stage
N"* cell against what that stage says, so a recommendation existed for a stage that had
not heard of it.

**And R-004 fired on the first command of the run.** `npm test | head && git commit`
reads `head`'s status, so a commit landed over a red validator. The rule is two years of
this repository's history in one line and it still had to fire.

**The check that catches it next time:** for the fence class, the five repaired scans and
the probes that re-ran. For the matrix–stage seam, the new guard. For a reader that does
not read — nothing, and that is B-003's job, not a seventh rule's.


### 2026-08-10 · `planning-system`/N3+N4+N5 · three board rows described the failure I kept hitting

**Symptom.** The negative suite failed and hung for most of a working day: concurrent
runs clobbering each other's `/tmp` scratch, a thirteen-minute serial pass long enough to
get backgrounded, and copies taken from a working tree I was editing at the time.

**All three were already written down.** B-005, B-021, B-023 — on the board this very
programme built, by me, before any of them fired. I read them as a queue of someday-work
rather than as a description of what was blocking the step in front of me.

**Surfaced at:** the operator, saying *"your runs fail and hang forever."* Not a stage,
not a check, not the board — a person watching from outside.

**Owned by:** stage 0 of every iteration since the board existed. The harvest reads the
board. Nothing in it asks *"is one of these rows the reason the current step is failing?"*

**Root cause, and it is the honest one.** A queue answers *what should we do next*. It
does not answer *what is biting us right now*, and those are different questions asked of
the same rows. The exposure line and `/task-pipeline checkup` shipped in this module exist
precisely to surface a standing condition **before** work rather than when somebody thinks
to look — and I built both without once running them on myself.

**Fix, by grade.**
1. *(mechanical)* One snapshot, eight workers: **13+ min → 5m34s**, measured. Every test
   runs against a pristine copy, so editing the tree mid-run is harmless. All three rows
   closed by behaviour rather than by a note.
2. *(mechanical, and the parallel run earned it immediately)* Three shipped steps read
   `rm -rf /tmp/X && cp -R . /tmp/X-2` — deleting a directory they did not own. Harmless
   while the suite was serial; a race the first hour it was not. The existing reuse guard
   never saw them because it compared only `cp` targets while the defect lived in the
   `rm`. Both now checked.
3. *(no new standing instruction.)* The candidate — *when a step fails twice for the same
   reason, search the board before diagnosing* — is a judgement rule, and the list sits at
   six of ten. It goes into the next prune's argument, not silently into the list.

**Two self-inflicted guard defects, kept because they rhyme.** The exposure guard's needle
looked for *"never a percentage"* while the doctrine it guards says *"no percentage,
ever"* — guard and prose written an hour apart, already disagreeing. And its `%` check
matched **its own line**, the one line in the file guaranteed to contain the literal, and
passed a planted percentage. A detector that matches itself first is checking the wrong
thing.

**And the ordering promise was inverted.** *"Oldest first"* compared version strings, so
`v1.10.0` sorted before `v1.9.0` — with the list truncated at eight, the genuinely oldest
rows never printed at all. The doctrine said one thing and the code did another on this
repository's own data, and a reader found it.

### 2026-08-10 · `planning-system`/N2 · the file whose job is not to claim things claimed three

**Symptom.** Ten review rounds, roughly twenty findings, **none from my probes**. The
doctrine landed on the first pass and was never argued with. Three findings were one
shape, and it is the shape worth the entry:

- `Auto=pass` written on all ninety-nine rows while four coverage verdicts read
  **`review`** — *no check can decide this*;
- four REQs recorded as **shipped** while the modules that would ship them did not exist;
- one REQ stamped with the release *before* the file its criterion requires existed,
  contradicting the row directly beneath it.

In the file built specifically so that a machine cannot claim a person looked. It claimed
three other things instead, in its first seeding, from a script I wrote in five minutes
after spending an hour on the doctrine forbidding exactly that.

**Surfaced at:** stage 7, by a reader who compared two adjacent rows and saw them
disagree about a date.

**Owned by:** stage 5. The doctrine was the careful part; the seed was the afterthought,
and the seed is what shipped a false record.

**Root cause.** A generator writes what its author assumed, not what the sources say, and
nothing compares the two. [`learned.md`](../../plugins/task-pipeline/skills/task-pipeline/references/learned.md)
rule 9 — *a generator seeds green* — one level out: here it seeded **truth-shaped**.

**Fix, by grade.**
1. *(mechanical)* The REQ is checked against the brief the row **names**, not the union of
   all briefs — ids 001–014 recur across all nine, so the union check passed almost any
   mispairing. `review → none` is in the template and the doctrine. Rows for modules that
   have not shipped are omitted rather than stamped.
2. *(nothing above that.)* R-005 dispatched the reader and the reader found all of it.

**The check that catches it next time:** for pairing, the guard. For *"the seed wrote what
I assumed"* — nothing mechanical, and saying so is the honest end of this entry. No check
compares two adjacent rows for a contradiction about a date. A person did.


### 2026-08-09 · `planning-system`/N1 · everyone who reads a value, and not the file that writes it

**Symptom.** Ten review rounds, twenty-nine findings, none of them from my probes. The
doctrine landed on the first pass and was never argued with. Every finding was in the
machinery, and they sort into two classes that are really one.

**Class one — the detector reversed three times.** Positional read the wrong cell in the
five ledgers that carry *two* status columns. Pure-text then broke in **both directions
with one regex**: too strict for a live row worded *"open as a printed exclusion"*, too
loose for a description reading *"Open-source …"*, because a hyphen is punctuation
exactly like the arrow. The answer was in between — the header names the candidate
columns, all of them, and a status matches on a word boundary *inside* them.

Between those, the worst single defect: tightening against the false positive, I
hand-listed the separators and **omitted the arrow my own annotations use**, so all
twenty-four resolved rows went invisible and the guard passed by seeing nothing at all.
One negative test covered that path and caught it. That is the suite's entire argument
in a sentence.

**Class two — the doctrine promised what the code did not do.** Five times. `open` alone
while the prose said `backlog`; `backlog` added while `unresolved` was still only
promised; *"two triggers"* in a file whose code checked three; a comment claiming
coverage of adjacent tables it never tested for; a guard against false success that
verified a word appeared *somewhere on the page*.

**Surfaced at:** stage 7, ten rounds, by a reader.

**Owned by:** stage 5 for the detector, stage 3 for the promises — an enumeration
written in prose and enforced in code is two artifacts, and nothing compared them.

**Root cause, and it is the last finding.** The value nobody owned — a ledger row homed
`backlog`, pointing at a place the pipeline named and did not own — came from
`templates/carryover.md`, whose worked example showed exactly that as a *settled*
outcome. **Six rounds went into the doctrine, the guard, the board and three consuming
surfaces before anyone opened the file the value came from.** Fixing every reader and
not the writer is a shape worth its own name.

**Fix, by grade.**
1. *(mechanical)* The trigger enumeration is now **extracted from the regex** and
   required to appear in the paragraph that enumerates it, both directions — the class
   that ran through six rounds, closed by computation rather than a sixth correction.
   The seeded ledger template names three unsettled values and its example carries a
   real id. Nineteen new guards and three new property checks; a property check exists
   because *"the guard stays quiet on the valid pattern"* is not a rejection and does
   not belong in a suite of rejections.
2. *(nothing above that.)* R-005 dispatched the reader and the reader found all
   twenty-nine. R-001 fired twice on my own probes, R-002 on a mis-applied batch, R-004
   on a commit chain that ran past a failing edit.

**The check that catches it next time:** for the promises, the computed enumeration. For
the origin — nothing mechanical, and that is the honest end of this entry. Nothing told
me to read the file that writes the value rather than the files that read it.


### 2026-08-09 · `audit-followup`/M6 · the module was right, the guards were not

**Symptom.** The doctrine this module set out to write landed intact and unchallenged:
`learned.md` gets no cap, because a cap belongs to a file read *in full* every run and
this one is entered by citation. Four measurements refused the original premise before a
line was written, and none of the eight review rounds argued with any of them.

**Every one of the twenty findings was in the machinery.** Two were red, and both were
the same shape:

- Deleting the **highest-numbered** rule shrinks `max()` with it, so the silent-deletion
  guard sees no gap at all. My probe planted mid-list — the shape the author imagines.
  The reader deleted the last row.
- The cross-commit comparison read the mark at `HEAD`, which **equals the working tree on
  a committed checkout** — i.e. in CI. It fired only in the local pre-commit window, and
  its self-test exercised exactly that window. Green everywhere, blind everywhere it ran.

**Surfaced at:** stage 7, eight rounds, twenty findings, **none from my probes**.

**Owned by:** stage 5 for the guards; stage 6 for the probes, which is the same sentence
said twice — the probe and the guard were written by the same model of the problem, so
the probe could only confirm it.

**Root cause, and it is one thing.** *A check's scope is a claim about where it applies,
and mine were always narrower than the shipped surface.* Three hand-written corpora had
each missed a live file. One probe planted in the middle of a list. One check ran in a
window nobody deploys from. One property test lived only in CI, so the local gate was
blind to it — and CI failed on a string this same change had renamed. One citation
naming two guards was parsed as naming none, exempting itself from the invariant it was
written under. **Nobody notices a corpus that is too small, because everything inside it
passes.**

**Fix, by grade.**
1. *(mechanical)* Corpora are **discovered**, not listed (`_discover_md`), each exclusion
   carrying its reason. The high-water mark is compared against every value the file's
   history has held. Both directions checked — a gap has one side, and so does a
   resurrection. `test/negatives.py` runs property checks too, with their own floor,
   their own `-k` selection, their own heading, and a verdict that says what ran rather
   than *"all 0 guards pass"*.
2. *(mechanical, and the one to remember)* A probe must be able to **fail for its own
   reason**. The anchor test tripped a different check and so could not tell a working
   anchor from a regressed one; it now flips when — and only when — the anchor is
   reverted, which is what *"this test measures that"* means.
3. *(no new standing instruction.)* R-005 already dispatches the reader, and the reader
   found all twenty. Adding a seventh rule would say what the sixth already says.

**The check that catches it next time:** for the corpora, discovery. For the mark, its
own history. For probes — nothing mechanical, and saying so is the honest end of this
entry: the only thing that found these was somebody who did not write them.


### 2026-08-09 · `audit-followup`/M5 · three summaries of one list, each complete on its own

**Symptom.** The module was written as *"add a sixth rotation axis"*. Measuring before
building — the discipline that has now changed four modules of six — found that the five
that existed were already summarised **three different ways**: `audit.md` defined five,
the Cursor rule named four, README named three. Nothing was wrong in any single file.
A list of three orthogonal things is a convincing list of three orthogonal things, so
each summary read as complete, and no reader had two of them open at once.

Then the PR that fixed this **committed the same defect inside itself**: it retitled
`gates.md` to *"the three axes"*, propagated that to README, `SKILL.md` and
`CONTRIBUTING.md` — and left the Cursor rule's own Gates section saying *"two axes"*
with no Axis C at all, fifty lines below an edit the same PR had made to that file.
Found by the reader, not by me, and invisible to every check: the claim registry's
corpus held neither the Cursor rule nor the command file.

**Surfaced at:** stage 7, four rounds, eight findings, **none of them from my probes**.

**Owned by:** stage 5 for the Cursor-rule miss (the file was open); stage 3 for the
spec, which promised a guard that was never built and a threshold the code did not use.

**Root cause.** A guard's corpus is a claim about where the rule applies, and mine was
narrower than the shipped surfaces. The registry was written when `references/` was the
whole world; the Cursor rule and the command are shipped doctrine that restate counts
like anything else, and they were simply never added. Nobody notices a corpus that is
too small, because everything inside it passes.

The first version of the new guard also measured the wrong unit — scoped to the file,
it accused `stages.md` of enumerating three axes whose three hits were 595 lines apart
and meant three different things. Vocabulary is not enumeration. That is the third time
in three releases that a guard in this file was defeated by **how the corpus stores a
sentence** rather than by what it says.

**Fix, by grade.**
1. *(mechanical)* The registry corpus now includes the Cursor rule and the command —
   proven live rather than assumed, because the `gates.md` axis count moved **6 → 7**
   the moment they were added. The enumeration guard is paragraph-scoped and derives
   its keys from `audit.md` at check time. `_flatten()` and `_paragraphs()` replace the
   three and four hand-rolled copies of the two idioms that keep defeating these guards.
   Eight new self-tests, including one that plants in `audit.md` itself and one that
   removes the guard's own source of truth.
2. *(mechanical, and the round-three finding worth keeping)* A **dormant** claim class
   is not a proven one. `rotation axes` matched nothing in the corpus by design, so its
   fail branch had never executed — dormant is green here, which is exactly why a
   dormant class still needs its plant.
3. *(none above that.)* R-005 fired and the reader found all eight.

**The check that catches it next time:** for the corpus, the two files are in it. For
the unit, the helper's docstring says what the choice costs. For a summary that lists
most of a list — the paragraph guard, which is the first mechanical answer this
repository has had to that shape.

**Re-derivation, used on the review itself.** The reader estimated the redundant-read
class at "3+"; an instrumented run counting `open()` rather than a grep of the source
returned **25 reads of `audit.md` and 668 `.md` opens**. Eight times low — and the axis
this module shipped is exactly the instruction to print that pair instead of asserting
agreement. Carry-over row 12 carries the number.


### 2026-08-09 · `audit-followup`/M4 · a section that named eight and disposed of seven

**Symptom.** The module counted abstentions for the first time. Its doctrine section opens
by naming **eight** vocabularies for declining to claim, sorts three into `abstained`, two
into `unlooked`, and excludes two by name. That is seven. **`review` was named and then
appeared in no bucket and no exclusion** — it simply stopped being mentioned.

In the section whose entire subject is *abstentions nobody counts*.

Four more from the same review, all mine: the guard held four reference files and not
`templates/carryover.md` — a template **seeded into host projects**, which teaches the
verdict format to everyone who installs the skill; the section-citation checker could not
see the citation this change added, because its matcher wants a bare filename in backticks
and the label this change wrote carries a path — `references/gates.md`, not `gates.md`, in the
backticks before the parenthesis; the shipped self-test removed both counts
at once and so proved neither was required alone; and `stages.md`'s stage-10 gate was left
behind while stage 6 in the same file was updated.

**Surfaced at:** stage 7, all five, by review.

**Owned by:** stage 3 for the omission — an enumeration is a design artefact, and this one
was written and never read back against itself. Stage 9 for the template.

**Root cause.** A list does not check itself. Naming eight and handling them one at a time
is exactly the shape where the last item is lost, because attention runs out on the ones
with interesting answers — and `review`'s answer *is* the interesting one: it is not a
claim the run declined, it is a rule that **declined to be mechanical**, so counting it per
run would report the same standing number forever. The item hardest to place is the item
most likely to be dropped.

This is `audit.md`'s own thesis at paragraph scale: *a contradiction has two sides and an
absence has one*. Nothing in the paragraph contradicted anything. `review` was simply not
there, and only counting the names against the buckets finds that.

**Fix, by grade.**
1. *(mechanical)* Each uncounted vocabulary now carries its own line **and its reason**, so
   an omission shows as a missing bullet rather than as silence. `templates/carryover.md`
   joins the guard's file list — second time this programme that an obligation reached the
   doctrine and not `templates/`. The citation matcher accepts a path-prefixed label; the
   corpus stayed green after widening, so nothing had gone through the hole, but the hole
   was open. Two per-disclosure self-tests replace the one that removed both at once.
2. *(none needed above that.)* R-005 fired and the reader found all five.

**The check that catches it next time:** for the template and the citation form, the two
widened guards. Writing this entry then hit the same class one level down — spelling the
citation form out literally *is* a citation, and the link checker resolved the ellipsis inside
it as a path and failed the suite. Correct behaviour, and the reason the form is now described
rather than written. For an enumeration that loses its last item — nothing mechanical, and that
is worth saying plainly rather than inventing a guard that would only fit this paragraph.


### 2026-08-09 · `audit-followup`/M3 · a guard that skipped the file defining the thing it guards

**Symptom.** The module gave the cold-retirement trigger a second unit and shipped a guard
holding both units together across every surface. Review returned **two Important** — the
first of this programme — and both were in that guard.

(a) The matcher never matched `references/retrospective.md`. Its canonical row reads *the
last **five run stamps***, with the emphasis markers **inside** the phrase, and the guard
normalised whitespace only. The one file that **defines** the trigger was silently skipped.

(b) `commands/task-pipeline.md` restates the retirement triggers verbatim, still carried
only the stamp unit, and was not in the guard's surface list. The guard's own comment said
*seven surfaces* over a list of six.

**Surfaced at:** stage 7, both, by review.

**Owned by:** stage 6. The guard was probed — once, against `acceptance.md`, which has no
bold interrupting the phrase. It fired, it was green, and it had never read the canonical
file.

**Root cause.** A probe demonstrates that a check can fire. It does not demonstrate *what
the check reads*, and choosing the most convenient file to plant in selects for the surface
with the least formatting. Both defects were **silent**: green over a file never opened,
and green over a file never listed.

Underneath is a class this bundle has now met three times, always by **formatting rather
than content** — a citation wrapped across two lines, a marker split by the ~80-column wrap,
and now emphasis inside a phrase. Each was recorded as a comment in the guard that hit it,
and [`gates.md`](../../plugins/task-pipeline/skills/task-pipeline/references/gates.md) —
the file that teaches how to write a check — said nothing.

**Fix, by grade.**
1. *(mechanical)* Emphasis is normalised alongside whitespace; the seventh surface is in the
   list and corrected; the comment's count is replaced by *the list is the count*. A negative
   self-test now plants **in `retrospective.md`**, the file the old guard skipped.
2. *(doctrine — the class, not the instance)* `gates.md` → *Writing the check itself* gains
   the rule with its three incidents in a table: normalise the corpus's own formatting, state
   which unit you chose, and **plant the probe in the file that defines the thing** rather
   than the most convenient one. `audit.md` says a class seen twice becomes a mechanism; this
   was the third, so a fourth comment would have been the thing that rule forbids.

**Standing instruction: none added.** R-005 requires an independent reader on a change that
adds or widens a check; it fired and found both. The gap was never that a rule went unread —
it is that the probe was written from the same model as the check, which is R-005's own
stated limit, and `gates.md` now carries the mechanical part.

**The check that catches it next time:** the new self-test for this instance; for the class,
the `gates.md` rule and the next reviewer.


### 2026-08-08 · `audit-followup`/M7 · a one-directional check, in the repository whose rule 2 is both directions

**Symptom.** The module added a guard comparing the companion **matrix** against the
**preflight block** — the two places `companion-skills.md` states the same list. It
checked matrix → preflight and stopped.

`learned.md` rule 2 is *absence needs its own check: compute the mapping in **both**
directions*, and its incident is four fully-specified entities with no schema anywhere,
found only by the direction that felt redundant. The reverse here is a real failure with
its own shape: a preflight line whose companion the matrix never explains, so the operator
is asked to install something nobody told them the purpose of. It would have passed in
silence.

Three smaller ones in the same review, all in this change: a suffix strip that could never
match (the capture stopped at a space before the token it was meant to strip, so the code
looked like it handled *"Figma MCP"* and did nothing); `SKILL-CARD.md`'s **risk disclosure**
not naming the MCP this release adds — the page a reviewer reads *before* deciding to trust
the skill; and a stray space before a comma from appending a clause to a line that already
ended in a bold marker.

**Surfaced at:** stage 7, all four, by the review.

**Owned by:** stage 6 for the guard, stage 9 for the disclosure — that is a propagation
row, and the matrix in `docs/DOCMAP.md` names `SKILL-CARD.md` for a user-visible change but
not for a new **capability reference**, which is what an added MCP is.

**Root cause.** Writing a check exercises the parts of the doctrine you are thinking about.
This one was written while thinking about rule 20 — *a thing that exists twice* — which it
gets right. Rule 2 was not in view, and nothing brings it into view: `learned.md`'s table
is read at the stage that *binds* it, not at the moment a new check is being written.

**Fix, by grade.**
1. *(mechanical)* Both directions now computed and both probed — the reverse plant fails,
   which it did not before. The suffix strip is live. `SKILL-CARD.md` names
   `chrome-devtools` **with what makes it different**: it drives a real browser, opens
   pages, runs scripts in them and reads console and network traffic. A reviewer deciding
   whether to trust the skill needs that, not the bare name.
2. *(note, expires in two runs)* `docs/DOCMAP.md`'s propagation matrix has no row for
   *adding a capability reference* (an MCP, a tool the doctrine names) as distinct from a
   user-visible capability. That is why `SKILL-CARD.md` was not walked.

**Standing instruction: none added, deliberately.** R-005 already requires an independent
reader on a change that adds or widens a check, it fired, and the reader is what found all
four. The gap is not that the rule went unread — it is that `learned.md`'s own table is not
consulted **while writing** a check, and that is one instance of rule 2 rather than a new
class. A seventh row for a variant of an existing rule is how a capped list stops being
read.

**The check that catches it next time:** nothing mechanical for the general case. For this
instance, the guard's own bidirectional probe, and the matrix note above.


### 2026-08-08 · `audit-followup`/M2 · a limit made visible, reported as a limit removed

**Symptom.** Review round two found that the claim registry's number-word map stopped at
forty-nine while the guard count it checks was already 130 — so any claim written as a word
above the ceiling would be **skipped without a word**. The fix shipped was to collect
unparseable tokens and print them beside the verdict, and the finding was recorded as
addressed.

It was not. A word-form claim of *"fifty-two files under `references/`"* was still skipped;
it now merely said so. Review round three reopened it, and the probe settled it: that exact
string is caught today and was not caught then.

**Surfaced at:** stage 7, by the review, twice — once to open it and once to reject the fix.

**Owned by:** stage 6. That is where a fix is supposed to be proven, and where "proven" was
allowed to mean *the gap is now visible* rather than *the gap is gone*.

**Root cause.** `gates.md` is emphatic that a `dormant` or `skip` state must be **printed** —
a mechanism that reports nothing when it looked at nothing is the false success the whole
file is about. That doctrine is correct and it was followed. What no line said is that
printing the gap does not **discharge** the finding. Having done the honest thing, it was
easy to record it as the whole thing.

The three review rounds together found thirteen issues; the module's own five probes found
none of them. That is the second consecutive module with that count, and it is exactly what
`R-005` was added for one release ago — it fired, it was followed, and it does not make the
probes better, because a probe is written from the same model of the problem as the check.

**Fix, by grade.**
1. *(mechanical)* The map now runs through ninety, and the lift was probed against the case
   that exposed it. The eval-runs row was the only one of six bypassing the shared
   digit-and-word matcher — a false negative on the very incident the registry is named
   after — and now uses it.
2. *(mechanical)* `CONTRIBUTING.md` invariant 13 still described the pre-registry single
   check while invariant 35 described the registry: two invariants over one guard, one
   stale. 13 now points at 35 and names no surfaces of its own.
3. *(standing instruction)* **R-006** — a finding is closed when the behaviour changes;
   reporting the gap is honest and is not a fix, and the close-out says which one happened.

**The check that catches it next time:** none, yet — and that is the retirement condition
written into R-006. When a close-out records per finding whether behaviour or only reporting
changed, a check can read that field and the instruction leaves.


### 2026-08-08 · `audit-followup`/M8 · five probes that all passed, and the two defects they could not see

**Symptom.** The change that widens rule 21's guard from one file to the class shipped to
review with two defects its own verification could not detect.

(a) **A proven false-negative path.** The ordered-list branch scanned the whole file and
compared only the *first* prune/stamp pair. A violating list placed after a correct one
was never examined. Four planted-defect probes passed, because every one of them planted
its defect as the first pair.

(b) **A shape with no pair at all.** `evidence-docs/SKILL.md` still taught *"prune first,
cap of ten"* in a table cell. Every shape written so far compares **two** act words;
a cell that
names one is invisible to all of them **by construction**, not by oversight. It was live
in the shipped skill and no probe could have found it, because a probe tests the predicate
you wrote.

**Surfaced at:** stage 7, both — by the PR review bot, on two separate passes.

**Owned by:** stage 6. That is where a new check is supposed to be proven, and where
"proven" was defined as *the probes I wrote pass*.

**Root cause.** A probe is written by whoever wrote the check, from the same model of the
problem. It proves the check catches what its author imagined and is silent about the rest
— which is exactly the failure mode `gates.md` names for a green nobody watched fail,
one level up: here the check *was* watched failing, five times, on five shapes its author
had thought of.

The run also produced three defects in its own **prose** — a surface count stated five
different ways, a 225-character line against this repo's own ~80 rule, and an acceptance
verdict contradicting the ledger it summarised. Those are the same class this release
fixes, committed while describing the fix.

**Fix, by grade.**
1. *(mechanical)* P3 moved inside the paragraph loop — scoped to one list block, **every**
   adjacent pair compared, history exemption computed once per paragraph including the
   preceding one. P5 added for the lone directive. Four negative self-tests; floor 120 → 124.
2. *(mechanical)* Every count deleted rather than corrected. The guard's `SCOPE` comment
   now states what it does **not** cover, and invariant 34 points at that comment instead
   of restating the shape count, so the two cannot disagree.
3. *(standing instruction)* **R-005** — an independent reader on any change that adds or
   widens a check. This is the one thing above that no check can decide.

**Axis, measured rather than felt.** `test/validate.py` was edited three times for the
same reason, which is the loop guard's trigger. Split, the two axes disagree: the guard's
shapes gave 5 new findings and 0 self-inflicted (still paying); the run's own prose gave 3
findings and 3 self-inflicted (exhausted). Lumping them would have stopped the half that
was working and continued the half that was not.

**The check that catches it next time:** for (a) and (b), the four new negative self-tests
plus the stated scope. For the class — a check written from its author's own model — there
is none, and that is what R-005 is for.


### 2026-08-08 · `audit-followup` / M1 · a rule fixed in one file of nine, and the wrong copy edited while fixing it

**Symptom.** Three, and the ordering between them is the finding.

(a) **Rule 21 shipped in `v1.23.0` and reached one file.** It changed the retro's act
order to *stamp first* in `references/retrospective.md`; `SKILL.md` (twice),
`acceptance.md` (three places), `stages.md` (three places), `templates/retro.md`,
`templates/README.md` and this repository's own `retro.md` header still said *prune
first* — the exact deadlock the rule defines. `SKILL.md` is what an agent loads first,
so the shipped skill's most-read surface taught the failure its newest rule documents.
The rule-21 guard exists and checks **one file**.

(b) **The version-sync invariant was named `four-way` on four surfaces while
`test/validate.py` enforced five.** `CONTRIBUTING.md` was substantively right — it named
`SKILL-CARD.md` in a following sentence — and still called the set four. `CLAUDE.md` did
not know the fifth surface at all. It surfaced when the release bump failed the guard.

(c) **While fixing (b), the run edited the wrong copy** — `~/CLAUDE.md` instead of
`./CLAUDE.md` — in a change whose subject is *a rule written in two documents is two
rules*.

**Surfaced at:** (a) stage 5, by R-003's sibling sweep, triggered by reading rule 21's
guard to learn where rules 17–21 bind. (b) stage 7, by the validator, on the version
bump. (c) immediately, as a failed edit.

**Owned by:** stage 9 for (a) and (b) — both are propagation. The `DOCMAP.md` matrix has
a row for *"a new document, rule or guard"* naming `SKILL.md`, the README, the manifest
and the Cursor rule; it has **no row for a change to an existing rule's ordering or
contract**, which is why v1.23.0 walked a matrix that did not ask about `acceptance.md`
or `stages.md`. (c) is stage 5 and cost nothing.

**Root cause.** A guard written *per rule* rather than *per class*. Rules 16–21 each got
a bespoke guard naming its consumer files by literal string. That catches a consumer
dropping a citation and cannot catch **a consumer that keeps the citation and contradicts
it** — which is exactly (a): every one of those eight surfaces still cites
`retrospective.md`, and every one states the opposite of what it says.

(c) is different in kind and worth separating: it failed *loudly*. `~/CLAUDE.md` did not
contain the string, so the edit errored instead of landing. Had both files contained it,
the run would have edited the wrong one and reported success — the silent half of the
same class, and the one R-002 exists for.

**Fix, by grade.**
1. *(mechanical, deferred to M8 with its own branch)* Widen the rule-21 guard from one
   file to the class: any surface stating the retro's three acts must state them in the
   order `retrospective.md` states them, compared **mechanically against that file**
   rather than against a literal, so the guard cannot drift from the doctrine it guards.
2. *(mechanical, this change)* Every counted name that undercounts its own list, removed
   rather than corrected — `four-way` and `fifteen rules` both became descriptions. A
   name that counts is a number, and it drifts like one.
3. *(note, expires in two runs)* `docs/DOCMAP.md`'s propagation matrix has no row for
   *changing an existing rule's ordering or contract*, as opposed to adding one. M8 adds it.

**Standing instruction:** none added. R-003 already names this class and **fired
correctly** — it is what found (a). The failure was not that the rule went unread; it was
that the *guard* for rules 17–21 was built per-instance. That is a mechanical fix, so it
belongs in a script (grade 1), not as a fifth row on a capped list.

**The check that catches it next time:** M8's class-comparison guard for (a); the
existing version-sync guard already caught (b) and is why it was found at all; (c) stays
`learned.md` rule 20's territory — *read the consumer to learn which copy ships* — and
`R-002`'s, both stamped as fired.

### 2026-08-06 · `carried-in-claims` · an exit code read through a pipe, and an edit that failed silently

**Symptom.** Two slips inside the change that adds rule 16, both of them the shape
rule 16 is about — believing a report instead of measuring.
(a) A planted-defect run was piped to `tail -2` and `$?` was read afterwards, so the
recorded status was `tail`'s. It printed `planted rc=0 (want non-zero)` while the
validator had in fact returned `1`; the guard was working and the measurement of it
was not.
(b) A python heredoc that inserted the new workflow step raised `ValueError` and
wrote nothing. The step count printed `119` — unchanged — and the failure was
visible only because the next command grepped for the inserted text.

**Surfaced at:** stage 6, both — (a) by re-running the same command without the pipe,
(b) by `grep -c` on the string that was supposed to have landed.

**Owned by:** stage 6. Both were verification steps that reported on themselves.

**Root cause.** `$?` after a pipeline is the last element's status, and a heredoc
that throws still exits the surrounding block cleanly enough to look like a write.
Neither is obscure; both are invisible unless the *result* is checked rather than the
*command*.

**Fix.** (a) Re-measured with `cmd >/dev/null 2>&1; echo $?` — `1` planted, `0` clean.
(b) Re-inserted with `cat >>` and confirmed by grep and by `yaml.safe_load`.

**Standing instruction:** none added. `R-004` already carries this class — *a gate's
exit code must govern what runs next* — and (a) is the same rule one step earlier:
the code you read must be the one you meant. Adding a fifth row for a variant of an
existing rule is how a capped list stops being read. Stamped `R-004` as fired.

**The check that catches it next time:** for (b), the negative self-test added in
this release fails when a consumer file loses its citation, which is what a silently
skipped insertion produces. For (a), nothing mechanical — it is `R-004`'s territory
and stays a review question.

### 2026-08-06 · `graph-staleness` · a guard green because it never looked, and a marker with four spellings

**Symptom.** Two independent failures, both inside the release that names their class.
(a) The new guard requiring the canonical distrust marker compared **per line**; this
doctrine wraps at ~80 columns, so in `README.md` and `stages.md` — where the marker is
split across two lines — it matched nothing and printed `PASS`. (b) The marker itself
was written four ways in one PR: absent from the doctrine's own three worked examples,
a second spelling (*"treat as stale until refreshed"*) in the `unresolvable` row, and
the sigil dropped in the Cursor rule and the config.

**Surfaced at:** stage 5 — (a) by probing the guard with a planted wrapped defect,
(b) by the PR review, which found one instance.

**Owned by:** stage 5 for both. (a) is the guard's own construction; (b) is the edit
that introduced the marker and did not sweep its own siblings unprompted.

**Root cause.** (a) A check whose predicate is *"the needle is on this line"* silently
assumes the source is not wrapped — and the one thing certain about this repository's
prose is that it wraps at ~80. The guard's own green was the only evidence anyone had
that it worked, which is the definition in `gates.md` → *False success*. (b) A marker
is a **string**, and its value is entirely that one grep finds every occurrence; four
spellings is not four styles, it is zero markers.

**Fix, by grade.**
1. *(mechanical)* The marker guard now normalises whitespace before counting — probed
   with a planted wrapped defect and watched rejecting it.
2. *(mechanical)* Hygiene **check 7** — a blank line inside a GFM table. The class hit
   **five** times in this run, and on the check's first armed pass it found three more
   in the v1.12.0 and v1.13.0 carry-over ledgers, which had been rendering broken since
   the day they were written. All eight fixed, none baselined behind a floor.
3. *(mechanical)* An undeclared hygiene floor is a failure rather than a zero: check 7
   shipped without `HYGIENE_FLOOR_7` and printed `ok … (floor )` over three real hits.
4. *(mechanical)* The guard count stopped being restated in prose at all — third
   hand-correction in one run, and the guard's message had always offered *derive or
   delete*.
5. *(standing instruction)* **R-004** — a gate's exit code must gate the next command.

**The check that catches each from now on:** negatives *"the distrust marker keeps its
sigil, even wrapped"*, *"the distrust marker gets no second spelling"*, *"the hygiene
gate catches a blank line inside a table"*, *"the hygiene gate refuses an undeclared
floor"*.

**What R-003 was worth, measured:** review found **1** of the four marker spellings.
Running its definition against the siblings found the other **3**. The instruction did
three quarters of the work on this run.


## Releases that carry no stamp — stated, not stamped

Ten consecutive releases, **`v1.16.0` through `v1.23.0`**, shipped without a run of this
pipeline: no brief, no spec, no acceptance, no stamp. Measured, not recalled —

```bash
git tag -l 'v1.*' --sort=-v:refname | while read -r t; do
  s=$(git rev-list -n1 "$t" | cut -c1-7)
  grep -q "$s" docs/superpowers/retro.md || echo "$t $s no stamp"
done
```

**No stamps were written for them, deliberately.** A stamp asserts that a run happened and
that its gates were walked. Writing ten to make the table look continuous would be the exact
defect this file exists to catch, on the file that catches it. The gap is recorded here
instead, which is the honest form of the same information.

Two consequences worth stating rather than leaving to be rediscovered:

- **The cold-retirement trigger was unreadable across that stretch.** It counts firings
  across the last five run stamps, and the counter moved four times in fourteen releases. It
  was not strict or lenient — there was nothing to read. That is why the condition now carries
  a second unit, sixty days, which nothing can stall
([`references/retrospective.md`](../../plugins/task-pipeline/skills/task-pipeline/references/retrospective.md)).
- **The lessons of those ten releases are in `CHANGELOG.md` and nowhere else.** They are not
  lost, and they are not where the next run's stage 0 looks. Rules 17–21 of `learned.md` were
  all earned in that stretch and reached the shipped doctrine directly, without passing
  through a retro — which is why five of them sat outside the *Where these bind* map until
  `v1.23.1` found it.

## Run stamps

One line per run, appended at stage 10, **capped at ten** — at the eleventh the
oldest rotates whole into `retro/YYYY-QN.md`. This is what makes "five runs"
countable; without it the cold-rule is a guess and the prune becomes a mood, and
without the cap the countable thing grows inside a section read in full.

| Date | Topic | Commit | Verdict | Retro |
|---|---|---|---|---|
| 2026-08-11 | `hand-back` / the-rail-said-where | `5ec4cdd` | four sections and two lists at both boundaries, gated at stage 10 across **four** surfaces · **the reader found the release built what it had just condemned** — a gate criterion with no artefact — so the hand-back now lands as a `hand:` line in the run ledger · six guard defects and four doctrinal, all planted and watched passing · guards 253 → **261** · six neighbour-answered predicates, all caught by their own probes rather than by a reader | 1 entry · 5 standing · retired 0 · added 0 · **stamps 11 → 10 (1 rotated)** · R-002, R-003, R-005, R-006 fired |
| 2026-08-11 | `neighbour-probe` / B-057 `plant-the-evidence-next-door` | `ac6e5db` | the neighbour probe as doctrine + three implementing it · **the doctrine failed its own first use** — one probe planted the needles of two RETIRED predicates · eight reader findings closed and each replayed failing, including a **declared span that was false** and a **silent loss of coverage** on a rekey · guards 250 → **253** · R-002 fired: a fix batch raised on its third edit and never wrote the file | 1 entry · 5 standing · retired 0 · added 0 · **stamps 11 → 10 (1 rotated)** · R-002, R-003, R-005, R-006 fired |
| 2026-08-10 | `stamp-cap` / B-055 `one-line-per-run-is-a-slope` | `141294a` | stamps capped at ten, 18 rotated whole into the archive · stamp section 2 099 → **1 088 tok**, read portion 3 333 → **2 335**, stage-0 floor → **~35 300** · **the reader found six ways past the first cap guard**, one of them the stamp shape this doctrine's own command writes · four surfaces had never learned the rule · a hand-written 21 was a computed 18 · guards 248 → **250** | 1 entry · 5 standing · retired 0 · added 0 · **stamps 11 → 10 (1 rotated at this prune)** · R-003, R-005, R-006 fired |
| 2026-08-10 | `loop-mechanism` / B-054 `the-loop-had-no-queue` | `64fcc6b` | the queue, `mode: dynamic`, `run.loop.arm`, the goal re-read between items · **R-005's reader found a contradiction the guards could not**: Part 1a armed unconditionally and overrode the file's own `Default off` · six guard defects, all planted and watched passing · guards 233 → **248** · **a red CI reached `main` on `5a77053`** — pushed after `npm test` without `test:all` | 1 entry · 5 standing · retired 0 · added 0 · R-003, R-005, R-006 fired |
| 2026-08-10 | `findings-entry` / B-047 `the-word-audit-could-not-reach-it` | `0df1e7a` | 8 REQ verified, 1 with its scope corrected (three surfaces, not four) · **routing measured on fresh agents, 7/10 → 9/10 → 8/10** — bug hunt and PR review moved in both after-runs, the production check in neither · **R-005's reader defeated the nine new guards fifteen ways**, all fixed, and the six added probes found a sixteenth · guards 218 → **233** · evals 21 → **28** | 1 entry · 5 standing · retired 0 · added 0 · R-003, R-005, R-006 fired; R-002 and R-004 did not |
| 2026-08-10 | `skill-audit` / fixes `trigger-wall-probe-floor` | `b7778c9` | 9 of 12 plan items · the command wall 1281 → 295 words · the description 1015 → 956 with both no-task modes named · **`test/probe.py` built, and it caught two of this release's own guards on first use** · stage-0 floor ~47 750 → ~36 950 tok · evals 15 → 21 · guards 210 → **218** | 1 entry · **5 standing (was 6)** · retired 1 (R-001, its condition met) · added 0 · R-002, R-003, R-004, R-006 fired |
| 2026-08-10 | `pipeline-audit` / P1+P2+P3+P4 `audit-and-four-modules` | `07e7824` | 12 REQ verified · 1 **partial and reported** (REQ-023: R-005's reader never ran — the review app reported `skipping` on all four PRs) · the audit's 8 findings closed as B-025..B-032 · guards 188 → **210** · **three probes wrong before their guards were** | 1 entry · 6 standing · retired 0 · added 0 · R-001, R-003, R-004, R-006 fired; R-002 and R-005 did not |
| 2026-08-10 | `planning-system` / N3+N4+N5 `exposure-checkup-loop` | `0137512` | 3 REQ · a vector never a probability, the command with no task in flight, the loop citing the board · **one review round by the lowered threshold, 5 findings** · the suite itself fixed: 13+ min → **5m34s** · carry-over 2 rows, 0 unresolved | 1 entry · 6 standing · retired 0 · added 0 · R-001, R-002, R-004 fired · guards 185 → 188 |
| 2026-08-10 | `planning-system` / N2 `verification-ledger` | `85f8c8a` | 3 REQ · the column a machine may not fill · **ten review rounds, ~20 findings, none from my probes** · carry-over 2 rows, 0 unresolved | 1 entry · 6 standing · retired 0 · added 0 · R-001, R-002, R-005 fired · guards 175 → 185 |
| 2026-08-09 | `planning-system` / N1 `the-board` | `4233c3d` | 4 REQ · a queue between runs, and the seam the ledger left dangling · **ten review rounds, 29 findings, none from my probes** · carry-over 2 rows, 2 open, 0 unresolved | 1 entry · 6 standing · retired 0 · added 0 · R-001, R-002, R-004, R-005 all fired · guards 156 → 175 + 4 property |
