# Plan — default-on routing + the adoption track

**Spec:** [`../specs/2026-08-03-default-routing-adoption-design.md`](../specs/2026-08-03-default-routing-adoption-design.md)
**Global constraints (verbatim from the spec):** description ≤1024 chars, capability
before `Use when`; every reference >100 lines carries a `## Contents` list matching
its headings; every section-qualified citation names a real section; living-document
counts are computed; a new guard needs a negative self-test watched failing.

## Execution order

| Group | Tasks | Runs after |
|---|---|---|
| A | 1, 2 | — |
| B | 3, 4, 5 | A |
| C | 6, 7 | B |
| D | 8, 9 | C |

No two tasks in a group write the same file.

### Task 1 — ratchet floor kinds · Implements: REQ-002
**Files:** `plugins/task-pipeline/skills/task-pipeline/templates/docgate.sh`
**DoD:** the floor block names each kind (`PROP_FLOOR` id threshold, `RESIDUE_FLOOR`
count) and its adoption value; both seeded shapes still exit 0 (`npm test`).

### Task 2 — the adoption doctrine · Implements: REQ-001
**Files:** `references/adoption.md` (new), `SKILL.md` (one reference line)
**DoD:** every section of spec §1 present, Contents matches headings, ≥1500 B,
reachable from `SKILL.md`, cites the floors from Task 1.

### Task 3 — vocabulary + boundary · Implements: REQ-003
**Files:** `SKILL.md` (frontmatter only)
**DoD:** work verbs RU+EN present, exclusion clause verbatim per spec §3, ≤1024,
`npm test` green.

### Task 4 — evals match the behaviour · Implements: REQ-004
**Files:** `evals/task-pipeline.evals.json`
**DoD:** exclusions unchanged, one new `should_trigger` row for repo-changing work
with no magic words; `python3 evals/run.py` exits 0 with five categories.

### Task 5 — version floor · Implements: REQ-007
**Files:** `references/companion-skills.md`
**DoD:** the agent-sync row states `≥ 1.3.0` and why.

### Task 6 — agent-sync binding patch · Implements: REQ-006
**Files:** `~/DATA/agent-sync/plugins/agent-sync/skills/agent-sync/references/pipeline-binding.md`,
`~/DATA/agent-sync/agent-sync.example.json`
**DoD:** a script validates the example against `pipeline.schema.json` and exits 0;
`guardedFiles` gains DOCMAP + retro; stage-9 doctrine corrected; gates extend.

### Task 7 — the routing rule · Implements: REQ-005
**Files:** `~/.claude/CLAUDE.md`
**DoD:** boundary, exclusions and both escape phrases present; states why the rule
lives there and not in the description.

### Task 8 — dogfood this repository · Implements: REQ-008
**Files:** `docs/DOCMAP.md` (new), `scripts/check-docs.sh` (new)
**DoD:** `bash scripts/check-docs.sh` exits 0 here, floors baselined at today.

### Task 9 — guards, negative tests, release · Implements: REQ-001, REQ-003, REQ-009
**Files:** `test/validate.py`, `.github/workflows/validate.yml`, `test/negatives.py`,
`README.md`, `CHANGELOG.md`, `SKILL-CARD.md`, `evals/RESULTS.md`, four manifests
**DoD:** two new guards each proven by a negative self-test watched failing;
`npm run test:all` green; version bumped; this run recorded in `RESULTS.md`.
