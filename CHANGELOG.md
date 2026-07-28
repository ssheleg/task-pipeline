# Changelog

## v0.16.0 — 2026-07-28

Scope stops leaking. The request becomes an addressable list of requirements, the
ids are traced through every stage, and a new final stage accounts for all of them.

The failure this fixes: every gate up to now asked *"is this artifact good?"* and
none asked *"does this still contain everything that was asked for?"* Scope doesn't
leak inside a stage — it leaks on the **seams**, because brief → spec → plan → task
briefs is four rewrites by a model and nothing compared the lists.

### Added
- **The REQ spine.** The grill's second hard output is a requirement table in the
  brief — one row per *independently verifiable* deliverable, each naming **how it
  is verified** (test name, `file:line`, command + expected output, scenario id). A
  requirement you can't say how to verify is a badly-stated requirement, and gets
  split during the grill rather than discovered at the end. One REQ = one
  deliverable, not one per sentence: an inflated table is ignored, and an ignored
  table protects nothing.
- **Traceability through the run.** Spec sections carry `covers: REQ-…`; plan tasks
  carry `Implements: REQ-…`; the implementer's task brief quotes the requirement
  statement **verbatim**, so it optimises the requirement and not just the
  instruction; the review rubric gains a verdict beside spec-compliance and
  code-quality — **does this satisfy its REQ?**
- **Stage 10 — Acceptance** (`references/acceptance.md`, manual gate). Closes the
  circle: every REQ gets `verified` / `partial` / `deferred` / `dropped`, written to
  `specs/<topic>-acceptance.md`. `verified` **requires evidence** — a passing test
  name, a `file:line`, a command and its output. "Done" without evidence is
  downgraded to `partial`, never upgraded. Then the operator is asked the closing
  question out loud, list in hand: *here's what you asked for, here's what shipped,
  here's what's deferred and where it lives — what's missing?* Asked even when the
  table is green. Manual by design: an automated check can prove the table is
  well-formed; only the person who asked can confirm it is what they asked for.
- **The carry-over ledger** (`templates/carryover.md`) — append-only, seeded at
  stage 0, written by every stage, read in full at stage 10. Implementer concerns
  and parked review findings are harvested into it before the scratch workspace is
  deleted. The rule: **deferred out loud is forgotten** — a row with no home
  (issue, backlog, or an agreed `dropped`) blocks the acceptance gate.

### Changed
- **The brief→plan seam is now mechanical.** Stage 4's gate is **set equality**
  between the brief's REQ ids and the union of `Implements:` across plan tasks. A
  non-empty difference fails the gate and is reported as the explicit list of
  dropped requirements — a comparison, not a judgement call.
- **No silent narrowing.** The REQ list is frozen once confirmed: adding mid-run is
  free, **removing or narrowing needs the operator's explicit agreement**, recorded
  in the ledger. Quietly restating the task smaller is the subtlest loss, because
  every later gate then passes honestly on a task that shrank without anyone
  deciding it should.
- **Gates tightened** — stage 0 requires the REQ table and a seeded ledger; stage 2
  requires the design to answer every REQ (or an operator-agreed drop); stage 3
  requires `covers:` on every section; stage 5 harvests concerns into the ledger;
  **stage 7 refuses to deploy while any REQ is still `open`** (a `partial` ships only
  with explicit acceptance — a gap is cheapest to close before it ships).

### Tests
- `references/acceptance.md` joins the built-in doctrine set (stub-rejected);
  `templates/carryover.md` required; the brief template must carry
  `## Requirements`, a `REQ-NNN` row and the verification column; the shipped flow's
  last stage must be `acceptance` with a **manual** gate whose check demands
  evidence; the plan gate must state the set comparison.
- Nine new invariants, each verified to fail on a broken copy; four added to CI as
  negative self-tests.

## v0.15.0 — 2026-07-28

Coherence pass over the v0.13.0 port: three contradictions resolved, three gaps
closed, and the config's gate text re-synced with the doctrine.

### Fixed
- **Model policy contradicted itself.** `build.md` and `review.md` told the final
  whole-branch review to run "on the most capable model available" while
  `model-tiering.md` promises **one** model per run. Both now default to the run's
  confirmed model; when the run sits below the top tier, escalation for that single
  review (and for fix-loop rounds 4–5) is **offered out loud**, never switched
  silently, and only the operator's recorded override map authorizes a cheaper tier.
- **Parallel groups were planned and then forbidden.** `planning.md` mandates
  dependency-ordered parallel groups with exclusive file ownership; `build.md` said
  "never dispatch implementers in parallel". New §4.2 states the real rule: default
  sequential, fan out only when the tasks share a group, own disjoint files **and**
  each implementer gets its own worktree; integrate the worktrees one at a time; any
  merge conflict means the plan's ownership was wrong — fall back to sequential and
  record it. The fix loop never fans out.
- **Scratch dirs could land in a task's diff.** The isolation snippet now ignores
  **and commits** both `.worktrees/` and `.task-pipeline/` before anything is
  created.

### Added
- **Stage 5 now ends with integration.** Sync with the base branch, re-run the full
  suite on the merged result (green-in-isolation is not green), land it the
  project's way — merge, or a PR, which is outward and needs a go — never
  force-push a shared branch, never land on `main` when the brief forbids it, then
  remove the worktree. Stages 7–9 lint, deploy and document the integrated result,
  so "leave it unmerged" is allowed but must be recorded. The stage-5 gate, the
  stage table, the Cursor rule and the example config carry the new condition.
- **Inline execution mode.** A harness without subagents (or a plan too small to be
  worth dispatching) runs the same loop inline: same isolation, ledger, TDD and
  review rubric applied to your own diff — declared out loud, since a self-review is
  weaker evidence than a fresh reviewer's. Replaces the capability that
  `superpowers:executing-plans` used to cover.
- **Grill + brief sweep row for integration** — how the branch lands (merge / PR +
  approver / "leave it") and whether parallel fan-out is wanted, so stage 5 never
  stops to ask.

### Changed
- The implementer contract spells the TDD loop out inline instead of pointing a
  zero-context subagent at a file it can't resolve, and the plan header no longer
  cites a skill-internal path.
- `pipeline.example.json` gate text for stages 4, 5 and 6 re-synced with
  `references/stages.md`; stage 4's gate now also names type/name consistency and
  the per-task DoD.
- `review.md` defines `$WORKSPACE` where it first uses it; `build.md` §4 subsections
  renumbered after the insert.

## v0.14.0 — 2026-07-28

### Fixed
- Skill front-matter was **1039 characters**, over the 1024 canon limit, and the
  validator did not check it. Description tightened to 996 and the limit is now
  enforced.

### Changed
- Triggers restructured English-first — `'run this through the pipeline' /
  'прогони по конвейеру'` — in both the skill and the Cursor rule.
- README is English-only, with a plain statement of what the pipeline gives you
  and an author/links block.

### Added
- Validator enforces the description canon: `Use when` opening, Russian trigger
  aliases present, front-matter under 1024 characters.

## v0.13.0 — 2026-07-28

The last external dependency is gone. Every stage now runs on doctrine that ships
inside the skill — the pipeline installs and runs with nothing else present.

- **superpowers is no longer a prerequisite.** The preflight no longer resolves
  `superpowers:*`, the "install this or stop" branch is deleted, and no stage can
  fail because a companion plugin is missing. `Prerequisites` in SKILL.md and the
  README now read "none required".
- **Six new built-in references carry stages 2→6:**
  - `references/brainstorm.md` — stage 2: read the brief first, explore, scope-check
    for decomposition, one question at a time, 2–3 approaches with a recommendation,
    YAGNI, design approved section by section. The **hard gate** (no code, no
    scaffolding before approval, including on "obviously simple" tasks) is explicit.
  - `references/spec.md` — stage 3: UX-track order, what the spec must lock (types,
    schemas, signatures, file layout) plus the **Global Constraints** block stages
    4–5 consume verbatim, the self-review pass, the operator-review gate.
  - `references/planning.md` — stage 4: zero-context task format, dependency graph,
    parallel groups with exclusive file ownership, required plan header and task
    structure, the no-placeholders list, the self-review checklist.
  - `references/build.md` — stage 5: worktree detection (submodule guard, native
    tool first, ignored-directory check, baseline tests), a git-ignored ledger at
    `.task-pipeline/build/<plan>/progress.md` that survives compaction, the
    file-based dispatch contract, the four implementer statuses, the five-round fix
    loop with its breaker and adjudication rules, and the single final fix wave.
  - `references/review.md` — the review rubric (spec compliance, correctness,
    constraints, test honesty, degradation, boundaries, security, docs-same-change),
    severity ladder, controller rules ("never pre-judge a reviewer"), and the three
    reviewer prompts. External helper scripts are replaced by plain git commands, so
    the doctrine works on any agent.
  - `references/tdd.md` — stages 5–6: the iron law, red/green/refactor with both
    mandatory verifications, honest-test rules, the stage-6 full-suite gate, and the
    rationalization table.
- **Ported, not depended on.** Stages 2–6 are adapted from `brainstorming`,
  `writing-plans`, `using-git-worktrees`, `subagent-driven-development`,
  `test-driven-development` and `requesting-code-review` in
  [obra/superpowers](https://github.com/obra/superpowers) (MIT) and rewritten for
  this pipeline's stages, gates, artifacts and single-model policy. `LICENSE` gains
  a second *Third-party* section with Jesse Vincent's copyright notice covering the
  six files.
- **Optional bridge, not a dependency.** An operator who already runs an equivalent
  skill set can substitute it on stages 2/4/5/6 via `pipeline.json` → `skills[]`.
  Nothing detects, recommends or waits for it; the gates still govern; providers are
  never mixed inside one stage.
- **Config:** `pipeline.example.json` stages now name `task-pipeline:brainstorm`,
  `task-pipeline:spec`, `task-pipeline:plan`, `task-pipeline:build` +
  `task-pipeline:review`, and `host:test-runner` + `task-pipeline:tdd`.
- **Every channel updated** — SKILL.md (built-in doctrine table, stage table,
  references list), `references/stages.md`, `references/companion-skills.md` (matrix
  split into built-in vs optional, superpowers moved to a struck-through
  "not a dependency" row), `references/artifacts.md` (new files in the repo map, the
  `.task-pipeline/` scratch workspace, and a note that `docs/superpowers/` is a
  retained directory *name*, not a dependency), the `/task-pipeline` command, the
  Cursor rule (now carrying the design gate, plan format, build loop and TDD rules
  inline) and the README in both languages.
- **Validator:** requires all six doctrine files and rejects stubs (<1.5 KB), and
  fails the build if the shipped default flow names an external provider
  (`superpowers:*`, `grill-me`, `grilling`) in any stage's `skills[]`.
- **Artifact paths unchanged** — briefs, specs and plans still live under
  `docs/superpowers/{specs,plans}` so existing projects need no migration; the name
  is now documented as historical convention only.

## v0.12.0 — 2026-07-27

The grill stops being someone else's skill. It is ported in, in full, and gains
the domain-awareness half it was missing.

- **The intake grill is now BUILT IN — zero external dependency.** New
  `references/grill.md` carries the whole doctrine: the interview loop, domain
  awareness, the autonomy sweep and the output contract. No companion skill to
  install, no provider to resolve, no fallback path, no version skew with someone
  else's repo. `grill-me` / `grilling` are gone from the companion matrix,
  the preflight block and every channel's docs.
- **Ported from [mattpocock/skills](https://github.com/mattpocock/skills)** — the
  `grilling` / `grill-with-docs` interview loop and its domain discipline, MIT,
  adapted to this pipeline's flow. `LICENSE` gains a *Third-party* section with
  Matt Pocock's copyright notice covering the three affected files.
- **New: domain awareness during the grill.** The grill now reads the project's
  own `CONTEXT.md` / `CONTEXT-MAP.md` / `docs/adr/` and holds the operator to
  them — challenging terms that conflict with the glossary, sharpening vague or
  overloaded words into canonical ones, stress-testing relationships with concrete
  edge-case scenarios, and surfacing contradictions between the code and what was
  just said. Resolved terms are written to `CONTEXT.md` inline as they land, never
  batched.
- **New: ADR discipline.** An ADR is offered only when a decision is hard to
  reverse **and** surprising without context **and** the result of a real
  trade-off; any one missing, skip it. Files are created lazily, numbered
  sequentially in `docs/adr/`.
- **New templates** `templates/context.md` and `templates/adr.md` — the formats
  those two artifacts follow, shipped on every install channel alongside
  `brief.md`. `references/artifacts.md` now maps `CONTEXT.md` and `docs/adr/` into
  the canonical layout.
- **Validator:** requires `references/grill.md` and all three templates; the
  broken-relative-link check now strips fenced code blocks first, so illustrative
  paths inside examples stop being false failures (verified it still catches real
  broken links outside fences).

## v0.11.0 — 2026-07-27

The intake grill becomes mandatory, autonomy becomes something the grill actively
buys, and the model stops being a hardcoded per-stage tier list.

- **Stage 0 is now MANDATORY — the stage, not a particular skill.** No "clear
  enough task" exemption, no starting stage 1 without a committed,
  operator-confirmed brief (the entry-from-super-ux short-circuit remains the one
  sanctioned bypass, and still demands a scope confirmation). The **provider** is
  what's swappable: `grill-me`/`grilling` when that chain resolves, otherwise the
  orchestrator's own grill loop — both implement the same **grill contract**, and
  the loop is explicitly no longer described as a "fallback".
- **Grill-provider reality documented.** `grill-me` typically ships
  `disable-model-invocation: true` (so the orchestrator can't call it — the
  operator runs `/grill-me`) and is usually a thin wrapper delegating to
  `/grilling`; if that delegate doesn't resolve the chain is dangling and the
  built-in loop runs. The install line was also wrong — corrected to
  `/plugin marketplace add alirezarezvani/claude-skills` →
  `/plugin install engineering-advanced-skills@claude-code-skills`, with
  `npx skills add mattpocock/skills` noted as the upstream origin.
- **New: the autonomy sweep.** The grill no longer only resolves the *task*; a
  mandatory pass walks stages 1→9 and pre-resolves everything that would otherwise
  interrupt the run — docs sources, branch/tracker policy, the test command and
  what "green" means, the lint command, deploy target + release toggle + deploy
  authorization, log/health locations, docs and wiki targets, the model. Each row
  gets an answer or an explicit "stop and ask here"; an unasked question is a
  scheduled interruption. Stages 5–9 read the brief instead of asking.
  `templates/brief.md` gains the matching `## Autonomy` table.
- **Deploy authorization has a hard floor.** The brief can carry a standing
  authorization for the manual stage-7 gate **only if it is specific** (named
  target + named preconditions). A vague "just do everything" does not authorize an
  outward, irreversible action.
- **Model policy replaces model tiering.** One model for the whole run, confirmed
  **once at preflight** instead of a reminder at every stage boundary. Default
  recommendation: *the most capable reasoning model the environment offers* — a
  **tier, not a string**. Vendor ids are gone from everything shipped: they go
  stale as generations ship and the operator may be on another provider entirely.
  Stage configs use provider-agnostic tokens (`default` / `inherit`), resolved at
  runtime; stage-5 subagents are pinned to the confirmed model; an unavailable tier
  degrades honestly instead of blocking.
- **Validator gains four enforced invariants** (each with a CI negative self-test
  proving it can fail): no hardcoded vendor model id anywhere shipped (skill,
  references, cursor rule, command, README); stage `model` must be a
  provider-agnostic token; the intake-grill gate must stay `manual` and declare
  itself mandatory; `templates/brief.md` must keep its autonomy sweep.
- Docs realigned across every channel — SKILL.md, `references/stages.md`,
  `references/model-tiering.md`, `references/companion-skills.md`,
  `pipeline.schema.json`, `pipeline.example.json`, the `/task-pipeline` command,
  the Cursor rule, and the README in both languages.

## v0.10.0 — 2026-07-25

Review pass — doc drift and a distribution defect found by an adversarial audit.

- **FIX: the stage-0 brief template never reached 3 of 4 install channels.**
  `templates/brief.md` sat at the repo root, outside the plugin source, so the
  skills CLI / npx / install.sh installs had no such file while `stages.md` told
  the agent to seed from it. Moved to
  `plugins/task-pipeline/skills/task-pipeline/templates/brief.md` — inside the
  skill dir, so every channel ships it.
- **FIX: stale super-ux chain in `pipeline.example.json`.** Stage 3 still listed
  only `ux-foundation` + `ux-scenarios`; it now runs the current chain
  (`/ux` → `ux-foundation` → **`ux-flows`** → `ux-scenarios` → **`/ux-lint`**),
  matching SKILL.md and `stages.md`. Stage-4 gate now also names `SCR-` screens.
- **FIX: README documented the old chain** in both languages, and recommended the
  skills CLI for Claude Code (which shadows the plugin). Both corrected; multiple
  agents now shown as repeated `--agent` flags.
- Description now opens with "Use when …" per canon. `ux-contract` stamp updated
  v2 → v4. Model tiering moved to the current Opus generation (`claude-opus-5`).
- README gains npm / CI / license badges.

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
