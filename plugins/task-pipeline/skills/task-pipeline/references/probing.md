# Probing — how a check is proven before it is trusted

The authoring doctrine for **probes**: planting a defect, watching the guard
refuse it, and keeping that proof alive after the release that ships it. It
lived inside [`gates.md`](gates.md) until 2026-08-31 and moved here whole —
one home, routed from the gate doctrine it proves. The law it serves is
[`audit.md`](audit.md)'s exit criterion: **a green from a check nobody has
watched fail is not evidence.**

## Contents

- Probing — plant, run, restore
- A probe rots, and every way it rots reports green
- The neighbour probe — plant the evidence outside the subject
- A green probe is evidence only if the mutation is known to have landed
- Rationalizations

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
And **a check keyed to one spelling of a rule is *The neighbour probe*'s class, above**: it
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
because the identifier still appears in an import. That is case 2 above and it is the same class as
[`gates.md`](gates.md) → *A ratchet's matcher is itself a check, and it needs a near-miss*, one level down.

## Rationalizations

| Excuse | Reality |
|---|---|
| "The check is green, that's evidence" | Only if you have seen it red. An unproven check is a decoration that reports success. |
| "I probed it when I wrote it" | A probe proves the check works today. The thing it guards is the thing that moves it — re-read the anchor on every release that touches the subject. |
| "The plant obviously landed, the file is smaller" | `replace` matching nothing returns the string unchanged and raises nothing. Assert the mutation landed, in the same breath as planting it. |
| "Some guard fired, so the probe passed" | A plant that trips some *other* check has proved that other check works. The message that fired must belong to the guard under test, named up front. |
