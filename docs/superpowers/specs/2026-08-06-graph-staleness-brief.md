# Task brief — make code-graph staleness visible at stage 0

Status: **stage 0, in the grill** · branch `feat/graph-staleness-visible`

## Knowledge sources (the phase-1 harvest — written BEFORE the first question)

| Source | What it says about this task | Fresh? | Authority | Stale after this run? |
|---|---|---|---|---|
| `graphify-out/graph.json` | reach across 95 source files; carries `built_at_commit` at top level | built `3944593` — **0 commits / 0 days behind HEAD, signal: built_at_commit (exact)** | index | **yes — refresh at stage 9** |
| `references/knowledge-graph.md:81` | "Record it in the ledger **with its build date** … whether stage 9 owes it a refresh" | current | doctrine | **yes — this run changes it** |
| `references/knowledge-graph.md:163` | rationalization row: *"The graph is probably stale" → then it has a build date and you can say so. Stale-and-dated is a finding; stale-and-unknown is what you get by not building one.* | current | doctrine | **yes** |
| `references/knowledge-sources.md:97` | "Record the row **with the graph's build date**, because a graph is a source" | current | doctrine | **yes** |
| `references/knowledge-sources.md:149` | the source-ledger table shape (4 columns) that the brief template extends to 5 | current | doctrine | maybe |
| `references/stages.md:96` | stage-0 harvest: "the graph's row carries its build date" | current | doctrine | **yes** |
| `references/stages.md:100` | stage-0 **GATE (manual)**: "the source ledger is written…" | current | gate | **yes** |
| `templates/brief.md:34,69` | the seeded ledger row: `built YYYY-MM-DD` \| index \| **yes — refresh at stage 9** | current | template | **yes** |
| `README.md:241` | "in the source ledger **with its build date**, because a graph goes stale exactly like…" | current | public doc | **yes** |
| `cursor/rules/task-pipeline.mdc:89` | same sentence, self-contained (no relative links allowed) | current | portable rule | **yes** |
| `CHANGELOG.md:913` (v1.5.0) | the historical statement of the same rule | 2026-08-01 | history | **no — history is not back-filled** |
| `references/gates.md` → *False success* | *an actor's own reply is not evidence about the world*; the test: **what does it print when it did not look?** | current (v1.14.0) | doctrine | no — cited, not restated |
| `references/learned.md` rule 8 | **compute, never restate** — the reason a build date typed by hand is not the deliverable | current | doctrine | no |
| `references/gates.md` → *Progressive arming* | states `ok` / `dormant` / `skip` / `ERR`; a mechanism that cannot look must say so distinctly | current | doctrine | no |
| `docs/superpowers/retro.md` → standing instructions | **R-001** prove the plant landed · **R-002** re-verify the whole batch on any error · **R-003** run a fixed defect's definition against its siblings — all three bind this run | read in full 2026-08-06 | binding | stamp at stage 10 |
| `test/validate.py:1405–1426` | the existing code-graph guard: doctrine shipping ⇒ stage 9 must name it in **both** the config gate and `stages.md` | current | guard | **yes — the sibling to extend (R-003)** |
| `CLAUDE.md` | `npm test` / `npm run test:all`; four-way version sync; the stage list on nine surfaces; corrupt fixtures in python, never `sed -i` | current | convention | no |
| `CONTRIBUTING.md` → invariants | every new guard needs a matching negative self-test in `.github/workflows/validate.yml` | current | convention | **yes — one added** |
| wiki: `projects/task-pipeline/concepts/code-graph-as-harvested-source` | the graph as harvest source #2; three close-out artifacts; divergence as the fourth audit axis | synced 2026-08-05 | context | **yes — update at stage 9** |
| wiki: `projects/task-pipeline/concepts/false-success` | the class this REQ set is an instance of | synced 2026-08-05 | context | maybe |
| `docs/superpowers/specs/2026-08-04-run-continuity-carryover.md:15,20` | the precedent: a stale graph recorded as a carry-over row with its reason, closed later | 2026-08-04 | precedent | no |

**The finding that started this run, recorded as a source in its own right:**
`docs/superpowers/specs/` holds brief/carry-over/acceptance artifacts for
`run-continuity` (v1.11.0), `artifact-hygiene` (v1.12.0) and `spec-plan-quality`
(v1.13.0) — and **none for v1.14.0 or v1.14.1**. Those two releases did not run
through the pipeline, so stage 9 never opened and the graph sat two releases stale
while `graphify-out/graph.json` still reported a build date that read as fresh.

## Scope

**In.** The stage-0 source-ledger row for the code graph states a **measured** lag
(commits and days behind `HEAD`), **names the signal it measured with**, and
carries an explicit distrust marker until the graph is refreshed.

**Out.** The refresh cadence (stage 9 stays unconditional — untouched). Any
`always | major | manual` mode in `pipeline.schema.json` — considered and rejected
with the operator at intake, reason recorded below. Blocking a run on a stale
graph.

## Decisions locked

| # | Decision | Why | Rejected alternative |
|---|---|---|---|
| D-1 | Cadence doctrine is **not** touched; stage 9 stays unconditional | the rule was already right — what failed is that a run outside the pipeline is bound by nothing | a `graph_refresh: always\|major\|manual` field in the schema: `major` manufactures precisely the state the doctrine warns about — a graph confidently wrong between releases, which the next harvest reads first |
| D-2 | The lag is **computed**, never typed | `learned.md` rule 8 (*compute, never restate*); a hand-typed build date is the assertion this run exists to replace | leaving the row as `built YYYY-MM-DD` |
| D-3 | No staleness threshold | `continuity.md`'s precedent: an unmeasurable threshold becomes unconditional doctrine, not config. Any lag > 0 is stated as a number and marked | "mark it only past N commits / N days" |
| D-4 | Absent or unresolvable `built_at_commit` degrades to `mtime` and **says which signal it used** | `gates.md` → *False success*: silence must not be indistinguishable from a fresh graph. Three distinct states, mirroring *Progressive arming* | printing nothing when the stamp is missing |
| D-5 | The measurement is **doctrine naming the exact git commands**, not a shipped script | stage 0 runs before anything is installed in a host project, and the pipeline's promise there is zero dependencies; the numbers still come from git rather than judgement, which is what D-2 asks for | `templates/graph-staleness.sh` — a fourth seeded file with its own contract to `npm test`, which must be seeded into the project before it can run at the one stage that precedes seeding |
| D-6 | Stage 0 must name the measurement in **both** places — `pipeline.example.json` gate check and `stages.md`'s stage-0 section — and the existing guard is **extended** to cover stage 0, not duplicated | settled by the sources, not asked: `test/validate.py:1405` already enforces exactly this for stage 9, with the comment *"the file reads as law and the run never does it"*. **R-003** requires running a fixed defect's definition against its siblings; stage 0 is stage 9's sibling here | a second, parallel guard — the duplicate `audit.md` warns about |
| D-7 | Version **v1.15.0** (minor), released end to end | new doctrine + new gate criteria + new guards is a feature, not a fix | patch |

## Requirements — the REQ spine (frozen; adding is free, removing needs a go)

| id | Requirement | Verified by |
|---|---|---|
| REQ-001 | `knowledge-graph.md` states the measured-lag rule: the two exact git commands, and the row format that carries commits + days + the signal | guard asserts both command literals and the row shape are present |
| REQ-002 | Three distinct signal states are named — `built_at_commit` (exact), `mtime` (approximate, stamp absent), and stamp-present-but-unresolvable — so silence is never indistinguishable from a fresh graph | guard asserts all three states are named in `knowledge-graph.md` |
| REQ-003 | `knowledge-sources.md` says the graph row carries the measured lag, **citing** `knowledge-graph.md` rather than restating the commands | guard: the file names the lag rule and does not carry a second copy of the commands |
| REQ-004 | `templates/brief.md`'s seeded ledger row shows the measured form, not a bare `built YYYY-MM-DD` | guard rejects the bare-date form in the template's graph row |
| REQ-005 | `stages.md` stage-0 harvest line **and** its `GATE (manual)` criteria require the measured row | guard (the stage-9 guard extended to stage 0) |
| REQ-006 | `pipeline.example.json` stage-0 `gate.check` requires the measured row | same guard, config half |
| REQ-007 | The existing code-graph guard at `test/validate.py:1405` is **extended** to stage 0 in both halves — R-003's sibling sweep, not a parallel copy | the guard's own source; no second guard added for the same class |
| REQ-008 | Every new guard has a negative self-test in `.github/workflows/validate.yml`, each **proved plant-first** per R-001, and the negatives floor is raised | `npm run test:negatives` green with the raised floor; each plant asserted to have landed before the guard is trusted |
| REQ-009 | `README.md` and `cursor/rules/task-pipeline.mdc` state the measured form; the Cursor rule stays self-contained (zero relative links) | existing link guard + grep for the superseded "build date" phrasing |
| REQ-010 | `CHANGELOG.md` gains a v1.15.0 section written as *what changed and why*; version synced across `package.json`, `marketplace.json`, `plugin.json` and the CHANGELOG heading | existing four-way version-sync guard |
| REQ-011 | `references/portability.md`'s manifest homes this workflow decision | manifest guard + review |
| REQ-012 | `CONTRIBUTING.md` gains the invariant, citing a literal the validator actually prints | existing invariant-citation guard |
| REQ-013 | Released: tag `v1.15.0`, `release.yml` green, the registry serves it, local installs updated | `npm view task-pipeline-skill version` == 1.15.0 and the launcher update run |

## Autonomy (the sweep — stages 1→10 read this instead of asking)

| Stage | Question it would otherwise stop on | Answer |
|---|---|---|
| all | model | the run's confirmed tier, one model, no hardcoded id |
| 1 | external docs to ground | none locked from recall: the only external contracts are `git` CLI and graphify's `graph.json` shape, and **D-4 already forbids assuming the stamp exists** |
| 2–4 | design/spec/plan approval | this brief's decisions D-1…D-7 stand as the approved design; a change to any of them re-opens stage 2 |
| 5 | branch policy | `feat/graph-staleness-visible`, already created; work lands there, never on `main` |
| 6 | test + lint commands | `npm test` (= `python3 test/validate.py`), `npm run test:negatives`, `npm run test:all`; the validator is the lint |
| 7 | deploy target and authorization | **authorized: full run to tag `v1.15.0` and release.** PR merged, tag pushed only with `npm test` green on the tagged commit, `release.yml` publishes |
| 8 | health check | the release workflow's own `npx` smoke test, then `npm view task-pipeline-skill version` |
| 9 | docs/wiki/graph targets | `CHANGELOG`, `README`, `CONTRIBUTING`, `references/artifacts.md`; wiki `projects/task-pipeline/`; `/graphify . --update` |
| 10 | UI verdict | **no user-facing surface** — no super-ux track, no Figma; recorded rather than skipped |

## Done-criteria

Every REQ verified with evidence, `npm run test:all` green, PR merged into `main`,
`v1.15.0` on npm, the graph refreshed and the retro stamped.

## Open assumptions / risks

- **The staleness row is prose an agent writes.** D-5 accepts this: the numbers come
  from git, but nothing stops an agent from omitting the row entirely except the
  stage-0 gate criterion. That is rung 2 on the enforcement ladder, and the
  retire-when is written into the doctrine: promote to a script when a run is
  observed passing stage 0 with an unmeasured graph row.
- **`built_at_commit` is written by graphify only when the caller passes it.** The
  three-state design (D-4) is the mitigation, not a workaround — and it is the
  reason the states must be named in the doctrine rather than left to judgement.

