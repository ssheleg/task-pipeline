## Fix cycles 6–14 of the release iteration — #125, branch `iter1/M-5-N-1` (2026-10-15)

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

Next task: run round 16 of verification on #125's head. The release order after v1.95.0 is
the coordinator's.

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
