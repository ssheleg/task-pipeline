# FW07 owner release candidate — implementation review

Source contract: [frozen packet](../../plans/2026-10-13-pretag-admission/README.md),
[interface](../../plans/2026-10-13-pretag-admission/interface.md), and
[19 planned controls](../../plans/2026-10-13-pretag-admission/first-controls.json).
This branch is separate from the v1.94.1 metadata repair and has not published a tag.

## Implemented boundary

The owner-only `scripts/release_candidate.py` implements prepare/check/publish.
A standalone clone, full history, clean source, owner manifests/card/changelog,
accepted default-branch ancestry and remote tag absence are checked. Preparation
records ownership before creating its annotated local candidate; unowned existing
or published tags refuse without replacement. There is no force or delete path.

Private Git-directory records separate `mechanical_evidence`, `hook_observation`
and `external_authority=NOT_VERIFIED_BY_HELPER`. The fixed command is
`npm run test:all`; production has no command substitution or skip flag. Its exact
source/tree, helper/suite/hook identity, tag object/peel and complete log digest must
still match before an explicit single-ref push. Failure, interruption and uncertain
push outcome remain non-passing records; they do not trigger a blind retry.

`--context-root` is accepted only at preparation. It binds an actual same-origin,
same-commit clean project, its current Run header and profile digest. The helper
never copies or writes a ledger. A missing or changed context refuses publication;
prepare/check without context remain usable. The existing release-gate.sh executes
with that real context and exact outward command; its refusal is retained. A nested
subprocess is not claimed as native PreToolUse interception, and hook exit zero is
not an operator grant. Existing external authorization still governs the caller.
No broad local-tag exemption or change to the shipped hook was made.

The stage-7 owner `pipeline.json` wording now distinguishes local preparation from
publication and follows R-010: tag visible first, complete check, inspected unlooked,
then only the same candidate may push. This owner config and helper are excluded
from the package's `files` list; no version or packaged skill text changes here.

## Focused evidence and limits

`python3 -B test/audit_regressions/fw07_release_candidate.py` initially passed
[first25 controls](first-focused.txt), then [32 controls](focused32.txt), and final [34 controls](focused34.txt).
These use real disposable bare Git remotes, commits and refs, plus the existing
hook as an actual process. The expensive suite is substituted only at the Python
fixture seam. Positive controls inspect actual remote annotation objects; refusal
controls preserve foreign tags/receipt targets and inspect absence of remote writes.
Every fixture tree was removed by its context manager. Two final controls run an
actual owned suite child through SIGTERM and simulated low-disk handling and verify
that it exits; neither invokes the broad owner suite. Source review also aligned the
card fixture with the actual bold Version label before the final replay.

Coverage includes the 19 frozen scenarios, with additional missing/changed run
context, FIFO receipt, no structural verdict, retained prior-check evidence and
unknown CLI argument controls. A nested fixture's later unlooked disclosure is
retained without misclassifying it as the initial structural check: release-gap
admission examines disclosures before the first owner structural PASS. Missing that
PASS refuses admission, even with exit zero. This is command/source-bound output
admission, not a cryptographic proof against a hostile executable or local user.

Complete owner suite, final production tag gate, genuine candidate CI, independent
source acceptance, native host behavior and npm publication remain NOT_RUN. Existing
worktrees share unrelated candidate tags; do not interpret their release-gap failures
as a result for this standalone-clone design. Broad validation remains serialized.

Next: independent review of source identity, real run-context binding, hook reuse,
interrupt/push uncertainty and the 34-control corpus; fix any findings before one
composed owner aggregate and normal candidate integration. Published failed v1.94.0
and the separate v1.94.1 repair remain untouched.
