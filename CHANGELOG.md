# Changelog

## v0.9.0 — 2026-07-23

Full structural parity with the sibling `super-ux` per the ssheleg skill canon
(make-skill): the Cursor channel and a templates dir were the last gaps.

- **Cursor channel.** New `cursor/rules/task-pipeline.mdc` — a self-contained,
  agent-requested rule (`alwaysApply: false` + a trigger `description`, no external
  links so it survives being copied into any project) that carries the full
  intake-grill + 9-stage discipline and the super-ux recommendation. Install
  globally via `npx skills add ssheleg/task-pipeline --agent cursor --global`, or
  copy per project into `.cursor/rules/`.
- **Templates dir.** New `templates/brief.md` — the stage-0 intake-brief skeleton
  this plugin seeds into `docs/superpowers/specs/…-brief.md` (create-if-absent,
  never overwrite), plus `templates/README.md` mapping template → destination →
  stage. Spec/plan and `docs/ux/*` skeletons remain owned by superpowers / super-ux.
- **Validator + packaging.** The validator now checks every `cursor/rules/*.mdc`
  has `description` + `alwaysApply` frontmatter and that `templates/brief.md`
  exists; `package.json` `files` ships `cursor` and `templates`. All prior gates
  (four-way version sync, config conformance, gate types, release shape, links)
  retained.
- **Docs.** README gains a Cursor install block and an "Updating everywhere" table
  (one channel per agent — the plugin+plain duplicate caveat spelled out);
  `references/artifacts.md` and stage 0 reference the brief template.

## v0.8.1 — 2026-07-23

- Docs consistency: the SKILL.md super-ux intro now lists the full current chain
  (`/ux`, `ux-foundation`, `ux-flows`, `ux-scenarios`, `/ux-lint`) instead of the
  pre-flows subset, matching the stage-3 table and `companion-skills.md`. Wiki
  synced to the current architecture.

## v0.8.0 — 2026-07-23

Project-configurable release automation, super-ux embedding refreshed to its
current chain, a locked artifact structure, a companion-skills preflight, and a
full contradiction sweep.

- **Release automation — project-configurable & individually toggleable.** New
  optional `release` block in `pipeline.schema.json` (master `enabled` toggle,
  `trigger`, project-defined `steps`, `verify` smoke-checks) with the repo's own
  config in `pipeline.example.json`. Reference implementation
  `.github/workflows/release.yml` is **off unless armed** per repo via the
  `RELEASE_ENABLED` variable; when on it validates the tag ↔ manifest version,
  cuts a GitHub release from the CHANGELOG, and smoke-tests `npx` from a clean
  checkout — closing the previously-manual post-deploy gap. Validator shape-checks
  the block and enforces that `enabled:true` ships the workflow.
- **super-ux embedding updated to super-ux's current chain.** The stage-3 UX
  track now walks `/ux` → `ux-foundation` (WHY) → `ux-flows` (flows + `screens.md`,
  Figma frames) → `ux-scenarios` (WHAT) → **`/ux-lint`** (`docs/ux/lint.py`, must
  pass), reflecting super-ux ≥0.17 (flows/screens layers, linter, Figma). The
  linter is wired into stage 7 (lint) and stage 9 (same-change), and stage-4 DoD
  now carries `SCR-` screens alongside scenario IDs.
- **Entry-from-super-ux short-circuit.** When launched *from* super-ux (its `/ux`
  hand-off, UX chain already built), stage 0 detects the existing validated
  chain/plan and **skips the grill + UX rebuild** — it verifies (`/ux-lint`
  green), confirms scope in one line, and resumes at the first stage with real
  work. super-ux skills are treated as idempotent (reuse, never rebuild).
- **Companion-skills preflight.** New `references/companion-skills.md`: a matrix
  of what powers each stage (superpowers, super-ux, grill-me, context7,
  wiki-update) with install lines and a preflight recommendation block emitted
  before stage 0, so the operator can arm the full flow up front. super-ux install
  lines are surfaced the moment a UI task is detected.
- **Locked artifact structure.** New `references/artifacts.md` fixes the canonical
  `docs/superpowers/{specs,plans}` + `docs/ux/*` layout, the stage→artifact map,
  and this repo's own structure — so every stage writes to the same place.
- **Contradiction sweep.** Manifest descriptions (marketplace/plugin/package) and
  the "9 stages" wording in README + SKILL.md now account for stage 0; the v0.1.0
  spec/plan carry *historical snapshot* banners; model tiering marks 0–4 Fable;
  `conventions.md` covers the super-ux linter and the release block.

## v0.7.0 — 2026-07-23

Front-loaded **intake grill** (stage 0) + super-ux promoted to a recommended,
auto-detected workflow for any user-facing task.

- **New stage 0 — Intake grill (Fable, manual gate).** Before any technical work,
  the pipeline interviews the operator relentlessly — one question per turn, a
  recommended answer with each, exploring the codebase/docs before asking — until
  every decision branch is resolved and locked into a committed **task brief**
  (`docs/superpowers/specs/…-brief.md`). This expands a one-line request into a
  complete input so stages 1→9 run autonomously (only the built-in gates pause).
  Inspired by [Matt Pocock's grill-me](https://github.com/mattpocock/skills);
  uses the `grill-me` / `grilling` skill if it resolves, else a built-in grill
  loop (no hard dependency). The 5 grill rules + stopping condition are embedded
  in `references/stages.md`.
- **super-ux recommended for ANY user-facing task.** The stage-0 grill detects a
  UI surface (web/mobile/CLI/TUI) early and surfaces super-ux immediately: **use
  it if installed**, otherwise print the install line on the spot
  (`/plugin marketplace add ssheleg/super-ux` → `/plugin install super-ux@super-ux`,
  or `npx skills add ssheleg/super-ux`). The stage-3 UX track (`/ux` →
  `ux-foundation` CJM → `ux-scenarios`) is unchanged; the spec gate still requires
  it for UI tasks.
- **Docs synced:** SKILL.md gains the intake overview, a strengthened super-ux
  block (recommended / use-if-installed / install-now) and an optional grill-me
  note; stages table + `pipeline.example.json` gain stage 0; model tiering marks
  0–4 as Fable; the `/task-pipeline` command and README (EN + RU) describe the
  grill-first flow.

## v0.6.0 — 2026-07-23

Typed gates + generic pipeline contract (merged the good ideas from the `os`
branch onto main, **keeping** the v0.5.0 UX track, the npm installer, and CI).

- **Typed gates:** every gate is now tagged `auto` (the orchestrator verifies the
  check itself, pass/fail) or `manual` (wait for the operator's explicit go).
  SKILL.md gained a **Type** column; `stages.md` tags each gate; SKILL.md's
  *How to run* spells out honoring the type (an auto gate never substitutes for a
  required manual approval). Default assignment: 2/3/7 manual, the rest auto.
- **Generic config contract:** new **`pipeline.schema.json`** (universal contract —
  ordered `stages[]`, each with `skills[]` + `gate{type,check}`; no fixed stage
  count, no baked-in skills) and **`pipeline.example.json`** (this plugin's own
  9-stage flow as config, UX track included). New *Bring your own skills* section:
  a host project copies the example to `pipeline.json` and rewrites it with its
  own stages/agents/gate-types.
- **Validator:** checks the schema is well-formed and the example conforms — a
  dependency-free shape check (states unique, `skills[]` non-empty, `gate.type` in
  {auto,manual}, `gate.check` present) plus a full `jsonschema` pass when the
  library is available. All prior checks (four-way version sync, command
  frontmatter, relative links, npm bin) retained.
- **Retained from main (not regressed by the merge):** the super-ux UX track
  (stage-2 UI detection, stage-3 `/ux`→`ux-foundation` CJM→`ux-scenarios`,
  scenario IDs in stage-4 DoD), `bin/task-pipeline.js` + `package.json`, and the
  CI workflow with its negative self-test.

## v0.5.0 — 2026-07-20

UX track: scenario-first design for user-facing tasks, built on
[super-ux](https://github.com/ssheleg/super-ux).

- **Stage 2 (Brainstorm)** now includes a mandatory **UI detection** check —
  records whether the task touches a user-facing surface (web/mobile/CLI/TUI);
  the verdict arms the UX track and is part of the stage gate.
- **Stage 3 (Spec)** gains a conditional **UX track that runs before the spec**
  (and therefore before any plan): `/ux` setup check → `ux-foundation`
  (personas, JTBD, **customer journey maps**, user stories) → `ux-scenarios`
  (usage scenarios drafted + validated per ux-contract v2, traced to
  foundation). Spec must embed the UX layer: scenario IDs, CJM stages served,
  applicable UX patterns/quality bars. Gate extended accordingly; super-ux
  missing on a UI task → install instructions + stop.
- **Stage 4 (Plan)** gate extended: UI tasks name the scenario ID(s) they
  implement; DoD includes satisfying them.
- README (EN + RU): UX track section; super-ux added to prerequisites.

## v0.4.0 — 2026-07-19

npm installer.

- **`bin/task-pipeline.js`** — zero-dependency Node installer CLI (mirrors
  `install.sh`: skill → `~/.claude/skills/task-pipeline`, command →
  `~/.claude/commands/`; idempotent, overwrite only behind `--force`).
- **`package.json`** — package name **`task-pipeline-skill`** (unscoped
  `task-pipeline` is taken on npm); bin command stays `task-pipeline`;
  `files` whitelist ships `bin` + `plugins`. Works without npm publish via
  `npx github:ssheleg/task-pipeline`; after publish also `npx task-pipeline-skill`.
- **Version sync is now four-way** (marketplace.json, plugin.json,
  package.json, CHANGELOG top entry) — validator enforces, plus checks the
  bin entry resolves and the files whitelist ships the skill sources.
- **CI:** `node --check` + a functional install run (fresh → rerun-skip →
  `--force`) against a fake `$HOME`.

## v0.3.0 — 2026-07-19

Packaging/tooling alignment with the ssheleg skill-repo canon (make-skill).

- **CI:** `.github/workflows/validate.yml` runs the structural validator on every
  push/PR, plus a **negative self-test** — corrupts a copy of the repo and expects
  the validator to FAIL (a validator that can't fail is decoration) — and a
  `bash -n` syntax check of `install.sh`.
- **Validator hardened:** now also enforces command frontmatter
  (`description` + `argument-hint`), **CHANGELOG top-entry version sync** with the
  manifests, and resolution of every relative markdown link in the repo.
- **`install.sh` is idempotent:** reruns skip already-installed skill/command;
  destructive overwrite only behind `--force` (never silently `rm -rf`s an
  existing install).
- **`/task-pipeline` is an idempotent entry point:** detects an existing pipeline
  TaskList and resumes from the first incomplete stage instead of restarting.
- **README:** added the `npx skills add ssheleg/task-pipeline` install path
  (vercel-labs skills CLI, 70+ agents) and a closing Russian section.

## v0.2.0 — 2026-07-18

- Added a dedicated **Tests** stage (new stage 6, model Opus) between Dev and
  Lint/deploy: writes tests for new functionality, updates/repairs existing tests
  touched by the change, and adds edge-case + failure-path coverage.
- Hard **full-suite-green gate before deploy** — the deploy stage now requires both
  lint clean and the whole suite green; never advances on a red or partial run.
- Pipeline grew 8 → 9 stages; deploy/post-deploy/docs renumbered 7/8/9. Model
  tiering: Fable 1–4, Opus 5–6, inherit 7–9. Docs/tables/references synced.
- Added a real `/task-pipeline` slash command (`commands/task-pipeline.md`);
  `install.sh` now installs it to `~/.claude/commands/` alongside the skill so the
  command works for the plain-skill path too.
- Validator hardened: enforces marketplace↔plugin.json **version sync** and the
  presence of the command file.

## v0.1.0 — 2026-07-18

Initial release.

- Thin orchestrator skill that runs a task through 8 gated stages (docs study →
  brainstorm → spec → plan → subagent build → lint/deploy → post-deploy log check
  → docs/wiki sync), built on the [superpowers](https://github.com/obra/superpowers) skills.
- Hybrid distribution: Claude Code plugin/marketplace + plain `~/.claude/skills` copy.
- Soft per-stage model tiering (Fable stages 1–4, Opus stage 5, inherit 6–8) — reminder only.
- Generic-portable: stages 6–8 read the host project's `CLAUDE.md` conventions with detection fallbacks.
- Structural validator (`test/validate.py`); spec + plan under `docs/superpowers/`.
