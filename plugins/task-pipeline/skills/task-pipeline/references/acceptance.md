# Acceptance — stage 10, built in

The pipeline is a funnel: every gate before this one asks *"is this artifact
good?"* — is the spec committed, does the plan parallelize, is the suite green.
None of them asks *"does this still contain everything that was asked for?"*

That is this stage's only job: **go back to the brief and account for every
requirement.** It is what turns the pipeline from a funnel into a circle.

## Contents

- Why a stage and not a gate
- First, the ladder walk — what the list itself is missing
- Inputs
- Output — the coverage table
- Evidence, not assertion
- Several repositories — a submodule is finished when its parent says so
- The closing question
- The retrospective — the run's last act
- A `verified by` name is a claim until it resolves
- A seam is not a deliverable, and REQ rows are written against deliverables
- GATE (manual)
- When the answer is "something's missing"

## Why a stage and not a gate

The loss this catches doesn't happen inside a stage — it happens **on the seams**.
Brief → spec → plan → task briefs is four rewrites by a model, and anything not
carried forward disappears silently because nothing compares the lists. Stage 4's
gate catches the brief→plan seam mechanically; stage 10 catches everything the
run itself decided, deferred, or quietly dropped along the way.

It runs **last** — after docs and wiki (stage 9), because those are deliverables
too and a requirement may name them.

## First, the ladder walk — what the list itself is missing

The REQ table answers *"did everything on the list ship?"*. It cannot answer
*"should something else have been on the list?"* — a comparison needs two sides,
and an absence has one.

So **before writing the coverage table**, walk the ladder in
[`audit.md`](audit.md): each REQ bottom-up through its rungs (decision → spec
section → contract **and its failure behavior** → task → change → executed test →
surface and docs), checking the seam at each step. It is one pass, scoped to this
run's deliverables, and it is the only part of the pipeline that can find a gap
that was never a row.

- **An absence found here becomes a new REQ row with its check**, then the table is
  written. The list is frozen against *narrowing*, never against additions
  ([`grill.md`](grill.md) → *The REQ spine*). Writing the table first and appending
  afterwards is how acceptance goes green over a gap.
- **A finding that belongs to a lower layer goes back to that layer** — spec gaps to
  stage 3, plan gaps to stage 4 — rather than being patched in place at stage 10.
- **Report the audit's two counts** (new findings; findings caused by this run's own
  fixes) in the ledger. They are what tells the next pass whether the axis is
  exhausted (`audit.md` → *Every pass changes the axis*).

## Inputs

Read all of them before writing anything:

- the ladder walk's findings (above) — they may have added REQ rows
- the brief's **REQ table** (`docs/superpowers/specs/<topic>-brief.md`)
- the **carry-over ledger** (`…-carryover.md`) — in full, every row
- the plan and its task statuses
- git log for the run's branch; the test suite's final output
- stage 8's post-deploy notes; stage 9's doc/wiki changes
- for UI tasks: `docs/ux/scenarios.md` statuses and the `/ux-lint` result

## Output — the coverage table

Write `docs/superpowers/specs/YYYY-MM-DD-<topic>-acceptance.md`:

```markdown
# Acceptance — <topic>

Run: <branch/commit range> · Date: YYYY-MM-DD

| REQ | Requirement | Status | Evidence |
|---|---|---|---|
| REQ-001 | CSV export from a report | verified | `test_export_csv` ✓ · `api/export.ts:88` |
| REQ-002 | Export respects active filters | verified | `test_export_respects_filters` ✓ · SCN-014 PASS |
| REQ-003 | Button disabled on an empty report | deferred | agreed 2026-07-28 → LIN-482 |
| REQ-004 | XLSX export | partial | CSV path done; XLSX missing → LIN-483 |

## Carry-over still open

- (rows from the ledger whose home is not an issue/backlog/`dropped`)

## What the operator should look at

- <anything the run judged, guessed, or deferred that deserves a second opinion>
```

### The four statuses

| Status | Means | Requires |
|---|---|---|
| `verified` | done and demonstrated | **evidence** — a passing test name, `file:line`, command output, or a scenario ID with PASS |
| `partial` | works for some of what was asked | an explicit list of what's missing + where it's tracked |
| `deferred` | agreed not to do it now | the operator's agreement **and** a tracker entry |
| `dropped` | agreed it isn't wanted | the operator's agreement + the reason |

**A `dropped` is a scope decision, and it outlives this run.** The operator's
agreement closes the row here; the **Doc Loop**
([`documentation.md`](documentation.md)) is what stops the same requirement being
re-proposed next quarter by someone who never saw this table. A `deferred` needs its
tracker entry, not an entry in the register — it is a schedule, not a decision.

Those four are the only ways a requirement may close. Anything that fits none of
them is `unknown`, and **`unknown` fails the gate** — that is the whole mechanism:
the run cannot end while a requirement is still unclassified.

## Evidence, not assertion

**"Done" without evidence is not done.** This is the same rule the review rubric
and the test-honesty rules apply one level down, raised to the level of intent:

- A passing test **name**, not "tests pass".
- A `file:line`, not "implemented in the export module".
- A command **and its output**, not "verified manually".
- For user-facing behavior, the scenario ID and its status.

If the evidence for a requirement is "I read the code and it looks right", the
status is `partial`, not `verified` — say so plainly rather than upgrading it.

## Several repositories — a submodule is finished when its parent says so

A parent repository records each submodule as **a pointer to one commit**, and
moving the submodule does not move the pointer. So the work is committed, pushed,
its CI is green and its own roadmap says done — while anyone who clones the parent
gets the commit **before** the change.

Neither repository looks wrong on its own. The disagreement exists only *between*
them, which is why it survives every check that runs inside one — including this
stage, if this stage only ever looks at the repo it was working in.

Before the table is called complete, this reports nothing, **for the parent as well
as every submodule**:

```bash
git submodule status          # no line begins with '+'  (a '+' is the missing bump)
git -C <each repo> status --porcelain
git -C <each repo> log @{u}..HEAD --oneline
```

Where [agent-sync](https://github.com/ssheleg/agent-sync) is installed,
`/agent-sync finish` runs exactly this plus *no lease left held*, and `--gates`
adds the project's own gate commands.

When it fails, the fix is two commands and **the second is the one that gets
forgotten**:

```bash
git -C <submodule> push
git add <submodule> && git commit -m "chore: bump <name> submodule — <why>"
```

A REQ whose evidence lives in an unpushed commit, or in a submodule the parent
doesn't point at yet, is `partial` — the evidence is not reachable by anyone but
you.

## The closing question

The table is preparation. The stage exists for the question that follows it, asked
out loud, with the list in front of the operator:

> Here's what you asked for, here's what shipped, here's what's deferred and where
> it lives. **What's missing?**

Ask it even when the table is all green. The operator holds context the brief
never captured, and this is the cheapest moment in the whole run to hear it. An
answer here becomes new REQ rows or new ledger entries — not a new argument about
whether the run was finished.

## The retrospective — the run's last act

After the closing question, before the run is called done:
[`retrospective.md`](retrospective.md), written to `docs/superpowers/retro.md`.
Every run **stamps and prunes**; only a run that *diverged* writes an entry.

The order is fixed, and it is a **dependency, not a preference** — step 2 reads the
counter step 1 writes ([`learned.md`](learned.md) rule 21):

1. **Stamp the run first** — one line: date, topic, commit, verdict, retro counts. It
   costs nothing and it is the only thing that makes the next step computable.
2. **Then prune.** Every standing instruction is checked against its three
   retirement triggers — it became a check, its surface is gone, or it has not
   fired in the last five run stamps **or in the last sixty days** — and the list is held
   to its cap of **ten**.
   Every deletion writes one line in the log; silent deletion is forbidden.
3. **Write the entry, if the run diverged** — symptom, the stage it surfaced at,
   the stage that *owned* it, the root cause, the fix (mechanical > standing
   instruction > note with an expiry), and the check that catches it next time.

The counts are printed **beside this gate's verdict**, exactly like the carry-over
ledger's, so a list that quietly grew back is visible at the moment it happened:

```
GATE 10 acceptance: PASS — 14/14 REQ verified
  carry-over: 0 unresolved · retro: 7 standing (was 9) · retired 3 · added 1
  abstained: 2 (1 partial · 1 cannot-verify) · unlooked: 3 dormant
```

## A `verified by` name is a claim until it resolves

Reported from another project. Two rows in one run named checks that did not exist — a
locale-parity test for a project with ten locales and no such test, an index-resolution
test that had never been written. Both rows carried a status, an owner and an evidence
cell. **Nothing in the artefact distinguishes *"this check exists and passed"* from *"this
is the name a check would have if someone wrote it"*.**

This file already requires the evidence to come from a check seen failing once. That
requirement is about the **check**; nothing walks back from the **name** to ask whether a
check by that name is on disk. The ladder walk found both, because it re-derives coverage
from the artefact instead of reading the table — which also means the table was wrong for
the whole run until its last gate.

**So every name in a `verified by` cell resolves before the table is accepted** — to a
file, a test name a runner will select, or a command that exits. A cell naming nothing is
a REQ with status **`unknown`**, never `verified`.

The coverage table is this pipeline's own record of what was proven. When it can carry an
unresolvable name it stops measuring the run and starts recording the author's intent,
which is [`gates.md`](gates.md)'s false success living inside the pipeline's own artefact.

## A seam is not a deliverable, and REQ rows are written against deliverables

Also reported. Two halves of a feature shipped in one run, each correct alone, each with a
passing unit test. Together they formed a closed loop: a guard turned away users who had
not reached a state, and the new flow that would put them into that state sat behind the
guard. **The defect was in the seam, and a seam has no file.** The coverage table had a
row per artefact and both rows were green.

The blindness one layer down is already named — a handler test proves the handler, not the
request path. This is that shape one layer up.

**So when a run replaces a component that another component branches on, stage 2 writes an
explicit REQ for the boundary** —
not *"A works"* and *"B works"* but **"a user in state X reaches Y"**. Phrased as a
journey it is testable; phrased as two artefacts it is not.

**This does not contradict [`decomposition.md`](decomposition.md), and the wording matters
because a first draft did.** That file says a REQ appearing in two modules means the seam
runs *through* a requirement, and tells you to re-cut. A boundary REQ is not that: it is a
single requirement about the transition, owned by **one** module — the one that consumes
the boundary — and it maps to exactly one module like every other. Cite it as a journey
owned by the downstream module, and both rules hold.

**And where no check can span the seam** — a server-rendered redirect on one side, a
client write on the other — the table says so under `unlooked` rather than showing two
green rows. Two green halves reporting a working whole is exactly the shape this file
spends its length refusing.

## GATE (manual)

All of:

1. **Every shipped REQ has a verification row, and every row names a REQ its own run
   carries** ([`verification.md`](verification.md)) — both directions, because a shipped
   feature that entered no ledger and a ledger row about nothing are different failures.
   The row's `Human` is a date or the literal `never`; `never` is a **fact** and its
   count has no floor, no direction and never a target.
2. **The ladder walk ran** ([`audit.md`](audit.md)) — every REQ's rungs checked
   bottom-up, findings ordered by seam, absences turned into REQ rows **before**
   the table was written, and the two pass counts recorded.
3. **Every check this gate leans on has been seen failing** at least once against a
   planted defect (`audit.md` → *Exit criterion*; the procedure, with the commands,
   is [`gates.md`](gates.md) → *Probing*). An unproven check's green is not
   evidence. That includes **the documentation gate** the project's doc map names
   ([`documentation.md`](documentation.md)) — stage 9 ran it, this stage is where it
   is *proven*, and its **ratchet counts are printed beside this verdict**. A
   documentation gate is the easiest one in a run to inherit unproven, because it
   was green the first time anyone looked at it.
4. **Every REQ has a status** — none `unknown`, none blank.
5. **Every `verified` carries evidence** of the kind above.
6. **Every `partial` names what's missing** and where it's tracked.
7. **Every `deferred` / `dropped` has the operator's agreement** recorded (in the
   ledger or here) and, for `deferred`, a tracker entry.
8. **No carry-over row is left `unresolved`** — every one has a home, and the
   ledger's counts are printed with this verdict, not just filed.
7a. **Every disclosure is printed** ([`gates.md`](gates.md) → *Disclosures*):
   `abstained` — every REQ closing `partial`, every `unknown`, every ⚠️ *cannot verify
   from diff* the controller could not resolve — and `unlooked`, every check that
   reported `dormant` or `skip`. They are **not** ratchets: no floor, no direction, and
   a movement either way wants one sentence. A run reporting `abstained: 0` is claiming
   it knew everything, which is a stronger statement than any run this stage has ever
   seen close honestly.
9. **Every repository is closed, the parent included** — `git submodule status`
   shows no `+`, and each repo is clean and pushed. A submodule is finished when
   its parent points at it.
10. **The operator answers the closing question** and signs off.
11. **The retrospective is written** ([`retrospective.md`](retrospective.md)) — **in
    order**: the run is stamped with its commit first, **then** the prune runs before
    anything is added (standing instructions checked against their retirement triggers,
    the list at or under its cap of ten, every deletion logged), **then** a run that
    diverged gets its entry with a root cause and a named check. The stamp precedes the
    prune because a retirement trigger counts firings across the last five run stamps
    ([`learned.md`](learned.md) rule 21). The counts are printed beside this verdict,
    not filed.

Manual by design. An automated check can prove the table is *well-formed*; only
the person who asked can confirm it is *what they asked for*. Do not let a green
table substitute for that answer.
12. **The hand-back is written** ([`progress.md`](progress.md) → *The hand-back*) —
   the request quoted as it was GIVEN, where the run stands against it, what was solved
   with its evidence, what surfaced that nobody asked for, every decision still waiting
   **asked here with options rather than listed**, and the ambiguity count computed from
   its four registers with their ids. A run that cannot say what happened has not
   finished; it has stopped. This file is the one stage 10 opens, and it carried every
   other criterion while omitting this one for a release.
13. **The run has given the environment back** ([`residue.md`](residue.md)) — all
   eight classes enumerated **by class, never by one tool**, everything this run
   started ended in dependency order, each teardown verified by **re-enumerating
   rather than by the teardown's own reply**, and the result written as a `holds:`
   line. `holds:` reaching zero is required here and **only** here. An item left
   standing on purpose passes with its owner and reason named; an item **this project
   does not own** is **reported, never ended** — the inventory is machine-wide and
   the authority is not. An earlier run of *this* project is a third case, ended only
   when provably spent ([`residue.md`](residue.md) → *Three owners*).


## When the answer is "something's missing"

Don't argue and don't re-litigate the gates. Add the missing thing as a new REQ
row (with its check) or a ledger entry, then say plainly what it costs: a fix now,
or a tracked follow-up. Both are legitimate outcomes of this stage. Closing the
run with a known gap is fine **if the gap is written down** — closing it with the
gap only in someone's memory is the failure mode this whole spine exists to
prevent.
