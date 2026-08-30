# Changelog

## v1.79.1 — the probe that a healthy release disarmed

The first round of `v1.79.0` failed in the release job on the
mentioned-vs-declared probe — not because that guard regressed, but because
v1.79.0 was the first release in seven to carry a run stamp, which emptied the
trailing set the probe's mutation lived in. A plant that inherits its
precondition from repository history switches itself off the moment the history
improves; the healthiest possible release is exactly what disarmed it.

The plant now creates its own precondition: it un-stamps every release newer
than the newest declared tag — matching the stamp-row shape, because the first
repair matched "any line naming the sha" and deleted a standing instruction's
`Fired at` cell instead, leaving the stamp intact and the probe green over
nothing — mentions those releases unbolded in the gap section's prose, and then
un-bolds the declarations. Watched both ways on the tagged tree: the correct
guard refuses (8 trailing releases named nowhere), and a deliberately regressed
guard that reads mentions as declarations accepts.

**`v1.79.0` is a dead tag.** Its round shipped nothing — the suite failed before
the release step, publish was skipped, npm never saw it — and the tag ruleset
forbids deleting the tag, so it stays pointed at a tree whose own release suite
refuses it. The version is burned, not reused: this release carries the whole
v1.79.0 payload below, plus the probe repair.

Guards: 417 → **417** — the repaired plant changed shape, not count.

## v1.79.0 — the gate that could not see, and the example that disarmed it

Four defects in the release machinery, each demonstrated live before it was
fixed, plus the two commits that had been sitting on `main` unreleased — one
version string was serving different trees through different channels.

**A blind release gate now fails closed.** `printf '' | release-gate.sh` exited
0 with no output, with a run in flight — an empty or unparseable hook payload
was a silent skip, so the gate allowed every release for as long as its stdin
plumbing was broken. That is the exact shape this repository's own retro names:
a component that never receives its input fails open and is indistinguishable
from approval. With a ledger present the gate now refuses (exit 2), names the
payload failure and the next step, and appends an `event: gate-blind` line to
the ledger so the blindness survives the refusal scrolling away. With no run in
flight it stays silent, as before — installing the plugin still changes nothing
in an ungoverned repository.

**A green lint stage can no longer stand in for the tests stage.** The stage
scan took the first stage that was declared `tests` *or* merely carried a gate
command — so a lint stage declared before the tests stage captured the gate,
and its green observation released a tag with the suite never run. The scan is
two-pass now: a stage the project declared as `tests` outranks any stage that
happens to carry a command. The observer had the same first-match break — only
the first command-bearing stage was ever recorded — and now records every
declared command under its own stage id, so the real suite's runs leave the
trace the release gate corroborates against.

**`npm run publish` is a project's script, not the registry act.** `"publish"
anywhere in npm's argument list` classified it as `npm publish`; the subcommand
must now be the first non-flag token. Fail-closed overmatch is still overmatch —
a gate that fights an ordinary script daily is a gate that gets removed.

**The build gate now fires on the flow this plugin ships.** It matched
`state == "build"` while the shipped `pipeline.example.json` names its build
stage `dev` — the canonical config, copied verbatim per its own note, disarmed
the hook it ships beside. The declaration path now matches `build` or `dev`,
mirroring the hook's own ledger fallback, and the fixture loads the example
unmodified so the two cannot drift apart silently again.

**The example no longer arms a loop its own note calls off, and no longer
teaches the retro deadlock.** `run.loop.mode` was `dynamic` under a `_run_note`
saying "shipped explicitly OFF" — every project copying the example verbatim
armed the loop. It is `off` now, with queue, arm and command kept as
documentation of the shape. And stage 10's check ordered "prune before you add …
then stamp", which is the deadlock the retro doctrine records: the
cold-retirement trigger reads the stamp, so a prune placed ahead of it can never
run on real data. The check now orders stamp → prune → entry and carries the
sixty-day cold clause the doctrine already had.

**Three stage-0 surfaces stopped telling the run to read the uncapped log in
full.** `templates/retro.md`, `references/knowledge-sources.md` and
`templates/brief.md` each instructed reading the retro's Recent log end to end —
contradicting the retro's own header, measured at 74% of the file with nothing
capping it. All three now say what the command surface already said: standing
instructions and run stamps are read in full because they are bounded by
construction; the Recent log and the archive are queried by the task's nouns.

**Also in this release, previously on `main` with no section here:**
`references/prioritisation.md` — the impact ladder that dominates (a gate, not a
factor: confidence × ease orders within a rung and never across one) with the
operator above it, and `references/stages.md`'s note on what a stage that
produces user-facing text owes. Both shipped commits now share a heading with
the version that carries them.

**And this file itself is repaired:** the `# Changelog` H1 sat below five
version sections with an unheaded block attached — the split half of v1.78.0's
own entry, orphaned when the section was inserted above the title instead of
below it. The H1 leads the file again and the orphan is back in its section.

Guards: 413 → **417**. Four new plants, one per gate fix — a blind gate reverted
to skip, the two-pass scan collapsed to first-match, the npm overmatch restored,
the build-state match narrowed back — each watched failing against the fixtures
before it shipped. `test/negatives.py`'s floor moved with the count, in this
change.

## v1.78.4 — the channel that sends the installs, on npm too

- The `skills.sh` badge and the canonical `homepage` reached GitHub in the previous cycle and stopped
  there: npm serves the README and the metadata from the last **publish**, so the package
  page still showed a badge-less README and a homepage pointing at GitHub.
  This release carries both across.
- No behaviour changes. Cut because a change that lands on `main` and never publishes is a
  change the package's own readers cannot see.

## v1.78.3 — the shared seam is explicit

Both shared validators now state `diverges: none`, completing the umbrella
mechanism contract.

## v1.78.2 — the router and the shared mechanisms agree with the umbrella

The description restores the exact `the full cycle` carrier used by the family
router. The eval and social-preview validators now declare their umbrella-owned
shared mechanisms.

## v1.78.1 — one discovery contract from intake to release

The description now starts with the family's `Use when` shape while preserving
both routing boundaries and the explicit `Not for:` clause; its working headroom
is recomputed and gated. Portable trigger and behavior evals, a generated social
preview, and a one-command README viewport now ship. CI adds the pinned house
audit and the eval validator's planted failure; the existing self-observed suite
remains labelled separately from blind model evidence.

## v1.78.0 — the run names the standard, not a person

The banner the pipeline prints before its first question read *"Running **Proof of
Done** by Sergey Sheleg"*, and the sign-off repeated the attribution. A run should
tell the operator which standard the output will be held to; whose name is on the
standard is not what the work will be measured by.

Both lines now carry the title alone, and the sign-off — which prints only after
every gate has closed — carries the two addresses instead:

    — **Proof of Done**
    https://github.com/ssheleg/sshlg-skills · https://skills.sshlg.me

The rule around it is unchanged and is the point: the sign-off comes **after** the
work, never instead of a finding, and a run that ended red, ended early or ended
with rows still open prints the attribution and drops the request. Asking to be
endorsed while something is still open is asking to be judged on manner rather
than on evidence.

**The flow diagram now reads top to bottom, and cannot trip GitHub's renderer.** It
was reported failing with *"Could not find a suitable point for the given
distance"* — the error mermaid's edge routing raises on long curved edges, which is
exactly the shape of the two dotted returns from acceptance. The chain carries a
linear-curve directive now and the loop labels are short. Rendered locally with the
mermaid engine before and after: that proves the source is valid, and it does not
prove GitHub's server-side renderer agrees, which is what the directive is for.

**Two negative self-tests were seeding nothing, and held this release.** Both
CHANGELOG count probes asserted that the topmost section already stated a guard
count, and this entry legitimately says nothing about guards — so they planted
nothing, reported `BROKEN`, and stopped the release. Correct as a signal, wrong as a
finding: the sibling probe at `## Unreleased` had already learned to **create its own
precondition** and says so in its own comment. Both now write the count they are about
to break, derived from the same thing the guard counts rather than from a literal,
because a literal is what went stale on three consecutive releases.

Guards: 413 → **413** — unchanged. Nothing was added; two were repaired to fire at all.

## v1.77.0 — a mention is not a declaration

The release-gap check counted every `vX.Y.Z` token in `## Releases that carry no stamp` as a
declaration that the release carries no stamp. So one sentence explaining a *stamped* release
— the words "the figure was already false at the `v1.76.0` tag" — exempted that release from
the check, and the negative self-test that exists to catch exactly this read as accepted for
the same reason: it too was reading the section's prose.

Declarations are bold now, which is the convention every entry in that section already
followed. Prose about a release can no longer excuse it.

Two plants cover it. The new one leaves the trailing release in the section in the same
words and removes only its bold — a mention where a declaration was — and requires the
refusal; watched firing in a standalone clone of 122 tags, and printing SKIP with its reason
in a submodule checkout, where no tags are visible and the check it probes cannot look.

Also: the README no longer presents `npm test` as runnable from a package that ships no
`test/` directory, and `test/residue.py` tags each workspace with the process group that made
it, so a scan of the shared `$TMPDIR` stops reporting another session's trees — and an
earlier run's deliberately kept evidence — as this run's leak.

Guards: 412 → **413**. `test/negatives.py`'s floor moved with it, in this change, because a
floor below the count cannot notice losing the difference.

## v1.76.1 — the number the published README had never checked

The README's validator line said **all 23 references** and the tree it shipped
held **36**. Not drift: the count was already wrong at the `v1.76.0` tag, so npm
has been serving a false figure since that release, while a checkout of the
umbrella — whose pin points at the branch tip — has been serving the true one.
One version string, two documents, and the difference was a fact about the skill.

Found by comparing trees rather than version strings, which is the only way this
class is visible: `npm view` answered `1.76.0` for both.

    published README   all 23 references
    references in the tarball's own tree   36

Nothing else changed. The tag exists so the published document stops lying.

Guards: 412 → **412**. Flat, and stating it is not decoration: the claim registry
reads the topmost section for this number, and a section that omits it reports the
class as *dormant* — which is how a release with no live count silently disarmed the
two plants that probe it. Omitting the line is a change to the guard suite's own
coverage, so it is written even when the number does not move.

## v1.76.0 — the audit that starts cold

**`project-audit` ships as this plugin's third skill.** `references/audit.md` has
been the family's audit *method* since v1.20.0 — the L0→L7 ladder, seams over
artifacts, axis rotation, the exit criterion. It assumes a brief with REQ rows
and a module map, which most repositories do not have; pointed at one that does
not, its true first finding is *"your spine is missing"*, and that is not an
audit. The new skill is the **procedure** around the method: discover what the
project is, probe it from that, read the production evidence a repository cannot
hold, hand phase 4 back to the ladder, and leave two artefacts. The method is
not copied — a second copy would be a second rule.

**Probes return three verdicts, and the third one is the design.** `clean`,
`finding`, `blind`. A probe whose need is unmet, whose command is missing or
whose output is empty returns `blind` **with the reason**, and the reason reaches
the page as a section of its own rather than an appendix. Without it, "no error
tracker is configured" and "no errors" render identically and a reader takes the
second meaning. This is `audit.md`'s *silence is not a reading* raised from a
command to a probe.

**The class a version check cannot see.** A registry serves the **tag**; a plugin
marketplace and a skills CLI serve the **branch tip**. Measured in this family on
2026-08-22: npm served one file at 4344 lines while the marketplace served it at
4575, and all three channels answered `1.15.0` — with the pin checker green
throughout, correctly, because it compared the two strings. `channel-divergence`
compares **trees**, and three of its traps are fixtures rather than prose:

- the first draft compared the tarball against the **tag** and reported clean.
  Those agree by construction, because the registry publishes *from* the tag —
  a tautology returning green, which is the *false success* shape `gates.md`
  names;
- counting a path present in one channel and absent from the other produced
  **22 findings** on a member where one file had moved. A tarball ships what its
  `files` allowlist permits; that is packaging, not divergence;
- a branch already bumped past its tag makes no common claim, so it is `blind`.

Re-derived against a differently-shaped command: `git diff --name-only
v1.15.0..HEAD` returns the same eight paths the probe reports for `agent-sync`,
`sheleg-design` sits exactly on its tag and the probe is silent, and `make-skill`
is one commit past and the probe returns one.

**Two artefacts, and the second is what makes it a ratchet.**
`docs/audit/<date>-audit.html` for a person and `docs/audit/<date>-audit.json`
for the next run. A finding's id is derived from its probe and its place, so it
survives a rewording; the next audit prints what closed, what is new, and what
has now survived three runs — which is itself a finding, because a defect nobody
picks up is a decision nobody wrote down.

**Read-only, and the report is shareable by construction.** Findings leave as
proposed board rows priced with the project's own formula; nothing is written.
The page carries aggregates and pointers, never raw bodies — a secret is reported
by `file:line` and class with the value in neither artefact nor on stdout, and
the redaction is total rather than a prefix.

**Found by the fixtures rather than by reading**, and both are now checks:

- the audit read **its own output** as project state. Run 1 saw a clean tree; run
  2 saw `docs/audit/` and reported the project dirty. Standing instruction #2 —
  prove idempotence at the layer that repeats — is exactly this shape, and the
  three-run fixture is what surfaced it;
- the obvious fix was worse than the bug. `git status --porcelain` collapses an
  untracked directory to its shallowest path, so excluding by path silently
  failed to match; widening the match to *either is a prefix of the other* would
  have hidden every new file under `docs/`. `-uall` asks git for the full list
  instead, and a fixture holds the sibling case.

**The refusal phrase is «без диагностики», not «без аудита».** `аудит` is this
plugin's own trigger — kept deliberately after re-derivation — and
`triggers_test.js` refuses any refusal phrase containing a trigger, because
saying it would fire the hook it exists to silence.

`npm test` now runs three suites: the validator, `graph.py`'s 149 cases and
`project_audit_test.py`'s 43. The validator refused the release until the new
suite joined both documented equations — a suite outside the full run is a suite
CI does not have.

Guards: 412 → **412**. Flat, and the flatness is the point: every check this
release adds guards the shipped collector, so it lives in `project_audit_test.py`
where the code it exercises is, not in the structural validator. Counting them
as validator guards would inflate a number whose whole job is to make a dormant
check visible.

## v1.75.0 — 2026-08-22 — the day's findings become doctrine

Nothing new ships behind a flag here; what ships is the doctrine the previous release
earned, written where the next run will read it instead of in a changelog nobody greps.

**`documentation.md` canon 2 gains its dual.** *Numbers are computed, never restated* had
a half nobody had written down: **an example that instantiates a number IS one.** A release
note explaining that a count was written in the wrong shape — with the digits in it — places
a second readable count in a section a gate reads, so a probe that removes the real one
leaves the narrative matching and the guard silent. Measured three times in one hour, each
time inside prose *about* this very failure. The umbrella already said it for commands:
name a dead command, never claim it. It holds for a number, a version and a shape.

**`gates.md` gains three sections.**

*A probe rots, and every way it rots reports green.* The three assertions prove a probe
works today; the thing it guards is the thing that moves it. An anchor pinned to a literal
dies on the release that changes the number it guards. A precondition inherited from the
tree evaporates **when the system works correctly** — an honest run stamp leaves nothing
"after the newest stamp", a release absorbs the `## Unreleased` section — and the probe
lands and proves nothing. The triage is one question: *what does this probe look for, and
who is allowed to change it?*

*A ratchet prices the rule, not the exception.* A coverage check that asserts once per
exception and falls through on the ordinary case makes the correct remediation lower the
count — so the gate goes red on the stricter answer and a legitimate lowering becomes
indistinguishable from the failure the floor exists to catch. One assertion per subject
examined, whatever its verdict. And measure the floor **after** the last edit: read, keep
editing, restate is how every floor ends up below its true count, silently, because a floor
is a minimum.

*Run the whole suite locally before you push the tag.* Also **R-010**, because it is a
run-level obligation rather than a note. One tag took five CI rounds where the last four
were a single twelve-minute local run apart — and the second half is what makes it a rule:
a branch push cannot see a tag that does not exist yet, so three checks have no earlier
chance to fire.

### And R-010 failed on its own release, which is the finding

The local suite was green and CI was not. The difference was one precondition asking
`os.path.isdir(".git")` — false in a **submodule** checkout, where `.git` is a file holding a
gitdir pointer. The whole release-gap check had been switching itself off in the only checkout
this family is developed in, since the day it was written, with no line of output. It ran in CI
alone, which clones standalone, so a class of defect reached four tag pushes before anyone asked
why the local run was green.

This repository had already recorded that class **twice**, in `docgate.sh` and in the retro log,
both naming `[ -d .git ]` as the wrong question. This instance was missed both times. Knowing a
class is not sweeping it — which is standing instruction R-003, also already in force.

Two fixes, and the second is the general one: ask `exists`, never `isdir`, of anything named
`.git`; and **a precondition that fails must disclose rather than skip**. A check guarded by a
bare `and` evaporates without output, and it evaporates most reliably in the environment its
authors work in. R-010 gains the half it learned by failing: *a green local suite is not
evidence until you know which checks looked* — tag locally first, run, then read the `unlooked`
line before believing the exit code.

Seven board citations into `gates.md` were re-pointed across two passes, which is the ordinary
cost of inserting text above them and the reason those citations carry a phrase as well as a
range.

Guards: 412 → **412**. Flat by construction: this release adds doctrine, not checks, and a
guard count that rose on a documentation change would be a number borrowed from a suite that
never ran. The shape of that line is the one canon 2's new half is about, so it is written
here in the form the guard reads and described nowhere else in this section.

## v1.74.0 — 2026-08-20 — a node is closed by three readings, not one

**A verifier reads the diff it was handed, and that is the definition of its context, not a
shortcoming.** It also means a class of defect is invisible to it by construction: the change is
correct where it was made and a caller's contract moved under it; a second implementation of the
same rule did not get the fix; a documented behaviour is now false and the document still reads
as true; another feature reaches the same path and nobody considered the interaction. None of
those is a bug in the changed lines. All of them ship.

A node is now closed by **three independent readings at escalating visibility**, and the run may
not advance until all three pass.

| Tier | Subject | Characteristic finding |
|---|---|---|
| `unit` | the changed functions, classes and branches, plus the node's own `check` | a branch nothing exercises; a boundary that moved |
| `seam` | everything that can reach the change — callers, callees, implementors, shared state, the neighbours' tests | a contract that moved under a dependent; the duplicate that did not get the fix |
| `product` | documentation, scenarios, user-visible strings, the neighbouring features sharing this path | a documented behaviour that is now false; an interaction nobody listed |

**Blind is the design, not a detail.** The three dispatch in parallel and no tier reads another's
report, because three readings that inform each other are one opinion with three signatures — and
the failure is specific: an agent that has just read a convincing account of the implementation
will paraphrase it back as product truth. `certify` refuses a report whose prose cites another
tier's verdict.

**`certify` is a gate in front of `close`, and `close`'s contract is unchanged.** It takes one
report per tier, requires all three to pass, and assembles the same seven-key verdict `close`
already consumed — then runs that verdict through `close`'s own `verdict_violations` before
writing it, so a certification cannot hand the run a verdict its consumer refuses. No field is
used for something it does not mean: `confirms` → `done`, `not_examined` → `not_verified`, a
`risk` finding → a blocker with `can_continue_around: true`.

**Two rules give a pass its meaning.** A tier cannot pass on an empty `scope` — a report naming
nothing it read is a rubber stamp, and three rubber stamps cost three times one verifier while
reading as three times the assurance, which is strictly worse than what they replaced. And a tier
cannot pass while carrying a `breaks` finding. There are two severities and no third, because a
certification that admits a maybe admits everything.

**The fix cycle records itself.** A failing round leaves the node open and writes its round number,
this round's three verdicts and the whole history onto the node — on failure too, because a failing
round that wrote nothing would erase the only evidence that a node is churning. Every `breaks`
finding carries the `check` that will prove its fix, so it becomes a node the next round can close.
At the ceiling (`--ceiling`, default 3) the gate **measures rather than stops**: it names the tier
that has failed *every* round, because the same tier failing three times is a planning defect
wearing a verification failure's clothes, and different tiers each round is churn across levels.

### The verification of this change, and what it caught in itself

`test/certify_mutations.py` disables each of the gate's sixteen rules in a copy of the tree and
requires a fixture whose name begins `certify:` to notice. **16 of 16 noticed.** It is wired into
`test:all`, and it exists because the first two attempts at this pass were both wrong:

* The first reported **11 of 11 killed** and proved nothing — every mutant had died of the same
  unrelated fixture, because the copy has no `.git` and one pre-existing case checks the commit
  stamp. A mutant is killed only by a `certify:` fixture now.
* Fixing that reported **0 of 16** and explained why: the twenty new fixtures had been inserted
  **below** `graph_test.py`'s `if failures: sys.exit(1)`, so any earlier failure skipped all of
  them. Locally everything was green and they ran; in CI, on the run where they mattered, they
  would not have. The block moved above the summary, and the mutation pass now asserts its own
  control — that exactly twenty ran and none was red — before reporting a single result.

149 graph fixtures, 20 of them new. `references/certification.md` is the doctrine; the three
agents ship beside `verifier.md`, which now points at them.

### The first live dispatch, and what it caught

The fixtures prove the **gate**. Whether the shipped agent prose yields a usable report is a live
dispatch, so one was run: all three tiers against `sheleg-design@f88c14b`, a strict reduced-motion
check that had shipped green through a single verdict hours earlier.

All three returned a well-formed eight-key report. **Two returned `fail`, with five `breaks`
findings between them.** The unit tier ran the node's check in an isolated worktree at the
certified commit, ran its own negative control, and put a cross-level observation in
`not_examined` rather than claiming it — which is the instruction that keeps the levels apart.

What the independence bought, stated as measurements rather than as a claim about the design:

* the **seam** tier instrumented the gate's `check()` calls and found the ratchet prices the
  *exception* rather than the rule — collapsing the four durations the requirement names as its
  first remediation dropped the count by 4 against its floor and turned the suite red on the
  stricter answer
* the **product** tier planted a defect and watched it pass: a duration whose token name carries
  no duration word was outside the walk entirely, and thirteen such tokens across ten layers were
  clean by habit rather than by the check
* **both outer tiers independently** found a propagation-matrix row still stating the obligation
  the change had replaced — two blind readings converging is the signal that they are reading
  different things

None of the five is a bug in the changed lines, which is the class this gate was built for. They
are fixed in `sheleg-design@874ba17`; four further findings are filed there as decisions rather
than repairs. The one about the author is filed too: every ratchet floor set that day sits below
its true count, because the sequence was measure, keep editing, restate.

Guards: 412 → **412**, and the flatness is the honest number — written in that exact shape
because the guard reads it:  this release adds no validator
negative, because every rule it adds lives in `scripts/graph.py` rather than in `validate.py`, and
`.github/workflows/validate.yml` plants defects for the second. The certification's own negative
control is `npm run test:certify` — **16 mutations, 16 noticed** — wired into `test:all` beside
the 14 property checks. A guard count that rose here would be a number borrowed from a suite that
never ran.

**The shape of that line is load-bearing, and this is the second time it has bitten.** The
v1.39.0 entry wrote the count with no colon, the pattern missed, and `npm test` was green over
a number it had never read. This release first wrote it with the bold around the whole phrase
instead of around the second number, and the same guard went silent again. The readable shape is
`Guards: N → **M**`, and the negative test that plants a stale count is the only reason either
miss was caught.

**Neither wrong form is reproduced here, and that is deliberate.** Writing the bad example with
real digits makes it a second readable count in this section — which is exactly what happened on
the first attempt: the plant removed the real count, the narrative about the mistake still
matched, and the guard stayed silent over a section that no longer stated anything. A document
that quotes a form as an example is indistinguishable from the form itself.

## v1.73.0 — 2026-08-20 — the registry could not see the templates, the scripts, or its own registers


**The claim registry had the class for this exact incident and it fired on nothing.** Three
shipped surfaces said *34 reference files* over a directory of 35 — `scripts/graph.py`'s
`doctrine` docstring and `templates/run.md` twice — and `npm test` printed
`reference files: dormant (truth 35)`. Two holes, either of which was enough: the pattern
knew only the word order ``N files under `references/` ``, and the corpus was eight named
files plus `references/**`, so `templates/` and `scripts/` were never opened. The class now
reads any phrasing of the count, the corpus reads the templates and the shipped script, and
the class is armed at three agreeing sites instead of dormant.

**And it never read this repository's own registers.** `docs/DOCMAP.md` names decisions,
open questions, the board, the ledger and the retro as the registers, and its propagation
matrix sends *a number stated in a living document* to this registry — which could not see
any of them. `docs/OPEN_QUESTIONS.md` said *the 250 guards* against a workflow defining 390,
in a phrasing the guard class already knew. Bringing them in refused 26 statements and every
one was narration, so a number inside a **dated item** is a record and exempt; on the board
the discriminator is the State cell rather than the date, because every row names the day it
was filed and B-001 — open — was stating its description budget and its reference-file count
as facts about now.

**Fourteen consecutive releases carry no run stamp**, `v1.60.1` through `v1.72.0`, and the
retro's honest-gap section named only `v1.16.0`–`v1.23.0`. Its *Measured, not recalled*
receipt could not produce the measurement: it grepped `docs/superpowers/retro.md`, removed at
v1.53.0, and grepped for a tag's own commit when a stamp names the commit the *run* ended on.
Rewritten as a tag-range walk that reads the archive too, and a guard now requires every
release after the newest stamp to be named in that section.

Also: `## Unreleased` is where the guard count lives between a tag and the next bump (B-104);
`Environment` is a required cell on every verification row with the vocabulary read out of
the shipped template (B-099's other half); the graph schema states its three node rules
behind `$ref`s and the checker follows them (B-079, proved by moving them, not by a fixture);
an open board row's `file:N-M` must quote the phrase it points at, which caught five stale
citations and then caught this change's own edits four more times; the acceptance ladder is
policy **`AP-1`** with an owner and an in-force date, and `gates.md`'s *the framework fixes
no stage count* is scoped to the pipeline's shape; `read:` and `gate:` are reported
**unattested** instead of claimed *never agent-written*, because the ledger is the file the
agent appends to at every stage; `validate.yml` no longer re-validates a SHA on its own tag
push; and every documented `npm` equation is compared against `package.json` — `CLAUDE.md`
had `npm test` as `validate.py` alone, dropping 129 graph cases.

**What the suite found that no reading did.** This change broke **thirteen** existing
plants and `npm run test:all` named every one: the two verification-header probes spell
the whole header and it gained a column; two CHANGELOG probes scoped themselves to
`^## v` and the count now lives in `## Unreleased`; **seven** graph-schema probes walk
`node.allOf` inline and the rules moved behind `$ref`. All thirteen were repaired by
deriving the guard's own scope rather than restating it, which is what `learned.md`'s
*sweep the class* asks for — and the sweep needed two rounds: six schema probes were
repaired together and the seventh surfaced on the next full run, having died on
`KeyError: 'if'` where the others had died on their own asserts. A class fixed in six of
seven places is the shape standing instruction R-003 exists for.

One of the twelve was sharper than the rest, and it was self-inflicted twice over: the
honesty note explaining that `OQ-0002` no longer restates a total put an ISO date in the
row, which made the row a dated record and **disarmed the register plant** — green over
exactly the stale total it had been written to catch. `OQ-####` now uses its `Status`
cell, the discriminator the board already uses, and the register plant sits on an open
board row where no prose edit beside it can turn it off.

Guards: 390 → **412** · property checks 9 → **14**


## v1.72.0 — a node says how it will be closed

**B-080 closed, and with it the last of four requirements this pack's own manifesto named
as unbuilt.** The Proof of Done manifesto cites this repository as its reference
implementation and filed four gaps against it by id; three closed on 2026-08-17, and this
is the fourth. The public document now says all four are built and names the commit for
each.

### `check` — the per-node completion test

A node could not say how it would be closed, while shipped doctrine told the verifier to
"run the checks the task named". The doctrine read a field the schema did not have.

`check` is a string, **required on every node whose status is not `parked`** — the parked
node being the one nobody will close, where a placeholder would be confidence without
correctness. Never a list: a node needing two unrelated checks is a node doing two jobs, and
one gate made of two commands is `a && b`, which is still one gate. Stated twice on purpose,
in the schema and in `violations()`, because the schema never runs against a live graph.
`add --check` is required like `--why`, and a replan entry naming no check is refused before
the close writes anything.

### The record the manifesto opens with now reads as one event

`residue.md`'s opening record is quoted by an external document and permalinked from a public
site. It said the inventory was queried "one minute later" beside a `ps` line showing the
process at 3:12 — two accurate observations of different things, framed so a reader had to
reconcile them by hand. Both moments are now stated, the interval between them named, and
**what the record never carried is named too**: the wall-clock times, which `git log --follow`
proves were never in it. A disambiguation, not a correction — no number changed.

The E4 sentence claimed more than its own block: "that **they** have been up for three days"
from a measurement of the oldest one. Now "the oldest of them".

### Three plants that could not run, and one row that could not be parsed

CI failed twice on this release's work, and neither failure was noise.

A ledger row wrote a pytest filter as a backticked `-k a|b|c`; markdown does not care about
backticks, so two pipes split one cell into three and that row carried ten cells against a
header of eight. Locally the damage sat in a column nothing read, so every gate run passed.
Every `REQ` row must now match the header's cell count, with the remedy named in the refusal.

Then three schema plants died on `KeyError` before reaching their own `PLANT DID NOT LAND`
assert, because the new `check` rule added an `allOf` branch keyed on `not: {const: parked}`
and each plant indexed the const directly. All three traverse tolerantly now. **The assert
catches a plant that does not land; nothing catches a plant that cannot run** — the third
instance of that class in three days, and it is filed family-wide rather than here.

Guards: 389 → **390**. The new rule arrived without a plant, which this repository's own standard refuses; that is the plant. `graph.py` 114 → 129 cases.



## v1.71.1 — four shapes of a green that measured nothing

> **v1.71.0 is a burned tag.** Its entry was prepended **above** `# Changelog`, so
> `test/validate.py`'s newest-section parser read the *previous* release while the
> negative self-test planted its defect in *this* one. The two looked at different
> sections, the plant proved nothing, and CI failed with *"the release entry claimed a
> guard count the workflow does not define"* — which is the R-001 failure the plant's
> own comment describes, reproduced by the release that shipped the doctrine about it.

Four issues, one class: a signal that reports success while checking nothing. All four
survived at least one release in a real project, and none is visible to inspection — the
command reads correctly, the test name is accurate, the document's rows look settled.

### The false-success table gains two shapes, and its rules go from two to four (#48, #49)

**Read through a pipe.** GitHub Actions runs `run:` under `bash -e` **without** `pipefail`, so
`npm test 2>&1 | tee ../test.log` concluded `success` over its own `# fail 55`. Then the same
author did it by hand hours after fixing it: `check-docs.sh | grep -E '^(OK|FAIL)' | tail && git
commit` committed over a `FAIL` printed to their own screen. **This is the least visible entry
in the table because the command reads as diligence** — `check.sh | grep FAIL` looks like
somebody being careful.

**An absence with no subject.** A viewport suite pinned a responsive rule as a pair: the column
visible at 1280, absent at 1279. The column had been removed from the product months earlier, so
the desktop half failed and the compact half **passed at every width**. The test named after the
compact band proved nothing about it. This is the complement of *watch the green fail against a
planted defect*: that rule finds a check which **cannot fail**; this one finds a check which
**cannot succeed meaningfully**.

### A check with a wrong premise can still be the thing that finds the defect (#40)

A new check going red on day one invites one reflex — *the check must be wrong, relax it*.
A guard asserted two constants for "the price of one unit per year" were equal; the premise was
wrong, they belong to two different products. Reading further, the disagreement was **visible to
customers**: both still sell from one page, and the note under the volume table promised a
discount computed from the header's price while the table's numbers gave roughly half of it.

`gates.md` now says to **separate the premise from the observation before touching either**, and
to relax the assertion only after what it surfaced has its own record — otherwise the finding
leaves with the check that found it.

### A hand-corrected document drifts back within one run (#39)

Four boards consolidated into one, every row re-checked; within 24 hours a row settled in code
that morning read `open` again — in **two** places, because a row in a section table and again
in a summary has to be closed twice. **A document's claims are never executed**, so nothing
distinguishes a row that *is* true from one that *was* true, and the audit correcting it is the
only reader that checks.

`documentation.md` gains the rule: a correction is done not when the rows are right but when
**something other than the next audit** will notice them going wrong — with the four claim types
and what makes each self-checking. Where a claim genuinely cannot be derived, **say so in the
row**; correcting it silently a second time teaches readers that somebody else is checking.

> **After the tag, on the same tree.** `v1.71.1` is cut, and the guard-count claim
> `test/validate.py` reads is the newest `## vX.Y.Z` section's — which post-tag is this one,
> with no version heading yet open for the work that follows. So the live figure is stated
> here rather than inside a released sentence, and the released sentence below is not edited:
> B-080 closed on 2026-08-19 with eight plants and TP-02 with five on the same day, so
> Guards: 376 → **389**. The guard has no home for a count between a tag and the next bump;
> filed as `B-104`, and the note is what keeps the number true meanwhile. **The bold belongs
> on the number alone**: the plant that corrupts this count reads `Guards: N → **M**` out of
> the raw section, so bolding the whole phrase left the validator reading a count no plant
> could still corrupt — which is the form this note was introduced with, and no second
> count-shaped figure belongs in this section for the same reason.

Guards at the tag: 376 → 376. No guard was added or removed — that release is doctrine, and
each of the four rules is cited from the reference that owns it rather than restated.

Closes #39, #40, #48, #49.

## v1.70.0 — the stemmer cannot conjugate, so the description says the other form

`запиши решение` — the imperative a person actually types — reached no route at all, while
`evidence-docs` advertised the infinitive `записать решение`. The umbrella's matcher stems
`записать` to `записа-` and cannot reach `запиш-`: the с/ш alternation is a conjugation class,
not an ending, and `lib/triggers.js` says in its own header that it is *deliberately NOT a
morphological analyser*.

**So the fix is here rather than there.** Teaching a load-bearing stemmer one conjugation
class for one trigger was measured and refused (`B-84` on the umbrella's board); advertising
the second form costs **19 characters in a description with 124 free**. The description now
carries both, and the umbrella routes `запиши решение`, `запишите решение` and
`запиши решение по архитектуре` to `evidence-docs`.

**One false positive, measured rather than overlooked.** It also fires on «запиши решение
суда». A court decision does not occur on this machine and the cost of the hit is one injected
line — where `аудит` was refused against `аудитория` precisely because that word is common.
The trade is named here so a later reader does not have to re-derive it.

Coverage on the umbrella's own corpus: **64/15 → 65/14** of 79 prompts.

Guards: 376 → **376**. No guard was added or removed — this release changes one description
and nothing it asserts is new; the umbrella's fixture that every trigger is advertised is what
holds the pair together, and it lives there rather than here.

## v1.69.0 — the work graph, and a check that mentions is not a check that binds

**Module 1 of the role-agent programme, complete** — T-1 through T-7, briefed in
`docs/evidence/specs/2026-08-17-role-agent-graph-brief.md`. The graph is on disk, a script
walks it, a verifier closes one node at a time against a seven-key verdict, and the loop
reads a queue rather than its own recollection.

**Counted at the close, not carried from a section above:** 376 guards · 114 graph fixtures · 24 exposure fixtures · 9 verbs on `graph.py` · 35 reference files · `npm run test:all` exits 0 over eight suites. The figures in the sub-sections below are each true at the moment that sub-section landed, which is why this line exists.


**`graph.schema.json` and `graph.example.json` ship**, and `test/validate.py` reads
them. `.task-pipeline/graph.json` is the queue the loop walks — a run artifact, never
committed by the skill, so what ships is the schema and one example that exercises it.

**The first draft of the check asserted membership in `required` and nothing else,
and an independent reader defeated every requirement it claimed to enforce.** Standing
instruction `R-005` exists for exactly that — *your own reading of your own check is
the reading that missed it* — and this is the first time it has been run on a check
this repository added. Eight bypasses, all now refused and each watched refusing:

| Bypass | Why it worked |
|---|---|
| `nodes` declared an object map, `items` left as decoration | `items` constrains arrays only, so every element check was vacuous — REQ-001, 002 and 003 defeated at once |
| `owner` in `required`, `minLength` dropped | a node whose owner is `""` satisfies `required` and dispatches to nobody |
| `owner` typed `["string", "null"]` | the same, with `null` |
| `edges` requiring `payload` and neither endpoint | an edge is from, to, and what it carries |
| `items` given as a tuple | binds element 0, frees the rest — and crashed the check rather than failing it |
| a name in `required` that `properties` never declares | constrains nothing at all |
| a two-hop `$ref` | reported five fields missing that were not missing |
| an example of `{"nodes": [], "edges": []}` | validates against any schema and demonstrates none of it |

**And one claim in the schema's own prose was false.** It said `done` implying
evidence was beyond JSON Schema. Draft-07 `if`/`then` states it exactly, and now does
— so a node called done by assertion is refused **by the format**, before any script
runs. The line between "the schema's job" and "the script's job" moved to where the
format actually puts it: what remains for `graph.py` is cross-document — whether an
owner names a role that exists, whether `serves` resolves, whether the edges cycle.

**A NameError, found by the reader and not by the author.** The skip path appended to
`_skips`, which exists in a **sibling repository's** validator and not in this one. On
any machine without `jsonschema` the run died on a bare traceback and the ~250 checks
below it never ran; CI could not see it, because CI installs `jsonschema` first. The
accumulator here is `_UNLOOKED`, and the one-line fix that defines `_skips` would have
been worse — a silent skip, which `test/validate.py:395` forbids by name.

### T-2 — the walk, and the promise it exists to keep

`scripts/graph.py` ships: `validate`, `next`, `goal`. Stdlib only, verified by
parsing its own imports — `references/portability.md` makes `scripts/` the one
Claude-Code capability that travels, and a dependency here would have made the
graph Claude-Code-shaped.

**The design's central claim is now a measurement.** A 400-node graph is 51 KB on
disk and produces a **27-byte** frontier; a 4-node graph produces the same 27
bytes. Context cost is **flat in graph size**, which is the property every other
part of this programme rests on — and it is why `next` prints the frontier and
nothing else. That line enters a context on every iteration of every loop.

It checks the three things a schema cannot reach, and only those: whether `owner`
names a role that **exists** (with the misspelt near-miss caught separately from
the absent one, per `R-008`'s enumerate-the-shapes rule), whether `blocked_by` and
the edges name nodes that exist, and whether the edges **cycle** — the one failure
of this design that looks exactly like slow progress.

Exit codes are the contract per `R-004`: `3` is *nothing left to do* and `4` is
*nothing runnable*, because a finished graph and a stalled one are different facts
and a caller that cannot tell them apart will wait on the wrong one.

`test/graph_test.py`, **14 cases**, joins `npm test`. This is also the first
`scripts/` in this repository, so `CLAUDE.md`'s sentence about the only executable
code being two installers and the validator was false the moment it landed, and is
corrected in the same change.

Guards: 351 → **376**. Twenty-three plants across the module, structurally distinct rather than variations,
each asserting it landed before the validator runs.

### Stage 9 — the third artifact, and one false alarm I raised myself

The code graph was **33 commits behind** and its report described a *different* graph: 1787
nodes and 1847 edges in `GRAPH_REPORT.md` against 1535 nodes in the `graph.json` beside it,
with the report the older of the two. `graphify update .` re-extracts without an LLM call, so
the refresh cost nothing but time: **1866 nodes · 1983 edges · 231 communities**, stamped at
`26ac6dd`, and the report now agrees with the graph exactly.

**The hubs are seven doctrine sections and three test helpers, and no undocumented code
seam.** `project()`, `exposure()` and `row()` are hubs because twenty-four fixtures call them
— scaffolding, not architecture. That `graph.py`'s own functions are *not* hubs is the
informative part: nine verbs with little internal coupling is what the design intended.

**And I raised a false alarm on the way, which is worth recording because of how it read.**
The first measurement said *1535 nodes and zero edges* — a graph that answers no reach
question at all, which is exactly the failure `references/knowledge-graph.md` warns of, since
a wrong graph carries the authority of a machine. It was wrong: edges live under `links` in
this format, and there were 1585 of them. A check that reads the wrong field reports the most
alarming possible state with total confidence — the same shape as a check that reads the
wrong subject, one axis over, and the reason the second measurement was taken before anything
was filed.

**Disclosed rather than skipped in silence:** 231 communities now carry 156 saved labels, 154
of them renamed by their hub. Refreshing the names needs an LLM call and was not made, so the
community names in the report are hub-derived and not semantic.

### Stage 6 — the full suite, and the thing it found was the suite itself

`npm run test:all` ran six suites and **`graph_test.py` was not one of them.** 114 fixtures —
the whole of module 1 — lived in `npm test` and outside the command named *all*. Every command
in `test:all` passed, so *the full suite is green* had been a true sentence about a smaller set
than it names. `exposure_test.py` was worse off: **24 fixtures in no script at all**, testing
the very file this release extended with the staleness section.

Both are in now, and a guard **discovers** the suites rather than listing them — every
`test/*_test.py` and `negatives.py` must be reachable from `test:all`, resolving one level of
`npm run`. A list there would drift exactly the way the thing it checks drifted.

**Its own first run was wrong, and said so.** Substituting script names in declaration order
made `npm run test` a prefix of `npm run test:probe`, so four suites were reported absent that
the chain reaches. Longest name first.

**Then the full suite found two rotted CI plants — both rotted by edits made in this release.**

- *coverage stops refusing a requirement nothing serves* replaced the first
  `return 1 if bad else 0`, and that line **stopped being unique** the day `cmd_close` landed:
  the plant disarmed `cmd_validate` instead and the guard, correctly, stayed green. This is a
  new shape of an old class — a plant pinned to a literal usually rots because the literal
  disappears; this one rotted because the literal **multiplied**. It anchors inside
  `cmd_coverage` now.
- *a worked GATE verdict that prints no disclosures* matched a sentence that B-064 appended
  `· holds: 0` to, hours earlier. It matches the line's **shape** now.

Both were watched landing and firing before the suite was re-run. `test:all` → **exit 0**
across eight suites: 376 guards, 114 graph fixtures, 24 exposure fixtures, 9 property checks,
7 + 7 artifact fixtures, the release-gate harness and the documentation gate.

### T-7 — the doctrine that names the graph, and module 1 closes

`scripts/graph.py`, `graph.schema.json` and `.task-pipeline/graph.json` had shipped and **no
doctrine file named any of them.** The schema disclosed it about itself: its `queue`
description said `continuity.md` did not yet know about `work-graph`. A capability with no
doctrine is one an agent meets by accident, and the run that meets it by accident is the run
that reads the graph itself — which is the one thing the design exists to prevent.

`references/work-graph.md` ships: what each field is for and the failure it prevents, the
nine verbs with their exit codes, the three invariants a schema cannot state and the fourth
reason `violations()` restates the ones it can (**the schema is never applied to a live
graph** — `graph.py` is stdlib by design, so a rule checked only against the shipped example
is a rule the run does not have), and what the graph deliberately does not do.

**Stage 2 now writes it and its gate reads it.** The queue was already declared there — *the
queue exists here, so the loop arms here* — and the graph is where that declaration becomes
walkable: the frozen REQ ids so `serves` resolves, one node per unit of work with its owner
and what it touches, an edge per dependency **naming what it hands over**, then
`graph.py validate`. A graph that does not validate is not a queue, and `next` refuses to
walk one. `continuity.md` prefers it over the module map and the task list for a measured
reason rather than a taste: 400 nodes and 4 produce the same 27-byte frontier.

**The verb list is discovered from the script, not typed into the doctrine.** Two homes for
one list is the class B-084 recorded twice in a day, and the plant is a tenth verb shipped
without a doctrine row — refused.

**And the position hole appeared a third time.** `graph.py validate` is named in stage 2's
body and in stage 2's gate, so a file-wide search was satisfied by either: removing it from
the body left the gate to cover for it. Body and gate are checked separately now, as are
`SKILL.md`'s stage-table row and `stages.md`'s prose — the stage list is compared across
three surfaces, so a criterion on one is a criterion the others quietly drop.

Six planted defects watched refused. **Module 1 of the role-agent programme is complete:
T-1 through T-7.**

### T-5 — `close` consumes a verdict, and the verdict grew its seventh key

`verdict_violations()` had **no CLI verb**: the gate this module's own docstring calls *the
thing `close` consumes* was reachable only from the test suite, while `agents/verifier.md`
told an agent to run `graph.py close`. Shipped doctrine pointing at an absence — the class
B-080 is about, in the file that names it.

`close <id> --verdict <path>` checks the verdict, closes the node, applies `replan.add` and
`replan.park`, records a revision, and prints the goal with the new frontier count.

**A stop closes the node and refuses the next step.** `replan.possible: false` means the run
cannot continue around what it found — not that the work just verified did not happen.
Exiting 0 there would let the loop carry on past a stop; discarding the close would throw
away a verdict somebody earned. Both directions are fixtured, and the CI plant is the first
of them.

**`close` stamps the commit; the verifier never supplies it.** Evidence is prose, and a
verdict written after the tree moved is evidence about a different tree. An agent cannot name
the wrong commit if it is never the one naming one. Outside a checkout the stamp says
`unavailable` and why — canon 9a.

**The seventh key is `not_verified`, and it is the one people collapse into `not_done`.**
`not_done` is *asked for and absent*; `not_verified` is *present and unchecked* — the second
ships and the first does not. `npm test` has printed `unlooked: N` for releases, so the
pipeline named the concept everywhere except in the verdict that closes work with it. An
empty list is a valid answer; silence is not.

**And it walked straight into B-084's class again.** `close` wrote `verb: "close"` into the
revision log while the schema enumerated only `add` and `park` — so the first `close` wrote a
graph its own shipped schema rejects. The fixture asserting *the graph after a close still
validates* **passed**, because `violations()` never reaches an enum; a `jsonschema` probe
caught it. Both ends now agree from one place, the runtime enforces the set, and a fixture
compares the two homes directly rather than trusting either.

`test/graph_test.py` → **114 cases**.

### B-092 — the report an operator actually reads

Every gate computes exactly what a not-verified field needs: `abstained` for claims the run
declined to make, `unlooked` for checks that did not look. **None of it reached the
hand-back** — four sections and two counters, none of which said what the claim covers or
what was never checked. So a run could hand back a report honest sentence by sentence and
still be **indistinguishable from a run whose checks never looked**, which is the failure
`references/progress.md` names three separate times about other things.

`SCOPE` and `NOT VERIFIED` are in the block now, and in the `hand:` ledger shape beside it —
the block is transient and the ledger is what survives a compaction, so a field in one and
not the other is lost exactly when it is needed.

`NOT VERIFIED` is **populated from the disclosures rather than composed**: the `abstained`
and `unlooked` sets in words, plus anything built this iteration that no check touched.
Composed by hand it becomes a summary of the parts somebody remembered. And the literal
`none within the stated scope` is required for the empty case, because an empty field and
*nothing inside what SCOPE names is unverified* read the same and are not the same — canon
9a, one artifact over.

**Three of the five plants defeated the guard first, all by the same hole: either side
satisfying a check meant for both.** A search for the words anywhere in `progress.md` passed
a block that carried neither, since the doctrine discusses them in prose throughout — it
reads **inside the block** now. And a search for `scope` among `run.md`'s `hand:` lines was
satisfied by the *example* while the *shape* had lost it, and vice versa — each `hand:` line
is now checked against its own continuation, shape and worked example alike, because an
example that omits what the shape mandates teaches the omission.

One miss was mine rather than the guard's: the plant harness filtered failures for `B-092`
while that check cited only canon 9a, so a working guard read as a hole. The attribution now
names both.

### Canon 9a — a measured zero and an unmeasured quantity may not print the same

This arrived **three times under three names** in one programme before anyone named it:
*State zero out loud* for the code graph, `unanchored`/`unresolvable` for the verification
ledger, and `unmeasured` for `graph.py doctrine` — joined this release by `next` reporting
how many runnable nodes declared no `touches`. Four sites, one rule, and
`references/audit.md` is explicit that a class seen twice becomes a mechanism rather than
another paragraph.

Canon 9 already said *carry the absence*. 9a says **refuse the number**: `0 of 34 files
read` and *the recorder was never installed* are opposite facts, and a `0` claims the first
while meaning the second — the most reassuring answer available, derived from an instrument
nobody switched on.

**The check is over the shape, not the four sites.** Any verb of `graph.py` that prints a
count must carry, in the same function, a word for the case where nothing measured it. A
list of the four would not catch the fifth, which is the whole reason the rule is written
down — and the plant is exactly that fifth: a new counting verb, added and refused.

**It also caught the difference between a word being present and a word being said.** The
first version searched the whole function body, so a site that kept its `undeclared`
variable and printed `note:` instead passed. It reads **printed text only** now — the same
lesson as four substring failures earlier in this release, arriving once more in a new
costume.

Measured before writing, and it changed the work: `templates/stage-coverage.sh` prints three
counts and no absence word, which looked like a fourth instance — and is not. It
**enumerates** every unaccounted stage by name, so its `accounted for 0` is a measurement
rather than a claim. The check was scoped to what actually has the defect.

### B-093 — two runnable nodes, one mutable target

`references/planning.md` states the rule with the right teeth — *distinct is not the same as
independent, and the check is what they touch, never what they are called* — and it lived
**entirely in the markdown plan**. The role-agent design replaced that plan with
`graph.json` as the thing deciding what runs next, and the node had no field for what it
mutates. So `frontier()` ranked by `blocked_by` alone and could hand two agents two runnable
nodes that write the same file, with nothing able to report it.

`touches` ships on the node — paths, register names, remote resource ids — and `next` reports
a pair of **simultaneously-runnable** nodes sharing one. Only simultaneously: a pair where
one waits on the other never holds the target at once, and reporting it would be a warning
nobody can act on, which is how a warning becomes noise.

**Both reports go to stderr, and that is a contract rather than a preference.** The frontier
rows are parsed one per node and are the one line paid for on every iteration of every loop
— a warning among them reads as a node.

**And the third state is the one that matters: nobody declared anything.** A frontier whose
nodes carry no `touches` produces no pairs, which looks exactly like a frontier that was
checked and found clean. So `next` prints how many runnable nodes said nothing — the same
shape `doctrine` refuses to print `0` for, one axis over.

**Three existing fixtures went red, and they were right to.** They asserted *the frontier
and nothing else* by reading stdout and stderr merged, so a disclosure written to stderr
looked like a violation of the width contract. The contract is about stdout; the helpers
`run_out` and `run_at_out` read that stream alone, and a helper that merges the two cannot
tell the contract from its breach. Six planted defects watched refused, including both
disclosures relocated to stdout.

`test/graph_test.py` → **101 cases**.

### B-065 — what the invariants bind together, coordination must guard together

Two halves of this row had gone stale and the third could not be mechanised, so it was
closed by measuring all three rather than by taking the easy one.

**Stale, and the measurement says so.** *«six registers under lease»* — `idRegisters` is
deliberately **empty**: the `fs` backend cannot reserve an id safely, and a declaration that
cannot be served reads as a capability nobody then writes the procedure for. *«the same
config in the other projects»* — measured: **all eight** family repositories carry one.

**Genuinely open, and now closed.** The version-sync invariant names **five** surfaces that
must move together; four were lease-guarded. The fifth is `SKILL-CARD.md` — whose omission
had already surfaced once on a release bump, from the validator rather than from a reader.
Two agents bumping a version collided there with no lease, which is not hypothetical: this
project lost four version numbers and a `files[]` entry to exactly that. `SKILL-CARD.md` and
the carry-over ledgers are guarded now.

**The surfaces are discovered, not listed.** A file *declaring* the current version — JSON
`"version": "x"` or the card's `| **Version** | x |` row — is a surface a bump touches, and
each must match a `guardedFiles` glob. A list here would drift from the invariant exactly
the way the last one did; watched catching a `registry.json` created for the test and never
mentioned to the check.

**And the habit was promoted rather than left as a row nobody can close.** *Take the lease
before the edit, not after the collision* is `R-009` now, with the retirement condition the
doctrine requires. It is a standing instruction and not a mechanism because whether a write
is *about to* happen is not a state a script can read — the guard refuses an unleased edit
*at* the edit, which is already too late to have avoided the race. B-75 is the evidence: a
second session committed to the umbrella with no leases and **invisible to `agent_sync
status`**, so the config being present is not the habit being held.

Five planted defects watched refused.

### B-061 — which doctrine a run actually read, and the one number it must refuse to print

The bundle is **34 reference files**. A run reads some subset and nothing recorded which,
so **a skipped file and a read one were indistinguishable** — the class every guard in this
repository exists to catch, left standing over the doctrine itself.

A `PostToolUse` hook on `Read` now appends `read: references/<file>.md` to the run ledger,
deduplicated, and **always exits 0**: a hook that can fail a `Read` breaks every turn in
every session, including sessions of packs that never asked for this one. It is
hook-written for the same reason `gate:` is — a claim about what somebody read, written by
the party the claim is about, is not evidence.

`scripts/graph.py doctrine` reports it, and **the state that matters is the one where it
must not print a number.** No ledger, or a ledger with no `read:` lines, prints
`unmeasured` and says why: the hook being absent and the run having opened no doctrine are
**opposite facts**, the ledger cannot separate them, so neither is claimed. `0 of 34` there
would be the reassuring answer to a question nobody asked, over 34 files nobody checked —
and that is precisely the shape that went unnoticed for a whole bundle.

Where the hook did fire, it prints the count **and every unread file**, because a number
says there is a gap and not where. It is a disclosure — no floor, no direction, never a
target: a run that needs four files and reads four is not worse than one that reads thirty,
and the moment the number becomes something to raise, a run will open files to raise it.

**No per-file reading floor was invented.** Stage 0's mandatory items are the floor that
exists and they are not per-file; declaring one inside a measurement would be a doctrine
decision smuggled in as a count.

Two existing guards caught this change as it landed, both correctly: a relative link in a
seeded template (which resolves from `templates/` and nowhere it is seeded to), and **a
ledger shape with no reader** — `read:` had to be named in the doctrine that consumes it
before the template could declare it. Seven planted defects watched refused.

### B-064 — a worked example is the executable half of doctrine, and now something checks one

Three times in one release a rule moved and its own example did not. An agent copies the
example literally and paraphrases the prose, so **the example is what ships** — and nothing
compared one against the rule it illustrates.

Now something does. Every `GATE <n> <name>: PASS|FAIL` block across `references/` and
`templates/` is read and required to carry the `holds:` line `gates.md` says every gate
prints. Three of the seven did not; they do now. And the page that **states** a mandate must
carry a conforming example of its own — the prose gets paraphrased and the example gets
copied, so the page stating a rule is the page that most needs one.

**The unit is the block, and that is not a detail — it is the whole finding.** A verdict is
its `GATE …` line plus the indented continuation beneath it. Measuring by *line* said five
examples lacked `holds:`. Measuring by *block* says three did: two carried it on a
continuation line all along.

**So the first version of this fix was wrong, and this check caught it ten minutes later.**
Reading line-wise, `holds: 0` was appended to two blocks that already said
`holds: 10 — none — enumerated 8/8 classes`. Two values for one disclosure in one verdict is
**worse than none**, because a reader picks one and copies whichever they picked. Both
duplicates are reverted, and the guard now refuses a repeated disclosure as well as a
missing one — a rule it learned from being broken by the change that introduced it.

Six planted defects watched refused: a continuation-line disclosure removed, an inline one
removed, the disclosure renamed inside an example, a **new** example added without it, a
second contradicting value, and the stating page losing its own example.

### B-076 — a ruling is not a measurement

Gate types were `auto` and `manual`, and that was one short. A reviewer's ruling, a check
that the scenarios are coherent, a verdict that a mockup is good — none has a complete
deterministic check, and all three rode in `auto`, **indistinguishable from an exit code**.
A coverage table then cannot tell a measured row from an opinion, and the role-agent
programme multiplies it: `reviewer`, `ux`, `ui` and `market-analyst` produce judgement by
design.

`judgment` ships. `auto` now means only what a machine established, and a judgment gate
**must name its `judge`** — the schema refuses it otherwise. That obligation is not
bookkeeping: a ruling with no author cannot be weighed for independence, and independence
is not a property of *having* a reviewer. This pipeline's own `R-005` reader shares a
model, instructions and repository with the author it reviews, differing only in context.
It is a real second reading and it is **not** a deterministic runner, a contract at another
boundary, or an external system. Naming the judge is what makes that difference visible
instead of assumed.

**It generalises a rule this repository already had in one place.**
`templates/verification.md` turns a coverage verdict of `review` into `none` in the `Auto`
column, because that column records what a machine established. That is the `judgment` type
applied to one column, and it has been sitting there being right.

**Which of this pipeline's own gates are judgement is deliberately not decided.**
`references/gates.md` says gate assignment is the operator's call and the framework fixes
none — so shipping a reclassified stage list would contradict the sentence above it.

**Eight planted defects, all refused on the first attempt — including the two shapes that
defeated every guard before this one.** Renaming the doctrine row to `judgement` and the
section to *About judgment gates* both fail now, because the checks anchor on a line's
opening cell rather than searching for a word. That was the session's repeated lesson —
four guards had been beaten by a substring — and this is the first one written with it in
hand.

### B-081 — proof expires, and the ledger had only one end of it

The verification ledger tracked rows nobody had **ever** confirmed and had no notion of a
row whose confirmation the tree has since **overtaken**. A row verified at commit A read
`verified` after commit B, forever. Those are the same failure from two ends, and only one
end was instrumented — so a ledger could read fully green over a tree where every check ran
against code that has since moved.

**This is a port, not a design.** `references/knowledge-graph.md` already gives the code
graph a stamp, a distance, three states, and a marker on every non-current one. The same
contract, applied to the ledger: `Observed at` is the commit the check ran against, and
`exposure.sh` reports **current · behind · unresolvable · unanchored** — a disclosure with
no floor, no direction and never a target, exactly like the `never` column beside it.

`behind` means **unproven for this tree, never wrong.** The section knows the distance and
does not know whether the commits between touched anything the row covers; claiming more
would be the estimate-printed-as-measurement this pipeline refuses elsewhere. And
**invalidation is not deletion** — an overtaken row is true about the tree it observed and
stays; re-observing appends.

**Where it prints turned out to matter as much as what it prints.** The first placement put
the section after the check-list, and `exposure.sh` exits early when nothing is unverified
— so the counts were invisible in exactly the state where they matter most. `0 unverified`
is the sentence most likely to be read as *nothing to look at*.

**Three of the eight plants defeated the guard on the first attempt, and one of them for the
fourth time this session.** Checking `"staleness" not in output` passed a section renamed to
`was-staleness`, because the old string is a substring of the new one; the guard anchors on a
line *beginning* `staleness —` now. Checking `"not trusted" not in output` passed a plant
that stripped the marker from the `behind` row only, because the unresolvable row still
carried one — it is checked **per state** now. And nothing asserted the **shipped** template
carried the column at all, so every project seeding it would have got a section dormant
forever, and dormant is green. All eight refused now.

### B-087 — the pointer is not the path

Stage 10 already required `git submodule status` with no `+` and every repository clean
and pushed. That is a statement about **commits**: the parent points at the child's newest
one. It proves nothing about whether the two versions work *together*. A parent can point
at a green submodule whose contract the parent's own code calls with the previous
signature, and every check passes — the child's suite ran against the child, the parent's
against the parent, and no check ran across the pointer. Neither repository looks wrong
alone, which is how this survived being written down twice.

`templates/convergence.sh` ships, and the criterion fires **only where a component
pointer moved in the range being accepted** — a range that crossed no boundary has no seam
to prove, and demanding a record for it is how a gate becomes noise. Where one moved, the
acceptance owes a named cross-component path, the exact versions it observed, and the
observation to the same standard a single REQ meets.

It also checks the thing `git submodule status` **cannot see: whether the pinned commit is
published at all.** Measured here on 2026-08-16 — a release tag failed CI at checkout
because the parent pinned a commit that existed only on one machine, and `submodule
status` showed no `+` because the pointer matched the *local* head.

**Two things happened on its first live run, and both are the point.** It found a real,
current defect in the umbrella: the parent's pointer and the child's HEAD disagree, so a
clone would get a different tree than the one tested. And it found a defect **in itself** —
the published-pin section read `git -C <c> rev-parse HEAD`, the *child's* HEAD, where it
needed `git rev-parse HEAD:<path>`, the parent's pointer. Those are the same fact only
while they agree, and they disagree in precisely the case the section exists for. So its
first live run reported about a commit the parent does not pin.

**The gate does not read the script; it runs it over four shapes built from real git
repositories** — a repository pinning nothing (dormant and green, because a gate that
starts red teaches its project the gate is noise), a range touching no component, a moved
pointer with no record, and a record that names no version. Five planted defects watched
refused, including a verdict block that prints FAIL and returns 0.

### B-086 — what produced the proof

Every artifact here recorded what was done, what proved it, and whether a person looked.
None recorded what **produced** it. Two runs six months apart, one under v1.40 doctrine
and one under v1.69, leave indistinguishable coverage tables — so a defect traced to a
doctrine change cannot be scoped to the runs that carried it.

`graph.py producer` prints seven fields, and **needs no graph**, because it is wanted
beside an acceptance artifact rather than inside a run. Three resolve from the tree —
the skill version from the plugin manifest, a digest of the project's `pipeline.json`,
and `git rev-parse HEAD`. Four belong to the harness (`actor`, `model`, `runtime`,
`trace`) and are read from named environment variables a project wires once.

**A field that cannot be resolved prints anyway and says why.** An omitted field is
indistinguishable from one that was checked and found empty — the rule every disclosure
in this pipeline already follows, applied to the one artifact that had no disclosures at
all. And `model` is deliberately **not inferred**: naming a vendor id in a shipped skill
is forbidden here, and inferring the wrong one is worse than saying nothing.

`templates/verification.md` carries the block above its rows, with the command that
computes it, so it is pasted rather than typed.

**Two harness defects surfaced while building this, and both were worth more than the
feature.** A fixture raising anything but `AssertionError` used to abort the whole suite —
one `KeyError` hid every case after it, and a harness that stops at the first crash
reports fewer failures than exist. It reports a `CRASH` line now and keeps going: the
count went from 1 visible failure to 4. And the guard could not observe the
no-manifest branch, because this repository always has a manifest — so a version *guessed*
as `task-pipeline@unknown` passed. That branch has its own fixture now, copying the bundle
alone, which is exactly what a plain-skill install is; watched failing against the guess.

`test/graph_test.py` → **93 cases**.

### B-085 and B-077 — the one edge between intent and execution, and the relation over it

`serves` was a non-empty string and nothing more, so `serves: "REQ-999"` and
`serves: "asdf"` passed every gate identically — and that field is the **only** edge
joining the intent graph to the execution graph. T-2's own DoD claimed *«every `serves`
resolves»* and nothing did.

The graph now carries `requirements`: the REQ ids the brief froze, **required and
non-empty**, plus optional `goal_clauses` for release work no requirement names.
Enumerated rather than substring-matched against the goal's prose, because matching a
sentence is the kind of check that produces confidence without correctness. A `serves`
resolving to neither is refused, with a near-miss hint.

**And `add` refuses to invent a requirement.** The REQ table is frozen at stage 0 —
adding to it is free and the *brief* does it, not a node. The refusal says so and lists
what is available, because an agent told only «no» will try a synonym.

**`graph.py coverage` computes the relation, and says which quarter of it it cannot
see.** `references/acceptance.md` defines the path a requirement takes and an agent
walked it from a checklist, one REQ at a time — the pipeline's own definition of a rule
that should have been a mechanism. Three directions are now computed: a requirement no
node serves, a requirement whose every node is **parked** (covered on paper and by
nothing that will run), and each requirement with the nodes and statuses serving it. The
fourth — an evidence row closing no requirement — lives in `docs/evidence/verification.md`,
which this script does not read, and **the report says that out loud**, because a report
silent about its own blind spot reads as the whole relation.

**Two of the guards for this were defeated on their first attempt, and both by shapes
this file has now met three times.** A source scan for `cmd_coverage` passed a
renamed-and-unwired `_cmd_coverage_disabled`, because the old name is a substring of the
new one. And the guard ran `coverage` only against the shipped example, which is fully
covered on paper — so a `return 0` that had stopped refusing anything passed. Both are
behavioural now: the example supplies the **failing** control (it has a parked-only
requirement, and refusing it is correct), a copy with the parked node removed supplies
the passing one, and the subparsers are **built from the dispatch table**, so a verb
argparse accepts and the dispatch lacks cannot exist — it used to raise `KeyError`, which
is a traceback where a named refusal belongs. Seven planted defects watched refused.

`test/graph_test.py` → **85 cases**.

### B-084 — the mutation verb was drawing chronology

The graph stored one fact in two unlinked places. `blocked_by` is what `frontier()`
obeys; `edges` carries the `payload` the schema requires — and nothing read it past a
from/to existence check. So `references/planning.md`'s fake-edge test, stated for the
markdown plan, was **unenforceable on the artifact that replaced the plan**, and
`graph.py add` wrote the first field and never the second. Every node added mid-run
therefore created a dependency whose payload was unnamed *by construction*. Measured by
the four-way manifesto audit: adding a node to the shipped example gave 5 nodes, 2
edges, `validate` exit 0.

Four things move together, because separately each leaves a hole the others cover:

- **`violations()` refuses an edge whose `payload` is missing or blank**, and refuses a
  `blocked_by` with no payload-bearing edge **in the blocker→blocked direction** — a
  backwards edge no longer satisfies a dependency.
- **`title` and `serves` must be non-empty at runtime.** Both were schema-only, and the
  schema has never run against a live graph, so `serves: ""` passed the gate while the
  format forbade it.
- **`add` takes `--carries`**, one per `--blocked-by`, pairing in the order written, and
  writes the edge **with** the node. A count mismatch is refused and names both counts.
- **`add` takes `--why`, and there is now a revision log.** `park` demanded a reason
  from the start and `add` demanded nothing, which left half the graph's revision
  surface silent — and a graph that changed for reasons nobody recorded can always
  explain its own completion by appealing to a plan that existed only at the end. Both
  verbs append `{verb, node, why}`; the schema requires all three and requires `why` to
  hold a non-whitespace character; `next` never prints the log, because the frontier's
  width is what a loop pays for on every iteration and this grows.

**Tightening the rule invalidated the fixtures that had relied on it being loose**,
which is the clearest evidence it bites: the test helper now *derives* an edge for every
`blocked_by` it builds, and the one fixture that needs a dependency with no edge asks
for it explicitly. Four planted defects were watched being refused, including a
`why` pattern of `^.*$` and a nullable `why` — the two shapes that defeated this file
twice already today.

`test/graph_test.py` → **75 cases**.

### The npx install path lost the verifier without saying so

`agents/` is a Claude Code plugin capability, and `install.sh` and
`bin/task-pipeline.js` copy the skill directory and the command and nothing else. That
absence is the **design** — the brief chose plugin agents with honest degradation. It
was silent, which is the part that was not: an operator on the npx path reads doctrine
naming `task-pipeline:verifier`, finds a name that resolves to nothing, and nothing they
ran ever mentioned it.

Both paths now print what they are not installing, how many files it is, that **every
role still runs** — on the main thread rather than in its own context, which costs
context and speed and not doctrine — and the two commands that get the agent-backed
version.

**The guard RUNS the installers against a throwaway `HOME` rather than reading them**,
and that decision was forced twice. The first version scanned the source for the printed
string — and the first draft of this very fix defined `discloseAgents()` and never
called it, which satisfies a source scan exactly. The second was defeated by a
substring: `bin/task-pipeline.js` already prints *"Any agent (70+): npx skills add…"*,
about the seventy agent products this skill installs into, and a check for the word
`agent` passed it while the real gap stood untouched. It matches `agents/` with the
slash, in output, from a real run. Three planted defects watched being refused, the
dead-code one included.

### The R-005 read of T-3 — fourteen findings, and two of them were critical

The reader that standing instruction `R-005` requires was given the wave and told to
defeat it. It did, and the two worst were in checks written that same hour:

**The new schema check read the rule's shape and never its behaviour.** It asserted
that `parked_reason` carried a `pattern` — and `"^.*$"` is a pattern. Swap it in, drop
`minLength`, and the whole gate stays green over a schema that accepts `parked_reason:
""`. This is the fourth time this file has been defeated by the same class: a name in
`required` constraining nothing, a nullable type, a decorative `items`, and now a
pattern that matches everything. **The check now RUNS the regex** — it must reject
`""` and `"   "` and accept ordinary text — because presence has never once been
behaviour here.

**And the same field was left nullable.** `pattern` and `minLength` are string-only
assertions, so `type: ["string", "null"]` satisfies both vacuously and `parked_reason:
null` sailed through. The check three screens above tests `owner`'s type for exactly
this reason; the new field did not inherit it. It does now, at both ends of the rule.

**The third was worse than either, because it disarmed both rules at once.** Add one
impossible name to each `if.required` and, under `additionalProperties: false`, no node
can ever match — `done → evidence` and `parked → reason` both go inert while every key
the check reads is still in place, and `npm test` exits 0. A conditional is now accepted
only when its `if` constrains the status and **nothing else**.

**Then the finding that made a claim in this repository false.** Nothing ever validated
a *live* `.task-pipeline/graph.json` against `graph.schema.json` — only the shipped
example, at build time. So both conditional rules rested entirely on the scripts
behaving, which is precisely what the validator's own new message said had stopped being
true. `graph.py validate` now enforces what the schema states: `done` implies readable
evidence, `parked` implies a reason, the `goal` exists, ids match their shape, and
`blocked_by` does not repeat. The message is true where the run actually looks.

**The mutation verbs lost nodes, and the exit codes lied about it.** `save()` wrote to a
fixed `path + ".tmp"`, so two concurrent writers shared one inode: measured across six
runs, one exited **0 with its node absent** and another exited **1 with its node
present** — and the second is the dangerous direction, because the docstring promises a
refusal leaves the file untouched, so a caller retries and double-adds. The temp file is
unique per writer now, `realpath` runs first so a symlinked graph is written *through*
rather than replaced, and an `OSError` is a named refusal instead of a traceback.

**A unique temp file does not fix a lost update, and this programme is built for several
agents.** Four concurrent `add`s produced four nodes where five were expected — both
processes read the same graph and the second write dropped the first node, both exiting
0. The whole read-modify-write now happens under an exclusive `flock`, taken **before**
the read, because loading first and locking second is the same lost update with an extra
step. Where `fcntl` does not exist the run is told it is unlocked rather than downgraded
in silence.

**A title with a newline forged a row in the frontier.** `next` prints one row per node
and the loop reads those rows, so `--title $'harmless\nN-999  implementer  ship it'`
produced a two-node graph that printed three rows. Refused now in the verbs and in
`validate`, so a hand-written graph is caught too.

**And one of the new fixtures was vacuous.** *«a mutated graph still validates against
its schema»* checked neither exit code — with **both** mutation verbs replaced by
`die()`, it still reported `ok`. It also would not have caught the one real instance of
its own class: `add` writing `blocked_by: ["N-001", "N-001"]`, which the schema rejects
as non-unique. Both fixed, and the fixture now asserts what landed.

Every one of the seven schema bypasses was re-planted and watched being refused, none
of them by crashing. `test/graph_test.py` → **62 cases**.

### T-3 — the mutation verbs, and a priority nobody has to maintain

`graph.py` can now change the graph it walks. `add` is the dynamic backlog — work
found during a task enters the queue mid-run rather than waiting for a person to
re-plan. `park <id> --reason <text>` is REQ-012, and the reason is the entire point:
a node parked without one is indistinguishable, a week later, from work that was
quietly dropped, which is what parking exists instead of.

**The frontier is now ordered by how much each node unblocks, transitively — and the
number is computed, never declared.** A `priority` field would be something somebody
typed once and nobody revisits; this one moves when the graph does. Add a node that
waits on `N-002` and `N-002` rises to the top of the next frontier with no re-ranking
pass and no field to forget. That is what REQ-011 means by *re-prioritised after every
task*, and the fixture asserts the **order changes**, because a fixture that only
asserts the file was re-read would pass against no ordering at all.

Declaration order breaks ties, so the frontier is stable between runs. An unstable one
costs more than it looks: an agent that calls `next` twice gets a different first row
and starts the other node.

**`park` refuses without a reason, and "without" has four shapes.** Only the first is
argparse's: the flag absent (exit 2, usage), the flag empty, the flag whitespace, and a
reason already recorded that a second park would overwrite. The last one refuses *and
quotes the reason it is protecting* — the first reason is the one somebody wrote at the
time, and the second park is usually someone who has forgotten it.

`add` checks every shape before appending, so **a refusal leaves the file byte-identical**
and a caller can retry without first working out what the failed attempt did. Ids are
allocated from the **maximum in use, never the count** — ids stop being contiguous the
first time anything is renumbered, and from that moment counting hands out one that
already exists. Both verbs refuse outright on a graph that was *already* invalid and say
so in those words: a mutation that reports pre-existing damage as though the caller
caused it sends the next fix to the wrong place.

`save()` writes to a temp file beside the graph and `os.replace`s it. A crash mid-write
now loses the mutation instead of the queue. This repository has destroyed a file by
writing it in place twice, and both times what saved it was a copy somebody had made by
hand.

**REQ-012 moved from the script into the format.** The reason used to live in `note` —
a free-text field with no description and no rule, which made a park carrying a reason
and a park carrying an unrelated remark the same shape to every reader and every check.
It is `parked_reason` now, **required by the schema when the status is `parked`**,
exactly as `evidence` is required when the status is `done`, with the same
non-whitespace `pattern` the wave-2 convergence check taught this file to write.

**And that broke a guard, which is the guard working.** draft-07 allows one `if`/`then`
per schema object, so the second rule went into an `allOf` beside the first — and
`test/validate.py` read `node["if"]` literally and went red immediately. It walks `allOf`
recursively now, so a schema stating both rules inline, both in `allOf`, or one of each
reads the same. Six planted defects were watched refusing, including the inverse: the
old inline shape is still accepted, which is what a widening has to prove it did not
break. Two of the six are now CI plants; the section's running count is at the top.

`test/graph_test.py` → **52 cases**.

### Wave 2 — T-4 and T-6, and the check `build.md` puts over a fan-out

`agents/verifier.md` ships — the first agent this plugin has. It closes one node and
returns a six-key verdict, and `graph.py`'s `verdict_violations()` refuses one that
omits a key or claims `done` with no evidence. The agent file says what it cannot do
and why that matters: **it cannot ask the operator anything**, so a verdict meaning
*«I need a decision»* has to say so in `replan.why` rather than end in a question
nobody will see.

`pipeline.json` moves to `mode: dynamic` — `interval` dropped, because the schema
calls it meaningless there — and records `release.goal`.

**Then the convergence check `references/build.md` §4.2a requires over a fanned-out
group, and it earned its place.** Nine contradictions, every one of them invisible to
the three per-task reviews that had already passed:

| Found | Between |
|---|---|
| the verdict gate accepted `evidence: ["", "  "]` that the **schema refuses** — `close` would write a node its own shipped schema rejects | `graph.py` ↔ `graph.schema.json` |
| `release.goal` was undeclared in the schema, so the guard T-6 shipped **could not see the field T-6 shipped** — `additionalProperties` is true, and renaming it away kept every gate green | `pipeline.json` ↔ `pipeline.schema.json` |
| `ROLES` held ten of the brief's thirteen — and its own refusal message **named the manager while the set rejected it** | `graph.py` ↔ the brief |
| `verifier.md` told an agent to run `graph.py close`, which is T-5 and does not exist | the agent ↔ the script |
| `_goal_note` claimed the goal is *"printed above the frontier every iteration"*; nothing prints them together | the config ↔ the script |
| the schema's `queue` cited `continuity.md`, which still describes a two-item queue set that does not include `work-graph` | the schema ↔ the doctrine |
| the brief's REQ-005 required `plugin.json` to **declare** `agents`, and declaring it fails `--strict` | the brief ↔ the platform |
| *«five keys»* over a six-key object, in five places | everywhere at once |
| T-6's new guard shipped with **no negative self-test**, against this repo's own stage-6 gate | the change ↔ the gate |

Every one is fixed. Two are worth naming for the shape rather than the fix:

**`ROLES` conflated two different axes.** Whether a role ships as a subagent and
whether it may **own a node** are separate questions, and the first draft answered
the second with the first. `manager` and `business-analyst` are main-thread doctrine
*because* their job is asking the operator — that is precisely why they cannot be
agents, and it says nothing about whether work can belong to them. Both own nodes
now; `project` still cannot, because the brief defers it for having no stated job,
and a role that cannot say what it does cannot own work either.

**And the fix for the evidence bug was itself incomplete.** A cross-check fixture —
asking the gate and the schema the same question and requiring the same answer —
caught `["  "]` surviving one and not the other: the gate strips, and `minLength: 1`
counts a space. The schema now requires a non-whitespace character, and the fixture
that found it is in the suite.

`test/graph_test.py` → **29 cases**. Two of them were added here.
## v1.68.0 — the worst body in the family, and the rule that was wrong about it

**6685 tokens against a 5000 budget → 4735**, under the 4750 working limit, by
splitting rather than trimming. This was the largest `SKILL.md` body in the
ssheleg family and the furthest over — 34% — and the body loads on every turn of
every session that resolves the skill.

Most of the overrun sat in the **stage table's Gate column**, which restated
`references/stages.md` under a heading that literally says *(detail in
`references/stages.md`)*. The table is the index and the run order now; the
reference is what you read while standing in the stage. Nothing was deleted:

| Moved | To | Why there |
|---|---|---|
| Stage 10 in a project of several repositories | `references/acceptance.md` | it owns stage-10 close-out |
| Step 5's cross-cutting rules | `references/gates.md` | they fire at any stage, not inside step 5 |

and five *Prerequisites* paragraphs that restated a reference in full were cut to
the rule plus the failure it prevents — which is what a body is for — with the
procedure left in the file that owns it.

**All 38 routed trigger phrases across both skills survive verbatim**
(`node test/advertised_check.js`), and the stage list still matches across the
three surfaces the validator compares mechanically.

### The description rule was wrong, and this repository was already right

The family's shared auditor demands a description **start** with `Use when …`.
This repository's own validator refuses exactly that, and its comment says why:
Anthropic's guidance asks for **both** halves — what the skill does and when to
use it — and their own example leads with the capability (*"Extracts text and
tables from PDF files… Use when working with PDF files."*). Demanding `Use when`
at position 0 enforces the WHEN half and leaves the WHAT half optional.

So the 2026-08-16 audit's finding that this description *"does not open with Use
when, against the house rule its sibling obeys"* is **withdrawn — the house rule
is the one that is wrong**, and this repository had corrected its own copy of it
already. Applying the corrected rule to the family measures **22 of 24 skills**
opening with the trigger, so flipping it rewrites 22 descriptions that carry live
routing phrases. That is a family decision rather than a member's, and it is
filed as umbrella `B-76` rather than taken here.

### Fixed

- A negative self-test was pinned to a literal containing a **line break**, so it
  stopped landing the moment the paragraph reflowed — the guard then read green
  while proving nothing. Matched by regex now. Same class as the two that refused
  `seo-aeo-audit`'s release earlier the same day, and the reason the local gate
  there learned to catch it before the tag.

Guards: 351 → **351**. No guard was added or removed — one plant was repaired, and
the suite that reports `all 351 guards provably reject their planted defect` was
red until it was, which is the whole point of counting them.

Found by the nine-repository audit of 2026-08-16 (umbrella `B-66`;
`F-task-pipeline-01`, and `F-task-pipeline-02` withdrawn).

## v1.67.0 — a ledger records two different things, and most record only one

**A ledger records two different things, and most record only one.** *What confirmed it*
is evidence — a command, a CI run id, a fixture name. *Whether a person looked* is the
`Human` axis, and it is the only one the exposure line is defined over.

Measured across this family: nine repositories, **ten** header shapes, **815** rows.

| what the state column can say | rows | repositories |
|---|---|---|
| whether a **person** looked (`Human`) | **126** | 1 |
| a date and what was watched (`Last verified`) | 180 | 1 |
| `verified` — by a person **or** a command, indistinguishable | 391 | 4 |
| nothing: evidence recorded, no state column at all | 118 | 3 |

So `never` is measurable in **one repository of nine, over 15% of the rows**, and the
number this doctrine is written around is undefined in the rest. That is not a defect in
those ledgers — recording what confirmed something is the Auto job done properly. **The
defect is doctrine that speaks as though the column were there**, so `references/verification.md`
now states the split, and three rules follow from it: where there is no state column the
line says so and prints no number; a `verified` that cannot separate a person from a
command may not be reported as human confirmation; and adding the column later never
reaches backwards, because a back-filled ledger answers the question wrongly instead of not
at all.

`exposure.sh` also stops calling a self-explaining status unreadable. `**observed** — the
row exists because the miss happened in this run` is an ordinary way to write a state, and
four rows in this family were reported unparseable for explaining themselves. The
vocabulary now matches the **leading word**, with the empty cell tested before the word is
taken so a blank still counts as unconfirmed.

Guards: 351 → **351**. Fixtures 20 → **20**; these are behaviours the existing cases
exercise by running the script, and all nine family ledgers were run through it by hand.

## v1.66.0 — the shape is not fixed, so nothing may assume it

**The check-list printed the size of the work labelled as who it hurts, in every seeded
project.** `exposure.sh` read the board's blast radius from column 5. That is `Blast` in the
family umbrella's eight-column board and **`Size`** in the ten-column board this repository
seeds, so a host project got `[blast L]` — a work-size letter presented as a severity.

It shipped for a full release **two lines away from where the same lesson had just been
applied to the ledger's status column**. Fixing one instance of a class and leaving the
other in the same file is the recurrence this repository's retro already names.

Blast is resolved by header now, and two fixtures hold both shapes: the ten-column board
must yield `[blast 3]` and not `[blast L]`, and the eight-column one must not regress. A
third case asserts that a board with **no** blast column prints no blast at all — an
invented weight is worse than a missing one, because it looks like data.

**The rule is written down rather than left as two fixes.** `references/backlog.md` gains
*The shape is not fixed, so nothing may assume it*: resolve every column by header name,
once per section and knowing a file may hold more than one shape; treat an absent column as
absent; and name the column in the output where the reading depends on it. Two board shapes
exist in this family and five ledger shapes, all documented in their own headers, and none
of them is wrong — reading any of them by position is.

Fixtures 18 → **20**. Guards: 351 → **351**; these are behaviours of the seeded script,
which the fixtures exercise by running it.

## v1.65.0 — a decision is not debt

**`open` is work not done, `dropped` is an idea abandoned, and neither fits a deliberate
*no*.** Putting a decision in `open` has a cost that only appears later: **it accrues age
exactly like debt and eventually outranks real work.**

Measured on 2026-08-16. Two rows in the family umbrella recorded decisions on 2026-08-06 —
one waiving a UX chain in favour of fixtures, one keeping a skill an audit because another
router carries the design-time rule. Both sat `open`. The moment the age term started being
computed they reached the **top** of that board at 2.67 each, and the next run spent itself
re-deriving two decisions that were correct when made and are still correct.

So `waived` is a state: not counted open, no priority (`—`), and it must name what would
bring it back. **The `revisit:` clause is mandatory and gated** — a waiver with no trigger
is a row nobody will reconsider, and the trigger has to be something a later run can
measure. *"The command surface grows past what the fixtures describe"* is checkable; *"if
it becomes a problem"* is not.

The doctrine also requires the condition to be **re-derived when the row is touched**, like
any other claim. Both umbrella rows were re-measured before being waived — 8 CLI commands
with 0 uncovered by fixtures, and a router that still states the rule — because a waiver
resting on a condition nobody has checked is the same expired claim in a quieter voice.

Guards: 349 → **351**. Both new plants watched rejecting their defect: a waived row that
keeps its priority, and a waiver that names no trigger.

## v1.64.0 — the exposure line reported a clean bill on ledgers it could not read

**The exposure command reported a clean bill on ledgers it could not read.** Shipped two
releases ago keyed on POSITION — `NF >= 7`, status in field 7. Run against the family
umbrella's four-column ledger it found **four rows out of 298**, because those four happen
to contain a `|` inside inline code and so crossed the field count by accident, and from
them printed:

```
exposure: 0 unverified · never checked · 125 releases carry one
         every shipped row carries a human confirmation
```

The most reassuring sentence available, derived from punctuation, in the one tool whose
stated purpose is to stop silent greens. Its own two halves contradict each other and the
fixtures did not notice.

**The status column is now found by name, per section, and the order matters.**
`sheleg-design` carries both `Last verified` (a date and the thing watched) and `Status`
(which holds `**green**`); preferring `status` read the gate instead of the person and
reported 174 confirmations. Preference is `Human`, then `Last verified`, then
`Status`/`State`. **`Verified by`, `Confirmed` and `How it is checked` are deliberately not
status names** — five members hold shell commands under those headers, and a column of
commands read as a column of statuses is how `python3 test/validate.py` became a status
nobody could parse.

Three further corrections, each of which was hiding a real row:

- **Bold is stripped before matching.** These ledgers write `**never**`, not `never`.
- **A shrug is not a clean bill.** A status that is neither a date nor a known word gets
  its own count and its own list, and no clean bill prints over it.
- **Only a `Human` column licenses the word "human".** The umbrella's ledger defines
  `verified` as *a person **or** a command*, so a confirmation drawn from `Status` now says
  which column it came from.

Measured across the family afterwards: `task-pipeline` **126 unverified**, `sheleg-design`
1, and `seo-aeo-audit`, `super-ux` and `agent-sync` **dormant — no status column at all**,
which is the truth their shapes support and not a zero.

Fixtures 14 → **18**, the four new ones named for the exact silent green.

Guards: 349 → **349**. No new plant: every one of these is a behaviour of the seeded
script, which the fixtures exercise directly by running it.

## v1.63.0 — the row you are about to work is a claim, and it has a date

**A board row states the world at its `Source` date and says nothing about now.** Three
rows expired inside one day on 2026-08-16 — one recorded a script and thirteen green
fixtures as *built and parked* when every artifact had been deleted, one named six files
belonging to another repository where a sweep found eleven, one said the graphs were
frozen at a date nine days old when every one had been rebuilt. None was wrong when
written. Each was caught only because the cycle that picked it up happened to measure
first; nothing required it.

`references/knowledge-sources.md` gains the rule beside *Carried-in claims*, which covers
the sibling case of what a run inherits about itself: **re-derive the row's checkable
claims before acting on them, and correct the row in the same run.** Most name something a
command settles — a file, a count, a commit, a version, a green suite. What no command can
settle is acted on as an assumption, out loud.

It also names the sharper half, which is arithmetic rather than prose: **a row's derived
columns decay and nothing notices, because the number still looks like a number.** A rank
computed from an age term is wrong the moment the age moves. If a board computes a
priority, something must recompute it — a promise in the header that it happens at stage 10
is not a mechanism.

Guards: 349 → **349**. No new plant, and the reason is measured rather than asserted:
across the seven open rows the family carries, the checkable claims total **two file paths
and one count**. A gate over that corpus would pass everything and read like coverage.

## v1.62.0 — a board row that says work exists names where it lives

**`open` claims nothing exists. `parked` claims something does — and now has to say
where.** B-58: a row read as ready-to-merge for two days while its artifacts had already
been deleted. It said *"built and parked … held at `scratchpad/b29-exposure/`"*, a
session-scoped temp directory, and when a run finally went to land it nothing on disk, in
git history, in a stash or in a dangling object held any of it. **A board cannot tell a
claim about a filesystem from a claim about a repository**, and that row was the first
kind while reading like the second.

The status cell of a parked row now carries a branch or a commit, and two rules gate it:
an open row may not home its work in a per-session directory, and a `parked` status
without a ref is refused.

**A prose detector was written first and thrown away.** Matching *"parked"*, *"is built"*,
*"ready to merge"* in the description cell fired on **three rows out of 187 and every one
was false** — two closed rows narrating this incident and the row that asked for the rule.
A check whose every current hit is wrong teaches evasion; what ships reads the status
cell, which is never prose, and both rules measured **zero** across 191 rows including the
templates.

The first draft of the guard read `cells[-2]`, which is the status in an eight-column
board and the *Home* column in the ten-column template — so the parked rule examined the
wrong cell and reported nothing, fifty lines below the comment explaining why positional
reads fail on this corpus. It is position-free now, and the plant that was silently
passing is the one that proved it.

Guards: 347 → **349**. Property checks: 9 → 9.

## v1.61.0 — the command that was built, parked, and lost

**The exposure command lands, two days after it was declared built.** B-43 recorded
`templates/exposure.sh` and its fixtures as finished and parked in a session scratchpad,
blocked only on a concurrent release. The scratchpad was cleaned; nothing on disk, in git
history, in a stash or in a dangling object held any of it. **The row described work that
no longer existed**, and nothing would have said so until someone went to merge it.

So it is rebuilt, and this time the validator asserts it: a seeded shell script must
exist, must carry a shebang, and must still be named by the doctrine that tells a project
to copy it. All three watched failing.

`exposure.sh` turns [`verification.md`](plugins/task-pipeline/skills/task-pipeline/references/verification.md)
into the line and the check-list `references/exposure.md` specifies, so a host project
gets the number without an agent in the room. **It exits 0 whatever the number is** — a
threshold here would be a target on `never`, and the cheapest way to satisfy such a
target is a date nobody earned.

Three of its fourteen fixtures caught real defects in the first draft, all of them lying
in the reassuring direction:

- `$(grep -c "" f || echo 0)` prints **two** zeroes when nothing matches — grep prints its
  own 0 and exits 1, so the fallback runs as well. The variable became `"0\n0"`, every
  numeric test after it died with *integer expression expected*, and the script fell over
  precisely in the case that means "everything is confirmed".
- BSD `sort` exits with *Illegal byte sequence* on the non-ASCII `What` column under a
  UTF-8 locale. The error went to stderr, the check-list came out **empty**, and the
  count above it still said 126 unverified. A list that silently empties is worse than no
  list.
- Byte-wise `substr` cut a Cyrillic letter in half. Truncation is by whole words now, which
  cannot land inside a character.

Guards: 344 → **347**. Property checks: 9 → 9. Three new plants: the seeded script
disappearing, the doctrine that stops naming it, and a percentage reaching the exposure
line — the last because the doctrine says *no percentage, ever*, and a later hand adding
`(N%)` would be adding it to look helpful.

## v1.60.1 — the gate can see an invariant it breaks elsewhere

**This gate can now see an invariant it breaks one repository away.** The family umbrella
routes work by matching a prompt against a table in `lib/triggers.js`, and every trigger
there must be a word this skill's own `description` advertises. Nothing here knew that
table existed. On 2026-08-16 `sheleg-design` 1.37.0 shipped green having dropped a phrase
that was still a live trigger, the umbrella found out minutes after the tag, and it cost a
patch release — because the member releases FIRST and the umbrella re-pins after.

`test/validate.py` now asks the umbrella's own checker (`test/advertised_check.js`), which
reads the module the hook itself calls. **No copy of the table lives here**, so there is
nothing to drift. With no umbrella above this checkout — a standalone clone, and CI — it
discloses rather than passing, because a check that cannot look must never read as one
that looked.

Guards: 344 → **344**, and the reason no plant joins this repository's own suite is the
check's shape. It only sees anything when an umbrella checkout sits above this one, which
is never true in this repository's CI — a negative self-test here would have to assert a
refusal that cannot happen. The plant lives where the submodules exist: `sshlg-skills`
runs one against every member's own gate.

Watched refusing a real drop before shipping: every one of the seven members carrying
routed triggers had one of its own advertised phrases removed and every one of them failed
its own gate.

## v1.60.0 — the gate this skill ships had never run on this skill

Wiring it in was one line. Running it once found five things, and each was silent in a
different way:

- **It was skipping itself in every submodule checkout.** The section asked `[ -d .git ]`,
  and a submodule's `.git` is a *file* holding a `gitdir:` pointer — the same shape that
  disarmed two negative self-tests in v1.58.0, now found a third time in two days, in the
  shipped gate. It asks `git rev-parse --is-inside-work-tree` now, which knows all three
  shapes.
- **Its corpus default still named the artifact root as it was before the 2026-08-13
  rename**, so in every migrated project the SHA and propagation sections found nothing and
  reported **dormant** — which reads exactly like having nothing to check. The root is
  resolved now, new name first.
- **Eleven commit references could not be followed.** Nine are pre-gate history rewritten
  early in this project's life, one is a documentation placeholder that never named a
  commit, and two were branch commits a **squash merge** had replaced — which is the same
  class as the amend above, arriving from a different direction. The two were repointed to
  the commits that carry their work on `main`; the other nine are **enumerated by name**
  in the archive with their date and reason, so the gate passes over exactly those and
  fails on the twelfth. An exception with names, never a floor.
- **Two decisions named documents that never cited them.** `DEC-0001` and `DEC-0004` are
  now cited in `progress.md` and `companion-skills.md` — which is the propagation contract
  working the moment anything checked it.
- **One id was reported undefined because the checker could not tell a plant from a
  claim.** A retro entry recording *planted `DEC-0009` while the highest defined id was
  `DEC-0001`* was read as a citation. A line describing a planted defect is sample content
  by the same argument as a fenced block, and `strip_asides` now treats it as one.

`npm run test:docs` is a script, and `test:all` calls it, and a guard requires both — a
gate nobody's aggregate command runs is a gate that goes quiet the first busy week.

Guards: 344 → **344**. The change is a gate script and its wiring; every finding above
was watched being produced by the gate itself, which is the only plant a script that
reads a project's own git history can have.

## v1.59.0 — never amend a commit a record already names

### Fixed

- **The stamping procedure invited the defect it then had to repair, twice in one
  close-out.** `retrospective.md` says stamp the run with its own commit; the only way to
  know that commit is to make it; so the stamp gets folded in with `--amend` — and the
  amend mints a new SHA, leaving the stamp naming a commit that resolves on the machine
  that wrote it and reaches no clone. It happened here on 2026-08-16 and then again in the
  umbrella twenty minutes later, which is a procedure fault rather than two lapses.

  The doctrine now says it in one line — **once a file names a SHA, that commit is
  frozen** — states the order that removes the temptation (commit the work, *then* stamp in
  a commit of its own), and names the only repair that does not re-enter the loop: a
  follow-up commit, never a second amend.

- **The documentation gate asked the weaker of the two questions.** It required every
  backticked SHA in the retro to *resolve*, and an amended-away commit resolves for as long
  as the object survives locally. It now also requires **reachability from `HEAD`**
  (`git merge-base --is-ancestor`), which is the question a reader two months later is
  actually asking. Watched failing on a purpose-built repository whose stamped commit had
  been amended away: `commit ... resolves but is NOT reachable from HEAD`.

- **Three id registers that could never allocate are removed** (`B-45`). They were declared
  over the `fs` backend, whose `reserve` refuses by design, and `agent_sync.py check` had
  been calling it a problem for as long as they stood. A declaration that cannot be served
  is worse than none: it reads as a capability, so nobody writes the procedure it hides —
  and on 2026-08-15 two sessions filed a different `B-073`. Allocation is manual, documented
  in `CLAUDE.md`, and the guard that requires that documentation now fires on the **backend**
  rather than on the declaration, so removing the registers could not retire it.

Guards: 344 → **344**. Property checks: 9 → 9. No new plant, and that is the honest
number: what changed is a gate script (`templates/docgate.sh`) rather than a validator
guard, and it was watched failing against a purpose-built repository whose stamped commit
had been amended away — the plant lives in that measurement rather than in the workflow,
because a gate that runs over a project's own git history cannot be planted from inside a
copy of this one.

- **The coordination snapshot exists and is linked.** `docs/AGENT_SYNC.md` was missing
  entirely, which `check` had also been reporting. Generated from the live configuration and
  linked from `CLAUDE.md`; `agent_sync.py check` → **exit 0, `setup healthy`**, for the first
  time in this repository.

## v1.58.0 — a fan-out is not finished when its branches are

The graph model this pipeline was audited against in v1.57.0 named one defect and fixed
it in one place. Applying the same model to the rest of the skill found the same defect
in **three more**, and they are the same sentence each time: work fans out, the branches
each go green, and the node that consumes them trusts them because they arrived.

### Added

- **The harvest is a convergence, and now it has a check.** Stage 0 queries the code, the
  graph, `CLAUDE.md`, the ADRs, the docs, past briefs, the wiki, the board — all
  independently — and lands them in one brief the interview then treats as a single
  answer. Phase 2 checks each *answer* against the harvest; **nothing compared the sources
  with each other**, so a doc contradicting the code produced two rows that each looked
  fine and the run followed whichever it read last. The ledger now carries a
  `Contradictions:` line with four things to look for, and the stage-0 gate reads it.
  `Contradictions: none` is the answer most runs write, and writing it is the point.

- **Stage 3's COPY and VISUAL tracks are a parallel layer, and their convergence has a
  check.** Neither consumes the other — copy is written from the scenarios and the brand
  pack, the visual from the frame and the style pack — so the order they were written in
  was a fake edge teaching a run to wait for a result that never arrives. What they do
  share is the screen, which is where the real failure lives: **each track is right alone
  and they disagree together.** A label the layout has no room for, a state one drew and
  the other never wrote, two names for one component, a tone the motion contradicts.

- **Stage 9's three artifacts are named as a convergence**, and the graph↔docs divergence
  check as its gate rather than a nicety — it is the only thing that compares two of the
  three outputs against each other.

Guards: 339 → **344**. Property checks: 9 → 9. Five new plants, one per branch of the
three new checks, each anchored on a heading and each asserting it changed something.
Two of the five were broken on their first run and both failures were mine: a grep
pattern one character short of the message it looked for — **the same class fixed hours
earlier in this programme and not swept into the new plants**, which is R-003 — and an
assertion looking for the doctrine in the file that does not hold it.

### Changed

- **The stage-4 gate reads both halves of what it requires**, and the id/version
  allocation this repository actually uses is written down. `.claude/agent-sync.json`
  declares three id registers over an `fs` backend whose `reserve` refuses by design —
  correctly, since *pretending would hand two agents the same id* — and the declaration
  read as a capability, so nobody wrote the manual procedure it was hiding. On 2026-08-15
  two sessions filed a different `B-073` and two branches claimed one version number.
  `CLAUDE.md` now carries the three-step allocation (lease first, compute from the
  **committed** file, commit before releasing) and the version rule (`git ls-remote --tags`,
  because a local checkout is not where the answer lives), the shipped doctrine in
  `documentation.md` carries the generalisable half, and a guard requires both.

### Fixed

- **Two concurrent runs of `test/negatives.py` no longer corrupt each other** (`B-075`).
  Every step copies the repo to a **fixed** `/tmp` name, which is right in CI — one runner
  per job — and wrong on a machine where a second suite is already running. The runner now
  serialises the runs instead: an exclusive lock for the duration of the suite, so a second
  run **waits** rather than corrupting the first and says so instead of producing a number
  nobody can trust. The 344 workflow steps are untouched — they are the CI contract, one
  runner per job, and they were never the ones colliding.

  **The first fix was wrong and is worth recording.** It rewrote every `/tmp/...` path in a
  step's script to a per-run name, and it broke two plants whose payload **is the workflow
  text** — they search the copied workflow for a literal path in order to duplicate it. A
  mechanical rewrite cannot tell a path being *used* from a path being *discussed*, which is
  the umbrella's standing instruction #7 met for the second time in two days, both times by
  the same author. The suite caught it; reading did not.

  **Watched both ways, under real overlap.** Before, two concurrent runs of one selector
  returned `1 guard did not fire, 7 broken` and `8 guards did not fire` — two different
  wrong answers about a tree that was not changing. After, both return `all 8 guards
  provably reject their planted defect`, exit 0, with the second printing that it waited.

## v1.57.0 — an arrow that carries nothing is not an arrow, and two green diffs can still contradict each other

The pipeline has drawn a dependency graph at stage 4 since it had a stage 4, and grouped
tasks topologically off it. What it never said was how to tell a **real** edge from one
that only records the order somebody typed the tasks in. The self-review asked the right
question in a checklist line — *does this `depends:` point at a task that really produces
what's consumed* — and no gate read the answer, so a plan could serialise itself entirely
and pass every check.

Audited against *Graph Engineering with Claude*
(`https://x.com/Mahaximus_/status/2082442856417956173`), findings and both rejections in
`docs/evidence/specs/2026-08-15-graph-audit.md`. **Nine of the ten macro stage edges carry
data**, which is the audit's first result and the reason nothing was reordered.

### Added

- **The fake-edge test, as a numbered procedure** (`references/planning.md`). Six steps
  over the graph you just drew: for each arrow, does output from A actually enter B, and if
  you cannot name what crosses it, delete it. Expect two or three per plan.

- **A `Carries` column in the *Execution order* table**, and it is the whole mechanisation:
  a cell you cannot fill **is** the finding. The fake-edge test stops being a thing an agent
  remembers to do and becomes a column a reviewer can see is empty.

- **`Edges: <n> declared, <n> carry data, <n> removed`** in the stage-4 self-review, and
  the gate reads it. Computed, like every other line in that block.

- **The group convergence check** (`references/build.md` §4.2a). A per-task review reads
  **one diff**; a fanned-out group produces several, and the defect that exists only
  *between* two of them passes both. One check over the group's reports and diffs together,
  after the last task and **before the first worktree is integrated** — the only moment all
  of them exist and none has landed. Five things it looks for, each a real defect invisible
  in a single diff: an empty deliverable, two outputs that cannot both be true, off-brief
  work, one REQ satisfied twice differently, a Global Constraint only one task applied.
  **A clean group logs a line too**, because a check whose silence is indistinguishable from
  not having run is not evidence.

- **A statement that this pipeline is a static graph, and why** (`references/planning.md`).
  Auditability: a graph that decides its own shape produces a shape nobody drew, and then
  *"here is the pipeline"* and *"here is what this run did"* stop being the same document.
  The two places the run **does** discover structure — the module map and the carry-over
  ledger — are named, and both land in a committed artifact, which is what separates
  discovery from a dynamic graph.

- **A preference for a harness-native fan-out primitive**, on the same reasoning §1 already
  applies to worktrees: the harness owns the concurrency cap, the isolation and the resume.
  Stated **without naming a product** — the keyword for one host's fan-out was renamed six
  weeks after the article documenting it, and doctrine pinned to a vendor's noun rots on
  that schedule.

### Fixed

- **`test/negatives.py` could not restore `.git` in a submodule checkout, so two guards
  silently never fired.** The restore was gated on `os.path.isdir(.git)`. In every checkout
  of this repository **as a submodule** — which is how the `sshlg-skills` umbrella ships it,
  and therefore how most work on it happens — `.git` is a 48-byte file holding a `gitdir:`
  pointer, so the branch was skipped and both git-dependent guards reported `fatal: not a
  git repository` and were counted as *did not fire*. CI clones normally and was green,
  which is why it survived. Measured before: exit `1`, `2 guard(s) did not fire`. After:
  exit `0`, **all 318 guards**, twice consecutively.

  The copy resolves the `gitdir:` pointer and **copies** the directory rather than pointing
  at it, for two reasons that both bite: a plant that commits would otherwise move the real
  branch, and the module's config carries `core.worktree` aimed back at the live checkout,
  which would make every git command inside the snapshot operate on the tree the snapshot
  exists to protect. That one key is stripped from the copy.

- **The fan-out rule was stated with three conditions in `build.md` and one in
  `stages.md`.** The summary kept *own worktree* and dropped *same group* and *exclusive
  file ownership*, so a reader who took the summary as the rule would fan out two tasks that
  share a file, in separate worktrees, and meet the conflict at integration. Both surfaces
  now state all three.

- **A property check's plant had gone narrow one column over, and CI is what found it.**
  *The Human column survives a header reorder* rewrites the ledger's header and then swaps
  each row's two last cells — matching on `| <auto> | <human> | — |`, with the `—` a
  literal. Seven rows added by this run carry a finding id in `Note` instead, went
  unmatched, stayed in the old order under a reordered header, and the check reported the
  **doctrine** broken when the **plant** was what had aged. It had already been widened once
  for exactly this reason one column to the left, which is what makes it a class rather than
  an incident: a plant anchored on the CONTENT of a cell describes the table it was written
  against. It now matches any note.

Guards: 322 → **339**. Property checks: 9 → 9. Seventeen new plants, because a rule a check
can decide is written as the check and not as prose somebody remembers: the fake-edge test
renamed away, the `Carries` column dropped, the stage-4 gate no longer reading it, §4.2a
deleted outright, §4.2a losing its *before integration*, and `stages.md` dropping the
convergence check from its stage-5 summary — which is the exact drift F-5 found, now
guarded in the direction it drifted. The other eleven came from **an independent reviewer
across five rounds on the PR**, which is the mechanism standing instruction R-005 exists to buy: it found four
branches of the new guards with no plant behind them, a `_section()` site with no
`is None` arm (the shape every other site in the file has), a stage-5 guard checking one
of the three preconditions its own message claims, and an uncached read of a memoised
document. It also found the two gaps that were not nits — see below. Every plant is
anchored on a heading or a token, and every one asserts it changed something before the
validator is asked.

**Two of the reviewer's findings were defects, not nits, and both were fixed before
merge.** First: the convergence check was written into narrative prose and into
`SKILL.md`'s stage table, and **into neither GATE bullet** — so a fanned-out group could
reach stage 6 having never run it. `build.md`'s and `stages.md`'s gates now require it,
and a guard requires the gate to require it. Second: the `.git` restore resolved a
`gitdir:` pointer by hand, which is right for a submodule and **wrong for a linked
worktree** — the shape `build.md` itself tells every run to work in, where `objects`,
`refs` and `config` live wherever `commondir` points. It now asks
`git rev-parse --git-common-dir`, which answers correctly for all three shapes. A fix that
covers one of two shapes of the same defect is half a fix.

### Not changed, deliberately

- **Stage 8 → 9.** The audit's F-4 asked whether docs depend on the post-deploy check or
  only on the version stage 7 produced. Rejected with reasoning rather than left open: a
  single agent session runs serially so removing the edge buys no wall-clock, and a
  post-deploy check can change what stage 9 must write. Weak is not the same as fake.
- **The stage list, the stage count and every gate type.** Gate *criteria* moved at stage 4
  and stage 5; nothing was renumbered, reordered or retyped.

**Released as 1.57.0, not 1.56.0.** This work was branched, reviewed over five rounds and tagged in its own tree while a concurrent session merged a different 1.56.0 — the
browser-channel release below. Both branches claimed the number; the id register that would have prevented it is declared in `.claude/agent-sync.json` and cannot allocate
against an `fs` backend, which is the umbrella's open row **B-45**. The same collision took a board id: `B-073` here was renumbered to **B-075**.

## v1.56.0 — the stages demanded a look and named no way to take one

Since v1.36.0 three stages have required the rendered surface to be checked in a
browser, and v1.55.0 gave that requirement a second channel. Neither release said
**how a look is taken**. An agent reading this bundle learned which plugin to install
and nothing about what to do with it — which is precisely how a run reports *checked in
a browser* and means *ran the unit tests*.

`references/browser.md` is that mechanism, and stages 5, 6 and 8, `tdd.md` and both
gate rows in `SKILL.md` now point at it.

### Added

- **The one model both channels share.** A snapshot returns the accessibility tree with
  a **ref** per element, and you act on the ref — not on pixels, not on coordinates. Three
  consequences the doctrine already rested on and had never stated: a look costs a page of
  text and no vision model, a ref is deterministic where a coordinate is not, and **a ref
  that stops resolving is a finding rather than an error to retry past**.
- **The look as four runnable commands** — `open`, `snapshot`, `console`, `requests` —
  with the MCP and `chrome-devtools` names beside them, because the look is the same look
  and that is why the matrix ranks neither.
- **Sessions and the daemon.** The browser lives between commands, which is the whole
  reason the four compose; `-s=<session>` isolates, `list` is the evidence the environment
  is clean, `kill-all` is for the zombie left by a crash.
- **`--json` / `--raw`.** The difference between output a reader reads and output a check
  can gate on. A gate that regexes prose breaks on the release that rewords it.
- **"Tested in a browser" separated into the three claims it conflates** — the look, the
  spec suite (`playwright test`, the runner) and the **library** (`class Playwright`),
  which is an automation API and not a test framework at all. Choosing the library where a
  runner was wanted is how a project grows a half-runner nobody trusts.
- **Auth and mocking as solved steps rather than exemptions.** `state-save` / `state-load`
  (`--storage-state` on the MCP) for a surface behind a login — the state file is a
  credential and goes where credentials go; `route` / `route-list` / `unroute` for the
  failure paths a mocked unit test can never show rendering.
- **The loop that turns a look into a test that keeps it found:** `generate-locator` on
  the element the look caught, then `pause-at` / `step-over` / `resume` to watch the new
  spec see what you saw. A browser finding fixed with no test behind it is a finding
  scheduled to return.
- **What the channel can reach**, because recommending a real browser is the widest
  capability in the matrix: the MCP confines file access to the workspace roots until
  `--allow-unrestricted-file-access` says otherwise, `--isolated` keeps nothing,
  `--secrets` exists so a password reaches the browser and not the transcript — and
  `--allowed-origins` is **not** a security boundary, which is upstream's own wording.

### Measured rather than restated

- **The MCP's tool list is capability-gated: 24 tools by default, 42 with
  `--caps vision,pdf,devtools`** — counted by starting the server and calling `tools/list`,
  not read off a page. `browser_start_tracing`, `browser_start_video` and
  `browser_pdf_save` are **absent** from a default server. A doctrine naming them without
  `--caps` sends an agent to a tool that is not there, and the agent concludes the doctrine
  is stale rather than the server narrow. The page current at the time also listed route,
  cookie and localStorage tools this version does not ship at all — which is why the CLI is
  what this file names for state and mocking.
- Every CLI command and flag in the new file was checked against `playwright-cli --help`
  before it shipped, `--persistent` included, which lives on `open` rather than at the top
  level.

### Corrected before merge, by the reader

- **`npx playwright-cli --help` — this file's own re-derivation command — did not run.**
  Outside a project that has already installed it, npm resolves the bare `playwright-cli`
  to **somebody else's package**: Microsoft's, deprecated in favour of this one, latest
  `0.262.0` against `@playwright/cli`'s `0.1.18`. The line sat inside the sentence that is
  the whole file's evidentiary warrant. It now says `npx @playwright/cli@latest --help`
  and explains the trap.
- **`state-save .auth/state.json` fails on a directory that does not exist** — real exit 1,
  `ENOENT`. The recipe gained the `mkdir -p` it always needed.
- **The prescribed verdict quoted a filtered number as the page's request count.**
  `requests` hides successful static resources by default and says so in its own footer.
  Failures are listed either way, so *no status ≥ 400* survives and *"14 requests"* is
  gone.

### Guards

Guards: 318 → **322**. Property checks: 9 → 9. Two checks: a stage that asks for a browser
channel must **link** the mechanism, and the mechanism must keep the whole look in one
runnable fence inside the section the stages point at.

**Both shipped weaker first, and the independent reader `R-005` requires broke both.**
The pointer check tested the substring `browser.md`, so `<!-- browser.md -->` — invisible
once rendered — satisfied it while the stage named no reachable mechanism. The recipe
check searched the whole file, so the four commands could be parked in a fence captioned
*"the ones this file tells you never to run"*, every needle intact and the recipe deleted;
it also accepted `open` off an incidental mention in the session table. An earlier draft
had already been caught by a `\b` that let `console-messages` satisfy `console`, and
`tdd.md` could drop both its pointers because only `stages.md` was read.

**The scope is now written down rather than implied.** An anti-recipe *inside* the right
section still passes: no text check separates *run these four* from *never run these four*,
because the difference is the prose. Three drafts were spent proving that; the fourth
stopped and filed `B-073`. `B-074` carries the other hole the reader found — a stage can
demand the look while naming no channel, and nothing looks at it.

## v1.55.0 — the browser step gets a second channel, and the table that names it stops truncating itself

The bundle has told every web project to check the rendered surface since v1.36.0, and
it named exactly one way to do it: the `chrome-devtools` MCP, behind a plugin install.
One channel is a single point of failure for a step the pipeline asks for at three
stages, and the operator's report was the ordinary one — it lags.

Playwright now sits beside it, and **neither is ranked**. They do the same look; the
difference is stated as capability rather than quality, so a run picks by need instead of
by taste. `playwright` costs the least per look — its own upstream sells the CLI on not
loading large tool schemas and verbose accessibility trees into the model context, and
both of its channels snapshot the accessibility tree rather than pixels.
`chrome-devtools` is the one that reaches past the page: `lighthouse_audit`, performance
traces and heap snapshots have no Playwright equivalent, and `seo-aeo-audit` builds on
the first of them.

### Added

- **`playwright` as a companion**, with two install paths that need no plugin:
  `npm install -D @playwright/cli@latest` (then `npx playwright-cli`) and
  `claude mcp add playwright npx @playwright/mcp@latest`. Verified against the registry
  at release time: `@playwright/cli` 0.1.18, `@playwright/mcp` 0.0.79.
- **One detection rule for both channels instead of two that drift**, with the
  tie-breaker written down: `playwright` where the project already runs it or context
  budget is tight, `chrome-devtools` where the question is Lighthouse, a trace or a
  heap snapshot. A run that ranks them has invented a fact the matrix does not carry.
- **Stop at the first channel that answers.** Both open the page and read the console
  and the network log; running the look twice is a cost with no second fact.
- **A browser test suite is the other half of the gate, never a substitute for the
  look** (stages 6, `tdd.md`, `SKILL.md`). `playwright test` in CI is a suite whose
  runner happens to be a browser: it proves what someone thought to assert, and cannot
  report the console error nobody asserted on or the element that moved under a header.
  The suite is counted as coverage; the look is still a page opened and read. This
  closes `OQ-0003` as `DEC-0004`.
- **What the look finds is fixed in the stage that found it** (stages 5 and 6). A
  browser finding parked for later is the diff-review verdict wearing a screenshot.

### Fixed

- **Three claims this release shipped as facts, corrected against the tool's own
  `--help`.** The independent reader measured them. *"Costs the least per look"* was
  upstream's CLI-against-MCP comparison restated as this repo's CLI-against-`chrome-devtools`
  fact — now attributed and scoped. *"Both channels snapshot the accessibility tree rather
  than pixels"* was true of the default and denied a `screenshot` both channels ship —
  now says which is the default and what the other costs. *"`chrome-devtools` alone
  reaches performance traces"* was simply false: `playwright-cli tracing-start` records
  one. Only the Lighthouse and heap-snapshot legs are exclusive, and the honest
  difference on traces is that one channel **analyses** what the other only records.
- **The look was called a half of the gate in the same file that calls it never a gate.**
  Stage 6's new paragraph made the browser look sound like gate membership while the
  GATE bullet above it, both matrix rows and `SKILL.md` all keep it recommended and
  degradable. Stage 5 had the mirror defect: *fixed in this task, not filed* against a
  GATE bullet that explicitly permits parking with a ruling. Both now say the thing the
  gate actually enforces.

- **A pipe inside a matrix cell silently disabled the guard that reads it.** Both
  readers of `companion-skills.md`'s table split cells on `|` and do not decode `\|`,
  so an escaped pipe ends its cell early and hands the next check a different column.
  The `graphify` row had carried `graphify query\|affected\|god-nodes` since it was
  added: the matrix→stages check has been reading that row's second cell as `affected`,
  parsing no stage numbers out of it, and passing **without comparing anything** — a
  guard quiet because its input was truncated, which reads exactly like a guard that
  looked and agreed. Found while planting a defect into the new `playwright` row and
  watching the check stay silent. There is now a guard for the class, probed both ways,
  and the `graphify` row is comma-separated. The umbrella hit the same class from the
  other side in `B-40` (an *un*escaped pipe adding a column), which is the second
  sighting that makes it a check rather than a third ledger row.

### Guards

Guards: 315 → **318**. Property checks: 9 → 9. Two new checks over the companion matrix,
each watched failing against a plant: the row's cell count against the header (which
catches a bare pipe and an escaped one alike), and a row that derives no stage at all.
The first draft of the first check tested `\|` only, and the independent reader `R-005`
requires broke it with a bare pipe in one move — with a control proving the hole masked
real matrix→stages drift. The second check exists because the same reader measured every
row and found `agent-sync` deriving nothing from `stage-10`, one row below the `graphify`
row this release set out to fix.

## v1.54.0 — a run cannot reach acceptance with a stage it never stamped

The 2026-08-13 artifact-root run closed at stage 10 with `0,1,2,5,6,7,8,9,10` recorded
and **3 (spec) and 4 (plan) never stamped**. The status line printed `3· 4·` and 73% and
was exactly right; nothing read it. Detection existed — `lib/runledger.js` renders that
rail — and no gate refused on it, which is the difference between a display and a check.

Stage 7's release gate could not have caught it either: it fires before 8, 9 and 10
exist, and it asks only about the tests stage.

### Added

- **`templates/stage-coverage.sh`**, seeded at stage 0 and run at stage 10 before the
  coverage table. It reads the stage ids `pipeline.json` declares and the `stage: <id>
  … verdict` lines the ledger holds, and names every declared stage with no verdict.
  Last verdict per id wins — a stage re-entered after a fix has the outcome of the
  re-entry, not of the failure that caused it.
- **Both remedies are legitimate, and the refusal says so.** Stamp what happened,
  because a merged stage still has an outcome; or stop declaring in `pipeline.json` a
  stage this project folds into another. What is not legitimate is a flow that declares
  eleven stages against a ledger that accounts for nine.
- **Exit 2 when it cannot look** — no config, no ledger — and that is not a pass.
  Standing instruction #1: a component that never received its input refuses rather than
  approves. It has its own negative self-test, because "no input" is the state in which
  a checker most easily agrees with everything.

Guards: 313 → **315**. Property checks: 9 → 9. The first new one plants the incident
itself — a five-stage flow whose ledger stamps four — and requires the refusal to name
stage 3.

## v1.53.0 — the artifact root stops carrying another pack's name

The paperwork directory was called `docs/superpowers/`. The name came from an unrelated
pack — one whose own tests walk the same path — and `references/artifacts.md` had called
it "historical convention" since v0.1.0, promising that a host project *may relocate the
root*. Nothing kept that promise: the path was hardcoded in 24 places in the validator,
in the gate prose of `pipeline.json`, and in 26 CI plants.

### Added

- **`paths.artifacts` in `pipeline.schema.json`.** Any relative path, and it outranks
  both discovered names. This is what turns the v0.1.0 sentence into a mechanism.
- **The artifact-root rule, resolved rather than spelled.** `paths.artifacts` →
  an existing `docs/evidence/` → an existing `docs/superpowers/` → `docs/evidence/` for
  a project that has neither. A directory is adopted only when it **carries a register**
  (`retro.md`, `backlog.md`, `verification.md`, or a `specs/plans/briefs/retro`
  directory): a project may keep an unrelated `docs/evidence/`, and adopting it on a
  name match would write a run's paperwork into somebody else's folder. The answer is a
  record — `{root, reason, legacy, leftover, collision}` — because a bare string cannot
  say *this is the legacy name*, *records also sit over there*, or *the default landed on
  an occupied directory*.
- **Two implementations, one table, compared to each other.**
  `bin/lib/artifact-root.js` ships; `test/artifact_root.py` serves the validator;
  `test/artifact_root_test.py` builds all seven cases as real trees and fails when the
  two disagree. Checking each against the table alone would let them drift into two
  readings that are both "right".
- **`npx task-pipeline migrate-artifacts [--dry-run]`.** Optional, always: the legacy
  name is supported and **no run warns about it**. It moves the directory, refuses when
  `paths.artifacts` is set rather than overriding the operator, never overwrites a
  collision, backs up before writing — and **lists every file elsewhere that names the
  old path without editing one of them.** Rewriting arbitrary documents in somebody's
  repository would mean deciding for them which mentions are a path in use and which are
  a sentence about the old name; this release got that distinction wrong in its own
  sweep before the command was written, which is the argument for not automating it.
- **`/task-pipeline setup` now opens with the resolved root and why**, with all four
  outcomes spelled out — including the one where the default lands on a directory that
  exists and carries no register, which is a stop-and-ask rather than a write.

### Changed

- **The default is `docs/evidence/`**, matching the `evidence-docs` skill this plugin
  already ships. **Nothing migrates on its own.** A project on `docs/superpowers/` keeps
  it, forever, with no warning on any run — an upgrade is a no-op for everyone already
  running.
- 24 sites in `test/validate.py` and 105 occurrences across 34 files now go through the
  rule: doctrine writes `<artifacts>/`, templates and this repository's own statements
  write the resolved name. **Frozen records were not touched** — a brief from March
  describes where things were in March, and rewriting it would falsify the record.

### Fixed

- **A guard that had lost its subject.** The prose sweep rewrote
  `` `docs/superpowers/…` `` to `` `<artifacts>/…` `` — and the guard comparing
  `artifacts.md`'s tables against its layout tree searched for the resolved literal, so
  it found nothing and passed by having nothing to check. Reported by the negative
  self-test as *does not actually fire*, not by the validator, which was green. That is
  standing instruction #6's corollary landing in this repository's own validator one
  release after the instruction was written; the guard is now anchored on the symbol the
  doctrine writes, and it has been watched failing against a planted defect.
- **A plant that no longer landed.** The CI plant removing the layout tree anchored on a
  bare `superpowers/` — a spelling the path sweep never matched — and said so, loudly,
  because it asserts its own effect. Repointing the other 26 plants recovered 24 broken
  negative self-tests.
- **A backup taken when nothing moved.** `migrate-artifacts` copied the legacy tree
  before every run, so a second run against a still-colliding tree changed the tree it
  claimed to leave alone. Found by the three-run fixture rather than by reading: the pure
  planner was right and the command that repeats was not, which is standing instruction
  #2 arriving in the release that cites it.

Guards: 312 → **313**. Property checks: 9 → 9. The new one reverses the precedence in
one of the two resolver implementations: the table still describes the correct order, so
a suite that merely ran both would stay green while they drifted apart on a case the
table never named. Two new suites join CI — the artifact-root rule (7 cases, both
implementations compared) and `migrate-artifacts` (7 cases, three real runs with hashes
compared). 26 CI plants were repointed at the new root and 24 broken negative self-tests
recovered; two remain unable to fire in a submodule checkout for a reason that predates
this release (the harness copies to `/tmp` without a resolving `.git`, and both guards
read git history — CI clones normally and is green).

## v1.52.0 — the three moments the run's own record could not show

### Added

- **`hooks/run-lifecycle.sh`** — one line shape for three events the ledger was
  blind to:

  ```
  event: <compact|session-end|subagent> — <detail> — <ISO-8601>
  ```

  - `compact` marks the boundary **the ledger exists because of** —
    `templates/run.md` says so in its own header, and until now that boundary was
    the one thing the file could not show. A resumed run could not tell "the
    context was compacted here" from "nothing happened".
  - `session-end` marks a run whose session ended without reaching acceptance.
    That is precisely what `/task-pipeline checkup` looks for, and it was
    invisible: the ledger simply stopped, which is indistinguishable from a run
    still in progress. A run that *did* reach acceptance is not filed as
    abandoned, or the report fills with runs that closed exactly as intended.
  - `subagent` records one finishing, so the `hand:` count has something to be
    checked against other than itself.

  **It never writes a `hand:` line, and that is not a shortcut.** That shape
  carries `done`, `surfaced`, `decisions` and `amb` — judgements only the agent
  holds. A hook filling them in would fabricate the evidence the line exists to
  provide. It records what it can see and leaves the accounting to whoever can
  account.

  One shape rather than three: a ledger grammar is read by four documents and
  several hooks, and every shape added is a shape each of them must learn.

- **`hooks/build-gate.sh`** — editing the product before the plan is agreed now
  asks. Stage 5 is where code is written; editing during intake, docs, brainstorm,
  spec or plan is the pipeline's discipline being skipped, and it is the skip
  nobody notices because the work looks like progress.

  `ask`, never `deny`: the routing boundary says a typo, a one-line fix or a
  mechanical rename never went through the pipeline anyway, and no hook can tell a
  typo from a feature. **The build stage is resolved by role, never by number** —
  the same lesson v1.51.0 learned from the release gate, applied before it could
  be repeated. **The pipeline's own artefacts are never gated**: `docs/`,
  `.task-pipeline/`, README and CHANGELOG are what stages 0-4 are *for*.

Guards: 311 → **312**. Property checks: 9 → 9. The release-gate suite is 29 → 43
fixtures, all run as processes.

## v1.51.0 — the gate stopped being keyed to a number, and stopped believing the agent

### Fixed

- **v1.50.0's release gate blocked every release forever in any project whose flow
  has no stage 6.** It matched `stage: 6` literally. A six-stage project with tests
  green at stage 4 could never tag anything again — and this file's own
  `progress.md` says the rail "is computed, never eleven" for exactly this reason:
  a host project replaces the flow. A wrong rail misinforms; a wrong gate stops the
  work. Reproduced against a six-stage project before it was fixed.

  The tests stage is now resolved from `pipeline.json` — a stage whose `state` is
  `tests`, or one declaring `gate.command` — and failing that from the ledger by
  name. When it cannot be resolved the gate still refuses, because a run is in
  flight and nothing in it reports a suite passing, but the reason now says how to
  make the flow readable.

### Added

- **`hooks/gate-observer.sh` — the observation the gate rests on.**
  `stage: … verdict pass` is typed by the agent the release gate constrains, so on
  its own the gate confirmed an assertion with the same assertion. The observer
  records the **observed** exit code of the command the project declared, as a new
  ledger line:

  ```
  gate:  <stage id> — command "<cmd>" — exit <N> — <ISO-8601>
  ```

  and the release gate requires the claim and the observation to agree. It records
  a red run as a red run — a hook that hid one would read as "the suite was never
  run", which is the opposite of what happened. Only the declared command is
  observed, compared on the normalised command line: `echo "npm test"` and
  `npm test --watch` are not the project's gate, and treating them as one puts a
  fabricated observation in the file the gate trusts.

  **No `gate.command` declared → the gate degrades to the claim alone.** Stated
  here rather than discovered.

  **The LAST observation, not any of them.** "Some run of the suite was green" is
  true of almost every repository that has ever been red, and a gate satisfied by
  history rather than by current state is satisfied permanently. Found by running
  the observer against this pipeline's own ledger, where an earlier green sat
  above a later red and the gate waved it through.

Guards: 310 → **311**. Property checks: 9 → 9. The new guard disarms the
corroboration — it makes the gate accept the claim alone — and requires the suite
to notice; `test/negatives.py`'s floor moved with it in the same change. The
release-gate suite is 16 → 29 fixtures, all run as processes.

## v1.50.0 — the stage-7 gate stops being a sentence somebody reads

### Added

- **`plugins/task-pipeline/hooks/release-gate.sh` — the stage-7 rule, enforced at
  agent time.** `stages.md` has always said a release does not leave stage 7 until
  the full suite is green at stage 6. That was a sentence an agent reads and a
  person hopes was obeyed, checked — when it was checked — after the tag was
  already public. A `PreToolUse` hook now refuses `git tag`, a tag push,
  `gh release create` and `npm publish` while the run ledger records no
  `stage: 6 … verdict pass`.

  Three narrownesses are the whole design, and each is the difference between a
  gate people keep and a gate people rip out:

  1. **Only outward acts.** Ordinary commits are how stage 5 works; gating them
     would fight the pipeline's own build loop and be gone within a day.
  2. **Only where a pipeline runs.** No `.task-pipeline/run.md` means exit 0
     before anything else is read, so enabling the plugin changes nothing in any
     other repository on the machine.
  3. **Only what the ledger says.** Nothing reruns a suite or believes a claim —
     `progress.md` already makes the ledger append-only, and this reads it.

  The refusal names the act, the ledger to record the stage in, and the opt-out.
  A refusal with no next step is how an operator learns to remove a gate.

  Fail-closed by construction: an internal failure exits 2 as well, because every
  non-zero code other than 2 is non-blocking in Claude Code, and a crashing gate
  that fails open is worse than no gate — it reads as one.

- **`test/release_gate_test.py`** — 16 fixtures, run as a process with real JSON on
  stdin, wired into `npm run test:all` and CI. Eight of them were watched failing:
  the first implementation fed its own python source to `python3 -` through a
  heredoc **and** tried to read the payload from stdin, so `sys.stdin.read()` came
  back empty, every release was classified as "not a release", and the gate
  allowed everything while looking installed. The payload now travels in the
  environment.

### Notes

- The hook lives in the plugin's `hooks/hooks.json` rather than in `SKILL.md`
  front matter. Front-matter hooks are scoped to a skill's activation; a release
  gate has to hold for the whole run, across turns where the skill is not the
  thing being invoked. `agent-sync` already enforces its leases from the same
  channel, so this is the family's proven path rather than a new one.

Guards: 309 → **310**. Property checks: 9 → 9. The new guard is the negative
self-test that disarms the release gate — it blanks the payload handoff, which is
how the gate was really broken for its first eight fixtures — and requires the
suite to notice. `test/negatives.py`'s floor moved with it in the same change,
because a floor below the count cannot notice losing the difference.

## v1.49.2 — four stray table rows, and a list that promised three and delivered two

### Fixed

- **The body shipped a rendering defect.** Four rows of the built-in-doctrine
  index — `artifacts.md`, `companion-skills.md`, `conventions.md`,
  `model-tiering.md` — sat between the grill's bullet list and `## How to run`
  with no header row above them. GFM needs a delimiter row to open a table, so an
  agent reading `SKILL.md` saw four lines of literal pipes. Moved back into the
  index where their shape says they belong.

- **"Three things the grill does beyond clarifying the request" listed two.** The
  displaced rows had taken the third with them. Restored from
  `references/grill.md`, which still carries it in full: **the design
  destination** — which Figma file, in which team, decided at stage 0 rather than
  at drawing time. Restored rather than renumbered, because the reference proves
  what was lost; renumbering to "two" would have made the body agree with itself
  and disagree with the doctrine.

Guards: 309 → **309**. Property checks: 9 → 9. This release restores content and
adds no enforcement — the defect was structural markdown, which no guard here
reads, and the count is stated because two probes read the newest section.

### Note on the token budget

The body is **5969 tokens against a 5000 cap**, up 108: the restored bullet costs
more than the four moved rows save. Correctness first — a body promising three
items and delivering two, with four lines rendering as garbage, is worse than
being over a soft cap it was already over.

The gap is now measured rather than estimated, so it stops being re-litigated by
prose trims. Three attempts at trimming prose produced 35 tokens between them. The
whole doctrine index is 555 tokens — 320 in the descriptive column, 235 in the
reference names — so compressing every description to nothing closes at most **26%
of the 1219-token gap**, and less than that if the stage numbers stay, which are
the navigational value. The remainder lives in the Stages table's `Gate` column
(`grep -c '^\*\*Gate' references/stages.md` → **0**: the body is its only home)
and in the five-step operating procedure. Closing the gap therefore means moving
content into references — a restructuring of the skill, not a trim.

## v1.49.1 — the entry states the count its own guard reads

### Fixed

- **v1.49.0 tagged but never released.** Its CHANGELOG entry stated no
  `Guards: N → **M**` count, so two of this repo's negative self-tests had
  nothing to patch and reported `PLANT DID NOT LAND` — the release job failed
  after the tag was already public. Same class as v1.45.0, and the guard worked
  exactly as designed: a probe that cannot plant says so instead of passing.

  The count is unchanged because v1.49.0 added a feature, not enforcement.

Guards: 309 → **309**. Property checks: 9 → 9. The installer change is
behavioural and carries no new guard; the count is stated because two probes read
the newest section and a count-shaped sentence with no count is the one case
where silence and agreement look the same.

### Changed

- Everything in v1.49.0, which never shipped: the installer now offers the
  family's routing block via `npx sshlg-skills routers --member task-pipeline`,
  scoped so it repairs only this skill's own section. See that entry below.

## v1.49.0 — the installer stops leaving the skill unrouted

### Changed

- **The installer now offers the family's routing block** (closing B-06 in the
  umbrella). Until now only `super-ux` delegated: install this skill on its own
  and no router was written at all, so an agent had the skill and no rule saying
  when to reach for it. The bundle installer wrote all eight, which is why
  nothing looked broken — the gap only opened for someone installing one member.

  Delegated to `npx sshlg-skills routers --member task-pipeline` rather than
  reimplemented, for three reasons:

  - The block describes what the machine actually has. A lone member rendering
    the whole thing would print a table for routers nobody installed.
  - `--member` scopes the write to this skill's own section. Verified by damaging
    two sections of a real block and running this installer: its own was
    repaired, the other left exactly as it was.
  - The launcher is the only writer that copies the operator's global instruction
    file before touching it. That file has no version control behind it.

  `--no-install` keeps it from silently downloading a package nobody asked for.
  When the launcher is absent the command is printed instead of failing: ending
  an install in an error over an optional follow-up reads as a failed install.
  Both paths were exercised.

## v1.48.0 — a screen is the frame implemented, and four mechanisms this project owed itself

**A screen is the frame, implemented.** Until now Figma was an address and a link: the
brief recorded which file, `screens.md` carried frame URLs, the linter checked they were
not stale. Nothing said the screen is **built from** it. Now the order of authority is
fixed — `super-ux` says what the screen does, the **frame** says what it is made of, and
`sheleg-design` says how it looks and moves **where the frame is silent**, after the file
and never instead of it.

Made concrete rather than aspirational: the composition is compared against the node
tree, not recalled; layout is read from `get_design_context`, because from a screenshot
it is recovered approximately and approximate is indistinguishable from exact in a
report; a node with a Code Connect mapping is used, not reimplemented, since a rewrite
is a silent fork of the design system; and a raw hex where a variable exists is a token
that has quietly split in two.

With the honest boundary that keeps it followable: **a frame is one width.** Behaviour
at other breakpoints, and states the frame never draws — error, empty, loading — are
decisions that get **recorded**, not guessed. Without that line the rule is broken on
day one and then ignored entirely.

**No frame for a screen: build it, name it, offer to draw it, mark what gets drawn.**
Figma stays a recommendation whose absence is named and never blocks. The screen comes
from the style pack, the spec says so screen by screen, and the run offers to draw the
missing frames into the file the brief already named — which screens, where, from what,
so the size is visible before anyone says go. Drawing happens only on an explicit go,
and whatever is drawn is marked as coming from implementation. **A designer must be able
to tell a decision from a generation**; an unmarked generated frame is the same false
confidence as an unproven green.

**Another agent may be in this repository right now.** Isolation used to mean *your*
passes not colliding with each other. It now also means someone else's: a worktree per
agent, always, because sharing a checkout is what turns two independent changes into one
corrupted state — a copy taken mid-write, an edit staged into another commit, a branch
switched under a running test. And a lease before any shared register where the project
carries `.claude/agent-sync.json`, because a worktree separates files and answers nothing
about who may edit the board.

With the asymmetry that keeps the rule from becoming a licence: **on finding the other
agent mid-run, leave their work alone.** Their uncommitted edits are not yours to stage,
revert or stash. Put a ref on your own committed work so a branch reset cannot lose it,
and continue in a worktree of your own — ending someone else's work to unblock yours is
what `residue.md` refuses, one layer up.

This is measured, not feared. One session produced four version collisions, a `files[]`
entry dropped silently by a merge and caught only by the validator, and a test run that
failed because a probe copied the tree while another agent was writing to it. This
repository now carries the coordination config it was telling every other project to keep.

**Four mechanisms this project had decided on and never built.**

`DEC-0001` ruled that `SURFACED: 0` is checked against what the run filed — a run that
opened a board row and reports nothing surfaced contradicts its own artefacts, and the
`Source` column makes that computable. The decision was recorded and nothing implemented
it, which is R-006's own subject applied to a decision instead of a finding. It is a
check now, and it carries its residual in the same breath: it kills the silent zero, not
the blind spot.

`R-006` has been in force for four releases because nothing could read the distinction
it draws. Stage 10 now records, per finding, **one of two words** — `behaviour` or
`reporting`. A row saying `reporting` stays open on the board; only `behaviour` closes it.

**The release path now runs the suite it advertises.** Two releases shipped over a red
suite because the negatives ran on the PR and never on the tag. A tag is not evidence.

**And a version number already spoken for now fails at the commit rather than at the
merge.** Four collisions in one session, each costing a renumber of a whole branch.

Guards: 294 → **309**.

## v1.47.2 — the body stopped retelling its own references

`Prerequisites` was 2585 of the body's 6585 tokens, and most of it was a second
telling: super-ux, the bridge, the grill, the harvest, the documentation gate and the
retrospective each have a reference that carries them in full. The body now keeps what
a reference cannot — the traps, and the one hard requirement — and points at the rest.

What stayed inline, deliberately: **the stage-3 spec gate stops** on a UI task with no
super-ux; the grill's single sanctioned bypass; **the retro is read two ways** and the
difference matters (standing instructions in full because they bind and are bounded,
the recent log queried because nothing caps it); a stale code graph is a false premise
**carrying the authority of a machine**, since a wrong doc gets argued with and a wrong
graph gets believed; and the operator outranks any document **only out loud**.

~6585 → ~6180 tokens against a 5000 budget. **Still over, and the rest is not a trim.**
What remains is `How to run` and `Stages` — the operating instructions themselves —
and moving those out is a decision about what a reader must have in hand before the
first stage, not a compression exercise. It is coupled to the description question the
v1.47.0 entry recorded: both are about what this one file is obliged to carry.

## v1.47.1 — the fixes a reader found, which three releases shipped without

v1.46.0 was tagged and published from a commit that carried this branch's doctrine and
none of the three commits answering the reviewer. The defects below were already found
and already fixed when the release went out; this is them arriving.

**`docs/DOCMAP.md` forbade the register shipping beside it.** It said, in as many words,
that no `docs/DECISIONS.md` is created here deliberately — and the release shipped that
file. The old rule was right about the risk and wrong about the mechanism: `OQ-####`
closes with `Resolved→DEC-####`, and a CHANGELOG version heading cannot be that target,
because two decisions in one release collapse to a single pointer. SSOT is kept by
direction now — the reason lives in `DECISIONS.md`, the CHANGELOG points at the id. The
reversal is `DEC-0003`, because a register that appears without a decision is exactly
the fork the old rule feared.

**`HOW-IT-WORKS.md` called itself the version it was written under.** Its first line
promises a rewrite every release and names the banner as the freshness signal; the
banner read 1.45.0 while every other surface read 1.46.0. Corrected, and the two
releases that landed from another session are named for what they were, so the gap in
the version history is explained rather than silent.

**An absolute rule keeps every keyword while an appended clause reverses it.** This
release found that class, guarded it on stage 10's criterion 13, and left `residue.md`'s
two absolute rules on plain substring presence — *"never released by this run, unless it
has clearly expired"* passed. Sweeping the fix to its siblings then produced the reason
to sweep it structurally: the second copy of the carve-out pattern had its escaping
doubled, so it matched a literal backslash and walked past every inversion while looking
correct. One home now — `_EXCEPTION_MARKER` and the `_carve_out` helper that reads it —
with two call sites.

**A probe demanded a dependency the harness disclaims.** `res8` required PyYAML to be
installed; the guard it tests degrades honestly without it. `test:all` was red on any
machine lacking it. Three branches now: the guard fired, the guard said it could not
look, or neither — and only the third is an error.

Also: the owner-row check went through `_row_cells` instead of a hand-rolled regex, as
that helper's own docstring asks; and a reflow that fixed a 157-character line had
orphaned two words onto a five-character one.

Guards: 291 → **294**.

## v1.47.0 — a green suite that cannot speak for an agent

The suite gate at stage 6 assumes the thing under test is deterministic: run it twice,
get the same answer, and a pass means something. An agent breaks that assumption, and
until now this pipeline had nothing to say about it — a grep across the plugin for
`llm-as-judge`, `eval suite`, `regression fixture` and `trace id` returned nothing.

**`tdd.md` gains *When the thing under test is an agent*.** The artifact under test is
the execution record, not the source: the code says what the agent is allowed to do,
only a run says what it did. Three tiers with unequal authority at the gate — step and
turn **block**, thread **reports** — plus the two rules an ordinary suite never needs.
**Assert the side effect, not the sentence**, because an agent that says it saved the
preference and did not passes trajectory and response and is broken. And **a model
judging a model is not a check until it has been calibrated** against human labels on
cases known to be bad. The suite is grown from production failures, minimised, and kept
permanently — a fixed defect that silently returns is the whole reason.

The gate states what it does **not** cover, as canon 6 requires: an offline suite speaks
for the cases already known and for nothing else, which is why production observation
stays a stage-8 concern.

**Three canons extended rather than an eleventh added.** Canon 3 says every fact has one
home, so the agent case belongs inside the canons it is an instance of, not beside them:

- **Canon 1** — where the subject is non-deterministic, the address is a **trace id and
  the assertion that ran against it**; a rerun is not the same run.
- **Canon 5** — a model used as a judge is the same object as a check: until it has been
  seen disagreeing with a human on a known-bad case, its pass is an opinion with a
  number attached.
- **Canon 8** — a score produced by a model is an estimate in every report that quotes
  it, however many decimal places it carries.

**`evidence-docs` gains one routing row** and no doctrine — it is a navigator. The row
names its target instead of linking it: this navigator already carries eleven
out-of-directory links that break wherever a packager ships the skill alone, and a
twelfth would widen a known defect. Stated rather than fixed, and the count is unchanged
at eleven — measured before and after, not assumed.

`Guards: 291 → 291`. This release adds doctrine, not enforcement: nothing here is
machine-checkable yet, and the count says so rather than leaving a reader to infer it.
The gate written into `tdd.md` is a specification a host project runs against its own
agent — this repository has no agent to run it against, so arming it here would be a
check with nothing to look at, which `gates.md` calls dormant and forbids passing.

## v1.46.0 — what a run leaves running, what "done" costs to say, and what a check is for

Three rules this pipeline had been following by disposition rather than by doctrine,
and one it had not been following at all.

**`evidence-docs` can now be reached in Russian.** It shipped without Russian triggers
while `task-pipeline`, beside it in the same plugin, had carried them since v0.14.0 — a
navigator nobody can summon is a navigator nobody reads. Its description now opens with
`Use when …`, names twelve triggers on both sides, and keeps the `без доков` opt-out the
body always documented. `task-pipeline`'s own description is deliberately unchanged: the
house auditor requires every description to open with `Use when …`, this repository's
validator requires the opposite — capability first, trigger second — and fails the build
on anything else. Measured in both directions; which of the two rules is wrong is a
decision, not a fix to slip into a release.

**A run is not only a diff — it is also everything it left running.** A background
shell, a monitor polling an API, a scheduled loop, a coordination lease, a worktree,
a container, scratch files, a draft PR. `references/residue.md` names eight classes
and requires each to be enumerated **by class, never by one tool** — because the
measured case that produced this file was a task inventory reporting *"No tasks
found"* while `ps` showed the monitor alive and polling every thirty seconds. An
inventory that does not contain the thing that leaks is a green light with no lamp
behind it.

Every gate now prints `holds: N` beside its verdict, the run ledger gains a fifth
declared line shape, and stage 10 gains criterion 13: give the environment back.
The asymmetry is the point — **end what this run started, report what it did not**.
The inventory is machine-wide and the authority is not, so a stale-looking lease
belonging to another agent is named, never released.

The field is `holds:` rather than `residue:` because `gates.md` already prints
`unmarked residue: 0` for documentation items, and `residue: 0` is a substring of
it. A check written for the new field would have been answered by the old line — the
class this repository has now met nine times, caught here before it shipped.

**"Done" is a claim, and it names what makes it true.** Every disclosure in this
bundle asks *what does it print when it did not look?* — of checks. `progress.md`
now asks it of the run's own sentences, which reach the operator where the check
does not. Three shapes, each requiring no intent to mislead: the plan reported as
the outcome, the reply reported as the result, the part reported as the whole. And
the honest negative is a result: *"not done, the fixture needs a credential I do not
have"* is a complete report where *"done, with a small caveat"* is not.

**The result is the goal; the check is how you know.** Every other line in
`gates.md` pushes one way — prove more, assume less — and read alone it produces a
run that spends an afternoon proving a one-character change. Verification now scales
to what breaking costs, using the `sev × blast` the board already computes, with
four named signals that you have crossed over. This never licenses skipping a gate:
the floor is not proportionate to anything, and cutting it to go faster is the
failure the file exists to prevent, arriving on schedule.

**Publishing was half a loop.** `retrospective.md` closes it: an issue resolves when
the **behaviour** changed and its closing comment names the file, the line and the
guard; an issue nobody worked stays open rather than being triaged into silence;
nothing is deleted, because the number is what the CHANGELOG points at. The queue a
run pulls from when it finishes early is that pile, then the board, then the open
questions.

Guards: 275 → **291**, each still proven against a planted defect — including a
neighbour probe that caught a defect in one of this release's own guards on its
first use: the criterion-13 check scoped *to the next heading* rather than *to the
item*, so a needle parked in between answered for the rule.

## v1.45.1

### Fixed

- **The v1.45.0 entry had no `Guards: N → **M**` line**, so the negative
  self-test that plants a stale count had nothing to plant into and failed with
  `PLANT DID NOT LAND`. The count is a claim about *now* and every release
  section is required to restate it — a release that omits it silently disarms
  the check that keeps the number honest.

### Counts

- Guards: 275 → **275**.

## v1.45.0

### Changed

- **The body went 367 lines / 7514 tokens to 338 / 6088** — measured with
  `cl100k`. The reference routing existed **three times**: a 36-row "Built-in
  doctrine" table, a flat `## References` catalogue below it, and again in the
  stage table's `Invoke` column. One home now — the routing table, keyed by the
  stage that sends you there — and the four files that lived only in the flat
  list gained rows so nothing lost its trigger.

- **The description is 970 chars**, exactly the 5% headroom the canon asks for,
  down from 1010. Getting there took three attempts: the validator locks the
  `Not for:` exclusions and the verbs `adopt`/`harden` against the NOTRIG evals
  from the 2026-08-03 design, and refused two rewordings before accepting one
  in text nothing had locked.

### Counts

- Guards: 275 → **275** — this release adds none; it removes duplication from
  the body and touches no check.

### Known gap

- **The body is still 6088 tokens against a 5000 cap.** What remains is a
  36-entry routing table and a five-step operating procedure, and both are what
  the skill *is* — a body that indexes 32 references cannot be smaller than its
  index. Cutting further would mean removing the routing this skill exists to
  do. Recorded rather than papered over: the number is real and the canon's cap
  does not have a clause for a skill whose body is a router.

## v1.44.0 — six lessons other projects paid for, carried home by the mechanism that exists for it

`retro.publish` sends a skill-level lesson upstream as an issue. Six arrived in one day
from projects that are not this one, and every one is a diagnosis: the class, why the
existing doctrine did not catch it, and the fix by grade. This release is those six.

| Issue | What it bought |
|---|---|
| #30 | a name in `verified by` **resolves**, or the row is `unknown` — never `verified` |
| #31 | a probe that mutates a file asserts its plant landed **— now a guard** |
| #32 | a seam is not a deliverable: an explicit REQ for the boundary, phrased as a journey |
| #33 | the tests gate names **what each case consumes**; a timeout is unclassified, not slow |
| #34 | stage 10 carries a `publish:` line — an unarmed path stops looking like silence |
| #35 | a ratchet's matcher is itself a check: feed it a **near-miss it must reject** |

### Two of them had already been found here, independently

**#35 is the neighbour probe**, shipped in v1.42.0 after a reader defeated six guards whose
evidence sat next to their subject. The reporting project reached it from a ratchet whose
matcher credited every parent with its child's coverage. Same class, two routes, no
contact — which is the strongest evidence either had.

**#31 is R-001**, born here on 2026-08-03 and **retired in v1.38.0** on its own trigger:
*"a probe harness exists that asserts the plant changed the parsed text"*. The harness does
exist. The retirement was still premature, because the condition was *"a harness exists"*
and the thing that mattered was *"the harness is used everywhere"*. It cost the reporting
project three incidents in one day and this repository six in this session's own releases.
**A retirement trigger phrased as the existence of a mechanism, rather than its reach, is
a trigger that fires early.**

### The number that took four attempts

Enforcing #31 meant counting probes that mutate a file without asserting the plant landed:

```
hand-written classifier   206 of 206 already carry it   (wrong)
the guard, first version   22 do not                    (wrong — one spelling)
the sweep that followed    "fixed" 6 sound probes, corrupted 5
the truth                  16
```

The guard corrected the hand count that motivated it. Then the guard was itself the class
two sections above — keyed to one spelling, it reported as defective six probes that
obeyed the rule in different words, and a sweep written from that verdict split five live
statements. Found by `compile()` and a restore from git.

**Every** mutating probe carries the assertion, and **no figure is written here** — the
third attempt to put one beside it was wrong too. The count is a `grep` away and the
guard computes it on every run; a number in prose next to a check that can count is
restating instead of computing, which is the rule this very release imports and which
this paragraph broke three times before it stopped trying.

- Guards: 261 → **275**.

## v1.43.0 — the rail said where, and nothing said what happened

A fourteen-iteration session on this repository ended each return with the same question
from the operator: *what did you actually do?* The rail answered **where** the run was —
one line, computed, correct — and nothing answered the rest. Everything else was
recoverable from artefacts; what a run learned by accident was recoverable from nothing.

### The hand-back

At both boundaries — an iteration's close and stage 10's — the run now writes four
sections and two lists:

```
TASK        the request as it was GIVEN, quoted from the brief
PROGRESS    where the run stands against that request
DONE        what was solved, each with its evidence
SURFACED    what came up that nobody asked for

DECISIONS WAITING  <n>   each as a question with options, asked HERE
AMBIGUITIES        <n>   computed from four registers, with ids
```

**TASK is quoted, never paraphrased** — a run that restates the request in its own words
after eight iterations has rewritten it, and the operator cannot see that happen.
**DECISIONS WAITING are asked, not parked**: a question in a report is answered days
later, if at all. And **AMBIGUITIES are computed**, from four registers an earlier stage
already wrote — open `OQ-####` rows, carry-over rows with no home, REQ rows whose check is
`review` rather than a command, and source-ledger rows reading *none found*. An unbounded
*"is anything unclear?"* becomes a ritual sentence within three runs.

**It is a gate criterion, not a good intention.** `progress.md` already carried one
instruction with no gate behind it — *"copy it, tick it"* — and the v1.37.0 audit found
that no run had ever obeyed it.

### The reader found that this release built what it had just condemned

A gate criterion with **no artefact**. Every guard read the doctrine files, so all any of
them could establish was that the instruction was still written down — none could
establish that a run obeyed it. The reader then constructed a conforming hand-back
concealing a weakened test and showed that **nothing in the repository would notice**,
and that an audit a year later could reach no verdict either way, because there would be
no run records to check. This file's own diagnosis of *"copy it, tick it"* — a rung-1
rule read as rung 3 — reproduced one level up.

**The hand-back now has an address:** a `hand:` line in the run ledger, declared as its
fourth shape. `grep -c '^hand:'` against `grep -c '^iter:'` is what makes a missing one
readable.

Six more, all verified by planting and watching `PASS`:

- **`"hand-back"` as a bare substring could not tell a requirement from a mention** — a
  gate reading *"the hand-back is OPTIONAL and may be skipped"* passed, in the release
  whose entire argument is that it must be a criterion. Both gate guards now require the
  normative phrase;
- **the gate span was unbounded below** — the GATE is the last bullet, so a paragraph
  after it answered for it;
- **the template was every fence joined**, so a worked example — the likeliest next edit
  to that section — would have answered for the template;
- **the two lists were left to prose** while the four sections were read from the fence,
  which is the split this release wrote a guard to forbid;
- **the AMBIGUITIES subsection could be replaced by explicit judgement** and pass, keeping
  the four words as *examples*;
- and a relocated section was reported as a deletion.

**Four doctrinal defects, not guard defects:**

- *"at both boundaries"* named a pair this file defines as something else three sections
  above — a reader resolving it there writes a hand-back at task start, where TASK is the
  only field with content;
- **the four ambiguity sources had no commands**, though the section claimed *"each read
  by a command"* — and one of them would have grepped for a string the source ledger's own
  doctrine never writes, returning a false zero;
- **one register is structurally zero at the gated boundary**: stage 10's own gate already
  forbids an unresolved carry-over row, so that count is zero because a sibling clause
  compelled it. The section now says to print *why*;
- and **`acceptance.md` — the file stage 10 actually opens — never mentioned the
  hand-back**, while carrying every other criterion. Two surfaces were updated where four
  state this gate.

**Still true and stated rather than fixed:** `SURFACED` has no register behind it, and the
doctrine calls it the section that earns the hand-back. *"Nothing surfaced"* remains a
quiet decision. The `hand:` line records that a hand-back happened, never that it was
complete.

### Six predicates answered by their neighbours, all caught by their own probes

- the four section names were read from the whole section, and `SURFACED` appears in the
  sentence explaining why SURFACED matters — so renaming the template row left the guard
  green. It now reads the **fenced template**;
- `asked` appears in `SURFACED`'s own description (*"nobody **asked** for"*), so the
  decisions check was answered by a neighbour;
- and the section span was narrowed to `#{2,3}` by reflex, which cut the guard off from
  the `###` subsection holding four of the things it checks. **The span follows the
  subject, not a house style** — v1.42.0 narrowed a different span for the opposite
  reason.

Not one of these needed a reader. The neighbour-probe habit shipped one release earlier
caught all three, which is the first evidence it does what it was written for.

- Guards: 253 → **261**.

## v1.42.0 — a probe proves the phrasing its author had in mind

Six times in one session a guard was defeated by **text that was not its subject**, and
every one of those guards had a probe, and every probe fired. The probes and the guards
were written in the same hour from the same reading of the same file, so they shared the
blind spot rather than covering it.

| The check's subject | What answered it instead |
|---|---|
| stage 2 names the loop's arming | *"it **arms** the UX track"*, present since v1.7.0 |
| the section states the authorization floor | the same phrase in a Rationalizations row, and in a section from v1.11.0 |
| the run stamps have a cap | the **standing instructions'** `max 10` in the same cell — and, once narrowed past it, the same cap on the other side of the `·` |
| a section read in full stays capped | rows under one heading, while a second heading held forty more |

### The doctrine failed its own first use, and a reader caught that too

R-005's fourth consecutive reader read the three new probes against the section that
defines them. **`nb03` was not a neighbour probe.** It planted the needles of two
*retired* predicates — proving the guards that used to exist were neighbour-answerable
and saying nothing about the one that does. The instruction *"plant the guard's own
evidence"* reads as *"plant something that used to satisfy it"* unless it says **which
literal**, and now it does: the one the predicate matches today, read out of the guard.

Seven more, each planted and watched passing, each now replayed and failing:

- **Part 1a's precondition could be replaced by its opposite** and a housekeeping aside in
  a `###` subsection answered for it — the reading `Default off` exists to forbid, shipping
  behind a parenthesis;
- **the stage-2 guard's declared span was false.** Its comment said *"the GATE bullet and
  nothing else"*; the GATE is the last bullet, so the split handed it everything to the
  section end and a trailing note satisfied it;
- `- **GATEways to stage 3:**` was taken as the gate — no word boundary;
- **a decoy row about the archive answered for the live file**, because the retrospective
  check scanned every `|` line rather than the row it names;
- **the scope depended on a `·`** no doctrine requires: replacing it with `, and` restored
  the v1.41.0 defeat by punctuation;
- **one disjunct was dead and the live one was a literal** — the source line-wraps, so the
  check was a false positive on any reword and a false negative on inversion;
- and **rekeying the stage-2 guard silently lost coverage**: deleting the whole queue
  bullet began to pass, while its probe kept firing only because it *also* deleted the
  gate clause. A probe whose stated claim has quietly become another probe's claim.

**A probe that only deletes is not a neighbour probe** — it may be correct, but if it
leans on copies already next door it must assert they are there, or a later edit demotes
it to a delete-only test that still passes.

### The neighbour probe

`gates.md` now asks a guard that reads a scoped span for a **second** probe, planting in
two places at once: break the subject, plant the guard's own evidence **next door**, and
require it to still fail. A guard that goes green is reading the neighbourhood, and the
ordinary probe cannot tell the difference — which is why it is a separate probe rather
than a stricter one.

Three shipped with it, one per guard that fell this way. **The third failed on its first
run and was right to:** a planted sentence saying *"after-decomposition remains a word in
the schema"* satisfied the stage-2 guard, proving it neighbour-answerable. The guard is
now keyed on the stage's **gate** — what it must DO — rather than on prose around it,
because prose above a gate can say anything.

**Positional narrowing is not scoping**, and three of the six were "fixed" that way
before falling again to text still inside the cut.

### Half of B-057 was already mechanised, and the row overstated it

`test/negatives.py` runs `differs_from_repo` on every planted copy, so a probe whose
needle no longer matches fails **loudly** rather than silently — which is what every
stale literal in this session actually did. The remaining half is the silent one, and it
is what the neighbour probe is for.

- Guards: 250 → **253**.

## v1.41.0 — one line per run is a slope, not a bound

`retro.md` is read **in full** at stage 0, and its own doctrine called both read sections
*bounded by construction*. Measured 2026-08-10:

```
standing instructions   ~1 234 tok   capped at ten
run stamps              ~2 099 tok   27 rows, capped by nothing
recent log             ~12 441 tok   queried, not read
```

The v1.38.0 audit found exactly this shape in the narrative log and moved it out of the
floor. It left the neighbour in the same file, with the same property, because the
neighbour's growth is **tidy** — one line per run. A tidy slope is still a slope: at a
hundred runs the stamp table alone is ~7 800 tokens of a floor the doctrine believes is
bounded.

**The cap is ten, and the cold trigger is why.** It reads *the last five run stamps*, so
ten is that with a margin and a rotated row can never be one the trigger needed. Eighteen
stamps rotated into `docs/superpowers/retro/2026-Q3.md`, whole, append-only. The stamp
section went **2 099 → 1 088 tok**, the read portion **3 333 → 2 335**, and the stage-0
floor to roughly **35 300**.

### The reader found six ways past the cap, and one of them was the doctrine's own command

R-005's reader defeated the first cap guard six ways, each planted and watched passing:

- **a second `## Run stamps — …` heading in the same file** held forty more rows and
  passed. The guard read a *section*; stage 0 reads the **file**;
- **one leading space** on a row — still a valid table row — hid it from `startswith("|")`;
- **the stamp command this doctrine ships** (`printf '%s · %s\n' …`) appends prose, not a
  table row. An agent obeying the shipped instruction literally produced forty stamps the
  guard could not see, with `unlooked: 0`;
- **`templates/retro.md`** ships the same table to every host project and was outside the
  corpus — the fourth hand-written list this repository has caught, against an invariant
  that says corpora are discovered;
- **rotation by deletion** passed: a stamp removed from `retro.md` and absent from the
  archive is history destroyed, and the guard could not tell moving from deleting;
- and the row check — already narrowed twice — was defeated by **swapping the two items
  around the `·`**, which is the standing instructions' `max 10` answering for the stamps
  again, on the other side of the separator.

Both guards are rewritten to count by **predicate over a discovered corpus**: three stamp
shapes (table row, list item, and the `<date> · <sha>` line the doctrine writes), every
file carrying a `## Run stamps` section, and the doctrine's cap read from the segment that
names the stamps rather than from anywhere in the row.

**Four surfaces had never learned the rule** — the live section's own intro, stage 10's
prune, `templates/retro.md`, and `templates/retro-archive.md`, which had no destination
section for a rotation the doctrine names. And stage 0 still called *one line per run* a
bound. All five now say the same thing.

**A hand-written count in this release was wrong.** It said twenty-one stamps rotated;
computed, it is **eighteen** (28 → 10). In a repository whose loudest canon is *compute,
never restate*.

### Two predicates that were answered by their neighbours

Both found by their own probes, both the same shape as the defects the last release's
reader named:

- the first version asked whether the file contained *"one line each"* and *"bounded by
  construction"*. After the fix both survived **only inside the sentences criticising
  them**, and the guard fired on its own correction. A predicate that cannot tell a claim
  from its refutation has a false-positive budget above zero, which `gates.md` sets at
  zero;
- scoped to the table row, it was then answered by the **standing instructions' own
  `max 10`** in the same cell. It now reads only the part of the row after `Run stamps`.

- Guards: 248 → **250**.

## v1.40.0 — the loop had a cadence and no queue

`run.loop` said how **often** to continue. It never said **what the next item is**, so an
armed mode still left the run choosing its next move by recollection — `learned.md` rule
16, once per fire. And nothing scheduled the next turn at all: on 2026-08-10 a run of
this pipeline wrote *«продолжаю без остановки»* and the turn ended, because a sentence
about future behaviour is not a wakeup. That run is this release's occasion and its
evidence.

### The queue is stage 2's

The **module map** when the brief was a platform, the plan's task list otherwise. Both
already existed, both were already ordered, and neither had ever been named as the thing
the loop walks. `run.loop.queue` names it; `run.loop.arm` says where the mode is armed,
and the default for a queue-bearing run is **after decomposition** — arming at preflight
arms a loop with nothing to walk.

Arming is a consequence, not a request, for the same reason the mode is recorded rather
than asked for: a capability the operator must remember to switch on is one they forget
on exactly the run that needed it.

**What arming does not change is stated where it could be missed.** The four stops are
the four stops; a `manual` gate still waits; an outward act still needs its own specific
authorization. *A generic flag is not a specific authorization*, and arming a queue is
the most generic flag there is — guarded, because that sentence is what the deploy floor
rests on.

### `mode: dynamic`

`interval` was the only mode while a fixed tick was the only primitive. A harness that
can schedule its own next turn picks each delay from what it is waiting for, and **prints
the delay it chose** — the disclosure that replaces an interval run's job id. A run
silent about its pacing cannot be told apart from one that quietly stopped, which is the
claim this file already forbade for harnesses with no primitive at all.

### The goal is re-read between items, not only the board

Each iteration already re-measured the work-list, which answers *what is open*. It did
not answer *whether the open thing still serves what this run was for*. A queue built at
stage 2 outlives the reason it was built, because the operator learns things between
items and says so. So the bottom of an iteration now quotes the goal, states whether the
next item still serves it, and re-orders or re-scopes when it does not — a row that stops
serving the goal leaves for the board with its reason.

A queue re-derived only by `age` and `sev` is honest about priority and silent about
purpose. Both numbers can be right while the run finishes something the operator stopped
wanting two items ago.

### The reader found the contradiction, not the bug

R-005's reader defeated all five guards and then read the doctrine as a reader rather
than its author. Part 1a said *"arming is a consequence, not a request"* and stated its
trigger as a fact about the **work** — a queue with more than one item — with no
antecedent about configuration. Two sections above, the same file says **Default off.
Silence arms nothing, exactly as silence authorizes no deploy**, and `grill.md`'s deploy
floor is explicitly said to rest on that distinction. Read cold, Part 1a arms a loop in a
project with no `pipeline.json` at all.

The contradiction was in the phrasing, not the intent — `stages.md` had already restated
the rule with the antecedent intact. **Part 1a gave way**, and a guard now requires it to
state its precondition, because five guards checked for the presence of strings and not
one would have noticed either reading.

What the reader took apart in the guards, all verified by planting the defect and
watching `PASS`:

- **a deleted contract was a skip, not a failure.** Removing the whole `run.loop` block
  left CI green with two tidy `unlooked` lines — and `run` allows additional properties,
  so the example still conformed while meaning nothing;
- **`_loop_block` searched instead of addressing.** A deprecated top-level `loop` earlier
  in file order answered for the real contract;
- **presence tests let the release's own thesis be reverted.** `arm` existed, so setting
  the example back to `preflight` passed;
- **`if _qv and …` short-circuited itself** — an open string in place of the queue enum
  passed, which is precisely the failure the guard was written for;
- **the floor guard had never tested its own rule.** Its phrase entered the file in
  v1.11.0, twenty-nine releases earlier; both doctrinal statements could be deleted and a
  Rationalizations row kept it green;
- **the dynamic-disclosure regex was content-blind** — a sentence keeping the words and
  inverting the obligation passed — and it triggered off the prose word, so renaming the
  mode switched the guard off;
- **`arm the mode` matched a bullet forbidding arming**, and `"loop"` matched any
  sentence about any loop. Both now key on the schema's own tokens.

Guards 233 → **248**: seven more probes than the first pass shipped with, six of them for
fail sites that did not exist until the reader's findings were fixed.

### Also

- **A guard was listing the legal modes instead of reading them.** Adding `dynamic`
  failed the guard on a correct example — a check enforcing its own staleness. It now
  reads the enum out of the schema.
- Guards: 233 → **248**, one per new fail site, each with its planted defect.

## v1.39.0 — the skill could not be reached by the word "audit"

`references/audit.md` has said since v0.1.0 that an audit may be **the whole task** —
stages 3–5 producing findings and fixes instead of a feature. No routing surface named
it. Every trigger noun was build-shaped, and the exclusion clause read *"Not for:
answering a question, explaining or reading code"* — which is the opening move of an
audit, a bug hunt, a production check and a PR review alike.

### Measured, not supposed

Ten routing queries, one fresh agent each, holding nothing but the competing skill
descriptions and one user sentence (`evals/routing/render.py`, results in
`evals/routing/RESULTS.md`). **7 / 10 before.** The three misses were the three the board
row predicted, and none of them was a failure to find a match — each agent **quoted this
skill's own exclusion clause back as the reason it refused**:

- «проверь, нет ли ошибок в обработчике вебхуков» → `none`
- «проверь, всё ли живо в проде после вчерашнего релиза» → `none`
- «посмотри PR #24 и скажи, что там не так» → `none`

A fourth result only the reasoning shows: «сделай аудит модуля оплат» *did* route, and
justified it by stretching the build verb `hardening`. A right answer resting on a
stretch is one rewording from a miss.

### The boundary is what a request ends in

Not whether it reads. An answer stops in the conversation; a change **or a finding**
lands in the tree, and the pipeline is what carries REQ rows, board rows and fixes
there. The description, the portable routing rule and the Cursor rule now all say so,
and `reading` is gone from the exclusions — guarded, so it cannot come back quietly.

### Two things the harvest found before the first grill question

- **`перевести` was locked into the verb list by the v1.9.0 design and never shipped.**
  It existed in exactly one place in this repository: the design that locked it.
- **`REQ-003` was accepted `verified` anyway.** The evidence recorded was the clause's
  *shape* and its character count — neither of which can see a missing member of the
  list the REQ locked. An L1→L2 absence that passed an L5 check. A guard now reads the
  locked list out of that design and compares it to the shipped surface, so the next
  dropped verb is a failure rather than a week.

### The reader earned its standing instruction

R-005 exists because an author's probes only exercise the shapes the author already
thought of. Dispatched on the nine new guards, an independent reader defeated them
**fifteen ways**, each verified by planting the text and watching the validator still
print `PASS`. The three worth naming:

- **A presence test over a whole file proves a word exists, not that the rule says it.**
  The reader deleted the entire boundary clause from the Cursor rule, put the old
  exclusion back, added one unrelated sentence elsewhere containing the same four class
  names — and the guard passed. Both cross-surface checks are now scoped to the
  `## Routing` section.
- **A `should_not_trigger` control counted as coverage.** The eval-coverage guard joined
  every query regardless of category, so deleting all four findings evals and mentioning
  the words in one negative control certified *named and untested* — the exact state it
  cites `B-046` for — as green. It now reads `should_trigger` queries only.
- **The anti-dormancy sentinel was itself one synonym from dormant**, and the
  locked-verb guard read a regex out of a document this repo forbids maintaining, so
  relabelling one heading in a superseded design would have silenced the check that
  exists because a verb was silently dropped. Both now fail loudly instead.

Nine of the fifteen were in checks written that same hour. The tenth fail site had no
probe at all — ten branches, nine tests — which is the invariant the repository states
about itself and did not keep.

### Also

- **False-positive controls, because widening a vocabulary can steal work.** Three
  competitors already claim the word *audit* — `seo-aeo-audit`, `ux-audit`,
  `make-skill`. All three are eval cases now, and all three still won their query.
- **R-003 sweep** turned up the same word-map ceiling that produced R-006, in the
  redaction-rule count: past ten it compared against the digit alone. It now accepts
  either form and names both when it fails.
- Guards: 218 → **233**; eval cases 21 → **28**; description 956 → 1004 of 1024, paid for
  by cutting mechanism prose that could not affect routing.

## v1.38.0 — the wall came down, and a green started meaning something

An audit of this skill measured nineteen problems and asked one question of all of them:
*why can an agent that follows every rule here still report work it did not do?* The
answers were not in the doctrine. They were in how much of it there is, how it is
delivered, and what nobody checks.

### The wall

`commands/task-pipeline.md` — the first text an agent reads when the skill fires — was
**one paragraph of 1281 words carrying 25 obligations, with a 4115-character line**.
Twenty-five duties in one breath: which of them an agent obeys is a function of position,
not importance.

Same doctrine, eight headed sections, nothing removed:

```
paragraphs        5  ->  34
longest paragraph 1281 words  ->  295
longest line      4115 chars  ->  261
```

### The trigger surface said nothing about two of the three modes

`setup` and `checkup` appeared in **no browsable surface** — not the skill description,
not the command description, neither manifest. `checkup` exists specifically to be run
when nothing else is; the only way to learn it existed was to open the file you open by
running the thing it replaces.

The description was also at **1015 of its 1024-character ceiling**, with ~40% spent on
mechanism prose that cannot affect routing. Cut, both modes named, and it now sits at
956 with room to grow. Both manifests described the product as it stood at v1.30 — seven
releases of capability absent from the only text a marketplace shows.

**The plan proposed separate command files for the two modes and the doctrine refused
it.** `exposure.md` says *a mode of the command, not a new command, because a second
command costs every surface a command touches*. The doctrine is older than the plan and
it won.

### `test/probe.py` — R-001's retirement condition, three years of releases late

The standing instruction R-001 has said since 2026-08-03: *prove the plant landed in the
text the check actually parses.* Its retirement condition, written at birth, was **"a
probe harness exists that asserts the plant changed the parsed text"**. It was never
built, and three probes failed in a single day for want of it.

Three assertions per plant, and the third is the one hand-rolled probes keep missing:

1. the substitution **landed** — `replace` matching nothing raises nothing;
2. the exit code is **non-zero** — never a `FAIL` line on stdout;
3. **the guard that fired is the guard under test**, named up front rather than
   recognised afterwards. A plant that trips some *other* check has proved that other
   check works.

The harness self-tests its own failure branches (`npm run test:probe`), because a
harness whose failure path has never executed is exactly what it exists to stop. **On its
first use it caught two of this release's own guards being too loose** — one accepted any
three reader states rather than requiring the load-bearing one, and one matched
`none found` against a coincidental sentence in another paragraph.

### The independent reader is now dispatched by a stage, and read by its output

R-005 requires an independent reader on any change that adds or widens a check. Four pull
requests of almost nothing but check work were opened in one day; the review app reported
**`skipping`** on every one, and twenty-two guards merged on author probes alone. Nothing
was violated. Nothing read the reviewer's output either.

Stage 7 now dispatches the reader — a subagent it can watch, a bot whose **verdict** it
then reads, or a person — and records exactly one of three states beside the gate:

```
reader: 6 findings, 4 confirmed
reader: none found
reader: NO READER — <why>
```

The third is printed, never omitted. *A reader was requested* and *a reader reported* are
different facts that look identical in a transcript.

### `learned.md` rule 22 — an operation that changed nothing reports like one that changed everything

Four incidents in two programmes, each invisible until something downstream failed: an
import that never landed, a doctrine phrase worded differently, a `gh` call refused behind
`>/dev/null`, and a test piped to `head` so `$?` belonged to `head`. **Assert the effect,
not the call.**

### The retro's uncapped narrative stopped being read in full

The doctrine said stage 0 reads three sections of `docs/superpowers/retro.md` in full
because *"all three are bounded by construction, which is why the cap is not
negotiable."* Measured, that claim was false:

```
Standing instructions   ~ 1 394 tok   capped at ten rows
Run stamps              ~ 1 842 tok   one line per run
Recent log              ~10 937 tok   narrative — capped by nothing   ← 74% of the file
```

An uncapped section inside a source that **binds** the run is precisely what makes the
capped part get skimmed. The log is now **queried by the task's nouns**, like the
archive; the instructions and the stamps are still read in full, because they are the
part that is actually bounded.

**Stage-0 reading floor: ~47 750 → ~36 950 tokens** from that one change.

**And the audit that found this over-claimed in the same paragraph.** Its own table said
`stages.md` was *"read in full at stage 0"*; grepping the obligation returns only the
retro. The report now says *the gates a run must satisfy*, which is weaker and true.

### The preflight now says what has not been measured

It reported companion availability in careful detail and this skill's own evidence not at
all — while `evals/RESULTS.md` recorded **one self-observed run by the author and zero
blind runs on zero models**. A skill silent about its own evidence is read as tested, by
the bundle that demands evidence of everyone else. The line prints while no blind run is
recorded and disappears when one is; it is a state of the evidence, not a warning.

The suite itself was frozen at the v1.9 feature set — **zero cases** touching the board,
the verification ledger, the exposure line, the progress rail, `checkup`, `setup`,
`copywriting` or `sheleg-design`. Now **21 cases**, including the two no-task modes,
the three stage-3 tracks, the progress rail and run ledger, the dispatched reader, and a
question that must **not** trigger the pipeline at all.

Guards: 210 → **218**, property checks 8.

## v1.37.0 — the audit, and the four things it found the pipeline could not say

One release, four modules, and an audit that put four questions to this pipeline and
answered them with measurements rather than opinion:

- **99 shipped REQ, 99 of them at `Human: never`** — nothing has ever been confirmed by
  a person, and the exposure line has been saying so on every run.
- **`copywriting` appeared 0 times in the bundle and `sheleg-design` once**, as a name in
  a README list.
- **The review loop ran ten rounds, ten, eight, four, three** against a stated ceiling of
  two stage re-entries — because a review round was named in no cap at all.
- **Nothing ever printed which pipeline, which module, or which iteration was running.**
  The run checklist existed and was marked *"copy it, tick it"*.

Guards: 188 → **210**, property checks 8. Every one watched failing against a planted
defect, and three of the probes were wrong before their guards were.

### The lesson that stopped dying in the repository that learned it

`retrospective.md` has said *"open an issue upstream"* since v1.9.0 and named no
repository, no trigger and no authorization — an instruction on rung 1 that every reader
took for done. So a defect in **the skill** — a gate that loops, a doctrine promising
what nothing enforces, a rule firing on the wrong shape — was rediscovered independently
in every project that ran the pipeline and fixed in none of them.

**Opt-in, per project, off by default**, `pipeline.json` → `retro.publish`:

```json
"retro": { "publish": { "repo": "…", "label": "retro-insight", "redact": "strict" } }
```

Absent, nothing is published and nothing is asked. Opening an issue in another
repository is an **outward act**, and an outward act taken from a generic flag is one
nobody authorized — the same floor deploy authorization uses.

**The body is printed in full before it is sent, and the printed string and the sent
string are one string.** Redacting after the print, or printing a tidier version of what
actually goes out, is the false-success shape this bundle names outright: a mechanism
reporting on itself instead of on what it did.

**Five numbered redaction rules**, because *insight only* is not a specification. No host
paths — only paths inside task-pipeline itself. No host identifiers: repository,
organisation, branch, commit, tag, issue. No code, no config values, no data, not even
redacted. No names of any kind. And the title states the **class**, not the incident.
When in doubt the rule is subtraction: an insight that survives losing a detail is still
an insight, and a detail that leaks cannot be recalled from an index.

**Seven guards, and one of them was broken by the fence above.** The check that makes the
doctrine's own worked issue obey its own rules was silent against three separate plants —
an absolute path, a commit id, a foreign repository slug — because the fence scan matched
` ``` ` followed by a newline, and the ```json block one paragraph up made every
subsequent fence pair with the wrong delimiter. Five fence scans across four modules had
the same bug; all are language-tolerant now, and the earlier modules' probes were re-run
to prove the change broke nothing (R-003: sweep the detector's siblings).

### What it does, how it sounds, how it looks

The audit measured this one rather than argued it: **`copywriting` appeared zero times
in the whole bundle, and `sheleg-design` once — as a name in a list in the README.**
Meanwhile the companion matrix named six super-ux surfaces while super-ux shipped eight
skills and fifteen commands. So a run designed a flow, then wrote its interface strings
by taste and picked its visual values at the keyboard, and every gate in the pipeline
reported green over both.

**Stage 3 now runs three tracks, and none substitutes for another:**

| Track | Answers | Owner |
|---|---|---|
| UX | what the interface must **do** | super-ux — the WHY→UI→scenario chain |
| COPY | how it **sounds** | `copywriting`, against the brand pack |
| VISUAL | how it **looks** | `sheleg-design` — tokens, themes, rhythm, motion |

Each carries its boundary in both directions, because a track that over-reaches is
routed around. The copy track takes interface strings, errors, empty states, the
landing, the user-facing changelog — and explicitly **not** commit messages, PR text,
code comments or a developer README. The visual track takes the visual layer and
explicitly **not** a purely structural change, which is the UX track's.

**A refusal is a sentence, never a silence.** *"as is"* ends the visual track and
*"draft"* ends the copy track; either is the operator's call and costs nothing. But it
is recorded in the brief and said in the close-out, because a track skipped in silence
and a track that ran are identical afterwards — the `⊘` rule one layer up.

**`sheleg-design` joins the matrix and the preflight**, and super-ux's row finally names
its copy half.

**The new guard found a live defect on the clean tree before it found anything else.**
It compares the matrix's *"needed for stage N"* cell against what that stage actually
says, and reported that `chrome-devtools` had been pointed at **stages 5–6 since the day
it was added, with stage 5 never naming it**. Fixed here: stage 5 now checks a rendered
surface per task, while the implementer that wrote it is still dispatched.

**And a probe found a hole in its own guard.** Removing `copywriting` from stage 3 left
the check silent, because it reads matrix **row names** and the copy half lives inside
super-ux's own cell — precisely where it had been invisible all along. A second, narrow
check now covers the three tracks by name. It is narrow on purpose: generalising the
sub-skill mapping would demand stage 3 name `/brand-lint` and `ux-audit` too, and a
check that over-reaches is switched off by the third person who hits it.

### The loop that had no ceiling, the exemption nobody measured

Three findings from the same audit, all of them gates behaving as prose.

**The review loop was capped by nothing.** `build.md` caps the stage-5 fix loop at five
rounds per task and `loop-guard.md` caps stage re-entries at two — and a review round is
neither, so nothing counted them. The run stamps say what that cost: **ten rounds, ten,
eight, four, three**, in one programme.

**A flat cap would have been the wrong fix**, and this is the part worth keeping. Every
one of those runs recorded *"none from my probes"* beside its count — the reader was
still finding real defects on round nine. Stopping at two would have shipped them. So
the cap is a **decision point**: default 3 rounds per artifact (`pipeline.json` →
`run.review.maxRounds`), and at the cap the run stops reviewing and prints the pair
`audit.md` already defines, per round:

```
review cap reached — 3 rounds — artifact: test/validate.py
  round 1: 12 new · 0 self-inflicted
  round 2:  5 new · 1 self-inflicted
  round 3:  1 new · 3 self-inflicted
```

Self-inflicted ≥ new and the axis is exhausted; new still ahead and continuing is the
operator's call, made with numbers rather than fatigue. Rounds are counted from the run
ledger's `touch:` pass numbers, never from memory. Every finding left open at the cap
leaves as a board row with its evidence, never as a shrug.

**The pipeline ran eleven stages over a typo because nothing measured the exemption.**
The boundary — a one-line fix, a mechanical rename — existed in prose and depended on an
agent remembering it. Stage 0 now runs a three-question triage with something behind each
question, and **proposes** the short path: stages 1–4 marked `⊘` with the triage answer
as the reason. Propose, never take: the answer goes in the brief and silence takes the
full flow, the same floor deploy authorization uses. The glyph is what makes it safe —
a skipped stage is printed on the rail *with its reason*, and a skip nobody can see is
indistinguishable from a stage never entered.

**`exposure.md`'s worked example disagreed with its own output, in both directions at
once.** It taught `31 releases since the last human confirmation` while the code printed
`releases carry one`, and it hardcoded `99` — a live count that drifts. The example now
carries no digits at all, and a guard computes the format's vocabulary **from the print
statement** and requires the doctrine to show it.

**Six new guards, each watched failing.** Two of them found their own author first: the
short-path check was scoped to a paragraph while the bullet it reads carries a fenced
block, so it stopped three lines short of the glyph and passed in silence — and its
replacement matched the fence's own backtick and accused the clean tree. A detector that
finds itself before it finds anything else is checking the wrong thing, twice in one
module.

### A run that says which pipeline it is on, and where in it

An audit of this pipeline asked four questions of it. The first was *does the agent
understand the plan it is executing?* — and the honest answer was that nothing in eleven
stages ever printed which pipeline, which module, or which iteration was running. The
run checklist existed and was marked *"copy it, tick it"*: an instruction with no gate
behind it, which is the same failure it was written to prevent, one level up.

**The run prints where it is, at two boundaries and only two** — task start and
iteration close ([`references/progress.md`](plugins/task-pipeline/skills/task-pipeline/references/progress.md)):

```
task-pipeline v1.34.0 · pipeline-audit · module P1 «the progress print» (1 of 4)
  0 ✓  1 ✓  2 ✓  3 ▶  4 ·  5 ·  6 ·  7 ·  8 ·  9 · 10 ·
  ███████░░░░░░░░░░░░░░░░░░░  gates 3/11 · now 3 Spec · manual
  board B-028 · carry-over 0 rows · exposure 99 never · unlooked 0
```

An iteration is already defined as *one item taken to its gate*, not one agent turn.
Printing per turn would put a bar above every tool call and teach the operator to skip
the block that matters.

**The rail is computed from the project's own `pipeline.json` and carries no stage count
of its own.** The eleven above are this plugin's *example* flow; a host replaces them. A
bar reading `gates 5/11` in a project with six stages is a summary confidently wrong
about the thing it summarises, printed in the one place a run is trusted at a glance.

**Every number on the block is borrowed, and the block computes nothing.** `board` comes
from the backlog, `carry-over` from the ledger, `exposure` from the verification file,
`unlooked` from the gate's own disclosure. If the block disagrees with a gate verdict,
the block is wrong — that direction, always, because the gate looked and the block
quoted. A progress line that computed its own counts would be the fourth copy of the
truth, and this repository already knows what happens to those.

**A glyph is read from the verdict its gate wrote, never from memory.** `✓` means the
gate passed, not that the stage was walked — a rail is a summary, and a summary is the
easiest artefact in a run to write from recollection. `⊘` may never be silent: a skipped
stage with no recorded reason is indistinguishable from a stage never entered, and the
two mean opposite things.

**`.task-pipeline/run.md` is finally written.** `loop-guard.md` has named it since the
day it shipped, calls its own churn detection *mechanical*, and reads `touch:` lines from
it — and **no run had ever created it**. The detector had no input; the guard sat on
rung 1 while every reader took it for rung 3. It is now seeded at stage 0 from
[`templates/run.md`](plugins/task-pipeline/skills/task-pipeline/templates/run.md), named
in that stage's gate, and serves two readers: the guard reads the touches, the progress
block reads the stage verdicts and counts the `iter:` lines. The counter is a `grep -c`,
not a number the agent is carrying — after a compaction the agent's count is gone and
the file's is not.

**Five new guards, each watched failing against a planted defect.** The header block's
field set compared **both ways** between its two copies; every glyph a rail prints
present in the legend; the computed-rail promise stated where a reader meets it; and the
ledger's line shapes compared declared-vs-shown **and** against the files that read them.
The first version of the fourth probe removed one of three `touch:` lines from the worked
log, left the shape shown, and read the guard's correct silence as a broken guard — R-001
again, and the reason it is a standing instruction.

## v1.33.0 — the number, the list, and the command that shows them with no task running

Three modules shipped as one, because they are one capability: the index, the list it
produces, and the command that prints them when nothing else is running.

**Exposure is a vector with its components named, never a probability.** The request that
started this asked for *"the probability of an error"*. It is not computable from these
inputs, and a number dressed as one is the class this repository has spent its history
removing — so the guard rejects a `%` on that line outright:

```
exposure: 99 unverified · never checked · 10 releases carry one
    REQ-001  references/setup.md — the entry audit: when it runs …   v1.10.0
    …
    and 91 more — the full list is `/task-pipeline checkup`
```

**`never checked`, not `0 days`.** When no row has ever been confirmed — this repo's
exact state — a zero would read as *checked today*, the precise inversion this pipeline
exists to prevent. The literal is required by its own guard.

**A single score was refused on purpose.** One number invites a threshold, and a
threshold here is a target on `never`, which `verification.md` says may never have one.
The components are one line; a reader can hold three.

**`/task-pipeline checkup` runs with no task in flight**, which is the whole point:
accumulated unconfirmed work is invisible precisely because nobody is running a pipeline,
so a check living only inside a run can never say *stop, fourteen things are
unconfirmed*. It reads four files this pipeline already keeps and writes nothing unless
asked — and then only board rows whose `Source` names the checkup, printed before they
are added.

**And `continuity.md` finally names the file it always demanded.** It has required each
iteration to re-measure the work-list since the beginning, and said *"next up is X"* is
a claim no gate reads. The board is that list; the claim now cites a `B-NNN`, which can
be checked, rather than a description, which cannot.

**Two defects in the new guard, both self-inflicted and both instructive.** Its needle
looked for *"never a percentage"* while the doctrine it guards says *"no percentage,
ever"* — guard and prose written an hour apart, already disagreeing. And the `%` check
searched for a literal that its own line necessarily contains, so it matched **itself**
and passed a planted percentage. A detector that matches itself first is checking the
wrong thing.

Guards: 185 → **188**, property checks 8.

## v1.32.0 — the column a machine may not fill

Stage 8 already performs the verification trio, reads the CI verdict and opens the
rendered page. All of it **per run**, none of it accumulating — so *"which features has
nobody confirmed since they shipped?"* had no artifact to be asked of.

`docs/superpowers/verification.md` is one row per shipped REQ, and its point is a single
column: **`Human` — a date, or the literal `never`.** Nothing else. *"soon"*, *"mostly"*
and *"looks fine"* are how a column stops being answerable, and this is the one thing in
the pipeline a machine may not write on your behalf.

**`never` is a fact, not a failure.** The count has no floor, no direction, and may
never be given a target — the moment `never` becomes something to avoid writing, the
column starts lying and the pipeline loses its only signal about the world outside its
own checks. One of the new checks is a **property check** proving that filling the
column does not fail the build: a gate that punishes an honest answer guarantees there
will not be one.

**It keys to the brief, not to the coverage table**, and that was a measurement rather
than a preference. Ten acceptance files here carry their first REQ-bearing table in
nearly as many shapes, because `acceptance.md` fixes it in prose — the same drift the
carry-over ledger reached with six header shapes. Eight of nine briefs carry
machine-readable `| REQ-NNN |` rows; the ninth was this programme's own brief, fixed the
day it was measured. That the coverage table has no template is a real finding with a
real cost, and it is on the board rather than fixed here.

Both directions, because they are different failures: a shipped REQ that entered no
ledger, and a ledger row about a requirement no brief carries.

**Seeded truthfully: 103 rows, every one `never`.** Thirty-one versions shipped, and not
one recorded instance of a person confirming a shipped requirement afterwards. That is
not a new problem — it is the first time it can be stated.

**Review round: N1's lesson carried forward by its wrong half.** The Human check
scanned *every* cell for a date or `never`, so a bare date sitting in the Note column
satisfied a row whose Human read *"soon"* — precisely the prose the guard exists to
reject. N1 concluded *"the header names the candidate columns and the match happens
inside them"*, not *"never look at columns"*; this file is templated and has exactly one
shape, so the column is located by name and read alone.

**A file that states one truth twice, and drifted for two modules.** `artifacts.md`
carries an ASCII layout tree *and* the tables that name the same files — and the tree
never gained `backlog.md` (shipped in v1.31.0) or `verification.md` (this release), both
named in tables a hundred lines above it. A reader found it; nothing compared them. The
tree is now computed against those tables.

The seeded ledger also truncated its `What` column at 72 characters, leaving unterminated
code spans, while the template it follows says *"copied from the brief, not re-worded"* —
sixty-seven of a hundred and three rows landing at exactly 72 is a script's fingerprint,
not an editor's. Reseeded in full: 26 to 246 characters, none at 72.

**The ledger recorded unbuilt features as shipped and verified.** The seed took every
REQ from every brief — including this programme's own, whose REQ-004/008/009/010 belong
to modules that do not exist yet, and whose N2 rows were stamped with N1's version. In
the file whose entire purpose is *what actually shipped*. Reseeded: **99 rows**, four
omitted as not yet built, each module stamped with its own release.

**And the count is printed.** It was computed and dropped on the floor for a release — a
measurement nobody surfaces is the same silence as no measurement:

```
verification: 99 shipped REQ · 99 never confirmed by a person  (disclosure — no floor, no target)
```

Ninety-nine shipped requirements, not one confirmed by a person. That is the answer to a
question this repository could not previously ask.

Guards: 175 → **185**, property checks 4 → 8.

## v1.31.0 — the board, and the pointer that was never the one dangling

The carry-over ledger has always offered `backlog` as a home for a deferred row — a
place the pipeline **named and did not own**. The obvious fix was to build that
backlog. Measuring first changed the target: across ten ledgers in this repository,
**not one row has ever used that value.** The dangling pointer was never `backlog`. It
was `open` — **sixteen rows across six ledgers** (later re-measured: **24 rows across eight**), deferred out loud and filed nowhere.

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

**A tightening that turned the guard off.** Fixing the false positive above, the
separators were hand-listed — and the list omitted the arrow this repo's own annotations
use (`open → B-001`), so **all twenty-four resolved rows became invisible** and the
check passed by seeing nothing at all rather than by finding everything homed. The one
negative test covering that path caught it, which is the entire argument for the suite
in a sentence. The separator is now *"not a word character"* and the predicate is proven
against eight concrete cases instead of one.

**The detector reversed three times, and the third answer was in between.** Positional
read the wrong cell wherever a ledger carried two status columns. Pure-text then broke in
both directions with one regex — too strict for a live row worded *"open as a printed
exclusion"*, too loose for a description reading *"Open-source …"*, because a hyphen is
punctuation exactly like the arrow. What ships reads the header for **candidate columns**
— all of them, never just the last — and matches a status on a word boundary **inside**
them. A description cannot masquerade as a status because it is never looked at.

Every reversal was found by a reader. None by a probe.

**Two surfaces did not know the board exists.** `cursor/rules/task-pipeline.mdc` and
the command restate stage 0 and stage 10 in detail, and neither mentioned it — the same
one-rule-in-one-file-of-nine class this repository has a guard for on the rotation axes
and none for a new mechanism. Both carry it now, the Cursor rule by restatement because
it is self-contained by contract.

**The class that ran through six rounds is closed by computation, not by a sixth fix.**
Every one of those rounds found the same shape: the doctrine promised a resolution
trigger the check did not enforce — `open` alone while the prose said `backlog`,
`backlog` added while `unresolved` was still only promised, *"two triggers"* written in
a file whose code checked three. `audit.md` says a class seen twice becomes a script, so
the enumeration is now **extracted from the regex** and required to appear wherever the
doctrine lists it, in both directions. A guard that loses its own source fails rather
than passing.

**And the seam's origin was the template nobody opened.**
`templates/carryover.md` — the first ledger every host project ever sees — showed a bare
`backlog` home as a *settled* outcome, with a worked example carrying no board id. Six
rounds went into the doctrine, the guard, the board and three consuming surfaces before
anyone read the file the value came from. It names three unsettled values now, its
example carries a real id, and the guard checks the template beside the live ledgers.

**The guard written to close a false-success class had the class.** It verified that a
trigger word appeared *somewhere on the page* rather than that it was presented as an
enabled trigger — so prose reading *"those are the only two triggers"* would pass on the
strength of the third word appearing in a later paragraph. Scoped to the enumerating
paragraph now, and what it still cannot decide is written into the code rather than
implied by its silence.

Guards: 156 → **175**, property checks 1 → 4.

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

> **Never released on its own.** There is no `v1.5.0` tag and no `1.5.0` on npm,
> so `npm install task-pipeline-skill@1.5.0` and `git checkout v1.5.0` both fail. This section
> describes work that shipped inside a later version. The note is here because
> the section reads as a release (2026-08-17, umbrella `B-71`).

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
