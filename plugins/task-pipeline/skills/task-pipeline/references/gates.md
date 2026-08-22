# Gates — the three axes, and how to build one that cannot lie

**One job: turn a rule into something that can say no.** [`audit.md`](audit.md)
says a class seen twice *belongs in a script*; this file is where that script comes
from — how it is written, where it runs, how it is armed, how it is proven, and
what you must know **before** you quote its green as evidence.

**Boundary, so this file does not become a second source.** The *law* lives
elsewhere and is not restated here:

| The law | Lives in | This file adds |
|---|---|---|
| A check must be watched failing before it is trusted | [`audit.md`](audit.md) *Exit criterion*, [`learned.md`](learned.md) 4–5 | the executable recipe |
| Ratchet, never TODO | [`audit.md`](audit.md) §3, [`learned.md`](learned.md) 7 | floor variables, and where the count is printed |
| A gate's exit code is part of its output | [`learned.md`](learned.md) 11 | where the verdict block goes |
| A checker with false positives is worse than none | [`learned.md`](learned.md) 10 | how to measure before shipping |
| A generator seeds green | [`learned.md`](learned.md) 9 | progressive arming |
| A class that repeats twice becomes a gate | [`audit.md`](audit.md) §1 | the six-step recipe |

---

## Contents

- Axis A — the stage gate type
- The judgment gate — a ruling is not a measurement
- Axis B — the enforcement mechanism
- Axis C — degrees of freedom
- Progressive arming
- Before you run a check
- False success — when a mechanism reports a win it never checked
- Anatomy of a project gate
- Writing the check itself
- Probing — plant, run, restore
- A probe rots, and every way it rots reports green
- A ratchet prices the rule, not the exception
- Run the whole suite locally before you push the tag
- The neighbour probe — plant the evidence outside the subject
- A ratchet's matcher is itself a check, and it needs a near-miss
- A green probe is evidence only if the mutation is known to have landed
- The false-positive budget
- Ratchets
- The result is the goal; the check is how you know
- Disclosures — counted like a ratchet, and deliberately not monotone
- Where a gate runs
- Adding a check to an existing gate
- Rationalizations
- Cross-cutting, at every stage

## Axis A — the stage gate type

From [`../pipeline.schema.json`](../pipeline.schema.json), one per stage:

| Type | Meaning | Failure to respect it |
|---|---|---|
| `auto` | the orchestrator verifies the `check` itself, pass/fail, and stops on fail | advancing on an unverified check |
| `judgment` | somebody **rules** on it, because no complete deterministic check exists; the gate names its `judge` | recording the ruling in the slot reserved for what a machine established |
| `manual` | wait for the operator's **explicit** go | treating an auto verification as the approval |

**An auto gate never substitutes for a required manual approval.** A green table is
not the operator confirming it is what they asked for, and no amount of checking
makes it one. Which stages are manual is the **operator's** decision, recorded in
their `pipeline.json`; the framework fixes no stage count and no gate assignment.

**That sentence is about the pipeline's SHAPE, and nothing else.** It says a project
chooses how many stages it runs and which of them wait for a person. It does not say the
criteria inside a gate are per-run negotiable: where a project keeps stage 10 manual, what
that gate asks is [`acceptance.md`](acceptance.md)'s policy **`AP-1`**, which is versioned
and has an owner. The two rules stood side by side unscoped until 2026-08-20 (`B-091`), and
a reader could take either as the whole rule — *the framework fixes nothing* and *the ladder
is fixed* are both in the shipped doctrine, which is how an acceptance standard becomes
something every run re-argues.

## The judgment gate — a ruling is not a measurement

Two types were not enough, and the gap was not cosmetic. A reviewer's ruling, a check that
the scenarios are coherent, a verdict that a mockup is good — none has a complete
deterministic check, and all three rode in `auto`, **indistinguishable from an exit code**.
A coverage table then cannot tell a measured row from an opinion, and the role-agent
programme multiplies the problem: `reviewer`, `ux`, `ui` and `market-analyst` produce
judgement by design.

`auto` now means only what a machine established.

**The precedent already existed in miniature, and this generalises it rather than
inventing it.** [`templates/verification.md`](../templates/verification.md) already turns a
coverage verdict of `review` into `none` in the `Auto` column — because that column records
what a machine established, and a review is not that. That rule, applied to one column, is
the `judgment` type in one instance.

Three obligations, and the third is the one that bites:

1. **It names its `judge`** — a role, an agent, a person. The schema refuses the gate
   without one. A ruling with no author cannot be weighed for independence, and
   independence is not a property of *having* a reviewer: this pipeline's own `R-005` reader
   shares a model, instructions and repository with the author it reviews, differing only in
   context. That is a real second reading and it is **not** a deterministic runner, a
   contract at another boundary, or an external system. Naming the judge is what makes the
   difference visible instead of assumed.
2. **The verdict is recorded as judgement**, in the artifact that quotes it — never
   promoted to a pass in a column that means *a machine established this*.
3. **It may not stand in for a `manual` gate.** A judgement can be rendered by an agent; an
   *authorisation* cannot. Anything outward, irreversible, or costing money stays `manual`
   however confident the judge.

**Which of this pipeline's own gates are judgement is deliberately not decided here.**
Gate assignment is the operator's call and the framework fixes none — so shipping a
reclassified stage list would contradict the sentence above it. The type exists; the
project chooses where it applies.

| Rationalization | Why it is wrong |
|---|---|
| *"The reviewer approved it, so the gate passed."* | It did — as a judgement. Type it as one, or the table claims a machine agreed |
| *"A second agent checked it, so it is independent."* | Independence is a different **evidence path**, not a second reader. Name the judge and the difference is visible |
| *"There is no check for this, so it has to be `manual`."* | `manual` waits for a person's authority. `judgment` records a ruling. Collapsing them puts a human in the loop for everything that is merely hard to measure, which is how an operator learns to route around the pipeline |

## Axis B — the enforcement mechanism

Where a rule actually lives. A rule climbs this ladder; it does not start at the top.

| Rung | Mechanism | Costs | Promote when |
|---|---|---|---|
| 1 | **Doctrine line** in a reference file | reading attention | it was violated once |
| 2 | **Review question** at a named gate | a person's time, every run | no check can decide it — and say *why*, in one line |
| 3 | **Script check** in the project's gate | writing it once | the class has occurred **twice** |
| 4 | **CI step** | minutes per push | it must hold for people who never run it locally |
| 5 | **Hook** ([`hooks.md`](hooks.md)) | latency on every tool call | the failure is cheaper to prevent than to detect, and the target is an edit an agent is making now |

A rule may sit on several rungs. What it may never do is **pretend** to be on a
higher one: a doctrine line that reads as if it were enforced is the same failure as
a gate that prints `FAIL` and exits `0` — both report a world they are not looking
at.

**Rung 2 is where honesty is bought.** "No check can decide this" is a legitimate,
common answer. Written down with its reason, it is a finding somebody can later
disprove. Left unwritten, it is indistinguishable from an omission.

---

## Axis C — degrees of freedom

Axis B says how hard a rule bites. This one says how much latitude the *instruction*
leaves, and it is a separate choice: a low-freedom instruction guarded by nothing is
a wish, and a high-freedom instruction behind a blocking hook is a bottleneck.

Match the level to how **fragile** the step is, not to how important it feels:

| Level | Shape | Use when | Example here |
|---|---|---|---|
| **high** | prose direction, no prescribed sequence | many routes reach a good answer and context decides | stage 2 — the design conversation |
| **medium** | a named order with room inside each step | the sequence is fixed, the content is judgement | stage 0 — two phases, adaptive questions |
| **low** | run exactly this, in this order, no variation | the operation is fragile, irreversible, or must be identical every time | stage 5's TDD order · stage 7's deploy · stage 9's matrix walk |

The picture worth keeping is an **open field versus a narrow bridge**. In the field,
say where to go and let the agent find the route. On the bridge there is one safe way
across, and the guardrails are the instruction.

**Over-constraining costs as much as under-constraining and is harder to see.** A
high-freedom step written as low freedom produces an agent that follows the letter
past the point where the letter stopped fitting — and reports success, because it did
what it was told. Where a step is genuinely open, say so out loud; that sentence is
what stops the next reader from hardening it.

Every stage in [`stages.md`](stages.md) declares its level and its reason, on the
line under its heading.

## Progressive arming

A gate seeded into a young project has almost nothing to check yet, and a gate that
starts red teaches everyone on day one that it is noise ([`learned.md`](learned.md)
rule 9). So each section reports one of four states and only one of them fails:

| State | Means | Fails? |
|---|---|---|
| `ok` | the check ran and passed | no |
| `dormant: … — no <artefact> yet` | the input does not exist yet | no |
| `skip: … — <why>` | the input exists, the check could not run here | no |
| `ERR` | the check ran and found something | **yes** |

`dormant` and `skip` are **printed, never silent** — that is the whole reason they do
not quietly become permanent.

They also force one more obligation on the verdict line: it must report **what the
run actually looked at**. Every section dormant is indistinguishable from a gate
blind to the shape in front of it, and exit 0 alone cannot tell those two apart.

## Before you run a check

Four preconditions. Skipping any of them turns a run into a claim.

1. **The base is green** — or its known-red baseline is *recorded*. A new guard
   added to an already-red base passes for the wrong reason and proves nothing.
2. **The check has been probed.** Green from a check nobody has watched fail is
   worth nothing. If you did not plant the defect, you do not know what the green
   means.
3. **You have read its scope header** and know what it does **not** cover. A gate
   is evidence for exactly the surface it walks; quoting it beyond that is how
   "the gate is green" becomes a false statement made in good faith.
4. **You have read the ratchet floors.** A pass with a floor that was quietly
   raised is a pass over the thing the floor was hiding.

**And one rule for the moment after.** A new check that goes red on the day it is
written invites one reflex — *the check must be wrong, relax it*. Sometimes the
check **is** wrong, **and the red is still the finding.** A guard asserted two
constants describing "the price of one unit per year" were equal; they belong to
two different products, so the premise was wrong and the obvious move was to
delete the assertion. Reading further showed the disagreement was **visible to
customers**: both products still sell from one page, and the note under the volume
table promised a discount computed from the header's price while the table's own
numbers gave roughly half of it. Nothing miscalculated — only the claim on the page
was false.

So: **separate the premise from the observation before touching either.** Ask what
the check *saw*, not whether it was entitled to look. Relax or delete the assertion
only after the thing it surfaced has its own record — otherwise the finding leaves
with the check that found it, and nothing remembers it was ever seen.

---

## False success — when a mechanism reports a win it never checked

The four preconditions above protect a *check*. The same law binds an **action**:

> **An actor's own reply is not evidence about the world. Confirm an effect by
> re-reading the state it changed.**

A failure is loud and gets fixed on the pass that finds it. A false success is
silent and **removes the reason to look**, which is why every shape below survived
at least one release in this repository:

| Shape | What reported success | What was actually true |
|---|---|---|
| Fail-open hook | any exit code but `2` is non-blocking, so a **crashed** guard *allows* the action | the guard never ran |
| Teardown by reply | a cancel accepted an id that was never scheduled and returned success | the job was still armed |
| Presence instead of absence | a counter asserted the new number was present, not that the old one was gone | four surfaces still printed the old number, green for three releases |
| Half-applied batch | a batch of edits reported done while one edit never applied (R-002) | the file was unchanged |
| Silence read as a pass | a section with no input printed nothing, and the caller counted it as checked | nothing was looked at |
| **Read through a pipe** | the caller read the **formatter's** exit code, not the gate's | `npm test 2>&1 \| tee ../test.log` under `bash -e` without `pipefail` concluded `success` over its own `# fail 55`; `check-docs.sh \| grep FAIL \| tail && git commit` committed over a `FAIL` printed to the author's screen |
| **An absence with no subject** | an assertion that a thing is gone, about a thing that exists nowhere | a viewport test asserting a column leaves the tree at 1279px passed at **every** width — the column had been deleted from the product months earlier |

**The test.** For any mechanism you are about to trust, ask:
*what does it print when it did not look?* If that is indistinguishable from what
it prints when it looked and found nothing wrong, it is not evidence — give it a distinct `dormant`
or `skip` state (→ *Progressive arming*), or verify the effect independently.

Four rules follow. Elsewhere in this bundle they are **cited, never restated**:

1. **Verify by re-reading, not by the reply.** After a teardown, cancel, delete,
   disable, publish or migrate: query the authoritative state and assert the item's
   new condition.
2. **Assert the absence of the old, not the presence of the new.** A check that only
   proves the new value exists stays green while the old one is still shipping.
3. **Read a gate's own exit code, never a pipeline's.** `set -o pipefail`, or
   `${PIPESTATUS[0]}`, or do not pipe. GitHub Actions runs `run:` under `bash -e`
   **without** `pipefail`, so `gate | tee` reports `tee`. This is the least visible
   entry in the table because the command reads as diligence: `check.sh | grep FAIL`
   looks like someone being careful, and it is the shape that reports success while
   printing failure to the screen of the person who wrote it.
4. **An absence assertion needs a subject that exists somewhere.** Before pinning
   "X must not appear here", prove X appears *somewhere* — otherwise the assertion is
   true for a reason unrelated to what it claims, and the complement of *watch the
   green fail against a planted defect* is what catches it: that rule finds a check
   that **cannot fail**, this one finds a check that **cannot succeed meaningfully**.
   Both are invisible to every mechanical signal — the test is green, its name is
   accurate, its code reads correctly.

---

## Anatomy of a project gate

Ten properties. Each one is here because its absence has shipped.

| Property | Rule | The failure it prevents |
|---|---|---|
| **Exit code** | non-zero on **any** failure | a gate that appended a check *after* its verdict block printed `FAIL` and returned `0`; CI was green over it for an unknown period |
| **Verdict last** | nothing may run after the verdict block | the same failure, from the other end |
| **Scope header** | states what the gate does **not** cover | a green quoted as proof of a surface nobody walked |
| **Portability** | POSIX + bash 3.2: no `grep -P`, no `sed -i`, no `readarray` | BSD `sed -i` needs an argument GNU refuses, and `0,/re/` does not exist there — it silently edits nothing and the check reads as a guard that failed to fire |
| **Ratchet floors** | `<NAME>_FLOOR` variables at the top; counts printed beside `OK` | a backlog that grows back without anyone explaining why |
| **Skips are printed** | a check that could not run says so | a submodule not checked out silently removing coverage |
| **Progressive arming** | a section with no input artefact prints `dormant: … — no <artefact> yet` and does **not** fail | a freshly seeded project starting red, which teaches everyone on day one that the gate is noise |
| **Computed, never restated** | derive every count at check time | two documents quoting a total that went stale |
| **Both directions** | any two-layer mapping is checked each way | four fully-specified entities with no schema anywhere — found only by the direction that felt redundant |
| **Named location** | every error prints file **and** line | a finding nobody can act on |

Shape:

```bash
#!/usr/bin/env bash
# check-docs.sh — the documentation gate for <project>.
# SCOPE: walks <what>. Does NOT check <what>.
# Portable to macOS bash 3.2: no grep -P, no sed -i, no readarray.
set -u
FAIL=0
PROP_FLOOR=${PROP_FLOOR:-1}          # ratchet: raising it is a decision

# ---------- 1. <name> ----------
...                                   # ok: / ERR: / skip: / dormant:

# ---------- VERDICT — nothing runs after this block ----------
if [ "$FAIL" -ne 0 ]; then echo "FAIL: <gate>"; exit 1; fi
echo "OK: <gate> — backlog: $BACKLOG (floor $PROP_FLOOR) · registers: $DECS decisions · $OQS open"
exit 0
```

---

## Writing the check itself

- **Pick the unit and say what it costs.** A check that scopes to a table *row*
  will let one marker in that row exempt everything else in it. That is a real
  blind spot; measured and accepted beats unmeasured and denied, so write it in the
  comment.
- **Prefer a deterministic rule to a heuristic.** A parity-based check for
  unbalanced markup produced six false positives out of six on a real corpus and
  was discarded. If the rule cannot be stated exactly, that is information.
- **Never infer from strings the environment also produces.** Matching `"claude"`
  in a process command line matched the throwaway shell of every tool call.
- **Compute the count you print.** A number restated in prose is a number that will
  be wrong; derive it from the source at check time so the two cannot disagree.
- **Normalise the corpus's own formatting before you match, and say which unit you
  chose.** A predicate written against the sentence you have in mind meets the sentence
  as the file actually stores it: wrapped at some column, with emphasis, inside a table
  cell. Three separate guards in this bundle were defeated that way and none of them by
  its content —

  | What defeated it | The guard | The fix |
  |---|---|---|
  | a citation wrapped across two lines | the section-citation check | normalise whitespace, match over the paragraph |
  | a marker split by the ~80-column wrap | the distrust-marker check | same |
  | `**five run stamps**` — bold inside the phrase | the cold-retirement check | strip emphasis too |

  Each was silent, which is the expensive part: the guard reported green over a file it
  had never read. Pick the unit deliberately — **line, paragraph, or whole file** — write
  down which, and probe the shape the corpus actually contains rather than the shape you
  typed into the regex. And plant the defect **in the file that defines the thing**, not
  in the most convenient one: a probe against a surface with none of the formatting is a
  probe that cannot fail for this reason.

---

## Probing — plant, run, restore

The law is [`audit.md`](audit.md)'s exit criterion. The procedure is this, and it is
not optional for a check you intend to trust:

```bash
cp -R . /tmp/probe && cd /tmp/probe
python3 - <<'PY'                       # plant IN PYTHON, never sed -i
p = "docs/DECISIONS.md"
s = open(p).read().replace("DEC-0001", "DEC-9999", 1)
open(p, "w").write(s)
PY
bash scripts/check-docs.sh; echo "planted -> exit=$?"   # MUST be non-zero
cd - && bash scripts/check-docs.sh; echo "clean -> exit=$?"  # MUST be 0
```

**Assert on `$?`, not on a `FAIL` line in the output.** A line on stdout is a
decoration; the exit code is what CI reads.

**Doubt the probe before you doubt the check.** On the project this comes from,
**four of five** silent probes were the probe's fault: one added a *definition*
where the check looks for an unresolved *reference*; one edited a string whose
whitespace did not match; one hit the first prose mention instead of the table row;
one flipped a row whose cell was already empty, so nothing was planted. A silent
check is a claim about two things, and the probe is the one to doubt first — prove
your edit landed in the text the check actually parses.

**Three assertions, and the third is the one hand-rolled probes keep missing.** A
plant that trips some *other* check has proved that other check works. Three probes
in one day passed that way: one removed 1 of 3 identical lines and left the shape
intact; one decremented a number inside an **already-released** section; one deleted
the shouted spelling of a phrase and left the lowercase one. Each landed somewhere
real and demonstrated nothing about the guard it was written for. So:

1. **the substitution landed** — `replace` matching nothing returns the string
   unchanged and raises nothing;
2. **the exit code is non-zero** — not a `FAIL` line on stdout;
3. **the message that fired belongs to the guard under test** — named up front, not
   recognised afterwards.

`test/probe.py` does all three (`npm run test:probe` self-tests the harness, including
its own failure branches, because a harness whose failure path has never executed is
the thing it exists to stop). Declare the plant as `Plant(label, path, old, new,
expect=<the guard's own words>)` rather than hand-rolling a fourth copy of the loop.

**Record the probe.** One line per section, in the change that ships the check.
Otherwise the next reader has to redo it to know whether it was ever done.

---

## A probe rots, and every way it rots reports green

The three assertions above prove a probe works **today**. They say nothing about the
day after, and a probe is uniquely exposed: the thing it guards is the thing that moves
it. Four rotted in one release on 2026-08-22, and none of them failed loudly — two
reported `caught`, two reported nothing at all.

**1. The anchor is a literal the guarded thing moves.** A probe pinned to *"the bundle
is N reference files"* stops landing the day a reference file is added — on the release
that changes the very number it guards. Same for a version, a count word, a phrase a
release rewrites. **Derive the anchor**: read whatever the text currently says and make
*that* wrong. A probe that computes `wrong = stated - 1` never needs maintaining.

**2. The precondition is inherited from the tree rather than created.** This is the
subtle one, because it is triggered by the system working correctly. A probe that
narrows a declared gap to expose *releases after the newest run stamp* has nothing to
expose the moment a release writes an honest stamp — the newest release is now the
newest stamp. A probe requiring an `## Unreleased` section has none the moment a release
absorbs it. **Both landed. Both proved nothing.** A probe must construct the state it
needs: remove the stamp, write the section, then plant the defect.

**3. The document quotes the form the probe removes.** Covered as
[`documentation.md`](documentation.md) canon 2's second half, and it belongs here too
because the probe is where it surfaces: prose describing the wrong shape *with real
values in it* is a second instance of the shape. The probe deletes the real one, the
narrative still matches, the guard is silent.

**How to see it before CI does.** Ask one question per probe: *what does this probe
LOOK FOR, and who is allowed to change it?* Where the answer is "the thing it guards",
it is rotting already. A repository-wide sweep is one grep — a two-digit literal inside
a needle, an `assert` or a `replace` — and the triage is: the number a probe **writes**
is correct, the number it **looks for** is the defect.

## A ratchet prices the rule, not the exception

A floor that counts assertions is a floor that can be lowered by improving the code, if
the assertions are attached to the wrong things.

Measured: a coverage check called `check()` once per *exception* — a silent value, a kept
value, a promise — and simply `continue`d on the ordinary case. Collapsing four kept
values, **the remediation the requirement names first**, therefore dropped the count by
four against its floor and turned the suite red on the stricter answer. The only way
through was lowering a ratchet whose own reason says a falling count is how a deleted
requirement hides — so a legitimate lowering and the failure the floor exists to catch
became indistinguishable.

**One assertion per subject examined, whatever its verdict.** The ordinary case asserts
too. Then the floor is a function of how large the corpus is, not of how many exceptions
it happens to contain, and doing the right thing can never lower it.

**And measure the floor after the last edit, not before it.** Read the count, keep
editing, restate the count you read — every floor set that way sits below the true one,
and a floor is a minimum, so nothing ever says so. Where the gate cannot enforce
equality — it must not, or the ratchet stops allowing growth — it can still **print the
gap**: `floor 4026, ran 4027: 1 check is not pinned` turns a silent difference into a
visible one for the cost of one line.

## Run the whole suite locally before you push the tag

Not a preference: an arithmetic. A release workflow that runs the full suite takes
twenty-five to forty minutes per round, and it reports one failure at a time. The same
suite on the machine that wrote the change takes twelve and reports all of them at once.

On 2026-08-22 one tag took **five CI rounds** — a stray key in a `run:` block, a missing
run stamp, a stamp cap, and then four rotted probes — where a single local `test:all`
before the first push would have found the last four together. Every refusal was correct.
The cost was entirely in asking the wrong machine.

**A green local suite is not evidence until you know which checks LOOKED.** This
instruction failed on its own release: the local run was green, CI was not, and the
difference was a precondition asking `os.path.isdir(".git")` — false in a submodule
checkout, where `.git` is a *file* holding a gitdir pointer. One check switched itself
off in the only checkout the family is developed in, silently, and had been doing so
since it was written. The repository had recorded that class **twice** already, in two
other files, and this instance was missed both times: knowing a class is not sweeping
it. Two consequences, and the second is the general one:

- ask `exists`, never `isdir`, of anything named `.git`;
- **a precondition that fails must disclose, not skip.** Where a check cannot run, it
  appends to the unlooked list and the run prints it. A check guarded by a bare `and`
  evaporates without a line of output, which is the one thing this file's own canon
  forbids — and it evaporates most reliably in the environment its authors use.

The rule has a second half, and it is the one that makes it stick: **a tag is the only
thing that runs some checks.** A branch push cannot see a tag that does not exist yet, so
the tag-ancestry check, the version-sync check and the run-stamp check have no earlier
opportunity to fire. Locally, run them the way the release does — against the tree you are
about to tag, with the suite the release claims.

## The neighbour probe — plant the evidence outside the subject

A probe proves a guard rejects **the phrasing its author had in mind**. That is less than
it looks, and the gap has one shape: **a check answered by text that is not its subject.**

Measured on one project in one session, six times, each found by a reader planting a
defect and watching `PASS`:

| The check's subject | The text that answered it instead |
|---|---|
| stage 2 names the loop's arming | *"it **arms** the UX track"*, present since an earlier release |
| the section states the authorization floor | the same phrase in a Rationalizations row, and in a section written twenty-nine releases before |
| the run stamps have a cap | the **standing instructions'** `max 10`, in the same table cell — and, once the check was narrowed past it, the same cap moved to the other side of the `·` |
| a section read in full stays capped | rows under **one** heading, while a second heading in the same file held forty more |

Every one of those guards had a probe. Every probe fired. The probes and the guards were
written in the same hour from the same reading, so they shared the same blind spot.

**So a guard that reads a scoped span owes a second probe, and it plants in two places at
once:**

1. **break the subject** — remove the thing the guard is about;
2. **plant the guard's own evidence next door** — in a sibling section, an adjacent table
   cell, a rationalizations row, the other side of a separator;
3. require the guard to **still fail**.

A guard that passes step 3 is reading its subject. A guard that goes green is reading the
neighbourhood, and the ordinary probe cannot tell the difference — which is why this one
is separate rather than a stricter version of it.

**Step 2 means the literal the predicate matches *today*, read out of the guard.** The
first three neighbour probes written against this section got that wrong on their first
run: one planted the needles of two **retired** predicates, which proves the guards that
used to exist were neighbour-answerable and says nothing about the one that does. A
neighbour probe keyed to a needle the guard no longer reads is the same defect it was
written to catch, one level up.

**A probe that only deletes is not a neighbour probe.** It may still be a correct probe —
but if it relies on copies that already sit next door, it must **assert they are there**.
Otherwise a later edit removes them and the probe quietly becomes a delete-only test that
still passes, having stopped testing the thing it is named for.

**Positional narrowing is not scoping.** Three of the six were "fixed" by cutting the
search down to a row, then to everything after a phrase, and fell each time to text that
was still inside the cut. Scope by *what the span is about*: split to the cell, then to
the item, then match on flattened text so an emphasis marker cannot hide the boundary.

**And state the span in the guard.** One line above the predicate — *what it reads, and
where that ends*. It costs nothing and it is the only part of a check a later reader can
disagree with before the defect arrives.

## A ratchet's matcher is itself a check, and it needs a near-miss

Reported from another project through `retro.publish`, and it is the neighbour probe's
own class arrived at independently — which is the strongest evidence either has.

A run built a ratchet to hold a coverage debt: a list of units with no test, a guard that
fails when the list grows, a count printed at the gate. Exactly the shape
[`audit.md`](audit.md) asks for instead of a deferred TODO. The guard decided whether a
unit was covered by asking whether its identifier appeared **anywhere** in the test
corpus. The identifiers were path-like and many were prefixes of longer ones, so every
unit that happened to be the parent of another was credited with its child's coverage.

**A ratchet whose matcher is looser than its subject shrinks itself.** It reports progress
for work nobody did, and because a ratchet is trusted precisely so that nobody re-derives
it, the error compounds for as long as the ratchet exists.

Both existing rules were satisfied. The ratchet was printed. The guard had been seen going
red when the list grew. Neither asks whether the matcher can tell its subject from a near
neighbour, and that is the only question that would have caught it.

**So before a ratchet is kept, feed its matcher a near-miss it must reject** — the prefix,
the parent, the same name in a comment or an import, the longer extension. Seeing a guard
go red on a real change proves it **reacts**; seeing it stay green on a look-alike proves
it **discriminates**. Only the second makes its number worth trusting.

**And when a matcher is corrected, re-derive the whole ratchet and print both numbers with
the reason.** In the reporting project the corrected count was *identical* to the old one
and the composition was not: rows credited falsely came back in as rows genuinely paid off
went out. A single number with no delta reads as a run where nothing happened.

## A green probe is evidence only if the mutation is known to have landed

Also reported from another project, three times in one day, each caught only because the
result was too good:

1. a scripted substitution missed on indentation — the file was unchanged and the probe
   measured nothing;
2. an assertion written against a bare identifier kept matching the **import line** after
   the field it guarded was deleted;
3. a file-extension alternation matched the longer extension as though it were the
   shorter, reporting nine live files as missing.

In all three the observable was identical to success. *"See it fail once"* has an unstated
precondition — **that the thing you changed is the thing the check reads** — and a planted
defect that did not land produces the same green as a check that cannot fail.

**So a probe that mutates an existing file asserts its plant landed, in the same breath as
planting it.** A probe that writes a whole file has no such question: the file exists or
the command failed. This repository measured itself while writing this section and got the
number wrong three times. A hand-rolled classifier said *206 of 206 already carry it*.
The guard written from the rule said **22 did not** — and was itself too narrow, matching
one spelling of the assertion, so six probes that already had it in lower case were
called defective. A sweep then "fixed" those six and **corrupted five**, splitting live
statements. The true figure was **16**, and it took the guard, a compile check and a
restore from git to find it.

Two things are worth keeping from that. **The check corrected the measurement that
motivated it** — which is the argument for writing checks rather than counting by hand.
And **a check keyed to one spelling of a rule is the class two sections above**: it
reported as defective the probes that obeyed the rule in different words. **Every**
mutating probe carries the assertion now — the figure is deliberately not
written here. A first draft said *201*, which was true of the branch point and false in
the same commit, because the twelve probes added for this release are themselves mutating
probes. The guard computes it; a number in prose beside a check that can count is the
class this bundle calls restating instead of computing. Probes that write a whole file
need none: the file exists or the command
failed.

**Prefer an assertion that names the construct over one that names a substring of it.** A
guard written against a bare identifier survives the deletion of everything it guarded,
because the identifier still appears in an import. That is case 2 above and it is the same
class as the section before this one, one level down.

## The false-positive budget

Run a new heuristic over the **real corpus** before shipping it and count the false
positives. Zero, or replace the heuristic with a deterministic rule.

The budget is not perfectionism. A gate that cries wolf is switched off by the
third person who hits it, and after that it protects nothing while still appearing
in the pipeline as a control. A noisy check is worse than no check, because it also
consumes the credibility of the checks beside it.

---

## Ratchets

A **ratchet** is a named, counted set that may only shrink, printed on every run.

- Its floor is a **variable at the top of the script**, so raising it is a visible
  edit and a decision.
- Its count is printed **beside the verdict**, so `PASS` never reads as *verified*
  — it reads as *"green, and here is exactly what was not looked at"*.
- A ratchet that grew needs a sentence in the run log saying why.

```
GATE 9 docs: PASS — propagation backlog: 121 (was 162) · unmarked residue: 0
  abstained: 0 · unlooked: 4 (3 dormant · 1 skip — no submodules in this repo) · holds: 0
```

A ratchet nobody prints is a TODO with a better name.

## The result is the goal; the check is how you know

Everything else in this file pushes one way: prove more, assume less. Read alone it
has an obvious failure mode — a run that spends its afternoon proving a
one-character change and never ships the thing it was asked for. **The deliverable
is the working result, as described in the brief. A check is how the run knows it
has one. A check that is not buying that knowledge is not diligence; it is the run
optimising the wrong thing.**

**Scale the check to what breaking costs, and the project already computes that.**
The board ranks by `sev × blast` ([`backlog.md`](backlog.md)). The same two inputs
size the verification:

| What breaking costs | What the check has to be |
|---|---|
| an outward, irreversible or shared-state effect — deploy, publish, a lease, another agent's file | proven: watched failing against a planted defect, and re-read rather than trusted from the reply |
| a contract other code depends on | an executed test, named in the REQ row |
| behaviour a person will see | observed on the surface — a browser, the actual output — not inferred from a diff |
| a typo, a comment, a rename the compiler checks | the compiler, the suite already running, and nothing more |

**Four things that mean you have crossed over**, and each has cost this project a
run:

- **A third pass over the same axis finds mostly what the last pass's fixes broke.**
  The axis is exhausted — rotate it or stop ([`audit.md`](audit.md)).
- **The check is being widened after it went green**, with no failure in hand. A
  check widened by imagination is a check whose scope nobody has measured.
- **The evidence is being gathered for a claim nobody made.** If no REQ row and no
  gate criterion asks for it, it is not evidence — it is browsing.
- **The run is on its second measurement of the same number.** One measurement plus
  what it does not cover, stated, beats two measurements and no decision.

**This never licenses skipping a gate.** The gates are the floor, and the floor is
not proportionate to anything — a `manual` gate waits, `unknown` fails stage 10, and
a green nobody watched fail is not evidence at any blast radius. What is
proportionate is the work *above* the floor: how many axes, how many passes, how
much of the corpus. Cutting the floor to go faster is not speed; it is the failure
this whole file exists to prevent, arriving on schedule.

**Where it is recorded.** Stages 3 and 4 carry a `Cost:` line —
`<surfaces>/<guards>/<REQ> now, <…> at stage 2 — <proportionate | grown, and why>`.
*Grown, and why* is the honest answer often enough that it is written into the form.

## Disclosures — counted like a ratchet, and deliberately not monotone

A ratchet may only shrink. **Some numbers must not be**, and printing them under a
ratchet's discipline inverts the thing they measure.

**Abstention is the case that matters.** This bundle has eight vocabularies for declining
to claim — `partial`, `unknown`, `cannot verify from diff`, `review`, `dormant`, `skip`,
`recalled`, `ungated` — and until they were counted, none of them appeared beside a
verdict. So `PASS` read as *verified* rather than as *"green, and here is what nobody
claimed"*.

The obvious fix is a ratchet, and it is wrong. A count of abstentions that may only shrink
puts pressure on exactly one thing: **claiming more**. A run reaching `abstained: 0` is not
more careful; it is a run that stopped saying *I don't know*, which is the cheapest way to
make the number fall. Refusals and wrong answers are communicating vessels — squeeze one
column and it reappears in the other, silently, because a wrong claim looks like a claim.

So a **disclosure** is printed beside the verdict like a ratchet and carries the opposite
rule: **no floor, no direction, and a movement in either direction wants one sentence.**

The disclosures below are kept separate because they are different facts — the list is the count:

| Disclosure | Counts | Reading it |
|---|---|---|
| `abstained: N` | claims the run **declined to make** — `partial`, `unknown`, `cannot verify from diff` | a *choice*. Rising can mean the work got harder or the run got honest; falling can mean either the reverse |
| `unlooked: N` | checks that **did not look** — `dormant`, `skip` | a *state of the corpus*, not a decision. It falls as the project grows the inputs those checks need |
| `holds: N` | what the run left **running or lying about** — the eight classes in `references/residue.md` | a *state of the environment*, not of the corpus or of the run's claims. A legitimate 2 during a build beats a manufactured 0; only stage 10 requires it to reach zero or name an owner per item |

Three are deliberately **not** counted, and saying which is part of the disclosure:

- **`review`** — *no check can decide this* — is an abstention, and it is the one this
  section first listed and then forgot, which is exactly the failure it exists to catch.
  It stays out of `abstained` because it is not a claim the run declined: it is a rule
  that **declined to be mechanical**, recorded once at rung 2 with its reason (→ *Axis B*).
  Counted per run it would report the same standing number every time and say nothing
  about the run.
- **`recalled`** — a property of one claim, already carried in the ledger beside the
  command that would re-derive it.
- **`ungated`** — a property of the whole run, said once, in words.

A vocabulary that is named and then left out of every bucket is the one that goes
uncounted forever. So each gets its line, including the one that got missed here.

**What makes a disclosure honest rather than decorative** is the same thing that makes a
ratchet honest: it is *computed*, and it is printed whether or not anyone likes the
number. What makes it different is that **nobody may set a target for it.** A target on an
abstention count is an instruction to guess.

---

## Where a gate runs

| Place | Good at | Limit |
|---|---|---|
| **Local pre-commit** | fast feedback for the author | skippable, and skipped exactly when someone is in a hurry |
| **CI** | authoritative; holds for people who never run it locally | minutes late, and it checks out the repo in a shape the author's machine never has — rehearse that shape |
| **Hook** ([`hooks.md`](hooks.md)) | stops the edit *before* it happens | Claude Code only; a crashing hook **fails open** |
| **Stage gate** (this pipeline) | judgement, and the things only a person can answer | it is the run's own memory, not the repository's |

The four are not alternatives. The same rule can be a hook for the agent, a
pre-commit for the human and a CI step for the record — what it must never be is
*declared* in one place and *enforced* in none.

---

## Adding a check to an existing gate

1. **Name the class** — the shape, not the instance. "This id is undefined" is an
   instance; "an id referenced and never defined" is a class.
2. **Find the unit** the check will parse: a line, a table row, a paragraph, a
   file. Write down what that unit will miss.
3. **Write the predicate deterministically**, with the file and line in the error.
4. **Measure it** over the real corpus; zero false positives or rewrite it.
5. **Plant, run, restore** — both directions observed, and recorded.
6. **Wire its count into the verdict line**, with a floor if it cannot be zero yet.

Step 6 is the one that gets skipped, and it is the one that makes the check
survive: a number beside `OK` is read every run, and a check nobody sees the output
of is deleted in the next refactor by someone who assumed it was dead.

---

## Rationalizations

| Excuse | Reality |
|---|---|
| "The check is green, that's evidence" | Only if you have seen it red. An unproven check is a decoration that reports success. |
| "It printed FAIL, so it failed" | CI reads `$?`. A gate has shipped that printed `FAIL` and exited `0`, and nobody noticed for an unknown number of runs. |
| "I'll write the check later, the rule is documented" | Then it is on rung 1 and behaves like rung 3 in everyone's head. That gap is the whole failure. |
| "It's one occurrence, a note is enough" | It is. On the second, the note becomes a script — that is the rule, and the third occurrence is proof it was ignored. |
| "The heuristic mostly works" | Measure it. Six false positives out of six on a real corpus is what "mostly" felt like from inside. |
| "The gate would be red on day one, so I'll add it later" | Make the section dormant instead. Dormant is visible and green; "later" is neither. |
| "I raised the floor to get the build green" | Then say so in the log, in the same commit. A floor raised silently is a ratchet running backwards. |
| "A hook is overkill, CI catches it" | CI catches it after the edit, the commit and the push. If the point is to stop the edit, CI is the wrong rung — and if it is not, do not pay the latency. |

---

## Cross-cutting, at every stage

5. Cross-cutting, every stage: **when anything is settled — scope, a contract, a
   name, a policy, a vocabulary — run the Doc Loop
   (`references/documentation.md`) before the run moves on**: reserve the id,
   record it, resolve the question it answers, propagate by the matrix, commit
   with the ids. A decision that lives only in the spec dies with the spec, and one
   that lives only in the conversation was never made;
   **answer from the brief's autonomy section rather
   than asking again** — it was grilled precisely so you wouldn't have to;
   **anything deferred, dropped or left half-done goes into the carry-over ledger
   the moment it's said** — deferred out loud is forgotten; **never narrow the task
   silently** — the REQ list is frozen, adding is free, removing needs the
   operator's explicit agreement; **when a loop starts undoing an earlier pass —
   the same file edited twice for the same reason, a closed finding coming back, a
   third entry into one stage — stop and run the loop guard**
   (`references/loop-guard.md`): name the two shapes, escalate to the layer that
   owns the conflict, re-plan the check as an ordered list, then go through it one
   item at a time; **when a pass is *searching* rather than editing and starts
   finding mostly what the previous pass's own fixes broke, the axis is exhausted —
   rotate it, don't look harder** (`references/audit.md`); **every gate
   prints `holds: N` — what this run left running** across the eight classes
   (background shells, monitors, scheduled loops, coordination leases, worktrees,
   containers, scratch files, remote state), enumerated **by class and never by a
   single tool**, and stage 10 does not close while this run's residue is live and
   unaccounted (`references/residue.md`); and remember that a
   green from a check nobody has watched fail is not evidence; task
   tracker + conventional commits per host conventions; worktree isolation for the
   build, integrated back per the brief's branch policy before stage 7; honest
   degradation (never claim a failed/skipped step succeeded);
   outward/irreversible actions (deploy, publish, repo create, opening a PR,
   **editing a shared design file — frames are read by designers and stakeholders,
   so drawing in one is publishing — and above all *creating* one, which needs a
   named team and never happens while a recorded file resolves**) need explicit
   operator go — or a **specific** standing authorization recorded in the brief
   (named target + preconditions; a vague "do everything" is not one).

Moved out of `SKILL.md` on 2026-08-16 for the same budget reason as the
multi-repository block: these fire at any stage, so they belong with the gate
doctrine rather than inside step 5 of the run order.

