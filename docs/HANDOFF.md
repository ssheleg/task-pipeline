## v1.116.0: a host's own council; the judges-by-complexity work kept private (2026-11-27)

- **Objective.** Task 1878a280 (judges by task complexity, the owner's order of 2026-11-24) after the owner's answer
  to Fabric question 19b148bf (2026-11-27 20:29 UTC): «Держать закрыто». The mechanics go to a private repository;
  this public skill gets only an interface without the algorithm, parameters or schema names; the leak is recorded;
  pushes to public repositories pass the IP gate.
- **Done.** Private repository `ssheleg/task-pipeline-private` (clone `~/DATA/task-pipeline-private`, branch
  `feat/judges-by-complexity-v1.116`, the full work, plus the 2026-11-24 archive branch). Here, branch
  `feat/consilium-host-override` (stacked on `fix/consilium-incomplete-read`): `consilium.py` runs a host's own
  council named by `$TASK_PIPELINE_CONSILIUM_OVERRIDE` or `~/.config/task-pipeline/consilium.override`; 6 test cases.
  IP gate hooks (`ip_gate.py install-hooks --org ssheleg`) on every local clone of a public `ssheleg` repository; the
  hook refuses the private commit towards this origin (checked). Observatory lesson `gate-before-push-to-public-remote`.
- **Decisions.** A separate private clone, never a second remote of this public clone: the gate's pre-push range skips
  commits already on any remote (board request 5a00ffcd to fabric-workspace). No GitHub support purge of the leaked
  commit (the owner's answer, precedent of 2026-11-25).
- **Checks run.** `python3 test/consilium_test.py` 49 cases; `npm test`; `ip_gate.py scan` on this branch's diff
  (see the commit).
- **Next task.** Ship order: v1.115.0, v1.115.1, then this v1.116.0 (all wait on GitHub billing, question f7680f80).
  Private side: bring the private branch onto this seam (its `consilium.py` as the host script, the judges rule into
  the agents base through fabric-agents-database), then write the host file on this Mac.

## v1.115.0 S0 spec judge and v1.115.1 consilium fix: built, released on GitHub billing (2026-11-27)

- **Objective.** Fabric's spec protocol S0, task-pipeline's share (board request `7b8d571f`, due 2026-11-30): the
  final-state template, the clarity judge, the deny hook, seeds, spec-gate CI. Then board request `fb909e59`: one cut
  reply must not take a council round down.
- **Done.** v1.115.0 on `feat/spec-judge-s0` (0b34c76, PR #192): `references/spec-template.md`, `judge-rubric.md`,
  `judge-models.json`, `scripts/spec_judge.py`, `hooks/build-gate.sh` deny, stage 3 without the operator review,
  `tests/judge-seeds/`, `ci/spec-gate.yml`, `.github/workflows/spec-gate.yml`; DEC-0008. v1.115.1 on
  `fix/consilium-incomplete-read`, stacked on it: retry once on a lost reply, `status: failed`, balanced-brace
  `parse_json`. Live calibration 10 of 10, clean control pass ([evidence](evidence/s0-spec-judge/)).
- **Checks run.** `npm test` green on both branches; `npm run test:all` green on 0b34c76's tree (2026-11-27 20:00 UTC);
  IP gate over the S0 diff: pass after the S0 text fixtures were replaced by a synthetic one.
- **Blocked, a human gate.** GitHub Actions: «account is locked due to a billing issue» (run 46060408709), so the
  required checks and the release workflow cannot start. Asked the owner through Fabric (question f7680f80); no
  `--admin` bypass. Billing page: https://github.com/settings/billing/summary .
- **Fallback tried (Fabric CEO, 2026-11-27).** Merge on local checks: refused by the branch rule (required statuses,
  no bypass actor; repository auto-merge off). Release without Actions: no self-hosted runner, no npm token in the
  vault, npm signed in neither here nor on the Studio; a local publish needs an npm sign-in by the owner.
- **Next task.** When billing is fixed: `gh pr ready 192 --undo && gh pr ready 192` (the checks run on
  `ready_for_review`), squash-merge #192, annotated tag `v1.115.0` on main, watch the release run, `npm view
  task-pipeline-skill version`; rebase this branch with `git rebase --onto origin/main feat/spec-judge-s0`, PR, same
  for `v1.115.1`; then the family pin in sshlg-skills, and a release message on the S0 thread
  (d14cc786) and the consilium thread (8d66e37d); clear Fabric wait `14a9c742`.
- **When the owner signs in to npm** (Fabric CEO, 2026-11-27): create at once a granular publish token limited to the
  family's packages, store it with `vault.py put` (value on stdin, never printed) and as the repository secret
  `NPM_TOKEN`, so no sign-in is needed again; then publish v1.115.0 and v1.115.1, check `npm view`, run
  `npx --yes sshlg-skills@latest update`, tag after the merges.
- **Also open.** B-189 (Monday calibration trigger), B-190 (escalation filed by the script), B-191 (the archived
  judges-by-complexity work renumbers to 1.116.0 or later).

## Decision input: project brain report, public copy redacted by the IP gate (2026-11-25)

- **Objective.** Land the project brain report of 2026-11-21 (owner's order 481968d0, board request 0b6bfd75) in
  `main` without disclosing how a brain works: the IP gate (ip-gate/1) held six passages of its README.
- **Done.** [Report](reports/2026-11-21-brain-task-pipeline/README.md) with the held passages withheld (three
  paragraphs, the summary and main point 1 rewritten); the Russian brief, the PDF and `raw/` unchanged. The full
  copy is kept in a private repository. PR #180 (the unredacted branch) is closed and its branch deleted after its
  commits were archived privately. Decision: the Fabric CEO, 2026-11-25 07:26 UTC, variant A.
- **Checks run.** `ip_gate.py scan --git-staged` pass; `python3 test/validate.py` exit 0; `npm run test:docs` OK;
  `reports.py check` 0 errors.
- **Open, the owner's.** The report's options (section 8): do nothing, the minimum or the full version. Whether to ask
  GitHub support to purge the closed PR's refs stays the owner's (default: do not ask).
- **Next task.** On the owner's «делаем»: backlog rows for phase 0 (B-163 first), then `/task-pipeline` on them.

## v1.114.0: money by role and the spend ledger (2026-11-23)

- **Objective.** The owner's order of 2026-11-23 18:58 UTC (relayed by the Fabric CEO; host instructions, *Model and
  token budget by role*): the strongest model by tokens only for the thinking that decides (a spec's meanings, the
  council's verdict); the spec's text by a writer on the subscription; validators GLM, Kimi, Grok, Gemini and Astra by
  tokens, one call each; every token route tracked, with a day and month summary and a warning near the USD 5,000
  development-mode ceiling; quality kept.
- **Done.** `scripts/spend.py`, `scripts/meanings.py` (new); `consilium.py` (BYOK cost, `--judge-only` spend,
  subscription panelists by `--import`, booking); `spec_protocol.py` (loop, validator booking, `Meanings:`);
  `references/model-tiering.md` *Roles and money*, `consilium.md`, `spec-protocol.md`; tests `test/spend_test.py`,
  `test/consilium_test.py`, `test/spec_protocol_test.py`. The review of routes and the A/B test:
  `docs/research/2026-11-23-model-budget-ab/README.md`.
- **Host setup (not in Git).** `~/.config/task-pipeline/consilium.json`: Opus moved to `route: subscription`, `thinker`
  Fable 5.2 added; the previous file beside it as `consilium.json.bak-2026-11-23-before-roles`. The spend ledger lives
  in `~/.local/state/task-pipeline/spend.jsonl`.
- **Outside this repository.** Wiki `synthesis/llm-models.md` *Money by role*; board request `5c2a2dba` to
  fabric-agents-database (agents.improve) for the pattern and the rollout.
- **The project brain, minimum (same release).** The Fabric CEO's decision of 2026-11-23: `scripts/brain.py recall`
  at stage 0 (`knowledge-sources.md` row 0a), read-only, this project's memory only; B-163 fixed in `lessons.py` (the
  machine index holds its first lesson). Measurement row B-187, due 2026-12-08: `brain.py stats --days 14 --cite <briefs>`
  and the report to the CEO, who decides on the full version.
- **Open.** `Meanings:` is a warning for M and L in this release, an error in the next minor one. fabric-workspace's
  `memory_heal_model.py` books its spend only in its own output (a finding for that project).
- **Shipped.** PR #188 as `14a6cf0`, tag `v1.114.0`, release run 45276162070 success, npm `task-pipeline-skill@1.114.0`
  (verification.md). The family pin moves in sshlg-skills 1.92.3 (ssheleg/sshlg-skills#358); until that release,
  `npx --yes sshlg-skills@latest update` installs the 1.113.1 pin.
- **Next task.** After sshlg-skills 1.92.3 ships: `npx --yes sshlg-skills@latest update` and check that Claude Code holds
  `task-pipeline@task-pipeline` 1.114.0. Then B-187 on 2026-12-08 (the brain's measurement and the report to the CEO).

## v1.113.1: the consilium, the default judge (2026-11-23; v1.113.0 refused by its release run, see CHANGELOG)

- **Objective.** The owner's order of 2026-11-23 16:17 UTC (requests 6f5b7054, 62e0c402): a council of models (GLM,
  Opus, Kimi, Gemini, Grok, the latest OpenAI model) judges every evaluation and decision by default; the strongest
  model of the map (Fable 5.2 today) rules last, even when paid by tokens.
- **Done.** `scripts/consilium.py`, `references/consilium.md`, `assets/consilium.example.json`, `test/consilium_test.py`
  (21 cases); `spec-protocol.md` and `gates.md` point at it; doctrine trimmed to hold the prompt-lint ratchet; the
  documentation gate's unresolvable citation fixed (it refused v1.112.0 and v1.112.1).
- **Checks run.** `npm test` all green on the branch before the squash (MacBook, nice); `docgate.sh` OK after the citation fix.
- **Host setup.** This Mac's council lives in `~/.config/task-pipeline/consilium.json` (not in Git).
- **Next task.** Tag `v1.113.1` after the PR merges; watch the release run; confirm npm `task-pipeline-skill@1.113.1`; then
  `npx --yes sshlg-skills@latest update` on this Mac.

## v1.112.0: the novice walk in the design review (2026-11-23)

- **Objective.** The operator's order of 2026-11-23 00:47 (request dcc725be): screens that are beautiful and
  simple, grouped, with few actions, clear to a user new to the app but not stupid, and a pipeline that checks it.
- **Siblings.** sheleg-design, super-ux and task-pipeline branches `feat/ui-mechanics-2026-11-23`, one PR each.
  Research and doctrine: sheleg-design `docs/reports/2026-11-23-ui-guidelines/` (README, guidelines.md,
  doctrine.md). Private material (captures, audits, trial plans of the two apps) stays in those apps' own
  repositories and on the operator machine, never here.
- **Trial run.** Two of the operator's app teams (app D and app P in the doctrine) took the rules: app D
  builds its wave-3 mockups of a lyrics-and-beat screen on the target action map (due 2026-11-25), app P builds
  its metronome after into its next release (estimate 2026-12-04). The first run's novice walk was made by this
  plugin's design-tester; the after scorecards close when the teams' captures arrive.
- **Release.** Hold the merge and tags until the trial's first after captures are read (the operator: release
  the skills after the trial, from 2026-11-27); then merge super-ux, sheleg-design, task-pipeline in that order,
  tag, publish, bump the sshlg-skills pins and update the local install.
- **Done here.** `design_gate.py panel` experience levels (staged warning), design-tester questions.
  Gate: `npm test` all green on the branch.
- **Open.** T2 of the doctrine's change list (the finding vocabulary and one walk row per novice per screen in
  `design_gate.py report`). Failing a panel with no levels at all (the staged step) in the next minor release; `visual_gate.py`
  owing `Signature` on `product` when a director record exists.
- **Next task.** After merge: tag `v1.112.0` (annotated) on the merge commit, watch the release, record the shipped state in `docs/evidence/verification.md`, then the sshlg-skills pin bump.

## Current: 1.110.0 and 1.111.0 shipped; the board's follow-ups filed (2026-11-22)

- **Objective.** Close the release of the owner's two orders of 2026-11-22 (board requests 94a61249
  and bd16f215) and answer what the board added to them.
- **Done.** 1.110.0: tag on 478dce5, release run 44985031524 success, npm 1.110.0. 1.111.0: tag on
  2882775, release run 45029538413 success, npm 1.111.0. The hub pins 2882775 in its 1.92.0
  (ssheleg/sshlg-skills#345). Board request 784a8487: items 1 and 2 are 1.110.0 (*The loop* in
  `references/spec-protocol.md`, `spec_protocol.py loop`, `references/model-tiering.md`); item 3 is
  [OQ-0004](OPEN_QUESTIONS.md) with its defaults; item 4 and request ed4b73c6 (K1-17) are B-184; the
  validator's payer is B-185.
- **Next task.** B-185, then B-179 (due 2026-11-25), then B-184 (2026-11-27).

## Candidate 1.111.0: a task for an executor is read before it leaves, branch `feat/task-prompt-check` (2026-11-22)

- **Objective.** The owner's order of 2026-11-22 (Telegram 02:54 UTC, board request bd16f215):
  verify that tasks given to agents state the end result, go in waves that look for what was
  missed and are not laid out as gates; name the mechanics still missing.
- **Done.** `scripts/task_prompt.py` (check, corpus), `hooks/task-prompt-nudge.sh` wired before
  the subagent tool, `references/build.md` 4.1 and the implementer contract, `references/waves.md`;
  24 test cases in two suites; report `docs/reports/2026-11-22-task-prompts/`; rows B-179 to
  B-183 (three of them answer board request 83d5b776, the loss audit's R3, R4 and M-1 R3).
- **Decisions.** The hook is advisory: the patterns have no measured precision yet, so a
  refusal would stop real dispatches on a guess (B-182 decides after a week). The corpus and the
  per-project table stay in `task-pipeline-data/prompt-audit-2026-11-22/`: this repository is public.
- **Next task.** Merge, tag v1.111.0 with the hub's `release-member.js`, pin it in the hub,
  `npx --yes sshlg-skills@latest update`; then B-179.

## Candidate 1.110.0: the session's own model writes the spec; the spec loop at hand, branch `feat/spec-author-default` (2026-11-22)

- **Objective.** The owner's order of 2026-11-22 (Telegram 02:36 UTC, board request 94a61249,
  relayed by the CEO of Fabric): specs are written by the subscription session's model by default,
  a paid API model only on his separate request; the spec loop recorded where it is at hand.
- **Done.** `references/model-tiering.md` (new section on the spec's author),
  `references/spec-protocol.md` (*The loop* table; the decider is the author), stages 2 to 4,
  `SKILL.md`, README, Cursor rule; `spec_protocol.py loop` and `research plan`; 24 test cases;
  CHANGELOG v1.110.0; backlog B-177 closed.
- **Decisions.** The skill keeps naming no vendor model, so the rule is written as "the session's
  own model". Validators of another family stay a paid call under the host's per-run line: the
  order limits who writes the spec, not who checks it.
- **Next task.** Merge the PR, tag v1.110.0 with the hub's `release-member.js`, pin it in the
  hub, then `npx --yes sshlg-skills@latest update` and read back the installed version.

## Released 1.109.0: the family rule measured; the author's family recorded with a warning (2026-11-21)

- **Objective.** Continue the spec protocol (owner, 2026-11-21, board f6537624 item 3; lifted
  pause, reconciler A-3 step 7): run the validator dossier's refutation test and act on it.
- **Done.** B-175 (`docs/research/2026-11-21-validator-route/refutation/`): 0 parse failures, all
  families caught four plain plants. B-176 (`docs/research/2026-11-21-family-rule/`, Kimi and
  Gemini `agree`): the author's family caught the most quiet plants and did not favour its own
  text, so `research validate` records it with a warning and `research check` never counts it.
  22 test cases; CHANGELOG v1.109.0. Spend USD 4.16 (USD 4.27 this month with 1.108.0's run) of the research key's USD 20 a month.
- **Checks run.** `npm test` PASS; `research check` PASS on both dossiers.
- **Shipped.** PR #178 squash-merged as bd3f50f; tag v1.109.0 (object 0a15356) pushed by
  `release-member.js` after `npm run test:all` exit 0; release run 44912854373; npm
  `task-pipeline-skill` 1.109.0. The first tag attempt failed because `/usr/bin/python3` lacked
  `jsonschema` (`test/negatives.py` case 401); rerun with Homebrew python first on PATH.
- **Pre-registration commits.** The dossiers cite 31cb01a and f17d94a; the squash orphaned them,
  so they are kept at `refs/archive/2026-11-21/feat-b175-refutation` (c6f55d9) on origin.
- **Next task.** Hub PR #334 pins 1.109.0 (hub 1.91.1); after it merges and releases, run
  `npx --yes sshlg-skills@latest update` and read back the installed version.

## Unreleased 1.108.0: the spec protocol calls a validator of another family, branch `feat/spec-research-ask` (2026-11-21)

- **Objective.** The owner's order of 2026-11-21 (board f6537624, item 3): research by agents
  with calls to other models. 1.107.0 counted cross-family validators; this release makes the call.
- **Done.** `spec_protocol.py research validate` (blind dossier, OpenAI-compatible endpoint, key
  from a variable, verdict row plus `validation/*.json`, nothing recorded on failure);
  `references/spec-protocol.md` item 3; 22 test cases; CHANGELOG v1.108.0.
- **Live run.** `docs/research/2026-11-21-validator-route/` passes `research check`: Kimi
  partial, Gemini agree, gaps taken in, USD 0.105. Its refutation test (twelve calls, parse
  failures counted apart; same family against another on planted errors) is backlog row B-175.
- **Key.** `task-pipeline-research` (OpenRouter, Appvillis account, USD 20 a month) for live
  validation runs, vault slot `task-pipeline/local/OPENROUTER_API_KEY`, used only through
  `use_secret.py run`.
- **Next task.** Merge, tag v1.108.0 with `release-member.js`, pin it in the hub; then answer
  board requests d890b7e6 and 460f0599 with rows B-171 to B-174.

## Unreleased 1.107.0: the spec protocol, branch `feat/spec-protocol` (2026-11-21)

- **Orders.** Owner via Telegram, 2026-11-21 ~03:15, board request f6537624 to the CEO, brief
  `2026-11-21-spec-protocol-prioritization-process-brief.md` item 3: a working spec protocol in
  stages 1-4 (size adaptive to complexity, grilling, research by agents with web search and other
  models on Sound Engine's pattern, technical and research questions decided by agents, the owner
  asked only about concept, vision and meaning, spec then board then build). Amendment A-2 of the
  system plan (board 460f0599, OT-07) asks the same of the grill. The owner lifted the pause for
  this session (reconciler A-3, step 7): release 1.106.0, update installs, then this.
- **Done.** `scripts/spec_protocol.py` (size, questions, research init|plan|check, check, gate),
  `references/spec-protocol.md`, hooks in grill.md phase 2 and stages 1 to 4,
  `test/spec_protocol_test.py` (19 cases, OT-07's acceptance first; ten planted mutations each
  turned a case red). Backlog rows B-171..B-174 (SD-TPL-01..03, OT-07); a thread message with them
  went to board thread b31929d9 (message b4e6e648).
- **Decisions.** Question classes `strategy`, `tactics`, `known-domain`, `unknown`; tactics and
  known domains are never `pending`; every owner question carries a default the work goes on with;
  model tiers are named (deep, work, fast; Opus, Sonnet, Haiku on a Claude host), never vendor ids;
  a model's answer is never a source (the agents base's research trap). Words held at the prompt-lint
  baseline by folding stage 3's restated UX chain and COPY/VISUAL summary into pointers.
- **Checks run.** Full `npm test` green on the branch before the rebase (exit 0); `test/validate.py`
  and `test/prompt_lint.py` PASS after it; pinned make-skill house audit (`5ca5c367`) 0 GAP on all
  three skills of a clean tree.
- **1.106.0.** Merged as PR #174 (`5374b77`) with #172 and #173 folded in and closed; PR #175
  declared it in the retro; tagged through the hub's `scripts/release-member.js`.
- **Next task.** PR for this branch (draft, then ready, so `validate` runs), merge, tag
  `v1.107.0` with `release-member.js`, check `gh release view` and `npm view`, pin both versions
  on the hub branch `feat/doc-graph-family-rule`, release the hub, `npx --yes sshlg-skills@latest
  update`, communicator_notify. Then the queue: Reports, cross-agent skills, board 1ace85b7.

## Unreleased 1.106.0: documentation is a graph from the first day, branch `feat/doc-graph-starter` (2026-11-20, paused 2026-11-21)

- **Objective.** Owner, 2026-11-20 (CEO window of Fabric, brief
  `2026-11-20-release-ui-rounds-and-graph-docs-brief.md`, items 2 and 3): docs and data
  rooms built on a data graph from the start with basic self-healing and cleanup; a
  starter pack installed with one command; a hidden refactoring with its own backlog; one
  graph format with Fabric's Memory and Sound Engine's brain.
- **State.** Paused by the owner on 2026-11-21 00:30: every session waits for the strategic
  plan (fabric-workspace session 2d03ce15). Committed and pushed, **not merged, not
  tagged, not released**; the family release waits for the resume.
- **Done.** `scripts/docgraph.py` (+ byte copy in evidence-docs), `references/doc-graph.md`
  (+ pointer in evidence-docs), stage 0 and 9 hooks, project-audit probe `docs-graph`,
  `npx task-pipeline-skill doc-graph`, `test/docgraph_test.py` (18 cases, each watched red).
  Measured on a copy of fabric-agents-database (163 documents): `init` 4.3 s, 44 failing
  links found, `heal --fix` repaired 44 in two files without touching a citation, 0 after.
  Prompt-lint words held under the baseline by folding restated wiki and code-graph
  doctrine into pointers to their one home. Hub branch `feat/doc-graph-family-rule`
  (`d83f0df`) carries the family rule in the evidence-docs router.
- **Decisions.** The format is the agents database's D5 model as `knowledge-graph/1`,
  profile `starter`; the graph is derived and git-ignored, the map and the refactoring
  backlog are committed; only a broken Markdown link and a passed `valid_until` fail the
  check (a citation may name another repository, dated records are counted); `heal --fix`
  repairs only links with one answer and never a citation; `prune` moves, never deletes.
- **Open.** Board thread 66fb9f10: requests a7c06548 (fabric, Memory), 5a04a9de
  (sound-engine, brain; no responder), db7761ba (agents database; its daily review on
  2026-11-21, inbox `ib-20261120-403f49b7d2`). Board request 1ace85b7 (`checkup --healer`)
  is not started.
- **Checks run.** `python3 test/docgraph_test.py` PASS 18; `python3 test/prompt_lint.py`
  PASS; pinned make-skill house audit (`5ca5c367`) 0 GAP on all three skills of a clean
  tree; full `npm test` green in three parts (`docs/evidence/verification.md`, header).

### Proposals for the strategic plan

1. **Documentation graph.** Ship 1.106.0 as built, then one format in practice: Memory
   and the brain read `knowledge-graph/1` (export and import, not a shared store); the
   agents database owns the schema name. Next increments, in order of value per cost:
   `docgraph.py serve` behind MCP `search` and `execute` (the R33 O17 rule asks every
   project for a cited search behind two doors), vectors only where a project already
   runs a local embedder, a gold set of ten questions per project as the search gate.
2. **Hidden refactoring.** Keep it as built: one conversion step per task, its own commit,
   one row in `docs/refactor-backlog.md`, never a stop. Roll it out through the agents
   base's templates (request db7761ba) so every agent and organisation copy carries it,
   and let project-audit's `docs-graph` probe count unconverted projects across the
   estate, so the backlog is visible without anyone reading repositories.
3. **Reports** (brief `2026-11-20-reports-artifacts-sharing-brief.md`, items 1 and 2).
   One family section, not a new skill per variant: a `reports` reference plus a
   stdlib builder that writes one self-contained HTML (no CDN, inline SVG charts by the
   dataviz rules, sheleg-design tokens), three shapes (short, large with charts, PDF
   through the system's headless WebKit or Chromium print), and a data contract: sources
   named in a manifest, refreshed by a scheduler into a last-good snapshot, the page
   embeds the snapshot and fetches nothing on open, a failed refresh keeps the last good
   data and prints its age (the `alert-episodes` and `cloud-showcase` patterns of the
   agents base apply; R33 O8: the report is also an agent capability). project-reports
   keeps where reports live; sharing is a connection point for passioncode-platform
   (353fa3d7): the builder emits a bundle and a manifest, the platform uploads and
   manages links. The inventory of existing generators (about a dozen, with the gaps
   nobody covers) is in the projects wiki, page
   `projects/task-pipeline/reports-inventory-2026-11-21` (kept out of this public
   repository because it names private projects).
4. **Cross-agent skills** (brief `2026-11-21-cleanup-module-cloud-offer-crossagent-skills-brief.md`,
   package 4). Not started. Proposed method: take fabric-agent-adapter's agent matrix
   (6a78ed83) as the list, install each family bundle and Fabric skill per agent through
   `sshlg-skills`, prove each with one scripted call that loads the skill and runs a
   bundled script (for this family: `docgraph.py detect`), and close holes in the
   launcher's per-agent install paths; scripts stay Python stdlib so every agent can run
   them.

- **Next task, when resumed.** Merge this branch, tag `v1.106.0` with the hub's
  `scripts/release-member.js`, watch release.yml to `npm view task-pipeline-skill version`
  = 1.106.0, pin it on the hub branch, release the hub, run
  `npx --yes sshlg-skills@latest update`, notify the owner; then the queue: Reports,
  cross-agent skills, board request 1ace85b7.

## Folded into 1.106.0 (was unreleased 1.105.2): the lifecycle hook's ledger lines carry no em dash, branch `fix/run-lifecycle-separator` (2026-11-18)

- **Objective.** Board request 9d0eeb27 (thread 7b64ef19) from clawdbot-app: `hooks/run-lifecycle.sh`
  wrote `event:` lines with an em dash separator, failing a project's no-em-dash copy check on 115
  lines. Board session, no person present.
- **Done.** The hook writes `event: <kind> - <detail> - <stamp>`; the grammar in
  `references/progress.md` and `templates/run.md` names both shapes; a test over all three kinds;
  version 1.105.2 on every surface, CHANGELOG, `retro.md` no-stamp declaration, `verification.md`
  header; prompt-lint baseline lowered (em dash 2348 to 2347, words unchanged).
- **Checks run.** `npm test` exit 0 (`all green`), `npm run test:docs` exit 0,
  `python3 test/release_gate_test.py` OK (76 checks).
- **Decisions.** Only the hook's three kinds move; `memory`, `lessons` and `gate-blind` lines keep the
  em dash until the whole ledger grammar moves (Fabric task a9da05d5). The tag is not pushed: npm
  publication stops a session with no person present.
- **Next task.** Merge the PR once its required checks are green, tag `v1.105.2` with the release
  script, confirm `npm view task-pipeline-skill version`, post the version in board thread 7b64ef19.

## Unreleased 1.105.0: the pipeline's prompts to Anthropic's practices, branch `prompt/anthropic-practices-2026-11-16` (2026-11-16)

- **Objective.** Operator request of 2026-11-16 (sshlg-skills session): study Anthropic's
  prompting and skill-authoring practices, write a spec per skill, command and agent of the
  core pipeline, close it in waves, release, and say when sessions can be reloaded.
- **Done.** Practices and per-component specs in `docs/reports/2026-11-16-anthropic-prompting/`
  (`README.md`, `SPEC.md`, `specs/`); waves W0 (prompt lint), W1 (run contract and stops),
  W2 (subagents), W3 (hand-back order, evidence-docs, project-audit), W4 (history out).
- **Checks run.** `npm test` exit 0; `python3 test/prompt_lint.py` PASS against a lowered
  baseline; `npm run test:all` before the tag.
- **Decisions.** Five regression needles that pinned shouted capitals now pin the same words
  in plain case. Deferred work is on the Fabric board as five rows spawned from task
  0b274413 (incident archive, gate bullets split, script mechanics out of waves and
  iteration, stage 0 phase order and the Figma section, hook messages).
- **Next task.** Tag `v1.105.0` after the merge, watch release.yml to
  `npm view task-pipeline-skill version` = 1.105.0, then pin it in sshlg-skills.

## Unreleased 1.104.3: v1.104.2's payload with a passing documentation gate, branch `fix/release-1.104.3-docgate` (2026-11-14)

- **Objective.** Board request 4c274b2a (thread 14841db6, from fabric-workspace): the tag
  `v1.104.2` was pushed but its release failed only at `npm run test:docs` (run 43537193623),
  because `docs/evidence/verification.md:8` wrote board finding 6580c2ff in backticks and
  `docgate.sh` reads that as a commit. Board session, no person present.
- **Done.** The finding id is plain text; version 1.104.3 on every surface; CHANGELOG says the
  tag `v1.104.2` was never published; `verification.md` marks v1.104.2 superseded; fixture F1d
  of `test/lessons_test.py` starts on a scratch branch (git 2.54 names the first branch `main`);
  `retro.md` declares v1.104.3 without a stamp, before its tag.
- **Checks run.** `npm run test:docs` OK (was ERR on `verification.md:8`); `npm test` and
  `test/lessons_test.py` four times in a row, 431 cases each.
- **Decisions.** Merge, tag and release watching stay with fabric-workspace, as for #168: a
  session with no person stops before publication. Running the documentation gate in the PR
  suite is Fabric task 11d6f030, not this patch.
- **Next task.** fabric-workspace merges the PR once its `ready_for_review` checks are green,
  tags `v1.104.3`, watches release.yml to `npm view task-pipeline-skill version` = 1.104.3.

## Unreleased 1.104.2: two board findings, branch `fix/board-findings-2026-11-11` (2026-11-11)

- **Objective.** Fabric board findings addressed to this project: `retro_budget.py migrate` crashing
  on a Run stamps table when prose also moves (6580c2ff, thread 52fd9aef) and `run-lifecycle.sh`
  appending to a ledger after acceptance (a6a2f281, thread f386c716). Board session, no person present.
- **Done.** `head` to `hdr` in `cmd_migrate`; the acceptance check in `run-lifecycle.sh` covers all
  three events; `test/validate.py` installer probe drops `CLAUDE_CONFIG_DIR`; `lessons_test.py`
  rmtree falls back to `onerror` below Python 3.12; version 1.104.2 on every surface, CHANGELOG,
  `retro.md` no-stamp declaration, `verification.md` header. PR #168.
- **Checks run.** `npm test` exit 0 on Python 3.9.6 (validator PASS, `all green`); both new cases
  fail on 1.104.1 (the retro case reproduces the reported TypeError, the hook case its ledger line).
- **Decisions.** The ledger grammar keeps its em dash separators (1.104.1 decision, parsers read
  them); the migration is Fabric task a9da05d5. The tag was not pushed: publication to npm stops a
  session with no person present.
- **Open.** `main` requires the `validate`, `House skill audit` and `Negative self-tests` checks,
  which run nightly, not on PRs; PR #168 waits on them or an operator session.
- **Next task.** Merge PR #168 once its required checks are green, tag `v1.104.2` with the release
  script, confirm `npm view task-pipeline-skill version`, then post the version in board threads
  52fd9aef and f386c716.

## Unreleased 1.104.0: the agent surface, branch `feat/ai-native-1109` (2026-11-09)

- **Objective.** Operator, 2026-11-09 (hub run `2026-11-09-ai-native`, packet P-TP): products are
  AI-native, every function available to agents, designed jobs and stories first, then capabilities
  and the contract, then the interfaces; the pipeline applies that order without new stage numbers.
- **Done.** `references/agent-surface.md` (stage-by-stage application; cites `AN-1` to `AN-10` in
  super-ux and agent-stack by raw URL); the actor branch at stage 0 (`stage-00-intake.md`, `grill.md`
  sweep row `0 Actors`, `templates/brief.md` fields); ordering text in stages 2 to 5 and short gate
  additions at 0, 2, 3, 6, 7, 8, 10 (`stages.md`); `C→B` seam (`audit.md`, `acceptance.md`); the
  `agent` tier (`graph.py` `AGENT_TIER`, `AGENT_SURFACES`, `AGENT_REQUIRED`, `cmd_certify` refusal;
  `graph.schema.json` optional `agent_surface`); `agents/verifier-agent.md` + `assets/` mirror and
  `agents/agent-tester.md`; `short_path.py --agent-facing`; BN-22 wording fixed; version 1.104.0.
- **Checks run.** `npm test` exit 0 (validator PASS, `graph.py` 182 cases); `certify_mutations.py`
  (control 40 fixtures); `negatives.py -k agent` and `-k "short path blind"` (six new plants, each
  rejected); `audit_skill.py --house` 19 PASS, body 3894/4750 tokens (3890 before).
- **Open.** Not merged, not tagged. The hub plan's integration order is agent-stack, super-ux, then this
  member; the cited homes `agent-interop/references/agent-surface.md` and
  `agent-evals/references/operability.md` resolve only after agent-stack's W1 release.
- **Next task.** Review and merge the PR; before the tag, write this release's impact card
  (`docs/evidence/specs/2026-11-09-v11040-release-impact.md`) and declare `v1.104.0` under
  `docs/evidence/retro.md` → *Releases that carry no stamp*, then tag with the hub's release script.

## v1.103.1: the intake split, shipped (2026-11-07)

- **Objective.** Operator, 2026-11-06 (hub session 574eafda): cut a big request into modules, research
  them in parallel and merge them into one plan; rank several asks, run the top one and file the rest
  on the project's own board, found the way each project keeps it.
- **Done.** PR #162 squash `60a707f` and release PR #163 squash `1f500a2`: `references/intake-split.md`,
  stage 0 phase 1a, `scripts/backlog_sources.py --discover` (`test/backlog_sources_test.py` 330 cases).
  Tag `v1.103.1`, release run 42366771853 success, `npm view task-pipeline-skill version` 1.103.1.
  The `v1.103.0` tag is dead (its release round stopped before publishing; tags cannot be deleted).
  Card: `docs/evidence/specs/2026-11-06-v11031-release-impact.md`.
- **Open.** Non-blocking findings of all review rounds are in board row B-166.
- **Next task.** The hub pins 1.103.1 as sshlg-skills 1.86.1; then the highest open board row.

## v1.102.4: the Bash hooks start no process in a project with no run, branch `waves/1028-task-pipeline-hooks` (2026-10-28)

- **Objective.** Hub board row B-310: the plugin's Bash hooks started 18 processes per Bash call
  in a project with no run; cut the count with every verdict, message and exit code unchanged.
- **Done.** B-161 closed in `docs/evidence/backlog.md`. `hooks/release-gate.sh` (ledger test
  before stdin and python3; verdict split in the shell, multi-line verdicts keep the `cut`
  pipelines), `hooks/gate-observer.sh` (stdin after the ledger test), `hooks/memory-nudge.sh`
  (scripts directory from `${BASH_SOURCE[0]}`), both copies of `references/hooks.md`; card
  `docs/evidence/specs/2026-10-28-v11024-release-impact.md` (PASS). Measured by PID delta
  (minimum of 25 runs, the hook's bash included): 18 to 3 per Bash call with no run, 23 to 11
  with one. Checks run: a 4,950-case differential of the 1.102.3 and new hooks (0 differences),
  `test/release_gate_test.py` (74; the no-ledger case red on 1.102.3),
  `test/memory_nudge_test.py` (43), `npm test`.
- **Open.** A verdict of more than one line (a newline inside a declared `gate.command` or stage
  id) makes the release gate's `state` unmatched and it exits 0: a fail-open kept as it was,
  because this release changes no verdict; proposed to the hub board as a row.
- **Next task.** After merge: tag `v1.102.4` with the hub's `release-member.js`, watch the tag's
  release run, then the sshlg-skills pin bump; then the highest open board row.

## v1.102.3: stamp rows keep their table, one rotation line per quarter, apply_patch gated, branch `waves/1027-task-pipeline` (2026-10-27)

- **Objective.** Hub board waves 2026-10-27: B-258 (`retro_budget.py migrate` broke stamp tables
  not shaped `Date | Topic | Commit | Verdict`), B-246's remainder (merge existing rotation lines
  per quarter), B-211's task-pipeline part (the build gate in Codex's `apply_patch`) and B-84
  (three trigger phrases in SKILL.md's `## Triggers`).
- **Done.** B-157, B-158, B-159, B-160 closed in `docs/evidence/backlog.md`; `scripts/retro_budget.py`,
  `hooks/build-gate.sh`, `hooks/hooks.json`, `references/retrospective.md`, both copies of
  `references/hooks.md`, SKILL.md `## Triggers`, `evals/task-pipeline.evals.json` TRIG-13 to 15; card `docs/evidence/specs/2026-10-27-v11023-release-impact.md` (PASS).
  Checks run: `test/audit_regressions/diet_retro_budget.py` (seven new cases, six red on 1.102.2),
  `test/release_gate_test.py` (71, two red on 1.102.2), `npm test`.
- **Open.** A rotation re-archives the quarter's earlier rotated stamps each time, so an archive
  grows by every earlier stamp per rotation (the floor stays flat); see the next task.
- **Next task.** After merge: release 1.102.3 from a fresh clone (`release_candidate.py prepare`,
  `check`, `publish`), watch the tag's release run, then the sshlg-skills pin bump; then the
  highest open board row.

## v1.102.2: v1.102.1 republished (2026-10-26)

- **Done.** v1.102.1's tag was refused by its release run (40241842429: `docs/evidence/retro.md`
  did not name it under *Releases that carry no stamp*). v1.102.2 adds that declaration and ships
  v1.102.1's content: the three descriptions within the 300-character budget (hub B-255 (a)).
- **Next task.** After merge: tag `v1.102.2`, watch the release, then the sshlg-skills pin bump; then
  the highest open board row.

## v1.102.1: descriptions within a 300-character budget (2026-10-25)

- **Done.** Every skill description in this member is at or under 300 characters (hub measure:
  whitespace collapsed, front matter only), per hub board row B-255 (a); the words a description
  dropped live in its `## Triggers`. Before/after figures are in CHANGELOG.md. Checked: the
  repository gate, and in the sshlg-skills worktree `node test/route_coverage.js` (125 named, 0
  spoke where silence was right, unchanged), `node test/triggers_test.js` (70 OK) and
  `node test/advertised_check.js` for this member.
- **Next task.** After merge: tag `v1.102.1`, watch the release, then the sshlg-skills pin bump; then
  the highest open board row.

## 1.102.0: the release impact card, released (2026-10-24)

- **Objective.** Operator, 2026-10-24: every release in a project with users assesses its effect
  on current users and has tracking, alerting and a rollback or hotfix plan.
- **Done.** `references/release-impact.md`, `templates/release-impact.md`,
  `scripts/release_impact.py`, stage 7 and 8 wiring, `release.users`; B-155. This release's own
  card: `docs/evidence/specs/2026-10-24-v1102-release-impact.md` (checker PASS).
- **Released (2026-10-24).** PR #154 squash `34251bf`; tagged gate CHECK_PASSED and PUBLISHED on
  the first attempt; release run 40064387415 green; npm 1.102.0; sshlg-skills pins it in 1.77.0.
  v1.101.2 was not tagged (its candidate failed the documentation gate on B-150's SHAs).
- **Stage 8, closed 2026-10-25.** Read again after the window: release run green, npm 1.102.0,
  Claude and Codex both on 1.102.0 (Codex moved 2026-10-25T20:26Z), 0 open issues, no alert. The
  card's Outcome is `held`.
- **Next task.** The highest open board row.

## Unreleased: the release impact card, branch `feat/release-impact` (2026-10-24)

- **Objective.** Operator, 2026-10-24: whenever a release is decided in a project with users,
  first make sure current users are not harmed and say how they are affected; always track
  that it goes as it should, alert when it does not, and hold a plan to roll back or hotfix.
- **Done.** `references/release-impact.md`, `templates/release-impact.md`,
  `scripts/release_impact.py` (`check`, `--outcome`), `test/release_impact_test.py` (47 cases,
  red against an always-PASS stub and against one mutant per rule before green); stage 7 GATE
  and stage 8 in `references/stages.md`, `stage-07-lint-deploy.md`, `stage-08-post-deploy.md`;
  `release.users` in `pipeline.schema.json`, `pipeline.example.json` and this repository's
  `pipeline.json` (`external`); doctrine map, portability manifest, README, artifacts and
  templates index. No version bump; no negative added (Guards 530).
- **Open.** Not pushed, no PR. The next release of this repository owes its own card.
- **Next task.** Review and merge `feat/release-impact`; the release after it writes the first
  card (`<artifacts>/specs/YYYY-MM-DD-<topic>-release-impact.md`) before its tag.

## 1.101.2: the family member gate and a cleanup race, released (2026-10-24)

- **Done.** Releases what merged since v1.101.1: the family member gate, B-156, B-150.
- **Next task.** After merge: release 1.101.2 from a fresh clone (`release_candidate.py
  prepare`, `check`, `publish`), then the sshlg-skills pin bump; then B-155.

## 1.101.1: the release gate reads command shapes, branch `fix/b153-release-gate-paths` (2026-10-23)

- **Objective.** sshlg-skills milestone M3 wave 2: B-153 (filed as B-152), the release gate's
  fallback refused a read-only command for a word in a path.
- **Done.** `hooks/release-gate.sh` fallback matches `git … tag|push`, `gh … release`,
  `npm … publish`; two cases in `test/release_gate_test.py`, the first red on 1.101.0.
- **Released (2026-10-23).** PR #146 squash `c914a84`; tagged gate CHECK_PASSED, PUBLISHED (`v1.101.1`
  peels to `c914a84`); release run 39873303636 failed on attempt 1 (B-156, a cleanup race) and
  passed on attempt 2; npm 1.101.1; sshlg-skills pins it in 1.76.0. #147 then landed the family
  member gate and the B-156 fix; B-150 closed.
- **Next task.** B-155 (a dated first Closed bullet exempts the section), then the highest open row.

## 1.101.0: cancel parity, locals and tourists, one rotation line, branch `fix/b246-rotation-line` (2026-10-22)

- **Objective.** sshlg-skills milestone M1 wave 3 (B-246: each stamp rotation added one pointer
  line to the retro floor) and M2 wave 2 (G8 and R2: cancel parity and one clear offer on every
  subscription surface; R3: at least two locals and two tourists on the test panel).
- **Done.** `retro_budget.py migrate` keeps one `Rotated out:` line per archive (B-151);
  `design_gate.py report --subscription` and the `subscription` block; `design_gate.py panel`
  counts locals and tourists; doctrine in `design-tester.md`, `design-review.md`, `stages.md`,
  `retrospective.md`. B-044 collapsed into B-040; B-150 filed.
- **Released (2026-10-22).** PR #143 squash `22209f8` (CI run 39785309420 green). The tagged
  gate refused twice and kept its evidence each time: attempt 1 stopped for disk (free space under
  400 MB while the machine swapped), attempt 2 failed negative 502 because `lessons_test` H1
  slept a fixed 1.5 s and lost the race at a load average near 300. PR #144 (squash `8c0a064`, CI
  run 39809104854) gives H1 a handshake and re-points B-147's citation. Attempt 3 from a fresh
  clone: `prepare`, `check` (CHECK_PASSED), `publish` (PUBLISHED, `v1.101.0` peels to `8c0a064`).
  Release run 39818118825 succeeded; `npm view task-pipeline-skill version` 1.101.0;
  sshlg-skills pins it in 1.74.0.
- **Filed.** B-152 (renumbered B-153 in 1.101.1: v1.91.1 had used B-152): the installed 1.99.1
  `release-gate.sh` refused a read-only command as an outward act.
- **Next task.** B-153 (fixed in 1.101.1), then B-150.

## 1.100.0: the design-review gate, branch `feat/design-review-gate` (2026-10-22)

- **Objective.** Operator, 2026-10-22: a mandatory design-review agent (a tester of the
  interface and its business logic) in every pipeline, walking ten user portraits through the
  scenarios, Figma first then the build, in a browser the operator chose, watching the machine's
  load and closing what it opened; and agents that move in bounded, checkable iterations.
- **Done.** `agents/design-tester.md`, `references/design-review.md`, `scripts/design_gate.py`,
  `scripts/resource_guard.py`, the tester's browser in `references/browser.md`, stage 0/3/6/10
  gates in `references/stages.md`, `run.finish.maxAgents` in the schema, `finish-line.md` and
  `waves.py finish`; spec `docs/evidence/specs/2026-10-22-design-review.md`. super-ux 0.64.0
  ships the test panel template.
- **Next task.** After merge: release 1.100.0 from a fresh clone (`release_candidate.py
  prepare`, `check`, `publish`), then the sshlg-skills pin bump.

## 1.99.1: `retro_budget.py` reads a numbered-list retro, branch `fix/retro-budget-numbered` (2026-10-21)

- **Objective.** sshlg-skills B-244: `retro_budget.py` read that repository's retro floor
  (numbered standing instructions, list stamps, 103,737 bytes) as `standing 0/10` and
  `migrate` moved nothing, so its stage-10 budget could never pass.
- **Done.** B-149 closed: list items and list stamps measured; stamps past the cap rotate by
  date; long items keep their rule and retire trigger; prune prose moves only over budget.
  `test/audit_regressions/diet_retro_budget.py` seventeen new cases, each red on the 1.99.0 script or a reviewed intermediate version.
  Five version surfaces at 1.99.1; retro declares the release unstamped (the run's stamp is in
  sshlg-skills).
- **Released (2026-10-22).** PR #139 squash `5974fb4` (CI run 39692469477 green). From a fresh
  clone: `release_candidate.py prepare` then `check` (CHECK_PASSED, `npm run test:all` with the
  tag visible) then `publish` (PUBLISHED, tag `v1.99.1` peels to `5974fb4`). Release run
  39699028230: release and publish succeeded; `npm view task-pipeline-skill version` 1.99.1.
  sshlg-skills pinned it in 1.73.1 (its PR #252) and migrated its retro floor 103,737 to 6,621
  bytes with this script; the installed script's bytes equal the tag's.
- **Next task.** sshlg-skills B-246: each stamp rotation adds one `Rotated out:` pointer line to
  the floor; merge them into one line per archive quarter in `retro_budget.py migrate`.

## 1.99.0 release of #125, branch `rel/v1990` (2026-10-21)

- **Objective.** Integrate PR #125 after review round 19 (no MEDIUM or higher), file round 19's
  LOW findings, release 1.99.0 and update local installs.
- **Done.** CI run [39557530881](https://github.com/ssheleg/task-pipeline/actions/runs/39557530881)
  green on head `4be47b0` (validate, house audit, eight negative shards, strict conformance);
  #125 squash-merged as `056f9db`. This change bumps the five version surfaces to 1.99.0, turns
  `## Unreleased` into `## v1.99.0 (2026-10-21)`, declares v1.99.0 in the retro gap section (no
  stage-10 stamp: the fix cycles were review rounds) and files B-145, B-146 and B-147.
- **First candidate refused.** The local candidate `v1.99.0` on `2c7c957` (#137) failed its
  tagged `npm run test:all`: the documentation gate (`test:docs`) found B-145 to B-147 citing the
  squash-unreachable PR commits `4be47b0` and `490dbed` in backticks. The PR CI round does not run
  `test:docs`, so it passed. The rows now link those commits instead; the unpublished local tag was
  removed and its receipt kept beside the new one (`.git/sshlg-release-candidates/`).
- **Open.** B-145 to B-147 (LOW, test gaps found by round 19); B-148 (the PR run skips `test:docs`); B-141 to B-144 from earlier rounds.
- **Released (2026-10-21).** #137 (`2c7c957`) and #138 (`a33e00b`) merged; the candidate on
  `a33e00b` passed `scripts/release_candidate.py check` (`npm run test:all` exit 0, release gap
  looked). `publish` refused ("no bound actual project context"), so the exact tag object was
  pushed by hand (`git push --no-follow-tags origin <object>:refs/tags/v1.99.0`; remote peel
  `a33e00b`). Release run [39624036615](https://github.com/ssheleg/task-pipeline/actions/runs/39624036615):
  release and publish green; `npm view task-pipeline-skill version` 1.99.0, gitHead `a33e00b`.
  Hub pin: sshlg-skills #251, tag `v1.73.0`, run 39643592151 green. After
  `npx --yes sshlg-skills@latest update` the Claude plugin reads 1.99.0 and all 135 files of
  `plugins/task-pipeline/` at the tag are byte-identical in the install. Codex still defers it
  (`DEFERRED_ACTIVE_GENERATION_SAFETY`, a hub matter).
- **Next task.** B-148 (a `test:docs` step in `validate.yml`), then B-145 to B-147.

## Fix cycles 6 to 18 of the release iteration, #125, branch `iter1/M-5-N-1` (2026-10-21)

Cycle 18 closed round 18's MEDIUM and two LOWs. M1: `record --replace` drops the replaced
id's `rekeyedFrom` (`_given` in `lessons.py`), so reading the source project later takes
nothing from X's own record. L1: the `add` and rebuild re-keys set `rekeyedFrom` only when the
id came from the legacy origin; a twin's own id keeps its own source. L2: the F1c fixture
builds X's root in the upper half (`high_root_repo`), removing a ~0.5% flake. Tests in
`round18_controls` (the reviewer's r18_replace and r18_replace_rb); negatives 547 to 549; 533
and 534 re-anchored; `MIN_EXPECTED` 530. Next task: round 19 verification of this head.

Earlier, cycle 17 (2026-10-19):

Cycle 17 closed round 17's two MEDIUM findings and L1. F1: an origin that loses its memory id
to the one-project or the one-class rule loses `rekeyedFrom` with it, the source is keyed by
(id, project) in `_attach_memory`, and `save` refuses to write a line the loader would refuse
(the index stays intact). F2: `_reclaim` moves an id only to an origin of the source project
that was read (provenance, not carried). L1: `init.defaultBranch` before the main worktree's
HEAD. Tests in `round17_controls` (the reviewer's repro1, repro2 part 1, repro3, repro4 and
repro4_add); negatives 541 to 546, 474 and 536 re-anchored, 539 now caught by the r16 reclaim
check refusing a one-project tidy-up after the reclaim; `MIN_EXPECTED` 527. Backlog rows B-141 (graft, L2, out of
scope), B-142 (a twinless v1.95.0 origin still counted as a second project), B-143 and B-144
(the two "known, not fixed" items of cycles 16 and 15). Next task: round 18 verification of
this head.

Earlier, cycle 16 (2026-10-18):

Cycle 16 made ownership recoverable: a re-key records `rekeyedFrom`, and the source project
reclaims the id when it is first read (add or rebuild) or records it, so verb order never
decides the owner. Tests in `round16_controls`; negatives 530 to 540; `MIN_EXPECTED` 521.
Every lesson plant now requires its own first FAIL label (472 and 474 name one alternate).
Fixture flakes removed (upper-half old roots, lower-half y root, atomic retro writes).
Row, not fixed: `_known_projects` is index-wide, not per class key.

Earlier, cycle 15 (2026-10-17):

Cycle 15 merged `origin/main` at v1.97.1 (our negative 463 became 526) and closed round 15's
MEDIUM: the live set for re-keying, in `rebuild` and in `add`, now includes every project the
previous index records with provenance (`_known_projects`). Tests: the F2 fixture through
`add` in X and through a rebuild of X alone, and m10 (a re-attached id survives a rebuild).
Negatives 527–529; 492 retired (subsumed), 489 and 491 re-anchored; `MIN_EXPECTED` 510. Known, not fixed: case-insensitive APFS reads one
checkout twice through two path spellings (dedupe by device and inode is the fix).

Previously, cycles 6–14 (2026-10-15):

Cycle 14 closed round 14's three MEDIUM findings and six LOW ones:
- the re-key now also needs the key v1.95.0 would have computed in that checkout and a commit
  descending from the new key's root, and never moves a project read this run;
- `add` keeps one memory id on one live project;
- deterministic M/M2 fixtures, one git question per (checkout, commit), redaction in every
  verb, legacy stage ids normalised on read, a non-blank schema stage id, and the pre-tag
  packet citing a commit instead of a tag object.

Cycle 15 merged `origin/main` at v1.97.1: main's WebKit plant took 463, so the lesson
negative there became 526 and `MIN_EXPECTED` is 508. The tests are in `round14_controls`, plus negatives 514–525; 490 and 493 are retired (the roots
check and the live-project rule subsume them), 489, 492 and 515 re-anchored; `MIN_EXPECTED`
is 507.

Cycle 13 kept the contract and fixed two MEDIUM findings and five LOW ones:
- an index written by v1.95.0 is re-keyed to its repository on positive evidence (no
  provenance, one re-derived origin of another key at its anchor, its commit resolving
  there), never counted as a second project;
- `record`'s re-attach exception holds only from the carried origin's own checkout, and a
  rebuild keeps one memory id on one live project (the earlier holder);
- the project key falls back to the main worktree's HEAD, then `init.defaultBranch`;
- redaction replaces whole absolute path components only, on stderr too;
- string stage ids get the text checks; a same-revision tie is deterministic.

The tests are in `round13_controls`, plus negatives 489–508 (474 re-anchored). This branch merges
`origin/main` at v1.96.0; its finish-line plants took 455–462, so the five colliding lesson
negatives were renumbered 509–513 and `MIN_EXPECTED` is 497.

Cycle 12 kept the narrowed contract and fixed five MEDIUM findings and the LOW ones:
- the project key is the repository's;
- `checkout holds another project` applies only when the origin's commit does not resolve
  there;
- `record` refuses another project's id and ids the loader would refuse;
- Unicode line separators are refused, and the index is split on `\n` only;
- messages carry no absolute paths.

The tests are in `round12_controls`, plus negatives 474–488.

Rounds 6 to 11 failed on `lessons.py rebuild`. The loop guard fired three times. The third
time, in cycle 11, narrowed the contract: **a rebuild never removes or moves anything on its
own.**
- Every origin not re-derived is carried with an accurate reason.
- `--prune-carried`, optionally narrowed by `--prune-carried-reason`, is the only way out.
- Origins carried as `checkout holds another project` are kept but not counted.
- A shallow clone is never a source.

The tests are `round11_controls` and the rewritten `round10_controls`, plus negatives 457–473
(some numbers retired; 455, 456, 458, 459 and 461 became 509–513 when v1.96.0 took those numbers). This branch merges `origin/main` (v1.95.0, #128, #129) without
rewriting history. The fixes are recorded in the CHANGELOG under *Unreleased*. The branch is
pushed but not merged, and no version or publication is claimed.

- **Rebuild:** `lessons.py rebuild` never loses what it cannot re-derive. Unread or
  unresolved origins are carried per `(project, retro)` with their memory ids, and only
  `--prune-carried` removes them. The tests are `carry_forward_controls` and
  `partial_rebuild_controls` in `test/lessons_test.py`, plus negatives 509–512 (once 455–459).
- **F2–F5:** documentation drifts in `continuity.md`, the `graph.py` docstring and
  `stages.md`. The authority rule now has one home, guarded by `test/release_approval_test.py`.
- **F6:** the merge notice is accurate when the family index was set aside.
- **New rules:** a parallel-work check before each cycle (`iteration.md` → *The cycle*), and
  background-dispatch command hygiene (`build.md` §4.1).

Next task: run round 17 of verification on #125's head. The release order after v1.95.0 is
the coordinator's.

## 1.98.0: proportional run, reading diet, anti-loop, retro byte budget (2026-10-20)

Objective (operator task, 2026-10-20): make a run cheaper, stop it looping, and put the
operators' retro insights into the retro doctrine; release it. Branch `feat/diet-1020`.

- **Done.** A: stage 0's triage decides the short path (`scripts/short_path.py`), the
  example's gates are `auto`. B: entry reads `SKILL.md` only, the rest loads per stage or
  on named triggers (`SKILL.md` → *What to read, and when*); the command is a pointer;
  descriptions 386/399/395 chars with the old trigger lists verbatim under `## Triggers`.
  C: `graph.py certify` tiers and rounds by risk, unchanged-input refusal, ceiling parks
  (exit 7); `waves.py finish --clean-rounds`; fix and review loops cap at three. D:
  `scripts/retro_budget.py`, the floor budget, Class and Cost per entry, `learned.md`
  rules 33 to 39, evidence-docs' retro doctrine a pointer; this repo's floor migrated
  (27 620 → 6 532 bytes, archive `docs/evidence/retro/2026-Q4.md`, hash-proved).
- **Decisions.** R3 owes two rounds (blind plus adversarial), not three; a flagship
  surface owes two with one adversarial; "small" is R1, at most five files, no contract,
  no user-facing change, no deploy; the budget is 12 000 bytes, rows 600, stamps 300;
  the validator's description checks read the description plus `## Triggers`.
- **Checks run.** `npm test` and `npm run test:all` locally (exit codes read directly);
  new suites `test/audit_regressions/diet_retro_budget.py`, `diet_proportional.py`.
- **Open.** The hub re-pin (ssheleg/sshlg-skills, B-154 closes there) is the hub's.
- **Integrated.** PR #135 squash-merged as `4e9a90a` after its CI round (validate, house
  audit, eight negative shards, strict conformance) and a local `npm run test:all` exit 0.
  The run stamp naming `4e9a90a` and the retro entry follow in their own PR.
- **Side effect to repeat.** An `rm -rf /tmp/*-copy` here ran while the session in
  `_worktrees/tp125-fix17` held the family scratch lock; its in-flight negative suite may
  report a spurious failure and should be re-run.
- **Next task.** After the stamp PR: the local annotated tag `v1.98.0` on `main`,
  `npm run test:all` on it, push, watch the release run, read the published package back
  (`npm view task-pipeline-skill version`).

## 1.97.0 source candidate — WebKit (Safari) first (2026-10-16)

Branch `docs/safari-first`, draft PR "1.97.0 — the look runs on WebKit first". REQ R11
of the 2026-10-16 family host-validation iteration. Ships the *Engine order — WebKit
(Safari) first* section of
[`references/browser.md`](../plugins/task-pipeline/skills/task-pipeline/references/browser.md),
the WebKit-first channel rule in `companion-skills.md`, aligned stages 5/6/8 and
`tdd.md`, [`DEC-0007`](DECISIONS.md), guard `P3-G0d` with negative plant 463. No tag,
publication or install readback; no WebKit page was opened (the flag was read from each
tool's `--help`). Exact next task: independent review of the draft PR, then normal
integration and the release gate; the umbrella pin stays with the iteration owner.

## 1.96.0 source candidate — the finish line (2026-10-15)

Branch `feat/finish-line`, draft PR "1.96.0 — a finish line: iterations stop when the
work is done, not when the search runs dry". Ships
[`references/finish-line.md`](../plugins/task-pipeline/skills/task-pipeline/references/finish-line.md),
`waves.py finish`, the brief's `## Finish line`, `run.finish` budgets and guards FL-G1..G7
with eight negative plants (455–462). No tag, publication or install readback. Exact next task:
independent review of the draft PR, then normal integration and the release gate.

## Operator stop: Claude continuation — FW07 child lifetime

The operator requested a handoff, not another wave. Start with the
[child-lock continuation packet](evidence/runs/2026-10-13-fw07-child-lock/README.md#claude-continuation-after-operator-stop).
Implementation25fb09d is pushed and focused-tested, with independent review and
canonical owner ports still pending. The existing complete gate on older875c6e6
continues under its owned watchdog; its partial checkpoint, exact process/source
identity, log and final-result paths are preserved in that packet. Inspect it
before starting any suite. No new full run or PR promotion is authorized by this
handoff itself; continue under the operator's resumed instruction and existing
repository policy. Do not unlink the permanent family scratch lock.

## FW07 R07 runner cleanup correction — composed, complete gate pending

[Packet and source-bound checks](evidence/runs/2026-10-13-fw07-copy-cleanup/README.md)
reproduce secondary-copy residue on the future 1.95.0 candidate and retire all
admitted literal plant copies while preserving the first-copy verdict. The active
1.94.1 clone and its public scratch directories were not touched. Independent
parser/cleanup review accepted the bounded correction; all declared destinations
are distinct, including secondary copies. The correction is now composed in PR127.
Next: the complete owner gate in the serial slot. Focused checks are not aggregate
or release acceptance.

## Current FW07 source candidate —1.95.0

[Draft integration PR127](https://github.com/ssheleg/task-pipeline/pull/127)
replaces PR123/PR124 only after accepted merge; both remain open meanwhile.

[Composition entry](evidence/runs/2026-10-13-fw07-composition/README.md) binds
stage routes, checkpoint recovery, independently reviewed owner helper and shared
scratch lock. Metadata names the next minor; no tag or publication. The prior
1.94.1 release clone remains untouched. Exact next task: source/metadata review,
then moved public plants and complete owner validation in the coordinator's serial
slot, normal genuine-check integration, and local-tag-aware accepted-source gate.
Native/model/token-quality results remain NOT_RUN. Original PR heads are preserved;
older isolated-candidate handoffs below describe their historical source cuts.

## FW07 checkpoint correction — isolated source slice

The [frozen packet and receipt](evidence/runs/2026-10-13-fw07-checkpoint-profile/README.md)
reproduces default-stage injection into a custom-profile checkpoint. Implementation
and actual CLI controls are isolated from stage-extraction PR123 and from the pending
release gate. Next: independent source review, then composed owner validation in the
coordinator's serial slot, genuine candidate checks and normal integration. No tag,
live Observatory exchange, native loading, task-quality or billing claim is made.

## Release repair candidate — v1.94.1 (2026-10-13)

The immutable v1.94.0 tag reached accepted main but its release failed the
missing-retrospective-declaration guard; publication was skipped. This patch
records both unstamped versions and synchronizes metadata without changing the
accepted skill payload. The earlier candidate notes below are historical.

[Repair packet](evidence/runs/2026-10-13-release-1941/README.md) owns current
source, checks, unpublished local-tag handling and the exact next task. Independent
audit, safe-disk full validation on the accepted local tag, normal integration and
release/readback remain separate gates. No completed stage-10 stamp is claimed.

## FW07 stage-3 prerequisite follow-up — 2026-10-13

The split stage-3 procedure and spec subject reference now follow the accepted
artifact-provider contract. Equivalent providers/inline fallback remain valid;
missing or invalid scenarios still refuse and unavailable lint stays NOT_RUN.
[Source correction and evidence](evidence/runs/2026-10-13-fw07-stage-split/README.md)
preserve the earlier lossless extraction claim at its original source.
Next: independent review, correct both evaluation arms identically, then public
plants and composed aggregate after release repair reconciliation and slot grant.

## FW07 stage split — current isolated implementation

Entry: [execution receipt](evidence/runs/2026-10-13-fw07-stage-split/README.md).
The independently accepted prerequisite correction is followed by lossless
stage extraction, explicit default entry/resume routes, consumer migration and
source controls. B-043 remains open. No version, release, native host or billed
usage result is claimed.

Structural validation passes. Exact next task: public-entry refusal, independent review,
then the moved negative corpus and composed owner aggregate in the serialized slot.
Keep every full gate and the selected custom profile's precedence intact. The
receipt preserves failed intermediate checks and names all validation not run.

## Prior prerequisite handoff

## FW07 prerequisite correction in progress

[Execution receipt](evidence/runs/2026-10-13-fw07-prerequisites/README.md) binds the
separate semantic correction to the accepted artifact-provider decision. Seven
shipped source homes now agree; focused9 + actual mutation18 + house19/0 pass.
The original structural failure is retained; corrected structural passes. Independent
review precedes extraction. No stages.md bytes or default gate types changed.

Exact next task: freeze this bounded correction after review, then implement the
accepted B-043 gate-spine and deterministic per-stage routes on this isolated branch.
The coordinator permits source work alongside the separate immutable release gate;
no overlapping full suite or publication is authorized by this handoff.

## Historical source feasibility handoff

## FW07 / B-043 source feasibility — 2026-10-13

Entry: [decision-input report](reports/2026-10-13-fw07-stage-reading-floor/README.md),
then [bounded execution packet](evidence/plans/2026-10-13-fw07-stage-reading-floor.md).
Frozen source: accepted 1.94.0 `4d750573ce53ea4c7ffa2bde192ee35b59acefa7`.
This branch changes only the report, its reproducible raw census, this handoff and
the packet. No shipped doctrine, gate, test, profile or workflow was edited.

Measured stages.md: 17,616 cl100k tokens/967 lines; literal-address census 327 lines
in 108 files, including historical evidence. Conservative entry model 11,258 before
new routing overhead is feasibility only, not observed host or billing savings.
The plan freezes conservation, exact on-entry/resume routes, custom-profile scope,
consumer migration, negative controls and portable install/read-accounting limits.

Parent accepted the bounded extraction packet and the separately recovered
[UX prerequisite correction](evidence/plans/2026-10-13-fw07-ux-prerequisite-correction.md).
Exact next task after current release completion: normalize the stale package
prerequisites across the packet's eight current source locations in a separate commit with actual negative controls, then freeze the
paragraph migration map on a new implementation branch. B-043 is still open; no runtime/model
quality or full-suite verdict is claimed by this planning slice.
## Owner-only release candidate implementation — 2026-10-13

[FW07 source and focused receipt](evidence/runs/2026-10-13-fw07-release-candidate/README.md)
implements the reviewed standalone-clone prepare/check/publish design and reconciles
the owner stage-7 ordering. Private exact-source evidence grants no authority;
publication requires faithful actual run context and the existing hook.
Next: independent source review and correction, then serialized owner aggregate.
No production tag, full gate or release claimed; v1.94.1 repair remains separate.

## Source-only release admission follow-up — 2026-10-13

[FW07 pre-tag packet](evidence/plans/2026-10-13-pretag-admission/README.md)
recovers the failed v1.94.0 admission and the stage-7/R-010 ordering conflict.
It proposes an exact local-tag-aware complete-suite receipt and distinct local
preparation versus publication, without modifying the v1.94.1 repair.
Next: independent packet review before implementation. No gate or tag changed.

## Release candidate — v1.94.0 (2026-10-13)

Five version surfaces now name v1.94.0 for the accepted release-iteration feature
and its independent fixes. This is a release candidate, not a publication claim.
Published release remains v1.93.3 until an exact-SHA release run and npm payload
readback prove otherwise. R30 owner gates merged through PR120 at9fb9cfb after genuine candidate checks.
The final feature PR112 still governs main integration.

Next: review this metadata diff, integrate via the feature branch, run the required
checks on PR112's final head, then tag the normally merged source. Verify annotated
tag, every release job, npm payload and installed copies before closing the hub pins.
Historical verification rows below retain their original observations.

# Start here — task-pipeline

## Current source state — 2026-10-13

Published release remains **v1.93.3**. The accepted feature branch is
[`feat/release-iteration` at its PR119 merge](https://github.com/ssheleg/task-pipeline/commit/3596355ae56bd067a243bd5d17a8d40aeec292a0).
PR114 and PR115–119 are merged into that feature; PR112 is the pending route to
`main`. No new version or publication is claimed for these changes.
[Verification](evidence/verification.md) · [board](evidence/backlog.md) · [CHANGELOG](../CHANGELOG.md).

The accumulated implementation contains the release-iteration loop, risk-based
certification rounds, lossless lesson index operations, wave planning and graph
synchronization, run-scoped memory-unavailable markers and complete plain-skill
installers. The later corrections preserve graph state on refusals, require a
supported locking backend, record watched waits without inventing an executor,
and provide a release-authority source locator without treating it as a grant.
The body headroom change relocates existing obligations to an explicit stage-0
reference; it does not remove them.

PR119's initial hosted run failed the graph-conditional reference invariant.
The corrected exact candidate passed all jobs, including all eight negative
shards, in the [source-bound receipt](evidence/runs/2026-10-13-feature-integration.json).
Its earlier [local full gate](evidence/runs/2026-10-13-l3-graph-waits-full.json)
remains bound to that earlier source; it is not a new full run at the merge SHA.
The [R07–R16 map](evidence/runs/2026-10-13-r07-r16-acceptance.md) records remaining
live-service and consumer-migration limits. Checkpoint/handoff fixtures are not
a live Observatory exchange. Legacy packet reads remain because the named
consumer still has legacy packets; a Fabric format rename is not assumed.

**Exact next task:** integrate the separately reviewed R30 owner-validator
correction, freeze the accumulated release candidate, run its required local and
hosted gates, and merge PR112 normally. Then version, publish, verify the registry
payload and update the hub pin and installations with source readback. Keep
publication, native discovery and model task quality as separate acceptance.
The lessons directory ownership remains in hub B-181 and `state-json.md`.

## Historical release notes

The sections below preserve observations at their stated releases. Their
then-pending next actions do not override the current task above. Historical
verification rows are not silently re-stamped from newer test results.

## v1.93.3 (shipped, #113), a patch to wave 2

Findings from a re-certification reading of v1.93.2 and an independent observer
(CHANGELOG `v1.93.3`, verification section *Shipped state — v1.93.3*):

- The seven wave-2 commit references that a clone cannot follow are backticked again and
  declared in `docs/evidence/retro.md` (`docgate:known-dead`, reason and
  `git fetch origin pull/109/head` beside it).
- `stage_checkpoint.py handoff` keys a retry on memory events only, so a `gate:` line no
  longer turns a retry into a replacing offer.
- R13 gained `scripts/backlog_sources.py` + `test/backlog_sources_test.py`; R16 gained
  `test/release_approval_test.py`. CI's validate job now also runs these two and
  `memory_nudge_test.py`, which was in `npm test` but not in CI.

**Done:** #113 merged and the `v1.93.3` tag points at its merge commit `52fa75d`. Left from it: the hub re-pins 1.93.3 instead of 1.93.2 in wave 5.

## Wave 2 (shipped as v1.93.2; its branch is deleted, its commits are under `pull/109/head`)

Driven by the sshlg-skills waves run: plan
[`docs/evidence/plans/2026-10-11-integration-waves.md`](https://github.com/ssheleg/sshlg-skills/blob/waves/2026-10-11-integration/docs/evidence/plans/2026-10-11-integration-waves.md)
(Wave 2, R07–R16).

At its original pre-release cut, wave 2 was versioned **1.93.0** and its
verification rows were recorded at `never`. That was a candidate observation:
v1.93.0 and v1.93.1 published nothing; the payload subsequently shipped as
v1.93.2, as stated in this section heading and CHANGELOG.

- **R07 test temp residue.** `tp-b80` (`test/validate.py`), `tp-stage-ckpt` and 15 files
  with bare `mkdtemp` clean up after themselves. A validator check now refuses a test
  file that makes temp state with no cleanup (plant `test/negatives/453-…`); writing it
  found and fixed two leaks in `test/validate.py` itself.
- **R08 / HK-05 / #91.** The 433 negative self-tests and 15 property checks are files
  in `test/negatives/` (the hub plan said `test/negatives.json`; each check is a shell
  script, so it ships as a directory, every file byte-checked against the YAML-parsed
  `run` value it came from); `validate.yml` went from 507,836 to 12,181 bytes; the `negatives`
  job runs `test/negatives.py --shard N/8` on an eight-value matrix. All eight shards
  passed locally on `941bed8`, pre-squash (438 plants rejected, 15 property checks printed, none
  dormant). On CI the eight shards took 3m29s–6m45s (row `R08-ci`), and B-100 is
  closed.
- **R09 budget.** Description 909 → 890 chars; body 4736 → 4646 of 4750 tokens. B-120
  closed with the auditor's reading.
- **R10 ledgers.** The verification headers read "released"; the merged branches
  `feat/wave-mode` and `fix/no-stamp-1912` are deleted.
- **R11** Observatory checkpoint/handoff and the memory nudge · **R13**
  `backlog-sources.json` · **R14** namespaced packet id · **R15** Fabric contract
  fixture · **R16** release approval mode.

PR [#109](https://github.com/ssheleg/task-pipeline/pull/109): run `38242485458` green —
the slowest shard 6m45s and the whole run 6m50s, where the one job had taken 90–111 min.
Verification row `R08-ci` holds the numbers. B-100 is closed with them.

The hub (ssheleg/sshlg-skills) re-pins task-pipeline in wave 5, which closes B-160. The family rows B-154 and HK-05 live in the
sshlg-skills board and close there, at the wave-5 re-pin.

The previous page (the 2026-09-07 Sherlock audit branch) is history:
[that revision](https://github.com/ssheleg/task-pipeline/blob/aea2e14561b3ed3a20ce05fcfa7c08e7b9ae74ab/docs/HANDOFF.md).
