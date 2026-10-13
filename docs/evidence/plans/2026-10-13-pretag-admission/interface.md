# Proposed owner-only interface — review before implementation

This addendum narrows the [source packet](README.md) after coordinator review.
No executable exists yet and none of the controls below is reported as run.
The helper is proposed at `scripts/release_candidate.py`, excluded from the npm
payload: it serves this repository's release, not a new public plugin API.

## Operations and identity

- `prepare --tag vX.Y.Z`: discover the owner repository from the current directory,
  resolve its Git directory/common directory, require a standalone full clone and
  clean HEAD, resolve the actual default branch of the configured authorized origin,
  fetch it and published tags, verify version and accepted reachability, and prepare
  the one owned annotated local tag. No force and no remote mutation. An existing
  unowned or remote tag refuses, even when its peel happens to match.
- `check --tag vX.Y.Z`: load that same preparation record, recheck source/tag identity,
  and execute exactly `npm run test:all` in the owner root. No `--command`, `--skip`,
  `--allow-unlooked`, subset mode or external success receipt. Return the actual
  failure on nonzero/interruption/disk stop. A successful receipt additionally
  records that the release-gap check looked; missing Git/tags disclosure refuses
  admission. Other named unlooked disclosures remain explicit for review rather
  than being silently erased or universally waived.
- `publish --tag vX.Y.Z`: revalidate the preparation and successful check receipt,
  unchanged source/tag/suite definition and complete log digest; verify current
  remote absence and default reachability. Evaluate the existing release authority
  and gate, then push only `refs/tags/vX.Y.Z:refs/tags/vX.Y.Z`. No all-tags, forced
  update, deletion, automatic version replacement, release creation or npm call.

A clean check result admits only the exact annotation object and peel tested.
Ordinary source edits, normal squash/merge to a new commit, candidate replacement,
or suite-definition drift invalidate it. A failed version is never repaired by
moving its published tag. Metadata repair selects a new version through the normal
reviewed source change; the helper does not choose one.

Use a private task-owned namespace under the standalone Git directory, for example
`sshlg-release-candidates/<tag>/`. Preparation, suite output and structured outcomes
live there with restrictive permissions, not in tracked source or a caller-selected
path. Reject symlink/nonregular receipt and log files before reading; bounded JSON
shape and streaming log digest avoid accidental unbounded memory use. An exclusive
local operation lock prevents this helper's cooperating invocations from mutating
the same candidate concurrently. This does not claim protection against a hostile
local process or an atomic transaction across local Git and the remote server.

A preparation record names schema, repository origin/default branch, Git directory,
HEAD/tree, tag name/object/peel, owner nonce, package version and relevant suite
source identity. A check result adds its exact preparation identity, fixed command,
start/end, exit/interruption disposition, complete output digest and unlooked
observations. Write pending/failure evidence before work and final outcomes by a
same-directory atomic replacement; incomplete results cannot be interpreted as pass.
The final push uses Git's ordinary remote refusal when the tag appears concurrently.
A timeout/unknown push outcome triggers read-only remote reconciliation, never a
blind second mutation or deletion.

## Existing authority and hook remain

The helper adds no operator gate and grants no authority. The standing release
instruction and the owner's actual run context remain the authority sources.
Local preparation must be admissible under the existing stage context. Do not edit
`release-gate.sh` to exempt all `git tag` commands and do not fabricate a passing
ledger to make preparation proceed.

A nested subprocess is not automatically observed by a native PreToolUse hook.
Therefore the proposed implementation must explicitly evaluate the **existing**
owner `release-gate.sh` against the exact outward Git command before publishing,
using the original project root and actual run ledger, and preserve its exit/output.
It must not reimplement a weaker imitation of that policy. A hook skip because no
run exists is not evidence of operator authority. The wrapper must disclose that
boundary; its receipt cannot claim native interception. The coordinator must review
this explicit policy reuse before code is written. If it cannot preserve the current
policy without broadening scope, keep publication as a refused operation until a
narrow design is agreed rather than silently bypassing the hook.

## Initial test boundary

[First controls](first-controls.json) are frozen before implementation. The fixture
repository has a real bare origin, default branch, accepted commit and annotated
candidate; process execution is replaced only at the test seam for the expensive
suite. Tests must inspect actual remote refs and preserved local bytes, not merely
compare an implementation's returned status string. Production has no caller option
to swap the fixed command. At least one controlled fake suite writes a marker that
proves the candidate annotation was visible while it ran; a branch-only green result
must never satisfy the tagged contract.

Before a complete production gate, run the focused refusal corpus, independent
source review and a fixture happy path. No production tag push occurs in this test
wave. Broad owner validation remains serialized. Exact production full-suite and
release workflow/npm acceptance are subsequent distinct observations.
