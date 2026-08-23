# Audit — finding what is missing, cross-cutting

Every gate in this pipeline asks *"is this artifact good?"*. Stage 10 asks *"is
anything from the list lost?"* ([`acceptance.md`](acceptance.md)). **Neither asks
what should have been on the list and never was.**

That gap is not an oversight in the gates. It is structural: a gate compares two
things, and **a contradiction has two sides while an absence has one.** Comparing
the spec against the plan finds a requirement that was dropped. It cannot find the
error path nobody specified, the entity nobody gave an owner, the failure mode
nobody named — because on both sides of every comparison, it simply isn't there.

This file is the method that finds those. It is **cross-cutting**: stage 10 runs it
before writing the coverage table, the program loop runs it per module, and a task
whose whole job is "audit X" runs nothing else.

## Contents

- Three things that are easy to confuse
- Why "look again, more carefully" stops working
- The ladder
- How one audit pass runs
- Two copies, and which one wins
- Silence is not a reading
- Exit criterion — the part usually skipped
- The three rules that stop this becoming another loop
- When this runs
- Rationalizations

## Three things that are easy to confuse

| File | Runs when | Answers |
|---|---|---|
| [`acceptance.md`](acceptance.md) | stage 10 | did everything **on the list** ship, with evidence? |
| [`loop-guard.md`](loop-guard.md) | any **editing** loop churns | is this pass undoing the last one? |
| **this file** | any **audit** pass | what is broken or missing that nobody has compared? |
| the `project-audit` skill | a **whole project** is the subject | what is true of this repository today — from a cold start, with no brief |

**`project-audit` is the cold-start caller of this file, not a second copy of
it.** This ladder needs a REQ row and a module map to walk; most repositories
have neither, and *"your spine is missing"* is a true first finding and a useless
audit. That skill discovers what the project is, probes it, reads the production
evidence a repository cannot hold, and hands phase 4 back here — so the method
below stays the one place it is written.

`loop-guard.md` governs loops that *change* things — the fix loop, a re-entered
stage. Its trip means a decision is being re-litigated at the wrong altitude. This
file governs loops that *look* for things. Its trip means the axis is exhausted,
which is a different failure with a different exit. Both can bind one run; they do
not overlap.

## Why "look again, more carefully" stops working

The method most audits use is **horizontal**: compare the documents against each
other, then do it again. It works, and then it fails in a way that is invisible
from inside it. Measured over seven passes on a production repository:

| Pass | Findings | …of which the previous pass's own fixes caused | Self-inflicted share |
|---|---|---|---|
| 4 | 12 | 5 | 42% |
| 5 | 17 | 9 | 53% |
| 6 | 13 | 10 | 77% |
| 7 | 19 | 4 | 21% — see the note below |

**The trend above is measured over passes four to six, and pass seven is not part of
it.** 42% → 53% → 77% is the decay this section teaches; the seventh pass fell back to
4 of 19 and **the record does not say what that pass did differently.** The row stays,
with the gap named, for two reasons. Deleting a measured row to protect a claim is the
opposite of what this file asks of every gate it describes — and the vertical pass
described below cannot be credited for the drop, because it is a separate pass over the
same repository, not the seventh. Whatever pass seven did, it is unrecorded, and an
unrecorded cause is what this table has to say about it.

By pass six the audit was **mostly repairing itself**. Not fatigue — arithmetic.
Each pass edits the corpus the next pass reads, so the newest edits are always the
least-reviewed text present, and they are what the next pass finds. The count stays
healthy while the yield goes to zero.

A single **vertical** pass over the same repository — one capability walked down
through its layers — found nine defect classes those seven passes had been
structurally **unable** to see. Not missed: unable. Two of them:

- **A component that encrypts every object in the system had no key store
  anywhere.** Its sibling's key table had been modelled for weeks. A comparison
  needs two sides; this had one.
- **An edit appended a new version while the derived index still pointed at the
  old text.** The archive is correct. The index is correct. The answer is correct —
  *against a version nobody is looking at.* Compare archive to archive and index to
  index: both pass. **The defect lives in the seam.**

## The ladder

The rungs are **layers of one deliverable**; the work is the **seams between
them**. Each rung's artefact either exists or it does not — that is what makes
absence findable.

| Rung | Layer | The artefact that must exist |
|---|---|---|
| **L0** | Requirement | a `REQ-###` row in the brief **with a named check** |
| **L1** | Decision | the locked decision this REQ rests on — **an entry in the register** (`DEC-####` or an ADR), or a `CONTEXT.md` term ([`documentation.md`](documentation.md)) |
| **L2** | Design | a spec section carrying `covers: REQ-…` |
| **L3** | Contract | an exact signature or schema · **and its failure behavior** |
| **L4** | Task | a plan task with `Implements:` and a DoD satisfiable **as written** |
| **L5** | Change | the commits — the thing actually in the tree |
| **L6** | Test | an **executed** assertion, by name — never "the tests pass" |
| **L7** | Surface | what a user reaches: scenario, screen state, CLI output, runbook |
| **F** | Frame — *conditional* | UI work with Figma on: one frame per `SCR-NN/<Screen>/<state>`, **in the one file the project recorded**. Not a step in the sequence — a **second, parallel statement of the same surface**, made in pictures |

**Audit the seams, not the artifacts.** Each rung is internally consistent most of
the time — that is exactly what the horizontal pass is good at, and it has already
done it. What survives lives between rungs:

| Seam | The question | What absence looks like here |
|---|---|---|
| L0→L1 | does the requirement rest on a **recorded** decision? | a REQ whose check implies a choice nobody ever made or wrote down |
| L1→L2 | did the decision reach the spec? | an ADR or glossary term agreed at the grill that no spec section cites |
| L2→L3 | does the section name its contract **and what happens when it fails**? | "handles errors" — no code, no shape, no caller-visible reason |
| L3→L4 | does every contract have a task that builds it? | stage 4's set-equality covers REQ→task; **nothing** covers contract→task |
| L4→L5 | did the DoD land in the tree? | a DoD line nothing in the diff satisfies, marked done anyway |
| L5→L6 | is there an executed observable? | "tests pass"; a test that still passes with the production code deleted |
| L6→L7 | can a user reach it, and does a doc say so? | shipped behavior with no scenario, no `--help` line, no runbook entry |
| L7→L0 | does the shipped surface satisfy the requirement's **statement**? | it does what the task said and not what the requirement meant |
| L2→F | *(UI)* does the frame render what the spec **says**? | a frame that promises a capability, limit or number the product does not have |
| F→L7 | *(UI)* did what shipped match the frame, or did the frame become fiction? | the frame is still the design of record and no longer describes anything that exists |
| →F | *(UI)* is every frame **in the recorded file**? | a second design file nobody opens, holding real work — the check is a `:fileKey` string match, so it is a gate, not an opinion |

The L7→L0 seam is stage 10's question, expressed as a seam. When it fails, the run
did every instruction correctly and delivered the wrong thing.

### The frame is a second claim, and nothing compares it to the first

Where the project designs in Figma, **super-ux owns the frame entirely** — the
on/off choice, the MCP preflight, the `SCR-NN/<Screen>/<state>` naming, and a
linter that catches a missing link, a broken trace or a stale one. That is a lot,
and none of it is this file's business.

What no linter can check is **what the frame says.** A frame link can be present,
correctly named, non-stale — and the picture behind it can state a retention
window, a credit meter, a pricing tier or a button whose promise the spec never
made and the code never implements. It is a *claim about the product*, rendered,
usually seen by more people than the spec, and frequently the thing a stakeholder
believes. Compare frames to frames and they are consistent; compare specs to specs
and they are consistent; the defect lives in the seam, and only a walk finds it.

So on UI work with Figma on, the walk carries one extra step in each direction:
read the frame against the spec section that covers its `SCR-` id (`L2→F`), then
against what actually shipped (`F→L7`). A mismatch is a finding like any other —
and it is usually the **frame** that must change, because the spec is the contract.
Say which one you are proposing to move, and why, rather than quietly redrawing.

**Editing someone else's Figma file is outward.** Frames live in a shared file that
designers and stakeholders read; changing one is publishing, not local work.
Propose the change, get an explicit go, and only then draw — the same rule as a PR,
a deploy, or docs in another repository. **Creating** one is stronger still: it
needs a named team and an explicit authorization recorded at intake
([`grill.md`](grill.md) → *The design destination*).

**And check the file, not just the frames.** Every deep link is
`figma.com/design/:fileKey/…`, so comparing each `screens.md` link's key against
the canonical record (`docs/ux/foundation.md` → *Design tooling*) is a string
match. A key that differs is a **second file with real work in it** — the failure
that starts with one agent unable to open the recorded file and quietly making a
new one. Nothing else in the chain notices: the new file is internally consistent,
its frames are named correctly, and the linter is green.

## How one audit pass runs

**Scope: one deliverable, all rungs.** One REQ, one module, one capability. Not
"audit the docs" and not "audit the change" — an unscoped instruction is what
produces seven converging passes.

**Input** is the artifact that already names every rung: the brief's REQ row plus
the module map row ([`decomposition.md`](decomposition.md)) when there is one. **If
the input can't supply the rungs, that is the first finding** — do not go looking
for the layers by hand; record that the spine is missing and fix that first.

**Procedure: bottom-up, L0 → L7, running the seam check at each step.**

The direction is not taste. A missing artefact at L1 makes everything above it
meaningless, so top-down you spend the pass polishing a surface for a contract that
does not exist. Bottom-up, the absence surfaces first and the six findings above it
collapse into one.

**Output: findings ordered by seam, never by file.** A file-ordered list reads as
noise; a seam-ordered one tells you **which layer of your own process is leaking**,
which is the thing worth knowing. Each finding carries `file:line`, the artefact
that is missing, and the minimal fix.

**Close through the pipeline, not around it.** A finding that is a genuine gap
becomes a **new REQ row** (with its check) or a carry-over row — the list is frozen
against *narrowing*, never against additions ([`grill.md`](grill.md) → *The REQ
spine*). A finding that contradicts the spec goes back to stage 3; one that
contradicts the plan goes back to stage 4. Auditing is not a licence to edit
across layers in place.

## Two copies, and which one wins

`learned.md` rule 20. When something exists twice — two build files, a schema and its mirror, a
vendored library, one rule written in two documents — the useful question is not *do they agree*.
Diffing them finds the difference and not the **direction**, and the direction is the whole finding:
one of them is what runs, and the other is what somebody reads and edits.

The copies cannot answer it about themselves. The consumer can, and usually in one line:

```bash
grep -rn "Dockerfile\|schema.json\|VERSION" .github/workflows/ Makefile* package.json
```

Two consequences worth stating separately, because they fail differently:

- **The copy that wins is often the one nobody hardened.** Attention goes to the copy people open,
  and the build reads the other.
- **A rule written in two documents is two rules.** One asks, one records; one describes, one
  decides. Edit only the first and the second silently disagrees — which is why a check that knows
  about both is worth more than a note asking people to remember.

## Silence is not a reading

`learned.md` rule 19. The ladder's evidence is commands and their output, and a command that
printed **nothing** has not answered — it has failed in a way that looks exactly like the answer
"nothing is wrong". The instrument and the subject fail identically, because both produce an empty
string.

Before a count, a probe or a diff becomes evidence:

- **The output is non-empty.** An empty result and a broken invocation are the same characters.
- **It is shaped as expected.** A `grep` whose pattern does not match the real output format returns
  success and nothing else, which reads as a clean pass through whatever it was pointed at.
- **Quote what was read, not what was concluded.** "0 findings" is a conclusion; the command and its
  actual output are the evidence, and only they survive review.

This is rule 11's other half. That one insists the exit code is part of the output; this one insists
the output is too. A command that never ran exits `0` and prints nothing, and satisfies a run that
checks neither.

## Exit criterion — the part usually skipped

A deliverable is **not** audited when somebody has read it. It is audited when:

1. every rung has its artefact, **and**
2. **every check you are relying on has fired at least once against a planted
   defect**, **and**
3. **the work-list is re-measured and printed beside the count the run opened
   with.**

Point 3 costs one command and covers the one claim nothing else reads. A run's
closing report says what shipped — and then, almost always, what is left and what
is next. That second half is a statement about the register, and if it came from
the same list the run started with, it has never been checked against anything. A
run can be entirely correct and still hand the operator a false map of the work
([`learned.md`](learned.md) rule 16, [`knowledge-sources.md`](knowledge-sources.md)
→ *Carried-in claims*).

Printing both numbers is what makes the measurement load-bearing rather than
ceremonial: **opened 36 open · closed 34 open · 2 rows closed this run.** A row in
a ledger that nobody reconciles stops being read by the third run. A pair of
numbers that has to agree cannot be filled in without looking.

**A green result from an unproven check is worth nothing.** This is the iron law of
[`tdd.md`](tdd.md) — *if you didn't watch it fail, you don't know it tests the
right thing* — raised from one test to every gate in the run. It applies to the
stage-4 set-equality check, the host's lint and test commands, the super-ux linter,
any script the host added, and every check you write during the audit itself.

Checks written under time pressure lie in ways that read as success: a predicate
that inspects the wrong shape and finds nothing; a probe that removes more than it
adds and reads the shrinkage as a pass; a regex that misses the very word it
searches for. All three pass loudly. **Plant the defect. Watch the check fail.
Remove it. Then trust the green.** Record in the ledger that you did.

## The three rules that stop this becoming another loop

### 1. A class that repeats twice becomes a gate, not a note

Once is an incident. **Twice is a category, and a category belongs in a script** —
the host's lint, its CI, its check runner — where nobody has to remember it.

Writing the third instance into the carry-over ledger is how a known, mechanical
defect class becomes permanent. If the class genuinely cannot be checked
mechanically, say so in one line and *say why*; that sentence is itself a finding
worth having.

**How to write, place, arm, probe and own that script is
[`gates.md`](gates.md).** "Put it in a script" with no place to put it is how the
third instance ends up in the ledger too.

### 2. Every pass changes the axis, not the effort

"Look again, more carefully" is what converges. Passes must be **orthogonal by
construction**:

1. **Seams** — one deliverable walked L0→L7 (this file's ladder).
2. **Invariants across deliverables** — one name, one enum, one owner, one spelling,
   everywhere. This is the horizontal pass, and it is where it belongs.
3. **One class swept end to end** — every error path, every count, every status
   vocabulary, every timeout, across the whole change at once.
4. **The graph against the docs** — where a code graph exists
   ([`knowledge-graph.md`](knowledge-graph.md)), it is a *second, machine-built
   statement of the same system*, and disagreement is mechanical rather than
   remembered: a hub `god-nodes` reports that no document names is an undocumented
   seam; an edge the docs deny is either a leak in the code or a lie in the docs; a
   doc naming a module the graph has no node for describes something that no longer
   exists. This axis is the only one that finds absences without reading for them,
   which is why it is worth rotating onto when the reading axes go quiet.
5. **False success** — not *"is this check correct"* but *"what does this mechanism
   print when it did not look?"* Wrongness is loud and the reading axes above find
   it; a mechanism that reports a win it never checked is silent, so it survives
   every pass that reads for wrongness. Sweep the change for actions trusted by
   their own reply. Definition and the known shapes: [`gates.md`](gates.md) →
   *False success*.
6. **Re-derivation** — take a number the audit has already produced and produce it
   again with a command of a **different shape**, then print both. Not a second
   opinion: a second *route*. Re-running the same command is a spell-check of the
   first run; asking a different question that must land on the same number is the
   only version that can come back disagreeing. The exit criterion is **the pair
   printed** — never "verified", never "matches". A re-derivation reported as
   agreement is a claim about a measurement nobody can see.

   ```
   claimed:    the version invariant is four-way          (CONTRIBUTING.md, prose)
   re-derived: grep -rl '"version"\|^## v' --include='*.json' --include='*.md' . \
                 | wc -l                                  -> 5 surfaces
   verdict:    REFUTED — the sentence and the corpus disagree; the corpus wins
   ```

   Rotate onto this axis when the reading axes go quiet **and the change carries
   numbers**: counts in prose, thresholds, "N of M" claims, anything a document
   asserts about itself. Its yield is not proportional to effort — it is
   proportional to how long the first number went unchallenged.

**The crossover is measurable, so measure it.** Every pass, count two numbers: new
findings, and findings caused by the previous pass's own fixes. When the second
overtakes the first, the axis is exhausted — **rotate it, don't push harder.** Both
counts go in the ledger; an audit that reports only "found N" cannot see its own
exhaustion.

### 3. What can't be fixed now becomes a ratchet, never a TODO

A **ratchet** is a *named, counted set that may only shrink, printed on every
run*.

The carry-over ledger ([`templates/carryover.md`](../templates/carryover.md)) is
the pipeline's ratchet, and it only works if its count is **printed at every gate
beside the verdict**:

```
GATE 6 tests: PASS — full suite green (247 tests)
  carry-over: 4 open (was 6) · unresolved: 0 · audit findings deferred: 2
  abstained: 1 (1 cannot-verify) · unlooked: 2 dormant · holds: 1 (container: pg-test, this run)
```

The difference from a TODO is not bookkeeping. A TODO is invisible until somebody
opens the file. A ratchet sits next to the word `PASS` on every single run, so
**"green" never reads as "verified"** — it reads as *"green, and here is exactly
what was not looked at."* A ratchet that grew needs a sentence in the run log
explaining why; a ratchet nobody prints is a TODO with a better name.

## When this runs

- **Stage 10, before the coverage table.** Acceptance reads the REQ list; the
  ladder walk is what can add to it. Absences found here become new REQ rows with
  their checks, and *then* the table is written — otherwise acceptance closes green
  over a gap that was never a row.
- **Per module in the program loop** ([`decomposition.md`](decomposition.md)) — one
  brick's ladder, at that brick's acceptance. Cross-module contracts are audited at
  the seam that owns them, not twice.
- **As the whole task**, when the operator's request *is* an audit. Then stages 3–5
  produce findings and fixes rather than a feature, and the exit criterion above is
  the stage-10 gate.
- **Never as an eighth "look again" pass.** If the last two passes found mostly
  self-inflicted findings, the answer is rule 2, not another pass.

Once both axes are exhausted, the next finding of a known class should be caught by
a script — and if it cannot be, **that is the finding: write the check.**

## Rationalizations

| Excuse | Reality |
|---|---|
| "The gates all passed, so it's complete" | Gates compare. Nothing that was never written appears on either side of a comparison. |
| "One more careful pass will catch it" | Measured: by pass six the passes were mostly fixing their own last pass. Rotate the axis. |
| "I'll audit top-down, the surface is where users are" | A surface built on an absent contract wastes the whole pass. Bottom-up, that absence is finding #1. |
| "The check is green, that's evidence" | Only if you have seen it red. An unproven check is a decoration that reports success. |
| "It's a small gap, I'll note it in the ledger" | Second occurrence of a class → it goes in a script. The ledger is for what cannot be automated, not what nobody automated. |
| "Findings grouped by file are easier to fix" | And impossible to learn from. Group by seam; the seam names which layer of your process leaks. |
| "The ledger has it, we won't forget" | Only if it is printed beside every verdict. Unprinted, it is a TODO, and TODOs are invisible by construction. |
| "This is out of scope for the audit" | Then it is a carry-over row with a home, right now. An audit that silently declines findings is worse than none. |
| "The UX linter is green, the frames are fine" | It proved the links exist, are named right and aren't stale. It cannot read the picture. A frame that promises a feature nobody built passes every lint there is. |
| "The frame is wrong, I'll just redraw it" | Editing a shared design file is outward, and the spec is the contract. Say which document you are moving and get the go. |
| "I couldn't open the recorded file, so I made a new one" | That is the duplicate, and it hides a permissions problem a new file does not fix. Unreachable means stop and ask. |
