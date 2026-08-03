# Brief — default-on routing + the adoption track

**Run:** `default-routing-adoption` · 2026-08-03 · stage-0 output, locked.
**Model:** the run's confirmed tier (most capable available), no per-stage override.

## Knowledge sources (the phase-1 harvest — written BEFORE the first question)

| Source | What it says about this task | Fresh? | Authority |
|---|---|---|---|
| `docs/superpowers/retro.md` | **R-001** doubt the probe before the check · **R-002** when a batch of edits errors, re-verify *every* edit in it. Both bind this run | 2026-08-03 | instruction |
| `evals/task-pipeline.evals.json` | `NOTRIG-01/02/03` require the skill **not** to fire on a question, an explanation or a typo fix | current | contract — constrains this task directly |
| Anthropic *Skills for enterprise* | a description that is too broad "steals triggers from existing Skills"; coexistence is an evaluated dimension | fetched 2026-08-03 | external contract |
| `references/companion-skills.md` | agent-sync is optional; absence ⇒ run is `ungated` | current | contract |
| agent-sync `references/pipeline-binding.md` | the binding to this skill — audited, findings A1–A5 below | released 1.4.2 (local checkout behind at `319f9df`) | contract |
| `~/.claude/CLAUDE.md` | the operator's global rules — **the only place a routing default can actually bind** | current | convention |
| this repo | **no `DOCMAP.md`, no register, no `scripts/check-docs.sh`** — the skill that seeds a doc system has not adopted its own | current | code |
| `graphify-out/` | absent — no code graph in this repo | — | — |
| obsidian-wiki | installed; sync at stage 9 | current | context |

**Reconcile (phase 1c):** working tree clean, `main` == `origin/main` at `eb9ce53`.
No divergence between intent and as-built to resolve.

## The finding that shaped the scope

**A skill's `description` cannot force routing.** It raises the odds the model
selects the skill; it cannot make selection mandatory. The only lever that makes
*"any task starts through the pipeline unless told otherwise"* binding is an
instruction in `CLAUDE.md`. So the deliverable has two halves and only one of them
lives in this repository — recorded here rather than discovered at stage 5.

## Scope

**In:** the adoption doctrine and its two walkthroughs; the docgate floor-comment
fix; the trigger vocabulary and the *when not to use* boundary; the routing rule in
the operator's global config; the agent-sync binding patch; the version floor; and
dogfooding the doc track onto this repository.

**Out:** running the behavioural eval suite across three models (a separate,
operator-time exercise); migrating any host project; changing the stage list, ids,
order or gate types.

## Decisions locked (the grill's output)

| # | Decision |
|---|---|
| D1 | **Both levers.** Widen the skill's trigger vocabulary *and* add the routing rule to the global `CLAUDE.md` |
| D2 | **The boundary is "changes the repository."** Feature, fix, refactor, migration, integration, adoption ⇒ pipeline. Question, explanation, code reading, a typo, a one-line edit ⇒ not. Escape phrases: *"без пайплайна"* / *"quick"* |
| D3 | **The `NOTRIG` evals stand.** They encode D2's exclusions; default-on is widened *inside* the boundary, never through it |
| D4 | **Dogfood.** This repository adopts its own doc track in this run, by its own brownfield tutorial |
| D5 | This repo's decision home stays **`CHANGELOG.md` + `docs/superpowers/specs/`** — recorded in `DOCMAP.md` as the choice, not left implied. No second register is created |

## Requirements (frozen — adding is free, removing needs the operator)

| REQ | Requirement | How it's verified |
|---|---|---|
| REQ-001 | `references/adoption.md` — doctrine + greenfield walkthrough + brownfield walkthrough | validator green: file ≥1500 B, reachable from `SKILL.md`, Contents matches headings; new guard requires both walkthroughs |
| REQ-002 | The docgate floor comments state each floor's **kind** — `PROP_FLOOR` an id threshold, `RESIDUE_FLOOR` a count | `grep` finds both kind-words; `adoption.md` cites them; both seeds still green |
| REQ-003 | Trigger vocabulary widened (RU+EN work verbs) **and** an explicit *when not to use* clause | description guard (WHAT-before-WHEN, ≤1024) + new guard requiring exclusion language |
| REQ-004 | Evals match the intended behaviour: exclusions kept, a new `should_trigger` row for repo-changing work with no magic words | `python3 evals/run.py` exits 0; five categories still covered |
| REQ-005 | Global `CLAUDE.md` carries the routing rule with D2's boundary and the escape phrase | `grep` for the boundary and both escape phrases |
| REQ-006 | agent-sync binding patched: config example **valid against `pipeline.schema.json`**, stage-9 doctrine corrected, `guardedFiles` gains `docs/DOCMAP.md` + `docs/superpowers/retro.md`, gates extend rather than replace | a script validates the example against the schema and exits 0 |
| REQ-007 | `companion-skills.md` states the **agent-sync ≥ 1.3.0** floor for `finish` | `grep` |
| REQ-008 | This repo adopts its own doc track: `docs/DOCMAP.md` recording D5, `scripts/check-docs.sh` seeded, floors set to today | `bash scripts/check-docs.sh` exits 0 in this repository |
| REQ-009 | This run recorded in `evals/RESULTS.md` as the first observed instruction-following run | a dated `## YYYY-MM-DD · <model>` heading exists and `evals/run.py` counts it |

## Users & UI verdict

No user-facing surface. **UI verdict: no** — the stage-3 UX track does not arm, and
super-ux is not required for this run.

## Autonomy (the sweep — stages 1→10 read this instead of asking)

| Stage | Question | Answer |
|---|---|---|
| run-wide | Model | the confirmed tier; no per-stage override |
| run-wide | Decide autonomously vs escalate | autonomous to the end, including commit, push and tag |
| 0 Harvest | Doc sources beyond this repo | agent-sync (`~/DATA/agent-sync`, pull before editing), the operator's global `CLAUDE.md`. Both are **owned by the operator** and edited directly, not by PR |
| 0 Docs regime | Decision home | D5 — CHANGELOG + `specs/`; DOCMAP records it; no second register |
| 1 Docs | External libs | none new; the hook contract was re-fetched 2026-08-03 |
| 2 Decompose | Platform or change? | a change — single module, no module map |
| 2–3 Spec | UI verdict | no |
| 3 Design surface | Figma | n/a |
| 3 Design file | Figma destination | n/a |
| 4–5 Dev | Branch policy | small doctrine edits land on `main` (house rule); no worktree needed |
| 5 Integration | How it lands | direct commits on `main`, conventional messages |
| 6 Tests | Test command | `npm test`; full: `npm run test:all` |
| 7 Lint | Lint command | the validator *is* the lint |
| 7 Deploy | Target + authorization | tag `vX.Y.Z` → release workflow. **Standing go for this run:** publish task-pipeline and the `sshlg-skills` catalogue pin, after `npm run test:all` is green on the tagged commit |
| 8 Post-deploy | Where health lives | `gh run list`, `npm view <pkg> version` |
| 9 Docs+wiki | Targets | `README.md`, `CHANGELOG.md`, `SKILL-CARD.md`, `CONTRIBUTING.md` invariants, wiki sync; no code graph in this repo |
| 10 Acceptance | Sign-off + tracker | the operator signs off; deferrals go to `evals/RESULTS.md`'s ratchet or the carry-over ledger |

## Done-criteria

`npm run test:all` green · both seeded shapes still green · this repo's own docs gate
green · agent-sync's example validated against the schema · every REQ closed with
evidence at stage 10 · retro written last.

## Open assumptions / risks

- **Widening triggers is the enterprise guidance's named anti-pattern** when it
  crosses into other skills' territory. D2's boundary is the mitigation, and
  `COEX-01` is the eval that would detect a breach — unrun, so this is a *stated*
  mitigation, not a measured one.
- **The routing rule binds only where that `CLAUDE.md` is read.** Another machine or
  a project-level config without it falls back to the description alone.
