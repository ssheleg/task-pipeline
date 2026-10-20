# Stages — detail & gates

For the selected **default profile**, read **one stage section of this file when that
stage starts** (the stage table in `SKILL.md` is the index), then the one detail it
links, on every entry or resume, including wave iterations and the short path. Do not
read this file end to end and do not preload all stage details. Missing or
unreadable detail means stop that stage and repair its route, never guess. A custom
profile uses its own declared doctrine and stages; numeric ids do not select these
default details, and the kernel still applies.


For each stage: what it does, what to invoke, artifacts, and the **GATE** that
must pass before advancing. Each gate is tagged with its **type** — `auto` (the
orchestrator verifies the check itself, pass/fail), `judgment` (a named judge
rules where no complete deterministic check exists — [`gates.md`](gates.md) →
*The judgment gate*) or `manual` (requires the operator's explicit go, including a
specific standing authorization naming the act, cited with its source and scope;
otherwise wait). **This example ships every gate `auto`** (since 1.98.0): where it
names an approval, the operator's answer or the standing authorization recorded in the
brief satisfies it without a pause. A project makes a gate `manual` in its own
`pipeline.json`. These stages (0 intake + 1→10) are the plugin's
**example** flow, encoded in `pipeline.example.json` against the universal contract
`pipeline.schema.json`; a host project replaces it with its own
stages/agents/types (see SKILL.md → *Bring your own skills*).

## The run checklist — printed, not remembered

Complex workflows lose steps silently. **The run says where it is**, at two boundaries
and only two — task start and iteration close ([`progress.md`](progress.md)):

```
task-pipeline vX.Y.Z · <topic> · module <id> «<name>» (N of M)
  0 ✓  1 ✓  2 ✓  3 ▶  4 ·  5 ·  6 ·  7 ·  8 ·  9 · 10 ·
  ███████░░░░░░░░░░░░░░░░░░░  gates 3/11 · now 3 Spec · manual
  board B-NNN · carry-over N rows · exposure N never · unlooked N
```

The rail's positions come from the project's own `pipeline.json`, never from the count
below — those eleven are this plugin's example flow. Each glyph is read from the
verdict its gate wrote to `.task-pipeline/run.md`, and from nothing else: a rail
written from memory is a summary that is confidently wrong exactly where it is trusted
at a glance.

The checklist below is what that rail summarises. This section said *"copy it, tick
it"* until 2026-08-10 — an instruction with no gate behind it, which is the same
failure it was written to prevent, one level up.

```
Pipeline progress
- [ ]  0  Intake — harvest + doc inventory + reconcile, grill, REQ table, brief locked
- [ ]  1  Docs study — every contract grounded on fetched docs, not recall
- [ ]  2  Brainstorm — design approved, UI verdict recorded, every REQ answered
- [ ]  3  Spec — committed, reviewed, every section covers: REQ-…
- [ ]  4  Plan — REQ set equality holds, no placeholders, groups share no files
- [ ]  5  Dev — tasks DONE, three verdicts each, suite green, branch integrated
- [ ]  6  Tests — full suite green, new checks probed both ways
- [ ]  7  Lint + deploy — clean, and the deploy authorization is specific
- [ ]  8  Post-deploy — clean boot, or an honest degradation report
- [ ]  9  Docs — matrix walked, registers written, docs gate green with ratchets printed
- [ ] 10  Acceptance — ladder walk first, every REQ with evidence, retro written last
```

Each line is a **gate**, not a task: an unchecked box means the gate did not pass,
never that the work was skipped quietly.

## Contents

- The run checklist — printed, not remembered
- 0 — Intake grill — MANDATORY
- 1 — Docs study
- 2 — Brainstorm + decompose
- 3 — Spec — with UX track for user-facing tasks
- 4 — Plan
- 5 — Dev
- 6 — Tests
- 7 — Lint + deploy
- 8 — Post-deploy
- 9 — Docs + wiki
- 10 — Acceptance
- The program loop — a platform, one brick at a time
- Cross-cutting — the Doc Loop
- Cross-cutting — the loop guard
- Cross-cutting — the audit
- A stage that produces text a user will read

## 0 — Intake grill — MANDATORY
- **Freedom: medium** — the interview adapts to the answers; its two phases and their order do not ([`gates.md`](gates.md) → *Axis C*).

**On entry or resume:** read [stage-00-intake.md](stage-00-intake.md) before stage work.

- **On the short path** (`stage-00-intake.md` → Phase 1d) this gate
  is: the triage line printed, the brief and its REQ rows in the run ledger, the retro
  floor read with its byte count, and the source ledger. Everything else below applies
  to the full flow.
- **GATE (auto):** shared understanding reached — **the source ledger is written
  (every source consulted, or an explicit "none found")** and **its `Contradictions:`
  line is written under it** — the harvest is a fan-out that converges on one brief, and
  nothing else compares the sources *with each other*; `Contradictions: none` is the
  answer most runs give and writing it is the point
  ([`knowledge-sources.md`](knowledge-sources.md)), **where a code graph
  exists its row carries the measured lag and the signal it was measured with — a
  bare build date does not satisfy this, because it is the graph's own reply rather
  than a measurement of it** ([`knowledge-graph.md`](knowledge-graph.md) →
  *Measure the lag*), **the documentation
  inventory is answered into `docs/DOCMAP.md`** with its registers, single homes,
  a non-empty propagation matrix and the gate command, **the regime is recorded**,
  **intent and as-built are reconciled with every divergence resolved**, the retro's
  in-force sections are read in full and its archive queried, every detected branch has
  a recorded answer or an explicit deferral, **every answer that contradicted a
  harvested source has a recorded resolution** (which governs, and whether the doc
  is now stale), no open contradictions, **every
  autonomy-sweep row is answered or explicitly marked "stop and ask here"**, **a
  user-facing task's brief names its `surface_class`**, the
  **REQ table is written and every row names its check**, **the brief's `## Finish line`
  is filled — objective, exit checks on the artefact the operator uses, scope, budget and
  base** ([`finish-line.md`](finish-line.md)), the carry-over ledger is
  seeded, **`.task-pipeline/run.md` exists and the header block has been printed**
  ([`progress.md`](progress.md)), the model decision is recorded, and the brief is
  confirmed: the operator's answer, or the standing authorization recorded in it. Stop when a
  re-scan surfaces no new branches (don't grill past diminishing returns;
  reversible calls can be deferred with a note). Only then start stage 1.
- **The verification ledger is read.** `<artifacts>/verification.md` — the harvest
  quotes **how many rows sit at `never`**, because that is the project's standing
  exposure and stage 0 is where it is cheapest to look ([`verification.md`](verification.md)).
- **The run ledger is seeded and the header block is printed** — in that order, before
  the first grill question. `.task-pipeline/run.md` from
  [`../templates/run.md`](../templates/run.md) is the record **two** mechanisms already
  depended on and no run had ever written: [`loop-guard.md`](loop-guard.md) calls its
  own churn detection mechanical and reads the `touch:` lines, and
  [`progress.md`](progress.md) derives the rail and the iteration counter from the
  `stage:` and `iter:` lines. The header goes out before the interview because a run
  that announces its position only at the end announced it to nobody. A new ledger starts a new
  run's memory state: a previous run's "memory unavailable" marker is honoured only while
  its own ledger line is in the ledger, so a reseeded ledger — even the same day — is nudged
  again, and the stale marker is cleared at the next `stage_checkpoint.py record`.
- **The board is read, or seeded.** `<artifacts>/backlog.md` ([`backlog.md`](backlog.md)) — its **open count is quoted in the brief**, measured by a command at the top of the run rather than inherited from the last run's report. Absent ⇒ seeded from the template and said so; an empty board and no board are the same thing to work on, and only one of them can be appended to.

## 1 — Docs study
- **Freedom: medium** — which sources to fetch is judgement; grounding contracts on fetched docs is not ([`gates.md`](gates.md) → *Axis C*).

**On entry or resume:** read [stage-01-docs-study.md](stage-01-docs-study.md) before stage work.

- **GATE (auto):** every contract the design will lock is grounded in fetched docs,
  not recall. Unresolvable libraries are flagged in the spec.

## 2 — Brainstorm + decompose
- **Freedom: high** — many designs are valid — this is the open field, and the only fixed thing is the gate ([`gates.md`](gates.md) → *Axis C*).

**On entry or resume:** read [stage-02-brainstorm.md](stage-02-brainstorm.md) before stage work.

- **GATE (auto):** the design is approved (the operator's go, or the brief's standing
  authorization), the UI verdict is recorded, **the
  queue is an artifact rather than a recollection** — where it is a work graph,
  `graph.py validate` exits 0 and `graph.py coverage` names any requirement no node serves,
  **every REQ is answered by the design** — a requirement the design doesn't
  address is either covered now or explicitly dropped by the operator, with the
  drop recorded in the carry-over ledger — **and, for a platform, the module map is
  approved**: brick criteria met or excepted in writing, dependency graph acyclic,
  build order topological, every REQ mapped to exactly one module, cross-module
  contracts named with their owner — **and the loop's arming state is printed**:
  armed with its queue and pacing, or not armed with the reason.

## 3 — Spec — with UX track for user-facing tasks
- **Freedom: medium** — what the contract says is judgement; which contracts must be locked is a list ([`gates.md`](gates.md) → *Axis C*).

**On entry or resume:** read [stage-03-spec.md](stage-03-spec.md) before stage work.

- **GATE (auto):** the **`## Self-review` section written and committed with
  computed values** — every check the spec names resolving or marked `review`, the
  brief's decisions and stage 2's rejected options read back with no unresolved
  contradiction, and the cost delta printed; spec committed **and** reviewed (by the
  operator, or under the brief's standing authorization by an independent reader); **every section carries
  `covers: REQ-…` and every REQ appears in at least one section**; for UI tasks
  additionally: the super-ux chain (foundation → flows → screens → scenarios) is
  designed, validated and approved; scenarios validated in `docs/ux/scenarios.md`;
  the linter passes; every user-facing spec requirement traces to a scenario ID
  (or an explicit v1-mode/tiny-project waiver by the operator). **With Figma on:
  the canonical record names one file per surface (App, Web, ASO), and every
  `screens.md` frame link's `:fileKey` is one of them** — a string match, not a
  judgement (`python3 scripts/visual_gate.py filekeys --record docs/ux/foundation.md
  --screens docs/ux/screens.md`); a key outside the set means the run drew in a file
  nobody recorded and nobody will open. **Every user-facing string went
  through the COPY track or the refusal is recorded**, and **the visual layer went
  through the VISUAL track or the refusal is recorded** — a recorded refusal passes
  this gate and an unmentioned one does not, which is the only difference that matters.
  **And the VISUAL track is checked by its trace, not by the fact that it ran:** on a
  `flagship`, `product` or `ad` surface the director record exists and carries the
  fields its class owes — `python3 scripts/visual_gate.py record
  docs/design/<surface>/director-record.md --class <surface_class>` exits 0. That
  command checks the headings itself and runs the record's own validator from `sheleg-design`
  (`--check-record`) where it is installed and new enough; where it is not, the
  validator reads **NOT_RUN** beside the verdict — never PASS — and the gate stands on
  the floor, said so. A record saying `Mode: declined` with its reason is the refusal,
  and it passes.
  **Where both tracks ran, their convergence check is recorded** — findings with the
  ruling, or `Tracks converge: clean`; a screen where each track is right alone and they
  disagree together is the defect neither track's own review can see.
  No plan (stage 4)
  starts before this — the chain comes BEFORE interface.

## 4 — Plan
- **Freedom: low** — the task format is prescribed and the REQ set-comparison is mechanical ([`gates.md`](gates.md) → *Axis C*).

**On entry or resume:** read [stage-04-plan.md](stage-04-plan.md) before stage work.

- **GATE (auto):** `python3 scripts/plan_audit.py` clean — the plan read as the agent
  who was NOT there will read it: every live node carries a packet answering the cold
  reader's eight questions, no two nodes the graph leaves unordered edit one file, the
  priority is computed from what each node unblocks, and a recorded per-stage model map
  names stages this pipeline has ([`planning.md`](planning.md) → *Plan audit*). Then:
  the **`## Self-review` section written with computed values**,
  every command, path and file a DoD names resolving; **set equality — the REQ ids in the brief equal the union of
  `Implements:` across plan tasks.** A non-empty difference fails the gate and is
  reported as the explicit list of dropped requirements; this is the seam where
  scope leaks silently, so the check is mechanical, not a judgement call. Plus:
  every spec requirement maps to a task; no placeholders; names and
  types consistent across tasks; every task carries a verifiable DoD; parallel-group
  tasks share no files **or other mutable target**; **every edge in the *Execution
  order* table carries a non-empty `Carries` cell and the self-review's `Edges:`
  line is computed** — an arrow whose payload nobody can name is a fake edge and
  the wait behind it is free to give away ([`planning.md`](planning.md)).
  For UI tasks: every task building user-facing behavior
  names the scenario ID(s) and `SCR-` screen(s) it implements, and its DoD
  includes satisfying them **and** updating the affected super-ux layers in the
  same change (super-ux *same-change* rule).

## 5 — Dev
- **Freedom: low** — TDD order, worktree isolation and 'a subagent never writes the register' are the narrow bridge ([`gates.md`](gates.md) → *Axis C*).

**On entry or resume:** read [stage-05-dev.md](stage-05-dev.md) before stage work.

- **GATE (auto):** **the hygiene gate green in diff mode after every task**
  (`references/build.md`) — six checks over what that task changed, no floor, and a
  finding fixed in-task or carried over with a reason; all plan tasks DONE (three review verdicts per task: spec
  compliance, **REQ satisfied**, code quality); **every group that fanned out ran its
  convergence check before its first worktree was integrated, and logged a line either
  way** ([`build.md`](build.md) §4.2a); every finding fixed or parked with a
  ruling; **every parked finding and implementer concern harvested into the
  carry-over ledger** — nothing stays only in the scratch workspace, which is
  deleted; no task left BLOCKED; full test suite green; branch integrated per the brief's policy (or the operator's
  "leave it" recorded).

## 6 — Tests
- **Freedom: low** — green means the full suite, and no skip smuggles a red one past ([`gates.md`](gates.md) → *Axis C*).

**On entry or resume:** read [stage-06-tests.md](stage-06-tests.md) before stage work.

- **GATE (auto):** **the hygiene gate green over the whole tree**, its six counts
  printed beside their floors; the **full** suite is green (not just the new tests); new/changed code
  is covered; **every check this run added or widened has been probed both ways —
  seen rejecting a planted defect and passing the clean tree, asserted on its exit
  code** ([`probing.md`](probing.md)); no `skip`/`xfail` smuggling a red suite past the gate; **on a
  `flagship`, `product` or `ad` surface where the VISUAL track ran, the visual half's
  `visual_gate.py sheet` exits 0** — NOT_RUN stops and asks, it is not green
  ([`browser.md`](browser.md) → *The visual half*). Never advance
  to deploy on a red or partial run. **The carry-over count is printed beside this
  verdict** — a ratchet nobody prints is a TODO with a better name
  ([`audit.md`](audit.md)) — **and so are the disclosures**, `abstained` and
  `unlooked` ([`gates.md`](gates.md) → *Disclosures*): what the run declined to claim,
  and what a check never looked at. Neither has a floor and neither may be targeted; a
  target on an abstention count is an instruction to guess.
- **Web front end? Then the surface is checked in a browser, not in the diff.**
  A passing suite proves the code does what its assertions say. It does not prove the
  page rendered — a component can be correct and land under a fixed header, a request
  can 404 while every unit test mocks it, and a console error costs nothing at test
  time. Where a browser channel is connected — `playwright` **or** `chrome-devtools`,
  either one, on WebKit first with Chromium a stated exception
  ([`browser.md`](browser.md) is the four commands this sentence means and the engine
  order; [`companion-skills.md`](companion-skills.md) is which channel):
  load the surface, take a snapshot, and read **the console and the network log**
  before calling it green. Absent, say the surface was verified **by reading the
  diff** — that is a weaker claim and the close-out records it as one, rather than
  letting "tests pass" stand in for "it renders". This is the `L6→L7` seam of
  [`audit.md`](audit.md)'s ladder: *is there an executed observable a user reaches?*
- **A browser test suite does not discharge the look, and does not become it.** A
  project whose CI runs `playwright test` has an *asserted* browser — it proves what
  someone thought to assert, on the paths someone thought to write. It cannot report
  the console error nobody asserted on, the bundle that 404s past a route nobody
  visits, or the element that moved four pixels under a header. So a green spec suite
  counts where every other test counts, inside **the suite half of the GATE above**;
  the look stays what it already is here — **recommended, never a gate**, and reported
  in the words the gate gives it. What the pair buys is that they fail differently: a
  run that answers *the surface was checked* by pointing at its spec suite has answered
  a different question. Where the suite is the thing that changed, the look is what
  proves it runs against a page that renders.
- **The visual half is a separate check, and on most user-facing classes a gate.** The
  look above reads the accessibility tree; it cannot say whether the surface looks like
  what was designed. Where the stage-3 VISUAL track ran on a `flagship`, `product` or
  `ad` surface, stage 6 also owes **the contact sheet** — frames over the `SCR-NN` states
  × viewport × theme × text × locale (pairwise, plus the mandatory pairs), each with its
  capture record, diffed against its Figma frame or approved baseline, the project
  linter run, the token drift probe run over the whole token file where Figma is on
  (`visual_gate.py tokens`; NOT_RUN without an export, never PASS), and the rubric
  read by a judge that is not the builder — and its command
  exits 0: `python3 scripts/visual_gate.py sheet <contact-sheet.json> --class
  <surface_class> --artifact-root <frames>` (NOT_RUN, exit 3, is not green). On
  `internal` it is recommended and the linter is the floor. The re-render budget is
  **one, two at most**, then `unresolved` to the person — never round three — and only
  external, specific feedback starts a round. The procedure and the order of the checks:
  [`browser.md`](browser.md) → *The visual half*.
- **What the look finds is fixed here.** A rendering defect found at stage 6 is a
  stage-6 finding: fix it, look again, then call the stage green. Filing it to the
  board and advancing is how a run reports *checked in a browser* for a page it has
  seen to be broken — so if it does leave unfixed, the reason is on record and the
  close-out carries it, exactly as a parked finding does.

## 7 — Lint + deploy
- **Freedom: low** — outward and irreversible — the authorization floor is exact or the stage stops ([`gates.md`](gates.md) → *Axis C*).

**On entry or resume:** read [stage-07-lint-deploy.md](stage-07-lint-deploy.md) before stage work.

- **GATE (auto):** lint clean (host linter **and**, for UI projects, the super-ux
  linter) **and** suite green **before** deploy, **and no REQ is still `open`** — a
  `partial` ships only with the operator's explicit acceptance. A gap is cheapest to
  close before it ships. **The
  carry-over count is printed beside this verdict.** Deploy is outward → explicit
  operator go, or a specific standing authorization naming that act, cited with its source
  and scope. Authorization to release does not silently authorize a separate deploy. If
  `release.authorized_by` is present, read that source and verify its authority,
  currentness and scope for the tag and publication; the locator is not authorization.
  If absent, inspect existing recorded authority before asking for a missing grant.
  **Before the tag, read
  the release's approval mode** (`pipeline.json` → `release.approval`; then
  [`deploy-targets.md`](deploy-targets.md) → *When the release waits for an approval*):
  `checks` — push the tag, watch the run selected by the tag, report; `reviewers` — the
  direct link to the run that is actually `waiting`, never a request without it. Respect deploy-from-main rules if the project mandates them. **Before
  tagging, the CI verdict for what was just pushed is READ, not assumed**
  ([`conventions.md`](conventions.md) → *The CI verdict*) — a tag on a commit whose
  run nobody read is how a red `main` ships.
- **The independent reader is dispatched by this stage, and read by its output**
  ([`review.md`](review.md) → *The independent reader*). On any change that adds or
  widens a check, the run dispatches a reader — a subagent it can watch, a bot whose
  **verdict** it then reads, or a person — and records exactly one of three states
  beside the verdict: `reader: N findings`, `reader: none found`, or `reader: NO READER
  — <why>`. The third is printed, never omitted; a requested reader and a reading are
  different facts that look identical afterwards. Four pull requests of check work once
  merged on a bot's `skipping` with nobody noticing, which is why this is a stage rather
  than a hope.
- **The review loop that lives here has a cap, and the cap is a measurement**
  ([`loop-guard.md`](loop-guard.md) → *The review loop*). **3 rounds** per artifact by
  default (`pipeline.json` → `run.review.maxRounds`); at the cap the run stops reviewing
  and prints new-versus-self-inflicted per round, and either the numbers end it or the
  operator continues it out loud. This stage's loop was capped by nothing until
  2026-08-10 and ran ten rounds twice in one programme, against a stated ceiling of two
  re-entries per stage — the ceiling simply did not name a review round. Every finding
  left open at the cap leaves as a board row with its evidence, never as a shrug.

## 8 — Post-deploy
- **Freedom: medium** — where the logs live varies; 'clean boot or an honest degradation report' does not ([`gates.md`](gates.md) → *Axis C*).

**On entry or resume:** read [stage-08-post-deploy.md](stage-08-post-deploy.md) before stage work.

- **GATE (auto):** clean boot confirmed, or an **honest degradation report** with next
  steps — never silent success. **The CI verdict is one of the reported facts, with
  its run id** — "CI is green" written without a command behind it prints the same
  whether it looked or not ([`gates.md`](gates.md) → *False success*).
- **Write the verification row.** One line per REQ this run shipped, into
  `<artifacts>/verification.md` ([`verification.md`](verification.md)) — the run,
  the tag or commit it went out in, what the gate said, and `Human: never` unless the
  operator confirmed during the run. The verification above already happened; this is
  the only step that makes it answerable **later**, and `never` is a fact rather than a
  failure — the count has no floor and may never be given a target.

## 9 — Docs + wiki
- **Freedom: low** — the matrix walk and the gate are mechanical; what a doc says is not this stage's call ([`gates.md`](gates.md) → *Axis C*).

**On entry or resume:** read [stage-09-docs-wiki.md](stage-09-docs-wiki.md) before stage work.

- **GATE (auto):** **the hygiene gate green**, counts printed; **the propagation matrix walked for every change type this run
  produced**, with every settled thing recorded under an id and every answered
  question resolved; **the documentation gate green, its ratchet counts printed and
  any skip stated** — this is what replaced the unfalsifiable *"docs in sync with
  code"*, which named no artefact and no command; every stale row in the source
  ledger either updated or carried over with its edit; the **as-built record
  written and reconciled**; UI: super-ux layers current + linter green; wiki synced
  (or absent and recommended once); **the code graph
  refreshed where one exists, or the reason it wasn't written into the carry-over
  ledger** (absent and recommended once is fine); dangling links fixed; **the CI
  verdict read for this stage's own push** ([`conventions.md`](conventions.md) →
  *The CI verdict*) — this stage pushes like any other and is the one that habitually
  ends a run, so an unread red here is a red `main` nobody is coming back to; **the
  carry-over count printed beside this verdict**.

## 10 — Acceptance
- **Freedom: medium** — the walk and the evidence rule are fixed; whether it is what was asked for is the operator's ([`gates.md`](gates.md) → *Axis C*).

**On entry or resume:** read [stage-10-acceptance.md](stage-10-acceptance.md) before stage work.

- **GATE (auto):** the ladder walk ran and its absences became REQ rows before
  the table was written; **the hand-back is written** — the request quoted as it was
  GIVEN, where the run stands against it, what was solved with its evidence, what
  surfaced that nobody asked for, every decision still waiting **asked here with
  options rather than listed**, and the ambiguity count computed from the four
  registers with its ids ([`progress.md`](progress.md) → *The hand-back*) — a run
  that cannot say what happened has not finished, it has stopped; **the `finish:` line is
  printed beside this verdict — `done`, `budget` or `blocked`, with its block**
  ([`finish-line.md`](finish-line.md) → *The finish block*); **the environment is
  given back** — all eight classes enumerated, everything this run started ended and
  verified by re-enumerating rather than by the teardown's reply, an earlier run of
  this project ended only when **provably spent**, an item this project does not own
  reported rather than ended, and the result written as a `holds:` line
  ([`residue.md`](residue.md)); **every disclosure printed beside the verdict** — `abstained` (what the run declined
  to claim) and `unlooked` (what a check never looked at), neither a ratchet, neither
  with a floor, neither ever a target ([`gates.md`](gates.md) → *Disclosures*); **the
  retrospective is written — stamped first, then pruned, then the entry; the
  list at or under its cap, every deletion logged in the archive with its commit,
  entries older than five run stamps rotated into `<artifacts>/retro/` **and the
  stamp table itself held to ten — at the eleventh the oldest stamp rotates whole into
  the same archive, and both counts print beside the verdict** (the stamp table is read
  in full at stage 0, so *one line per run* is a slope the prune has to stop), the run
  stamped with its commit, every SHA in either file resolvable, and the
  counts printed beside this verdict**; **every entry with a `**Lesson:**` line is in the
  local index (`lessons.py add` printed its id) or its refusal is printed, and the shared
  store's state is one ledger line** (`recorded`, `store refused — <code>`, or `shared
  lessons: absent`); **where `pipeline.json` → `retro.publish` is
  set, the skill-level insight is published as an issue on the skill's repository —
  its body printed in full first, the printed string and the sent string being one
  string, and the five redaction rules applied
  ([`retrospective.md`](retrospective.md) → *What may leave the project*). Absent, the
  step does not exist and is not asked about: publishing to another repository is an
  outward act and silence authorizes none. **Either way the verdict carries a `publish:`
  line** — the issue url, `0 (configured, nothing insight-grade)`, or `not configured
  (N insight-grade entries stayed local)`: an unarmed path and one with nothing to say
  are otherwise indistinguishable, which is how this instruction went unread for eight
  releases** ([`retrospective.md`](retrospective.md) → *`publish:` is a line in the
  verdict*)**; **the documentation gate has been seen
  failing once against a planted defect and its ratchet counts are printed**
  ([`gates.md`](gates.md)); **every repository is closed — the parent included:
  `git submodule status` shows no `+`, each repo clean and pushed**; **every check this gate leans on has been seen failing
  once against a planted defect** (an unproven check's green is not evidence);
  every REQ has a status (none `unknown`); every `verified`
  carries evidence; every `partial` names what's missing and where it's tracked;
  every `deferred`/`dropped` has the operator's agreement and, for `deferred`, a
  tracker entry; no carry-over row left `unresolved`, and the ledger's counts are
  printed with the verdict; the hand-back asks the closing question and carries
  the answer the operator can give at any time. `auto` by default since 1.98.0: a
  check proves the table well-formed, and only the person who asked can confirm it is
  what they asked for, so the run hands that question back rather than waiting on it.
  A project that wants the wait sets this gate `manual`.

## The program loop — a platform, one brick at a time

When stage 2 produced a **module map** ([`decomposition.md`](decomposition.md)),
stages 0–2 have run once for the whole platform and the rest of the pipeline runs
**per module**, in build order:

```
module N → 3 spec (dossier) → 4 plan → 5 build → 6 tests → 7 lint+deploy
         → 8 post-deploy → 9 docs+wiki → 10 acceptance → map status: done
         → module N+1 (back to 3)
```

- **No re-grilling, no re-decomposing per module.** New information that changes the
  map goes back to stage 2 as an explicit, operator-approved map revision — never a
  quiet edit mid-module.
- **Each module's spec is a full dossier** (`spec.md`): architecture, entities,
  contracts in and out, business rules, edge and failure cases, UI/Figma chain when
  it has a surface.
- **Deploy cadence is the brief's call** (autonomy sweep): per module, or once after
  several. Decide it up front, not per module.
- **Update the module map's status in the same commit as that module's acceptance.**
  The map is the resume point after a lost context.
- **Program done** when every row is `done` or `deferred` with an agreed home, the
  cross-module contracts are covered by tests that cross the seam, and a final
  acceptance covers the platform's whole REQ table — not module by module.
- **The whole board, rather than one platform, is wave mode**
  ([`waves.md`](waves.md)): stages 0–4 once over every open item, 5–8 per wave with a
  close pass after each, 9–10 to close the release.

## Cross-cutting — the Doc Loop

A decision is not made at stage 9. It is made the moment something is settled —
in the grill, in the brainstorm's approved design, in the spec's locked contract,
in a ruling on a review finding at stage 5 — and every one of those is a stage that
can lose it.

- **It fires at any stage**, and the seven steps live in
  [`documentation.md`](documentation.md): orient and reconcile → reserve the id and
  record → resolve the question it answers → propagate by the matrix → adjust scope
  → record as-built → commit with the ids.
- **Step 7 is part of the loop, not after it.** A decision recorded and uncommitted
  is a decision that survives exactly as long as the working tree.
- **Reserve before you mint.** Reading *"Next free ID"* is not reserving it, and a
  second agent reading it in the same minute gets the same number.

## Cross-cutting — the loop guard

Any stage can be re-entered and any loop can churn: a pass undoing what an earlier
pass decided, two shapes alternating, the same file rewritten with no new
information. [`loop-guard.md`](loop-guard.md) is the detector and the break
protocol, and it binds every repeating loop here — the stage-5 fix loop, a stage
re-entered after a failed gate, the program loop above, any audit → fix → audit
cycle.

- **Every repeating pass logs one line per touched file** (`touch: <file> — pass N —
  reason: <finding id / gate item>`) to the run ledger. Detection is mechanical, not
  a feeling, and the ledger is what survives compaction.
- **Trips on:** revert-oscillation (A→B→A); the same file edited twice for the same
  reason; a finding already ADDRESSED or parked coming back; a stage entered a third
  time for one artifact; two loops editing one file. Hard caps, each a stop: 3 fix
  rounds per task, 2 re-entries per stage per artifact, 3 passes per module.
- **On a trip: stop editing.** Name shapes A and B with their evidence, escalate to
  the layer that owns the conflict (rubric → operator → plan → spec → module map),
  re-plan the check as an ordered one-item-per-line checklist, then go through it in
  order, one commit per item. Never settle a higher-layer conflict inside a lower
  loop, and never adjudicate before the cap.

## Cross-cutting — the audit

The loop guard governs loops that **change** things. A loop that **looks** for
things fails the other way: it converges, spending pass after pass on its own last
pass's edits while the finding count stays healthy. [`audit.md`](audit.md) is that
method and that exit — the L0→L7 ladder, the seam questions, the axis-rotation
crossover, and the rule that a green from a check nobody has watched fail is worth
nothing.

- It runs **at stage 10 before the coverage table** (the only place that can find a
  requirement nobody ever wrote), **per module** in the program loop, and as the
  whole task when the request is itself an audit.
- **A finding class seen twice becomes a script**, not a third ledger row.
- **Whatever can't be fixed now becomes a ratchet** — a named, counted set that may
  only shrink, printed beside every gate verdict, so "green" never reads as
  "verified".

## A stage that produces text a user will read

The framework has no opinion on which skills run where — `pipeline.json` is the contract —
but two facts about copy are worth stating once, because a stage author rediscovers them
expensively.

**Route it through the copy skill, not through the stage's own prose.** A stage that writes
interface strings, a landing page or a changelog entry for users is producing brand surface;
the registers, terminology and canonical facts that constrain it live in `docs/brand/`, and
a stage writing directly does not read them.

**The humanization pass is decided once, in the brand pack, not per run.**
`docs/brand/voice.md` carries an optional `Humanization pass:` field; absent means nobody
has been asked, and the copy skill asks once and records the answer. A pipeline that asks
every run has turned a settled decision into a prompt, and a pipeline that gates on a
marker count has turned a writing-quality signal into a verdict — the false positives fall
hardest on people writing in a second language, and nothing here fails a stage for them.
`npx sshlg-skills humanizers` lists what is installed.

Entry and resume use the recorded run state ([`continuity.md`](continuity.md)).
