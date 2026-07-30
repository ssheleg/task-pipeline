# Changelog

## v1.4.2 — 2026-07-30

### Fixed
- **`pipeline.schema.json` identified itself with a URL that 404s.** The `$id`
  read `https://github.com/ssheleg/task-pipeline/pipeline.schema.json` — a path
  that has never existed (no `blob/main`, wrong depth). This file is installed
  into `~/.claude/skills/task-pipeline/`, so every install carried a schema
  whose declared identity could not be fetched by anything resolving it. Now the
  raw URL that actually serves the file, matching `agent-sync`'s convention.

### Changed
- `license: MIT` declared in the `marketplace.json` plugin entry and in the
  skill's front matter — the `LICENSE` file was invisible to both surfaces.

## v1.4.1 — 2026-07-30

### Changed
- `agent-sync` moved to **`ssheleg/agent-sync`**. The three places this skill
  links to it — `SKILL.md`, `references/stages.md`, `references/acceptance.md` —
  now point at the new owner rather than relying on GitHub's redirect.

## v1.4.0 — 2026-07-29

### `references/learned.md` — fourteen rules earned by failure, each with its incident

Taught to the pipeline by a real build: a 229-decision specification across four repositories with
several agents working at once. Every rule names the failure that produced it, because a rule with
no incident behind it is somebody's preference and gets argued with at the worst moment.

The ones that cost the most, now gate criteria rather than advice:

- **A gate's exit code is part of its output.** One printed `FAIL` and returned `0`; CI had been
  green over it for an unknown period.
- **Doubt the probe first.** Five probes failed before any check did — four times out of five the
  planted defect was never planted, and the silence read as a passing check.
- **Absence needs its own check.** Comparing documents finds contradictions, and a contradiction
  needs two sides; a whole missing subsystem has one. Only the reverse direction of a computed
  mapping found it.
- **Tests create what they assert on.** A test read another test file's leftovers, so it passed on a
  warm database and failed on the cold one every new developer has.
- **A generator seeds green** · **local infrastructure does not publish the host's default ports** ·
  **compute rather than restate** · **sweep the class, not the finding** · **ratchet, never TODO**.

Wired into stages 5, 6, 9 and 10 as gate criteria, not as reading. Two lessons are deliberately kept
OUT of the table, as review questions — *is this the right citation* and *did this number come from
the contract or from prose about it* — because a rule that pretends to be enforced and is not is the
same failure as the gate that printed `FAIL` and exited `0`.

## v1.3.2 — 2026-07-29

**The 26 negative self-tests could not be run anywhere except CI** — which meant
that on the maintainer's own machine, a new guard could never be watched rejecting
its planted defect. The project's own `references/audit.md` demands exactly that
(*plant the defect, watch the check fail, then trust the green*), and the tooling
made it impossible at the one moment it is worth most: while the guard is being
written.

Found by running the full CI suite locally during a validity re-check. Nine of the
26 failed — every one on BSD sed, none on a repo defect.

### Added
- **`test/negatives.py`** — runs every negative self-test locally, zero
  dependencies, same as the validator. `npm run test:negatives`, or
  `npm run test:all` for validator-then-guards. The corruptions are **read from
  `.github/workflows/validate.yml`, never duplicated** — a second copy of a
  corruption is a second thing to drift.
- **It tells a broken test from a guard that didn't fire.** If a planted defect
  changed nothing, the validator passing means the *test* proved nothing, not that
  the guard is dead. That case now reports `BROKEN`, with the fix pointed at the
  workflow. This is the failure mode that hid the sed problem in the first place: a
  no-op corruption reads exactly like a broken guard.
- It also refuses to run if it finds fewer than 20 tests — a parser or format change
  that silently matched nothing would otherwise report zero failures and look like
  success.

### Fixed
- **Every `sed -i` corruption in the workflow is now python.** BSD sed needs an
  argument GNU sed refuses, and `0,/re/` does not exist on BSD at all — there it
  edits nothing *silently*, and the test reads as a guard that failed to fire.
  Nine steps converted; CI and a laptop now run the identical script.

### Validator
- **`sed -i` in `.github/workflows/validate.yml` is now a failure**, and
  `test/negatives.py` must exist. Without both, the guards drift back to
  CI-only and stop being provable where they are written.
- The new self-test builds the forbidden token at runtime, because spelling it
  literally would make the workflow trip the guard it is testing. Verified the
  honest way: a clean copy passes, and the injected copy is the *only* reason the
  corrupted one fails — a self-test that passes because the base is already red
  proves nothing.

## v1.3.1 — 2026-07-29

### Stage 10 closes on the parent repository, not only on the one you edited

A submodule is finished when its parent says so. A parent records each submodule as a pointer to
one commit, and moving the submodule does not move the pointer — so work can be committed, pushed,
green in CI and marked done in its own roadmap while a clone of the parent still gets the commit
before it. Neither repository looks wrong alone; the disagreement lives between them, which is why
it survives every check that runs inside one.

Stage 10's gate now requires every repository — parent included — to be clean, pushed and pointed
at, with the plain-git commands given and `/agent-sync finish` named for projects that have it.

The rule reaches all seven surfaces that carry the stage-10 close-out: `SKILL.md`, the gate in
`references/stages.md`, the doctrine in `references/acceptance.md`, the machine-readable check in
`pipeline.example.json`, `build.md`, `conventions.md`, the slash command and the Cursor rule.

### Validator — the class that caused this is now a check

This close-out has failed to reach every surface **twice**: v0.17.1 fixed it for the third review
verdict, and this release's own first pass declared the parent-repository rule in `SKILL.md`,
`build.md` and `conventions.md` while `acceptance.md`, `stages.md` and the config — *the three
places that actually define the gate* — never heard of it. A gate that says "now requires X" only
where X is not enforced is inert, and no existing check saw it: the validator compared stage ids,
names and gate types, never gate content.

Twice is a category, so it is a check now. Whatever close-out concept `SKILL.md` names, the
surfaces that enforce stage 10 must name it too. Proven against a planted defect, with a CI
negative self-test.

## v1.3.0 — 2026-07-29

**One design file, in a named team, decided before anything is drawn.** Left to
drawing time, "where do I put this?" is answered by whichever agent is holding the
brush, and the answer is usually *create a new file* — which is how a project
acquires three files called some variation of "Design", each with real work in it
and no way to tell which one the team actually opens.

The duplicate is **silent by construction**: the second file is internally
consistent, its frames are named correctly, and the UX linter is green. Nothing
downstream notices that half the design now lives where nobody looks.

### Added — the design destination is a stage-0 decision
- **New sweep row `3 Design file`** (in both homes — `grill.md`'s table, which the
  grill reads, and `templates/brief.md`, which records the answer): **which
  team/org, by name, and which file.** Three legal answers: the file already
  recorded, a URL the operator supplies, or **creation in that named team,
  explicitly authorized**.
- **Creation follows the deploy-authorization floor.** *"Create the design file in
  team `Acme Product`"* authorizes one creation in one place; a vague "set up Figma
  for me" authorizes nothing, because deciding *where* on its own is the entire
  failure. `grill.md` → **The design destination** is the new doctrine section.
- **The team is recorded, not just the file.** A file URL identifies a file; it does
  not say whose workspace it lives in. super-ux runs `whoami` and asks which team
  when there are several — but nothing wrote the answer down, and a design that
  lands in someone's personal drafts is invisible to everyone who needs it.
- **Two rules that make it stick:** never create while a recorded file resolves;
  and **if the recorded file does not resolve, stop and ask — never create a
  replacement.** "I couldn't open it so I made a new one" is simultaneously the
  duplicate and a hidden permissions problem that a new file does not fix.
- **Written before the first frame, not after.** A file created and then lost to a
  crashed context is worse than none: it exists, it is empty, nobody knows it is
  there.

### Added — the check that catches it mechanically
- Deep links are `figma.com/design/:fileKey/…`, so **comparing every `screens.md`
  frame link's key against the canonical record is a string match**, not a
  judgement. A differing key *is* a second file. This is now the stage-3 gate and
  the audit ladder's **`→F`** seam; if it ever fires twice, it belongs in the host's
  lint, per the repeats-twice rule.

### Changed
- **Canonical record: `docs/ux/foundation.md` → *Design tooling*** — super-ux owns
  that section, it is per-project and it survives every run, which is exactly what
  "the agents always know which file" requires. The brief holds the **decision and
  the authorization** and points at it; it is a record, **not a second registry**,
  and if the two disagree `foundation.md` wins. On a project with no `docs/ux/` the
  brief is canonical instead, and **stage 9 writes the destination into the host's
  own docs** (`conventions.md`) so the next run finds it without asking.
- **Creating** a shared design file joins the outward list beside *editing* one —
  it is the stronger of the two, and it is the one that duplicates.

### Validator
- The shipped intake gate must settle the design destination; a config where stage 0
  never names the team or the file now fails. Proven against a planted defect and
  shipped with a CI negative self-test.

## v1.2.0 — 2026-07-29

The pipeline already knew about Figma — but only second-hand, through super-ux, and
**every one of its own promises had a Figma-shaped hole**. None of these required it
to learn Figma; super-ux owns that completely and keeps owning it.

### Fixed — four holes in the pipeline's own promises
- **The sweep never asked about the design surface.** super-ux asks "Figma or
  text-only" once per project and stores the answer — but that first ask lands
  *mid-run*, in the very run the sweep exists to make uninterrupted. Worse: when the
  Figma MCP is absent, super-ux correctly recommends it and then **continues
  text-only on its own, never blocking**. That is a scope change nobody agreed to —
  a UI feature ships "described" instead of "designed" and no gate says so. New sweep
  row **`3 Design surface`**: Figma on or text-only, is the MCP connected, and *if it
  isn't, ship text-only or stop and connect it?*
- **The single-preflight promise was broken for UI tasks.** `companion-skills.md`
  guarantees ONE block — companions plus the model — so the operator arms the whole
  run in one exchange. The Figma MCP is a companion stage 3 needs, and its check
  happened later, inside the stage. It is now in the matrix and in the preflight
  block, flagged only when the task is user-facing *and* the project designs
  visually (read `docs/ux/foundation.md` → Design tooling first; no record means the
  choice itself is a stage-0 question).
- **The audit ladder had no rung for the frame.** Added as **`F`** — deliberately
  *conditional and parallel*, not a step in the sequence, so `L0→L7` keeps its
  numbering. A frame is **a second statement of the same surface, made in pictures.**
  super-ux's linter proves a frame link exists, is named `SCR-NN/<Screen>/<state>`
  and isn't stale; **it cannot read the picture.** A frame can pass every lint there
  is while promising a retention window, a credit meter or a pricing tier the spec
  never described and the code never built — a rendered claim about the product,
  seen by more people than the spec, and often the version stakeholders believe.
  Compare frames to frames and they agree; compare specs to specs and they agree;
  the defect lives in the seam. Two new seam questions: **`L2→F`** does the frame
  render what the spec says, and **`F→L7`** did what shipped stay matched to it. The
  spec is the contract — name the document you propose to move instead of quietly
  redrawing.
- **Editing a shared design file was missing from the outward list.** Frames are
  read by designers and stakeholders; drawing in one is publishing, not local work.
  It now sits beside deploy, publish, repo-create and opening a PR — the list an
  agent actually reads.

### Added — validator
- **Autonomy-sweep drift guard.** The sweep lives twice: `grill.md`'s table is what
  the agent *reads* while interviewing, `templates/brief.md`'s is what it *writes*.
  A row added to one and not the other is a question never asked, or an answer with
  nowhere to land. The validator now compares the stage numbers the two tables cover
  and fails on a difference. Proven against two planted defects (a stage present
  only in the grill; a stage dropped only from the brief) plus an unmodified control,
  and shipped with a CI negative self-test. **Scope, stated honestly: it catches
  stage-level drift, not row-level** — a row added under a stage number both tables
  already mention passes.

### Changed
- The boundary is now written down in both directions: super-ux owns *how* to design
  (the choice, the MCP preflight, frame naming, the drift linter); task-pipeline owns
  *when to ask, what counts as degradation, and how to check afterwards that the
  picture and the product still say the same thing*.

## v1.1.1 — 2026-07-29

Version bump only — a fresh npm artifact for the v1.1.0 content. **No changes to
the skill, the doctrine, the gates or the installers**; the tree is identical to
v1.1.0. Nothing to re-read, nothing to re-learn.

(npm versions are immutable, so re-publishing the same content needs a new number.)

## v1.1.0 — 2026-07-29

**The pipeline could find a requirement that was named and lost. It could not find
one that was never named.** Every gate compares two things — and a contradiction has
two sides while **an absence has one**. Nothing in a diff between spec and plan
reveals the error path nobody specified, the entity nobody gave an owner, the
failure mode nobody thought of. This release adds the pass that can.

### Added
- **`references/audit.md` — the audit ladder, cross-cutting.** Eight rungs of one
  deliverable (requirement → decision → spec section → contract **and its failure
  behavior** → plan task → change → **executed** test → surface/docs) and, more
  importantly, the **seam between each pair**, each with its own question: did the
  decision reach the spec; does the section say what happens when the contract
  fails; does every contract have a task (stage 4's set-equality covers REQ→task and
  nothing covers contract→task); did the DoD land in the diff; would this test still
  pass with the production code deleted; can a user reach it and does a doc say so;
  and finally — does what shipped satisfy the requirement's own *statement* rather
  than the task's instructions.
- **Stage 10 now opens with the ladder walk, before the coverage table.** An absence
  found there becomes a **new REQ row with its check**, and *then* the table is
  written. Appending after the table is exactly how acceptance goes green over a
  gap. Findings that belong to a lower layer go back to that layer (spec → stage 3,
  plan → stage 4) instead of being patched in place at the last stage.
- **Findings are ordered by seam, never by file.** A file-ordered list reads as
  noise; a seam-ordered one names *which layer of your own process is leaking*,
  which is the part worth knowing.
- **Bottom-up, and that is not taste.** A missing artefact low on the ladder makes
  everything above it meaningless — top-down you spend the pass polishing a surface
  for a contract that does not exist. Bottom-up, the absence is finding #1 and the
  six findings above it collapse into it.

### Added — three rules that stop the audit becoming another loop
- **Every pass changes the axis, not the effort.** A searching loop does not
  oscillate the way an editing loop does — it **converges**, because each pass edits
  the corpus the next pass reads, so the newest edits are always the
  least-reviewed text present and are what the next pass finds. Measured over seven
  passes on a production repository: by pass six, ten of thirteen findings were
  caused by pass five's own fixes, while the raw count still looked healthy. So the
  doctrine requires **two counts per pass** — new findings, and self-inflicted ones —
  and names the crossover as the signal to **rotate the axis**: seams down one
  deliverable, then invariants across deliverables, then one class swept end to end.
- **A class that repeats twice becomes a gate, not a note.** Once is an incident;
  twice is a category, and a category belongs in the host's lint or CI where nobody
  has to remember it. Writing the third instance into the ledger is how a
  mechanical defect class becomes permanent. Wired into the stage-5 fix loop too.
- **What can't be fixed now becomes a ratchet, never a TODO.** The carry-over ledger
  is now defined as a *named, counted set that may only shrink, printed beside every
  gate verdict* — `carry-over: 4 open (was 6) · unresolved: 0`. A TODO is invisible
  until somebody opens the file; a ratchet sits next to the word `PASS` on every
  run, so **"green" never reads as "verified"** — it reads as *"green, and here is
  exactly what was not looked at"*. A ratchet that grew needs one sentence saying
  why.

### Added — the exit criterion that is usually skipped
- **A green result from an unproven check is worth nothing.** A deliverable is not
  audited when somebody has read it; it is audited when every rung has its artefact
  **and every check being relied on has fired at least once against a planted
  defect.** This is `tdd.md`'s iron law — *if you didn't watch it fail, you don't
  know it tests the right thing* — raised from one test to every gate, linter and
  script in the run, and it is now part of the stage-10 gate. Checks written under
  pressure lie in ways that read as success: a predicate that inspects the wrong
  shape, a probe that reads its own over-deletion as a pass, a regex that misses the
  word it searches for. All three pass loudly.

### Changed
- `loop-guard.md` and `audit.md` now state their seam explicitly in both files: the
  loop guard governs loops that **change** things and trips on oscillation; the
  audit governs loops that **look** for things and trips on convergence. Different
  failure, different exit, and an agent reading either one now learns when the other
  applies.
- `tdd.md` names the generalisation of its own iron law; `build.md`'s fix loop gains
  the repeats-twice rule; `templates/carryover.md` documents the ratchet contract.

### Validator
- `references/audit.md` joins the built-in-doctrine set (must exist, must not be a
  stub, must be reachable from `SKILL.md`).
- The shipped acceptance gate must require the ladder walk **and** say that an
  absence becomes a new REQ row — a config where stage 10 only compares the REQ list
  now fails.
- Both guards ship with CI negative self-tests, and both were proven the way this
  release demands: defect planted, check watched failing, defect removed.

## v1.0.0 — 2026-07-28

**1.0.** Eighteen releases in ten days added a stage, a requirement spine, a
decomposition pass and a loop guard; this one adds nothing and instead makes the
whole thing coherent enough to depend on. Every file was read against every other
file, the contradictions between them are fixed, and the repo now carries the
surface a stranger needs before they trust it.

What 1.0 promises: the stage flow (0 intake + 1→10), `pipeline.schema.json`, the
artifact layout in `references/artifacts.md`, and the two install paths are stable.
Breaking any of them means a 2.0.

### Fixed — contradictions between doctrine files
- **Two names for one idea.** `brainstorm.md` told the agent to split an oversized
  task into "sub-projects", each with its own spec→plan→build cycle;
  `decomposition.md` — the file that actually owns the procedure — calls them
  **modules**, cuts them at the end of stage 2, and runs stages 3→10 per module
  against a committed module map. An agent that read the first file ran a
  decomposition the second file's gate could not check. Brainstorm now hands off to
  `decomposition.md` by name.
- **The same split, invented twice.** `planning.md` independently told stage 4 to
  "split the spec into one plan per subsystem" — a second, unrecorded decomposition
  two stages after the one with the gate and the map. A plan now covers exactly one
  spec; a multi-subsystem spec arriving at stage 4 is a missed stage-2
  decomposition and goes back there.
- **A hardcoded `main`.** `build.md` and `review.md` both built the final
  whole-branch review package with `git merge-base main HEAD`, in a pipeline whose
  stage-0 brief records the base branch precisely because it is not always `main`.
  On any repo with a `master`, a `develop` or a stacked base, the final review saw
  the wrong diff. Both now read the brief's base.
- **A five-status set that claimed to have four.** `acceptance.md` listed four
  statuses, declared "there is no fifth status", then named `unknown` in the next
  clause. Reworded so the mechanism is legible: four ways to close, and anything
  that fits none of them is `unknown`, which fails the gate.
- **A version pin on someone else's contract.** The README and `stages.md` both
  pinned super-ux's scenario format at "ux-contract v4" — the exact cross-repo
  version skew this project ported its own doctrine in-house to avoid. Both now
  point at the contract super-ux itself ships, with no version named here.
- **A blockquote where a sentence should be.** In `knowledge-sources.md` the
  precedence chain `code > host docs and ADRs > the wiki > memory` wrapped so the
  second line *began* with `>`, which Markdown renders as a block quote —
  the rule about which source wins was visually broken in the file that defines it.
- **`skills[]` entries that resolve to nothing.** `pipeline.example.json` names
  `task-pipeline:grill` and `host:lint` beside real skills, with no key anywhere for
  the two prefixes. A host copying the example had no way to tell a notional label
  from an installable skill. The convention is now stated in the config and in
  `SKILL.md`: `task-pipeline:<name>` is this skill's own `references/<name>.md`,
  `host:<name>` is the host project's command per `conventions.md`, everything else
  is a real skill. Stage 3 also gained the `/ux` entry point and `/ux-lint`, which
  the doctrine mandates and the config had omitted.
- **A repo tree that had drifted.** `references/artifacts.md`'s map of this
  repository listed `templates/` outside the tree and missed several files.
- A broken ordered list in the Cursor rule (`3a.` is not a list marker) and a
  `references/` index in `SKILL.md` that never mentioned `templates/`.

### Added — the open-source surface
- `CONTRIBUTING.md` — dev setup, the repository layout, and **the nine invariants**
  written out with the failure each one prevents: four-way version sync, the stage
  list living on three machine-checked surfaces, every human-facing description
  having to name the flow's final stage last, no hardcoded vendor model ids, no
  unreachable reference file, no external provider in the default flow, stage 0 and
  stage 10 staying manual, the frontmatter budget, and resolving links.
- `SECURITY.md` — what the executable surface actually is (two installers, a
  validator, two workflows), private reporting with a 72-hour acknowledgement, and
  an explicit scope: doctrine that would lead an agent to exfiltrate secrets, push
  to an unnamed repo or deploy without a go **is** a security bug here.
- `CODE_OF_CONDUCT.md`, GitHub issue forms (bug / doctrine change, with routing to
  super-ux and obsidian-wiki), and a pull-request template whose checklist is the
  list of surfaces that drift.
- `CLAUDE.md` — house rules for any agent working in this repo, which is also what
  this pipeline's own stage-0 harvest reads first: the commands, the branch and
  commit policy, the invariants, and the docs that must be updated in the same
  change. The project now dogfoods the convention it asks of every host.
- **Two validator guards, each with a CI negative self-test:** the open-source root
  files must exist, and `npm test` must actually run the validator. A documented
  check nobody can run is a check nobody runs.

### Changed
- **README rewritten.** Same substance, ordered so it can be read: a one-paragraph
  statement of the problem, a Mermaid diagram of the flow with gate types coloured,
  the gate table, *what you get*, then a quickstart — before the deep sections.
  Configuration, install/update and a documentation map now live in their own
  places instead of interleaved with doctrine.
- Package, marketplace and plugin descriptions rewritten — shorter, and all three
  now say the same thing about the same ten stages.
- npm metadata: a `test` script (`npm test`), a `bugs` URL, `homepage` at the README.
- `.worktrees/` is git-ignored — stage 5 creates them.

> The open-source surface above shipped in v0.18.1, hours earlier the same day;
> it is restated here because it is part of what 1.0 means.

## v0.18.1 — 2026-07-28

Open-source hygiene pass — the repo is public, so the files a first-time
contributor looks for now exist, and the validator keeps them there.

### Added
- `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, issue forms and a
  pull-request template.
- `CLAUDE.md` — house rules for any agent working in this repo: the commands, the
  branch and commit policy, and the invariants that drift most often.
- The validator now requires the open-source root files, with a CI negative
  self-test that deletes `CONTRIBUTING.md` and proves the check fails.

### Changed
- npm metadata: a `test` script, a `bugs` URL, and `homepage` pointing at the
  README. Package, marketplace and plugin descriptions rewritten so all three say
  the same thing about the ten stages.
- `.worktrees/` is ignored — the pipeline creates them during stage 5.

## v0.18.0 — 2026-07-28

The grill stops opening cold. Stage 0 now reads what the project already knows
about the task **before** the first question, checks every answer against it, and
stage 9 updates the same list at the end — the loop the pipeline was missing.

### Added
- **Stage 0 phase 1: the knowledge harvest** (`references/knowledge-sources.md`).
  Before question one, query what the project already knows about *this* task —
  the code, `CLAUDE.md`/`AGENTS.md`, `CONTEXT.md` + `docs/adr/`, `docs/` and
  `docs/ux/`, previous pipeline briefs and their carry-over ledgers, **the
  knowledge wiki when one is installed**, and **any other repository or hosted doc
  system the project names as its docs**. It is retrieval scoped by the task's own
  nouns, not a read of everything: query, follow one hop, stop when the terms
  return nothing new. Nothing is ever fetched on a guess — a doc repo is in scope
  because the project names it.
- **The source ledger** — a required `## Knowledge sources` section in the brief
  (source, what it says about this task, freshness, authority, "stale after this
  run?"). `none found` is a valid, useful row: it tells the next run the search
  happened and came back empty. Silence doesn't.
- **Answers are validated against the harvest** (`grill.md` → *Domain awareness*).
  The cheap win is not re-asking what an ADR already answers. The one that matters:
  **an answer nobody can check is a recollection** — people answer from memory
  about systems they wrote a year ago, and a false premise adopted at stage 0 makes
  every later gate pass honestly on it. So the grill quotes the source instead:
  *"the March ADR says X, you just described Y — has it changed?"* The operator
  **outranks every document, but only out loud** — an override quoted against its
  source is a recorded decision, an unquoted one is an undetected divergence.
  Precedence when sources disagree: **code > host docs/ADRs > wiki > memory.**
- **obsidian-wiki is the recommended knowledge base**
  (https://github.com/ar9av/obsidian-wiki — Karpathy's LLM-wiki pattern), detected
  via `~/.obsidian-wiki/config` or a resolving `wiki-query`/`wiki-update`.
  Installed → queried in the harvest, synced with `wiki-update` at stage 9. Absent
  → the preflight prints `pip install obsidian-wiki` / `obsidian-wiki setup --vault
  <path>` **once** and the run continues. A recommendation, never a gate; a project
  whose `CLAUDE.md` names a different knowledge base wins.
- **Stage 9 closes the loop:** the stage-0 ledger *is* its work list. Every source
  the harvest read gets updated if this run changed or disproved it — including the
  docs the grill already proved stale, which is why those conflicts are logged in
  phase 2 instead of only being settled out loud. Docs living in **another
  repository** are outward: propose the edit and get an explicit go, or carry it
  over with the exact change written down. Never a direct push to a repo the task
  didn't name.
- **Autonomy-sweep row** for doc sources beyond this repo, and whether stage 9 may
  write to them — decided at intake, like every other outward action.
- **Three validator guards, each with a CI negative self-test:** the brief template
  must keep its `## Knowledge sources` section; the stage-0 gate must require the
  harvest *and* its ledger before the interview; the stage-9 gate must name that
  ledger as its work list. A harvest with nowhere to land degrades silently back
  into asking from memory, which is precisely the failure it exists to stop.

## v0.17.1 — 2026-07-28

A full-repo consistency audit. v0.16.0 added a third review verdict and a tenth
stage; several surfaces never heard about either. An agent reads one surface, not
all of them, so a stage that is `three verdicts` in the config and `both verdicts`
in the prompt that actually runs simply produces two.

### Fixed
- **The third review verdict now exists where reviews are actually dispatched.**
  `references/review.md`'s task-review prompt asked for *"two verdicts"* — so the
  REQ-satisfaction verdict the stage-5 gate requires was never returned. It now asks
  for three (spec compliance → **REQ satisfied** → code quality), with the REQ one
  judged against the requirement's quoted statement rather than the task's
  instructions. Same correction in `build.md` (§4.4 and its gate), `planning.md`'s
  plan header, `stages.md` and the Cursor rule.
- **Stage-5's gate now names the ledger harvest.** `build.md`'s gate omitted
  "every parked finding and implementer concern harvested into the carry-over
  ledger" — the one thing that must happen before the scratch workspace is deleted.
- **Three gates in the doctrine files were weaker than the same gates in
  `stages.md`:** `planning.md` didn't state the REQ **set-equality** check (the
  brief→plan seam), `spec.md` didn't require `covers: REQ-…` per section, and
  `brainstorm.md` didn't require every REQ answered by the design or the module map
  approved for a platform. All three now match.
- **Descriptions listed the flow wrong.** npm, the marketplace entry, the plugin
  manifest: `…post-deploy, acceptance, docs/wiki` — eleven items for ten stages,
  with the final stage listed second-to-last. The `/task-pipeline` command's
  description and `SKILL.md`'s frontmatter stopped at docs/wiki and never named
  acceptance at all.
- **Built-in doctrine tables were missing rows** for stage 10 acceptance
  (`SKILL.md`, `README.md`, `companion-skills.md`), stage-2 decomposition and the
  loop guard (`README.md`, `companion-skills.md`) — files that ship, are reachable,
  and were absent from the very tables that say what ships.
- Smaller drift: the Cursor rule's stage 9 dropped the wiki sync; four gate checks
  in `pipeline.example.json` had v0.16.0 sentences concatenated without punctuation;
  `stages.md` wrote `implements:` where the plan format writes `Implements:`;
  `artifacts.md` had the acceptance artifact listed before the spec and the ledger
  attributed to stages `0→9`; the v0.1.0 design snapshot's disclaimer still
  described the live shape as nine stages.

### Added
- **Three validator guards, each with a CI negative self-test**, so this class of
  drift fails instead of shipping:
  1. every human-facing description (npm, marketplace, plugin, `SKILL.md`, the
     command, the Cursor rule, `README.md`) must name the flow's **final stage**,
     and must not list it before the stage it runs after — derived from
     `pipeline.example.json`, not hardcoded;
  2. no shipped surface may say *two/both verdicts* while the dev gate declares
     three;
  3. each stage doctrine file's own `GATE (auto|manual)` must match that stage's
     gate type in the config.

## v0.17.0 — 2026-07-28

Two mechanisms stop being files nobody walks and become operational doctrine: a
platform is cut into bricks before it is specced, and a loop that starts undoing
itself is broken instead of endured.

### Added
- **Decomposition is stage 2's second half**, wired end to end —
  `references/decomposition.md` now reached from `SKILL.md`'s doctrine table, the
  stage-2 gate in `stages.md`, the example config, the Cursor rule, the command and
  the README. A brief that describes a *platform* — several independent
  capabilities, several separately shippable surfaces, REQs no single deliverable
  satisfies — is cut into **modules** before any spec exists: by capability, never
  by layer, and a candidate is a brick only when it is independently specifiable,
  buildable and testable, owns its entities, talks through declared contracts only,
  and can land while leaving the system working. The module map carries build order
  — **walking skeleton first**, then topological, no cycles — with every REQ mapped
  to exactly one module. Single-module work records `single module: <name>`: a
  skipped decomposition is a decision, never an omission.
- **The module dossier** (`spec.md`): for a decomposed platform the spec has nine
  required sections — purpose and boundary, architecture, entities and ownership,
  contracts in and out **with their behavior when the other side is down**,
  business rules in the domain's language, edge and failure cases, UI/Figma chain,
  non-functional limits, and open questions with a decide-by moment. A skipped
  section says why in one line; silence is not a skip.
- **The loop guard binds every repeating loop** — `references/loop-guard.md` is now
  referenced from `SKILL.md`'s cross-cutting rules, a `stages.md` section, the
  stage-5 fix loop, the Cursor rule and the command. Every repeating pass logs one
  line per touched file with the reason that forced it ("cleanup" is not a reason).
  It trips on revert-oscillation, a file edited twice for the same reason, a
  resurrected finding, a third entry into one stage, or two loops editing one file,
  plus hard caps (5 fix rounds per task, 2 re-entries per stage, 3 passes per
  module). On a trip: stop editing, name shape A and shape B with their evidence,
  escalate to the layer that owns the conflict, re-plan the check as an ordered
  checklist with one verification command per item, then go through it one at a
  time. **A higher-layer conflict is never settled inside a lower loop.**
- **Two autonomy-sweep rows** (grill + brief template): platform-or-single-module
  with the deploy cadence it implies, and who signs off acceptance plus where
  deferred REQs are tracked.
- **`conventions.md` gains the issue tracker** stage 10 needs — read the host's
  convention, never invent a tracker, never close a run on "we'll remember it".
- `artifacts.md` gains the module map and the run-level ledger
  (`.task-pipeline/run.md`) the loop guard writes to.

### Tests
- **The stage list is cross-checked across all three surfaces it is published on** —
  `SKILL.md`'s table, `references/stages.md` and `pipeline.example.json`: identical
  ids in identical order, matching names, matching gate types, and every stage in
  `stages.md` carrying a `**GATE (auto|manual)**` line. Drift between surfaces is
  invisible in review and lethal at runtime — a stage manual on one surface and auto
  on another.
- `decomposition.md` and `loop-guard.md` join the stub-rejected doctrine set.
- Three negative self-tests against a mutated copy: a flipped gate type, a removed
  GATE line and a deleted doctrine file each fail the validator.

## v0.16.1 — 2026-07-28

### Fixed
- **v0.16.0 added a tenth stage and left "1→9" in fifteen places** — the skill
  description, the command, the Cursor rule, `stages.md`, `grill.md`, the brief
  template, the example config and the README all still promised nine. The
  package, marketplace and plugin descriptions said "9 gated stages" too, which
  is what npm and the marketplace show. All re-synced to ten, and the plan
  filename now uses the same slug as the brief and the spec.

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

### Fixed
- **`decomposition.md` and `loop-guard.md` shipped unreachable.** Both linked only
  to each other; nothing in `SKILL.md` pointed at either, so under progressive
  disclosure an agent would never load them — two contracts that existed, passed
  every check, and were dead context. Wired into the doctrine table (stage 2 for
  decomposition, cross-cutting for the loop guard), and the validator now walks the
  link graph from `SKILL.md` and fails on any reference nothing reaches.

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
