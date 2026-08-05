# Carry-over ledger — artifact hygiene

Seeded at stage 0, appended by **every** stage the moment something is deferred,
dropped or left half-done, read in full at stage 10. Deferred out loud is forgotten;
a row here is the only form of deferral this run recognises.

The **count of unresolved rows is printed beside every gate verdict**, so a green
gate never reads as "nothing was set aside".

## Rows

| id | Raised at | What | Why deferred | Resolution | State |
|---|---|---|---|---|---|
| C-001 | 0 | The placeholder check must tell *using* a placeholder from *naming* one (A1) | Needed a measurement, not a guess | **Positional, not lexical:** a line-leading marker, optionally behind a comment introducer. Quoting/backticking would have caught 5 of 33. Measured 0 after the change, and it still fires on `# TODO:` | **closed at 2** |
| C-002 | 0 | Checks 5 and 6 have no measured false-positive rate yet (A2) | A detector is measured before it ships | Check 5: 0 across 94 files. Check 6 needed **two** corrections — same-or-higher level (62 → 4), then fenced content counting as body (4 → 2). Both remaining findings were real and are fixed, so the floor ships at 0 | **closed at 2** |
| C-003 | 0 | Per-task execution must stay fast or agents will skip it (A3) | A budget cannot be set before the checks exist | Diff mode scans only changed files; the full-tree run over 99 files is sub-second on this host. No budget rule was needed | **closed at 5** |
| C-004 | 0 | The `spec-plan-quality` run is parked at its stage-0 gate on branch `spec-plan-quality`, commit `dd3155e` | Sequenced behind this run on the operator's call | Unpark at stage 10 and hand it the hygiene line for its `## Self-review` section | open, owned by stage 10 |

| C-005 | 5 | Check 4 repeated check 2's false-positive mistake — matched its phrases anywhere and fired on this run's own brief and design | Not deferred: found by running the gate, fixed immediately, spec amended in place with the reason | Anchored line-leading. `learned.md` rule 6 (sweep the class, not the instance) was not applied by the spec that had just applied it once — recorded for the retro | **closed at 5** |
| C-006 | 5 | The VERDICT-last guard had been decorative since it shipped — it split on the word, which also appears in the header sentence forbidding anything after it | Found by writing its first probe; fixed in the same task | Splits on the `# ---------- VERDICT` marker and requires the marker to exist. Applies to `docgate.sh` too, which had the same hole | **closed at 5** |

## Counts

- Rows: 6
- Unresolved: 1 (C-004 — unpark `spec-plan-quality`, owned by stage 10)
- Closed: 5
