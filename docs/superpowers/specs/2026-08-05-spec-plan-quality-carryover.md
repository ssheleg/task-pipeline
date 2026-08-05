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

## Counts

- Rows: 3
- Unresolved: 3
- Closed: 0
