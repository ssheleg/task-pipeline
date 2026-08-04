# The grill — stage 0, built in

The intake grill is **part of this skill**. No companion skill to install, no
provider to resolve, nothing to fall back to: this file *is* the implementation.

Its job is not to design. It is to take a one-line request ("make me feature X")
and interview it into a brief complete enough that stages 1→10 finish without
coming back to the operator.

> Adapted, with thanks, from Matt Pocock's `grilling` / `grill-with-docs` skills
> (MIT — see this repo's `LICENSE` → *Third-party*). The domain-awareness
> half — glossary challenges, `CONTEXT.md`, ADR discipline — comes from there; the
> autonomy sweep and the brief are this pipeline's.

## Contents

- Phase 1 — harvest before you ask
- Phase 2 — the loop
- Domain awareness
- The autonomy sweep
- The design destination — one file, decided here, never invented later
- The REQ spine — the grill's other hard output
- Output

## Phase 1 — harvest before you ask

**Do not open the interview cold.** Stage 0 begins by finding what the project
already knows about this task: the code, `CLAUDE.md`, `CONTEXT.md` and the ADRs,
`docs/` and `docs/ux/`, past pipeline briefs, the **knowledge wiki** when one is
installed, and any **other repository or hosted doc system the project names as
its docs**. Full procedure, source order, the wiki's detection and install line,
and the ledger to write: [`knowledge-sources.md`](knowledge-sources.md).

Two things come out of it, both required before question one:

- the **source ledger** in the brief — one row per source consulted, what it says
  about this task, and how fresh it is (`no sources found` is a valid row);
- the list of things you therefore **don't need to ask**, and the specific points
  where a source looks stale or ambiguous — those become the sharpest questions.

Everything below runs against that harvest. An answer you can't check against a
source is a recollection, and the whole loop exists to stop the run from building
on one.

## Phase 2 — the loop

Interview the operator relentlessly about every aspect of the task until you reach
a **shared understanding**. Walk down each branch of the decision tree, resolving
dependencies between decisions one by one.

1. **One question per turn.** Never bundle. Wait for the answer before the next.
2. **Recommend an answer with every question** (+ a one-line rationale). "What do
   you think?" is lazy — you have the codebase in front of you, they don't.
3. **If the codebase can answer it, go read the codebase.** Spending the
   operator's turn on something `grep`/`Read`/context7 would have told you is the
   most common way to waste a grill.
4. **Depth-first.** Finish a branch before opening another; ask prerequisite
   decisions first, so later answers don't invalidate earlier ones.
5. **Reconcile contradictions immediately**, and chase dodges: "we'll decide
   later" → "what's the latest you can decide and still ship?"
6. **Cover the autonomy sweep** (below). An unasked question is not neutral — it
   is a scheduled interruption at stage 6.

**Stop** when a re-scan surfaces no new branches. Don't grill past diminishing
returns: genuinely reversible calls can be deferred with a note.

## Domain awareness

While exploring the codebase, also look for what the project already says about
itself — and hold the operator to it.

### Find the existing docs

Most repos have a single context:

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

A `CONTEXT-MAP.md` at the root means multiple contexts, and points at where each
one lives (`src/ordering/CONTEXT.md`, `src/billing/CONTEXT.md`, …), each with its
own `docs/adr/` alongside the system-wide one. Infer which context the task
belongs to; if it's genuinely unclear, ask.

Create these files **lazily** — only when you have something real to write.

### Techniques during the session

- **Challenge against the glossary.** When a term conflicts with `CONTEXT.md`, say
  so on the spot: *"Your glossary defines 'cancellation' as X, but you seem to mean
  Y — which is it?"*
- **Sharpen fuzzy language.** Vague or overloaded terms get a proposed canonical
  one: *"You're saying 'account' — do you mean the Customer or the User? Those are
  different things."*
- **Stress-test with concrete scenarios.** Invent specific cases that probe edge
  conditions and force precision about the boundaries between concepts.
- **Cross-reference with the code.** When the operator states how something works,
  check whether the code agrees, and surface contradictions: *"Your code cancels
  entire Orders, but you just said partial cancellation is possible — which is
  right?"*
- **Cross-reference with the harvest — every answer, not just the domain ones.**
  Phase 1 put the ADRs, runbooks and wiki pages in your hands; use them the same
  way: *"The March ADR says orders are written only through the command handler,
  you just described a direct write — has that changed?"* The operator **outranks
  every document**, but only out loud: an override quoted against its source is a
  recorded decision, an unquoted one is an undetected divergence. When two sources
  disagree, precedence is code > host docs/ADRs > wiki > memory, and the loser is
  logged for the stage-9 update ([`knowledge-sources.md`](knowledge-sources.md) →
  *Phase 2*).
- **Update `CONTEXT.md` inline.** Resolve a term → write it down right then, not in
  a batch at the end. Format: [`templates/context.md`](../templates/context.md).
  Keep it free of implementation detail — only terms a domain expert would
  recognize.

### Offer an ADR sparingly

Only when **all three** are true:

1. **Hard to reverse** — changing your mind later carries real cost.
2. **Surprising without context** — a future reader will ask "why on earth this
   way?"
3. **A real trade-off** — genuine alternatives existed and one was chosen for
   specific reasons.

Any one missing → skip it. Format and what qualifies:
[`templates/adr.md`](../templates/adr.md). ADRs land in `docs/adr/` with sequential
numbering (scan for the highest number, increment).

## The autonomy sweep

Resolving the *task* is not enough. The grill must also pre-resolve everything that
would otherwise stop stages 1→10 mid-flight. Every row gets an answer **or** an
explicit "stop and ask me here":

| Stage | What to settle up front |
|---|---|
| run-wide | the model decision ([`model-tiering.md`](model-tiering.md)); what to decide autonomously vs escalate |
| run-wide Pacing | the **run mode** ([`continuity.md`](continuity.md)): does the run advance item-by-item with no check-in between items, and on what interval? Read `pipeline.json` → `run.loop` first — a recorded mode is the answer and is not re-asked. **Absent, it is off**: recommend it, take the answer, record it. It never collapses a `manual` gate or an outward act, so this row buys pacing, not authorization |
| 0 Harvest | doc sources beyond this repo — other repos, hosted doc systems, the knowledge wiki, **the code graph** ([`knowledge-graph.md`](knowledge-graph.md): built / installed-not-built / absent) — and whether stage 9 may write to them (another repo is outward: propose + PR, never a direct push) |
| 0 Setup audit | doc map absent or stale: run the entry audit over the existing documentation before building on it ([`setup.md`](setup.md))? Asked once; a refusal is recorded and never re-asked |
| run-wide Escalation | cost of being wrong: decide alone while it stays inside the repository and reversible; escalate price, legal posture, promise, money, reputation, irreversible outward acts. Project exceptions? |
| 0 Docs regime | where settled things live (the decision home — **one** per project, and an existing `docs/adr/` **is** it), who may write it, whether a lease mechanism is present or the run is `ungated`, the gate command and its ratchet floors, and whether this run may raise a floor ([`documentation.md`](documentation.md)) |
| 1 Docs | external libs/APIs/SDKs in play; any private ones context7 can't resolve → where their docs live |
| 2 Decompose | is this a platform (several capabilities/surfaces) or one module? if platform: deploy cadence — per module or once at the end |
| 2–3 Spec | UI verdict (arms super-ux); any scenario-tracing waiver |
| 3 Design surface | UI tasks only: **Figma on or text-only** (super-ux's project-level choice, default on — check `docs/ux/foundation.md` → *Design tooling* before asking); is the Figma MCP connected; **and if it isn't — ship text-only, or stop here and connect it?** super-ux degrades to text-only on its own and never blocks, which means an unasked question here silently ships a UI feature with no mockups |
| 3 Design file | Figma on only: **exactly which file, in which team/org** — the recorded one, or a URL the operator gives, or *create one in a named team* with that creation explicitly authorized. A destination decided at drawing time is how a project ends up with three "design" files and no way to tell which is real. See *The design destination* below |
| 4–5 Dev | base branch; worktree/branch policy; is `main` off-limits; commit convention; task tracker |
| 5 Integration | how the branch lands (merge / PR + approver / "leave it unmerged"); parallel fan-out wanted (one worktree per implementer)? |
| 6 Tests | the test command; what "green" means here; known-red baseline; coverage expectation |
| 7 Lint+deploy | lint command; deploy target and path; release automation on/off; deploy-from-main rule; **deploy authorization** |
| 8 Post-deploy | where logs / health live (app name, endpoint, workflow) |
| 9 Docs+wiki | which module docs / runbooks this change updates; wiki sync yes/no; **code-graph refresh yes/no** (`/graphify . --update` — the third close-out artifact) |
| 10 Acceptance | who signs off; where deferred REQs are tracked (issue tracker, backlog); the **retro file** — does `docs/superpowers/retro.md` exist, and are its standing instructions in force for this run ([`retrospective.md`](retrospective.md)) |

**Deploy authorization has a hard floor.** Deploy and publish are outward and
irreversible, so a vague "just do everything" authorizes nothing. A standing
authorization counts only when it is **specific** — named target, named
preconditions ("staging once lint and the full suite are green; production always
asks"). Specific and recorded → it satisfies the stage-7 manual gate. Broader,
absent or ambiguous → stage 7 stops and asks.

## The design destination — one file, decided here, never invented later

When the project designs in Figma, **the destination is a stage-0 decision, not a
stage-3 side effect.** Left to drawing time, the question "where do I put this?"
gets answered by whichever agent happens to be holding the brush, and the answer is
usually *create a new file* — which is how a project acquires three files called
some variation of "Design", each with real work in it and no way to tell which one
the team actually opens.

**Settle three things, in this order:**

1. **Is there already a file?** Read `docs/ux/foundation.md` → *Design tooling*
   first. A recorded, resolving file ends the question — record "use the recorded
   file" and move on. Do not ask the operator something the project already answered.
2. **Which team / organization**, by name. A file URL identifies a file; it does not
   say whose workspace it lives in, and a design that lands in someone's personal
   drafts instead of the team space is invisible to everyone who needs it. When the
   operator belongs to several teams, the choice is theirs and it gets written down —
   `whoami` tells you which are available, it does not tell you which is right.
3. **Which file** — an existing URL the operator supplies, or **creation in that
   named team, explicitly authorized.**

**Creating a file in a shared workspace is outward and irreversible enough to need a
named target.** It follows the same floor as deploy authorization above: *"create
the design file in team `Acme Product`"* authorizes one creation in one place. A
vague "set up Figma for me" does not — the whole failure this row prevents is an
agent deciding *where* on its own.

**Two rules that make it stick:**

- **Never create when a recorded file resolves.** Check before you create, every
  time, in every run.
- **If the recorded file does not resolve** — deleted, moved, no access — **stop and
  ask. Never create a replacement.** A replacement is exactly the duplicate this
  section exists to prevent, and "I couldn't open it so I made a new one" is how it
  always happens. An unreachable file is usually a permissions problem, which a new
  file does not solve and does hide.

**Where it lives, and which copy wins.** `docs/ux/foundation.md` → *Design tooling*
is **canonical** — super-ux owns that section, it is per-project, and it survives
every run, which is exactly what "the agents always know which file" requires. The
brief records the **decision and the authorization** and points at it; it is a
record, not a second registry. If the two ever disagree, `foundation.md` wins and
the brief is the thing that was stale. On a project with no `docs/ux/` at all, the
brief is canonical instead, and **stage 9 writes the destination into the host's own
docs** (`CLAUDE.md` or the README) so the next run finds it without asking.

**Write it down before drawing, not after.** The URL goes into the canonical record
the moment the file is chosen or created — before the first frame. A file created
and then lost to a crashed context is worse than no file: it exists, it is empty,
and nobody knows it is there.

## The REQ spine — the grill's other hard output

Prose scope is not checkable. Before the brief is confirmed, the grill must turn
what was asked into an **addressable list of requirements**, because every later
stage traces to these IDs and stage 10 accounts for every one of them.

| ID | Requirement | How it's verified | Status |
|---|---|---|---|
| REQ-001 | … | test name / `file:line` / command + expected output / `SCN-…` | open |

Three rules that decide whether the spine is worth anything:

1. **One REQ = one independently verifiable deliverable.** Not one per sentence of
   the request. A small task gets three rows, not thirty — an inflated table is
   ignored, and an ignored table protects nothing.
2. **Every row names its check.** *A requirement you can't say how to verify is a
   badly-stated requirement* — split or sharpen it here, during the grill. This is
   the single defence against the failure mode where three vague REQs cover a large
   task and acceptance goes green over half of it.
3. **Ask what "finished" means per row, not for the task overall.** "Export works"
   hides five decisions; "exports the currently filtered rows as CSV, verified by
   `test_export_respects_filters`" hides none.

**Then freeze it.** Adding a requirement mid-run is fine — append with its source.
**Removing or narrowing one requires the operator's explicit agreement**, recorded
in the carry-over ledger. Quietly restating the task in smaller terms is the
subtlest way to lose it: every gate downstream then passes honestly, on a task
that shrank without anyone deciding it should.

## Output

Everything resolved goes into the **task brief**, seeded from
[`templates/brief.md`](../templates/brief.md) and committed to
`docs/superpowers/specs/YYYY-MM-DD-<topic>-brief.md` — scope, **the REQ table**,
**the phase-1 source ledger**, users, UI verdict, constraints, locked decisions,
the autonomy table, done-criteria, open assumptions. Seed the template only when
the file is absent; never overwrite an existing brief.

The ledger is not decoration: **stage 9 updates exactly what stage 0 read**, and
every doc the grill proved stale is already listed there with what's wrong.

Alongside it, seed the **carry-over ledger** from
[`templates/carryover.md`](../templates/carryover.md) at
`…-carryover.md` — append-only, written by every later stage, read in full by
stage 10. Anything deferred, dropped, or half-done from here on goes there the
moment it's said: **deferred out loud is forgotten.**

Plus, where the session produced them: an updated `CONTEXT.md` and any ADRs, each
written as the decision landed.

The operator confirms the brief. Only then does stage 1 begin.
