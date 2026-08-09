# Changelog

## v1.31.0 — the board, and the pointer that was never the one dangling

The carry-over ledger has always offered `backlog` as a home for a deferred row — a
place the pipeline **named and did not own**. The obvious fix was to build that
backlog. Measuring first changed the target: across ten ledgers in this repository,
**not one row has ever used that value.** The dangling pointer was never `backlog`. It
was `open` — **sixteen rows across six ledgers**, deferred out loud and filed nowhere.

`docs/superpowers/backlog.md` is the board: one per project, **mutable** where the
ledger is append-only, because a queue is re-ranked and a history is not. Rows leave
only into a *Closed* list, with the commit.

**Priority is computed, never assigned:** `prio = sev × blast + age_bonus`, inputs in
the row and the formula in the doctrine, so a ranking can be **checked** rather than
trusted. Two consequences are the point rather than side effects: an old small thing
eventually outranks a new medium one, and a row's priority moves without anyone
touching it — which is what makes the re-derivation at the end of an iteration real
work instead of ceremony.

**Ten ledgers, six different column shapes.** `#` or `id`; the status column named
*Home*, *Where it lives now*, *Resolution*, *Status* or *State*. So the guard finds
columns **by name** — a positional read would have silently checked the wrong cell in
five files out of six, and passed.

Both directions, because they are different failures: a ledger row pointing at an id
nobody issued, and a board row traceable to nothing. Neither is visible from the other
side.

The seam was closed rather than deferred: all sixteen rows carry a board id, so the
floor is **zero** and the next unhomed row fails the build instead of joining a debt.
This repo's own board opens seeded from those ledgers, with several rows that were the
same finding written separately by different runs — collapsed into one each, which is the
job the board exists for. The count is deliberately not restated here: it moved twice
while this entry was being written, which is exactly why this repository deletes
restated numbers rather than chasing them.

**The review found the guard reading the wrong cell in half the corpus.** The status
column was taken by position — and five of ten ledgers here carry *two* status-ish
columns (`status`+`home`, `resolution`+`state`), so "take the last one" read a different
cell per file and passed genuinely open rows in silence. Three more rows carry more
cells than their header and were skipped outright.

The test is now **position-free**: a row is open if any of its cells says so, and homed
if a board id appears anywhere in it. Neither question asks which column it came from,
so neither can be defeated by a shape nobody anticipated. It immediately found **eight
more open rows** — the true count was 24, not 16, and my own measurement was a third
low. Three of the eight were the same *"evals never run"* finding written by three
different runs; the board collapses them into one, which is the job it exists for.

Two more from the same round: the new stage-0 bullet was spliced into the middle of the
word *"the"* and `npm test` did not see it, and `templates/backlog.md` — the file seeded
verbatim into every host project — shipped a worked example that **contradicted the
formula printed two lines below it**. The arithmetic is now a guard, over both boards.

**The class the board logs hit the board itself.** A blank line inside its table split
three rows off into prose — and row **B-004** on that same board reads *"a blank line
silently splits a markdown table, and the documentation gate does not catch it."* Second
instance of a class this repository already had written down, so it became a script
rather than a third ledger row, swept across the whole corpus. B-004 is closed by the
check it asked for.

**A promise is not a check.** Three doctrine passages described stage-10 resolution as
keyed on a ledger row homed `backlog`, and the seeded template said outright that *the
gate refuses it* — while the shipped guard only ever looked for `open`. A reader seeded
a scratch ledger with exactly that row and watched it pass. Both triggers are enforced
now, and the doctrine describes what runs.

The split-table guard, one round old, could not tell *"table split"* from *"table ends,
table begins"* — it never checked whether the line after the blank opens its own table,
which its own comment claimed it did. A **property check** now proves it stays quiet on
the valid pattern, because a checker with false positives is worse than none.

Guards: 156 → **165**, property checks 1 → 2.

## v1.30.0 — the cap that would have measured the wrong axis

The audit's last finding was that `references/learned.md` has no retirement rule while
`retro.md` caps its standing instructions at ten. Four measurements, each with a
differently-shaped command — the rotation axis shipped one release ago, turned on the
backlog that proposed it:

| The belief | The command | Result |
|---|---|---|
| rules accumulate | table rows per tag: 15 → 18 → 21 → 21 | **flat for four releases** |
| growth *is* rules | words per section, v1.23.0 → HEAD | **+223, every word in the binding map** |
| the long incidents duplicate the retro | each incident's distinctive tokens against the whole retro corpus | **zero hits** — they are other projects' events, held nowhere else here |

A cap of N would have squeezed the axis that had not moved in four releases. A word
budget would have cut the incidents, which are the only record of those events anywhere
in this repository. **The finding was right that something was missing and wrong about
what.**

**Why the retro is capped and this file is not**, now written down where the proposal
keeps arriving: a cap belongs to a file you must *finish reading*. The retro's standing
instructions are read in full at stage 0 — bounded by construction, or the last one is
never reached. `learned.md` is entered by citation from twenty-three surfaces and its
binding map is that entrance. **A file you enter through an index needs its index to be
right, not its length to be short.**

**Two triggers retire a rule, and neither is a count:** the conditions can no longer
occur in any project the skill runs on, or the rule is **subsumed** — a merge, where the
absorbing rule names the absorbed one and every binding-map row is repointed in the same
change. Explicitly *not* "it became a check": that trigger is right for a standing
instruction, whose job is to be read until the machine takes over, but here the rule is
the **reason** the check exists, and a check whose reason was deleted is the next thing
somebody removes as noise.

Numbers are never reused and never closed up, so a departure shows as a **gap**, and a
gap the `### Retired` log does not name now fails the build. The log exists while empty
and says so — an absent log and an empty one are indistinguishable from outside, and
only one of them means nothing has been retired.

And the file's **shape** is now printed beside the validator's verdict — rules,
incidents, incident words, binding rows — as a disclosure: computed, no floor, no
direction, **never a target**. Growth becomes visible without becoming a lever.

**The review found a guard that could not catch the thing it was built for.** Deleting
the **highest-numbered** rule shrinks `max()` with it, so no gap ever opens — reproduced
by deleting rule 21 and getting a clean pass. My own probe had planted in the middle of
the list, which is the shape the author imagines. The mark now comes from the file
(`Numbers issued so far: N`, the one number this file states about itself), and the log
match is anchored to each line's leading number, because a bare digit anywhere in the
body — *"subsumed by 9"* — masked a genuine deletion of rule 9.

The disclosure was also wrong before it was right: one write-up covers two rules
(*"4 and 5 · Probes"*), so it printed 18 where the file has 19 write-ups covering 20
rules. It now says **rules with an incident**, because a label that does not say what
it counts is a number nobody can check.

**Swept the same class one level out.** The cold-retirement guard's corpus was a
hand-written list of seven files. Made **discovered** instead — any shipped surface that
states the condition must state both units — and it immediately found **thirteen**,
including `README.md`, the Cursor rule, `gates.md` and `learned.md` itself. A narration
of the old wording is exempt by the repository's existing convention: a double-quoted
span is a citation, and rule 21's incident is left as it happened.

**The class turned out to be the module.** Three guards in this file held
hand-written corpora; all three had missed a shipped surface, and each miss was found
by a reader or by a sweep rather than by the guard. All three are now **discovered**:
the cold trigger (7 listed → 13 found), the disclosure verdicts (5 listed → README's
worked `GATE 10` block found), and the claim registry (widened in v1.29.0 after the
same shape). *Nobody notices a corpus that is too small, because everything inside it
passes.*

**A high-water mark the same change can lower is not one.** A reader found the residual
hole and named why a file-only validator cannot see it: the evidence is in the previous
commit. Deleting rule 21 *and* editing the mark to 20 makes both numbers agree and no
gap opens. The check now reads the mark at `HEAD` through git — and where git cannot
answer, it **prints** the skip as an `unlooked` disclosure rather than going quiet,
because a check that falls silent outside a checkout reads exactly like a check that
passed. That assertion is a property, not a rejection, so it lives outside the negative
suite: the suite requires each of its tests to watch a guard *reject* something, and it
reported the mismatch itself.

**A citation naming two guards was checked as zero.** The extractor matched a single
backtick span followed by `)*`, so invariant 43 — the one this release added, naming
two — contributed nothing to the checked set and sat silently exempt from the invariant
that every citation must resolve. Found by a reader, on the invariant whose subject is
exactly that. Every literal inside a `*(guard: …)*` parenthetical is now checked, and
one branch that had shipped unprobed (a rule numbered above the mark) now has its plant.

The two discovered corpora also collapsed into one `_discover_md(skip, predicate)` —
second occurrence of the walk, and this file's own rule promotes a class at the second,
not the third.

**A check that only worked in the window its own test used.** The cross-commit
comparison read the mark at `HEAD` — identical to the working tree on a *committed*
checkout, which is what CI runs. It fired only in the local pre-commit window, and the
self-test exercised exactly that window. A reader committed the coordinated edit and
watched it pass. The mark is now compared against **every value this file's history has
held**, and the test commits its plant.

Two more from the same round: emptying the rules table wholesale made the list falsy and
skipped the entire check (`rules 0`, PASS), and `docs/superpowers/plans/` was missing
from the frozen-record exclusions its two siblings carry.

**CI caught what the local gate could not see.** Renaming the skip's message left the
property check grepping for the old string — and that step lives only in the workflow,
because it asserts something *is printed* rather than watching a guard reject. The local
runner had no way to run it, so `npm run test:all` was green while CI failed on a string
this same change had renamed. `test/negatives.py` now runs property checks too: a step
that exists only in CI is a step the author's gate is blind to.

**Both directions, on the guard about both directions.** The check found gaps the log
did not name, and never the reverse: a number *listed as retired* whose row is still in
the table — the log naming the wrong rule, or a retired rule quietly back. A gap has one
side and so does a resurrection; only the second pass sees it. This is `learned.md`'s own
rule 2 applied to the guard that guards `learned.md`.

**And the number the exclusion moved.** Adding `docs/superpowers/plans/` to the frozen
records took the discovered corpus from fourteen to thirteen, and two documents kept the
old number — so the corpus's own size is now a claim-registry class, computed from the
walk. The registry's evaluation moved below the walks that feed it: declared early,
computed late.

The local runner also learned to treat property checks as their own category — selected
by `-k`, shown by `--list`, and reported under their own heading rather than as *"the
validator accepted a planted defect"*, which is false for a check that plants nothing.
Its verdict now names what ran: `PASS: all 0 guards` over an empty selection is the
refused measurement this repository has a rule about.

**A probe that could no longer fail for its own reason.** The anchor test planted a log
line whose *body* held the digit it was about — and the high-water mark lives in that
same section, so a bare-digit scan picked up `21`, tripped a different check, and the
test failed either way. It could not tell a working anchor from a regressed one, which a
reader demonstrated by reverting the anchor. The mark is now stripped before the log is
parsed (it was never a log entry), the plant uses a number that is not a live row, and
reverting the anchor makes the test pass again — which is what "this test measures that"
means.

Two more of the same family: the rule-row regex existed twice, byte-identical, one for
the registry and one for the disclosure — rule 8's class inside the file that enforces
it, now one pattern with two readers. And property checks got the floor the negative
suite has had for releases: rename the only one and the category empties in silence,
which is the failure property checks were added to close, one level up.

Guards: 144 → **156**, plus 1 property check now covered locally.

## v1.29.0 — a sixth axis, and three summaries that each read as complete

**Re-derivation** joins the rotation axes in `references/audit.md`: take a number the
audit already produced and produce it again with a command of a **different shape**,
then print both. Not a second opinion — a second route. Re-running the same command is
a spell-check of the first run; only a differently-shaped question can come back
disagreeing. The exit criterion is **the pair printed**, never "verified", never
"matches": a re-derivation reported as agreement is a claim about a measurement nobody
can see.

It earns its place from this repository's own record. Four applications, two of which
refuted something already written down as fact: the version invariant called *four-way*
over five surfaces (`CONTRIBUTING.md:74`), and a graph shrink read as legitimate
tightening at 864→839 and as erosion at 839→798 — **same procedure, opposite answers**,
which is the whole argument for the axis in one line.

**The enumeration had already drifted, and nothing could see it.** Measured before
writing a word of doctrine: `audit.md` defined five axes, the Cursor rule summarised
four, `README.md` three. Each reads as complete on its own, because a list of three
orthogonal things is a convincing list of three orthogonal things. The Cursor rule now
carries all six (it is self-contained by contract and cannot point anywhere); README
stops enumerating and names the file that defines them — deleting a restatement is how
every count this repository got wrong has been fixed.

A guard now derives the axis keys from `audit.md` **at check time** and requires any
paragraph naming three or more of them to name all of them. Its first run accused
`stages.md` of enumerating three axes whose three hits were 595 lines apart and meant
different things; scoped to the file, the predicate was measuring vocabulary rather
than enumeration. The unit is the paragraph, and the guard says so in its own comment.

**Found by the false positive:** `gates.md` was titled *the two axes* over a file with
Axis A, B and C, and four surfaces repeated the two. README's prose named two and never
mentioned degrees of freedom at all — the axis about how much latitude an instruction
leaves, which is the one that gets skipped. All five sites corrected, and the count is
now computed from the `## Axis` headings by a claim-registry class, alongside a second
class for the rotation axes. The two are separated by the qualifier, because *axes* is
polysemous in this corpus and a guard that conflates them reports drift that is not
there.

**Review round.** Four findings, none from the probes. The guard re-read thirty
surfaces already cached; the flattening idiom had been hand-rolled three times, each
commenting on the earlier ones, and is now `_flatten()`; the spec claimed a guard that
did not exist. And the Cursor rule's **own** Gates section still said *"two axes"* with
no Axis C — introduced by this PR, fifty lines below an edit it made. Nothing could see
it: the claim registry's corpus held neither the Cursor rule nor the command file.
Both are in it now, and the count moved 6 → 7 the moment they were.

A second round found the same I/O class at two more call sites. Re-deriving its size
with a differently-shaped command — an instrumented run rather than a grep of the
source — put it at **25 reads of `audit.md` and 668 `.md` opens per run**, against an
estimate of "3+". The two named sites are fixed; the rest is carry-over row 12 with the
number attached, because a class measured and then left unmentioned is the TODO this
repository refuses to keep.

A third round found the sibling of the idiom the second round found — the
paragraph-split, hand-rolled at four sites — now `_paragraphs()`, whose docstring says
what the unit costs. And it found that the new **rotation axes** claim class was
permanently dormant and had **never been watched failing**: dormant is green by design
here, which is exactly why a dormant class still needs its plant. It has one now.

Guards: 136 → **144**.

## v1.28.0

### Eight ways to say "I don't know", and no way to count them

This bundle has eight vocabularies for declining to claim — `partial`, `unknown`,
`cannot verify from diff`, `review`, `dormant`, `skip`, `recalled`, `ungated` — spread
across sixteen reference files. Only one of them, `unknown`, blocks anything. **None of
them appeared beside a verdict**, and `grep` for a counter returned zero.

So `PASS` read as *verified*. It never read as *"green, and here is what nobody claimed
and what nothing looked at"*, which is the only thing a gate can honestly mean.

**The obvious fix is a ratchet, and it is wrong.** A ratchet may only shrink. A count of
abstentions under that rule puts pressure on exactly one thing: **claiming more**. A run
that reaches `abstained: 0` is not more careful — it has stopped saying *I don't know*,
which is the cheapest way to make the number fall. Refusals and wrong answers are
communicating vessels; squeeze one column and it reappears in the other, silently, because
a wrong claim looks like a claim.

`gates.md` therefore gains a second kind of counted set — a **disclosure**. Printed beside
the verdict exactly like a ratchet, and carrying the opposite rule: **no floor, no
direction, and never a target.** A target on an abstention count is an instruction to guess.

Two of them, kept apart because they are different facts:

| | Counts | How to read it |
|---|---|---|
| `abstained` | claims the run **declined to make** — `partial`, `unknown`, `cannot verify from diff` | a **choice**. Rising can mean the work got harder or the run got honest |
| `unlooked` | checks that **did not look** — `dormant`, `skip` | a **state of the corpus**, not a decision; it falls as the project grows the inputs |

`recalled` and `ungated` are deliberately not counted: the first is a property of one claim
and already lives in the ledger, the second a property of the whole run and said once in
words. Collapsing all eight into one number would be the false precision this change exists
to avoid — a figure nobody can act on.

Both print beside every worked verdict in the doctrine, both are required by the stage-6 and
stage-10 gates, and a guard holds the four verdict formats together — one statement on four
surfaces is this repository's most recurrent defect.

**Where this came from.** The programme that produced it started from a review of the
hallucination-mitigation literature, whose one directly importable idea was that
*uncertain refusals* belong in the results table **next to** factual errors, because the two
trade off. Everything else in that literature the doctrine already had. This is the import.

## v1.27.0

### A retirement trigger whose counter only some work moves

A standing instruction retires when it has not fired **in the last five run stamps**. A run
stamp is written by a run *of this pipeline*. Those two facts are fine apart and defective
together: where a project ships some of its work another way, the counter stops while the
work does not, so "the last five stamps" spans an arbitrary amount of change.

Measured on this repository: **ten consecutive releases, `v1.16.0` through `v1.23.0`, carry
no stamp at all** — four of the last fourteen tags moved the counter. Across that stretch the
trigger was not strict and not lenient. It was **unreadable**, and a list capped at ten whose
retirement condition cannot be read fills up and stops being pruned. That is the whole failure
mode: not a wrong answer, an absent one.

**The condition now carries a second unit — sixty days — and it is not belt-and-braces.** The
stamp count is the better signal while the pipeline is in use; the calendar is the one that
still works when it is not, which is precisely the state in which a stale rule does the most
damage. Both units are stated on every surface that states the condition, and a guard holds
them together: correcting the rule where somebody was looking and leaving it everywhere else
is the class `v1.24.0` shipped a guard for.

Entry **rotation** — *entries older than five stamps move to the archive* — is a different
mechanism and is deliberately out of scope, said in the guard's own comment so the exclusion
is a decision rather than an oversight.

### The ten releases are recorded, not stamped

`docs/superpowers/retro.md` now carries the gap as a section, with the command that produces
it. **No stamps were written for those ten releases.** A stamp asserts that a run happened and
that its gates were walked; writing ten to make the table continuous would be the exact defect
this file exists to catch, committed in the file that catches it.

Two consequences are stated there rather than left to be rediscovered: the cold trigger was
unreadable across that stretch, and the lessons of those releases live in `CHANGELOG.md` and
nowhere the next run's stage 0 looks — which is why rules 17–21 of `learned.md` sat outside
the *Where these bind* map until `v1.23.1` found them.

**A correction to this program's own ledger, made at the moment of use.** Its first row said
*"seven releases (v1.17.0–v1.23.0)"*. Re-measured before being acted on: **ten**, reaching
back to `v1.16.0`. The original was a filtered subset that had lost its filter — `learned.md`
rule 16, in the ledger of the run that ships rule 16's neighbours.

## v1.26.0

### A green suite is not a rendered page

Stages 5–6 verified a web front end by **reading the diff**. Nothing in the flow ever
opened it. That is not a gap in the tests — a suite proves the code does what its
assertions say, and it cannot see a component that renders correctly and lands under a
fixed header, a request that 404s while every unit test mocks it, or a console error that
costs nothing at test time. Stage 8 had the same shape one level out: a health check
proves the server answered, and a `200` says nothing about a bundle that never loaded.

`audit.md` already names this seam — `L6→L7`, *is there an executed observable a user
reaches* — and no stage owned it. A grep over `stages.md` and `tdd.md` for *rendered*,
*browser*, *screenshot* returned nothing at all before this change.

**`chrome-devtools` is now a recommended companion**, wired where it pays:

- **stages 5–6** — load the surface, snapshot it, and read the console and the network log
  before calling it green;
- **stage 8** — open the deployed page rather than curling it.

**Absent, the run says so in those words.** *"Verified by reading the diff"* is a weaker
claim than *"the page rendered"*, and the close-out records it as the weaker one instead of
letting a passing suite stand in for a surface nobody looked at. It is never a gate.

**The boundary is load-bearing and is written down.** A CLI, a library or a backend
service is never offered a browser. Offering one to a project with no browser is the
fastest way to teach an agent that the recommendation is noise — the same reasoning the
false-positive budget applies to gates.

### The list that existed twice and was never compared

Adding the companion surfaced something older: `companion-skills.md` states the
optional-companion list **twice** — as a table a reader consults, and as the block the
agent prints before stage 0 — and nothing compared them. A companion in the table and
missing from the block is a recommendation the operator is never offered; the reverse is
an install line for something the table does not explain. **Both copies are used**, which
is what makes it `learned.md` rule 20 rather than a style preference.

`chrome-devtools` would have been the first to drift. There is now a guard, probed both
ways, and invariant 36.

**One thing this release did not need, against expectation.** The reconnaissance said the
skill's `description` had nine free characters of 1024 and that adding a companion would
force a displacement — a real cost, since the description is the only thing a router reads.
Checking the analogy first showed the premise was wrong: `graphify`, `wiki-update`,
`context7` and `agent-sync` are **not** in the description either. Only `super-ux` is, and
only because it is a conditional *requirement* that blocks a gate. A companion is declared
in `companion-skills.md` and the stage gates. No displacement, because the change never
belonged to that surface.

## v1.25.0

### One check over one number, made into a registry over the class

The "compute, never restate" guard has existed since v1.5.0 and covered exactly one
number: the count of negative self-tests, added because two living documents claimed 46
after the suite reached 50. It stayed one check while the same class went stale in five
more places, each fixed as an instance and none of them gating the shape:

- `README.md` and `SKILL.md` described `learned.md` as *"fifteen rules"* against a table
  of twenty-one;
- `evals/RESULTS.md` ratcheted zero dated runs directly above a dated run, and directly
  on top of `evals/run.py`, which computes one and had been printing it for five releases;
- `docs/DOCMAP.md` claimed two standing instructions against the retro's four;
- the version invariant was **named** *four-way* on four surfaces while `test/validate.py`
  enforced five;
- `SKILL-CARD.md` counted "the 26 files under `references/`" against a directory of 28.

`audit.md` says a class seen twice belongs in a script. Six instances later, the file that
enforces that rule had not applied it to itself.

**The check is now a registry.** One row per claim class, each naming the pattern that
recognises the claim in prose, the command that computes the truth, and the incident that
earned the row. Adding a class costs one line instead of one more bespoke block nobody
generalises.

Two limits are stated rather than implied, because both were learned the hard way this
release:

- **A quoted number is a citation, not a claim.** `evals/RESULTS.md` narrates its own
  stale `"Dated runs recorded 0"` while explaining the incident, and the first version of
  the registry rejected it. The exemption is a quoted span — deterministic, with no marker
  vocabulary to grow per incident, which is the same drift this release is about.
- **A count of an enumeration inside one sentence is not computable from outside it.**
  `CLAUDE.md` said *"the stage list lives on nine surfaces"* above a list of ten. There is
  no command that can check that, so it is **deleted** rather than gated, and the line now
  says why.

**Numbers are read as digits and as words.** The incident that named the second row was a
word — `README.md` said *"fifteen rules"*, not *"15 rules"* — so a digit-only registry could
not have caught the defect it is named after. Adding word forms immediately found **four
live claims** the patterns had been skipping in silence: *"the ten canons"*, on four
surfaces. All four are correct, and none of them was being checked.

That correction matters more than the fix, because the first draft of this entry claimed
every dormant class was dormant *because the number had been deleted*. For the canons class
that was simply untrue: it was dormant because the check could not see the form the claim
was written in. **A dormant state is a claim about the corpus, and it needs the same
evidence as any other** — this one was plausible, unverified, and wrong.

**Every class reports `ok` or `dormant` beside the verdict.** Four of six are dormant now,
and that is measured rather than assumed: v1.23.1 and v1.24.0 deleted those numbers rather
than correcting them, which git history confirms. A registry reporting green over classes
it never looked at would be precisely the false success it exists to catch. It is a ratchet
against re-introduction more than a finder of present drift, and the verdict line says so
every run.

One false positive was measured and removed before shipping: `CONTRIBUTING.md` narrates
that its invariant list *"was eight guards behind"*, which is a **lag**, not a count of the
suite. The pattern excludes it explicitly rather than tolerating a noisy check — a gate that
cries wolf is switched off by the third person who hits it.

## v1.24.0

### A rule that reached one file, and the guard shape that let it

`v1.23.0` added rule 21 — *a step that consumes what a later step produces is a deadlock*
— and reordered the retrospective's three acts to **stamp → prune → entry**. It changed
`references/retrospective.md`. It changed nothing else.

Every other surface still taught the deadlocked *prune first* — the list is the count,
and it was written down rather than tallied, because a tally of this fix would be the
defect the fix is about: `SKILL.md` twice (including
the stage-10 gate row), `references/acceptance.md` three times, `references/stages.md`
three times, `references/companion-skills.md`, `references/knowledge-sources.md`,
`templates/retro.md`, `templates/README.md`, `commands/task-pipeline.md`,
`cursor/rules/task-pipeline.mdc`, `docs/DOCMAP.md`, `README.md` and this repository's own
`CLAUDE.md`. **`SKILL.md` is what an agent loads first**, so the most-read surface of the
shipped skill instructed the exact failure its newest rule defines.

**Why every existing guard was green.** Rules 16–21 each have a bespoke check that names
its consumer files and asserts a needle is present. That answers *"did a consumer drop its
citation?"* — a real failure, and it catches it. It cannot answer *"does a consumer
contradict what it cites?"*, because a contradicting consumer **keeps** its citation: the
link resolves, the section exists, the needle is there. A pointer's validity says nothing
about whether the two texts agree.

**The new guard compares order, not presence** — and derives the expected order from
`retrospective.md`'s own heading **at check time**, so it cannot drift from the doctrine it
guards the way a hardcoded literal would.

Four deterministic shapes, each arrived at by probing rather than by trusting a green:

- an adjacent enumeration (`prune, stamp` / `prune → stamp`);
- the `first … then` construction, with an aside allowed between;
- a bare `… then …` sequence with no "first" at all (`prune before you add … then stamp`);
- an **ordered list** whose items open with the acts — which needs no connector word, and
  which the first two shapes both missed.

Each of the four was found by running the check and reading the result, not by writing it
and shipping. Two of them were blind spots in the guard's *own* first version, and one of
those was blind to the exact wording this release introduced.

**Measured before shipping** (rule 10). The obvious predicate — *both act words in one
paragraph* — returns 32 hits on this corpus, of which 22 are false, including
`retrospective.md`'s own correct prose. The shipped predicate returns 8, all true. A
paragraph narrating the old order as a defect is exempt through an explicit marker list;
`learned.md`'s rule-21 incident and `retrospective.md`'s own rationale both need it.

Swept in the same change, because the class is *a claim that stopped being true*:
`SKILL-CARD.md` still said the eval suite was **"Never executed"** and counted "the 26
files under `references/`" against a directory holding 28.

## v1.23.1

### Four documents that had gone false, and the config this repository never wrote

A review of the hallucination-mitigation literature against this skill produced an
uncomfortable result: the doctrine already covers almost every applicable mitigation the
field names — grounding, constrained generation, post-processing that blocks unproven
assertions, self-contradiction detection. What it does not cover is **this repository
applying that doctrine to itself.** Everything below is a class the skill documents,
found in the skill.

**Four surfaces were stating numbers that had stopped being true.**

- `README.md` and `SKILL.md` said `learned.md` carries *"fifteen rules"*. The table has
  twenty-one. Both now describe the file without counting it — the table is the count,
  the same fix `CLAUDE.md` already applies to the invariant list, and the reason is that
  a hand-written count goes stale on the next rule rather than on the next audit.
- `evals/RESULTS.md` opened with *"the suite is authored and has not been executed"* and
  ratcheted *"Dated runs recorded 0"* — directly above a dated run, and directly on top
  of `evals/run.py`, which computes `recorded runs: 1` and had been printing it for five
  releases. The document and the tool beneath it disagreed, and nothing compared them.
  The ratchet now carries what actually matters: one run, **self-observed**, and **zero
  blind** — because collapsing those into a single total is how a self-check gets quoted
  as a result.
- `docs/DOCMAP.md` claimed two standing instructions against the retro's four, and
  duplicated both eval numbers. Its ratchet table now names **homes and commands, never
  values**. A ratchet copied into a second document is two ratchets, and the copy nobody
  runs is the one people read.

**`learned.md`'s own routing table stopped at rule 16.** Rules 17–21 were in the rule
table, each guarded in its consumer files, and absent from *Where these bind in the
pipeline* — the section an agent reads to learn *when* a rule applies. The rule's own
failure mode, applied to the map of the rules. All twenty-one now name their stage, and
the two mis-aimed citations that first attempt introduced were caught by the citation
guard rather than by a reader, which is the guard doing exactly its job.

**This repository had no `pipeline.json`.** The project that ships the config contract
had never written its own, so `run.loop` was unrecorded, the mode defaulted to off, and
every loop it ran was authorised in a chat message. There is now a real one: this repo's
eleven stages with its real host commands, its release block, and the loop mode recorded
as a file rather than remembered — including the note that the mode collapses
discretionary check-ins only, and is never the authorization for the tag push.

**Not fixed here, and named rather than quietly carried:** rule 21 changed the retro's
order to *stamp first* in `references/retrospective.md` and in no other file. Eight
sibling surfaces — `SKILL.md` included, which is what an agent loads first — still teach
the deadlocked *prune first*. That is a gate contract, so it ships on its own branch with
a guard that compares the class rather than one literal.

## v1.23.0

### A step that consumes what a later step produces is a deadlock — `learned.md` rule 21

The retrospective stage said **prune first, then stamp**. One of the prune's three retirement
triggers is *it has not fired in the last five run stamps* — so the trigger read a counter the same
stage wrote afterwards. On any list it had never run on real data, and it stays unreadable for
exactly as long as nobody stamps.

Measured on a real project: last entry five days old; stamps per day 33, 20, 26, **3, 0** — the zero
on a day with 107 commits — and the list sitting at **10 of 10**. Every run arrived at a stage that
opened with a full list, an unusable trigger and a mandatory deletion. It was not skipped out of
laziness: its first step could not be performed, and the cheap step that would have made it
performable was queued behind it.

Two changes, and the second only works because of the first:

- **Stamp first, then prune, then write.** The stamp is one line and costs nothing; it is also the
  only thing that makes the cold trigger computable.
- **Each trigger is a command, not a judgement.** All three are now runnable — grep for the rule's
  words in anything that executes, resolve every path and tool it names, count its firings across
  the last five stamps. A retirement condition nobody can run is one nobody applies, which is how a
  list reaches ten and stops being read.

`test/validate.py` guards all three: the new ordering, the absence of the old "runs BEFORE" wording,
and the triggers being expressed as commands. Watched failing against two planted defects.

## v1.22.0

### When a thing exists twice, ask which one is used — `learned.md` rule 20

A service had **two Dockerfiles**. One was added at the repository root by a run that checked for a
Dockerfile by looking where it expected one; `docker/Dockerfile` had been there all along, and
`.github/workflows/ci.yml` says `file: docker/Dockerfile`. They disagreed about the port — 8080 at
the root, 8000 in `docker/` — and the disagreement surfaced two days later as a **deployed service
that answered nothing**, while `docker ps` said `Up` and `systemctl` said `active`. The built one
also ran as root and copied the whole context including `.git`; the hardened one was the one nobody
built.

Diffing the two files finds the difference and not the **direction**, and the direction is the whole
finding. Only the consumer says which one ships, and it is one grep.

Its second shape: **a rule written in two documents is two rules.** This skill's own autonomy sweep
lives in `grill.md` (what the grill ASKS) and `templates/brief.md` (what the brief RECORDS), and in
the two releases before this one a row was added to one and not the other — twice — each time caught
by a validator that knew to look at both.

- `references/learned.md` — rule 20 and incident 20.
- `references/audit.md` — "Two copies, and which one wins", including why the copy that ships is
  usually the one nobody hardened.
- `references/grill.md` + `templates/brief.md` — sweep row `0 Duplicates`: the consumer line, quoted.
- `test/validate.py` — a guard, watched failing against three planted defects, the third being the
  sweep row present in one file and not the other.

## v1.21.0

### An empty measurement is a refused measurement — `learned.md` rule 19

Rule 11 says a gate's exit code is part of its output. This is the other half, and in practice the
louder one: **a command that never ran exits `0` and prints nothing**, and satisfies a run that
checks neither.

Three sightings in one session, one shape. A `docker run` without `-i` does not attach stdin, so a
heredoc carrying `ALTER ROLE` stopped at the docker CLI — `psql` read an empty script, did nothing,
exited `0`, and the step printed "password set". A `grep` pattern written against the wrong output
format matched nothing, so three consecutive planted-defect runs printed empty strings that read as
passes. A migration step printed no lines, which looked like a step that had not run and was in fact
a step that had. Every time, the instrument failed and the failure was indistinguishable from
success, because both produce nothing.

- `references/learned.md` — rule 19 and incident 19.
- `references/audit.md` — "Silence is not a reading": non-empty, shaped as expected, and quote the
  output rather than the conclusion drawn from it.
- `references/review.md` — the same bar before a finding is closed.
- `test/validate.py` — a guard, watched failing against two planted defects, asserted on both the
  exit code and the presence of the expected line.

## v1.20.0

### State that accumulates locally is created from nothing everywhere else — `learned.md` rule 18

The retro says this class has recurred longer than any other: three sightings across forty entries
before 2026-08-07, and four more that day alone. Its worst instance: a CI job that started an empty
database, created the runtime role, and ran the suite — with nothing between those steps applying
the schema. **1039 failed, 1339 errors, 4704 × `UndefinedTable`**, every suite touching a table, for
as long as the repository had real tests. Invisible locally by construction: the compose database is
migrated once by hand and stays migrated, so every author has a schema and the runner has none.

Local state is *cumulative*; CI state is *constructed*. A green obtained on the cumulative one
carries an unstated premise, false in the only environment that matters.

- `references/learned.md` — rule 18 and incident 18.
- `references/tdd.md` — "The green from residue": run the suite once against a freshly created
  instance, and name it in the report. "Green" and "green against a database created ten seconds
  ago" are different claims; only the second predicts CI.
- `references/grill.md` + `templates/brief.md` — sweep row `0 Fixtures`: what persists between runs
  here, and the command that recreates it from nothing.
- `test/validate.py` — a guard, watched failing against two planted defects.

## v1.19.0

### The copy you are about to edit may not be the copy that ships — `learned.md` rule 17

A machine keeps a skill twice: the working copy it publishes from and the installed plugin it runs.
On 2026-08-07 the working copy was **two commits behind its own origin** — `v1.16.2` against
`v1.18.0` — and the newer commits carried rule 16 itself. The tree was clean and nothing had
diverged; the copy had simply never been pulled. An edit there would have landed on 1.16.2 and the
release would have **deleted rule 16 and two versions of work by fast-forward** — not as a conflict
git would show, but silently. The project's own instruction names that directory as the source, so
whoever did it would have been following the documentation.

The check is one command and it runs **before the first edit**:

```bash
git fetch -q && git rev-list --count HEAD..@{u}     # 0, or stop and pull
```

- `references/learned.md` — rule 17 and incident 17.
- `references/knowledge-sources.md` — a harvest section, because this is a property of the sources
  that reading them cannot reveal.
- `references/grill.md` + `templates/brief.md` — autonomy-sweep row `0 Source`, in both files: the
  grill asks it, the brief records it, and a topic in only one is a question with nowhere to land.
- `test/validate.py` — a guard in the shape of rule 16's, so dropping a citation fails the build
  rather than quietly ending the coverage. Both halves were watched failing against planted defects.

## v1.18.0 — 2026-08-06

### Added
- **`references/deploy-targets.md`** — stages 7 and 8 knew what a deploy must
  satisfy and never said what to run. This carries the runbook template, the
  per-platform verbs (Heroku, DO App Platform, droplet over SSH, CI-as-deploy,
  and the quick table for Fly/Vercel/Cloudflare), and the verification trio.

### Changed
- **Stage 7: a missing runbook is now the stage's first deliverable**, not a
  reason to improvise. A deploy performed from an agent's inference about the
  project is one nobody can repeat or roll back, and the operator is already
  standing at that manual gate — the questions cost two minutes there and cannot
  be reconstructed during an incident.
- **Stage 8 names all three verifications, and says to check the deploy job**,
  not only the build. A green build beside a skipped or failed deploy is the
  commonest way a run reports success while nothing shipped — previously the
  stage said "confirm clean boot" and left the shape of the confirmation open.

### Notes
- Ported from a standalone `deploy` skill that lived only in a Cursor skills
  directory. The pipeline already owned the gates; what it lacked was the
  concrete verbs behind them, so the skill folded in rather than shipping beside.

## v1.17.0 — 2026-08-06

**A carried-in claim is a recollection — `learned.md` rule 16, and the four places
it binds.**

A long autonomous run advanced one roadmap row per iteration and was correct every
time: gates green, defects planted and watched to fail, docs closed in the same
change. What was wrong was the sentence between the iterations — *"the remaining
rows are these"* — taken from a list that had reached the context through a
compaction, had once been a filtered subset, and had lost its provenance on the
way. Eleven iterations later one command over the register printed **36 open rows
out of 99**. Nothing had failed, because nothing compares a run's belief about the
work-list against the register: the claim only ever existed in prose.

The same class had already bitten that project twice from the other side, and its
own roadmap names the property — seven rows reading `blocked` on producers the
dependency board recorded as delivered, *"no gate can catch it because it breaks
nothing, it only removes work from consideration"*. **Stale state does not throw.**
It narrows what gets considered, and every downstream gate then passes honestly on
the smaller world.

Rule 8 was the neighbour and not the same rule: it governs a number *inside a
document*, checked when that document is. Rule 16 governs a fact that crossed a
**session boundary** and is being reported as current — where there is no document
to check, only a memory that reads like one.

What changed:

- **`references/learned.md`** — rule 16 with its incident, and two binding rows:
  stage 0 harvest, and stage 10 plus every loop iteration.
- **`references/knowledge-sources.md`** — a new source (the task register, read for
  its *state*, with a command) and a new section, *Carried-in claims — measured or
  recalled*. Every inherited claim starts `recalled`; before it is acted on **or
  reported to the operator** it is re-derived and marked `measured`, or it is not
  stated. Three claims go stale most reliably and all three are cheap: the
  work-list, `green`, and a blocker or premise.
- **`references/continuity.md`** — in loop mode the harvest's documents may be
  carried between iterations; the work-list line may not, because the previous
  iteration is what invalidated it. And *"next up is X"* in a closing report is a
  claim about the board — the one sentence in the cycle no gate reads.
- **`references/audit.md`** — a third exit criterion at stage 10: the work-list is
  re-measured and **printed beside the count the run opened with**. A pair of
  numbers that has to agree cannot be filled in without looking, which is what
  keeps the measurement load-bearing instead of ceremonial.
- **`references/grill.md`** + **`templates/brief.md`** — one autonomy-sweep row:
  which register holds task state, and the command that reads it. Settled once; a
  project without one records it empty and the rule costs nothing.
- **Guard + negative self-test** — the rule's own failure mode applied to itself:
  doctrine carried in one file reads like doctrine in force. The validator names
  each consumer, so a file that drops its citation fails rather than silently
  ending the coverage. Guard count 119 → 120.


## v1.16.2 — 2026-08-06

### Added — a CI run is checked by reading it, not by assuming it

The bundle offered a place (`conventions.md`: *"CI: the workflow run."*) and a claim
(`release.verify`: *"CI green on the tagged commit"*) with no method between them.
Both are satisfiable by believing them, which is the class `gates.md` named in
v1.14.0: **an actor's own reply is not evidence about the world**, and the test —
*what does it print when it did not look?*

The occasion was v1.15.0's own release. `validate` was `completed/failure` on a push
to `main` and on the release tag. The failure was **correct**: the repository's own
*Every v\* tag must be contained in main* guard, firing on a tag that was not yet an
ancestor — precisely the defect v1.6.1 built it for. The guard worked, and **nothing
obliged anyone to read it**. A guard nobody reads is a fail-open hook with extra
steps; it surfaced only because the run happened to poll the API.

- **`conventions.md` gains *The CI verdict***: the commands (`gh run list … --json
  databaseId,name,status,conclusion,headSha`, then `gh run view … --log-failed`), an
  **unauthenticated fallback** on the `check-runs` API, and **three states** —
  concluded, in progress (*"it was still running when I looked"* is a report, not a
  verdict), and **no run found**, said out loud, because a project without CI is a
  legitimate state and not a green one.
- **Read the log, not just the verdict.** A conclusion says *that* it failed; only the
  log said *what* — the guard's name, the orphan tag and the one-line fix. A bare "CI
  failed" hands the next reader a search the log had already finished.
- **Two paths because one credential died.** `gh`'s token expired mid-run that night,
  and `gh auth status` reported it invalid from a **cached** verdict while `gh api
  user` succeeded. The doctrine names the live call, never the status command.
- **Bound at stages 7, 8 and 9** — every stage of this flow that pushes. The incident
  hit at the merge and again at the docs push; binding stage 8 alone would have caught
  neither. The gates cite `conventions.md`; a guard rejects a second copy of the
  commands.
- **It reports, it does not block** — the shape stage 8 already used for deploy logs.
  Blocking would make a project *without* CI cheaper to ship from than one with it.

### Fixed — the negatives floor may no longer lag its own workflow

`MIN_EXPECTED` is a number in a living document, so rule 8 binds it: it must **equal**
the workflow's count, not merely sit below it. Its own comment records the first lag
(20 while the workflow carried 34); v1.15.0 was the second — four canon self-tests
landed and the floor stayed at 104 while the file carried 108. A floor below the count
cannot notice losing the difference, which is the entire job. Now guarded, and the
guard was watched rejecting a lowered floor.


## v1.16.1 — 2026-08-06

### Fixed — frontmatter that a regex called valid and a YAML parser silently dropped

`evidence-docs`'s description contained *"read as true: a decision record"*. A
colon-space inside a plain YAML scalar makes the value a nested mapping, so the official
plugin validator reported the skill **loads with empty metadata — every frontmatter field
silently dropped**, which for a skill means it never triggers. v1.16.0 published in that
state.

The guard that was supposed to catch it checked the frontmatter with a regular
expression and passed: a check proving less than it claims, shipped in the release that
publishes canon 6. It now rejects a plain scalar carrying a colon-space, across **every**
`SKILL.md` in the plugin rather than only the new one — the class, not the instance.
Guards 112 → 113.

## v1.16.0 — 2026-08-06

### Added — `evidence-docs`: a second skill in this plugin, and the router row it fills

The canons landed in v1.15.0 with no way to reach them except through the pipeline. The
global router already reserved a name for the question *"what is this proved by?"* —
`evidence-docs` — and nothing resolved it. A routed name that resolves to nothing is the
shape `learned.md` rule 14 forbids, in the routing table itself.

`skills/evidence-docs/SKILL.md` is a **navigator, not a second copy**: the ten canons as
a one-line index, a pointer to their one home in `documentation.md` → *The canons*, and a
table of where to go next — set docs up from nothing, record a decision, avoid orphaning
docs on a change, build a check that cannot lie, trust a mechanism that reports success,
audit docs a project already has, seed a gate. It states its own boundary ("it will be
read as true"), what is explicitly out (drafts, chat, commit messages, code comments) and
its refusal phrase.

Shipping it as a second skill **in the same plugin** rather than a separate repository is
what keeps SSOT: one set of files, one release, and no copy to drift. `super-ux` already
ships six skills from one plugin, so the shape is the family's own.

### Guards — 108 → 112

The index is held to the doctrine's own canon list, the pointer to the one home is
required, the frontmatter is checked against the Agent Skills spec, and every relative
link is resolved **from the navigator's own directory** — it sits one level over from
everything it names, which is canon 4 enforced in the file that publishes canon 4.

## v1.15.0 — 2026-08-06

### Added — the ten canons: what makes a document evidence

The doctrine carried the mechanisms and never stated the standard they serve.
`references/documentation.md` now opens with ten laws — a claim carries its address,
numbers are computed rather than restated, one home per fact, a reference resolves from
where the document is *read*, green nobody watched turn red is not evidence, a check
proves its scope and nothing beyond it, silence is not a pass, an estimate is never
announced as a measurement, what was not checked is printed beside what was, and the
document ships in the change that made it true.

Each canon **names where it is enforced** instead of restating the mechanism, and the
boundary against `learned.md` is written down: the canons are epistemic (what makes a
claim documentation), `learned.md` is operational (what to do at a trigger). Two
undifferentiated rule lists would be the duplication canon 3 forbids.

Guarded four ways: the list exists, all ten laws are present, every canon names an
enforcement, and the boundary is stated. The enforcement check counts **per canon**
rather than in total — a total threshold only fires once most of them are gone, which
is a check proving less than it claims, canon 6 applied to itself.

**Found while writing them, by this repository's own guard:** canon 9 cited
`audit.md → Ratchets`, a section that lives in `gates.md`. The file resolved and the
section did not — the shape a link checker cannot catch and a reader believes.

### Added — a build date is the graph's reply about itself, not a measurement of it

Stage 0 reads the code graph before it reads anything else, and until now it recorded
that graph's freshness as `built YYYY-MM-DD`. That is true, self-reported, and silent
about the only thing the harvest needs to know: whether the graph describes the tree
this run is about to change. Twelve commits later the row still reads `built
2026-08-05` — and still reads *fresh*, because a date with nothing subtracted from it
is a fact with no scale. It is the class `references/gates.md` named one release ago:
an actor's own reply, standing in for evidence about the world.

The occasion was this repository's own. `docs/superpowers/specs/` holds a brief, a
carry-over ledger and an acceptance document for v1.11.0, v1.12.0 and v1.13.0 — and
none for v1.14.0 or v1.14.1. Those two releases never opened stage 9, so nothing
refreshed the graph, and the next harvest would have read a two-release-old index
behind a date that looked current.

- **`references/knowledge-graph.md` gains *Measure the lag***: three commands
  (`git rev-parse --verify`, `git rev-list --count`, `git log -1 --format=%ct`) so
  the number comes from git rather than from judgement, and **three states** —
  `built_at_commit` exact, file `mtime` approximate, and `unresolvable` — because
  `graph.json` carries the commit stamp **only when the caller passed it** and
  `graphify update` from the CLI does not. With one state, "could not measure" would
  print like "fresh", which is the failure the section cites `gates.md` for. Zero is
  stated out loud for the same reason.
- **No threshold, deliberately.** `continuity.md` refused a context-budget number on
  the same grounds: an unmeasurable threshold becomes unconditional doctrine, not
  config. One commit that moved the function this task is about outweighs fifty that
  touched a README, so anything but `current` carries `⚠ not trusted for reach until
  refreshed` — a marker, not a block. The graph is recommended everywhere else in this
  bundle; a blocking staleness check would make *no graph* cheaper than a week-old one.
- **The cadence is untouched.** Stage 9 already required the refresh unconditionally,
  and an `always | major | manual` mode was rejected rather than deferred: `major`
  schedules exactly the state the doctrine warns about — a graph confidently wrong
  between releases, read first by the next run.

### Added — hygiene check 7: a blank line inside a table

A GFM table ends at the first blank line, so a blank line left mid-table silently
demotes every row below it to pipe-delimited prose. The file stays well-formed, every
row is still present, and a diff showing only added lines shows nothing wrong. It
happened **twice inside this run** — a carry-over ledger and the brief's decision
table — which is `audit.md`'s threshold for a mechanism rather than a third ledger
row. On its first armed pass the check found **three more** in the carry-over ledgers
of v1.12.0 and v1.13.0, which had been rendering broken since the day they were
written. All three are fixed rather than baselined behind a floor.

The check shipped with `HYGIENE_FLOOR_7` undeclared, so `judge()` compared against an
empty string and printed `ok: check 7 … 3 (floor )` over three real hits — the gate
reporting a pass it never computed, on the release about exactly that. An undeclared
floor is now a failure, not a zero, and the reason is written beside it.

### Guards — 95 → 104, by extending a sibling rather than copying it

`test/validate.py` already enforced that the code-graph doctrine be named in **both**
halves of stage 9 — the config gate the orchestrator verifies and the section an agent
reads — because a file that "reads as law while the run never does it" is an inert
gate. Standing instruction R-003 requires running a fixed defect's definition against
its siblings, and stage 0 is the sibling: same doctrine file, one duty reading the
graph where the other refreshes it. So the existing guard was **extended**, not
duplicated.

At stage 0 the word *graph* is not the test — it was already there. The guard requires
the **measured lag**, and three more checks keep the cited section honest: the commands
must survive, all three states must survive, and `templates/brief.md` may not ship the
superseded bare-date row to every project scaffolded from it.

The repository's own drift guard caught the release mid-flight **three times**:
`SKILL-CARD.md` and `evals/RESULTS.md` said *95*, then *100*, then *102*. Its message
has always offered two fixes — *derive the number or delete it* — and three
hand-corrections in one run is the answer to which one was right. **The prose no
longer states a count at all**; it names the command that prints one. The guard's own
negative self-test was rewritten in the same move: its plant used to edit the
restated number in place, so it broke the moment the number went away — a test
coupled to the defect it was written against rather than to the rule. It now
*introduces* a count into a document that has none, which is what the guard actually
forbids.

### Fixed — one marker, one spelling

The distrust marker this release introduces was written **four different ways inside
the release that introduced it**: the doctrine's own three-state table omitted it
entirely, its `unresolvable` row invented *"treat as stale until refreshed"*, and the
Cursor rule and the config both dropped the sigil. Review caught the first; standing
instruction R-003 — run a fixed defect's definition against its siblings — found the
other three. `audit.md` says a class seen twice becomes a mechanism rather than a
third ledger row, so a guard now requires the canonical string and rejects the second
spelling. Greppability is the marker's only property: a ledger row is prose, and the
marker is the one string a later reader can search for.

That guard shipped green for the wrong reason and was caught by probing it rather
than by reading it. It compared **per line**, and this doctrine wraps at ~80 columns —
so in `README.md` and `stages.md`, where the marker is split across two lines, it
matched nothing and reported a pass. It now normalises whitespace before counting.
Two releases running, the defect found inside the release was an instance of the
class the release was about.

## v1.14.1 — 2026-08-05

### Fixed — a guard below the verdict block is dead code shaped like a guard

The fourteen guards v1.14.0 added were first appended to the *end* of
`test/validate.py`, below `if errors: … sys.exit(1)`. On a clean run they executed
after `PASS` was printed; on a corrupted one `sys.exit()` fired first and they never
executed at all. Every one was green for the single reason that cannot be argued
with: it never ran. The negatives runner caught it because it requires positive
evidence (`OK:` in stdout) rather than a non-zero exit — this release's own subject,
committed by the release that names it.

A guard now reads the validator's own source and rejects any `fail(` after the
verdict. It shipped with the same defect it checks for — `find()` matched the literal
inside the guard's own body — and its negative self-test caught that within one run;
`rfind`, with the reason written beside it. Guards 94 → 95.

## v1.14.0 — 2026-08-05

### Added — false success: the failure mode that removes the reason to look

Every incident this repository has recorded of a mechanism reporting a win it never
checked was fixed as its own instance, because the class had no name to be swept by:
the hook that fails open (any exit code but `2` is non-blocking, so a **crashed**
guard *allows* the action), the cancel that accepted an id that was never scheduled
and returned success, the counter that asserted the new number was present instead of
the old one being gone — green for three releases while four surfaces printed the old
one — and R-002's batch of edits reporting done while one edit never applied.

- **`references/gates.md` gains the class**: the law (*an actor's own reply is not
  evidence about the world*), the five known shapes, the test that separates a checked
  pass from a silent one — *what does it print when it did not look?* — and two rules:
  verify by re-reading rather than by the reply, and assert the **absence of the old**
  rather than the presence of the new.
- **`references/audit.md` gains a fifth axis.** The four existing axes read for
  wrongness, which is exactly what a false success is not. The new axis asks where a
  mechanism can report a win it never checked.
- **The other files cite the class, never restate it.** `continuity.md`'s cancel rule
  became one named instance instead of a second definition.

### Added — effect verification: the diff cannot show what the task did

`v1.12.0` added a hygiene gate over what a task **wrote**. It is blind to what a task
**did** — a file moved, a job cancelled, a service restarted, a record migrated — and
the implementer's report is not evidence about any of it.

- **`references/build.md`**: the implementer contract now requires a `verified-by:`
  line for every step whose effect lives outside its own diff, carrying the command
  that *confirmed* the state rather than the one that caused it. The hygiene-gate
  section names its own blind side and tells the controller to read those lines back.
- **`references/review.md`**: a new rubric item — **Effect verification** — rated
  **Important**, not Minor. A finding that never blocks is a finding the fix loop
  never sees.

### Guards — 80 → 94

Fourteen new checks, each with a negative self-test whose plant asserts it landed
before the edit. Two invariants added to `CONTRIBUTING.md`, both citing a literal the
validator actually prints. The negatives floor moved 80 → 94.

**One defect found by this run's own discipline:** the first draft of these guards was
appended *below* the validator's verdict block, so on a clean run they executed after
`PASS` was printed and on a corrupted one they never executed at all — fourteen guards
that could not fail. The negatives runner caught it because it requires positive
evidence (`OK:` in stdout), not merely a non-zero exit. A runner that accepted silence
would have shipped the exact defect this release is about.

## v1.13.0 — 2026-08-05

### Added — the read-back: four rules that existed and were never handed over

Stages 3 and 4 produced documents stating things nobody verified: that a named
check exists, that the spec agrees with decisions already made, that the
self-review happened at all, and that the change still costs what it was worth.

Five defects, and **four of them are one shape.** The rule already lived in this
bundle, in a stage that never handed it to the stage which had to obey it. The
evidence-for-checks rule sits at stages 6 and 10; the rejected-alternatives rule
sits at stage 2; `learned.md` rule 14 has sat at stage 9 since v1.4.0. Stage 3
names checks, contradicts decisions and writes DoDs — and read none of them back.

So the fix is one mechanism applied four times. `spec.md`'s self-review now asks
whether every check it names is real, reads back the brief's `Decisions locked`
table **and** the alternatives stage 2 rejected, and prints the cost.
`planning.md` asks whether every command, path and file a DoD names resolves.
`learned.md`'s stage map binds rule 14 at 3 and 4, not only at 9.

**The fifth is a genuine absence, and it prints rather than decides.** Nothing
anywhere asked whether a change had outgrown its worth. The new checkpoint counts
surfaces, guards and REQ rows now versus at stage 2 and prints all three — the
stage-3 gate is the operator's, and an agent that narrows the task on its own
judgement breaks *never narrow the task silently*.

**Both self-reviews now leave a committed trace.** A `## Self-review` section,
identical in shape across the two files, every line a **computed number rather
than a tick** — because a number nobody computed is visible as such and a
checkbox never is. `planning.md` already demanded the REQ set difference be
*printed*; this extends that principle to the rest of the checklist.

Three guards prove the files carry the items, with four probes. What they cannot
prove is that a run in someone else's repository performed a self-review — and
that boundary is stated in the spec, in the guard's own comment and here, because
a guard claiming otherwise would be the exact defect this release fixes.

Negative self-tests: 76 → 80.

## v1.12.0 — 2026-08-05

### Added — a gate for the defects an agent leaves behind

Every other check in this repository asks whether the work is *right*. None of
them asked whether the text is *intact* — whether a merge was left half-resolved,
a stub outlived its task, a generation stopped mid-fence, a file was "shortened"
while being rewritten, a retried edit duplicated a block instead of replacing it,
or a section was opened and abandoned. That class has an author, and the author is
an agent.

`templates/hygiene.sh` is the answer: a seeded, executable gate, sibling of
`docgate.sh`, carrying the same contracts — a `SCOPE:` header that names its own
false-positive surfaces, a VERDICT block that must be last, portability to macOS
bash 3.2, progressive arming, and a final line of computed numbers. It runs in two
modes: the run's diff at **zero tolerance**, and the whole tree behind per-check
**ratchet floors**, so an existing repository can adopt it without starting red
while nothing new is forgiven.

**It never edits.** None of the six defects is safely machine-fixable — deleting a
"duplicated block" sometimes deletes a legitimate repetition, and deleting a `TODO`
erases a reminder instead of discharging it. `references/build.md` makes fixing the
agent's obligation, at the point it is cheapest: after each task reports `DONE`,
before the reviewer sees it. Found one task later, a defect costs a re-dispatch;
found eight tasks later it is fixed by an agent that no longer remembers the code.

**Two of the six definitions were wrong until they were measured**, which is the
point of the rule that says measure a detector before shipping it. Matching the
word `TODO` anywhere found 33 hits here, 28 of them ordinary English — this is a
repository whose own doctrine is *"a ratchet, never a TODO"*. Anchored as a
line-leading marker: 0. Flagging a heading followed by any heading found 62
legitimate nestings; restricted to same-or-higher level it found 4, and the
detector still had a bug — fenced lines were skipped entirely, so a section whose
body is one code block looked empty. Counting fenced content as body: 2, both real.
Check 4 then repeated check 2's mistake in its sibling and was caught the same way.

Those last 2 were fixed rather than absorbed into a floor, so all six ship at 0.
One of them was a shape mistake in the retro template every project copies: a
one-line retirement record written as a heading, when a heading promises a section.

### Fixed — a guard that had been decorative since it shipped

Writing the first probe for the VERDICT-last contract revealed that the guard split
each gate script on the *word* `VERDICT`, which also appears in the header sentence
forbidding anything after it. Its "tail after the verdict" was therefore most of the
script, exit lines included, and it passed on anything. It now splits on the
`# ---------- VERDICT` marker and requires that marker to exist. A green from a
check nobody has watched fail is not evidence; this one was green for nine releases.

The template contract guards now iterate a `GATE_SCRIPTS` list instead of naming one
file, so a third gate costs one line rather than a copied block that drifts.

Negative self-tests: 68 → 75.

## v1.11.0 — 2026-08-04

### Added — run continuity: the pacing rules the operator was repeating by hand

Two rules that had to be said out loud at the start of every run. One of them was
already written down, which is the interesting half.

**The loop mode is now config, not a request.** `references/build.md` has carried
*"Continuous execution: don't check in between tasks"* since early on, and it did
not work — for two compounding reasons. It lived inside stage 5, so an agent
running any other stage never saw it; and on a harness where a turn ends, prose
cannot carry a run across the boundary at all. Only a scheduled re-invocation
can. So the decision moved to `pipeline.json` → `run.loop`, read at preflight in
the same block as the model: recorded means armed and never re-asked, absent means
**off**. `build.md`'s rule keeps its full force and gains one sentence naming its
scope, because the two govern different things and a reader was going to take one
for the other.

**The context rule fires on evidence or not at all.** The opposite failure was
live: runs announcing that context was nearly exhausted against a mostly-empty
window, because an estimate from transcript length was being presented as a
measurement. Nothing returns the remaining percentage, so the rule now admits
exactly two signals — the harness saying so, or the operator saying so — and
forbids the announcement without one. When it does fire: finish the item in
flight, start no new one, make the ledgers true, continue. Not stop.

There is deliberately **no config field** for the context half. The one number
anyone would put in it is the one that can never be honoured, and the schema's own
`description` says so — a blank space in a contract gets filled back in by the
next contributor as an oversight.

Both halves live in one new file, `references/continuity.md`, because they are one
mechanism: the loop is what makes the context rule necessary. Without a loop a run
stops at the turn boundary anyway; with one, it will start an item it cannot
finish.

### Fixed — three templates whose links were broken everywhere they are read

`templates/adr.md`, `carryover.md` and `routing-rule.md` carried relative links
that resolved from `templates/` — where the files are stored — and from nowhere
they are ever actually seeded. `carryover.md` had shipped one since v1.1.0 and the
link checker was green the whole time, because it resolves from the file's home.
No run had seeded the template verbatim, so nobody hit it until one did.

The rule is now the one the Cursor rule already follows: a document that travels
is self-contained, and names files in code spans rather than linking to them.

### Guards — 63 → 68

`run.loop.mode` must be set explicitly in the shipped example; five surfaces must
name `continuity.md`; the two load-bearing clauses in `continuity.md` must survive
an edit (matched after whitespace normalisation, since both wrap at 80 columns and
a line-oriented search would reject correct prose); and no seeded template may
carry a relative link. Four invariants added to `CONTRIBUTING.md`, each citing the
guard that enforces it.

`CLAUDE.md`'s claim of *sixteen* invariants — the list held twenty-four — was
deleted rather than corrected. A hand-written count drifts; that is what the rule
about computing numbers is for, and this file was breaking it.

## v1.10.3 — 2026-08-03

### Fixed — the cause behind five audits, rather than a sixth symptom

Five audit passes produced roughly thirty findings. Grouped by shape, **nine of them
were one missing row**: this repository ships a propagation matrix to every project it
touches and its own had no row for *adding a document*.

`adoption.md`, `setup.md`, `portability.md` and `learned.md` never reached the README
map · the manifest covered 14 of 26 references · the Cursor rule ran two releases
stale · `CONTRIBUTING.md` ran eight guards behind · `agent-sync` was doctrine in four
files and absent from the companion matrix · `templates/README.md` went stale. One
cause, nine symptoms, five audits — and **every check was green throughout**, because
a check can only walk the list it was given.

**The meta-row.** The most frequent change in any documented project is adding a
document, and it is the row nobody writes — so the matrix ends up unable to catch the
class it will meet most often. It is now:

- **step 0** of the matrix-building procedure in `references/documentation.md`, with
  the measurement attached;
- a row in this repository's own `docs/DOCMAP.md`, first;
- a row in the seeded `templates/docmap.md`, guarded — a seeded matrix without it
  fails the build;
- pass 4 of the entry audit in `references/setup.md`;
- a named step before the tag in `CONTRIBUTING.md` → *Releasing*, where the one cell
  that is `review` — the Cursor rule — is called out, because no check can decide
  whether a change alters how an agent behaves in a **foreign** project. That cell was
  skipped twice, and the rule shipped two versions stale.

### The two causes no row can fix, stated rather than left implied

**Guards are written after a finding.** The doctrine's own rule — a class seen twice
becomes a script — is by construction one instance late, and twice a fix was scoped to
its instance rather than its class.

**Author and reviewer are the same person**, which `SKILL-CARD.md` already discloses.
Five audits are what a review would have been.

## v1.10.2 — 2026-08-03

### Fixed — the list of invariants was eight guards behind, and now checks itself

A fifth audit pass, on two axes never used before: **the consumer's view** (unpack the
published package and run its installer in an isolated HOME — clean install works, the
refuse-on-plugin path fires, all 58 files present) and **one class swept end to end**:
every claim of enforcement against the guard that supposedly makes it true.

The doc map's six *Checked by* cells all resolved. `CONTRIBUTING.md` did not.
It states plainly that its invariants are *"what the validator enforces"*, and it had
sixteen while the validator enforced eight more concepts it had never heard of —
adoption, the exclusion clause, the opt-out, the input map, portability, the routing
template, the README-reach rule and the seeded-template Contents rule.

**The previous round fixed this class in one instance and not as a class.** The reach
guard shipped last release covers *references → README and manifest*; nothing covered
*guard → CONTRIBUTING*. `references/learned.md` rule 6 — sweep the class, not the
finding — applied to the sweep itself.

So the list is now **self-verifying**: invariants 17–24 name the new guards, and every
invariant that cites a guard cites a **literal this validator actually prints**. A
claim of enforcement is checked like any other claim. One discovered constraint is
stated with it: a cited literal must lie inside a *single* string in `test/validate.py`,
because the check reads that file as text — a quote straddling a line-continuation is
a citation nothing can find, which is how the first three citations failed.

## v1.10.1 — 2026-08-03

### Fixed — four surfaces that never heard about the last two releases

A fourth audit pass, on a fourth axis: **the claims of the last three releases,
checked against the tree.** All four findings are the same shape — a file shipped and
the surfaces that tell a reader it exists were never walked. Reachability from
`SKILL.md` was green throughout, because that check proves an agent can *find* a file,
not that anybody was *told* about it.

- **The Cursor rule was two releases behind** — and it is the surface that travels,
  copied into foreign projects and required to be self-contained. It knew the
  documentation track and nothing about adoption, the entry audit, portability, the
  routing boundary or the opt-out phrase: an agent reading it in another repository
  had no idea when the pipeline applies. Measured `0` for each. Now current.
- **The README's documentation map** listed `adoption.md` and named neither
  `setup.md` nor `portability.md` — and had never named `learned.md` at all.
- **The portability manifest covered 14 of 26 references.** It claims *every workflow
  decision*, and the twelve stage doctrines — spec, build, planning, review,
  acceptance, brainstorm, decomposition, tdd, conventions, companion-skills,
  knowledge-graph, model-tiering — had no row. The guard could not see it: it checked
  that every listed path resolves, which is the direction that cannot find an absence.
- **Two seeded templates over 100 lines had no `## Contents`** — the doc map (eight
  sections) and the brief (nine). The rule was scoped to `references/` while the files
  a host project actually reads were outside it.

**Two new guards, and they are the point.** Every reference must appear in the README
map *and* in the manifest; every seeded template over 100 lines carries its own
Contents. Both check the direction that finds absences, and both were watched failing.

## v1.10.0 — 2026-08-03

### Added — the entry audit, and a boundary that keeps the workflow portable

**`references/setup.md` — the audit that runs *before* the feature.** The ladder in
`audit.md` runs at the end of a run, over the change; nothing ran at the start, over
the documentation a project already has. Seven passes, cheapest first — one decision
home, register integrity, propagation (ratcheted), the matrix's *Checked by* column,
declared terms, the UX chain, and the gate itself proven against a planted defect.
Findings carry `file:line`, the minimal fix and **the seam they belong to**, ordered
by seam rather than by file, because a file-ordered list reads as noise and a
seam-ordered one names the layer of the project's own process that is leaking. It
ends in a fix plan, not a lecture, and it **fixes nothing while reading** — that is
how a pass starts finding its own edits.

**Offered once, never imposed.** Stage 0 asks when the doc map is absent or stale;
the answer, including a refusal, is recorded in the brief and never asked again. A
check that runs before every feature is a check people learn to dismiss.

**`references/portability.md` — the boundary the whole bundle rests on.** A decision
about *how the pipeline behaves* belongs in the bundle; a decision about *what this
project decided* belongs in the project. Get it backwards and one of two quiet
failures follows: an optimisation stranded in one repository, or a skill that has
learned one project's answers and stopped being project-agnostic.

It ships a **manifest** — every workflow decision with its home inside the bundle —
and a guard that resolves every path. And it names both directions, because a
comparison needs two sides: *outward*, does every workflow decision have a home here;
*inward*, is this project holding a rule that would be true in a repository nobody
has seen. The inward test is one line — **does the rule name a path, a command or a
person?** If not, it is the bundle's, and keeping it local costs every future project.

**The routing rule now travels.** It was hand-installed into an operator's config
last release, which made it the one workflow decision living outside the bundle —
neither installer touches any `CLAUDE.md`. It ships as `templates/routing-rule.md`,
and `setup` **offers** to append it. Offers, never writes: it is the operator's
configuration.

### Added — three smaller things the same run asked for

- **Self-currency.** Preflight compares the installed version with the released one
  and recommends the **launcher** (`npx sshlg-skills update`), never the bare
  per-skill form that re-creates the plain copy which shadows a plugin. Plus three
  staleness signals that are not version numbers: a standing instruction that has not
  fired in five stamps, a doc map older than the last release, a ratchet whose count
  has not moved.
- **The escalation boundary.** The autonomy sweep gains the rule that lets a run go
  further without stopping: decide alone while the cost of being wrong stays inside
  the repository and is reversible; escalate a price, a legal posture, a promise, money,
  reputation, and any irreversible outward act. **The tell is the cost of being wrong,
  not the size of the change.**
- **User paths become a stage-2 output.** The contract layer was never the thin one —
  the spec already locks error handling and a module dossier already has edge cases.
  The thin layer was the *conversation*: `brainstorm.md` mentioned edge cases once and
  scenarios not at all. Paths, states and error paths are now named where the design
  is approved, and the gate says so. Scenario IDs stay the chain's job — two sources
  for one scenario is worse than one.
- **Declared terms.** The seeded doc map gains a *Terms* table, and only terms it
  declares are checked. A heuristic over every capitalised word cries wolf, and a gate
  that cries wolf is removed by the third person who hits it.

Three new guards, each with a negative self-test watched failing.

## v1.9.1 — 2026-08-03

### Added — the direction of the artifact map that was missing

`references/artifacts.md` mapped **stage → what it writes → who consumes it** and
nothing the other way. What an agent actually needs at runtime is **what each stage
reads, and from where** — and that direction had been absent since the file was
written. It is `references/learned.md` rule 2 (*compute the mapping in both
directions*) left unapplied to this file itself: the direction that feels redundant
is the one that finds things.

Two tables now sit above the old one:

- **Stage → input map** — per stage, the exact inputs and their origin. Stage 9's row
  is the one worth reading twice: it takes **two different lists**, the stage-0 source
  ledger (what the run *read*) and the doc map's propagation matrix (what the run
  *owes*), and the gap between them is where documentation rots.
- **Project-saved rules, and where each one binds** — the eight files a host project
  owns that change how a run behaves, each with where it is read and where it is
  enforced: `CLAUDE.md`/`AGENTS.md`, `docs/DOCMAP.md`, the retro's standing
  instructions, the brief's autonomy section, the carry-over ledger,
  `docs/ux/scenarios.md`, `.claude/agent-sync.json`, and the operator's global config
  that decides whether a task routes here at all. Plus the precedence rule: for *what
  is*, code wins; for *what should be*, the register wins, and the gap is a finding
  rather than a tie-break.

A guard holds all three maps present, with a negative self-test watched failing.

## v1.9.0 — 2026-08-03

### Added — the adoption track, and default-on inside a stated boundary

Built by running this skill through itself: brief, spec, plan, gated stages,
acceptance. The stage-0 harvest found two things that changed the shape of the work,
and one of them is why this release exists at all.

**`references/adoption.md` — the first run in a project.** The pipeline assumed a
documentation system either exists or gets seeded, and said almost nothing about the
repository you actually have. Greenfield is mechanical: stage 0 seeds the map, the
registers and the gate, and the gate is green on day one because unarmed sections
print `dormant`. Brownfield is a different problem and now has seven steps, of which
**step 3 decides whether adoption survives**: baseline the ratchets at today —
`PROP_FLOOR` to the next free id, `RESIDUE_FLOOR` to the measured count — so the gate
is green on the history it inherited and red only on what happens next. On the
project this practice comes from, the first run of that check reported **162 missing
propagations across 73 decisions**; that is a printed number, not a to-do list, and a
gate that is red on adoption day is switched off on day two.

It also states the rule that keeps a register honest: **history is not back-filled.**
An old decision enters the register the day somebody is about to contradict it —
when the reason is being discussed anyway and the person holding the context is in
the room. A reconstructed rationale is indistinguishable from a real one forever.

**Default-on routing, inside a boundary.** The description now widens to work that
**changes the repository** — feature, fix, refactor, migration, integration, rewrite,
adoption, hardening, with Russian verbs beside the English — and carries an explicit
`Not for:` clause for questions, explanations, typos and one-line edits, plus the
opt-out phrases *"без пайплайна"* / *"quick"*. Two evals follow it: a plain Russian
refactor that must trigger, and the same request with the opt-out that must not. A
guard ties the two together, because an escape hatch nobody tests is a trap rather
than a default.

**The lever that actually binds is not in this repository**, and the brief says so:
a `description` raises the odds a skill is selected and cannot make selection
mandatory. Default-on is enforced by an instruction in the operator's `CLAUDE.md`;
the description makes it reachable.

### Fixed

- **The ratchet floors were documented as the same kind and are not.** `PROP_FLOOR`
  is an **id threshold**, `RESIDUE_FLOOR` is a **count**; the comment called both
  counts. Adoption turns on that distinction, so it is now spelled out where the
  floors are declared.
- **The frontmatter guard wore the platform's number.** It capped the whole block at
  1024 — the limit Anthropic puts on `description` alone — silently making the
  usable description ~975 and reading as if it were the real rule. The platform's
  limit stays on `description`; ours becomes a stated budget of 1200.
- **agent-sync's binding to this skill** (patched in that repository): its
  `pipeline.json` example claimed this schema permitted it while carrying a string
  `id`, a `title` where the schema says `name`, and no `state` at all — required. Its
  gate texts stated only agent-sync's half, so a host that copied them silently
  dropped the stage's real gate. Stage 9 pointed at the artifact-layout reference
  instead of that stage's doctrine. And `guardedFiles` did not cover `docs/DOCMAP.md`
  or `docs/superpowers/retro.md`, both of which this pipeline now creates and both of
  which lose data under a concurrent write. `companion-skills.md` states the
  **≥ 1.3.0** floor `finish` needs.

### Dogfooded

This repository ran its own brownfield walkthrough and wrote `docs/DOCMAP.md`. Step 1
— *inventory what is already there* — changed the plan: `npm test` already resolves
links, checks citations and computes counts over the same markdown, so **no second
gate was seeded**. The map records the gate that exists and why no other is created,
which is the walkthrough's step 2 read correctly: seed what is *missing*, and here
that was the map. The changed check went to the carry-over ledger for the operator's
agreement rather than being swapped silently.

Two new guards, each with a negative self-test watched failing.

## v1.8.1 — 2026-08-03

### Fixed — eight findings from a code-and-contradiction audit of 1.8.0

A third pass, on a third axis: the first read for contradictions, the second measured
against Anthropic's guidance, this one went after the **code** and the **invariants
between files**. Everything below was proven before the fix and again after.

**Fifteen broken cross-references, eleven of them pointing at a section about
something else.** Every per-stage freedom label cited `gates.md → Axis B` — which is
the *enforcement ladder* and contains no mention of degrees of freedom. Two more
cited sections that do not exist at all (`gates.md → progressive arming`,
`review.md → Final review`). This is the failure `references/learned.md` keeps as a
review question rather than a rule: *"a stale reference was replaced with a FALSE
one — the new target existed and said nothing about the subject."* The link checker
proved every file resolved and could not see it.

It is a rule now. `gates.md` gained the two sections the citations were reaching for
— **Axis C — degrees of freedom** and **Progressive arming** — and a guard checks
every ``file.md → *Section*`` pointer against the target's actual headings. Measured
before shipping: whitespace is normalised first, because a citation wrapped across
two lines is not a defect and six were reported as such.

**Both installers created the shadow copy this family exists to prune.**
`install.sh` and `bin/task-pipeline.js` write a plain copy to
`~/.claude/skills/task-pipeline`; the launcher (`sshlg-skills`) deletes exactly those
because while the plugin channel is active a plain copy **shadows it and keeps
serving the version it was copied from**. `CLAUDE.md` documented the shadow-creating
form (`--force`) as the local install path. Both installers now **refuse when a
plugin install is detected**, name the plugin commands instead, and take `--force`
only as a deliberate override.

**The npm package did not contain what the README points at.** `SKILL-CARD.md` and
the whole `evals/` directory were outside `files[]` while the shipped README linked
both — and `CONTRIBUTING.md`, `SECURITY.md` and `CODE_OF_CONDUCT.md` had been
dangling for npm consumers far longer. Rule 14 — *a document may not send a reader
to something absent* — applied to the artefact that is actually published. All are
packaged now, and a guard holds every relative README link to `files[]`.

**Living documents restated a guard count that had moved.** `SKILL-CARD.md` and
`evals/RESULTS.md` claimed 46 after the suite reached 50. Rule 8 — *compute, never
restate* — had never been applied to this repository's own prose. It is now: the
count is compared against the negative self-tests the workflow defines, and the
guard caught its own author within the minute, when adding three tests made the
freshly-corrected numbers stale again. CHANGELOG entries are exempt; they record
what a past release shipped.

**The contributor invariants were numbered 1,2,3,4,5,6,10,7,8,9 — and number 8
documented the opposite of what is enforced**, still requiring the description to
*open* with `Use when` after v1.8.0 made that a failure. Rewritten: sixteen
invariants, in order, each matching a guard that exists.

**Smaller:** the seeded gate's empty-project failure named only `docs/` while it also
scans the repository root, and offered no remedy — it now names both and says what to
do; `CLAUDE.md` gained the `evals/run.py` row it never had.

Three new guards, each with a negative self-test watched failing.

## v1.8.0 — 2026-08-03

### Added — the skill now meets Anthropic's own authoring guidance, measurably

Audited against the four Agent Skills pages (overview, best practices, enterprise,
API guide). Most of the spec already held — `name` 13/64 chars, `description` inside
1024, `SKILL.md` 334/500 lines, all 23 references linked **directly** from SKILL.md,
forward slashes only, 436 KB against a 30 MB ceiling, and the plan-validate-execute
pattern the guidance describes is exactly the stage 3→4 set-equality check. Five
things did not.

**Every reference over 100 lines now carries a `## Contents` list — 21 files, from
zero.** The guidance is explicit about why: *"This ensures Claude can see the full
scope of available information even when previewing with partial reads."* That
preview is real, and `references/stages.md` is 500 lines — an agent that previewed
it saw stages 0 and 1 and could not learn stage 9 existed. The list is **compared
against the file's own headings**, not merely required to be present, because a
hand-maintained contents list is a second source that goes stale on the next
heading.

**A behavioural evaluation suite, where there was none.** 46 structural guards prove
the skill is well-*formed*; nothing proved it *behaves*. `evals/` now carries 13
evaluations across the five dimensions the enterprise page names — should-trigger,
should-not-trigger, ambiguous, coexistence with super-ux, and instruction-following
(does phase 1 really run before the first question; does stage 9 walk the matrix and
print ratchets; does a stage-5 subagent refuse to write the register; does stage 10
run the ladder walk before the table).

`evals/run.py` validates the suite and prints the protocol. **It never reports a
pass**, because Anthropic ships no runner and a script claiming to have executed a
model would be the exact failure this repository is written against.
`evals/RESULTS.md` records the honest state — *authored, zero models exercised, zero
runs* — as a ratchet, so "46 of 46 green" is never read as "the skill is known to
work".

**A copyable run checklist and a stated degree of freedom per stage.** The guidance
recommends a checklist Claude copies into its response for complex workflows, and
matching specificity to fragility — high freedom in the open field, low on the
narrow bridge. Every stage now declares which it is and why: stage 2 is high (many
designs are valid), stages 5, 7 and 9 are low (TDD order, an irreversible deploy, a
mechanical matrix walk).

**`SKILL-CARD.md`** — the registry entry the enterprise guidance asks for (purpose,
owner, version, dependencies, evaluation status) plus an honest pass over its
risk-tier table. This skill scores **three High indicators** — shipped scripts, MCP
references, tool invocations — and says so, along with the three things a consumer
should know rather than discover: author and reviewer are the same person, commits
are unsigned, and behavioural evidence is missing rather than thin.

### Changed

- **The description leads with what the skill does, then the trigger** — the shape
  Anthropic's own examples use. The validator used to *require* the string start with
  "Use when", which enforced the WHEN half and left the WHAT half optional; it now
  checks for both, plus the third-person voice the guidance requires.
- MCP tools are named fully qualified (`context7:resolve-library-id`), because
  without the server prefix Claude may fail to locate the tool.

Four new guards, each with a negative self-test watched failing.

## v1.7.2 — 2026-08-03

### Fixed — nine findings from a post-release investigation of v1.7.1

The release was audited against the skill's own ladder, bottom-up, findings ordered
by seam. Every one below was proven before it was fixed and again after.

**The gate enforced one of the two register shapes it promises.** `documentation.md`
permits two decision homes — `docs/DECISIONS.md` or `docs/adr/` — and says they owe
the same six things; `docgate.sh` parsed only the first. Measured on a real ADR
project: **eight of ten sections went `dormant`**, dormant is green by design, and a
planted propagation violation was not caught. The gate now builds a **normalised
entry index** from whichever home exists, so no section knows which shape it is
reading, and holding both at once is itself an error. Seven planted defects on the
ADR shape, all firing.

Two of those probes exposed bugs in the checks rather than in the fixtures — the
fixture is derived from `templates/adr.md`'s own fenced example, so it cannot drift
from the documented format. HTML comments were not stripped, so a status line
carrying `<!-- or: Superseded by ADR-0012 -->` made an entry read as retired *and*
invented an undefined id; and the first fix dropped the line that **opened** the
comment, throwing away the `Status:` before it. Duplicate ADR numbers were counted
from the entry index, whose one-row-per-id dedupe swallowed exactly the second file
this check exists to find — it counts filenames now, because the filename is the
allocator.

**Exit 0 was not proof that the gate had looked.** Every section can go `dormant`,
so a gate blind to a shape passes identically to one that reads it. The validator
now asserts the seeded run **reports which shape it found** and **ran at least N
live checks** — the difference between "it did not fail" and "it looked".

**The Doc Loop was declared cross-cutting and appeared in no stage doctrine.**
`brainstorm.md`, `spec.md`, `build.md`, `review.md` and `acceptance.md` had zero
mentions of it — so the flow as an agent *executes* it never ran the loop, because
an agent opens the stage file, not the orchestrator's summary. All five now say
where a settled decision goes, and it is a guard.

Most of that gap was at stage 5, which settles more decisions than any other stage
and runs in an isolated worktree with parallel implementers. The rule is now
explicit and argued from the same physics as the existing parallel-fan-out rule:
**a subagent never writes the register** — append-only shared state cannot be
hand-merged across worktrees, and an id cannot be *reserved* from a branch that
cannot see the other writers. Decisions ride the implementer report and the ledger;
the orchestrator runs the loop after integration, as a single writer.

**`hooks.md` stated an external contract from memory.** Re-fetched from the Claude
Code hooks reference and corrected: `permissionDecision` has **four** values, not
one; there are **35** events, not the four listed; `effort`, `agent_id` and
`agent_type` were missing from the stdin fields; `if` is evaluated on five tool
events and its Bash matching is best-effort. The reference also says outright that
**exit 1 is non-blocking "even though 1 is the conventional Unix failure code"** —
which is the sharpest possible argument for the `|| exit 2` this file already
required. Provenance and fetch date are now in the file, because stage 1 of this
pipeline exists for exactly this.

**Smaller, and all real:** a "we don't document" escape hatch in `documentation.md`
contradicted the seeding rule four lines above it and the stage-0 gate; the stage-9
config gate carried both the retired criterion *"docs in sync with code"* and the
sentence declaring it retired; a lost edit meant the grill never asked the
documentation-regime question the brief had a field for — and the sweep-drift guard
missed it because it compared **stage numbers**, which both files still matched, so
it now compares topics per stage (measured: zero false positives, including the
legitimate case where the brief splits one grill row into two); `acceptance.md`
never mentioned the documentation gate it is supposed to prove; and nested bold in
the stage-10 gate criterion inverted the emphasis of everything after "every
deletion logged".

Three new guards, each with a negative self-test watched failing.
**46 of 46 guards provably reject their planted defect.**

## v1.7.1 — 2026-08-03

### Fixed — the tag-ancestry gate had been failing on every release since v1.6.1

The step that exists so *"a release does not live only on a tag"* — added after the
v1.4.4 incident — **failed on every tag from v1.6.1 onward**, and nobody saw it,
because `release` ran green beside it and the failing log showed only the echoed
script with no output of its own.

`git fetch --tags` without `--force` aborts with *"would clobber existing tag"* when
the checkout has already created `refs/tags/<tag>` locally and the tag is
**annotated**. `set -eu` then killed the step before its first `echo` — which is why
the log was blank and read as though the ancestry check itself had found something.
v1.6.1 was the first tag cut with `git tag -a`; every one since inherited it.

Two changes, and the second matters more than the first:

- `--force` on the tag fetch, with a printed note if it still degrades.
- **The step now says which failure it is.** If `refs/remotes/origin/main` cannot be
  resolved, every tag looks like an orphan and the old wording reported a
  catastrophe that was really a missing ref. It now fails with that sentence
  instead, and on success prints the tag count and the `main` it checked against.

This is the shape the repo's own doctrine names: a gate whose exit code nobody reads
is a gate that has stopped guarding — `references/gates.md` → *A gate's exit code is
part of its output*, and `references/learned.md` rule 11. It was found by watching
the release this release shipped, which is the only reason it was found at all.

## v1.7.0 — 2026-08-03

### Added — documentation is a deliverable, and it has a gate

Stage 9's gate read *"docs in sync with code"*. That sentence names no artefact and
no command, so nothing in the run could make it false — and the pipeline had no
concept of a decision outliving the spec that recorded it. Three built-in doctrines
close that, ported from a 260-decision, 72-document specification built across four
repositories with several agents editing at once.

**`references/documentation.md`** — the inventory (four questions, answered before
the first interview question and written to `docs/DOCMAP.md`), registers and stable
ids, single source of truth including its cross-repository form, **the Doc Loop as a
cross-cutting protocol** that fires whenever anything is settled rather than only at
stage 9, append-only history with three distinct edge markers, the propagation
matrix and its ratchet, navigation, intent vs as-built, and registers as shared
state.

Two measurements decide two of those rules rather than taste. **204 of 275**
refine/supersede edges pointed at an unannotated target — which was not 204
violations, because most were additive; *that ambiguity was the defect*, and it is
why `Refines:` / `Contradicts:` / `Supersedes:` are three markers with different
obligations. And turning the propagation check on found **162** missing citations
across **73** decisions, not the four an audit had reported — so it ships ratcheted,
because failing on all of them makes a gate people switch off.

**`references/gates.md`** — the two axes (a stage's `auto`/`manual` type versus the
enforcement mechanism) and the promotion ladder: doctrine line → review question →
script check → CI step → hook, with the trigger for each promotion. It owns
*procedure* only; `audit.md` and `learned.md` already own probes, ratchets, exit
codes and false positives as *law*, and a second statement of one law is the exact
defect this release ports a rule against.

**`references/hooks.md`** — the `PreToolUse` contract, led by the limit rather than
the capability: hooks exist only in Claude Code, and **any exit code other than 2 is
non-blocking, so a crashing guard fails open** and stops guarding without announcing
it. Elsewhere the run is `ungated` and must say so.

### Added — a documentation gate that travels, and seeds green

**`templates/docgate.sh`** is a portable gate (bash 3.2; no `grep -P`, no in-place
stream edits, no bash-4 builtins) with ten sections, ratchet floors as variables,
printed register sizes, and **progressive arming**: a section whose input does not
exist yet prints `dormant` and does not fail. That is what makes always-governed
survivable on a three-file repository — the alternative was regime tiers, and a tier
is a switch that gets set to "minimal" by whoever is in a hurry.

Probe log — every section planted, run, restored, asserted on `$?`:

```
1 links · 2 ids · 3 next-free · 4 counts · 5 propagation · 6 supersede
7 residue · 8 vocabulary · 9 commit SHAs (armed tree) · 10 doc map    10/10 fire
```

Two probes came back silent and they landed on opposite sides of the doctrine. One
was a bad probe: section 9 correctly *skips* outside a git tree, so expecting a
failure there was wrong. The other was a real bug in the gate — `$((0009))` is
octal, `9` is not an octal digit, the expansion errored, the `if` took its else
branch, and section 3 printed `ok` for **every id ending in 8 or 9**.

Also seeded: `docmap.md`, `decisions.md`, `open-questions.md`, `retro-archive.md`
and one worked `hooks.example.json`. Lease arbitration is **not** reimplemented —
`agent-sync` owns it and is now in the companion matrix and the preflight, where it
had been missing while four other files leaned on it.

### Changed — the retrospective is traceable, and bounded

Standing instructions carry `Born`/`Commit` and `Last fired`/`Fired at`; every log
entry, retirement and run stamp carries a commit; and every SHA must resolve, which
the seeded gate checks with `git rev-parse --verify` — rule 14 applied to history. A
`file:line` rots at the next edit, while `git show <sha>` reconstructs the whole
incident months later, which is exactly when a class returns.

Entries older than the last five run stamps now **rotate** into
`docs/superpowers/retro/YYYY-QN.md` — append-only, queried by the task's nouns,
never read end to end. This also closes a contradiction the file had carried from
the start: it was described as *read in full* while containing an unbounded log, so
the cap that justified reading it protected one section while the rest grew.

### Fixed — defects found while porting, in the files the port touched

- **`SKILL.md` promised what it contradicted 42 lines later**: "no stage that can
  fail because a dependency is missing", then "for UI tasks the spec gate
  **requires** super-ux". `companion-skills.md` had the true rule all along.
- **Source precedence was stated once for two different questions.** `code`, then
  docs, then the wiki, then memory is right for what *is* and wrong for what
  *should be*: a decision accepted and not yet built is still the decision.
- **`learned.md` narrated its most expensive incident and never gave it a row** —
  a full day of work performed under another session's identity. Now rule 15, with
  its check, cross-referencing the narration rather than repeating it.
- `conventions.md` never asked where decisions live; `audit.md`'s "put it in a
  script" had nowhere to point; the carry-over ratchet was required by one gate and
  specified for all of them; `templates/README.md` had no guard and would have gone
  stale on the first new template.
- `test/negatives.py`'s floor sat at **20** while the workflow carried **34** — it
  would have caught a total collapse and not the loss of a third of the suite.

Eleven new validator guards, each with a negative self-test watched failing. One of
them **executes** the seeded gate over a scratch project and requires exit `0`.
**43 of 43 guards provably reject their planted defect.**

## v1.6.1 — 2026-08-01

### Fixed — v1.6.0 shipped without `displayName`, because a release lived only on a tag

**`v1.4.4` was tagged, released and published to npm, and its commit was never in
`main`.** It added `displayName` ("Task Pipeline") to both manifests — the label the
plugin picker shows. Every branch cut from `main` afterwards therefore started from a
tree that had never seen it, and v1.6.0 published a manifest without the field,
quietly returning the picker to the kebab-case `name`.

Nothing inside either record looked wrong: `main` was consistent with itself, the tag
was consistent with itself, CI was green on both, and the registry served a 1.4.4 no
branch contained. That is the same shape as the parent/submodule pointer this
project's own stage-10 doctrine already guards against — **a disagreement that lives
between two records and survives every check that runs inside one.**

- `displayName` restored, and the v1.4.4 section restored to this file. The fix is a
  **merge of the tag**, not a re-typed field: copying the content back would have
  left the tag still outside `main`, which is the condition that caused this.
- **CI now refuses an orphaned release:** every `v*` tag must be an ancestor of
  `main`, checked on every push. The next tag that lands outside the branch is a red
  build, not a feature that disappears three releases later.
- **The validator now rejects unresolved merge conflict markers.** Resolving the
  merge above surfaced it: a `CHANGELOG.md` carrying three `<<<<<<<` markers passed
  every existing check, because they all look at structure and none at the text. In a
  repo that is almost entirely prose, a half-resolved merge ships as doctrine an
  agent reads and obeys. (34 guards now, each with its negative self-test; the
  tag-ancestry check is a CI step rather than a validator guard, since it needs git
  history the offline validator does not have.)

## v1.6.0 — 2026-08-01

### `references/retrospective.md` — the run teaches the next run, and the list stays short

Every gate in this flow is good at *this* run and blind across runs. So a class of
failure gets caught, fixed and forgotten five times, and nothing in the pipeline
notices it is the same one. The ladder walk finds what was never written **inside** a
run; nothing was looking across them.

Stage 10 now ends with a **retrospective** written to `docs/superpowers/retro.md` —
**one file per project, not per run**, seeded from the new `templates/retro.md`.
Every run prunes and stamps; only a run that *diverged* writes an entry, and the
entry names the stage that **owned** the failure rather than the stage that tripped
over it — recording it against the latter is how the same defect comes back.

**Fixes have three grades, and the highest one that works is the one you take:** a
mechanical check (a test, a lint rule, a gate criterion — the check *is* the memory,
so nothing has to be remembered or pruned later), a **standing instruction** for
what no check can decide, or a note that expires in two runs.

**The part that makes it survive: the prune is mandatory and runs before anything is
added.** Every standing instruction is checked against three retirement triggers —
it became a check · every path or command it names is gone · it has not fired in the
last five run stamps — and the list is held to a **hard cap of ten**. At eleven, the
oldest never-fired rule goes. "But they all matter" is precisely the state in which
the list stopped being read, and the ninth stale rule is what discredits the two that
are load-bearing.

Nothing leaves silently: **every retirement writes one line in the log**, so the
incident survives and only the instruction goes. The counts print beside the gate
verdict like the carry-over ledger's, so a list that quietly grew back is visible
where it happened.

Stage 0 reads the standing instructions **in full** (they are capped, so it is
cheap) and stamps each one as it fires — which is the only evidence behind the
cold-retirement rule. Without that stamp the prune is a mood.

Three new guards, each with its negative self-test: the retro must reach the
surfaces that *enforce* stage 10 — not just `SKILL.md`; the template must ship; and
its standing-instruction table must carry a **Retire when** column and the run
stamps. A retirement trigger written at birth is what makes the prune mechanical
instead of an argument every time.

### Also in this release — what an audit of the two features found

Both features were then walked against the tools they name, which is the only way
this class of defect surfaces:

- **The refresh command was wrong, in thirteen files.** `graphify . --update` was
  documented as a shell command. Run, it does not do what the text claims: the CLI's
  incremental form is `graphify update <path>` and it re-extracts **code only**,
  while `/graphify . --update` is the *agent* form that also re-reads the documents.
  Stage 9 is the stage that just changed the documents, so the shortcut would have
  produced the most expensive kind of stale graph — one that was refreshed. Both
  forms are now documented with the distinction spelled out, and the doctrine says
  which is the default and why.
- **Three stages pointed at doctrine that does not exist.** In the example config a
  `task-pipeline:<name>` entry *is* the built-in doctrine file `references/<name>.md`
  — and `knowledge-harvest`, `decompose` and `plan` resolved to nothing. It read as
  covered on every review. Fixed, and now a **guard** resolves every such entry
  (33 guards total, all provable locally).
- **The retro is a seeded file, and the templates README said only the brief was.**
  The seeding rule matters most there: overwriting `retro.md` with the skeleton
  destroys every lesson the project has bought. Stated explicitly.
- **The harvest source list is renumbered** (the retro's standing instructions are
  source 7, read *in full* rather than queried) and the graph doctrine now says
  plainly that `affected`/`path` are sharp on a code repo and near-useless on a prose
  one — an empty traversal there is not evidence of no coupling.

## v1.5.0 — 2026-08-01

### `references/knowledge-graph.md` — the code graph as a source, and as a second opinion

A grep finds a **name**. The questions that actually stop a run are *what calls this*
and *what breaks if it moves* — **reach** — and reach is exactly what a document
records least reliably, because it records the reach its author remembered. The
harvest had no way to ask that question, so it asked the operator, whose answer
nobody could check.

So the pipeline now uses a code graph where one exists
([graphify](https://github.com/Graphify-Labs/graphify) — detected via
`graphify-out/graph.json`; recommended, never a gate, exactly like the wiki, with its
install line printed once in the preflight block).

**Stage 0** queries it before the interview (`graphify query` / `affected` /
`god-nodes`) and records it in the source ledger **with its build date** — a graph
goes stale like any other source, and it points while the code decides.

**Stage 9 now closes three artifacts, not two:** docs, wiki, **and the graph**
(`/graphify . --update`). The reason it is a peer rather than an afterthought is
asymmetric: the next run's harvest queries the graph *first*, so a stale graph is a
false premise delivered with the authority of a machine. A wrong doc gets argued
with; a wrong graph gets believed.

**And then the part that finds things: the graph↔docs divergence check.** Two
independent statements of the same system, so a disagreement is mechanical instead of
remembered — a hub `god-nodes` reports that no document names is an undocumented
seam; an edge the docs deny is either a leak in the code or a lie in the docs; a doc
naming a module the graph has no node for describes something that no longer exists.
Doc-side findings are fixed at stage 9; **absences become REQ rows at stage 10**,
because this is a fourth audit axis (`references/audit.md`) and the only one that
finds an absence without reading for it. The graph is derived, so it is never
hand-edited: fix the code or the doc and re-extract.

Two new guards, both with negative self-tests: a
shipped graph doctrine must reach the **stage-9 gate** in `pipeline.example.json`
*and* the stage-9 section of `references/stages.md`. That is the third time this repo
has shipped a rule to `SKILL.md` and not to the surface that enforces it — a gate
declared where it is not enforced is inert.
## v1.4.4 — 2026-07-30

### Added
- **`displayName`** ("Task Pipeline") in both manifests — `name` stays kebab-case
  because it namespaces components; the picker shows this instead.

## v1.4.3 — 2026-07-30

### Fixed
- **`argument-hint` in the slash command was unquoted.** In YAML a bare
  `[a | b]` is a flow sequence, not a string, so the hint parsed as a *list*.
  Found by `claude plugin validate --strict`, the upstream schema checker, which
  now runs in CI on both this plugin and its marketplace manifest.
- **`homepage` and `repository` sat at the top level of `marketplace.json`,
  where Claude Code does not recognize them.** They are plugin-entry fields;
  moved there, so the values reach the plugin listing instead of being ignored.

## v1.4.2 — 2026-07-30

### Fixed
- **`pipeline.schema.json` identified itself with a URL that 404s.** The `$id`
  read `https://github.com/ssheleg/task-pipeline/pipeline.schema.json` — a path
  that has never existed (no `blob/main`, wrong depth). This file is installed
  into `~/.claude/skills/task-pipeline/`, so every install carried a schema
  whose declared identity could not be fetched by anything resolving it. Now the
  raw URL that actually serves the file, matching `agent-sync`'s convention.

### Changed
- `license: MIT` declared in the `marketplace.json` plugin entry and in the
  skill's front matter — the `LICENSE` file was invisible to both surfaces.

## v1.4.1 — 2026-07-30

### Changed
- `agent-sync` moved to **`ssheleg/agent-sync`**. The three places this skill
  links to it — `SKILL.md`, `references/stages.md`, `references/acceptance.md` —
  now point at the new owner rather than relying on GitHub's redirect.

## v1.4.0 — 2026-07-29

### `references/learned.md` — fourteen rules earned by failure, each with its incident

Taught to the pipeline by a real build: a 229-decision specification across four repositories with
several agents working at once. Every rule names the failure that produced it, because a rule with
no incident behind it is somebody's preference and gets argued with at the worst moment.

The ones that cost the most, now gate criteria rather than advice:

- **A gate's exit code is part of its output.** One printed `FAIL` and returned `0`; CI had been
  green over it for an unknown period.
- **Doubt the probe first.** Five probes failed before any check did — four times out of five the
  planted defect was never planted, and the silence read as a passing check.
- **Absence needs its own check.** Comparing documents finds contradictions, and a contradiction
  needs two sides; a whole missing subsystem has one. Only the reverse direction of a computed
  mapping found it.
- **Tests create what they assert on.** A test read another test file's leftovers, so it passed on a
  warm database and failed on the cold one every new developer has.
- **A generator seeds green** · **local infrastructure does not publish the host's default ports** ·
  **compute rather than restate** · **sweep the class, not the finding** · **ratchet, never TODO**.

Wired into stages 5, 6, 9 and 10 as gate criteria, not as reading. Two lessons are deliberately kept
OUT of the table, as review questions — *is this the right citation* and *did this number come from
the contract or from prose about it* — because a rule that pretends to be enforced and is not is the
same failure as the gate that printed `FAIL` and exited `0`.

## v1.3.2 — 2026-07-29

**The 26 negative self-tests could not be run anywhere except CI** — which meant
that on the maintainer's own machine, a new guard could never be watched rejecting
its planted defect. The project's own `references/audit.md` demands exactly that
(*plant the defect, watch the check fail, then trust the green*), and the tooling
made it impossible at the one moment it is worth most: while the guard is being
written.

Found by running the full CI suite locally during a validity re-check. Nine of the
26 failed — every one on BSD sed, none on a repo defect.

### Added
- **`test/negatives.py`** — runs every negative self-test locally, zero
  dependencies, same as the validator. `npm run test:negatives`, or
  `npm run test:all` for validator-then-guards. The corruptions are **read from
  `.github/workflows/validate.yml`, never duplicated** — a second copy of a
  corruption is a second thing to drift.
- **It tells a broken test from a guard that didn't fire.** If a planted defect
  changed nothing, the validator passing means the *test* proved nothing, not that
  the guard is dead. That case now reports `BROKEN`, with the fix pointed at the
  workflow. This is the failure mode that hid the sed problem in the first place: a
  no-op corruption reads exactly like a broken guard.
- It also refuses to run if it finds fewer than 20 tests — a parser or format change
  that silently matched nothing would otherwise report zero failures and look like
  success.

### Fixed
- **Every `sed -i` corruption in the workflow is now python.** BSD sed needs an
  argument GNU sed refuses, and `0,/re/` does not exist on BSD at all — there it
  edits nothing *silently*, and the test reads as a guard that failed to fire.
  Nine steps converted; CI and a laptop now run the identical script.

### Validator
- **`sed -i` in `.github/workflows/validate.yml` is now a failure**, and
  `test/negatives.py` must exist. Without both, the guards drift back to
  CI-only and stop being provable where they are written.
- The new self-test builds the forbidden token at runtime, because spelling it
  literally would make the workflow trip the guard it is testing. Verified the
  honest way: a clean copy passes, and the injected copy is the *only* reason the
  corrupted one fails — a self-test that passes because the base is already red
  proves nothing.

## v1.3.1 — 2026-07-29

### Stage 10 closes on the parent repository, not only on the one you edited

A submodule is finished when its parent says so. A parent records each submodule as a pointer to
one commit, and moving the submodule does not move the pointer — so work can be committed, pushed,
green in CI and marked done in its own roadmap while a clone of the parent still gets the commit
before it. Neither repository looks wrong alone; the disagreement lives between them, which is why
it survives every check that runs inside one.

Stage 10's gate now requires every repository — parent included — to be clean, pushed and pointed
at, with the plain-git commands given and `/agent-sync finish` named for projects that have it.

The rule reaches all seven surfaces that carry the stage-10 close-out: `SKILL.md`, the gate in
`references/stages.md`, the doctrine in `references/acceptance.md`, the machine-readable check in
`pipeline.example.json`, `build.md`, `conventions.md`, the slash command and the Cursor rule.

### Validator — the class that caused this is now a check

This close-out has failed to reach every surface **twice**: v0.17.1 fixed it for the third review
verdict, and this release's own first pass declared the parent-repository rule in `SKILL.md`,
`build.md` and `conventions.md` while `acceptance.md`, `stages.md` and the config — *the three
places that actually define the gate* — never heard of it. A gate that says "now requires X" only
where X is not enforced is inert, and no existing check saw it: the validator compared stage ids,
names and gate types, never gate content.

Twice is a category, so it is a check now. Whatever close-out concept `SKILL.md` names, the
surfaces that enforce stage 10 must name it too. Proven against a planted defect, with a CI
negative self-test.

## v1.3.0 — 2026-07-29

**One design file, in a named team, decided before anything is drawn.** Left to
drawing time, "where do I put this?" is answered by whichever agent is holding the
brush, and the answer is usually *create a new file* — which is how a project
acquires three files called some variation of "Design", each with real work in it
and no way to tell which one the team actually opens.

The duplicate is **silent by construction**: the second file is internally
consistent, its frames are named correctly, and the UX linter is green. Nothing
downstream notices that half the design now lives where nobody looks.

### Added — the design destination is a stage-0 decision
- **New sweep row `3 Design file`** (in both homes — `grill.md`'s table, which the
  grill reads, and `templates/brief.md`, which records the answer): **which
  team/org, by name, and which file.** Three legal answers: the file already
  recorded, a URL the operator supplies, or **creation in that named team,
  explicitly authorized**.
- **Creation follows the deploy-authorization floor.** *"Create the design file in
  team `Acme Product`"* authorizes one creation in one place; a vague "set up Figma
  for me" authorizes nothing, because deciding *where* on its own is the entire
  failure. `grill.md` → **The design destination** is the new doctrine section.
- **The team is recorded, not just the file.** A file URL identifies a file; it does
  not say whose workspace it lives in. super-ux runs `whoami` and asks which team
  when there are several — but nothing wrote the answer down, and a design that
  lands in someone's personal drafts is invisible to everyone who needs it.
- **Two rules that make it stick:** never create while a recorded file resolves;
  and **if the recorded file does not resolve, stop and ask — never create a
  replacement.** "I couldn't open it so I made a new one" is simultaneously the
  duplicate and a hidden permissions problem that a new file does not fix.
- **Written before the first frame, not after.** A file created and then lost to a
  crashed context is worse than none: it exists, it is empty, nobody knows it is
  there.

### Added — the check that catches it mechanically
- Deep links are `figma.com/design/:fileKey/…`, so **comparing every `screens.md`
  frame link's key against the canonical record is a string match**, not a
  judgement. A differing key *is* a second file. This is now the stage-3 gate and
  the audit ladder's **`→F`** seam; if it ever fires twice, it belongs in the host's
  lint, per the repeats-twice rule.

### Changed
- **Canonical record: `docs/ux/foundation.md` → *Design tooling*** — super-ux owns
  that section, it is per-project and it survives every run, which is exactly what
  "the agents always know which file" requires. The brief holds the **decision and
  the authorization** and points at it; it is a record, **not a second registry**,
  and if the two disagree `foundation.md` wins. On a project with no `docs/ux/` the
  brief is canonical instead, and **stage 9 writes the destination into the host's
  own docs** (`conventions.md`) so the next run finds it without asking.
- **Creating** a shared design file joins the outward list beside *editing* one —
  it is the stronger of the two, and it is the one that duplicates.

### Validator
- The shipped intake gate must settle the design destination; a config where stage 0
  never names the team or the file now fails. Proven against a planted defect and
  shipped with a CI negative self-test.

## v1.2.0 — 2026-07-29

The pipeline already knew about Figma — but only second-hand, through super-ux, and
**every one of its own promises had a Figma-shaped hole**. None of these required it
to learn Figma; super-ux owns that completely and keeps owning it.

### Fixed — four holes in the pipeline's own promises
- **The sweep never asked about the design surface.** super-ux asks "Figma or
  text-only" once per project and stores the answer — but that first ask lands
  *mid-run*, in the very run the sweep exists to make uninterrupted. Worse: when the
  Figma MCP is absent, super-ux correctly recommends it and then **continues
  text-only on its own, never blocking**. That is a scope change nobody agreed to —
  a UI feature ships "described" instead of "designed" and no gate says so. New sweep
  row **`3 Design surface`**: Figma on or text-only, is the MCP connected, and *if it
  isn't, ship text-only or stop and connect it?*
- **The single-preflight promise was broken for UI tasks.** `companion-skills.md`
  guarantees ONE block — companions plus the model — so the operator arms the whole
  run in one exchange. The Figma MCP is a companion stage 3 needs, and its check
  happened later, inside the stage. It is now in the matrix and in the preflight
  block, flagged only when the task is user-facing *and* the project designs
  visually (read `docs/ux/foundation.md` → Design tooling first; no record means the
  choice itself is a stage-0 question).
- **The audit ladder had no rung for the frame.** Added as **`F`** — deliberately
  *conditional and parallel*, not a step in the sequence, so `L0→L7` keeps its
  numbering. A frame is **a second statement of the same surface, made in pictures.**
  super-ux's linter proves a frame link exists, is named `SCR-NN/<Screen>/<state>`
  and isn't stale; **it cannot read the picture.** A frame can pass every lint there
  is while promising a retention window, a credit meter or a pricing tier the spec
  never described and the code never built — a rendered claim about the product,
  seen by more people than the spec, and often the version stakeholders believe.
  Compare frames to frames and they agree; compare specs to specs and they agree;
  the defect lives in the seam. Two new seam questions: **`L2→F`** does the frame
  render what the spec says, and **`F→L7`** did what shipped stay matched to it. The
  spec is the contract — name the document you propose to move instead of quietly
  redrawing.
- **Editing a shared design file was missing from the outward list.** Frames are
  read by designers and stakeholders; drawing in one is publishing, not local work.
  It now sits beside deploy, publish, repo-create and opening a PR — the list an
  agent actually reads.

### Added — validator
- **Autonomy-sweep drift guard.** The sweep lives twice: `grill.md`'s table is what
  the agent *reads* while interviewing, `templates/brief.md`'s is what it *writes*.
  A row added to one and not the other is a question never asked, or an answer with
  nowhere to land. The validator now compares the stage numbers the two tables cover
  and fails on a difference. Proven against two planted defects (a stage present
  only in the grill; a stage dropped only from the brief) plus an unmodified control,
  and shipped with a CI negative self-test. **Scope, stated honestly: it catches
  stage-level drift, not row-level** — a row added under a stage number both tables
  already mention passes.

### Changed
- The boundary is now written down in both directions: super-ux owns *how* to design
  (the choice, the MCP preflight, frame naming, the drift linter); task-pipeline owns
  *when to ask, what counts as degradation, and how to check afterwards that the
  picture and the product still say the same thing*.

## v1.1.1 — 2026-07-29

Version bump only — a fresh npm artifact for the v1.1.0 content. **No changes to
the skill, the doctrine, the gates or the installers**; the tree is identical to
v1.1.0. Nothing to re-read, nothing to re-learn.

(npm versions are immutable, so re-publishing the same content needs a new number.)

## v1.1.0 — 2026-07-29

**The pipeline could find a requirement that was named and lost. It could not find
one that was never named.** Every gate compares two things — and a contradiction has
two sides while **an absence has one**. Nothing in a diff between spec and plan
reveals the error path nobody specified, the entity nobody gave an owner, the
failure mode nobody thought of. This release adds the pass that can.

### Added
- **`references/audit.md` — the audit ladder, cross-cutting.** Eight rungs of one
  deliverable (requirement → decision → spec section → contract **and its failure
  behavior** → plan task → change → **executed** test → surface/docs) and, more
  importantly, the **seam between each pair**, each with its own question: did the
  decision reach the spec; does the section say what happens when the contract
  fails; does every contract have a task (stage 4's set-equality covers REQ→task and
  nothing covers contract→task); did the DoD land in the diff; would this test still
  pass with the production code deleted; can a user reach it and does a doc say so;
  and finally — does what shipped satisfy the requirement's own *statement* rather
  than the task's instructions.
- **Stage 10 now opens with the ladder walk, before the coverage table.** An absence
  found there becomes a **new REQ row with its check**, and *then* the table is
  written. Appending after the table is exactly how acceptance goes green over a
  gap. Findings that belong to a lower layer go back to that layer (spec → stage 3,
  plan → stage 4) instead of being patched in place at the last stage.
- **Findings are ordered by seam, never by file.** A file-ordered list reads as
  noise; a seam-ordered one names *which layer of your own process is leaking*,
  which is the part worth knowing.
- **Bottom-up, and that is not taste.** A missing artefact low on the ladder makes
  everything above it meaningless — top-down you spend the pass polishing a surface
  for a contract that does not exist. Bottom-up, the absence is finding #1 and the
  six findings above it collapse into it.

### Added — three rules that stop the audit becoming another loop
- **Every pass changes the axis, not the effort.** A searching loop does not
  oscillate the way an editing loop does — it **converges**, because each pass edits
  the corpus the next pass reads, so the newest edits are always the
  least-reviewed text present and are what the next pass finds. Measured over seven
  passes on a production repository: by pass six, ten of thirteen findings were
  caused by pass five's own fixes, while the raw count still looked healthy. So the
  doctrine requires **two counts per pass** — new findings, and self-inflicted ones —
  and names the crossover as the signal to **rotate the axis**: seams down one
  deliverable, then invariants across deliverables, then one class swept end to end.
- **A class that repeats twice becomes a gate, not a note.** Once is an incident;
  twice is a category, and a category belongs in the host's lint or CI where nobody
  has to remember it. Writing the third instance into the ledger is how a
  mechanical defect class becomes permanent. Wired into the stage-5 fix loop too.
- **What can't be fixed now becomes a ratchet, never a TODO.** The carry-over ledger
  is now defined as a *named, counted set that may only shrink, printed beside every
  gate verdict* — `carry-over: 4 open (was 6) · unresolved: 0`. A TODO is invisible
  until somebody opens the file; a ratchet sits next to the word `PASS` on every
  run, so **"green" never reads as "verified"** — it reads as *"green, and here is
  exactly what was not looked at"*. A ratchet that grew needs one sentence saying
  why.

### Added — the exit criterion that is usually skipped
- **A green result from an unproven check is worth nothing.** A deliverable is not
  audited when somebody has read it; it is audited when every rung has its artefact
  **and every check being relied on has fired at least once against a planted
  defect.** This is `tdd.md`'s iron law — *if you didn't watch it fail, you don't
  know it tests the right thing* — raised from one test to every gate, linter and
  script in the run, and it is now part of the stage-10 gate. Checks written under
  pressure lie in ways that read as success: a predicate that inspects the wrong
  shape, a probe that reads its own over-deletion as a pass, a regex that misses the
  word it searches for. All three pass loudly.

### Changed
- `loop-guard.md` and `audit.md` now state their seam explicitly in both files: the
  loop guard governs loops that **change** things and trips on oscillation; the
  audit governs loops that **look** for things and trips on convergence. Different
  failure, different exit, and an agent reading either one now learns when the other
  applies.
- `tdd.md` names the generalisation of its own iron law; `build.md`'s fix loop gains
  the repeats-twice rule; `templates/carryover.md` documents the ratchet contract.

### Validator
- `references/audit.md` joins the built-in-doctrine set (must exist, must not be a
  stub, must be reachable from `SKILL.md`).
- The shipped acceptance gate must require the ladder walk **and** say that an
  absence becomes a new REQ row — a config where stage 10 only compares the REQ list
  now fails.
- Both guards ship with CI negative self-tests, and both were proven the way this
  release demands: defect planted, check watched failing, defect removed.

## v1.0.0 — 2026-07-28

**1.0.** Eighteen releases in ten days added a stage, a requirement spine, a
decomposition pass and a loop guard; this one adds nothing and instead makes the
whole thing coherent enough to depend on. Every file was read against every other
file, the contradictions between them are fixed, and the repo now carries the
surface a stranger needs before they trust it.

What 1.0 promises: the stage flow (0 intake + 1→10), `pipeline.schema.json`, the
artifact layout in `references/artifacts.md`, and the two install paths are stable.
Breaking any of them means a 2.0.

### Fixed — contradictions between doctrine files
- **Two names for one idea.** `brainstorm.md` told the agent to split an oversized
  task into "sub-projects", each with its own spec→plan→build cycle;
  `decomposition.md` — the file that actually owns the procedure — calls them
  **modules**, cuts them at the end of stage 2, and runs stages 3→10 per module
  against a committed module map. An agent that read the first file ran a
  decomposition the second file's gate could not check. Brainstorm now hands off to
  `decomposition.md` by name.
- **The same split, invented twice.** `planning.md` independently told stage 4 to
  "split the spec into one plan per subsystem" — a second, unrecorded decomposition
  two stages after the one with the gate and the map. A plan now covers exactly one
  spec; a multi-subsystem spec arriving at stage 4 is a missed stage-2
  decomposition and goes back there.
- **A hardcoded `main`.** `build.md` and `review.md` both built the final
  whole-branch review package with `git merge-base main HEAD`, in a pipeline whose
  stage-0 brief records the base branch precisely because it is not always `main`.
  On any repo with a `master`, a `develop` or a stacked base, the final review saw
  the wrong diff. Both now read the brief's base.
- **A five-status set that claimed to have four.** `acceptance.md` listed four
  statuses, declared "there is no fifth status", then named `unknown` in the next
  clause. Reworded so the mechanism is legible: four ways to close, and anything
  that fits none of them is `unknown`, which fails the gate.
- **A version pin on someone else's contract.** The README and `stages.md` both
  pinned super-ux's scenario format at "ux-contract v4" — the exact cross-repo
  version skew this project ported its own doctrine in-house to avoid. Both now
  point at the contract super-ux itself ships, with no version named here.
- **A blockquote where a sentence should be.** In `knowledge-sources.md` the
  precedence chain `code > host docs and ADRs > the wiki > memory` wrapped so the
  second line *began* with `>`, which Markdown renders as a block quote —
  the rule about which source wins was visually broken in the file that defines it.
- **`skills[]` entries that resolve to nothing.** `pipeline.example.json` names
  `task-pipeline:grill` and `host:lint` beside real skills, with no key anywhere for
  the two prefixes. A host copying the example had no way to tell a notional label
  from an installable skill. The convention is now stated in the config and in
  `SKILL.md`: `task-pipeline:<name>` is this skill's own `references/<name>.md`,
  `host:<name>` is the host project's command per `conventions.md`, everything else
  is a real skill. Stage 3 also gained the `/ux` entry point and `/ux-lint`, which
  the doctrine mandates and the config had omitted.
- **A repo tree that had drifted.** `references/artifacts.md`'s map of this
  repository listed `templates/` outside the tree and missed several files.
- A broken ordered list in the Cursor rule (`3a.` is not a list marker) and a
  `references/` index in `SKILL.md` that never mentioned `templates/`.

### Added — the open-source surface
- `CONTRIBUTING.md` — dev setup, the repository layout, and **the nine invariants**
  written out with the failure each one prevents: four-way version sync, the stage
  list living on three machine-checked surfaces, every human-facing description
  having to name the flow's final stage last, no hardcoded vendor model ids, no
  unreachable reference file, no external provider in the default flow, stage 0 and
  stage 10 staying manual, the frontmatter budget, and resolving links.
- `SECURITY.md` — what the executable surface actually is (two installers, a
  validator, two workflows), private reporting with a 72-hour acknowledgement, and
  an explicit scope: doctrine that would lead an agent to exfiltrate secrets, push
  to an unnamed repo or deploy without a go **is** a security bug here.
- `CODE_OF_CONDUCT.md`, GitHub issue forms (bug / doctrine change, with routing to
  super-ux and obsidian-wiki), and a pull-request template whose checklist is the
  list of surfaces that drift.
- `CLAUDE.md` — house rules for any agent working in this repo, which is also what
  this pipeline's own stage-0 harvest reads first: the commands, the branch and
  commit policy, the invariants, and the docs that must be updated in the same
  change. The project now dogfoods the convention it asks of every host.
- **Two validator guards, each with a CI negative self-test:** the open-source root
  files must exist, and `npm test` must actually run the validator. A documented
  check nobody can run is a check nobody runs.

### Changed
- **README rewritten.** Same substance, ordered so it can be read: a one-paragraph
  statement of the problem, a Mermaid diagram of the flow with gate types coloured,
  the gate table, *what you get*, then a quickstart — before the deep sections.
  Configuration, install/update and a documentation map now live in their own
  places instead of interleaved with doctrine.
- Package, marketplace and plugin descriptions rewritten — shorter, and all three
  now say the same thing about the same ten stages.
- npm metadata: a `test` script (`npm test`), a `bugs` URL, `homepage` at the README.
- `.worktrees/` is git-ignored — stage 5 creates them.

> The open-source surface above shipped in v0.18.1, hours earlier the same day;
> it is restated here because it is part of what 1.0 means.

## v0.18.1 — 2026-07-28

Open-source hygiene pass — the repo is public, so the files a first-time
contributor looks for now exist, and the validator keeps them there.

### Added
- `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, issue forms and a
  pull-request template.
- `CLAUDE.md` — house rules for any agent working in this repo: the commands, the
  branch and commit policy, and the invariants that drift most often.
- The validator now requires the open-source root files, with a CI negative
  self-test that deletes `CONTRIBUTING.md` and proves the check fails.

### Changed
- npm metadata: a `test` script, a `bugs` URL, and `homepage` pointing at the
  README. Package, marketplace and plugin descriptions rewritten so all three say
  the same thing about the ten stages.
- `.worktrees/` is ignored — the pipeline creates them during stage 5.

## v0.18.0 — 2026-07-28

The grill stops opening cold. Stage 0 now reads what the project already knows
about the task **before** the first question, checks every answer against it, and
stage 9 updates the same list at the end — the loop the pipeline was missing.

### Added
- **Stage 0 phase 1: the knowledge harvest** (`references/knowledge-sources.md`).
  Before question one, query what the project already knows about *this* task —
  the code, `CLAUDE.md`/`AGENTS.md`, `CONTEXT.md` + `docs/adr/`, `docs/` and
  `docs/ux/`, previous pipeline briefs and their carry-over ledgers, **the
  knowledge wiki when one is installed**, and **any other repository or hosted doc
  system the project names as its docs**. It is retrieval scoped by the task's own
  nouns, not a read of everything: query, follow one hop, stop when the terms
  return nothing new. Nothing is ever fetched on a guess — a doc repo is in scope
  because the project names it.
- **The source ledger** — a required `## Knowledge sources` section in the brief
  (source, what it says about this task, freshness, authority, "stale after this
  run?"). `none found` is a valid, useful row: it tells the next run the search
  happened and came back empty. Silence doesn't.
- **Answers are validated against the harvest** (`grill.md` → *Domain awareness*).
  The cheap win is not re-asking what an ADR already answers. The one that matters:
  **an answer nobody can check is a recollection** — people answer from memory
  about systems they wrote a year ago, and a false premise adopted at stage 0 makes
  every later gate pass honestly on it. So the grill quotes the source instead:
  *"the March ADR says X, you just described Y — has it changed?"* The operator
  **outranks every document, but only out loud** — an override quoted against its
  source is a recorded decision, an unquoted one is an undetected divergence.
  Precedence when sources disagree: **code > host docs/ADRs > wiki > memory.**
- **obsidian-wiki is the recommended knowledge base**
  (https://github.com/ar9av/obsidian-wiki — Karpathy's LLM-wiki pattern), detected
  via `~/.obsidian-wiki/config` or a resolving `wiki-query`/`wiki-update`.
  Installed → queried in the harvest, synced with `wiki-update` at stage 9. Absent
  → the preflight prints `pip install obsidian-wiki` / `obsidian-wiki setup --vault
  <path>` **once** and the run continues. A recommendation, never a gate; a project
  whose `CLAUDE.md` names a different knowledge base wins.
- **Stage 9 closes the loop:** the stage-0 ledger *is* its work list. Every source
  the harvest read gets updated if this run changed or disproved it — including the
  docs the grill already proved stale, which is why those conflicts are logged in
  phase 2 instead of only being settled out loud. Docs living in **another
  repository** are outward: propose the edit and get an explicit go, or carry it
  over with the exact change written down. Never a direct push to a repo the task
  didn't name.
- **Autonomy-sweep row** for doc sources beyond this repo, and whether stage 9 may
  write to them — decided at intake, like every other outward action.
- **Three validator guards, each with a CI negative self-test:** the brief template
  must keep its `## Knowledge sources` section; the stage-0 gate must require the
  harvest *and* its ledger before the interview; the stage-9 gate must name that
  ledger as its work list. A harvest with nowhere to land degrades silently back
  into asking from memory, which is precisely the failure it exists to stop.

## v0.17.1 — 2026-07-28

A full-repo consistency audit. v0.16.0 added a third review verdict and a tenth
stage; several surfaces never heard about either. An agent reads one surface, not
all of them, so a stage that is `three verdicts` in the config and `both verdicts`
in the prompt that actually runs simply produces two.

### Fixed
- **The third review verdict now exists where reviews are actually dispatched.**
  `references/review.md`'s task-review prompt asked for *"two verdicts"* — so the
  REQ-satisfaction verdict the stage-5 gate requires was never returned. It now asks
  for three (spec compliance → **REQ satisfied** → code quality), with the REQ one
  judged against the requirement's quoted statement rather than the task's
  instructions. Same correction in `build.md` (§4.4 and its gate), `planning.md`'s
  plan header, `stages.md` and the Cursor rule.
- **Stage-5's gate now names the ledger harvest.** `build.md`'s gate omitted
  "every parked finding and implementer concern harvested into the carry-over
  ledger" — the one thing that must happen before the scratch workspace is deleted.
- **Three gates in the doctrine files were weaker than the same gates in
  `stages.md`:** `planning.md` didn't state the REQ **set-equality** check (the
  brief→plan seam), `spec.md` didn't require `covers: REQ-…` per section, and
  `brainstorm.md` didn't require every REQ answered by the design or the module map
  approved for a platform. All three now match.
- **Descriptions listed the flow wrong.** npm, the marketplace entry, the plugin
  manifest: `…post-deploy, acceptance, docs/wiki` — eleven items for ten stages,
  with the final stage listed second-to-last. The `/task-pipeline` command's
  description and `SKILL.md`'s frontmatter stopped at docs/wiki and never named
  acceptance at all.
- **Built-in doctrine tables were missing rows** for stage 10 acceptance
  (`SKILL.md`, `README.md`, `companion-skills.md`), stage-2 decomposition and the
  loop guard (`README.md`, `companion-skills.md`) — files that ship, are reachable,
  and were absent from the very tables that say what ships.
- Smaller drift: the Cursor rule's stage 9 dropped the wiki sync; four gate checks
  in `pipeline.example.json` had v0.16.0 sentences concatenated without punctuation;
  `stages.md` wrote `implements:` where the plan format writes `Implements:`;
  `artifacts.md` had the acceptance artifact listed before the spec and the ledger
  attributed to stages `0→9`; the v0.1.0 design snapshot's disclaimer still
  described the live shape as nine stages.

### Added
- **Three validator guards, each with a CI negative self-test**, so this class of
  drift fails instead of shipping:
  1. every human-facing description (npm, marketplace, plugin, `SKILL.md`, the
     command, the Cursor rule, `README.md`) must name the flow's **final stage**,
     and must not list it before the stage it runs after — derived from
     `pipeline.example.json`, not hardcoded;
  2. no shipped surface may say *two/both verdicts* while the dev gate declares
     three;
  3. each stage doctrine file's own `GATE (auto|manual)` must match that stage's
     gate type in the config.

## v0.17.0 — 2026-07-28

Two mechanisms stop being files nobody walks and become operational doctrine: a
platform is cut into bricks before it is specced, and a loop that starts undoing
itself is broken instead of endured.

### Added
- **Decomposition is stage 2's second half**, wired end to end —
  `references/decomposition.md` now reached from `SKILL.md`'s doctrine table, the
  stage-2 gate in `stages.md`, the example config, the Cursor rule, the command and
  the README. A brief that describes a *platform* — several independent
  capabilities, several separately shippable surfaces, REQs no single deliverable
  satisfies — is cut into **modules** before any spec exists: by capability, never
  by layer, and a candidate is a brick only when it is independently specifiable,
  buildable and testable, owns its entities, talks through declared contracts only,
  and can land while leaving the system working. The module map carries build order
  — **walking skeleton first**, then topological, no cycles — with every REQ mapped
  to exactly one module. Single-module work records `single module: <name>`: a
  skipped decomposition is a decision, never an omission.
- **The module dossier** (`spec.md`): for a decomposed platform the spec has nine
  required sections — purpose and boundary, architecture, entities and ownership,
  contracts in and out **with their behavior when the other side is down**,
  business rules in the domain's language, edge and failure cases, UI/Figma chain,
  non-functional limits, and open questions with a decide-by moment. A skipped
  section says why in one line; silence is not a skip.
- **The loop guard binds every repeating loop** — `references/loop-guard.md` is now
  referenced from `SKILL.md`'s cross-cutting rules, a `stages.md` section, the
  stage-5 fix loop, the Cursor rule and the command. Every repeating pass logs one
  line per touched file with the reason that forced it ("cleanup" is not a reason).
  It trips on revert-oscillation, a file edited twice for the same reason, a
  resurrected finding, a third entry into one stage, or two loops editing one file,
  plus hard caps (5 fix rounds per task, 2 re-entries per stage, 3 passes per
  module). On a trip: stop editing, name shape A and shape B with their evidence,
  escalate to the layer that owns the conflict, re-plan the check as an ordered
  checklist with one verification command per item, then go through it one at a
  time. **A higher-layer conflict is never settled inside a lower loop.**
- **Two autonomy-sweep rows** (grill + brief template): platform-or-single-module
  with the deploy cadence it implies, and who signs off acceptance plus where
  deferred REQs are tracked.
- **`conventions.md` gains the issue tracker** stage 10 needs — read the host's
  convention, never invent a tracker, never close a run on "we'll remember it".
- `artifacts.md` gains the module map and the run-level ledger
  (`.task-pipeline/run.md`) the loop guard writes to.

### Tests
- **The stage list is cross-checked across all three surfaces it is published on** —
  `SKILL.md`'s table, `references/stages.md` and `pipeline.example.json`: identical
  ids in identical order, matching names, matching gate types, and every stage in
  `stages.md` carrying a `**GATE (auto|manual)**` line. Drift between surfaces is
  invisible in review and lethal at runtime — a stage manual on one surface and auto
  on another.
- `decomposition.md` and `loop-guard.md` join the stub-rejected doctrine set.
- Three negative self-tests against a mutated copy: a flipped gate type, a removed
  GATE line and a deleted doctrine file each fail the validator.

## v0.16.1 — 2026-07-28

### Fixed
- **v0.16.0 added a tenth stage and left "1→9" in fifteen places** — the skill
  description, the command, the Cursor rule, `stages.md`, `grill.md`, the brief
  template, the example config and the README all still promised nine. The
  package, marketplace and plugin descriptions said "9 gated stages" too, which
  is what npm and the marketplace show. All re-synced to ten, and the plan
  filename now uses the same slug as the brief and the spec.

## v0.16.0 — 2026-07-28

Scope stops leaking. The request becomes an addressable list of requirements, the
ids are traced through every stage, and a new final stage accounts for all of them.

The failure this fixes: every gate up to now asked *"is this artifact good?"* and
none asked *"does this still contain everything that was asked for?"* Scope doesn't
leak inside a stage — it leaks on the **seams**, because brief → spec → plan → task
briefs is four rewrites by a model and nothing compared the lists.

### Added
- **The REQ spine.** The grill's second hard output is a requirement table in the
  brief — one row per *independently verifiable* deliverable, each naming **how it
  is verified** (test name, `file:line`, command + expected output, scenario id). A
  requirement you can't say how to verify is a badly-stated requirement, and gets
  split during the grill rather than discovered at the end. One REQ = one
  deliverable, not one per sentence: an inflated table is ignored, and an ignored
  table protects nothing.
- **Traceability through the run.** Spec sections carry `covers: REQ-…`; plan tasks
  carry `Implements: REQ-…`; the implementer's task brief quotes the requirement
  statement **verbatim**, so it optimises the requirement and not just the
  instruction; the review rubric gains a verdict beside spec-compliance and
  code-quality — **does this satisfy its REQ?**
- **Stage 10 — Acceptance** (`references/acceptance.md`, manual gate). Closes the
  circle: every REQ gets `verified` / `partial` / `deferred` / `dropped`, written to
  `specs/<topic>-acceptance.md`. `verified` **requires evidence** — a passing test
  name, a `file:line`, a command and its output. "Done" without evidence is
  downgraded to `partial`, never upgraded. Then the operator is asked the closing
  question out loud, list in hand: *here's what you asked for, here's what shipped,
  here's what's deferred and where it lives — what's missing?* Asked even when the
  table is green. Manual by design: an automated check can prove the table is
  well-formed; only the person who asked can confirm it is what they asked for.
- **The carry-over ledger** (`templates/carryover.md`) — append-only, seeded at
  stage 0, written by every stage, read in full at stage 10. Implementer concerns
  and parked review findings are harvested into it before the scratch workspace is
  deleted. The rule: **deferred out loud is forgotten** — a row with no home
  (issue, backlog, or an agreed `dropped`) blocks the acceptance gate.

### Changed
- **The brief→plan seam is now mechanical.** Stage 4's gate is **set equality**
  between the brief's REQ ids and the union of `Implements:` across plan tasks. A
  non-empty difference fails the gate and is reported as the explicit list of
  dropped requirements — a comparison, not a judgement call.
- **No silent narrowing.** The REQ list is frozen once confirmed: adding mid-run is
  free, **removing or narrowing needs the operator's explicit agreement**, recorded
  in the ledger. Quietly restating the task smaller is the subtlest loss, because
  every later gate then passes honestly on a task that shrank without anyone
  deciding it should.
- **Gates tightened** — stage 0 requires the REQ table and a seeded ledger; stage 2
  requires the design to answer every REQ (or an operator-agreed drop); stage 3
  requires `covers:` on every section; stage 5 harvests concerns into the ledger;
  **stage 7 refuses to deploy while any REQ is still `open`** (a `partial` ships only
  with explicit acceptance — a gap is cheapest to close before it ships).

### Fixed
- **`decomposition.md` and `loop-guard.md` shipped unreachable.** Both linked only
  to each other; nothing in `SKILL.md` pointed at either, so under progressive
  disclosure an agent would never load them — two contracts that existed, passed
  every check, and were dead context. Wired into the doctrine table (stage 2 for
  decomposition, cross-cutting for the loop guard), and the validator now walks the
  link graph from `SKILL.md` and fails on any reference nothing reaches.

### Tests
- `references/acceptance.md` joins the built-in doctrine set (stub-rejected);
  `templates/carryover.md` required; the brief template must carry
  `## Requirements`, a `REQ-NNN` row and the verification column; the shipped flow's
  last stage must be `acceptance` with a **manual** gate whose check demands
  evidence; the plan gate must state the set comparison.
- Nine new invariants, each verified to fail on a broken copy; four added to CI as
  negative self-tests.

## v0.15.0 — 2026-07-28

Coherence pass over the v0.13.0 port: three contradictions resolved, three gaps
closed, and the config's gate text re-synced with the doctrine.

### Fixed
- **Model policy contradicted itself.** `build.md` and `review.md` told the final
  whole-branch review to run "on the most capable model available" while
  `model-tiering.md` promises **one** model per run. Both now default to the run's
  confirmed model; when the run sits below the top tier, escalation for that single
  review (and for fix-loop rounds 4–5) is **offered out loud**, never switched
  silently, and only the operator's recorded override map authorizes a cheaper tier.
- **Parallel groups were planned and then forbidden.** `planning.md` mandates
  dependency-ordered parallel groups with exclusive file ownership; `build.md` said
  "never dispatch implementers in parallel". New §4.2 states the real rule: default
  sequential, fan out only when the tasks share a group, own disjoint files **and**
  each implementer gets its own worktree; integrate the worktrees one at a time; any
  merge conflict means the plan's ownership was wrong — fall back to sequential and
  record it. The fix loop never fans out.
- **Scratch dirs could land in a task's diff.** The isolation snippet now ignores
  **and commits** both `.worktrees/` and `.task-pipeline/` before anything is
  created.

### Added
- **Stage 5 now ends with integration.** Sync with the base branch, re-run the full
  suite on the merged result (green-in-isolation is not green), land it the
  project's way — merge, or a PR, which is outward and needs a go — never
  force-push a shared branch, never land on `main` when the brief forbids it, then
  remove the worktree. Stages 7–9 lint, deploy and document the integrated result,
  so "leave it unmerged" is allowed but must be recorded. The stage-5 gate, the
  stage table, the Cursor rule and the example config carry the new condition.
- **Inline execution mode.** A harness without subagents (or a plan too small to be
  worth dispatching) runs the same loop inline: same isolation, ledger, TDD and
  review rubric applied to your own diff — declared out loud, since a self-review is
  weaker evidence than a fresh reviewer's. Replaces the capability that
  `superpowers:executing-plans` used to cover.
- **Grill + brief sweep row for integration** — how the branch lands (merge / PR +
  approver / "leave it") and whether parallel fan-out is wanted, so stage 5 never
  stops to ask.

### Changed
- The implementer contract spells the TDD loop out inline instead of pointing a
  zero-context subagent at a file it can't resolve, and the plan header no longer
  cites a skill-internal path.
- `pipeline.example.json` gate text for stages 4, 5 and 6 re-synced with
  `references/stages.md`; stage 4's gate now also names type/name consistency and
  the per-task DoD.
- `review.md` defines `$WORKSPACE` where it first uses it; `build.md` §4 subsections
  renumbered after the insert.

## v0.14.0 — 2026-07-28

### Fixed
- Skill front-matter was **1039 characters**, over the 1024 canon limit, and the
  validator did not check it. Description tightened to 996 and the limit is now
  enforced.

### Changed
- Triggers restructured English-first — `'run this through the pipeline' /
  'прогони по конвейеру'` — in both the skill and the Cursor rule.
- README is English-only, with a plain statement of what the pipeline gives you
  and an author/links block.

### Added
- Validator enforces the description canon: `Use when` opening, Russian trigger
  aliases present, front-matter under 1024 characters.

## v0.13.0 — 2026-07-28

The last external dependency is gone. Every stage now runs on doctrine that ships
inside the skill — the pipeline installs and runs with nothing else present.

- **superpowers is no longer a prerequisite.** The preflight no longer resolves
  `superpowers:*`, the "install this or stop" branch is deleted, and no stage can
  fail because a companion plugin is missing. `Prerequisites` in SKILL.md and the
  README now read "none required".
- **Six new built-in references carry stages 2→6:**
  - `references/brainstorm.md` — stage 2: read the brief first, explore, scope-check
    for decomposition, one question at a time, 2–3 approaches with a recommendation,
    YAGNI, design approved section by section. The **hard gate** (no code, no
    scaffolding before approval, including on "obviously simple" tasks) is explicit.
  - `references/spec.md` — stage 3: UX-track order, what the spec must lock (types,
    schemas, signatures, file layout) plus the **Global Constraints** block stages
    4–5 consume verbatim, the self-review pass, the operator-review gate.
  - `references/planning.md` — stage 4: zero-context task format, dependency graph,
    parallel groups with exclusive file ownership, required plan header and task
    structure, the no-placeholders list, the self-review checklist.
  - `references/build.md` — stage 5: worktree detection (submodule guard, native
    tool first, ignored-directory check, baseline tests), a git-ignored ledger at
    `.task-pipeline/build/<plan>/progress.md` that survives compaction, the
    file-based dispatch contract, the four implementer statuses, the five-round fix
    loop with its breaker and adjudication rules, and the single final fix wave.
  - `references/review.md` — the review rubric (spec compliance, correctness,
    constraints, test honesty, degradation, boundaries, security, docs-same-change),
    severity ladder, controller rules ("never pre-judge a reviewer"), and the three
    reviewer prompts. External helper scripts are replaced by plain git commands, so
    the doctrine works on any agent.
  - `references/tdd.md` — stages 5–6: the iron law, red/green/refactor with both
    mandatory verifications, honest-test rules, the stage-6 full-suite gate, and the
    rationalization table.
- **Ported, not depended on.** Stages 2–6 are adapted from `brainstorming`,
  `writing-plans`, `using-git-worktrees`, `subagent-driven-development`,
  `test-driven-development` and `requesting-code-review` in
  [obra/superpowers](https://github.com/obra/superpowers) (MIT) and rewritten for
  this pipeline's stages, gates, artifacts and single-model policy. `LICENSE` gains
  a second *Third-party* section with Jesse Vincent's copyright notice covering the
  six files.
- **Optional bridge, not a dependency.** An operator who already runs an equivalent
  skill set can substitute it on stages 2/4/5/6 via `pipeline.json` → `skills[]`.
  Nothing detects, recommends or waits for it; the gates still govern; providers are
  never mixed inside one stage.
- **Config:** `pipeline.example.json` stages now name `task-pipeline:brainstorm`,
  `task-pipeline:spec`, `task-pipeline:plan`, `task-pipeline:build` +
  `task-pipeline:review`, and `host:test-runner` + `task-pipeline:tdd`.
- **Every channel updated** — SKILL.md (built-in doctrine table, stage table,
  references list), `references/stages.md`, `references/companion-skills.md` (matrix
  split into built-in vs optional, superpowers moved to a struck-through
  "not a dependency" row), `references/artifacts.md` (new files in the repo map, the
  `.task-pipeline/` scratch workspace, and a note that `docs/superpowers/` is a
  retained directory *name*, not a dependency), the `/task-pipeline` command, the
  Cursor rule (now carrying the design gate, plan format, build loop and TDD rules
  inline) and the README in both languages.
- **Validator:** requires all six doctrine files and rejects stubs (<1.5 KB), and
  fails the build if the shipped default flow names an external provider
  (`superpowers:*`, `grill-me`, `grilling`) in any stage's `skills[]`.
- **Artifact paths unchanged** — briefs, specs and plans still live under
  `docs/superpowers/{specs,plans}` so existing projects need no migration; the name
  is now documented as historical convention only.

## v0.12.0 — 2026-07-27

The grill stops being someone else's skill. It is ported in, in full, and gains
the domain-awareness half it was missing.

- **The intake grill is now BUILT IN — zero external dependency.** New
  `references/grill.md` carries the whole doctrine: the interview loop, domain
  awareness, the autonomy sweep and the output contract. No companion skill to
  install, no provider to resolve, no fallback path, no version skew with someone
  else's repo. `grill-me` / `grilling` are gone from the companion matrix,
  the preflight block and every channel's docs.
- **Ported from [mattpocock/skills](https://github.com/mattpocock/skills)** — the
  `grilling` / `grill-with-docs` interview loop and its domain discipline, MIT,
  adapted to this pipeline's flow. `LICENSE` gains a *Third-party* section with
  Matt Pocock's copyright notice covering the three affected files.
- **New: domain awareness during the grill.** The grill now reads the project's
  own `CONTEXT.md` / `CONTEXT-MAP.md` / `docs/adr/` and holds the operator to
  them — challenging terms that conflict with the glossary, sharpening vague or
  overloaded words into canonical ones, stress-testing relationships with concrete
  edge-case scenarios, and surfacing contradictions between the code and what was
  just said. Resolved terms are written to `CONTEXT.md` inline as they land, never
  batched.
- **New: ADR discipline.** An ADR is offered only when a decision is hard to
  reverse **and** surprising without context **and** the result of a real
  trade-off; any one missing, skip it. Files are created lazily, numbered
  sequentially in `docs/adr/`.
- **New templates** `templates/context.md` and `templates/adr.md` — the formats
  those two artifacts follow, shipped on every install channel alongside
  `brief.md`. `references/artifacts.md` now maps `CONTEXT.md` and `docs/adr/` into
  the canonical layout.
- **Validator:** requires `references/grill.md` and all three templates; the
  broken-relative-link check now strips fenced code blocks first, so illustrative
  paths inside examples stop being false failures (verified it still catches real
  broken links outside fences).

## v0.11.0 — 2026-07-27

The intake grill becomes mandatory, autonomy becomes something the grill actively
buys, and the model stops being a hardcoded per-stage tier list.

- **Stage 0 is now MANDATORY — the stage, not a particular skill.** No "clear
  enough task" exemption, no starting stage 1 without a committed,
  operator-confirmed brief (the entry-from-super-ux short-circuit remains the one
  sanctioned bypass, and still demands a scope confirmation). The **provider** is
  what's swappable: `grill-me`/`grilling` when that chain resolves, otherwise the
  orchestrator's own grill loop — both implement the same **grill contract**, and
  the loop is explicitly no longer described as a "fallback".
- **Grill-provider reality documented.** `grill-me` typically ships
  `disable-model-invocation: true` (so the orchestrator can't call it — the
  operator runs `/grill-me`) and is usually a thin wrapper delegating to
  `/grilling`; if that delegate doesn't resolve the chain is dangling and the
  built-in loop runs. The install line was also wrong — corrected to
  `/plugin marketplace add alirezarezvani/claude-skills` →
  `/plugin install engineering-advanced-skills@claude-code-skills`, with
  `npx skills add mattpocock/skills` noted as the upstream origin.
- **New: the autonomy sweep.** The grill no longer only resolves the *task*; a
  mandatory pass walks stages 1→9 and pre-resolves everything that would otherwise
  interrupt the run — docs sources, branch/tracker policy, the test command and
  what "green" means, the lint command, deploy target + release toggle + deploy
  authorization, log/health locations, docs and wiki targets, the model. Each row
  gets an answer or an explicit "stop and ask here"; an unasked question is a
  scheduled interruption. Stages 5–9 read the brief instead of asking.
  `templates/brief.md` gains the matching `## Autonomy` table.
- **Deploy authorization has a hard floor.** The brief can carry a standing
  authorization for the manual stage-7 gate **only if it is specific** (named
  target + named preconditions). A vague "just do everything" does not authorize an
  outward, irreversible action.
- **Model policy replaces model tiering.** One model for the whole run, confirmed
  **once at preflight** instead of a reminder at every stage boundary. Default
  recommendation: *the most capable reasoning model the environment offers* — a
  **tier, not a string**. Vendor ids are gone from everything shipped: they go
  stale as generations ship and the operator may be on another provider entirely.
  Stage configs use provider-agnostic tokens (`default` / `inherit`), resolved at
  runtime; stage-5 subagents are pinned to the confirmed model; an unavailable tier
  degrades honestly instead of blocking.
- **Validator gains four enforced invariants** (each with a CI negative self-test
  proving it can fail): no hardcoded vendor model id anywhere shipped (skill,
  references, cursor rule, command, README); stage `model` must be a
  provider-agnostic token; the intake-grill gate must stay `manual` and declare
  itself mandatory; `templates/brief.md` must keep its autonomy sweep.
- Docs realigned across every channel — SKILL.md, `references/stages.md`,
  `references/model-tiering.md`, `references/companion-skills.md`,
  `pipeline.schema.json`, `pipeline.example.json`, the `/task-pipeline` command,
  the Cursor rule, and the README in both languages.

## v0.10.0 — 2026-07-25

Review pass — doc drift and a distribution defect found by an adversarial audit.

- **FIX: the stage-0 brief template never reached 3 of 4 install channels.**
  `templates/brief.md` sat at the repo root, outside the plugin source, so the
  skills CLI / npx / install.sh installs had no such file while `stages.md` told
  the agent to seed from it. Moved to
  `plugins/task-pipeline/skills/task-pipeline/templates/brief.md` — inside the
  skill dir, so every channel ships it.
- **FIX: stale super-ux chain in `pipeline.example.json`.** Stage 3 still listed
  only `ux-foundation` + `ux-scenarios`; it now runs the current chain
  (`/ux` → `ux-foundation` → **`ux-flows`** → `ux-scenarios` → **`/ux-lint`**),
  matching SKILL.md and `stages.md`. Stage-4 gate now also names `SCR-` screens.
- **FIX: README documented the old chain** in both languages, and recommended the
  skills CLI for Claude Code (which shadows the plugin). Both corrected; multiple
  agents now shown as repeated `--agent` flags.
- Description now opens with "Use when …" per canon. `ux-contract` stamp updated
  v2 → v4. Model tiering moved to the current Opus generation (`claude-opus-5`).
- README gains npm / CI / license badges.

## v0.9.0 — 2026-07-23

Full structural parity with the sibling `super-ux` per the ssheleg skill canon
(make-skill): the Cursor channel and a templates dir were the last gaps.

- **Cursor channel.** New `cursor/rules/task-pipeline.mdc` — a self-contained,
  agent-requested rule (`alwaysApply: false` + a trigger `description`, no external
  links so it survives being copied into any project) that carries the full
  intake-grill + 9-stage discipline and the super-ux recommendation. Install
  globally via `npx skills add ssheleg/task-pipeline --agent cursor --global`, or
  copy per project into `.cursor/rules/`.
- **Templates dir.** New `templates/brief.md` — the stage-0 intake-brief skeleton
  this plugin seeds into `docs/superpowers/specs/…-brief.md` (create-if-absent,
  never overwrite), plus `templates/README.md` mapping template → destination →
  stage. Spec/plan and `docs/ux/*` skeletons remain owned by superpowers / super-ux.
- **Validator + packaging.** The validator now checks every `cursor/rules/*.mdc`
  has `description` + `alwaysApply` frontmatter and that `templates/brief.md`
  exists; `package.json` `files` ships `cursor` and `templates`. All prior gates
  (four-way version sync, config conformance, gate types, release shape, links)
  retained.
- **Docs.** README gains a Cursor install block and an "Updating everywhere" table
  (one channel per agent — the plugin+plain duplicate caveat spelled out);
  `references/artifacts.md` and stage 0 reference the brief template.

## v0.8.1 — 2026-07-23

- Docs consistency: the SKILL.md super-ux intro now lists the full current chain
  (`/ux`, `ux-foundation`, `ux-flows`, `ux-scenarios`, `/ux-lint`) instead of the
  pre-flows subset, matching the stage-3 table and `companion-skills.md`. Wiki
  synced to the current architecture.

## v0.8.0 — 2026-07-23

Project-configurable release automation, super-ux embedding refreshed to its
current chain, a locked artifact structure, a companion-skills preflight, and a
full contradiction sweep.

- **Release automation — project-configurable & individually toggleable.** New
  optional `release` block in `pipeline.schema.json` (master `enabled` toggle,
  `trigger`, project-defined `steps`, `verify` smoke-checks) with the repo's own
  config in `pipeline.example.json`. Reference implementation
  `.github/workflows/release.yml` is **off unless armed** per repo via the
  `RELEASE_ENABLED` variable; when on it validates the tag ↔ manifest version,
  cuts a GitHub release from the CHANGELOG, and smoke-tests `npx` from a clean
  checkout — closing the previously-manual post-deploy gap. Validator shape-checks
  the block and enforces that `enabled:true` ships the workflow.
- **super-ux embedding updated to super-ux's current chain.** The stage-3 UX
  track now walks `/ux` → `ux-foundation` (WHY) → `ux-flows` (flows + `screens.md`,
  Figma frames) → `ux-scenarios` (WHAT) → **`/ux-lint`** (`docs/ux/lint.py`, must
  pass), reflecting super-ux ≥0.17 (flows/screens layers, linter, Figma). The
  linter is wired into stage 7 (lint) and stage 9 (same-change), and stage-4 DoD
  now carries `SCR-` screens alongside scenario IDs.
- **Entry-from-super-ux short-circuit.** When launched *from* super-ux (its `/ux`
  hand-off, UX chain already built), stage 0 detects the existing validated
  chain/plan and **skips the grill + UX rebuild** — it verifies (`/ux-lint`
  green), confirms scope in one line, and resumes at the first stage with real
  work. super-ux skills are treated as idempotent (reuse, never rebuild).
- **Companion-skills preflight.** New `references/companion-skills.md`: a matrix
  of what powers each stage (superpowers, super-ux, grill-me, context7,
  wiki-update) with install lines and a preflight recommendation block emitted
  before stage 0, so the operator can arm the full flow up front. super-ux install
  lines are surfaced the moment a UI task is detected.
- **Locked artifact structure.** New `references/artifacts.md` fixes the canonical
  `docs/superpowers/{specs,plans}` + `docs/ux/*` layout, the stage→artifact map,
  and this repo's own structure — so every stage writes to the same place.
- **Contradiction sweep.** Manifest descriptions (marketplace/plugin/package) and
  the "9 stages" wording in README + SKILL.md now account for stage 0; the v0.1.0
  spec/plan carry *historical snapshot* banners; model tiering marks 0–4 Fable;
  `conventions.md` covers the super-ux linter and the release block.

## v0.7.0 — 2026-07-23

Front-loaded **intake grill** (stage 0) + super-ux promoted to a recommended,
auto-detected workflow for any user-facing task.

- **New stage 0 — Intake grill (Fable, manual gate).** Before any technical work,
  the pipeline interviews the operator relentlessly — one question per turn, a
  recommended answer with each, exploring the codebase/docs before asking — until
  every decision branch is resolved and locked into a committed **task brief**
  (`docs/superpowers/specs/…-brief.md`). This expands a one-line request into a
  complete input so stages 1→9 run autonomously (only the built-in gates pause).
  Inspired by [Matt Pocock's grill-me](https://github.com/mattpocock/skills);
  uses the `grill-me` / `grilling` skill if it resolves, else a built-in grill
  loop (no hard dependency). The 5 grill rules + stopping condition are embedded
  in `references/stages.md`.
- **super-ux recommended for ANY user-facing task.** The stage-0 grill detects a
  UI surface (web/mobile/CLI/TUI) early and surfaces super-ux immediately: **use
  it if installed**, otherwise print the install line on the spot
  (`/plugin marketplace add ssheleg/super-ux` → `/plugin install super-ux@super-ux`,
  or `npx skills add ssheleg/super-ux`). The stage-3 UX track (`/ux` →
  `ux-foundation` CJM → `ux-scenarios`) is unchanged; the spec gate still requires
  it for UI tasks.
- **Docs synced:** SKILL.md gains the intake overview, a strengthened super-ux
  block (recommended / use-if-installed / install-now) and an optional grill-me
  note; stages table + `pipeline.example.json` gain stage 0; model tiering marks
  0–4 as Fable; the `/task-pipeline` command and README (EN + RU) describe the
  grill-first flow.

## v0.6.0 — 2026-07-23

Typed gates + generic pipeline contract (merged the good ideas from the `os`
branch onto main, **keeping** the v0.5.0 UX track, the npm installer, and CI).

- **Typed gates:** every gate is now tagged `auto` (the orchestrator verifies the
  check itself, pass/fail) or `manual` (wait for the operator's explicit go).
  SKILL.md gained a **Type** column; `stages.md` tags each gate; SKILL.md's
  *How to run* spells out honoring the type (an auto gate never substitutes for a
  required manual approval). Default assignment: 2/3/7 manual, the rest auto.
- **Generic config contract:** new **`pipeline.schema.json`** (universal contract —
  ordered `stages[]`, each with `skills[]` + `gate{type,check}`; no fixed stage
  count, no baked-in skills) and **`pipeline.example.json`** (this plugin's own
  9-stage flow as config, UX track included). New *Bring your own skills* section:
  a host project copies the example to `pipeline.json` and rewrites it with its
  own stages/agents/gate-types.
- **Validator:** checks the schema is well-formed and the example conforms — a
  dependency-free shape check (states unique, `skills[]` non-empty, `gate.type` in
  {auto,manual}, `gate.check` present) plus a full `jsonschema` pass when the
  library is available. All prior checks (four-way version sync, command
  frontmatter, relative links, npm bin) retained.
- **Retained from main (not regressed by the merge):** the super-ux UX track
  (stage-2 UI detection, stage-3 `/ux`→`ux-foundation` CJM→`ux-scenarios`,
  scenario IDs in stage-4 DoD), `bin/task-pipeline.js` + `package.json`, and the
  CI workflow with its negative self-test.

## v0.5.0 — 2026-07-20

UX track: scenario-first design for user-facing tasks, built on
[super-ux](https://github.com/ssheleg/super-ux).

- **Stage 2 (Brainstorm)** now includes a mandatory **UI detection** check —
  records whether the task touches a user-facing surface (web/mobile/CLI/TUI);
  the verdict arms the UX track and is part of the stage gate.
- **Stage 3 (Spec)** gains a conditional **UX track that runs before the spec**
  (and therefore before any plan): `/ux` setup check → `ux-foundation`
  (personas, JTBD, **customer journey maps**, user stories) → `ux-scenarios`
  (usage scenarios drafted + validated per ux-contract v2, traced to
  foundation). Spec must embed the UX layer: scenario IDs, CJM stages served,
  applicable UX patterns/quality bars. Gate extended accordingly; super-ux
  missing on a UI task → install instructions + stop.
- **Stage 4 (Plan)** gate extended: UI tasks name the scenario ID(s) they
  implement; DoD includes satisfying them.
- README (EN + RU): UX track section; super-ux added to prerequisites.

## v0.4.0 — 2026-07-19

npm installer.

- **`bin/task-pipeline.js`** — zero-dependency Node installer CLI (mirrors
  `install.sh`: skill → `~/.claude/skills/task-pipeline`, command →
  `~/.claude/commands/`; idempotent, overwrite only behind `--force`).
- **`package.json`** — package name **`task-pipeline-skill`** (unscoped
  `task-pipeline` is taken on npm); bin command stays `task-pipeline`;
  `files` whitelist ships `bin` + `plugins`. Works without npm publish via
  `npx github:ssheleg/task-pipeline`; after publish also `npx task-pipeline-skill`.
- **Version sync is now four-way** (marketplace.json, plugin.json,
  package.json, CHANGELOG top entry) — validator enforces, plus checks the
  bin entry resolves and the files whitelist ships the skill sources.
- **CI:** `node --check` + a functional install run (fresh → rerun-skip →
  `--force`) against a fake `$HOME`.

## v0.3.0 — 2026-07-19

Packaging/tooling alignment with the ssheleg skill-repo canon (make-skill).

- **CI:** `.github/workflows/validate.yml` runs the structural validator on every
  push/PR, plus a **negative self-test** — corrupts a copy of the repo and expects
  the validator to FAIL (a validator that can't fail is decoration) — and a
  `bash -n` syntax check of `install.sh`.
- **Validator hardened:** now also enforces command frontmatter
  (`description` + `argument-hint`), **CHANGELOG top-entry version sync** with the
  manifests, and resolution of every relative markdown link in the repo.
- **`install.sh` is idempotent:** reruns skip already-installed skill/command;
  destructive overwrite only behind `--force` (never silently `rm -rf`s an
  existing install).
- **`/task-pipeline` is an idempotent entry point:** detects an existing pipeline
  TaskList and resumes from the first incomplete stage instead of restarting.
- **README:** added the `npx skills add ssheleg/task-pipeline` install path
  (vercel-labs skills CLI, 70+ agents) and a closing Russian section.

## v0.2.0 — 2026-07-18

- Added a dedicated **Tests** stage (new stage 6, model Opus) between Dev and
  Lint/deploy: writes tests for new functionality, updates/repairs existing tests
  touched by the change, and adds edge-case + failure-path coverage.
- Hard **full-suite-green gate before deploy** — the deploy stage now requires both
  lint clean and the whole suite green; never advances on a red or partial run.
- Pipeline grew 8 → 9 stages; deploy/post-deploy/docs renumbered 7/8/9. Model
  tiering: Fable 1–4, Opus 5–6, inherit 7–9. Docs/tables/references synced.
- Added a real `/task-pipeline` slash command (`commands/task-pipeline.md`);
  `install.sh` now installs it to `~/.claude/commands/` alongside the skill so the
  command works for the plain-skill path too.
- Validator hardened: enforces marketplace↔plugin.json **version sync** and the
  presence of the command file.

## v0.1.0 — 2026-07-18

Initial release.

- Thin orchestrator skill that runs a task through 8 gated stages (docs study →
  brainstorm → spec → plan → subagent build → lint/deploy → post-deploy log check
  → docs/wiki sync), built on the [superpowers](https://github.com/obra/superpowers) skills.
- Hybrid distribution: Claude Code plugin/marketplace + plain `~/.claude/skills` copy.
- Soft per-stage model tiering (Fable stages 1–4, Opus stage 5, inherit 6–8) — reminder only.
- Generic-portable: stages 6–8 read the host project's `CLAUDE.md` conventions with detection fallbacks.
- Structural validator (`test/validate.py`); spec + plan under `docs/superpowers/`.
