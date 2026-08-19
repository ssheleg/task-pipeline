# Verification — task-pipeline

## Shipped state — v1.68.0

This file recorded no version at all until 2026-08-17, so nothing said which artifact its rows were confirmed against — a ledger whose
own rule is that a row sits at `never` until somebody watched its check pass on **what shipped**.
The umbrella's disclosure now reports that gap for every member on each `npm test`.

> **Append-only.** One row per shipped REQ, written by stage 8. Nobody edits a row
> except to fill `Human`, and filling it is the one thing here a machine may not do.
>
> Seeded 2026-08-09 from the REQ tables of every brief this repository has, with
> `Shipped in` resolved from git — the tag containing the commit that added the brief.
> **Every row reads `never`, and that is not a failure.** It is what is true: the
> project has shipped thirty-one versions and nobody has ever recorded looking at a
> shipped requirement afterwards. Printing it is the first time that could be asked.
>
> The count has no floor, no direction, and may never be given a target. Doctrine:
> the skill's `references/verification.md`.
>
> **`Observed at` arrived on 2026-08-19, and every row that predates it reads `—`.** That is
> not an omission to be backfilled: the column records the commit a check actually ran
> against, and for a row written before the column existed nobody recorded one — the
> `unanchored` state `templates/exposure.sh` names, printed rather than guessed. B-081 gave
> the template this column on 2026-08-17 and this project's own ledger did not have it, so
> the pack shipped a freshness contract it did not keep. Re-observing a row appends a new
> row; it never edits an old one.

| REQ | What | Run | Shipped in | Observed at | Auto | Human | Note |
|---|---|---|---|---|---|---|---|
| REQ-001 | `references/adoption.md` — doctrine + greenfield walkthrough + brownfield walkthrough | `2026-08-03-default-routing-adoption` | v1.9.0 | — | pass | never | — |
| REQ-002 | The docgate floor comments state each floor's **kind** — `PROP_FLOOR` an id threshold, `RESIDUE_FLOOR` a count | `2026-08-03-default-routing-adoption` | v1.9.0 | — | pass | never | — |
| REQ-003 | Trigger vocabulary widened (RU+EN work verbs) **and** an explicit *when not to use* clause | `2026-08-03-default-routing-adoption` | v1.9.0 | — | pass | never | — |
| REQ-004 | Evals match the intended behaviour: exclusions kept, a new `should_trigger` row for repo-changing work with no magic words | `2026-08-03-default-routing-adoption` | v1.9.0 | — | pass | never | — |
| REQ-005 | Global `CLAUDE.md` carries the routing rule with D2's boundary and the escape phrase | `2026-08-03-default-routing-adoption` | v1.9.0 | — | pass | never | — |
| REQ-006 | agent-sync binding patched: config example **valid against `pipeline.schema.json`**, stage-9 doctrine corrected, `guardedFiles` gains `docs/DOCMAP.md` + `docs/superpowers/retro.md`, gates extend rather than replace | `2026-08-03-default-routing-adoption` | v1.9.0 | — | pass | never | — |
| REQ-007 | `companion-skills.md` states the **agent-sync ≥ 1.3.0** floor for `finish` | `2026-08-03-default-routing-adoption` | v1.9.0 | — | pass | never | — |
| REQ-008 | This repo adopts its own doc track: `docs/DOCMAP.md` recording D5, `scripts/check-docs.sh` seeded, floors set to today | `2026-08-03-default-routing-adoption` | v1.9.0 | — | pass | never | — |
| REQ-009 | This run recorded in `evals/RESULTS.md` as the first observed instruction-following run | `2026-08-03-default-routing-adoption` | v1.9.0 | — | pass | never | — |
| REQ-001 | `references/setup.md` — the entry audit: when it runs, what it inspects, the finding shape (`file:line` + minimal fix), and that its output is a fix plan the pipeline can run | `2026-08-03-setup-and-autonomy` | v1.10.0 | — | pass | never | — |
| REQ-002 | Stage 0 offers it **once** when the doc map is absent or stale; the answer is recorded in the brief's sweep and never re-asked | `2026-08-03-setup-and-autonomy` | v1.10.0 | — | pass | never | — |
| REQ-003 | `/task-pipeline setup` is a documented branch of the command | `2026-08-03-setup-and-autonomy` | v1.10.0 | — | pass | never | — |
| REQ-004 | Self-currency: preflight compares the installed version against the released one and recommends `npx sshlg-skills update`; staleness signals named (never-fired standing instructions, a stale doc map, a frozen ratchet) | `2026-08-03-setup-and-autonomy` | v1.10.0 | — | pass | never | — |
| REQ-005 | The escalation boundary: cost-of-being-wrong as the default rule, plus a sweep row for exceptions | `2026-08-03-setup-and-autonomy` | v1.10.0 | — | pass | never | — |
| REQ-006 | Term index: every domain term used in the docs resolves to one definition; the doc map gains a *Terms* row; the seeded gate gains the section | `2026-08-03-setup-and-autonomy` | v1.10.0 | — | pass | never | — |
| REQ-007 | Stage 2 produces user paths, states and error paths as **design outputs**, feeding the stage-3 chain | `2026-08-03-setup-and-autonomy` | v1.10.0 | — | pass | never | — |
| REQ-008 | Every new invariant has a guard **and** a negative self-test watched failing | `2026-08-03-setup-and-autonomy` | v1.10.0 | — | pass | never | — |
| REQ-009 | Released, catalogue pinned, local installs refreshed through the launcher, this run recorded | `2026-08-03-setup-and-autonomy` | v1.10.0 | — | pass | never | — |
| REQ-010 | `references/portability.md` — the manifest: every **workflow decision** with its home **inside the bundle**, plus the boundary rule (workflow decisions travel, project answers stay) | `2026-08-03-setup-and-autonomy` | v1.10.0 | — | pass | never | — |
| REQ-011 | The routing rule travels with the bundle: `templates/routing-rule.md`, and `setup` **offers** to append it to the operator's config rather than writing silently | `2026-08-03-setup-and-autonomy` | v1.10.0 | — | pass | never | — |
| REQ-001 | `pipeline.schema.json` gains a `run` block with `loop` and `contextBudget`; both optional, **absent ⇒ off** | `2026-08-04-run-continuity` | v1.11.0 | — | pass | never | — |
| REQ-002 | `references/continuity.md` exists and carries both halves | `2026-08-04-run-continuity` | v1.11.0 | — | pass | never | — |
| REQ-003 | The loop decision is **surfaced at launch**: preflight block in `SKILL.md`, a row in the grill's autonomy sweep, a row in `templates/brief.md`'s autonomy table | `2026-08-04-run-continuity` | v1.11.0 | — | pass | never | — |
| REQ-004 | `build.md`'s unconditional *"Continuous execution"* is reconciled with a default-off recorded mode — no two surfaces disagree | `2026-08-04-run-continuity` | v1.11.0 | — | pass | never | — |
| REQ-005 | The context rule states its **evidence condition** and forbids announcing exhaustion without a signal | `2026-08-04-run-continuity` | v1.11.0 | — | pass | never | — |
| REQ-006 | `/loop` is documented with its **real** semantics — fixed short interval, Claude-Code-only, and why a mid-task fire is safe — following `hooks.md`'s harness-limit precedent | `2026-08-04-run-continuity` | v1.11.0 | — | pass | never | — |
| REQ-007 | Every new guard has a negative self-test in `.github/workflows/validate.yml`, and `test/negatives.py`'s floor is raised | `2026-08-04-run-continuity` | v1.11.0 | — | pass | never | — |
| REQ-008 | The propagation matrix is walked: README map, portability manifest, Cursor rule, `CONTRIBUTING.md` invariants, `SKILL-CARD.md`, `CHANGELOG.md`, four-way version sync at **v1.11.0** | `2026-08-04-run-continuity` | v1.11.0 | — | pass | never | — |
| REQ-009 | The context rule also lands in `~/.claude/CLAUDE.md`, **with the diff shown before it is written** | `2026-08-04-run-continuity` | v1.11.0 | — | pass | never | — |
| REQ-010 | `pipeline.example.json` ships `run` **explicitly off**, so the example demonstrates the default instead of relying on its absence | `2026-08-04-run-continuity` | v1.11.0 | — | pass | never | — |
| REQ-011 | `docs/DOCMAP.md` gains a propagation row for **a change to the config contract** | `2026-08-04-run-continuity` | v1.11.0 | — | pass | never | — |
| REQ-012 | Every relative link in a seeded template resolves **from the destination the doctrine seeds it to**, not only from `templates/` | `2026-08-04-run-continuity` | v1.11.0 | — | pass | never | — |
| REQ-013 | The doctrine states what a loop fire does when the run is **parked at a `manual` gate**: the run quiesces its own loop and prints the re-arm command beside the gate | `2026-08-04-run-continuity` | v1.11.0 | — | pass | never | — |
| REQ-001 | `templates/hygiene.sh` exists and carries the full `docgate.sh` contract: `SCOPE:` header, VERDICT last, bash-3.2 portability, progressive arming, computed final line | `2026-08-05-artifact-hygiene` | v1.12.0^0 | — | pass | never | — |
| REQ-002 | Check 1 — conflict markers | `2026-08-05-artifact-hygiene` | v1.12.0^0 | — | pass | never | — |
| REQ-003 | Check 2 — placeholders, **with the false-positive surface solved** (A1) and the solution stated in `SCOPE` | `2026-08-05-artifact-hygiene` | v1.12.0^0 | — | pass | never | — |
| REQ-004 | Check 3 — unterminated fence | `2026-08-05-artifact-hygiene` | v1.12.0^0 | — | pass | never | — |
| REQ-005 | Check 4 — truncation stubs | `2026-08-05-artifact-hygiene` | v1.12.0^0 | — | pass | never | — |
| REQ-006 | Check 5 — duplicated adjacent block, the R-002 mechanisation | `2026-08-05-artifact-hygiene` | v1.12.0^0 | — | pass | never | — |
| REQ-007 | Check 6 — heading with no body | `2026-08-05-artifact-hygiene` | v1.12.0^0 | — | pass | never | — |
| REQ-008 | Two modes: diff at zero tolerance, tree behind a floor set to today's measured count | `2026-08-05-artifact-hygiene` | v1.12.0^0 | — | pass | never | — |
| REQ-009 | Doctrine: `build.md` runs it after each task; `stages.md` §5, §6 and §9 name it in their gate criteria; `gates.md` gains it as a worked example | `2026-08-05-artifact-hygiene` | v1.12.0^0 | — | pass | never | — |
| REQ-010 | The **fix obligation** is doctrine: a finding is fixed or explicitly carried over; the script never edits | `2026-08-05-artifact-hygiene` | v1.12.0^0 | — | none | never | — |
| REQ-011 | `npm test` executes the gate over a seeded scratch project and requires exit 0 | `2026-08-05-artifact-hygiene` | v1.12.0^0 | — | pass | never | — |
| REQ-012 | A negative self-test per check in `.github/workflows/validate.yml`; `MIN_EXPECTED` recomputed from the workflow | `2026-08-05-artifact-hygiene` | v1.12.0^0 | — | pass | never | — |
| REQ-013 | Propagation: `CHANGELOG.md`, `README.md`, `CONTRIBUTING.md` invariants, `templates/README.md`, `references/artifacts.md`, `references/portability.md`, `cursor/rules/task-pipeline.mdc` (`review`) | `2026-08-05-artifact-hygiene` | v1.12.0^0 | — | pass | never | — |
| REQ-014 | Four-way version sync at **1.12.0** | `2026-08-05-artifact-hygiene` | v1.12.0^0 | — | pass | never | — |
| REQ-001 | `spec.md` self-review gains **"every check this spec names resolves"** — a check that does not exist is either built or marked `review`, never asserted (D1) | `2026-08-05-spec-plan-quality` | v1.13.0^0 | — | pass | never | — |
| REQ-002 | `spec.md` requires a committed **`## Self-review`** section with computed values — REQ counts and the difference, checks named vs resolving, decisions reconciled, cost delta, placeholder and ambiguity counts (D2) | `2026-08-05-spec-plan-quality` | v1.13.0^0 | — | none | never | — |
| REQ-003 | `spec.md` self-review gains the **decision read-back**: the brief's `## Decisions locked` table *and* the register entries stage 2 recorded for rejected alternatives (`brainstorm.md:105`). A contradiction is resolved out loud, never silently (D3) | `2026-08-05-spec-plan-quality` | v1.13.0^0 | — | none | never | — |
| REQ-004 | `spec.md` self-review gains the **cost checkpoint**: print surfaces / guards / REQ count as of stage 2 and as of now. **Prints; never narrows.** The stage-3 gate is manual, so the operator decides (D4) | `2026-08-05-spec-plan-quality` | v1.13.0^0 | — | pass | never | — |
| REQ-005 | `planning.md` self-review gains **"every command, path and file a DoD names resolves"** (D1/D5 at stage 4) | `2026-08-05-spec-plan-quality` | v1.13.0^0 | — | pass | never | — |
| REQ-006 | `planning.md` requires the same committed **`## Self-review`** section (D2) | `2026-08-05-spec-plan-quality` | v1.13.0^0 | — | pass | never | — |
| REQ-007 | `learned.md`'s stage map lists rule 14 at **stages 3 and 4**, not only 9 — the read-back made structural (D5) | `2026-08-05-spec-plan-quality` | v1.13.0^0 | — | pass | never | — |
| REQ-008 | `references/stages.md` §3 and §4 gate criteria demand the `## Self-review` section and name what it must contain | `2026-08-05-spec-plan-quality` | v1.13.0^0 | — | none | never | — |
| REQ-009 | Every new guard has a negative self-test in `.github/workflows/validate.yml`; `test/negatives.py`'s `MIN_EXPECTED` recomputed from the workflow | `2026-08-05-spec-plan-quality` | v1.13.0^0 | — | pass | never | — |
| REQ-010 | Propagation walked: `CHANGELOG.md`, `CONTRIBUTING.md` → *The invariants* for each new guard, `cursor/rules/task-pipeline.mdc` (**this changes how an agent behaves elsewhere** → `review`), `templates/` if a template gains the section | `2026-08-05-spec-plan-quality` | v1.13.0^0 | — | pass | never | — |
| REQ-011 | Four-way version sync at **1.12.0** | `2026-08-05-spec-plan-quality` | v1.13.0^0 | — | pass | never | — |
| REQ-001 | `conventions.md` states the method: the commands for conclusion and failing log, both the `gh` and the unauthenticated path | `2026-08-06-ci-run-verified` | v1.16.2 | — | pass | never | — |
| REQ-002 | Three states named — concluded / in progress / no run found — so silence never reads as green | `2026-08-06-ci-run-verified` | v1.16.2 | — | pass | never | — |
| REQ-003 | `stages.md` § 7, § 8 and § 9 gates require the run's verdict to be **read and quoted**, citing `conventions.md` rather than restating it | `2026-08-06-ci-run-verified` | v1.16.2 | — | pass | never | — |
| REQ-004 | `pipeline.example.json`'s stage-8 gate check and `release.verify` require it | `2026-08-06-ci-run-verified` | v1.16.2 | — | pass | never | — |
| REQ-005 | Every new guard has a negative self-test, each proved plant-first (R-001); the floor rises | `2026-08-06-ci-run-verified` | v1.16.2 | — | pass | never | — |
| REQ-006 | `README.md` and the Cursor rule state it; the rule stays self-contained | `2026-08-06-ci-run-verified` | v1.16.2 | — | pass | never | — |
| REQ-007 | `CHANGELOG.md` v1.16.0 + four-way version sync + `SKILL-CARD.md` | `2026-08-06-ci-run-verified` | v1.16.2 | — | pass | never | — |
| REQ-008 | `CONTRIBUTING.md` invariant citing a literal the validator prints; `portability.md` homes the decision | `2026-08-06-ci-run-verified` | v1.16.2 | — | pass | never | — |
| REQ-009 | Released: tag `v1.16.0`, `release.yml` green, registry serves it, **and this run's own pushes verified by the new method** | `2026-08-06-ci-run-verified` | v1.16.2 | — | pass | never | — |
| REQ-001 | `knowledge-graph.md` states the measured-lag rule: the two exact git commands, and the row format that carries commits + days + the signal | `2026-08-06-graph-staleness` | v1.15.0 | — | pass | never | — |
| REQ-002 | Three distinct signal states are named — `built_at_commit` (exact), `mtime` (approximate, stamp absent), and stamp-present-but-unresolvable — so silence is never indistinguishable from a fresh graph | `2026-08-06-graph-staleness` | v1.15.0 | — | pass | never | — |
| REQ-003 | `knowledge-sources.md` says the graph row carries the measured lag, **citing** `knowledge-graph.md` rather than restating the commands | `2026-08-06-graph-staleness` | v1.15.0 | — | pass | never | — |
| REQ-004 | `templates/brief.md`'s seeded ledger row shows the measured form, not a bare `built YYYY-MM-DD` | `2026-08-06-graph-staleness` | v1.15.0 | — | pass | never | — |
| REQ-005 | `stages.md` stage-0 harvest line **and** its `GATE (manual)` criteria require the measured row | `2026-08-06-graph-staleness` | v1.15.0 | — | pass | never | — |
| REQ-006 | `pipeline.example.json` stage-0 `gate.check` requires the measured row | `2026-08-06-graph-staleness` | v1.15.0 | — | pass | never | — |
| REQ-007 | The existing code-graph guard at `test/validate.py:1405` is **extended** to stage 0 in both halves — R-003's sibling sweep, not a parallel copy | `2026-08-06-graph-staleness` | v1.15.0 | — | pass | never | — |
| REQ-008 | Every new guard has a negative self-test in `.github/workflows/validate.yml`, each **proved plant-first** per R-001, and the negatives floor is raised | `2026-08-06-graph-staleness` | v1.15.0 | — | pass | never | — |
| REQ-009 | `README.md` and `cursor/rules/task-pipeline.mdc` state the measured form; the Cursor rule stays self-contained (zero relative links) | `2026-08-06-graph-staleness` | v1.15.0 | — | pass | never | — |
| REQ-010 | `CHANGELOG.md` gains a v1.15.0 section written as *what changed and why*; version synced across `package.json`, `marketplace.json`, `plugin.json` and the CHANGELOG heading | `2026-08-06-graph-staleness` | v1.15.0 | — | pass | never | — |
| REQ-011 | `references/portability.md`'s manifest homes this workflow decision | `2026-08-06-graph-staleness` | v1.15.0 | — | pass | never | — |
| REQ-012 | `CONTRIBUTING.md` gains the invariant, citing a literal the validator actually prints | `2026-08-06-graph-staleness` | v1.15.0 | — | pass | never | — |
| REQ-013 | Released: tag `v1.15.0`, `release.yml` green, the registry serves it, local installs updated | `2026-08-06-graph-staleness` | v1.15.0 | — | pass | never | — |
| REQ-001 | `README.md` and `SKILL.md` no longer state a stale count of `learned.md` rules | `2026-08-08-audit-followup` | v1.23.1^0 | — | pass | never | — |
| REQ-002 | `references/learned.md` → *Where these bind in the pipeline* names rules 17–21 | `2026-08-08-audit-followup` | v1.23.1^0 | — | pass | never | — |
| REQ-003 | `evals/RESULTS.md` stops contradicting `evals/run.py` about dated runs and models exercised | `2026-08-08-audit-followup` | v1.23.1^0 | — | pass | never | — |
| REQ-004 | `docs/DOCMAP.md` ratchets match the artefacts they describe | `2026-08-08-audit-followup` | v1.23.1^0 | — | pass | never | — |
| REQ-011 | `pipeline.json` exists, records `run.loop` and this program's stages, and validates against `pipeline.schema.json` | `2026-08-08-audit-followup` | v1.23.1^0 | — | pass | never | — |
| REQ-006 | The code graph is rebuilt at HEAD and the graph↔docs divergence check is run, its findings recorded | `2026-08-08-audit-followup` | v1.23.1^0 | — | pass | never | — |
| REQ-005 | The "computed, never restated" guard is a **registry** of (claim pattern → computing command) covering ≥ 5 claim classes, each with its own negative self-test | `2026-08-08-audit-followup` | v1.23.1^0 | — | pass | never | — |
| REQ-012 | `chrome-devtools-mcp` is recommended for any project with a web frontend, with detection, install line and the stages it binds to; the boundary against super-ux is stated | `2026-08-08-audit-followup` | v1.23.1^0 | — | pass | never | — |
| REQ-007 | An honest retrospective entry records that v1.17.0–v1.23.0 shipped without a pipeline run or a stamp, and the stalled cold-retirement trigger has a stated fix | `2026-08-08-audit-followup` | v1.23.1^0 | — | pass | never | — |
| REQ-008 | Abstention is one named, counted set printed beside every gate verdict | `2026-08-08-audit-followup` | v1.23.1^0 | — | pass | never | — |
| REQ-009 | `references/audit.md` carries a sixth rotation axis — *re-derive, don't re-read* — with its exit criterion | `2026-08-08-audit-followup` | v1.23.1^0 | — | pass | never | — |
| REQ-010 | `references/learned.md` has a retirement rule and a cap, analogous to the retro's | `2026-08-08-audit-followup` | v1.23.1^0 | — | pass | never | — |
| REQ-013 | Every surface that states the retro's three acts states them **stamp → prune → entry**, and the rule-21 guard compares the class rather than one file | `2026-08-08-audit-followup` | v1.23.1^0 | — | pass | never | — |
| REQ-001 | `artifacts.md` names both new files in **both** maps and in the single-home table | `2026-08-09-planning-system` | v1.32.0 | — | pass | never | — |
| REQ-002 | `docs/superpowers/backlog.md` — seeded at stage 0 when absent, picked up when present | `2026-08-09-planning-system` | v1.31.0 | — | pass | never | — |
| REQ-003 | Any stage may append a row mid-run, same rule as the ledger: *deferred out loud or lost* | `2026-08-09-planning-system` | v1.31.0 | — | pass | never | — |
| REQ-005 | Every carry-over row homed `backlog` resolves to a real board id — **both directions** | `2026-08-09-planning-system` | v1.31.0 | — | pass | never | — |
| REQ-006 | `docs/superpowers/verification.md` — one row per REQ: shipped-in, auto verdict, human-confirmed date or `never` | `2026-08-09-planning-system` | v1.32.0 | — | pass | never | — |
| REQ-007 | Stage 8 writes the row; stage 10 refuses a REQ with no row | `2026-08-09-planning-system` | v1.32.0 | — | pass | never | — |
| REQ-015 | `playwright` is a companion with two no-plugin install paths, and neither channel is ranked above the other | `2026-08-14-playwright-browser-channel` | v1.55.0 | — | pass | never | — |
| REQ-016 | One detection rule covers both browser channels, with the tie-breaker written down and 'stop at the first that answers' | `2026-08-14-playwright-browser-channel` | v1.55.0 | — | pass | never | — |
| REQ-017 | A browser test suite is the coverage half of stage 6 and never the look — stated in stages.md, tdd.md and SKILL.md | `2026-08-14-playwright-browser-channel` | v1.55.0 | — | pass | never | — |
| REQ-018 | A browser finding is fixed in the stage that found it, not filed — stages 5 and 6 | `2026-08-14-playwright-browser-channel` | v1.55.0 | — | pass | never | — |
| REQ-019 | A pipe inside a companion-skills.md matrix row is refused; the graphify row that carried one since it was added is fixed | `2026-08-14-playwright-browser-channel` | v1.55.0 | — | pass | never | — |
| REQ-001 | The fake-edge test is a numbered procedure in `planning.md`, not a checklist line — guarded by a plant that renames it away | `2026-08-15-graph-audit` | v1.56.0 | — | pass | never | F-1 |
| REQ-002 | The plan's *Execution order* table has a `Carries` column and an empty cell is stated to be the finding — guarded both ways: the column dropped, and the gate no longer reading it | `2026-08-15-graph-audit` | v1.56.0 | — | pass | never | F-7 |
| REQ-003 | The stage-4 self-review states `Edges: <n> declared, <n> carry data, <n> removed`, and the gate reads it | `2026-08-15-graph-audit` | v1.56.0 | — | pass | never | F-1 |
| REQ-004 | `build.md` §4.2a — one convergence check over a fanned-out group's diffs together, **before** the first worktree is integrated, five catches, and a clean group logs a line too | `2026-08-15-graph-audit` | v1.56.0 | — | pass | never | F-2 |
| REQ-005 | This pipeline is stated to be a static graph by choice, with auditability as the reason and both bounded dynamic elements named | `2026-08-15-graph-audit` | v1.56.0 | — | pass | never | F-3 |
| REQ-006 | `stages.md` stage 5 states all three fan-out preconditions and names the convergence check — the drift that had it at one condition is guarded in the direction it drifted | `2026-08-15-graph-audit` | v1.56.0 | — | pass | never | F-5 · F-6 |
| REQ-007 | `test/negatives.py` restores `.git` from a submodule checkout's `gitdir:` pointer, stripping `core.worktree` from the copy; measured exit 1 with 2 guards down before, exit 0 with all 318 twice after | `2026-08-15-graph-audit` | v1.56.0 | — | pass | never | F-8 |
| REQ-008 | Both GATE bullets require the convergence check, not only the prose and the stage table — and a guard requires the gate to require it | `2026-08-15-graph-audit` | v1.56.0 | — | pass | never | PR #47 review; F-2's second half |
| REQ-009 | The `.git` restore resolves `git rev-parse --git-common-dir`, so it is correct for a clone, a submodule **and** a linked worktree — the shape `build.md` itself tells runs to use | `2026-08-15-graph-audit` | v1.56.0 | — | pass | never | PR #47 review; F-8's second shape |
| REQ-001 | Stage 0's harvest carries a `Contradictions:` line and the gate reads it — the fan-out that converges on one brief now compares its sources with each other | `2026-08-16-graph-backlog` | v1.58.0 | — | pass | never | G-6 |
| REQ-002 | Stage 3's COPY and VISUAL are a parallel layer after UX, and their convergence has a check with four named catches | `2026-08-16-graph-backlog` | v1.58.0 | — | pass | never | G-2 |
| REQ-003 | Stage 9's three artifacts are named as a convergence and the graph↔docs check as its gate | `2026-08-16-graph-backlog` | v1.58.0 | — | pass | never | G-3 |
| REQ-004 | Two concurrent runs of `negatives.py` serialise instead of corrupting each other; the second waits and says so | `2026-08-16-graph-backlog` | v1.58.0 | — | pass | never | B-075 |
| REQ-005 | Manual id and version allocation is written where an agent reads it, and a guard requires it wherever a register is declared over a backend that cannot reserve | `2026-08-16-graph-backlog` | v1.58.0 | — | pass | never | B-45 |
| REQ-001 | Never amend a commit a record already names — stated in `retrospective.md` with the order that removes the temptation | `2026-08-16-stamp-order` | v1.59.0 | — | pass | never | B-52 |
| REQ-002 | The documentation gate requires reachability from HEAD, not only resolution | `2026-08-16-stamp-order` | v1.59.0 | — | pass | never | B-52 · watched failing on an amended-away commit |
| REQ-003 | The three unservable id registers are removed and the guard that requires the manual procedure fires on the backend instead | `2026-08-16-stamp-order` | v1.59.0 | — | pass | never | B-45's remaining half |
| REQ-004 | `agent_sync.py check` exits 0 here for the first time — snapshot generated and linked | `2026-08-16-stamp-order` | v1.59.0 | — | pass | never | B-46 |
| REQ-005 | The shipped documentation gate runs on this repository, wired into `test:all`, and a guard requires the wiring | `2026-08-16-docgate-self` | v1.60.0 | — | pass | never | first execution here, ever |
| REQ-006 | Its two structural silences are gone — `[ -d .git ]` → `git rev-parse --is-inside-work-tree`, and the corpus root is resolved rather than assumed | `2026-08-16-docgate-self` | v1.60.0 | — | pass | never | both watched: the section printed `skip`, then ran |
| REQ-007 | Eleven unfollowable commit references resolved: two repointed to the squash commits carrying their work, nine enumerated by name with date and reason | `2026-08-16-docgate-self` | v1.60.0 | — | pass | never | gate now prints `every commit reference … resolves AND is reachable from HEAD` |
| REQ-008 | Two decisions that had propagated nowhere now cited by the documents they affect | `2026-08-16-docgate-self` | v1.60.0 | — | pass | never | DEC-0001, DEC-0004 |
| REQ-001 | The work graph's node contract gains `check` — how this node will be closed, required on every node except a `parked` one; `agents/verifier.md` runs it and its output is the evidence row | `2026-08-17-role-agent-graph` | unreleased | `8b7de18` | pass | never | B-080 · `npm test` exit 0, `graph_test.py` 129 cases, 8 plants watched refused through `test/negatives.py`; the four invalidators that would overtake this row are a change to `graph.schema.json`, to `violations()`, to `agents/verifier.md`, or to the eight plants |
