# Task brief — a CI run is checked by reading it, not by assuming it

Status: **stage 0 locked** · branch `feat/ci-run-verified`

## Knowledge sources (the phase-1 harvest — written BEFORE the first question)

| Source | What it says about this task | Fresh? | Authority | Stale after this run? |
|---|---|---|---|---|
| `graphify-out/graph.json` | reach across the skill's doctrine files | built `3944593` — 13 commits / 0d behind HEAD, signal: built_at_commit (exact) — ⚠ not trusted for reach until refreshed | index | **yes — refresh at stage 9** |
| **the incident, 2026-08-06** | `validate` was **completed/failure** on `0d32d85` (a push to `main`) and on the `v1.15.0` tag. Nothing in the pipeline required anyone to look; it surfaced only because the run happened to poll the API | today | evidence | no |
| `references/conventions.md` → *Post-deploy logs* | the whole of today's rule: *"CI: the workflow run."* — a place to look, with no method and no verdict | current | doctrine | **yes — this run changes it** |
| `pipeline.example.json` → `release.verify[0]` | *"CI green on the tagged commit"* — a claim with no way to earn it | current | contract | **yes** |
| `references/stages.md` § 7 GATE | requires lint + **suite green**, which is the *local* run; says nothing about the CI run the push triggers | current | gate | **yes** |
| `references/stages.md` § 8 GATE | *"clean boot confirmed, or an honest degradation report — never silent success"* — the right shape, applied to deploy logs rather than to the CI run | current | gate | **yes** |
| `references/gates.md` → *False success* | *an actor's own reply is not evidence about the world*; the test — **what does it print when it did not look?** | current (v1.14.0) | doctrine | no — cited, not restated |
| `references/gates.md` → *Progressive arming* | `ok` / `dormant` / `skip` / `ERR`: a mechanism with nothing to look at must say so distinctly | current | doctrine | no |
| `references/knowledge-graph.md` → *Measure the lag* | last night's precedent for this exact shape: name the commands, name the states, never let silence read as success | current (v1.15.0) | doctrine | no — the pattern to follow |
| `docs/superpowers/retro.md` → standing instructions | **R-001** prove the plant landed · **R-002** re-verify the whole batch on any error · **R-003** sweep siblings · **R-004** a gate's exit code must gate the next command — all four bind this run | read in full 2026-08-06 | binding | stamp at stage 10 |
| `CLAUDE.md` | `npm test` / `npm run test:all`; four-way version sync; every new guard needs a negative self-test | current | convention | no |
| the `gh` token expiry, 2026-08-06 | `gh` returned 401 mid-run after a successful call, and `gh auth status` reported a **stale cached** verdict while `gh api user` succeeded | today | evidence | no |

**Why the shape matters.** The red run was not a false alarm — it was the repository's
own `Every v* tag must be contained in main` guard, firing correctly on a tag that was
not yet an ancestor of `main`. The guard worked. **Nothing obliged anyone to read it**,
and a guard nobody reads is the fail-open hook with extra steps.

## Scope

**In.** A named method for establishing a CI run's verdict — read the run's
**conclusion**, and on failure read the **failing log** and quote the failing step —
bound at the gates where this run pushes.

**Out.** Choosing a CI provider, or requiring one. Blocking on a red run (stage 8's
existing shape already allows an honest degradation report). Any change to what the
workflows themselves check.

## Decisions locked

| # | Decision | Why | Rejected alternative |
|---|---|---|---|
| D-1 | The method lives in `conventions.md` (one home) and is **cited** at the gates | `documentation.md` canon 3: one home per fact. The gates say *what must be true*; conventions say *how this host answers it* | restating the commands at stages 7, 8 and 9 — three copies to drift |
| D-2 | Three states, mirroring *Measure the lag*: **concluded** / **in progress** (wait, never assume) / **no run found** (say so out loud) | `gates.md` → *False success*: the absence of a run must not read like a pass. A repository with no CI is a legitimate, recorded state, not a green one | one state, reporting only failures |
| D-3 | On a non-success conclusion, the **failing step's log is read and quoted** — the verdict alone is not the finding | tonight's red was explained only by its log, which named the guard, the tag and the fix. A bare "CI failed" would have sent the next reader guessing | reporting the conclusion alone |
| D-4 | Both an authenticated (`gh`) and an unauthenticated (`curl` on the check-runs API) path are named | `gh`'s token expired mid-run tonight, and `gh auth status` answered from a **stale cache** while the API worked. A method with one path is a method that stops at the first credential problem | `gh` only |
| D-5 | It **reports**, it does not block | stage 8's gate is already *"clean boot, or an honest degradation report — never silent success"*, and that shape is right here too | failing the gate on any red run |
| D-6 | Bound at stages **7, 8 and 9** — every stage of this flow that pushes | the incident hit at the merge (7) and again at the docs push (9); binding only stage 8 would have missed both | stage 8 alone |
| D-7 | Version **v1.16.0**, released end to end | new doctrine + new gate criteria + new guards | patch |

## Requirements — the REQ spine (frozen)

| id | Requirement | Verified by |
|---|---|---|
| REQ-001 | `conventions.md` states the method: the commands for conclusion and failing log, both the `gh` and the unauthenticated path | guard asserts the command literals are present |
| REQ-002 | Three states named — concluded / in progress / no run found — so silence never reads as green | guard asserts all three are named |
| REQ-003 | `stages.md` § 7, § 8 and § 9 gates require the run's verdict to be **read and quoted**, citing `conventions.md` rather than restating it | guard: each of the three sections names the rule; none carries a second copy of the commands |
| REQ-004 | `pipeline.example.json`'s stage-8 gate check and `release.verify` require it | guard, config half |
| REQ-005 | Every new guard has a negative self-test, each proved plant-first (R-001); the floor rises | `npm run test:negatives` green at the new floor |
| REQ-006 | `README.md` and the Cursor rule state it; the rule stays self-contained | link guard + grep |
| REQ-007 | `CHANGELOG.md` v1.16.0 + four-way version sync + `SKILL-CARD.md` | four-way sync guard |
| REQ-008 | `CONTRIBUTING.md` invariant citing a literal the validator prints; `portability.md` homes the decision | invariant-citation guard |
| REQ-009 | Released: tag `v1.16.0`, `release.yml` green, registry serves it, **and this run's own pushes verified by the new method** | `npm view task-pipeline-skill version` == 1.16.0; the run conclusions quoted in the acceptance |

## Autonomy

| Stage | Answer |
|---|---|
| all | one model, the run's confirmed tier |
| 1 | no external contract locked from recall; `gh`'s JSON fields and the check-runs API are verified live in this run |
| 2–4 | D-1…D-7 are the approved design |
| 5 | branch `feat/ci-run-verified`, never `main` |
| 6 | `npm test`, `npm run test:all`; the validator is the lint |
| 7 | **authorized: full run to tag `v1.16.0` and release** |
| 8 | the release workflow's own smoke test, then `npm view` — **and the new method applied to this run's own pushes** |
| 9 | CHANGELOG, README, CONTRIBUTING, artifacts.md; wiki; `/graphify . --update` |
| 10 | no user-facing surface — no super-ux track, no Figma; recorded, not skipped |

## Done-criteria

Every REQ verified with evidence, `npm run test:all` green, PR merged, `v1.16.0` on
npm, and the acceptance quoting the conclusion of every CI run this work triggered.

## Open assumptions / risks

- **The method is prose an agent runs.** Rung 2 on the enforcement ladder, like the
  measured lag. Promotion trigger written into the doctrine: promote to a script the
  first time a run is observed closing a stage with an unread CI verdict.
- **`gh auth status` lies from cache.** Tonight it reported an invalid token while
  `gh api user` succeeded. The doctrine names the live call, not the status command.
