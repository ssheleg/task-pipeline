# Backlog — task-pipeline

> **The board.** Mutable: priority is re-derived, state changes, rows close. A row may
> never vanish silently — it leaves into *Closed* with its commit.
>
> Seeded 2026-08-09 from **twenty-four open rows across eight carry-over ledgers** — sixteen across six by the first count, which read the status column by position and was wrong in half the corpus, which is
> what the project had committed to remembering with nowhere to rank it. Three of them
> were the same finding written three times; the board is where that collapses.
>
> `prio = sev × blast + age_bonus` — inputs in the row, formula here, so the ranking can
> be checked rather than trusted. Doctrine: the skill's `references/backlog.md`.

| id | What | Source | Size | Sev | Blast | Age | Prio | State | Home |
|---|---|---|---|---|---|---|---|---|---|
| B-001 | `SKILL.md`'s frontmatter description sits at **1015 of the 1024-character limit**, and the shipped doctrine is ~97.5k tokens over 30 reference files — the next companion must displace text, not append it | `08-08-audit-followup` #2 | M | 2 | 3 | 2 | **6** | open | — |
| B-002 | **Zero blind eval runs on zero of three models.** The skill's behavioural evidence is one self-check by its author; `evals/RESULTS.md` states the split honestly, which is reporting the gap, not closing it | `08-08-audit-followup` #6 · `08-03-default-routing` #C-1 · `08-03-setup-and-autonomy` #C-1 | L | 2 | 3 | 2 | **6** | open | — |
| B-003 | The independent reviewer is **not in the stage list** — it runs because this repository happens to have a bot on PRs. R-005 is a standing instruction precisely because no stage dispatches a reader | `08-08-audit-followup` #8 | M | 2 | 3 | 2 | **6** | open | — |
| B-006 | `npm run test:negatives` was **flaky**: failed 20, then 4, then passed 114 twice — never diagnosed | `08-06-ci-run-verified` #3 | M | 2 | 2 | 4 | 4 | open | — |
| B-007 | **The code graph's SEMANTIC layer is stale; its structural layer is current.** Three ledgers wrote this row separately; merged here. Re-measured 2026-08-10: `graphify update .` rebuilt the code/AST side to **1070 nodes, 1217 edges, 140 communities** (was 839), every one of the 32 reference files and every template represented, and every hub named by at least one document. What is still behind is the **semantic** pass: **80 markdown files** changed since it was built on 2026-08-05, so nodes like `loop-guard.md`'s *"Detection — the five shapes"* describe the previous version. Closing it needs `GEMINI_API_KEY`/`GOOGLE_API_KEY` or subagent dispatch — a credential, which is the one kind of step that stays with a person | `08-06-ci-run-verified` #4 · `08-06-evidence-docs` #2 · `08-06-graph-staleness` #8 · `08-08-audit-followup` #11 | M | 2 | 2 | 4 | 4 | open | — |
| B-008 | Promote the graph-staleness measurement from doctrine (rung 2) to a script (rung 3) | `08-06-graph-staleness` #2 | S | 1 | 2 | 4 | 2 | open | — |
| B-009 | `docs/DOCMAP.md` records **no register for open questions**, so a question raised mid-run has nowhere to live but the run's own ledger | `08-08-audit-followup` #3 | S | 1 | 2 | 2 | 2 | open | — |
| B-010 | The validator re-reads the same files from disk — **25 reads of `audit.md`, 668 `.md` opens per run**, measured by instrumentation against an estimate of "3+" | `08-08-audit-followup` #12 | S | 1 | 2 | 2 | 2 | open | — |
| B-011 | `grill.md` has no *"is this worth doing at all"* question, and the run that noticed deliberately did not add one | `08-05-spec-plan-quality` #C-002 | S | 1 | 2 | 5 | 2 | open | — |
| B-015 | Nothing tests the routing rule **as a rule** — that a task of the shape the rule describes actually reaches this pipeline | `08-03-setup-and-autonomy` #C-2 | M | 1 | 3 | 7 | 3 | open | — |
| B-024 | **The stage-10 coverage table has no template and its shape has already drifted.** Ten acceptance files in this repo, and the first REQ-bearing table differs in almost every one — ladder walks and coverage tables share a file with different columns. `acceptance.md` defines the shape in prose only, which is precisely how the carry-over ledger reached six header shapes | `2026-08-09-planning-system` / N2 stage 0 | M | 2 | 3 | 1 | **6** | open | — |
| B-024b | **A string substitution that matches nothing says nothing.** Three times this session an edit targeted a shape the file did not have — an import written on one line, a doctrine phrase worded differently, a probe pattern for rows that had changed — and each no-op was invisible until something downstream failed. The class is not the typo; it is that `replace` has no failure mode | `2026-08-09-planning-system` / N3 stage 5 | M | 2 | 3 | 1 | **6** | open | — |
| B-022 | **A guard read a table column by position and was wrong in half the corpus.** Ten ledgers, six header shapes, five with two status-ish columns. The class is wider than one guard: any check that locates data by column index over a hand-written corpus has the same blind spot, and it fails by passing | `2026-08-09-planning-system` / N1 stage 7 | M | 2 | 3 | 1 | **6** | open | — |
| B-016 | The term-index check has a false-positive budget that was never measured over a real corpus — `learned.md` rule 10 says measure a detector before trusting it | `08-03-setup-and-autonomy` #C-3 | S | 1 | 2 | 7 | 2 | open | — |
| B-033 | **The command body is one 1281-word paragraph with 25 obligations**, and it is the first text an agent reads when the skill fires. Longest line 4115 chars. Compliance becomes a function of position rather than importance | `2026-08-10-skill-audit` | M | 2 | 3 | 0 | **6** | open | — |
| B-034 | **`setup` and `checkup` are invisible in every browsable surface** — absent from the SKILL description, the command description and both manifests; they live only in the body of the file you open by running the thing they are an alternative to | `2026-08-10-skill-audit` | S | 2 | 3 | 0 | **6** | open | — |
| B-035 | **The description is at 1015/1024 chars and ~40% of it is mechanism prose** that cannot affect routing. Four references, two templates and two command modes shipped since and none could be mentioned | `2026-08-10-skill-audit` | M | 2 | 3 | 0 | **6** | open | — |
| B-036 | **Both manifests describe the product as it stood at v1.30** — no board, ledger, exposure line, progress rail, run ledger, copy/visual tracks or retro publishing. Seven releases absent from the only text a marketplace shows | `2026-08-10-skill-audit` | S | 1 | 3 | 0 | 3 | open | — |
| B-037 | **R-005's reader is a third party with no contract.** Four PRs of check work, `skipping` on all four, 22 guards merged on author probes alone. The pipeline reads its own dispatch, never the reviewer's output | `2026-08-10-skill-audit` | M | 3 | 3 | 0 | **9** | open | — |
| B-038 | **R-001's probe harness was written into its retirement condition in 2026-08-03 and never built.** Three probe faults in one day, each planting where convenient rather than where the check reads | `2026-08-10-skill-audit` | M | 2 | 3 | 0 | **6** | open | — |
| B-039 | **The stage-0 reading floor is ~48k tokens** before the first grill question — `retro.md` ~14.9k and `stages.md` ~13.2k, both required in full. Volume is itself an instruction, and the instruction is skim | `2026-08-10-skill-audit` | L | 2 | 3 | 0 | **6** | open | — |
| B-040 | **One `never` per 227 words across 77,230 words of doctrine.** 340 absolutes with no ranking function: an agent cannot tell which prohibition is load-bearing, so selective compliance looks arbitrary from outside | `2026-08-10-skill-audit` | M | 1 | 3 | 0 | 3 | open | — |
| B-041 | **92 hand-written counts in prose against 9 registered claim classes.** Most are true today; none of the 83 is guarded, in the repository whose loudest canon is compute-never-restate | `2026-08-10-skill-audit` | M | 1 | 3 | 0 | 3 | open | — |
| B-042 | **The eval suite is frozen at the v1.9 feature set** — zero cases for backlog, verification, exposure, progress, checkup, setup, copywriting or sheleg-design, and zero blind runs on any model | `2026-08-10-skill-audit` | L | 2 | 3 | 0 | **6** | open | — |

## Closed

Rows leave the table above only into this list, one line each, with the commit.

- **B-025 · Stage 7's review loop has no declared cap** — the cap is a decision point, not a stop — at it the run prints new findings against self-inflicted ones per round, because the ten-round runs were still finding real defects on round nine. `loop-guard.md` + stage 7 + `run.review.maxRounds`. Closed in v1.35.0.
- **B-026 · `.task-pipeline/run.md` had never been written by any run** — seeded at stage 0 from `templates/run.md`, named in that stage's gate, and read by two mechanisms — the churn detector and the progress rail. Closed in v1.34.0.
- **B-027 · Nothing in the pipeline owned how the product sounds or looks** — stage 3 runs three tracks with boundaries in both directions; `sheleg-design` joins the matrix and the preflight. Closed in v1.36.0.
- **B-028 · No stage prints which pipeline, which module or which iteration is running** — the header block at task start and the one-line iteration close, the rail computed from the project's own `pipeline.json`, every number borrowed from the gate that measured it. Closed in v1.34.0.
- **B-029 · Every lesson the pipeline learns dies in the repository that learned it** — `retro.publish`, off when absent; the body printed in full before it is sent, five numbered redaction rules. Closed in v1.37.0.
- **B-030 · Eleven stages and four manual gates for any change, including a one-paragraph edit** — stage 0's three-question triage proposes the short path and marks the skipped stages `⊘` with the triage answer — proposed, never taken silently. Closed in v1.35.0.
- **B-031 · The companion matrix is stale about super-ux's own surface** — super-ux's row names its copy half; a guard now compares the matrix's `needed for stage N` cell against what that stage says, and found `chrome-devtools` pointed at stage 5 with stage 5 silent. Closed in v1.36.0.
- **B-032 · `exposure.md`'s worked example disagreed with its own print** — the example carries no digits and its vocabulary is computed from the print statement. Closed in v1.35.0.
- **B-012 · The `v1.15.0` tag and its npm release** — `08-06-graph-staleness` #9; superseded: the project has shipped through `v1.30.0` since, and the release path is exercised every module. Closed by measurement on 2026-08-09.
- **B-013 · `gh` CLI unusable, token went invalid mid-run** — `08-06-graph-staleness` #10; environmental and no longer reproducing: `gh` has served every PR and merge of the last two programmes. Closed by measurement on 2026-08-09.
- **B-004 · A blank line silently splits a markdown table** — `08-05-artifact-hygiene` #C-007; the class hit this very board mid-build, splitting three rows off into prose, and a reader caught it. Promoted to a check the same day rather than to a third ledger row. Closed on 2026-08-09.
- **B-005 · Fixed `/tmp/<name>-copy` scratch paths** — the runner snapshots the tree once and runs every test against the snapshot; parallel execution means a second concurrent suite is rarely needed. Reproduced twice on 2026-08-09 before it was fixed. Closed 2026-08-10.
- **B-021 · The suite copied the repository per test, 13+ minutes** — eight-way parallel run over one snapshot: **5m34s**, measured. Closed 2026-08-10.
- **B-023 · Editing the working tree mid-run corrupted copies** — same change: tests read a pristine snapshot, never the live tree. Closed 2026-08-10.
- **B-017 · The `~/DATA/agent-sync` checkout was behind origin during the 2026-08-03 run** — `08-03-default-routing` #C-3; a run-local observation about another repository's working copy, not project work. Closed as `dropped` on 2026-08-09.
- **B-018 · The wiki was not synced** — `08-03-setup-and-autonomy` #C-4; synced repeatedly since, three times on 2026-08-09 alone. Closed by measurement.
- **B-019 · Ten consecutive releases shipped without a run stamp** — `08-08-audit-followup` #1; addressed in M3, which gave the cold-retirement trigger a second unit precisely because the stamp counter stops when the pipeline is not used. Closed on 2026-08-09.
- **B-020 · The M8 graph refresh dropped nine nodes to id collisions** — `08-08-audit-followup` #9; the row's own content already recorded **0 collisions** after M2's refresh while its status cell still read `open`. Closed by the row's own measurement.
- **B-014 · A run parked at its stage-0 gate** — `08-05-spec-plan-quality` #C-004; not work, a state note about a run that has since finished. Closed as `dropped` on 2026-08-09.

## How rows arrive

1. **Stage 0** seeds this file when absent, reads it when present, and quotes its open
   count in the brief.
2. **Any stage, mid-run** — the moment something is said aloud and not done.
3. **Stage 10** — every carry-over row still `open` arrives here with an id, and the
   ledger row is updated to name it. An `open` ledger row with no board id is the
   dangling pointer this file exists to resolve.
