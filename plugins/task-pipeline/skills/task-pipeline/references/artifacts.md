# Artifact structure — the canonical layout

Every stage that produces a durable artifact writes it to the **same** place, so
a resumed or handed-off run always knows where to look. This is the recommended
structure; a host project may relocate roots via its `CLAUDE.md`, but keep the
shape.

## Contents

- In the host project
- Stage → input map — where each stage's information comes from
- Stage → artifact map
- This repo (task-pipeline itself), for reference

## In the host project

```
CONTEXT.md                            # stage 0 — domain glossary, written inline as terms resolve
scripts/check-docs.sh                 # stage 0 seeds it, 9 runs it, 10 proves it — the docs gate
docs/
  DOCMAP.md                           # stage 0 — the inventory: registers, homes, matrix, gates
  DECISIONS.md                        # the decision register (DEC-####), append-only …
  OPEN_QUESTIONS.md                   #   … and its questions (OQ-####) — never delete a resolved row
  adr/
    NNNN-<slug>.md                    # the OTHER permitted decision home — one project uses ONE
  superpowers/
    retro.md                          # stage 10's last act — ONE per project, not per run
    retro/YYYY-QN.md                  # the archive: rotated entries + retirements, queried not read
    specs/
      YYYY-MM-DD-<topic>-brief.md     # stage 0 — locked intake brief (grill output)
      YYYY-MM-DD-<topic>-carryover.md # stage 0 seeds it; EVERY stage appends; stage 10 reads it
      YYYY-MM-DD-<topic>-modules.md   # stage 2 — module map + build order (platforms only)
      YYYY-MM-DD-<topic>-design.md    # stage 3 — the spec / module dossier (locks shared contracts)
      YYYY-MM-DD-<topic>-acceptance.md # stage 10 — REQ coverage table + evidence
    plans/
      YYYY-MM-DD-<topic>.md           # stage 4 — the implementation plan
  ux/                                 # super-ux, UI tasks only (see companion-skills.md)
    foundation.md                     # WHY: personas, JTBD, CJM, stories
    flows.md                          # HOW: task analysis + user-flow diagrams
    screens.md                        # UI map: screens + states, wireframes, Figma frames
    scenarios.md                      # WHAT: scenarios (source of truth for behavior)
    audits/YYYY-MM-DD-<scope>.md       # ux-audit reports
    plans/YYYY-MM-DD-<scope>.md        # super-ux fix plans (may hand off to this pipeline)
    lint.py, README.md                 # seeded by super-ux
graphify-out/                          # git-ignored: the code graph, if one is built
  graph.json                           # stage 0 queries it; stage 9 refreshes it
  GRAPH_REPORT.md  graph.html          # the plain-language report + interactive view
  manifest.json  cache/                # extraction bookkeeping — never edited by hand
```

Naming: date-prefixed `YYYY-MM-DD-<topic>` slugs, one topic per file, kebab-case.
Brief, carry-over, design, plan and acceptance share the **same `<topic>` slug**, so the chain is traceable
at a glance.

> The `docs/superpowers/` directory name is this pipeline's historical convention
> (kept so existing projects don't have to migrate) — **not a dependency on any
> external skill**. A host project may relocate the root via its `CLAUDE.md`; keep
> the shape, keep the slugs.

Loop-bearing runs also keep a **git-ignored** run ledger at `.task-pipeline/run.md` —
stage-level and program-level repeat touches, one line each, so the loop guard can
detect churn after a lost context (see [`loop-guard.md`](loop-guard.md)).

Stage 5 also creates a **git-ignored** scratch workspace per plan at
`.task-pipeline/build/<plan-basename>/` — ledger, task briefs, implementer reports,
review packages. It is deleted when the final review is clean; git history is the
record (see `build.md`).

## Stage → input map — where each stage's information comes from

The map below this one answers *what a stage writes*. This one answers *what it
reads, and from where* — the direction that was missing, which is
[`learned.md`](learned.md) rule 2 (*compute the mapping in both directions*) applied
to this file itself. A stage whose inputs are unnamed is a stage that will read
whatever the context happens to hold.

| Stage | Reads | From where |
|---|---|---|
| **0 Harvest** | the project's own knowledge about this task | code · the code graph (`graphify-out/`) · `CLAUDE.md`/`AGENTS.md` · `CONTEXT.md`/`docs/adr/` · `docs/` + `docs/ux/` · past briefs and carry-over ledgers · **the board** (`docs/superpowers/backlog.md`, open count quoted in the brief) · **the verification ledger** (`docs/superpowers/verification.md`, how many rows sit at `never`) · the retro's standing instructions **in full** · the wiki · any doc repo or hosted system the project names |
| **0 Inventory (1b)** | the documentation regime | `docs/DOCMAP.md` — registers, single homes, propagation matrix, gate commands, ratchet floors. Absent ⇒ seeded ([`adoption.md`](adoption.md)) |
| **0 Reconcile (1c)** | intent vs as-built | git (how it *should* be) against the run record (how it *turned out*) |
| **0 Grill** | the operator | the interview — every answer checked against the harvest, which is what makes it checkable rather than confident |
| **1 Docs study** | external library/API contracts | `context7:resolve-library-id` → `context7:query-docs`; web search where it cannot resolve. **Never from recall** |
| **2 Brainstorm** | what is already settled | the brief (scope, constraints, done-criteria) + the codebase. Re-asking what the grill answered is this stage's most common waste |
| **3 Spec** | the approved design + the UX chain | stage-2 design · `docs/ux/{foundation,flows,screens,scenarios}.md` (UI only) · the Figma canonical record in `docs/ux/foundation.md` → *Design tooling* · `DOCMAP.md` for where a settled contract is recorded |
| **4 Plan** | the spec and the frozen list | the spec's locked contracts and **Global Constraints** · the brief's REQ ids (the gate is a set comparison against them) |
| **5 Dev** | one task at a time | the plan task · the spec's Global Constraints, copied verbatim · host test/lint commands · the brief's branch policy. **A subagent reads only its own file-based brief** — that is the whole of its context |
| **6 Tests** | the host's runner | `CLAUDE.md`/`AGENTS.md` → *Lint + test*, else detection ([`conventions.md`](conventions.md)) |
| **7 Lint + deploy** | the host's lint and deploy path, and the authorization | host conventions · the brief's autonomy sweep, where a standing go must name target **and** preconditions |
| **8 Post-deploy** | where health lives | the brief's autonomy sweep (app name, endpoint, workflow) |
| **9 Docs + registers** | two different lists | the stage-0 **source ledger** (what this run *read*) **and** `DOCMAP.md`'s **propagation matrix** (what this run *owes*). They are not the same list, and the gap between them is where documentation rots |
| **10 Acceptance** | everything the run produced | the brief's REQ table · the carry-over ledger **in full** · plan task statuses · `git log` · the final suite output · stage-8 notes · stage-9 changes · `docs/ux/scenarios.md` + `/ux-lint` for UI |

### Project-saved rules, and where each one binds

These are the files a **host project** owns that change how a run behaves. An agent
that has not read them is running the pipeline's defaults, not this project's.

| Rule file | What it binds | Read at | Enforced at |
|---|---|---|---|
| `CLAUDE.md` / `AGENTS.md` | commands, deploy path, house rules, which docs exist and where | 0 | 6–10 |
| `docs/DOCMAP.md` | the decision home, each fact's single home, the propagation matrix, the gate and its ratchet floors | 0 (1b) | 9 |
| `docs/superpowers/verification.md` | one row per shipped REQ, and the one column a machine may not fill: the date a **human** confirmed it, or `never` ([`verification.md`](verification.md)) | 0 | written at 8, required at 10 |
| `docs/superpowers/backlog.md` | the project's work-list **between** runs — ids, the three priority inputs, state. Mutable; rows leave only into its *Closed* list ([`backlog.md`](backlog.md)) | 0 | re-derived at every iteration's end; resolved at 10 |
| `docs/superpowers/retro.md` | standing instructions — the rules no check can decide. Capped at ten, **read in full**, stamped the moment one fires | 0 | pruned at 10 |
| `specs/<topic>-brief.md` → *Autonomy* | every pre-resolved decision; stages 1→10 **answer from it instead of asking** | 0 | 1–10 |
| `specs/<topic>-carryover.md` | everything deferred, parked or half-done; appended the moment it is said | all | read in full at 10 |
| `docs/ux/scenarios.md` | the source of truth for user-facing behaviour (super-ux) | 3 | 3, 7, 9, 10 |
| `.claude/agent-sync.json` | which registers are guarded, and by whose lease | 0 | every guarded write |
| the operator's global `CLAUDE.md` | whether a task routes here at all, and the opt-out phrase | before stage 0 | — |

**Precedence when two of them disagree.** For *what is*: code, then host docs and
ADRs, then the wiki, then memory. For *what should be*: the register outranks the
code, because a decision not yet built is still the decision — and the gap between
them is a finding, not a tie-break ([`knowledge-sources.md`](knowledge-sources.md)).

## Stage → artifact map

| Stage | Writes | Consumed by |
|---|---|---|
| 0 Harvest | the brief's **Knowledge sources** ledger — every source consulted, its freshness, whether this run makes it stale | the grill (validation), **stage 9** (the update work list) |
| 0 Intake | `specs/<topic>-brief.md` — incl. the **REQ table** (seed from `templates/brief.md`) | stages 2–5, 7, 10 |
| 0→10 all | `specs/<topic>-carryover.md` — append-only ledger (seed from `templates/carryover.md`) | stage 10, in full |
| 10 Acceptance | `specs/<topic>-acceptance.md` — every REQ with a status and evidence | the operator |
| 10 Retro | `superpowers/retro.md` — standing instructions (max 10), the problem→cause→fix log, run stamps. Pruned **before** anything is added (`retrospective.md`) | **stage 0 of the next run**, in full |
| 0 Inventory | `docs/DOCMAP.md` + the registers + `scripts/check-docs.sh` — seeded **only when absent**, and the seeding is the register's first entry ([`documentation.md`](documentation.md)) | every later stage; **stage 9** walks the matrix, **stage 10** proves the gate |
| 0 Grill (domain) | `CONTEXT.md`, `docs/adr/NNNN-<slug>.md` — created **lazily**, only when a term resolves or a decision qualifies. Where `docs/adr/` **is** the register, entries carry the register's field set | stages 2–4 + the repo |
| any stage | a register entry per settled thing, via the **Doc Loop** — recorded, resolved, propagated, committed with its id | the next run's harvest |
| 8 Verification row | `docs/superpowers/verification.md` — one row per REQ the run shipped, written right after the deploy verification; `Human` starts at `never` ([`verification.md`](verification.md)) | stage 10 requires it; stage 0 of every later run reads it |
| 10 Board resolution | `docs/superpowers/backlog.md` — every unresolved ledger row — homed `backlog` or still `open` — arrives with a real id, and the ledger row is updated to name it; priority re-derived ([`backlog.md`](backlog.md)) | the next run's harvest, and every loop iteration |
| 10 Retro rotation | `docs/superpowers/retro/YYYY-QN.md` — entries older than five stamps, plus every retirement, each with its commit | queried by a later run's harvest |
| 2 Decompose | `specs/<topic>-modules.md` — module map, build order, contracts, per-module status (platforms only) | stages 3–10, every module's run |
| 3 Spec | `specs/<topic>-design.md` — module dossier for a decomposed platform (+ links `docs/ux/*` for UI) | stage 4 |
| 4 Plan | `plans/<topic>.md` | stage 5 |
| 3 UX track | `docs/ux/{foundation,flows,screens,scenarios}.md` | stages 4–9 + `/ux-lint` |
| 8 Post-deploy | log/health notes (in the run, not a committed file) | stage 9 |
| 9 Docs+wiki | host module docs + wiki pages + the refreshed `graphify-out/graph.json` (`knowledge-graph.md`) | the **next** run's stage-0 harvest |

## This repo (task-pipeline itself), for reference

```
.claude-plugin/marketplace.json               # marketplace manifest
plugins/task-pipeline/
  .claude-plugin/plugin.json                  # plugin manifest
  commands/task-pipeline.md                   # /task-pipeline
  skills/task-pipeline/
    SKILL.md                                  # the orchestrator itself
    pipeline.schema.json                      # generic pipeline contract
    pipeline.example.json                     # this plugin's own flow, as config
    references/                               # built-in stage doctrine:
      knowledge-sources.md grill.md           #   stage 0 (harvest, then interview)
      knowledge-graph.md                      #   stages 0+9: the code graph, refresh, divergence
      brainstorm.md decomposition.md          #   stage 2
      spec.md planning.md                     #   stages 3-4
      build.md review.md tdd.md               #   stages 5-6
      acceptance.md retrospective.md          #   stage 10 (close-out, then the retro)
      audit.md                                #   cross-cutting: the ladder + seams
      loop-guard.md                           #   cross-cutting: churn detection
      stages.md model-tiering.md              #   gates, model policy
      conventions.md artifacts.md             #   host conventions, this layout
      companion-skills.md                     #   optional companions + preflight
    templates/                                # skeletons seeded into a host project
      hygiene.sh                            # -> scripts/check-hygiene.sh (stages 5, 6, 9)
      README.md brief.md carryover.md context.md adr.md retro.md
cursor/rules/task-pipeline.mdc                # Cursor channel (self-contained rule)
bin/task-pipeline.js                          # npx installer (package task-pipeline-skill)
install.sh                                    # POSIX installer
test/validate.py                              # structural validator (npm test)
.github/workflows/{validate,release}.yml      # CI + toggleable release automation
.github/ISSUE_TEMPLATE/  .github/PULL_REQUEST_TEMPLATE.md
package.json  .gitignore
README.md  CHANGELOG.md  LICENSE  CLAUDE.md
CONTRIBUTING.md  SECURITY.md  CODE_OF_CONDUCT.md
docs/superpowers/{specs,plans}/               # this repo's own design history
```
