# Stage 9 detail

The full gate and freedom level remain in [stages.md](stages.md).

## 9 — Docs + wiki
- **The propagation sweep runs first** ([`documentation.md`](documentation.md)).
  The ledger below names the documents you **read**; the matrix in `docs/DOCMAP.md`
  names the documents you **owe**. They are not the same list, and the gap between
  them is where documentation rots — the document nobody read is exactly the
  document nobody updated. Walk the matrix row for **every** change type this run
  produced. Every settled thing gets an id in the register, every answered question
  is flipped to `Resolved→<id>`, and every document named in a
  `Consequences / affects:` line cites its decision.
- **Then run the documentation gate** (`bash scripts/check-docs.sh`, or whatever
  `docs/DOCMAP.md` → *Gates* names) and print its **ratchet counts** beside the
  verdict, so "green" reads as *"green, and here is exactly what was not looked
  at"* ([`gates.md`](gates.md)). A check that skipped says so.
- **The documentation graph** ([`doc-graph.md`](doc-graph.md)): `docgraph.py build`
  and `check` where `docs/graph/` exists; where not, the hidden refactoring.
- **The stage-0 source ledger is the work list** ([`knowledge-sources.md`](knowledge-sources.md)
  → *Close the loop*): every source the harvest read gets updated if this run
  changed or disproved it. What was worth reading at stage 0 and is wrong now is
  the next run's false premise.
- Update host module docs / runbooks per the project's self-update rules, in the
  **same change**. For UI tasks, confirm the super-ux layers were updated in this
  change and the linter is green (super-ux *same-change* + *no-drift* rules).
- **Where the actor branch is armed, `AGENTS.md` is generated, not edited**
  ([`agent-surface.md`](agent-surface.md)): its capability list comes from
  `docs/ux/capabilities.md` and the contract snapshot, with the registration
  command and one proving call. The event catalogue is updated only when events
  changed.
- **Sync the knowledge wiki** (obsidian-wiki's `wiki-update`) where installed
  ([`knowledge-sources.md`](knowledge-sources.md)): decisions, seams, why, not a diff
  summary. A missing wiki never blocks the gate.
- **Refresh the code graph (`/graphify . --update`), then check it against the docs**:
  [`knowledge-graph.md`](knowledge-graph.md) → *Stage 9* and *The divergence check*;
  absences go to stage 10 as REQ rows.
- **Docs living in another repository** are outward: propose the edit, get an
  explicit go, then open a PR there. No go → the exact edit goes in the carry-over
  ledger.
