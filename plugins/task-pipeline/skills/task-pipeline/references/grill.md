# The grill — stage 0, built in

The intake grill is **part of this skill**. No companion skill to install, no
provider to resolve, nothing to fall back to: this file *is* the implementation.

Its job is not to design. It is to take a one-line request ("make me feature X")
and interview it into a brief complete enough that stages 1→9 finish without
coming back to the operator.

> Adapted, with thanks, from Matt Pocock's `grilling` / `grill-with-docs` skills
> (MIT — see this repo's `LICENSE` → *Third-party*). The domain-awareness
> half — glossary challenges, `CONTEXT.md`, ADR discipline — comes from there; the
> autonomy sweep and the brief are this pipeline's.

## The loop

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
would otherwise stop stages 1→9 mid-flight. Every row gets an answer **or** an
explicit "stop and ask me here":

| Stage | What to settle up front |
|---|---|
| run-wide | the model decision ([`model-tiering.md`](model-tiering.md)); what to decide autonomously vs escalate |
| 1 Docs | external libs/APIs/SDKs in play; any private ones context7 can't resolve → where their docs live |
| 2–3 Spec | UI verdict (arms super-ux); any scenario-tracing waiver |
| 4–5 Dev | base branch; worktree/branch policy; is `main` off-limits; commit convention; task tracker |
| 6 Tests | the test command; what "green" means here; known-red baseline; coverage expectation |
| 7 Lint+deploy | lint command; deploy target and path; release automation on/off; deploy-from-main rule; **deploy authorization** |
| 8 Post-deploy | where logs / health live (app name, endpoint, workflow) |
| 9 Docs+wiki | which module docs / runbooks this change updates; wiki sync yes/no |

**Deploy authorization has a hard floor.** Deploy and publish are outward and
irreversible, so a vague "just do everything" authorizes nothing. A standing
authorization counts only when it is **specific** — named target, named
preconditions ("staging once lint and the full suite are green; production always
asks"). Specific and recorded → it satisfies the stage-7 manual gate. Broader,
absent or ambiguous → stage 7 stops and asks.

## Output

Everything resolved goes into the **task brief**, seeded from
[`templates/brief.md`](../templates/brief.md) and committed to
`docs/superpowers/specs/YYYY-MM-DD-<topic>-brief.md` — scope, users, UI verdict,
constraints, locked decisions, the autonomy table, done-criteria, open
assumptions. Seed the template only when the file is absent; never overwrite an
existing brief.

Plus, where the session produced them: an updated `CONTEXT.md` and any ADRs, each
written as the decision landed.

The operator confirms the brief. Only then does stage 1 begin.
