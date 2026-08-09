# Verification — task-pipeline

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

| REQ | What | Run | Shipped in | Auto | Human | Note |
|---|---|---|---|---|---|---|
| REQ-001 | `references/adoption.md` — doctrine + greenfield walkthrough + brownfi | `2026-08-03-default-routing-adoption` | v1.9.0 | pass | never | — |
| REQ-002 | The docgate floor comments state each floor's **kind** — `PROP_FLOOR`  | `2026-08-03-default-routing-adoption` | v1.9.0 | pass | never | — |
| REQ-003 | Trigger vocabulary widened (RU+EN work verbs) **and** an explicit *whe | `2026-08-03-default-routing-adoption` | v1.9.0 | pass | never | — |
| REQ-004 | Evals match the intended behaviour: exclusions kept, a new `should_tri | `2026-08-03-default-routing-adoption` | v1.9.0 | pass | never | — |
| REQ-005 | Global `CLAUDE.md` carries the routing rule with D2's boundary and the | `2026-08-03-default-routing-adoption` | v1.9.0 | pass | never | — |
| REQ-006 | agent-sync binding patched: config example **valid against `pipeline.s | `2026-08-03-default-routing-adoption` | v1.9.0 | pass | never | — |
| REQ-007 | `companion-skills.md` states the **agent-sync ≥ 1.3.0** floor for `fin | `2026-08-03-default-routing-adoption` | v1.9.0 | pass | never | — |
| REQ-008 | This repo adopts its own doc track: `docs/DOCMAP.md` recording D5, `sc | `2026-08-03-default-routing-adoption` | v1.9.0 | pass | never | — |
| REQ-009 | This run recorded in `evals/RESULTS.md` as the first observed instruct | `2026-08-03-default-routing-adoption` | v1.9.0 | pass | never | — |
| REQ-001 | `references/setup.md` — the entry audit: when it runs, what it inspect | `2026-08-03-setup-and-autonomy` | v1.10.0 | pass | never | — |
| REQ-002 | Stage 0 offers it **once** when the doc map is absent or stale; the an | `2026-08-03-setup-and-autonomy` | v1.10.0 | pass | never | — |
| REQ-003 | `/task-pipeline setup` is a documented branch of the command | `2026-08-03-setup-and-autonomy` | v1.10.0 | pass | never | — |
| REQ-004 | Self-currency: preflight compares the installed version against the re | `2026-08-03-setup-and-autonomy` | v1.10.0 | pass | never | — |
| REQ-005 | The escalation boundary: cost-of-being-wrong as the default rule, plus | `2026-08-03-setup-and-autonomy` | v1.10.0 | pass | never | — |
| REQ-006 | Term index: every domain term used in the docs resolves to one definit | `2026-08-03-setup-and-autonomy` | v1.10.0 | pass | never | — |
| REQ-007 | Stage 2 produces user paths, states and error paths as **design output | `2026-08-03-setup-and-autonomy` | v1.10.0 | pass | never | — |
| REQ-008 | Every new invariant has a guard **and** a negative self-test watched f | `2026-08-03-setup-and-autonomy` | v1.10.0 | pass | never | — |
| REQ-009 | Released, catalogue pinned, local installs refreshed through the launc | `2026-08-03-setup-and-autonomy` | v1.10.0 | pass | never | — |
| REQ-010 | `references/portability.md` — the manifest: every **workflow decision* | `2026-08-03-setup-and-autonomy` | v1.10.0 | pass | never | — |
| REQ-011 | The routing rule travels with the bundle: `templates/routing-rule.md`, | `2026-08-03-setup-and-autonomy` | v1.10.0 | pass | never | — |
| REQ-001 | `pipeline.schema.json` gains a `run` block with `loop` and `contextBud | `2026-08-04-run-continuity` | v1.11.0 | pass | never | — |
| REQ-002 | `references/continuity.md` exists and carries both halves | `2026-08-04-run-continuity` | v1.11.0 | pass | never | — |
| REQ-003 | The loop decision is **surfaced at launch**: preflight block in `SKILL | `2026-08-04-run-continuity` | v1.11.0 | pass | never | — |
| REQ-004 | `build.md`'s unconditional *"Continuous execution"* is reconciled with | `2026-08-04-run-continuity` | v1.11.0 | pass | never | — |
| REQ-005 | The context rule states its **evidence condition** and forbids announc | `2026-08-04-run-continuity` | v1.11.0 | pass | never | — |
| REQ-006 | `/loop` is documented with its **real** semantics — fixed short interv | `2026-08-04-run-continuity` | v1.11.0 | pass | never | — |
| REQ-007 | Every new guard has a negative self-test in `.github/workflows/validat | `2026-08-04-run-continuity` | v1.11.0 | pass | never | — |
| REQ-008 | The propagation matrix is walked: README map, portability manifest, Cu | `2026-08-04-run-continuity` | v1.11.0 | pass | never | — |
| REQ-009 | The context rule also lands in `~/.claude/CLAUDE.md`, **with the diff  | `2026-08-04-run-continuity` | v1.11.0 | pass | never | — |
| REQ-010 | `pipeline.example.json` ships `run` **explicitly off**, so the example | `2026-08-04-run-continuity` | v1.11.0 | pass | never | — |
| REQ-011 | `docs/DOCMAP.md` gains a propagation row for **a change to the config  | `2026-08-04-run-continuity` | v1.11.0 | pass | never | — |
| REQ-012 | Every relative link in a seeded template resolves **from the destinati | `2026-08-04-run-continuity` | v1.11.0 | pass | never | — |
| REQ-013 | The doctrine states what a loop fire does when the run is **parked at  | `2026-08-04-run-continuity` | v1.11.0 | pass | never | — |
| REQ-001 | `templates/hygiene.sh` exists and carries the full `docgate.sh` contra | `2026-08-05-artifact-hygiene` | v1.12.0^0 | pass | never | — |
| REQ-002 | Check 1 — conflict markers | `2026-08-05-artifact-hygiene` | v1.12.0^0 | pass | never | — |
| REQ-003 | Check 2 — placeholders, **with the false-positive surface solved** (A1 | `2026-08-05-artifact-hygiene` | v1.12.0^0 | pass | never | — |
| REQ-004 | Check 3 — unterminated fence | `2026-08-05-artifact-hygiene` | v1.12.0^0 | pass | never | — |
| REQ-005 | Check 4 — truncation stubs | `2026-08-05-artifact-hygiene` | v1.12.0^0 | pass | never | — |
| REQ-006 | Check 5 — duplicated adjacent block, the R-002 mechanisation | `2026-08-05-artifact-hygiene` | v1.12.0^0 | pass | never | — |
| REQ-007 | Check 6 — heading with no body | `2026-08-05-artifact-hygiene` | v1.12.0^0 | pass | never | — |
| REQ-008 | Two modes: diff at zero tolerance, tree behind a floor set to today's  | `2026-08-05-artifact-hygiene` | v1.12.0^0 | pass | never | — |
| REQ-009 | Doctrine: `build.md` runs it after each task; `stages.md` §5, §6 and § | `2026-08-05-artifact-hygiene` | v1.12.0^0 | pass | never | — |
| REQ-010 | The **fix obligation** is doctrine: a finding is fixed or explicitly c | `2026-08-05-artifact-hygiene` | v1.12.0^0 | pass | never | — |
| REQ-011 | `npm test` executes the gate over a seeded scratch project and require | `2026-08-05-artifact-hygiene` | v1.12.0^0 | pass | never | — |
| REQ-012 | A negative self-test per check in `.github/workflows/validate.yml`; `M | `2026-08-05-artifact-hygiene` | v1.12.0^0 | pass | never | — |
| REQ-013 | Propagation: `CHANGELOG.md`, `README.md`, `CONTRIBUTING.md` invariants | `2026-08-05-artifact-hygiene` | v1.12.0^0 | pass | never | — |
| REQ-014 | Four-way version sync at **1.12.0** | `2026-08-05-artifact-hygiene` | v1.12.0^0 | pass | never | — |
| REQ-001 | `spec.md` self-review gains **"every check this spec names resolves"** | `2026-08-05-spec-plan-quality` | v1.13.0^0 | pass | never | — |
| REQ-002 | `spec.md` requires a committed **`## Self-review`** section with compu | `2026-08-05-spec-plan-quality` | v1.13.0^0 | pass | never | — |
| REQ-003 | `spec.md` self-review gains the **decision read-back**: the brief's `# | `2026-08-05-spec-plan-quality` | v1.13.0^0 | pass | never | — |
| REQ-004 | `spec.md` self-review gains the **cost checkpoint**: print surfaces /  | `2026-08-05-spec-plan-quality` | v1.13.0^0 | pass | never | — |
| REQ-005 | `planning.md` self-review gains **"every command, path and file a DoD  | `2026-08-05-spec-plan-quality` | v1.13.0^0 | pass | never | — |
| REQ-006 | `planning.md` requires the same committed **`## Self-review`** section | `2026-08-05-spec-plan-quality` | v1.13.0^0 | pass | never | — |
| REQ-007 | `learned.md`'s stage map lists rule 14 at **stages 3 and 4**, not only | `2026-08-05-spec-plan-quality` | v1.13.0^0 | pass | never | — |
| REQ-008 | `references/stages.md` §3 and §4 gate criteria demand the `## Self-rev | `2026-08-05-spec-plan-quality` | v1.13.0^0 | pass | never | — |
| REQ-009 | Every new guard has a negative self-test in `.github/workflows/validat | `2026-08-05-spec-plan-quality` | v1.13.0^0 | pass | never | — |
| REQ-010 | Propagation walked: `CHANGELOG.md`, `CONTRIBUTING.md` → *The invariant | `2026-08-05-spec-plan-quality` | v1.13.0^0 | pass | never | — |
| REQ-011 | Four-way version sync at **1.12.0** | `2026-08-05-spec-plan-quality` | v1.13.0^0 | pass | never | — |
| REQ-001 | `conventions.md` states the method: the commands for conclusion and fa | `2026-08-06-ci-run-verified` | v1.16.2 | pass | never | — |
| REQ-002 | Three states named — concluded / in progress / no run found — so silen | `2026-08-06-ci-run-verified` | v1.16.2 | pass | never | — |
| REQ-003 | `stages.md` § 7, § 8 and § 9 gates require the run's verdict to be **r | `2026-08-06-ci-run-verified` | v1.16.2 | pass | never | — |
| REQ-004 | `pipeline.example.json`'s stage-8 gate check and `release.verify` requ | `2026-08-06-ci-run-verified` | v1.16.2 | pass | never | — |
| REQ-005 | Every new guard has a negative self-test, each proved plant-first (R-0 | `2026-08-06-ci-run-verified` | v1.16.2 | pass | never | — |
| REQ-006 | `README.md` and the Cursor rule state it; the rule stays self-containe | `2026-08-06-ci-run-verified` | v1.16.2 | pass | never | — |
| REQ-007 | `CHANGELOG.md` v1.16.0 + four-way version sync + `SKILL-CARD.md` | `2026-08-06-ci-run-verified` | v1.16.2 | pass | never | — |
| REQ-008 | `CONTRIBUTING.md` invariant citing a literal the validator prints; `po | `2026-08-06-ci-run-verified` | v1.16.2 | pass | never | — |
| REQ-009 | Released: tag `v1.16.0`, `release.yml` green, registry serves it, **an | `2026-08-06-ci-run-verified` | v1.16.2 | pass | never | — |
| REQ-001 | `knowledge-graph.md` states the measured-lag rule: the two exact git c | `2026-08-06-graph-staleness` | v1.15.0 | pass | never | — |
| REQ-002 | Three distinct signal states are named — `built_at_commit` (exact), `m | `2026-08-06-graph-staleness` | v1.15.0 | pass | never | — |
| REQ-003 | `knowledge-sources.md` says the graph row carries the measured lag, ** | `2026-08-06-graph-staleness` | v1.15.0 | pass | never | — |
| REQ-004 | `templates/brief.md`'s seeded ledger row shows the measured form, not  | `2026-08-06-graph-staleness` | v1.15.0 | pass | never | — |
| REQ-005 | `stages.md` stage-0 harvest line **and** its `GATE (manual)` criteria  | `2026-08-06-graph-staleness` | v1.15.0 | pass | never | — |
| REQ-006 | `pipeline.example.json` stage-0 `gate.check` requires the measured row | `2026-08-06-graph-staleness` | v1.15.0 | pass | never | — |
| REQ-007 | The existing code-graph guard at `test/validate.py:1405` is **extended | `2026-08-06-graph-staleness` | v1.15.0 | pass | never | — |
| REQ-008 | Every new guard has a negative self-test in `.github/workflows/validat | `2026-08-06-graph-staleness` | v1.15.0 | pass | never | — |
| REQ-009 | `README.md` and `cursor/rules/task-pipeline.mdc` state the measured fo | `2026-08-06-graph-staleness` | v1.15.0 | pass | never | — |
| REQ-010 | `CHANGELOG.md` gains a v1.15.0 section written as *what changed and wh | `2026-08-06-graph-staleness` | v1.15.0 | pass | never | — |
| REQ-011 | `references/portability.md`'s manifest homes this workflow decision | `2026-08-06-graph-staleness` | v1.15.0 | pass | never | — |
| REQ-012 | `CONTRIBUTING.md` gains the invariant, citing a literal the validator  | `2026-08-06-graph-staleness` | v1.15.0 | pass | never | — |
| REQ-013 | Released: tag `v1.15.0`, `release.yml` green, the registry serves it,  | `2026-08-06-graph-staleness` | v1.15.0 | pass | never | — |
| REQ-001 | `README.md` and `SKILL.md` no longer state a stale count of `learned.m | `2026-08-08-audit-followup` | v1.23.1^0 | pass | never | — |
| REQ-002 | `references/learned.md` → *Where these bind in the pipeline* names rul | `2026-08-08-audit-followup` | v1.23.1^0 | pass | never | — |
| REQ-003 | `evals/RESULTS.md` stops contradicting `evals/run.py` about dated runs | `2026-08-08-audit-followup` | v1.23.1^0 | pass | never | — |
| REQ-004 | `docs/DOCMAP.md` ratchets match the artefacts they describe | `2026-08-08-audit-followup` | v1.23.1^0 | pass | never | — |
| REQ-011 | `pipeline.json` exists, records `run.loop` and this program's stages,  | `2026-08-08-audit-followup` | v1.23.1^0 | pass | never | — |
| REQ-006 | The code graph is rebuilt at HEAD and the graph↔docs divergence check  | `2026-08-08-audit-followup` | v1.23.1^0 | pass | never | — |
| REQ-005 | The "computed, never restated" guard is a **registry** of (claim patte | `2026-08-08-audit-followup` | v1.23.1^0 | pass | never | — |
| REQ-012 | `chrome-devtools-mcp` is recommended for any project with a web fronte | `2026-08-08-audit-followup` | v1.23.1^0 | pass | never | — |
| REQ-007 | An honest retrospective entry records that v1.17.0–v1.23.0 shipped wit | `2026-08-08-audit-followup` | v1.23.1^0 | pass | never | — |
| REQ-008 | Abstention is one named, counted set printed beside every gate verdict | `2026-08-08-audit-followup` | v1.23.1^0 | pass | never | — |
| REQ-009 | `references/audit.md` carries a sixth rotation axis — *re-derive, don' | `2026-08-08-audit-followup` | v1.23.1^0 | pass | never | — |
| REQ-010 | `references/learned.md` has a retirement rule and a cap, analogous to  | `2026-08-08-audit-followup` | v1.23.1^0 | pass | never | — |
| REQ-013 | Every surface that states the retro's three acts states them **stamp → | `2026-08-08-audit-followup` | v1.23.1^0 | pass | never | — |
| REQ-001 | `artifacts.md` names both new files in **both** maps and in the single | `2026-08-09-planning-system` | v1.31.0 | pass | never | — |
| REQ-002 | `docs/superpowers/backlog.md` — seeded at stage 0 when absent, picked  | `2026-08-09-planning-system` | v1.31.0 | pass | never | — |
| REQ-003 | Any stage may append a row mid-run, same rule as the ledger: *deferred | `2026-08-09-planning-system` | v1.31.0 | pass | never | — |
| REQ-004 | Each loop iteration reads the board at the top and re-prioritises at t | `2026-08-09-planning-system` | v1.31.0 | pass | never | — |
| REQ-005 | Every carry-over row homed `backlog` resolves to a real board id — **b | `2026-08-09-planning-system` | v1.31.0 | pass | never | — |
| REQ-006 | `docs/superpowers/verification.md` — one row per REQ: shipped-in, auto | `2026-08-09-planning-system` | v1.31.0 | pass | never | — |
| REQ-007 | Stage 8 writes the row; stage 10 refuses a REQ with no row | `2026-08-09-planning-system` | v1.31.0 | pass | never | — |
| REQ-008 | The exposure index is computed and printed beside the verdict as a **d | `2026-08-09-planning-system` | v1.31.0 | pass | never | — |
| REQ-009 | `/task-pipeline checkup` runs **standalone**, with no task in flight | `2026-08-09-planning-system` | v1.31.0 | pass | never | — |
| REQ-010 | The index is never rendered as a probability or a percentage | `2026-08-09-planning-system` | v1.31.0 | pass | never | — |
