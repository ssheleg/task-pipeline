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
- What leaves this file, and why there is no cap

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
| 16 | **A carried-in claim is a recollection** | any run resuming from a summary, a handoff or a compacted context | re-derive the claim from its source before acting on it or reporting it | every state claim the run makes is marked `measured` with the command behind it, or it is not made |
| 17 | **The copy you are about to edit may not be the copy that ships** | any run editing a repository that has an upstream — a skill, a plugin, a vendored library, a fork | `git rev-list --count HEAD..@{u}` **before the first edit**; non-zero means stop and pull | the run states the count it measured, or it has not started |
| 18 | **State that accumulates locally is created from nothing everywhere else** | any run whose tests, migrations or fixtures read a database, a cache or a checkout that persists between runs on this machine | run the suite once against a **freshly created** instance of it, not the one that has been here for weeks | the run names the fresh instance it used, or the green is a green from residue |
| 19 | **An empty measurement is a refused measurement** | any command run to establish a fact — a count, a probe, a query, a suite | assert the output is **non-empty and shaped as expected** before reading meaning into it; a command that printed nothing did not answer | the run quotes the output it read, not the conclusion it drew from silence |
| 20 | **When a thing exists twice, ask which one is used — not whether they agree** | any artifact with a second copy: two build files, a vendored library, a schema and its mirror, doctrine in two documents | find the **consumer** and read what it names; the copies cannot answer this about themselves | the run names the file the build/test/deploy actually reads, quoted from the consumer |
| 21 | **A step that consumes what a later step produces is a deadlock, not an ordering** | any sequence where a check reads state another step writes — a prune reading stamps, a gate reading a ledger, a report reading counts | trace each input to the step that writes it; if that step is downstream, the check has never run on real data | every check names the step that produces its input, and that step is upstream of it |
| 22 | **An operation that changes nothing reports the same as one that changed everything** | a substitution whose needle is absent · a command whose output is suppressed at a decision point · an edit issued against a shape the file does not have | assert the effect, not the call: a replacement must report how many times it matched, and a command whose exit code governs the next step is never piped or silenced | four incidents in two programmes, each invisible until something downstream failed — an import that never landed, a doctrine phrase worded differently, a `gh` call refused behind `>/dev/null`, and a test piped to `head` so that `$?` belonged to `head` |

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

**16 · A carried-in claim.** A long autonomous run advanced one roadmap row per iteration. Each
iteration was correct: gates green, defects planted and watched to fail, docs closed. What was wrong
was the sentence between them — *"the remaining rows are these"* — taken from a list that had
arrived in the context through a compaction, had once been a filtered subset, and had lost its
provenance on the way. Eleven iterations later a single command over the register printed **36 open
rows out of 99**, not the handful being worked from. Nothing had failed, because nothing compares a
run's belief about the work-list against the register; the claim only ever appeared in prose.

**17 · The stale source.** A machine keeps its skills in two places: the working copy it publishes from and the installed plugin it runs. On 2026-08-07 the working copy was **two commits behind its own origin** — `v1.16.2` against `v1.18.0` — and the newer commits carried rule 16 itself. The repository was clean, nothing had diverged, and `git status` said so; the copy was simply never pulled. An edit made there would have landed on top of 1.16.2, and the release would have **silently deleted rule 16 and everything else in two versions** — not as a conflict, which git would have shown, but as a fast-forward over work that was already published. The project's own instruction names that directory as the source, so the person doing it would have been following the documentation. Nothing in the pipeline asked the one question that separates a source from a copy of one, and the check is a single command.

**18 · Residue.** A service's CI job started an empty database, created the runtime role in it, and ran the suite. Nothing between those two steps applied the schema. The result was **1039 failed, 1339 errors, 4704 × `UndefinedTable`** — every suite that touches a table — and it had been that way for as long as the repository had real tests. It was invisible because it is invisible *locally*: the compose database is migrated once, by hand, and stays migrated, so every author's machine has a schema and the runner's has none. The same day, in the same repository, a second instance: sixteen production tables owned by the **serving** role, because a migration had once been run as whoever was at the keyboard. Neither is a test defect. Both are the difference between state that accumulates and state that is created, and the only thing that tells them apart is running against something new.

**19 · Silence read as assent.** Three failures in one session, all the same shape. A `docker run` without `-i` does not attach stdin, so a heredoc carrying `ALTER ROLE` stopped at the docker CLI; `psql` read an empty script, did nothing, and exited **0** — and the step printed "password set". A `grep` pattern written against the wrong output format matched nothing, so three consecutive planted-defect runs printed empty strings that read as passes. And a migration step printed no lines at all, which looked like a step that had not run and was in fact a step that had. In every case the instrument failed and the failure was **indistinguishable from success**, because both produce nothing. Rule 11 covers the exit code; this covers the other half, which is louder in practice: an exit code of 0 from a command that never ran is the most convincing lie a run can tell itself.

**20 · The copy that wins.** A service had **two Dockerfiles**. One was added at the repository root by a run that checked whether a Dockerfile existed by looking where it expected one; `docker/Dockerfile` had been there all along, and `.github/workflows/ci.yml` says `file: docker/Dockerfile`. They disagreed about the port — 8080 at the root, 8000 in `docker/` — and the disagreement surfaced two days later as a **deployed service that answered nothing**, while `docker ps` said `Up` and `systemctl` said `active`. The built one also ran as root and copied the whole context, including `.git` and any `.env`; the hardened one was the one nobody built. Comparing the two files would have found the difference and not the direction. Only the workflow line says which one ships, and it is one grep. The same session hit this three more times: an autonomy sweep row added to the file that ASKS and not the file that RECORDS, twice, caught by a validator that knew to look at both.

**21 · The prune that could not run.** A retrospective's standing-instruction list has a hard cap of ten and three retirement triggers, one of which was, at the time of this incident, "it has not fired in the last five run stamps" — it has since gained a second unit, and the incident is left as it happened. The stage's own instruction was **prune first, then stamp**. So the trigger read a counter the same stage wrote afterwards: on a fresh list it is unreadable, and it stays unreadable for as long as nobody stamps. Measured on a real project: the last retro entry was five days old, stamps per day ran 33, 20, 26, **3, 0** — the zero on a day with 107 commits — and the list sat at exactly **10 of 10**, so every run arrived at a stage that opened with a full list, an unusable trigger and a mandatory deletion. It was not skipped out of laziness. It was skipped because its first step could not be performed, and the cheap step that would have made it performable was queued behind it.

The same class had already bitten that project twice from the other side, and its roadmap names the
property exactly: seven rows read `blocked` on producers the dependency board recorded as delivered,
and *"no gate can catch it because it breaks nothing — it only removes work from consideration"*;
and a row filed as *"the object nothing produces"* whose producer had shipped in between. **Stale
state does not throw.** It narrows what gets considered, silently, and every downstream gate passes
honestly on the smaller world.

Rule 8 is the neighbour, not the same rule: it governs a number *inside a document*, checked when
that document is checked. This one governs a fact that crossed a **session boundary** and is being
reported as current — the case where there is no document to check, only a memory that reads like
one.

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
| 0 Harvest · any run resuming from a summary | 16 — the work-list and every inherited state claim re-derived before use, [`knowledge-sources.md`](knowledge-sources.md) → *Carried-in claims* |
| any check you write | 4, 5, 7, 10, 11 — the procedure is [`gates.md`](gates.md) |
| **every stage** · any edit, any command whose result is read | 22 — a no-op is indistinguishable from success unless the effect is asserted; never suppress the output of a command a decision depends on |
| 3 Spec · 4 Plan | 2 (both directions), 8 (compute, never restate) |
| 5 Dev | 9 (generators seed green), 12 (tests create their own state), 13 (local infra) |
| 6 Tests | 4, 5, 10, 11 — every new check probed both ways, measured, and asserted on its exit code |
| 3 Spec | 14 — every check the spec **names** must resolve at the moment it is named, or be marked `review` |
| 4 Plan | 14 — every command, path and file a DoD names must resolve |
| 9 Docs | 8, 14 — every number computed, every target resolvable |
| 10 Acceptance | 1, 3, 6, 7 — axis rotation recorded, closure verified against artefacts, classes swept, ratchets printed |
| 10 Acceptance · every loop iteration | 16 — the work-list re-measured at close and printed beside its opening count ([`audit.md`](audit.md), [`continuity.md`](continuity.md)) |
| 0 Harvest · **before the first edit**, in any repository with an upstream | 17 — `git rev-list --count HEAD..@{u}` measured and its number printed, [`knowledge-sources.md`](knowledge-sources.md) → *The source is not the copy you have*; asked as row `0 Source` of [`grill.md`](grill.md) → *The autonomy sweep* |
| 0 Harvest · 5 Dev · 6 Tests | 18 — the suite run once against a **freshly created** instance of whatever persists between runs, [`tdd.md`](tdd.md) → *The green from residue*; asked as row `0 Fixtures` of [`grill.md`](grill.md) → *The autonomy sweep* |
| any command run to establish a fact — 6 Tests · 9 Docs · 10 Acceptance · 5 review | 19 — the output asserted non-empty and shaped as expected, and **quoted** rather than concluded from, [`audit.md`](audit.md) → *Silence is not a reading*; the reviewer's half is in [`review.md`](review.md) |
| 0 Harvest · 10 Acceptance | 20 — the **consumer** read to learn which copy ships, never the copies compared against each other, [`audit.md`](audit.md) → *Two copies, and which one wins*; asked as row `0 Duplicates` of [`grill.md`](grill.md) → *The autonomy sweep* |
| 10 Retro · **any gate or check you order** | 21 — each input traced to the step that writes it, and that step proven upstream, [`retrospective.md`](retrospective.md) → *Stamp first, then prune, then write* |

**This file is the shipped list; a project keeps its own.** Every rule in the table
above was earned on someone else's build and travels with the skill. The lessons *your*
project buys go in its retro ([`retrospective.md`](retrospective.md) →
`docs/superpowers/retro.md`), where they are capped, pruned and retired — and a
lesson there that would be true in any repository belongs here instead, as an issue
upstream. A local file that accumulates universal rules is a fork of this one that
nobody named.

---

## What leaves this file, and why there is no cap

`docs/superpowers/retro.md` caps its standing instructions at **ten** and retires them
on three triggers. Somebody proposes the same cap here about once a programme. It is
the wrong instrument, and the reason is worth more than the rule.

**A cap belongs to a file you must finish reading.** The retro's standing instructions
are read *in full* at stage 0 of every run — bounded by construction, or the last one
is never reached. This file is never read in full: it is entered by citation from the
stages, and *Where these bind in the pipeline* is that entrance. **A file you enter
through an index needs its index to be right, not its length to be short.**

And the cap would have measured the axis that is not moving. Re-derived across releases
rather than recalled — **measured at each tag**, so these rows are history and cannot
go stale; the live shape is printed by `npm test` beside its verdict, and this file
states no number about itself:

| | v1.14.1 | v1.20.0 | v1.23.0 | v1.29.0 |
|---|---|---|---|---|
| rules in the table | 15 | 18 | 21 | **21** |
| words in the file | 2165 | 2987 | 3696 | **3919** |

Rules have been flat for four releases while the file grew — and every word of that
growth is in the binding map, the section that makes a rule *reachable*. Cutting there
shortens the index. The largest section by far is the incidents, and those are the only
record of those events anywhere in this repository — checked by taking each incident's
distinctive tokens against the whole retro corpus, which returned nothing. They are not
a compression target; they are the thing the rules are made of.

**Two triggers retire a rule, and neither is a count:**

1. **The conditions cannot occur.** The tool, the layer, or the failure mode it names
   is gone from every project the skill runs on — not "we have not hit it lately".
2. **It is subsumed.** Another rule covers it entirely. This is a **merge**, not a
   delete: the absorbing rule names the absorbed one, and every binding-map row that
   pointed at the old number is repointed in the same change, or the map now sends a
   stage to a rule that is not there.

Never *"it became a check"* — that trigger is right for a standing instruction, whose
whole purpose is to be read until the machine takes over. Here the rule is the reason
the check exists, and a check whose reason has been deleted is the next thing somebody
removes as noise.

**Every deletion is logged as one line**, in the same change, the same discipline as
the retro's prune: the rule's number, its name, which trigger fired, and the commit.
A rule that vanishes silently takes its incident with it, and the next run re-learns it
at full price. Numbers are never reused and never closed up — a gap in the table is the
evidence that something left, and the log below says what.

### Retired

**Numbers issued so far: 22.** This is the high-water mark, and it is the only number
this file states about itself — deliberately, because the gap that proves a rule left
cannot be computed from the table alone: **deleting the highest-numbered rule shrinks
the maximum with it, and no gap ever opens.** That false negative shipped in the first
draft of this very section's guard and was found by a reader, not by its probe, which
had planted in the middle of the list.

*None retired yet.* Stated rather than omitted: an empty log and a missing log look
identical from outside, and only one of them means nothing has been retired. Each
retirement is one line, starting with the rule's number:

<!-- - **N · Name** — trigger: subsumed by M | conditions gone; `<commit>` -->

---
