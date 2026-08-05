# Carry-over ledger — spec and plan quality

Seeded at stage 0, appended by **every** stage the moment something is deferred,
dropped or left half-done, read in full at stage 10. Deferred out loud is forgotten;
a row here is the only form of deferral this run recognises.

The **count of unresolved rows is printed beside every gate verdict**, so a green
gate never reads as "nothing was set aside".

## Rows

| id | Raised at | What | Why deferred | Resolution | State |
|---|---|---|---|---|---|
| C-001 | 0 | Whether a `## Self-review` section of computed numbers is enough to stop it degrading into a template filled with zeroes (A3) | No check can decide it — needs a design judgement | — | open, owned by stage 2 |
| C-002 | 0 | `grill.md` has no "is this worth doing at all" question, and this run deliberately does **not** add one — D4 lands at stage 3 instead | Scoped out on purpose (D4 in *Decisions locked*), not forgotten. If the stage-3 checkpoint proves to fire too late in practice, stage 0 is where the follow-up goes | — | **open as a known exclusion**, revisit after one real run |
| C-003 | 0 | The previous run's four incidents live in this session's transcript; the branch that held them was deleted | Evidence is citable from the conversation, not from git. If the retro entry at stage 10 needs a commit, there is none to give | — | open, owned by stage 10 |

| C-004 | 0 | **This run is parked at its stage-0 gate, deliberately.** The operator sequenced the artifact-hygiene validators ahead of it | A mechanical scan holds without assuming the agent is diligent; a self-review item does not. Build the robust half first — and hygiene will hand this run a ready-made line for its `## Self-review` section | **Resume point:** branch `spec-plan-quality`, commit `dd3155e`, brief committed and gate not yet given. Restart at stage 0's gate, not at stage 0 | open — parked, not abandoned |

## Counts

- Rows: 4
- Unresolved: 4
- Closed: 0

## Parked

Stage 0 complete, gate not given. Nothing after stage 0 was started, so there is no
half-done work to reconcile on resume — only a brief awaiting a `go`.
