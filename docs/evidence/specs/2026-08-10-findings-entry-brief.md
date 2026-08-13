# Brief — findings-shaped work gets an entry (B-047)

Run opened 2026-08-10 at `9f67dcd` (v1.38.0). Board: **23 open**. Verification ledger:
**99 rows, 99 at `never`**. Model: Opus 5 (1M), confirmed at preflight, used throughout.

## The request, in one line

Findings-shaped work — an audit, a bug hunt, a production check, a PR review — has no
entry into this skill, and the exclusion clause points away from it while `audit.md:350`
says an audit may be the whole task.

## Source ledger (the phase-1 harvest, written BEFORE the grill)

| Source | What it says about this task | Fresh? | Authority |
|---|---|---|---|
| the code | description 956/1024, 68 chars headroom | `9f67dcd` | fact |
| the code graph | this surface is owned by **v1.9.0 `default-routing-adoption`** | 0 commits behind | reach |
| `…default-routing-adoption-design.md:§3` | **locked:** default-on widens *inside* the boundary, never through it; the exclusions are the same three the `NOTRIG` evals encode, **and the two must not drift** | 2026-08-03 | decision |
| `…default-routing-adoption-acceptance.md:34` | `REQ-003 vocabulary + boundary` marked **verified** | 2026-08-03 | claim |
| `references/audit.md:350` | an audit may be **the whole task**; stages 3–5 produce findings instead of a feature | current | doctrine |
| `retro.md` standing instructions | **R-005** (independent reader on any widened check) · **R-006** (a finding closes when *behaviour* changes) | in force | binding |
| retro archive, queried on *routing/trigger* | v1.9.0 plus three propagation entries | — | context |
| `docs/superpowers/backlog.md` | `B-001` (description budget), `B-002` (zero blind eval runs), `B-046`, `B-051` | current | state |
| `2026-08-10-routing-taxonomy.md` | the measurement this row came from | today | measurement |
| wiki (`obsidian-wiki`) | `projects/task-pipeline/` synced at `cf501f2`; no page owns routing | 1 behind | context |

**Found by the harvest, before the first question — two seam defects:**

1. **`перевести` was locked in the v1.9.0 verb list and never shipped.** It exists in
   exactly one place in the repository: the design that locked it. `git log -S` over
   `SKILL.md` returns nothing — it never landed.
2. **`REQ-003` was accepted as `verified` anyway.** The evidence recorded was the clause
   *shape* — `Not for:` present, both opt-out phrases, 1013/1024 chars, guard probed —
   which cannot see a missing member of the list the REQ locked. An L1→L2 absence that
   passed an L5 check, which is the seam `audit.md` exists to walk.

## Decisions taken at the grill

- **D-1 — the boundary is restated, no new mode.** The criterion becomes *what the
  request ends in*: an **answer** → not this skill; a **finding that lands in the
  repository** → this skill. Rejected: a third no-task mode `audit`, because
  `exposure.md` defines modes as writing nothing while `audit.md:350` defines an audit
  as stages 3–5 that write findings — one word, two mechanisms.
- **D-2 — the budget is paid by cutting mechanism prose.** `— gated stages whose
  doctrine ships inside this skill (no required companions)` (−79) and ` or reading`
  (−11) fund the findings clause (+121). Result **987/1024, 37 spare**. The stage list
  is not touched; invariant 2 holds.
- **D-3 — B-047 closes on an observed routing shift, not on a diff.** Fresh agents, given
  only the competing skill descriptions and one user sentence, name the skill they would
  use. Measured **before** the edit and **after**. No shift → the row stays open and the
  run says so. This is R-006 applied to the run that wrote R-006's own subject.
- **D-4 — the choice set for the measurement** is the installed family (`task-pipeline`,
  `super-ux`, `copywriting`, `sheleg-design`, `make-skill`, `agent-sync`,
  `seo-aeo-audit`) plus *none of these*. Stated rather than asked: a measurement offering
  one option tests agreement, not routing.

## Requirements (frozen — adding is free, removing needs the operator)

| id | Requirement | Verified by |
|---|---|---|
| REQ-001 | The description's boundary is restated as *answer vs finding that lands in the repo*; `reading` leaves the exclusion clause | guard: description ≤1024 **and** carries both halves of the criterion |
| REQ-002 | The four findings classes are named on **every** surface that carries the boundary — `SKILL.md`, `README.md`, `templates/routing-rule.md`, `cursor/rules/task-pipeline.mdc` | guard: the class list is discovered, not listed, and compared across surfaces |
| REQ-003 | The exclusion clause and the `NOTRIG` evals still encode the same exclusions — v1.9.0's no-drift rule survives the rewording | guard tying the clause to the `NOTRIG` cases |
| REQ-004 | `перевести` is restored to the verb list, and a guard asserts every verb the v1.9.0 design locked is present | guard over the locked list |
| REQ-005 | Routing is measured on fresh agents before and after; both runs recorded with their prompts | the measurement artifact + `evals/RESULTS.md` |
| REQ-006 | An eval case exists for each named findings class | guard: every class named in the description has a case |
| REQ-007 | The close-out states, per finding, whether **behaviour** or only **reporting** changed (R-006) | the acceptance table carries the field |
| REQ-008 | An independent reader reads every widened check before merge (R-005); its verdict is recorded, `NO READER` printed if absent | stage 7's reader output |

## Autonomy sweep (stages 1→10 read this instead of asking)

- **Branch + PR**, not `main`: this changes a public contract. Version **v1.39.0** (minor
  — new routing capability).
- Test `npm test`; full proof `npm run test:all`. Every new guard needs its negative
  self-test in `.github/workflows/validate.yml`, and `MIN_EXPECTED` moves in the same
  change.
- Corrupt files in **python, never `sed -i`**.
- Deploy = tag `vX.Y.Z` → release workflow; CI verdict **read**, never assumed.
- Stage 9: docs, wiki, **and the graph** (1 commit behind at open).
- No visual surface → `sheleg-design` not required; `super-ux` COPY track not triggered
  (this text is developer-facing doctrine, not product copy).

## Carry-over at open

| # | Item | Why not in this run | Home |
|---|---|---|---|
| 1 | The operator's global `~/.claude/CLAUDE.md` carries its own copy of the boundary | outside this repository — an edit to the operator's machine config needs their explicit go | asked at stage 9 |
| 2 | `B-048` (decide-don't-build), `B-049` (logs as a source), `B-050` (PR as a request) | named by the same taxonomy, different fixes; this run is the findings class only | board |
| 3 | `B-002` blind runs on three models | this run measures **one** model with fresh contexts, which is not a blind multi-model run | board |
