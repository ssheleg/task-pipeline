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
| 0 Harvest | doc sources beyond this repo — other repos, hosted doc systems, the knowledge wiki — and whether stage 9 may write to them (another repo is outward: propose + PR, never a direct push) |
| 1 Docs | external libs/APIs/SDKs in play; any private ones context7 can't resolve → where their docs live |
| 2 Decompose | is this a platform (several capabilities/surfaces) or one module? if platform: deploy cadence — per module or once at the end |
| 2–3 Spec | UI verdict (arms super-ux); any scenario-tracing waiver |
| 4–5 Dev | base branch; worktree/branch policy; is `main` off-limits; commit convention; task tracker |
| 5 Integration | how the branch lands (merge / PR + approver / "leave it unmerged"); parallel fan-out wanted (one worktree per implementer)? |
| 6 Tests | the test command; what "green" means here; known-red baseline; coverage expectation |
| 7 Lint+deploy | lint command; deploy target and path; release automation on/off; deploy-from-main rule; **deploy authorization** |
| 8 Post-deploy | where logs / health live (app name, endpoint, workflow) |
| 9 Docs+wiki | which module docs / runbooks this change updates; wiki sync yes/no |
| 10 Acceptance | who signs off; where deferred REQs are tracked (issue tracker, backlog) |

**Deploy authorization has a hard floor.** Deploy and publish are outward and
irreversible, so a vague "just do everything" authorizes nothing. A standing
authorization counts only when it is **specific** — named target, named
preconditions ("staging once lint and the full suite are green; production always
asks"). Specific and recorded → it satisfies the stage-7 manual gate. Broader,
absent or ambiguous → stage 7 stops and asks.

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
