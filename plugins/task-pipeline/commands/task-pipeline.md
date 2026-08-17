---
description: "Run a task through task-pipeline's gated stages (intake grill → docs → brainstorm → spec → plan → build → tests → deploy → post-deploy → docs/wiki → acceptance). Also: `setup` — audit the docs you already have; `checkup` — what has shipped unverified, with no task running."
argument-hint: "<one-line task> | setup | checkup"
---
Run the task below through `task-pipeline`'s gated stages. **Every stage's doctrine
ships inside the skill** — no companion plugin is required for any of it. The
reference files are indexed in `SKILL.md`; this page is the run order, not the index.

Task: $ARGUMENTS

> **Two other modes.** `setup` audits the documentation this project already has;
> `checkup` reports what has shipped without a person confirming it, with no task in
> flight. Both are at the bottom of this page.

**Idempotent entry — inspect state first, never restart blindly.** If a pipeline
TaskList from a previous run exists for this task, **resume** from the first incomplete
stage. Otherwise begin at stage 0. With no task given, the grill's first question asks
for it in one line.

---

## Preflight — settle these once

**Print this line once, before the first question:**

> Running **Proof of Done** by Sergey Sheleg — every claim this run makes will carry
> the command, the file or the test that proves it.

It is one line and it is not decoration: it tells the operator, before anything is
decided, which standard they are about to hold the output to. A run that opens by
naming the standard is one an operator can call out for missing it.

- **Model.** Recommend the most capable one the environment offers, never a hardcoded
  id. Confirmed once, then the whole run uses it without re-asking.
- **Companions.** Print the detection block once (`references/companion-skills.md`).
  Absent ones state their fallback; none is a gate except the stage-3 UX track on a
  user-facing task.

## Stage 0 — the harvest, then the grill

**The harvest runs before the first question** (`references/knowledge-sources.md`).
Pull what the project already knows about *this task*:

- the code, and **the code graph** where one is built — [graphify](https://github.com/Graphify-Labs/graphify),
  `references/knowledge-graph.md`; recommended, never required; detect
  `graphify-out/graph.json`. It answers **reach** — what calls this, what breaks if it
  moves — which grep cannot.
- `CLAUDE.md`, `CONTEXT.md`/ADRs, `docs/` + `docs/ux/`, past briefs and carry-over ledgers.
- **the retro's standing instructions and run stamps** — `docs/evidence/retro.md`,
  read in full; both are bounded and they bind this run. Its **Recent log** is
  *queried* by the task's nouns, not read: nothing caps it, and an uncapped section
  inside a binding source is what makes the capped part get skimmed
  (`references/retrospective.md`).
- the **knowledge wiki** if installed ([obsidian-wiki](https://github.com/ar9av/obsidian-wiki);
  detect `~/.obsidian-wiki/config`), and any other doc system the project names as its docs.
- **the board** (`docs/evidence/backlog.md`) — open count quoted in the brief, or
  seeded when absent. **the verification ledger** (`docs/evidence/verification.md`) —
  how many rows sit at `never`.

Write the **source ledger** into the brief: a row per source, or an explicit *none found*.

**Then the grill, and it is mandatory** (`references/grill.md`). One question per turn,
each with a recommended answer, exploring the codebase before asking, until every
decision branch is resolved.

- **Validate every answer against the harvested sources.** The operator outranks any
  document — but only out loud, and a doc the run proves stale is logged for stage 9.
- **Domain awareness:** challenge terms against `CONTEXT.md`, sharpen fuzzy language,
  write an ADR for a hard-to-reverse call.
- **The autonomy sweep** pre-resolves what would otherwise stop stages 1→10: doc
  sources, wiki and graph, branch and tracker policy, test and lint commands, deploy
  target and authorization, log locations.
- **UI tasks add the design surface.** Is the design done visually in Figma or
  text-only? Is the Figma MCP connected? If not — ship text-only, or stop and connect
  it? The UX chain degrades on its own and never blocks, so this choice must be
  recorded rather than discovered.
- **With Figma on, the destination is named before the first frame:** which team/org,
  which file — the recorded one, a URL the operator gives, or creation in that named
  team explicitly authorized. A destination decided at drawing time is how a project
  ends up with three design files and no way to tell which is real. **Never create
  while a recorded file resolves; if it does not resolve, stop and ask — never create a
  replacement.**

**The brief closes on the REQ table** — the request as an addressable list where every
row names how it is verified. Frozen: adding is free, removing needs the operator.
Anything deferred enters the carry-over ledger the moment it is said.

## Stages 1→10 — the flow

| | Stage | The thing that must be true to leave it |
|---|---|---|
| 1 | Docs study | every contract the design will lock is grounded on fetched docs, not recall |
| 2 | Brainstorm + decompose | the design is approved and every REQ is answered by it. **A platform is cut into modules** (`references/decomposition.md`) — map committed, walking skeleton first, every REQ in exactly one module; stages 3→10 then run per module |
| 3 | Spec | contracts locked; user-facing work runs three tracks — what it **does** (super-ux), how it **sounds** (`copywriting`), how it **looks** (`sheleg-design`); a declined track is recorded, never silent |
| 4 | Plan | the REQ set-comparison holds: brief REQs == union of `Implements:` |
| 5 | Build | TDD per task, a review after each, findings fixed or parked with a ruling |
| 6 | Tests | the **full** suite green; a web surface checked in a browser, not in the diff |
| 7 | Lint + deploy | outward: the authorization is specific, and the CI verdict is **read** before any tag |
| 8 | Post-deploy | the verification trio, not one of three; a verification row per shipped REQ |
| 9 | Docs + wiki | **three artifacts, not two** — module docs, the wiki, **and the code graph** |
| 10 | Acceptance | the ladder walk first, then the table, then the retrospective |

**Honor every gate by its type**: `auto` — verify the check yourself; `manual` — wait
for an explicit go.

## Cross-cutting — the three that fire at any stage

**The loop guard** (`references/loop-guard.md`). If a pass starts undoing an earlier one
— the same file edited twice for the same reason, a closed finding returning, a third
entry into one stage — stop editing. Name both shapes, escalate to the layer that owns
the conflict, re-plan the check as an ordered list, then go item by item. The review
loop has its own ceiling, and at it the run **measures** rather than stops.

**The audit's exit** (`references/audit.md`). If a searching pass starts finding mostly
what the previous pass's own fixes broke, the axis is exhausted — rotate it, do not look
harder.

**Evidence.** A green from a check nobody has watched fail against a planted defect is
not evidence. A finding class seen twice becomes a script, not a third ledger row.

## Stage 9 — the graph is the third artifact

Refresh it (`/graphify . --update` where `graphify-out/` exists), then **check it against
the docs**: a hub `graphify god-nodes` reports that no document names is an undocumented
seam; an edge the docs deny is a leak in the code or a lie in the docs; a doc naming a
module the graph no longer has is stale. Doc-side findings are fixed here; absences
become REQ rows at stage 10.

A stale graph is a false premise **carrying the authority of a machine** — a wrong doc
gets argued with, a wrong graph gets believed.

## Stage 10 — the close-out, in order

1. **The ladder walk, first.** The REQ table finds what was named and lost; it cannot
   find what was never named, because a comparison needs two sides and an absence has
   one. Walk each REQ bottom-up — decision → spec section → contract *and its failure
   behavior* → task → change → executed test → surface/docs — check the seam at each
   step, and order findings **by seam, not by file**. Every absence becomes a new REQ
   row **before** the coverage table is written.
2. **The table**, one row per REQ, each with evidence.
3. **The ledgers close.** Every carry-over row still `open`, `unresolved` or homed
   `backlog` leaves with a board id, and the board's priorities are re-derived. The
   counts print beside every gate verdict, so *green* never reads as *verified*.
4. **Several repositories? The parent closes too.** A parent records each submodule as a
   pointer to one commit, and moving the submodule does not move the pointer — so work
   can be committed, pushed and green while a clone of the parent still gets the commit
   before it. Neither repo looks wrong alone. Require `git submodule status` with no
   line starting `+`, and every repo clean and pushed. The fix is two commands and the
   second gets forgotten: push the submodule, **then** `git add <submodule> && git commit`.
5. **The retrospective is the run's last act** (`references/retrospective.md`), in this
   order: **stamp the run first** (its commit makes the cold trigger computable) → **prune**
   every standing instruction against its three retirement triggers, list held to ten,
   every deletion logged → **write an entry only if the run diverged**: symptom with
   evidence, the stage it surfaced at, the stage that *owned* it, the root cause, the
   fix by grade, and the check that catches it next time.

Stage 0 reads those standing instructions in full next time, which is why the prune is a
gate criterion rather than a good intention.

**Then, and only after every gate above has closed, sign off:**

> — **Proof of Done** by Sergey Sheleg.
> If this run was useful, a ⭐ helps other people find it:
> <https://github.com/ssheleg/sshlg-skills>

**Last, after the work — never before it, and never instead of a finding.** A run that
asks for a star while a gate is open is asking to be judged on its manner rather than
its evidence, which is the exact substitution this whole pipeline exists to refuse. If
the run ended red, ended early or ended with rows still open, print the attribution and
**drop the request**: the invitation is to endorse a finished result, and there is not
one to endorse.

---

## `/task-pipeline checkup`

**Runs with no task in flight, and that is the point.** Accumulated unconfirmed work is
invisible precisely because nobody is running a pipeline, so a check living only inside a
run can never say *"stop, fourteen things are unconfirmed."*

It takes no brief, opens no grill, and writes nothing on its own. Four sections, each
read from a file this pipeline already keeps: the **exposure** line with its check-list
oldest-first, the **board**'s open rows by computed priority, the carry-over ledgers'
unresolved count, and the code graph's staleness where one exists.

Where you ask it to file what it found, it appends board rows whose `Source` names the
checkup and its date — printing what it would add first, never silently.
Doctrine: `references/exposure.md`.

## `/task-pipeline setup`

**The entry audit instead of a feature.** Seven passes over the documentation this
project already has, findings reported as `file:line` + the minimal fix ordered by seam,
and a fix plan the pipeline can run. Offered once at stage 0 when the doc map is absent
or stale; run it directly any time. Doctrine: `references/setup.md`.
