# Carry-over ledger — spec and plan quality

Seeded at stage 0, appended by **every** stage the moment something is deferred,
dropped or left half-done, read in full at stage 10. Deferred out loud is forgotten;
a row here is the only form of deferral this run recognises.

The **count of unresolved rows is printed beside every gate verdict**, so a green
gate never reads as "nothing was set aside".

## Rows

| id | Raised at | What | Why deferred | Resolution | State |
|---|---|---|---|---|---|
| C-001 | 0 | Whether a `## Self-review` of computed numbers degrades into a template of zeroes (A3) | No check can decide it | Mitigation shipped and exercised: every line carries a **computed** value, and this run's own spec and plan both carry real ones. Whether that holds across runs is genuinely unknowable until several have passed — **left as a standing question, not a claim** | **closed at 3 — as a mitigation, not a proof** |
| C-002 | 0 | `grill.md` has no "is this worth doing at all" question, and this run deliberately does **not** add one — D4 lands at stage 3 instead | Scoped out on purpose (D4 in *Decisions locked*), not forgotten. If the stage-3 checkpoint proves to fire too late in practice, stage 0 is where the follow-up goes | Unchanged: D4 lands at stage 3, where the surface count is knowable. Revisit if the stage-3 checkpoint proves to fire too late in a real run | **open as a printed exclusion**, one run of evidence needed |
| C-003 | 0 | The four incidents live in the transcript; the branch holding them was deleted | No commit to cite | The retro entry cites this run's own commit and describes the incidents; the deleted branch is named as unavailable rather than implied to exist | **closed at 10** |

| C-004 | 0 | **This run is parked at its stage-0 gate, deliberately.** The operator sequenced the artifact-hygiene validators ahead of it | A mechanical scan holds without assuming the agent is diligent; a self-review item does not. Build the robust half first — and hygiene will hand this run a ready-made line for its `## Self-review` section | **Resume point:** branch `spec-plan-quality`, commit `dd3155e`, brief committed and gate not yet given. Restart at stage 0's gate, not at stage 0 | open — parked, not abandoned |

| C-005 | 5 | The hygiene gate did not run for task 2 — invoked from the wrong directory, and the commit landed anyway | Not deferred: noticed immediately | Re-run against `HEAD~1`, green. Recorded rather than quietly repaired, because "the gate ran" is exactly the kind of claim this release is about | **closed at 5** |

## Counts

- Rows: 5
- Unresolved: 0
- Closed: 4
- Open as a printed exclusion: 1 (C-002 — `grill.md`, revisit after one real run)

## Parked

Stage 0 complete, gate not given. Nothing after stage 0 was started, so there is no
half-done work to reconcile on resume — only a brief awaiting a `go`.
