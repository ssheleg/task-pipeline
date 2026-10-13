# FW07 composed source after accepted 1.94.1

This is source integration and focused offline evidence, not release, native-host,
model-quality or billed-token acceptance. The [source map](source-map.json) binds
accepted main, both original candidate heads and both normal merge commits.
Original PR123 and PR124 heads remain unchanged.

## Composition

Accepted base [540679](https://github.com/ssheleg/task-pipeline/commit/540679ea7552f8a37e99560e287a69c23cbd3c4a)
retains version1.94.1. Stage source
[5316132](https://github.com/ssheleg/task-pipeline/commit/5316132edd8133dd8bd06eeb8b55f010355b04b9)
and checkpoint source
[cb4c9db](https://github.com/ssheleg/task-pipeline/commit/cb4c9db7e83909ad081dfe4cd0e5f9de6c8e8757)
were merged in that order. Only CHANGELOG and HANDOFF conflicted; both task contexts
and accepted repair history were retained. Source code merged without conflict.
Twenty exact byte comparisons bind manifests/profile/schema to accepted base,
stage instructions to the reviewed stage source, and checkpoint executable to
its reviewed source. The card retains accepted version1.94.1 plus the stage
prerequisite text, checked separately. Release helper is absent and the existing
release hook is byte-identical to accepted base. No version or tag was created.

## Focused results on composition4fa9ff1

- `python3 -B test/audit_regressions/fix-tp-02.01.py`: [10 controls](contract.txt), exit0.
- `python3 -B test/audit_regressions/fw07_prerequisites.py`: [30 actual mutation-entry controls](prereq.txt), exit0.
- `python3 -B test/audit_regressions/fw07_stage_routes.py`: [51 controls](routes.txt), exit0.
- `python3 -B test/audit_regressions/fw07_checkpoint_profile.py`: [162 actual CLI controls](checkpoint.txt), exit0.
- `python3 -B test/stage_checkpoint_test.py`: [72 existing cases](existing-checkpoint.txt), exit0.
- `python3 -B test/memory_nudge_test.py`: [40 existing cases](memory.txt), exit0.

No full suite or shared public-negative runner was started: the coordinator owns
the serial slot for immutable1.94.1 validation. Public moved plants, aggregate,
installer replay and genuine candidate CI remain pending on final composed source.

## Preserved intermediate failures

The first merge's staged diff check flagged trailing whitespace in raw historical
patch context lines. A shell separator allowed that merge commit despite the
nonzero check; it is not recorded as a passed check. The second merge stores that
patch as deterministic gzip and updates its link. Decompression exactly equals
the original5316132 blob; old source remains unchanged. Its staged diff check
passed. Historical967-line conservation belongs to the original extraction cut,
before the separately accepted semantic corrections.

The initial source-map assertion incorrectly expected the whole card to equal
accepted base; it failed on the intended prerequisite text. Corrected checks bind
version and stage text separately. No source was changed to make that assertion pass.

## Next task

Independent composition review, then rebind the matched monolith/split holdout
packet to this accepted-base composition with identical checkpoint and semantic
corrections in both arms. Retain old hashes as provenance. Once serial slot is
available run moved public plants and the owner aggregate. The separately reviewed
release helper must not enter this branch until its independent acceptance.
Choose the next coherent package version only after source freeze;1.94.1 remains
the accepted base and must not be republished with these changed instructions.

## Independent stage/checkpoint composition acceptance

[Peer receipt](independent-peer-01b1928.json) accepts exact01b1928 at source level:
20bindings, every nonconflicting merge path, retained old HANDOFF/CHANGELOG lines,
card composition and lossless gzip patch verified. Existing focused receipts were
read, not independently rerun. Full and native outcomes remain unobserved.

## Accepted helper composition and newly exposed startup seam

Normal merge10b9a4a adds helper source4612024 plus independent receipt95c8626.
Only HANDOFF conflicted; both contexts retained. The reviewed helper was unchanged
by that merge. Package metadata still1.94.1 pending future candidate version.

Its composed focused replay [failed](helper-first-failure.txt) at real interruption
cleanup. Source review found Popen preceding SIGTERM handler registration. A
[deterministic owned-child probe](early-term-baseline.json) delivers SIGTERM before
Popen returns: driver exits-15 and child survives. That exact child process group
was terminated explicitly. The first probe setup mistakenly constructed Candidate
in a linked worktree and produced no child marker; it is not baseline evidence.

The correction registers SIGTERM/SIGINT handlers before launch and records a flag
instead of raising during Popen. Once the process handle is acquired, normal
cleanup reaps the owned child and restores both previous handlers. Deterministic
early-term and early-int controls supplement the existing real interruption/disk
controls. This is bounded process cleanup evidence, not protection from SIGKILL
or every possible hostile race. Independent correction review remains required.

Corrected composed replay: `python3 -B test/audit_regressions/fw07_release_candidate.py`
passes [56 controls](helper56.txt), exit0. This supersedes only the failed helper
replay; no whole-owner gate is implied. The source correction is isolated in its
own commit after the normal helper merge.

## Final cleanup interruption correction

Independent review found a smaller late-flag window at bc2c0f8: a finished child's
second poll in final cleanup can receive TERM/INT after the earlier flag read.
The [portable peer probe](late-signal-peer.py) and [baseline](late-signal-peer-baseline.json)
show `(0,None)` for both signals. No real child or external operation is involved
in this controlled finished-handle probe. The helper now consumes the flag again
after cleanup/restoring handlers and before returning. The regression's exact
`late_signal_controls` function [passes2 cases](late-signal2.txt), including restored
handlers. The earlier56-case source run remains a separate historical verdict;
a complete58-case replay is not claimed by this focused delta.

## Final independent helper correction acceptance

The reviewer accepted exact9b3fa1a via an immutable four-blob Git snapshot:
[58 controls passed](helper-independent-final.json), exit0,114.48seconds, snapshot
removed. The [replay script](helper-independent-replay.py) retains that procedure.
Earlier [peer replay during source edits](helper-peer-source-churn.json) failed
source-identity binding and is explicitly contaminated, not a candidate failure
or success. The implementer changed the worktree after a correction request while
that replay was still running; immutable source extraction prevented recurrence.
No complete owner suite, native interception or production release is claimed.

## Standing release-order reconciliation

`pipeline.json` stage7 already names local annotation → complete tagged-tree
check → publication. CONTRIBUTING now gives the actual owner helper commands
in that order with conditional chaining and real context/authority boundaries.
R-010's operative sentence now says local tag first explicitly, matching its
existing explanation; historical incident prose remains unchanged. No new human
approval flow or native hook exemption is added. CONTRIBUTING is a published
document, so this change belongs to the future composed package version.

## Future1.95.0 source candidate

Fetched origin/main still names1.94.1; remote v1.95.0 is absent at preparation.
The coordinator accepted a new minor for changed stage/checkpoint behavior. Five
manifest/card/changelog surfaces now name1.95.0, with truthful NOT_SHIPPED ledger
and no-stamp declaration. No tag was created. Stage/checkpoint/helper/lock source
remains the reviewed composition; metadata preparation is not release acceptance.

The [pre-version structural run](structural-preversion-failure.txt) failed because
1.94.1 was already bound to a different local shared-repository tag, and a historical
source-map JSON key `version` was interpreted as another synchronized manifest.
The future version resolves the first issue. The receipt key now explicitly says
`accepted_base_version`, preserving1.94.1 as historical data without making that
receipt an artifact manifest. No validator or release-gap check was weakened.

[Candidate metadata binding](candidate-1950.json) records the new five surfaces.
`python3 -B test/validate.py` [passes](structural-1950.txt), exit0; its three
unlooked disclosures remain coordination, backlog citation anchoring and absent
umbrella routing observation. This is an untagged structural run, not the required
complete tagged-source release gate. Both actual strict manifest validations pass:
[marketplace](marketplace-1950.txt) and [plugin](plugin-1950.txt). All executable
source remains the reviewed composition; complete aggregate and release are pending.

## Draft integration entry

[Draft PR127](https://github.com/ssheleg/task-pipeline/pull/127) is the coherent
successor to PR123/PR124. [Creation readback](draft-pr127-created.json) records
OPEN/draft at0cb1044 with no check runs requested. The coordinator independently
accepted the final metadata delta; no tag or full-suite acceptance was inferred.
The original two PRs remain open and their heads are preserved until accepted
replacement merge. Full local gates and genuine eligible candidate checks precede
normal merge/promotion; this draft is for source review while the serial slot is held.

## Completed worktree cleanup

[Cleanup receipt](completed-worktree-cleanup.json) records five completed own
worktrees removed without force after exact remote-head, composed ancestry, clean
status and no-open-handle checks. Their ignored local records were archived under
the common Git directory with byte hashes verified before removal; branches and
tags remain. The current candidate and active release clone were preserved.
This maintenance operation does not add validation or release acceptance.

## Pre-integration owner gate on875c6e6: exit1, and most of it never ran

`npm run test:all` on exact875c6e6 (tree cc947755), started 13:50UTC, 2380.9s,
**exit1**: [result](preintegration-875c6e6.json), [log](preintegration-875c6e6.log.gz)
(gzip of the 57289-byte log, sha256 1d3fa5b4…, equal after decompression). Source,
tree, status and tag refs were unchanged after the run; the owned TMPDIR was removed.

Failure: `test/negatives.py` reported `0 guard(s) did not fire, 2 test(s) broken` —
plants 388 and 429 stopped with `PLANT OVERREACHED`. Cause: 23060e8 moved stage 3 and
stage 5 narrative into `stage-03-spec.md`/`stage-05-dev.md`; the validator reads it
there through `test/stage_routes.py::detail_text`, and plant 393 was migrated, but 388
and 429 still asserted the narrative inside the spine section, where only the GATE
bullet remains. Deterministic, not a scratch race: the same assertion fails on a
plain read of the composed `stages.md`.

`test:all` chains with `&&`, so **nothing after `negatives.py` ran**: test:certify,
exposure, probe, anchors, runner, hooks, artifacts, docs and audit-regressions are
NOT_RUN on this source. The suites before it passed (validate, graph171,
project_audit, packet_schema, browser_claims, visual_gate, stage_checkpoint72,
backlog_sources40, release_approval41, memory_nudge, lessons, waves, continuity_doc,
install_test). This result is no gate for any later source.

Correction: both plants now assert survival in the detail file the validator reads,
which the plant does not touch; the spine edit and the expected validator message
are unchanged. Both run green alone (exit0). The full owner gate must be rerun on
the next composed source (with the child-lifetime correction), serially.

### The nine suites that never ran, on a9e45af

Run from a clean clone at exact a9e45af (the plant correction) with an owned
TMPDIR, each suite separately so one failure cannot hide the next:
[summary](tail-a9e45af.txt) — certify (873s), exposure, probe, anchors, runner,
hooks, artifacts, docs and audit-regressions all exit0. This covers what875c6e6
left NOT_RUN; it is still not the full chained gate, which owes one run on the next
composed source. Observation, not a failure: the owned TMPDIR kept 37
`task-pipeline-test-*-graph` trees. `certify_mutations.py` runs `graph_test.py`
against mutants whose cases fail on purpose, and `test/residue.py` keeps a failing
case's tree as evidence; a mutation run therefore leaves one tree per killed case
in TMPDIR. Recorded for the backlog; not changed here.
