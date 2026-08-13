# Acceptance — `audit-followup` · M1 `truth-restore`

**Shipped:** `v1.23.1` · commit `68b4428` · npm `task-pipeline-skill@1.23.1`
**Gates:** `npm run test:all` exit **0** — `PASS: task-pipeline structure valid`,
`PASS: all 120 guards provably reject their planted defect`, measured on the commit the
tag points at, unpiped.

## Ladder walk — run before this table was written

Scope: the six REQ rows of M1, each walked L0→L7 bottom-up.

| Seam | Finding | Became |
|---|---|---|
| L1→L2 | The version-sync invariant is stated on four surfaces as *"four-way"* while `test/validate.py` enforces five. The decision (which surfaces must agree) never reached the documents describing it | fixed in this change across `CLAUDE.md`, `CONTRIBUTING.md`, `README.md`, `docs/DOCMAP.md` |
| L2→L3 | Rule 21 changed the retro's act order in `references/retrospective.md`; its contract — what stage 10's gate *says* — was not moved. Eight sibling surfaces still state the deadlocked order | **REQ-013**, new row, module **M8**, priority 2 |
| L6→L7 | `evals/RESULTS.md` had no statement connecting the blind/self-observed split to canon 5, though it is the same law. Surfaced by the graph↔docs divergence check, not by a reader | fixed in this change |
| L0→L1 | REQ-011: the loop mode was authorised in conversation and recorded nowhere. No decision existed for a config the run depended on | `pipeline.json` written, mode recorded with its scope limits |

Two passes ran. **New findings: 4 · self-inflicted by the previous pass: 0.** The axis is
not exhausted; it was rotated once anyway, from *reading the documents* to *the graph
against the documents*, which is what produced the L6→L7 row.

## REQ coverage

| ID | Status | Evidence |
|---|---|---|
| REQ-001 | `verified` | `grep -rE "(fifteen\|…) rules" --include='*.md'` over the tree returns nothing outside `CHANGELOG.md`; `README.md:811` and `SKILL.md:337` quoted after the edit |
| REQ-002 | `verified` | computed set difference: table rules `1..21`, cited in the binding map `1..21`, **MISSING: none**. Two mis-aimed citations in the first attempt were rejected by the citation guard and corrected |
| REQ-003 | `verified` | `python3 evals/run.py` prints `recorded runs: 1`; the document's ratchet now states `1`, and splits it into `0` blind |
| REQ-004 | `verified` | `docs/DOCMAP.md` ratchet table names homes and commands, no values; `grep -n "version surface" docs/DOCMAP.md` quoted |
| REQ-011 | `verified` | `jsonschema.validate(pipeline.json, pipeline.schema.json)` → `VALID`; `mode: interval`, `interval: 15m`, eleven stages, gate types printed |
| REQ-006 | `verified` | `built_at_commit 68b4428` == `git rev-parse HEAD`; `git rev-list --count <built>..HEAD` → **0**. Graph rebuilt from 27-commits-stale to current: **840 nodes, 1128 edges, 101 communities**, health check `OK` — 0 dangling, 0 missing, 0 self-loop, 0 collapsed |
| REQ-013 | `deferred` | added mid-run by R-003's sweep; operator-visible in the brief and this table; tracked as module **M8** at priority 2 |

**7 rows · 6 `verified` · 1 `deferred` · 0 `unknown`.**

## What the operator should look at

**The abstention this run could not close.** Carry-over row 6: the skill's behavioural
evidence remains **one self-observed run on one model, zero blind runs on zero of three**.
Every gate above is structural. Nothing in M1–M8 changes that number, and the honest
place to say so is here, beside the green.

**A slip worth seeing.** Fixing the "one rule, two documents" class, the run edited the
wrong copy — `~/CLAUDE.md` instead of `./CLAUDE.md`. It failed loudly (no match) rather
than silently, and the real home was then located by grepping both. Recorded in the retro.

## Gate verdict

```
GATE 10 acceptance (M1): PASS — 6/7 REQ verified, 1 deferred to M8
  carry-over: 6 rows · 0 unresolved · 1 resolved this module (row 5, graphify skill)
  guards: 120 provably rejecting a planted defect · graph lag: 0 commits
  abstained: 1 (REQ-013 deferred) · unmeasured: behavioural evidence, 0 blind runs
```
