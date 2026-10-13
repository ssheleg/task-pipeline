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
No broad local-tag exemption is added. The narrow shipped-hook correction below
is required for the exact object-to-tag destination used by publication.

The stage-7 owner `pipeline.json` wording now distinguishes local preparation from
publication and follows R-010: tag visible first, complete check, inspected unlooked,
then only the same candidate may push. The owner config and helper are excluded from the package files list. The later
peer correction changes the packaged hook; a future composed release must version
and verify that payload. This branch does not widen the v1.94.1 repair.

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

## Independent findings and correction

The first implementation's fixture used a guessed package name and reproduced it
in admission. Root review found the actual owner is `task-pipeline-skill`.
[The archived-source reproduction](owner-identity-baseline.json) confirms the old
helper refused the actual owner manifest. The corrected fixture now imports the
canonical package manifest rather than inventing its name/scripts; this observation
supersedes the initial source acceptance assumption, not the historical test output.

Other reviewed corrections:

- Private namespace directories and receipt/log files require this user's ownership,
  regular type and no group/other access. Unsafe existing paths refuse without
  silently changing their mode or adopting them.
- Executing helper bytes must equal the tracked candidate helper. The candidate
  source is clean and includes that file; an external different helper refuses.
- Publish uses the bound annotation OBJECT as its refspec source, then reads the
  remote tag object and peeled commit before reporting PUBLISHED. Local alias
  replacement at the last call cannot substitute a different object. Missing or
  ambiguous readback stays unconfirmed and does not trigger a second push.
- The existing hook now recognizes a refspec whose destination is `refs/tags/`.
  This permits faithful evaluation of the exact object-to-tag command. It still
  blocks that actual command under a failed ledger, preserves named-tag behavior,
  and leaves a branch destination outside its tag classifier.
- Actual context directories cannot alias a foreign ledger, and a changed remote
  default branch invalidates the prepared identity.

[Final focused47 controls](focused47.txt) pass, as do all [existing hook65 controls](existing-hook65.txt).
The first new context-alias fixture failed its expected diagnostic because Git
already refused its untracked symlink as dirty source. That [failed test output](fixture-expectation-failure.txt)
is retained. The corrected control explicitly ignores the alias in the fixture's
local Git excludes, then observes the intended context-kind refusal. No production
guard was weakened to accommodate the expectation.

[Packaged-source change identity](packaged-change.json) records the hook delta.
This is source-level review evidence only; the final implementation still needs
independent acceptance and the full serialized owner gate. No real tag was created,
changed or pushed by these tests, and no v1.94.1 repair source was edited.

## Effective destination correction

A second independent probe found an actual unintended write at abf3dff:
`remote.origin.pushurl` pointed at another owned bare repository. The helper checked
fetch origin but pushed to the alternate remote, then correctly reported unconfirmed
readback too late to prevent that mutation. The [exact-source probe](pushurl-peer-probe.py)
and [baseline result](pushurl-peer-baseline.json) preserve the failure; all those
remote repositories were disposable local fixtures.

The helper now requires one identical effective fetch/push URL, checks that its
literal use will not undergo another rewrite, and uses the bound URL for default
branch/tag checks, push and readback. Multiple push destinations and matching
push-only prefixes refuse. It reads Git configuration and never changes it.
Git documents that `pushInsteadOf` rewrites push destinations and that an explicit
remote pushurl masks that setting for the named remote; this is why checking only
the named remote is insufficient when switching to a literal URL.
[Git configuration reference](https://git-scm.com/docs/git-config#Documentation/git-config.txt-urlltbasegtpushInsteadOf)

An attempted command-scoped temporary remote probe failed with `No such remote` on
the local Git and is retained in [the first correction output](destination-first-failure.txt).
The correction uses Git's literal fetch URL expansion and reads matching push-only
prefixes conservatively. [Final52 controls](destination52.txt) pass, including alternate
pushurl, multiple pushurl, pushInsteadOf, explicit-pushurl-masked rewrite, and a late
pushurl change that cannot redirect the already bound literal destination.
No claim of resistance to an adversarial process modifying Git configuration during
an operation is made. No real repository tag or configuration was changed by tests.
