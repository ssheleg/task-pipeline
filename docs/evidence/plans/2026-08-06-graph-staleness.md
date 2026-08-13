# Plan — the graph's ledger row states a measured lag

Design: [`../specs/2026-08-06-graph-staleness-design.md`](../specs/2026-08-06-graph-staleness-design.md)
Brief: [`../specs/2026-08-06-graph-staleness-brief.md`](../specs/2026-08-06-graph-staleness-brief.md)

Executed inline (nine small tasks over prose and one Python file, ordered by
dependency — doctrine first, then the guards that read it, then the negatives that
prove the guards). No parallel group, so no shared-file conflict is possible.

| # | Task | Implements | Files owned | DoD |
|---|---|---|---|---|
| T1 | The measured-lag rule in the doctrine's home: three states, three commands, the row format, the zero case, and the promotion trigger | REQ-001 REQ-002 | `references/knowledge-graph.md` | the three command literals and all three state names present; `npm test` green |
| T2 | The ledger definition cites the rule; the seeded template row shows the measured form | REQ-003 REQ-004 | `references/knowledge-sources.md`, `templates/brief.md` | neither file restates the commands; the template's graph row no longer reads a bare `built YYYY-MM-DD` |
| T3 | Stage 0 names it in both halves — the agent-facing section and the config gate | REQ-005 REQ-006 | `references/stages.md`, `pipeline.example.json` | both mention the measured lag; existing gate-type guard still green |
| T4 | Extend the code-graph guard to stage 0 (R-003 sibling sweep), plus the doctrine-content guards | REQ-007 | `test/validate.py` | one guard covers stages 0 and 9; no second guard for the same class; all `fail(` above the verdict block |
| T5 | One negative self-test per new guard, each **proved plant-first** (R-001); floor raised | REQ-008 | `.github/workflows/validate.yml`, `test/negatives.py` | every plant asserted to have landed in the parsed text before the guard is trusted; `npm run test:negatives` green at the new floor |
| T6 | The public surfaces state the measured form; the Cursor rule stays self-contained | REQ-009 | `README.md`, `cursor/rules/task-pipeline.mdc` | no live surface still says "with its build date"; zero relative links in the rule |
| T7 | The release record and the four-way version sync | REQ-010 | `CHANGELOG.md`, `package.json`, `.claude-plugin/marketplace.json`, `plugins/task-pipeline/.claude-plugin/plugin.json` | four-way sync guard green; the CHANGELOG section reads as *what changed and why* |
| T8 | The workflow decision gets a home; the invariant cites a printed literal | REQ-011 REQ-012 | `references/portability.md`, `CONTRIBUTING.md` | the invariant quotes a literal `test/validate.py` actually prints |
| T9 | Ship it | REQ-013 | — (git, CI) | PR merged, tag `v1.15.0`, `release.yml` green, `npm view task-pipeline-skill version` == 1.15.0, local copies updated |

**Set equality check (stage-4 gate):** brief REQ ids = {001…013}; union of
`Implements:` above = {001…013}. Difference: **∅**.

## Self-review

- Every REQ in the brief maps to exactly one task; no task invents a requirement.
- No placeholders: every task names its real files and a DoD a check can read.
- File ownership is disjoint by construction — the tasks run in sequence.
- Names and paths resolve: all nine `Files owned` entries exist in the tree today
  except none — verified before this plan was committed.
- **Computed, not asserted — and the estimate was wrong, which is why it is measured
  at the end rather than trusted from the start:** tasks **9** · REQ rows covered
  **13** · files touched **22** (planned 13; the gap is this run's own artifacts plus
  three surfaces the repo's drift guard surfaced) · guards **95 → 102** (planned 97 —
  the four stage-0/doctrine checks and the template check were counted as two) ·
  negatives floor **95 → 102**.
- **Where the correction came from:** not from re-reading the plan. `npm run test:all`
  failed on `SKILL-CARD.md` and `evals/RESULTS.md` still saying *95 structural
  guards* — invariant 13 catching an estimate that had been written down as a fact.
