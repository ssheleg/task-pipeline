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
| B-001 | `SKILL.md`'s frontmatter description sits at **1015 of the 1024-character limit**, and the shipped doctrine is ~97.5k tokens over 30 reference files — the next companion must displace text, not append it | `08-08-audit-followup` #2 | M | 2 | 3 | 1 | **6** | open | — |
| B-002 | **Zero blind eval runs on zero of three models.** The skill's behavioural evidence is one self-check by its author; `evals/RESULTS.md` states the split honestly, which is reporting the gap, not closing it | `08-08-audit-followup` #6 · `08-03-default-routing` #C-1 · `08-03-setup-and-autonomy` #C-1 | L | 2 | 3 | 1 | **6** | open | — |
| B-003 | The independent reviewer is **not in the stage list** — it runs because this repository happens to have a bot on PRs. R-005 is a standing instruction precisely because no stage dispatches a reader | `08-08-audit-followup` #8 | M | 2 | 3 | 1 | **6** | open | — |
| B-005 | The negative self-tests use **fixed `/tmp/<name>-copy` paths**, so two concurrent runs of `npm run test:all` overwrite each other's scratch | `08-06-evidence-docs` #1 | S | 2 | 2 | 3 | 4 | open | — |
| B-006 | `npm run test:negatives` was **flaky**: failed 20, then 4, then passed 114 twice — never diagnosed | `08-06-ci-run-verified` #3 | M | 2 | 2 | 3 | 4 | open | — |
| B-007 | **The code graph is stale and its refresh erodes it.** Three ledgers wrote this row separately; merged here. Currently 839 nodes at `2fc201e`, 11 commits behind, and a full rebuild needs a Gemini key or subagent dispatch | `08-06-ci-run-verified` #4 · `08-06-evidence-docs` #2 · `08-06-graph-staleness` #8 · `08-08-audit-followup` #11 | M | 2 | 2 | 3 | 4 | open | — |
| B-008 | Promote the graph-staleness measurement from doctrine (rung 2) to a script (rung 3) | `08-06-graph-staleness` #2 | S | 1 | 2 | 3 | 2 | open | — |
| B-009 | `docs/DOCMAP.md` records **no register for open questions**, so a question raised mid-run has nowhere to live but the run's own ledger | `08-08-audit-followup` #3 | S | 1 | 2 | 1 | 2 | open | — |
| B-010 | The validator re-reads the same files from disk — **25 reads of `audit.md`, 668 `.md` opens per run**, measured by instrumentation against an estimate of "3+" | `08-08-audit-followup` #12 | S | 1 | 2 | 1 | 2 | open | — |
| B-011 | `grill.md` has no *"is this worth doing at all"* question, and the run that noticed deliberately did not add one | `08-05-spec-plan-quality` #C-002 | S | 1 | 2 | 4 | 2 | open | — |
| B-015 | Nothing tests the routing rule **as a rule** — that a task of the shape the rule describes actually reaches this pipeline | `08-03-setup-and-autonomy` #C-2 | M | 1 | 3 | 6 | 3 | open | — |
| B-022 | **A guard read a table column by position and was wrong in half the corpus.** Ten ledgers, six header shapes, five with two status-ish columns. The class is wider than one guard: any check that locates data by column index over a hand-written corpus has the same blind spot, and it fails by passing | `2026-08-09-planning-system` / N1 stage 7 | M | 2 | 3 | 0 | 6 | open | — |
| B-023 | **Editing the working tree while `npm run test:negatives` runs** gives some of its 164 `cp -R .` copies a half-written file. Nothing detects it; the suite would simply report something that was never a state of the repo | `2026-08-09-planning-system` / N1 stage 6 | S | 2 | 2 | 0 | 4 | open | — |
| B-021 | The negative suite copies the whole repository **once per test** (`cp -R .` × 163) and now runs over ten minutes — long enough that it gets backgrounded, which is how a suite stops being run before every commit | `2026-08-09-planning-system` / N1 stage 6 | M | 1 | 2 | 0 | 2 | open | — |
| B-016 | The term-index check has a false-positive budget that was never measured over a real corpus — `learned.md` rule 10 says measure a detector before trusting it | `08-03-setup-and-autonomy` #C-3 | S | 1 | 2 | 6 | 2 | open | — |

## Closed

Rows leave the table above only into this list, one line each, with the commit.

- **B-012 · The `v1.15.0` tag and its npm release** — `08-06-graph-staleness` #9; superseded: the project has shipped through `v1.30.0` since, and the release path is exercised every module. Closed by measurement on 2026-08-09.
- **B-013 · `gh` CLI unusable, token went invalid mid-run** — `08-06-graph-staleness` #10; environmental and no longer reproducing: `gh` has served every PR and merge of the last two programmes. Closed by measurement on 2026-08-09.
- **B-004 · A blank line silently splits a markdown table** — `08-05-artifact-hygiene` #C-007; the class hit this very board mid-build, splitting three rows off into prose, and a reader caught it. Promoted to a check the same day rather than to a third ledger row. Closed on 2026-08-09.
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
