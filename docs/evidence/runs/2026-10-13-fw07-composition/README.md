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
