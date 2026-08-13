# Brief — audit-followup

**Run:** `2026-08-08-audit-followup` · **Stage 0 locked:** 2026-08-08
**Opening commit:** `f2cac02` (v1.23.0)

## The task, in one line

Close the six findings of the 2026-08-08 hallucination-mitigation audit, plus one
operator-added capability, as a **program**: stages 0–2 once, stages 3→10 per
module, one module per loop iteration.

## Where the work came from

A review of *A Concise Review of Hallucinations in LLMs and their Mitigation*
(arXiv:2512.02527v1) was mapped against this skill. The paper's applicable levers —
knowledge integration, formal-methods-guided prompting, post-processing that blocks
unproven assertions, self-contradiction and self-consistency detection, uncertain
refusal as a measured category, detection during generation rather than after — are
almost all already present as doctrine. **The findings are not doctrinal gaps; they
are failures of this repository to apply its own doctrine to itself**, plus three
genuine imports the paper does supply.

## Knowledge sources (harvest, phase 1)

| Source | What it says about this task | Fresh? | Authority |
|---|---|---|---|
| `test/validate.py` | 120 guards; the "computed, never restated" guard (`validate.py:329-341`) matches only the literal pattern `N guards` | current | **decides** |
| `graphify-out/graph.json` | `built_at_commit 3944593` = v1.14.1; `git rev-list --count 3944593..HEAD` → **27** | ⚠ **stale** | not trusted for reach until refreshed |
| `CLAUDE.md` (project) | `npm test` is the gate; doc/doctrine fixes land on `main`, stage-list/gate/public-contract changes go on a branch through a PR; never tag before `npm test` is green on the tagged commit | current | convention |
| `~/.claude/CLAUDE.md` (global) | after any release, update every local copy on this machine as Definition of Done | current | convention |
| `docs/DOCMAP.md` | registers, SSOT table, propagation matrix, gates; matrix row *"a number stated in a living document → recompute it"* already exists | ⚠ **its own ratchets are stale** — claims "2 of a hard cap of 10" standing instructions, `retro.md` has 4 | register |
| `docs/superpowers/retro.md` | **R-001, R-002, R-003, R-004 read in full — all four bind this run** (see below). Last run stamp `2026-08-06 graph-staleness 2ce6ecc`; seven releases since carry no stamp | binding | binding |
| `evals/RESULTS.md` + `evals/run.py` | document states "has not been executed" / "Dated runs recorded 0"; `run.py:121` computes `recorded runs: 1` | ⚠ **self-contradiction** | evidence |
| `references/learned.md` | 21 rules in the table; `README.md:811` and `SKILL.md:337` say "fifteen"; *Where these bind in the pipeline* stops at rule 16 | ⚠ stale on two axes | doctrine |
| `pipeline.json` | **absent** — this project has never written its own config, so `run.loop` is unrecorded and the mode defaults to off | — | — |
| `~/.obsidian-wiki/config` | vault `sshlg-projects-vault`; project knowledge under `projects/task-pipeline/` | current | context |
| `gh variable list` | `RELEASE_ENABLED=true`, `PUBLISH_NPMJS=true` — a pushed `vX.Y.Z` tag publishes to npm without a human step | current | **outward** |
| `npm view task-pipeline-skill version` | `1.23.0` — equal to HEAD and to the installed local plugin | current | measured |
| grep over `companion-skills.md`, `stages.md` | **zero** mentions of a browser / devtools / rendered-surface companion | current | measured |

### Standing instructions in force (read in full, they bind this run)

| id | Instruction | Consequence for this run |
|---|---|---|
| R-001 | When a check stays silent against a planted defect, prove the plant landed in the text the check actually parses **before** touching the check | every new guard in M2 is probed, and a silent probe is doubted before the check is |
| R-002 | When a batch of edits returns **any** error, re-verify **every** edit in that batch | multi-file propagation edits are verified per file, not per batch reply |
| R-003 | When you fix a defect in one check or detector, **immediately run that defect's definition against its siblings** | M1 fixes four instances of one class; the sweep for a fifth is part of M1, not a later ticket |
| R-004 | When a gate runs, the **next command must be conditional on its exit code** — never a gate and a commit as two lines | every commit/tag/push is chained `npm test && …`, never newline-separated |

## Autonomy sweep

| Question | Answer | Source |
|---|---|---|
| Test command | `npm test`; full proof `npm run test:all` | `CLAUDE.md` |
| Lint | none separate — the validator is the lint | `CLAUDE.md` |
| Eval shape gate | `python3 evals/run.py` | `docs/DOCMAP.md` |
| Branch policy | mechanical doc fixes → `main`; gate / public-contract changes → branch + PR | `CLAUDE.md`, **operator confirmed 2026-08-08** |
| Version policy | mechanical restoration = patch; each structural module = its own minor | **operator confirmed** |
| Deploy target | tag `vX.Y.Z` → `.github/workflows/release.yml` → GitHub release + npm `task-pipeline-skill` | `CLAUDE.md`, `gh variable list` |
| Deploy authorization | **standing, for this program.** Named target: `ssheleg/task-pipeline`, tag `vX.Y.Z` → GitHub release + npm `task-pipeline-skill`. Precondition: `npm run test:all` green **on the commit the tag points at**, chained with `&&` per R-004. No other outward act is covered — no new repos, no marketplace changes, no PR merges without the CI check green | **operator confirmed 2026-08-08** |
| Post-release obligation | `npx --yes sshlg-skills@latest update`, then confirm the installed plugin version | global `CLAUDE.md` |
| Model | top tier available — `Opus 5 (1M context)`; unchanged for the whole program | preflight |
| Run mode | loop **on**, one module per iteration. Pacing delegated to the agent: no wait when an iteration closes green, 1–15 min only when something needs to settle. To be **recorded** in `pipeline.json` (REQ-011), not remembered | operator instruction |
| Docs targets | `CHANGELOG.md`, `README.md`, `SKILL-CARD.md`, `references/*`, `cursor/rules/task-pipeline.mdc`, `CONTRIBUTING.md`, per the `DOCMAP.md` propagation matrix | `docs/DOCMAP.md` |
| Wiki target | `projects/task-pipeline/` in `sshlg-projects-vault`, via `wiki-update`, **after every iteration** | operator instruction |
| Graph target | `/graphify . --update` **after every iteration** | operator instruction |
| UI work? | **no** — this program ships prose, config and Python. M7 *documents* a browser companion; it does not build an interface. super-ux is not required | brainstorm gate |
| Tracker | this TaskList + the module map below | — |

## Decisions settled at stage 0

| # | Decision | Because |
|---|---|---|
| D1 | The backlog is the six audit findings + the operator's chrome-devtools request, as a frozen REQ seed. Each iteration's stage-10 ladder walk **may add** rows; removing one needs the operator | evidence already gathered; a fresh L0→L7 sweep would spend two iterations searching rather than fixing |
| D2 | Mechanical restoration lands on `main` as a patch; each structural module gets its own branch, PR and minor | matches `CLAUDE.md` and the repo's own history (one feature = one minor) |
| D3 | Deploy authorization is standing for this program, with the named target and precondition above | six manual gates on an identical, verifiable act is the nag R-004's class warns about |
| D4 | No retro stamps are fabricated for v1.17.0–v1.23.0. The honest act is one entry recording that those releases bypassed the pipeline, plus a fix for the trigger that stalled | a stamp asserts a run happened; writing seven would be the exact failure this repository exists to prevent |
| D5 | The operator's *"го до конца автономно"* (2026-08-08, after gate 0 was presented) is an explicit go covering **this program's manual gates** — 0, 2, 7 and 10 — for all seven modules | it is explicit, scoped to this run, and recorded here rather than remembered. It does **not** widen D3: the only outward act authorized is still the named tag → release → npm path, on its stated precondition |

## REQ table — frozen against narrowing

| ID | Requirement | How it is verified | Module | Status |
|---|---|---|---|---|
| REQ-001 | `README.md` and `SKILL.md` no longer state a stale count of `learned.md` rules | `grep -cE '^\| [0-9]+ \|' references/learned.md` equals the stated number, or no number is stated | M1 | open |
| REQ-002 | `references/learned.md` → *Where these bind in the pipeline* names rules 17–21 | set of rules in the table minus set cited in the binding map is empty, computed | M1 | open |
| REQ-003 | `evals/RESULTS.md` stops contradicting `evals/run.py` about dated runs and models exercised | `python3 evals/run.py` printed count equals the document's stated count | M1 | open |
| REQ-004 | `docs/DOCMAP.md` ratchets match the artefacts they describe | standing-instruction count equals `grep -cE '^\| R-[0-9]+' docs/superpowers/retro.md`; eval rows equal `run.py`'s | M1 | open |
| REQ-011 | `pipeline.json` exists, records `run.loop` and this program's stages, and validates against `pipeline.schema.json` | the file loads and validates; `run.loop.mode` is not `off` | M1 | open |
| REQ-006 | The code graph is rebuilt at HEAD and the graph↔docs divergence check is run, its findings recorded | `built_at_commit` equals `git rev-parse HEAD` at refresh time; divergence findings in the carry-over ledger | M1 | open |
| REQ-005 | The "computed, never restated" guard is a **registry** of (claim pattern → computing command) covering ≥ 5 claim classes, each with its own negative self-test | `npm run test:all`; each class planted and watched to fail, then restored | M2 | open |
| REQ-012 | `chrome-devtools-mcp` is recommended for any project with a web frontend, with detection, install line and the stages it binds to; the boundary against super-ux is stated | reach + citation guards green; the propagation matrix walked for a new-companion change | M7 | open |
| REQ-007 | An honest retrospective entry records that v1.17.0–v1.23.0 shipped without a pipeline run or a stamp, and the stalled cold-retirement trigger has a stated fix | the entry exists, its SHAs resolve under `git rev-parse --verify`, and no fabricated stamp was added | M3 | open |
| REQ-008 | Abstention is one named, counted set printed beside every gate verdict | doctrine names all six tokens in one place; the verdict format carries `abstained: N`, guarded | M4 | open |
| REQ-009 | `references/audit.md` carries a sixth rotation axis — *re-derive, don't re-read* — with its exit criterion | the axis exists with its exit criterion; citation guard green | M5 | open |
| REQ-010 | `references/learned.md` has a retirement rule and a cap, analogous to the retro's | doctrine states the triggers and the cap; guarded | M6 | open |
| REQ-013 | Every surface that states the retro's three acts states them **stamp → prune → entry**, and the rule-21 guard compares the class rather than one file | no surface matches a prune-before-stamp pattern, computed; the widened guard planted and watched to fail | M8 | open — **added at M1**, see below |

**REQ-013 was added while M1 was running**, by R-003's sweep ("fix a detector, immediately
run its definition against its siblings"). Rule 21 shipped in v1.23.0 and changed the retro
order in `references/retrospective.md` alone; `SKILL.md:157`, `SKILL.md:267`,
`acceptance.md:179/184/228`, `stages.md:487/494/498`, `templates/retro.md:4` and
`templates/README.md:23` still teach *prune first* — the exact deadlock the rule names.
`SKILL.md` is what an agent loads first. The list is frozen against narrowing, and adding
is free, so this is a row rather than a note.

## Module map — the backlog, in priority order

Stages 0–2 run once. Stages 3→10 run **per module**, one per loop iteration.
Priority is re-evaluated at the end of every iteration.

| # | Module | REQs | Lands on | Version | Priority | Why here |
|---|---|---|---|---|---|---|
| M1 | `truth-restore` | 011, 001, 002, 003, 004, 006 | `main` | patch `v1.23.1` | **1** | **walking skeleton.** Four documents and one graph are false *right now*, and stage 0 of every later iteration reads them. Nothing else is trustworthy until this lands |
| M2 | `claim-registry` | 005 | branch + PR | minor `v1.24.0` | 2 | the check that stops M1's class from recurring — second, so it guards numbers that are already true |
| M7 | `rendered-surface-check` | 012 | branch + PR | minor | 3 | operator-added, unblocked by anything, and it closes the `L6→L7` seam with an observation instead of a reading |
| M3 | `retro-continuity` | 007 | `main` | patch | 4 | bookkeeping and honesty; blocks nothing, but the stalled trigger degrades every later prune |
| M4 | `abstention-ratchet` | 008 | branch + PR | minor | 5 | the cheapest genuine import from the paper |
| M5 | `re-derive-axis` | 009 | branch + PR | minor | 6 | generalises what M2 does mechanically into an audit axis |
| M6 | `learned-retirement` | 010 | branch + PR | minor | 7 | last, because it changes the shape of the file every earlier module edits |

## Carry-over ledger — seeded

| # | Row | Raised at | Home | Status |
|---|---|---|---|---|
| 1 | Seven releases (v1.17.0–v1.23.0) shipped without a pipeline run, a brief, a spec or a stamp | stage 0 | REQ-007 / M3 | open |
| 2 | The shipped doctrine is ~97.5k tokens over 30 reference files; `SKILL.md`'s frontmatter description is at 1015 of 1024 characters, so it cannot absorb another sentence | stage 0 | M6 addresses the growth rule; the description budget has no home yet | **open — needs a home** |
| 3 | `docs/DOCMAP.md` has no register for open questions (`none`), so a question raised mid-run has nowhere to live but this ledger | stage 0 | — | open |

## Gate 0 — status

Source ledger written · retro read in full, four standing instructions in force ·
documentation inventory answered (`docs/DOCMAP.md` exists and is **itself a finding**) ·
intent reconciled against as-built, three divergences found and turned into REQ rows ·
autonomy sweep covered · REQ table written, twelve rows, each naming its check ·
module map written with priority order.

**Awaiting the operator's explicit go.**
