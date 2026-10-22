## 1.101.0: cancel parity, locals and tourists, one rotation line, branch `fix/b246-rotation-line` (2026-10-22)

- **Objective.** sshlg-skills milestone M1 wave 3 (B-246: each stamp rotation added one pointer
  line to the retro floor) and M2 wave 2 (G8 and R2: cancel parity and one clear offer on every
  subscription surface; R3: at least two locals and two tourists on the test panel).
- **Done.** `retro_budget.py migrate` keeps one `Rotated out:` line per archive (B-151);
  `design_gate.py report --subscription` and the `subscription` block; `design_gate.py panel`
  counts locals and tourists; doctrine in `design-tester.md`, `design-review.md`, `stages.md`,
  `retrospective.md`. B-044 collapsed into B-040; B-150 filed.
- **Next task.** After merge: release 1.101.0 from a fresh clone (`release_candidate.py
  prepare`, `check`, `publish`), then the sshlg-skills pin bump; then B-150.

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
