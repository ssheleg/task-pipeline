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
- **The stage-0 source ledger is the work list** ([`knowledge-sources.md`](knowledge-sources.md)
  → *Close the loop*): every source the harvest read gets updated if this run
  changed or disproved it. What was worth reading at stage 0 and is wrong now is
  the next run's false premise.
- Update host module docs / runbooks per the project's self-update rules, in the
  **same change**. For UI tasks, confirm the super-ux layers were updated in this
  change and the linter is green (super-ux *same-change* + *no-drift* rules).
- **Sync the knowledge wiki** — `wiki-update` when
  [obsidian-wiki](https://github.com/ar9av/obsidian-wiki) is installed (detect:
  `~/.obsidian-wiki/config`, or the skill resolves). Not installed → recommend it
  once with its install line and continue; a missing wiki never blocks the gate.
  Distil the knowledge (decisions, seams, why), not a diff summary.
- **Refresh the code graph** — `/graphify . --update` when one exists
  ([`knowledge-graph.md`](knowledge-graph.md)). The close-out has **three**
  artifacts, not two: docs, wiki, graph. The graph is the source the *next* run's
  harvest queries first, so a stale one is a false premise carrying the authority of
  a machine — a wrong doc gets argued with, a wrong graph gets believed. Incremental
  and model-free for code; a run that deleted code legitimately rebuilds smaller
  (`--force`).
- **Then check the graph against the docs** — the cheap half of the divergence sweep
  (`graphify god-nodes`; any doc naming a module the graph no longer has). A hub no
  doc names, or an edge the docs deny, is either a leak in the code or a lie in the
  docs; a doc naming a node that no longer exists is a stale ledger row found
  mechanically. Doc-side findings are fixed here; **absences go to stage 10's ladder
  walk as REQ rows** ([`audit.md`](audit.md)).
- **Docs living in another repository** are outward: propose the edit, get an
  explicit go, then open a PR there. No go → the exact edit goes in the carry-over
  ledger.
