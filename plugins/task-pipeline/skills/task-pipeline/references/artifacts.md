# Artifact structure — the canonical layout

Every stage that produces a durable artifact writes it to the **same** place, so
a resumed or handed-off run always knows where to look. This is the recommended
structure; a host project may relocate roots via its `CLAUDE.md`, but keep the
shape.

## In the host project

```
CONTEXT.md                            # stage 0 — domain glossary, written inline as terms resolve
docs/
  adr/
    NNNN-<slug>.md                    # stage 0 — ADRs for hard-to-reverse decisions
  superpowers/
    specs/
      YYYY-MM-DD-<topic>-brief.md     # stage 0 — locked intake brief (grill output)
      YYYY-MM-DD-<topic>-carryover.md # stage 0 seeds it; EVERY stage appends; stage 10 reads it
      YYYY-MM-DD-<topic>-acceptance.md # stage 10 — REQ coverage table + evidence
      YYYY-MM-DD-<topic>-design.md    # stage 3 — the spec (locks shared contracts)
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
```

Naming: date-prefixed `YYYY-MM-DD-<topic>` slugs, one topic per file, kebab-case.
Brief, carry-over, design, plan and acceptance share the **same `<topic>` slug**, so the chain is traceable
at a glance.

> The `docs/superpowers/` directory name is this pipeline's historical convention
> (kept so existing projects don't have to migrate) — **not a dependency on any
> external skill**. A host project may relocate the root via its `CLAUDE.md`; keep
> the shape, keep the slugs.

Stage 5 also creates a **git-ignored** scratch workspace per plan at
`.task-pipeline/build/<plan-basename>/` — ledger, task briefs, implementer reports,
review packages. It is deleted when the final review is clean; git history is the
record (see `build.md`).

## Stage → artifact map

| Stage | Writes | Consumed by |
|---|---|---|
| 0 Intake | `specs/<topic>-brief.md` — incl. the **REQ table** (seed from `templates/brief.md`) | stages 2–5, 7, 10 |
| 0→9 all | `specs/<topic>-carryover.md` — append-only ledger (seed from `templates/carryover.md`) | stage 10 |
| 10 Acceptance | `specs/<topic>-acceptance.md` — every REQ with a status and evidence | the operator |
| 0 Grill (domain) | `CONTEXT.md`, `docs/adr/NNNN-<slug>.md` — created **lazily**, only when a term resolves or a decision qualifies | stages 2–4 + the repo |
| 3 Spec | `specs/<topic>-design.md` (+ links `docs/ux/*` for UI) | stage 4 |
| 4 Plan | `plans/<topic>.md` | stage 5 |
| 3 UX track | `docs/ux/{foundation,flows,screens,scenarios}.md` | stages 4–9 + `/ux-lint` |
| 8 Post-deploy | log/health notes (in the run, not a committed file) | stage 9 |
| 9 Docs+wiki | host module docs + wiki pages | — |

## This repo (task-pipeline itself), for reference

```
.claude-plugin/marketplace.json              # marketplace manifest
plugins/task-pipeline/
  .claude-plugin/plugin.json
  commands/task-pipeline.md                   # /task-pipeline
  skills/task-pipeline/
    SKILL.md
    pipeline.schema.json                      # generic pipeline contract
    pipeline.example.json                     # this plugin's own flow, as config
    references/{grill,brainstorm,spec,planning,build,review,tdd,acceptance}.md  # built-in stage doctrine
    references/{stages,model-tiering,conventions,artifacts,companion-skills}.md
cursor/rules/task-pipeline.mdc                # Cursor channel (self-contained rule)
plugins/task-pipeline/skills/task-pipeline/templates/{brief,carryover,context,adr}.md   # stage-0 skeletons (ship on every channel)
bin/task-pipeline.js                          # npx installer (package task-pipeline-skill)
package.json
install.sh                                    # POSIX installer
test/validate.py                              # structural validator
.github/workflows/{validate,release}.yml      # CI + toggleable release
README.md  CHANGELOG.md  LICENSE
docs/superpowers/{specs,plans}/               # this repo's own design history
```
