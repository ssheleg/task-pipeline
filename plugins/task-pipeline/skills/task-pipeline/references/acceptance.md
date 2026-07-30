# Acceptance — stage 10, built in

The pipeline is a funnel: every gate before this one asks *"is this artifact
good?"* — is the spec committed, does the plan parallelize, is the suite green.
None of them asks *"does this still contain everything that was asked for?"*

That is this stage's only job: **go back to the brief and account for every
requirement.** It is what turns the pipeline from a funnel into a circle.

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

## GATE (manual)

All of:

1. **The ladder walk ran** ([`audit.md`](audit.md)) — every REQ's rungs checked
   bottom-up, findings ordered by seam, absences turned into REQ rows **before**
   the table was written, and the two pass counts recorded.
2. **Every check this gate leans on has been seen failing** at least once against a
   planted defect (`audit.md` → *Exit criterion*). An unproven check's green is not
   evidence.
3. **Every REQ has a status** — none `unknown`, none blank.
4. **Every `verified` carries evidence** of the kind above.
5. **Every `partial` names what's missing** and where it's tracked.
6. **Every `deferred` / `dropped` has the operator's agreement** recorded (in the
   ledger or here) and, for `deferred`, a tracker entry.
7. **No carry-over row is left `unresolved`** — every one has a home, and the
   ledger's counts are printed with this verdict, not just filed.
8. **Every repository is closed, the parent included** — `git submodule status`
   shows no `+`, and each repo is clean and pushed. A submodule is finished when
   its parent points at it.
9. **The operator answers the closing question** and signs off.

Manual by design. An automated check can prove the table is *well-formed*; only
the person who asked can confirm it is *what they asked for*. Do not let a green
table substitute for that answer.

## When the answer is "something's missing"

Don't argue and don't re-litigate the gates. Add the missing thing as a new REQ
row (with its check) or a ledger entry, then say plainly what it costs: a fix now,
or a tracked follow-up. Both are legitimate outcomes of this stage. Closing the
run with a known gap is fine **if the gap is written down** — closing it with the
gap only in someone's memory is the failure mode this whole spine exists to
prevent.
