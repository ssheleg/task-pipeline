# Brainstorm — stage 2, built in

The design conversation is **part of this skill**. No companion to install, no
provider to resolve, nothing to fall back to: this file is the implementation.

Stage 0 locked *what* is being built. Stage 2 decides *how*, and stops at an
approved design — not at code.

> Ported, with thanks, from the `brainstorming` skill in
> [obra/superpowers](https://github.com/obra/superpowers) (MIT — see this repo's
> `LICENSE` → *Third-party*), rewritten for this pipeline: the brief is the input,
> the UI verdict is a required output, and the spec write-up moved to stage 3
> ([`spec.md`](spec.md)).

## The hard gate

**No implementation action before the operator approves a design.** No code, no
scaffolding, no file creation "to see how it'd look", no invoking a
frontend/backend/build skill. This holds for every task regardless of how simple it
looks.

**"Too simple to need a design" is the trap, not the exception.** A one-function
utility, a config flip, a copy change — all of them go through this stage. Simple
tasks are where unexamined assumptions survive longest. The design may be three
sentences; it still gets presented and approved.

## Input: the brief, not a blank page

Read the stage-0 brief first (`…-brief.md`). Everything it locked — scope, users,
constraints, done-criteria, the autonomy sweep — is **settled**. Re-asking a
question the grill already answered is the single most common way to waste this
stage. If the brief and the codebase disagree, that's a contradiction to surface,
not a question to re-open from scratch.

## The loop

1. **Explore the current state.** Files, module docs, recent commits, the
   conventions the repo already follows. Do this before asking anything.
2. **Scope check, early.** If the task actually describes several independent
   capabilities or separately shippable surfaces, say so immediately: that is a
   **platform**, and it gets cut into modules at the end of this stage by
   [`decomposition.md`](decomposition.md), before any spec is written. Brainstorm
   the platform's shape — the pieces, how they relate, what order they land in —
   not the details of one corner; those belong to each module's own stage-3
   dossier. Don't refine something that needs splitting first.
3. **Questions one at a time.** Never bundle. Multiple choice where it fits, open
   where it doesn't. Purpose, constraints, success criteria — anything the brief
   left at design level.
4. **Propose 2–3 approaches with trade-offs**, lead with your recommendation and
   the reason for it. **YAGNI ruthlessly** — strip anything the task doesn't need
   from every option before presenting.
5. **Present the design in sections**, each scaled to its complexity (a couple of
   sentences when it's straightforward, up to a few hundred words when it's
   genuinely nuanced). Ask after each section whether it holds. Cover:
   architecture, components, data flow, error handling and degradation, testing.
6. **Go back when something doesn't fit.** A revised section beats a design that
   was approved because it was hard to argue with.

## Design for isolation and clarity

- Break the system into units with **one clear purpose each**, communicating
  through well-defined interfaces, understandable and testable on their own.
- For every unit you should be able to answer: what does it do, how is it used,
  what does it depend on?
- Can a reader understand a unit without reading its internals? Can the internals
  change without breaking consumers? If not, the boundaries need work.
- Smaller focused files are also what the *implementer* (often a subagent with a
  narrow context) handles reliably. A file growing large is usually a signal it
  does too much.

## Working in an existing codebase

- Explore the structure before proposing changes; follow the patterns already
  there.
- Where existing code genuinely blocks the work — a file that's grown unwieldy,
  tangled responsibilities, an unclear boundary the change has to cross — include
  the targeted improvement in the design, the way a careful developer improves code
  they're working in.
- Don't propose unrelated refactoring. Anything out of scope goes to the backlog,
  not into this design.

## UI detection — a required output

One branch is always: **does this touch a user-facing surface** (web, mobile, CLI,
TUI — a screen, a command, a visible behavior)? Stage 0 usually answered it; this
stage confirms it against the design that actually emerged. Record the verdict —
it arms the stage-3 UX track ([`spec.md`](spec.md) → *UX track*). When it's
genuinely borderline, record "yes": a false positive costs one extra chain, a false
negative ships an unspecified interface.

## The approved design is a set of decisions — record them

An approved approach is a decision, and so is each alternative rejected for a reason
worth remembering. Run the **Doc Loop** ([`documentation.md`](documentation.md)) on
the ones that will outlive this run: the shape chosen, the boundary drawn, the option
deliberately not taken. Not every preference — the ones a future reader would
otherwise re-litigate from scratch, which is the same test an ADR applies.

The cost of skipping it is specific: a design approved in conversation and recorded
only in the spec dies with that spec, and the next run re-opens a question the
operator already answered.

## GATE (manual)

The operator approves the design **and** the UI verdict is recorded **and every REQ
in the brief is answered by the design** — a requirement the design doesn't address
is either covered now or explicitly dropped by the operator, with the drop written
into the carry-over ledger. For a platform, the module map
([`decomposition.md`](decomposition.md)) is committed and approved as part of this
same gate. Then, and only then, stage 3 writes it up.

## Rationalizations

| Excuse | Reality |
|---|---|
| "The brief already says everything" | The brief locks *what*. If it also locked *how*, say so in one line and get the approval anyway — the gate is the point. |
| "It's a one-line change, design is ceremony" | Then the design is one line. Present it. |
| "I'll scaffold while they think" | Scaffolding is implementation. The gate is before it, not around it. |
| "Both approaches are fine, let them pick" | You read the codebase, they didn't. Recommend, then let them override. |
| "I'll add the extra option now, it's cheap" | YAGNI. Every unused branch is code someone maintains and a test someone writes. |
