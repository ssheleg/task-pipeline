# Rules earned by failure

**One job: the mistakes that cost real time on a real project, each with the check that now catches
it.** Every rule here names the incident that produced it. A rule with no incident behind it is
somebody's preference, and it will be argued with at the worst moment.

They come from one 260-decision, 72-document specification built across four repositories with
several agents working at once. Nothing here is hypothetical.

**A rule belongs in the table only when it has a check.** Two of the lessons below could not be
mechanised and are kept out of it deliberately, as review questions — because a rule that pretends
to be enforced and is not is the same failure as a gate that prints `FAIL` and exits `0`.

---

## Contents

- The table — trigger · check · exit criterion
- The incidents, so the rules are not abstract
- The two that are not in the table, and why
- The one instruction that would have prevented the most
- Where these bind in the pipeline

## The table — trigger · check · exit criterion

| # | Rule | Trigger | The check | Exit criterion |
|---|---|---|---|---|
| 1 | **Change the axis when it stops paying** | any second review or audit pass | count new findings and self-inflicted ones separately | self-inflicted exceeds new → change the axis, do not "look again more carefully" |
| 2 | **Absence needs its own check** | any two-layer model — entity/table, screen/frame, task/module, requirement/test | compute the mapping in **both** directions | zero orphans each way, printed |
| 3 | **Verify closure against the artefact** | closing anything that names a design, a build or a file | open the artefact, not the document describing it | the artefact carries a marker naming what it was last verified against |
| 4 | **Probe the detector** | every new check, lint rule or assertion | plant the defect → run → assert non-zero; restore → assert zero | both directions observed once, and recorded |
| 5 | **Doubt the probe first** | a check that stays silent when it should fire | prove the planted defect exists in the text the check actually parses | the probe is shown to have changed what the check reads |
| 6 | **Sweep the class, not the finding** | any correction | grep the whole corpus for the same shape before closing | the class is gated, or named in the note so the next reader can finish it |
| 7 | **Ratchet, never TODO** | anything that cannot be fixed now | a named, counted set printed on every run | the number may only fall, and `OK` prints it beside itself |
| 8 | **Compute, never restate** | any count or cross-reference stated in prose | derive it from the source at check time | the stated number and the computed one are the same object |
| 9 | **A generator seeds green** | any scaffold, template or code generator | run the generated project's own checks inside the generator's tests | fresh output exits zero |
| 10 | **Measure a detector before trusting it** | a new heuristic check | run it over the real corpus and count false positives | zero false positives, or the heuristic is replaced by a deterministic rule |
| 11 | **A gate's exit code is part of its output** | any gate or CI step | run it against a planted defect and assert on `$?` | non-zero, not merely a `FAIL` line on stdout |
| 12 | **Tests create what they assert on** | any test touching shared state | run the suite against a cold, empty environment | the cold run and the warm run agree |
| 13 | **Local infrastructure does not fight the host** | any dev compose or service definition | assume the host already runs the defaults | services reachable with the host's own still running |
| 14 | **A document may not send a reader to something absent** | any instruction naming a command, file or install | resolve it | the gate fails when the target does not exist |
| 15 | **Identity before coordination** | any lease, lock, claim or run id | ask what two instances with the same identity would do, and make the tool answer it | two instances demonstrably get two identities |

---

## The incidents, so the rules are not abstract

**1 · Change the axis.** Seven passes of comparing documents against each other were instrumented.
Findings per pass: 12, 17, 13, 19 — and *caused by the previous pass*: 5, 9, 10, 4. By the sixth
pass the method was mostly repairing itself, because each pass edits the corpus the next one reads,
so the newest text is always the least reviewed. The fix is not more care; it is a different axis.

**2 · Absence.** Comparing documents found contradictions for weeks and never found that one
service had **no key store at all** — a decision made it the encryptor of every media object, the
other service's table had been modelled for weeks, and this one had no entity, no fields, no
rotation story. A contradiction needs two sides. Absence has one. The register that finally caught
it checks *entity → table* and *table → entity*, and **only the second direction found anything**:
four entities fully specified, cited by build tasks, with no schema anywhere.

**3 · Closure against the artefact.** Two gaps were marked **closed** while the design still
violated them — the closure had been verified by reading the specification, which had been fixed,
while the frames had not. Twice is a category, so every drawn screen now carries a marker naming the
newest decision its *frames* were checked against, and the linter fails when the prose cites
something newer.

**4 and 5 · Probes.** Every check written was exercised against a planted defect. **Five probes
failed before any check did:** one added a definition where the check looks for an unresolved
reference; one edited a string whose whitespace did not match; one hit the first prose mention
instead of the table row; one flipped a row whose producer cell was empty, so nothing was planted;
one counted matching lines and counted the check's own `INFO` line as a hit. Four times out of five
the probe was wrong, not the check.

**6 · Sweep the class.** A pass fixed four invented audit-action names in a table and stopped at the
rows it was looking at; two rows in the same table still said something else, found the next day.
The same shape recurred three times — a retired word corrected on one screen and left on two others,
a value fixed in a light frame and left in its dark twin, a stale retention window removed from
three documents' prose and surviving in a design.

**8 · Compute.** Two documents had to stop quoting totals after they went stale. The register that
replaced them computes its cross-reference column from lines the tables themselves carry, so the two
cannot disagree.

**9 · Seeds green.** A documentation gate added to a scaffold **failed on its own seeds** — it read
the template block and the allocation line as real identifiers. A project that starts red teaches
everyone on day one that the gate is noise.

**10 · Measure the detector.** A parity-based check for unbalanced markup produced **six false
positives out of six** on the real corpus. It was discarded for a deterministic rule. A gate that
cries wolf is removed by the third person who hits it.

**11 · Exit codes.** A repository's docs gate appended a check *after* its verdict block, so it
printed `FAIL` and returned `0`. CI had been green over it for an unknown period.

**12 · Cold runs.** An isolation test read whatever another test file had left in the database. Test
files run alphabetically and the one that creates that data runs later, so the test **passed on a
warm database and failed on a cold one** — which is what every new developer has.

**13 · Ports.** A dev compose published the default Postgres and Redis ports. The machine already
ran both, so the containers were silently shadowed: the tools connected to the host's services and
the migration failed with a permission error that named nothing about the collision.

**14 · Absent targets.** A repository's first instruction to every agent was to run a command that
was not installed, with no install line anywhere and no statement of what a session without it
actually is.

**15 · Identity.** The coordination plugin derived one run id **per checkout**. A hook has the
session id in its environment and a plain shell command does not, so the second session in a
checkout adopted the first one's identity: **an entire day of work was performed holding another
session's leases**, and the end-of-work check that had just been written offered to release
*theirs*. It was invisible from inside — `whoami` reported a lease and a run id, both plausible,
both somebody else's — and it surfaced only because a new command printed a lease nobody could
account for. This is the same failure as *the one instruction* below, and it is in the table rather
than only in that list because it **has** a check. Follow-on, from the first two attempted fixes:
**do not infer identity from strings the environment is also free to contain** — matching `"claude"`
in a process command line matched the throwaway shell of every tool call, and matching the binary
path hit the same wall. Prefer a fact something authoritative wrote down.

---

## The two that are not in the table, and why

Kept as review questions, because no check can decide them:

- **Is this the right citation?** A stale reference was replaced with a *false* one — the new target
  existed and said nothing about the subject. A gate can prove an identifier resolves; only a reader
  can prove it is the right one. **Ask at review: did you open the target and confirm it says the
  thing?**
- **Does the prose match the contract, or another paragraph of prose?** A "correction" to an attempt
  cap introduced a second vocabulary for one counter, because it was written against a description
  instead of the schema. **Ask at review: which artefact did this number come from?**

---

## The one instruction that would have prevented the most

> **Before trusting any tool's report about the world, make it report something you can already
> verify.**

Four of the worst failures on that project were the same failure wearing different clothes: a test
suite reporting green having skipped every assertion; a gate printing `FAIL` and exiting `0`;
containers reporting healthy while the tools talked to the host's services; a coordination plugin
reporting a lease held by an identity that belonged to a different session. In each case the tool
was describing a world it was not looking at, and in each case one deliberate check against a known
answer would have exposed it in a minute.

---

## Where these bind in the pipeline

| Stage | Rules that apply |
|---|---|
| 0 Inventory · 9 Docs · any register write | 8 (compute), 14 (targets resolve — including every commit SHA in the retro), 15 (identity before a lease) — see [`documentation.md`](documentation.md) |
| any check you write | 4, 5, 7, 10, 11 — the procedure is [`gates.md`](gates.md) |
| 3 Spec · 4 Plan | 2 (both directions), 8 (compute, never restate) |
| 5 Dev | 9 (generators seed green), 12 (tests create their own state), 13 (local infra) |
| 6 Tests | 4, 5, 10, 11 — every new check probed both ways, measured, and asserted on its exit code |
| 9 Docs | 8, 14 — every number computed, every target resolvable |
| 10 Acceptance | 1, 3, 6, 7 — axis rotation recorded, closure verified against artefacts, classes swept, ratchets printed |

**This file is the shipped list; a project keeps its own.** These fifteen were
earned on someone else's build and travel with the skill. The lessons *your*
project buys go in its retro ([`retrospective.md`](retrospective.md) →
`docs/superpowers/retro.md`), where they are capped, pruned and retired — and a
lesson there that would be true in any repository belongs here instead, as an issue
upstream. A local file that accumulates universal rules is a fork of this one that
nobody named.
