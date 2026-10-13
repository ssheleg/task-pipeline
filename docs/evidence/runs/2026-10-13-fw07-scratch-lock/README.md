# FW07 shared scratch lock — bounded implementation

The [reviewed packet](../../plans/2026-10-13-negative-lock-namespace/README.md)
and its canonical three-owner census reproduce the TMPDIR mismatch and
cross-owner scratch overlaps. This separate branch changes only owner test code
and evidence. Active accepted1.94.1 release source/tag is untouched.

## Mechanism

`test/negative_lock.py` selects one lock below physical `/tmp`, independent of
TMPDIR, cwd or owner. Exclusive-create or no-follow nonblocking open admits only
a regular current-user file, mode600, one link and matching descriptor/path inode.
A held file never gets truncated, chmodded, unlinked or stolen. The descriptor
holds flock for the suite lifetime; ordinary close/process exit releases it.
A waiting acquisition rechecks the named inode after waking. Unsupported flock
or no-follow platforms refuse explicitly. Existing old versions and direct
manual plant execution do not join this lock; migration remains coordinated.
No hostile-process race immunity beyond these observed admission checks is claimed.

The runner consumes the helper and refuses before plants on failed lock admission.
[Scope receipt](source-scope.json) binds the helper, unchanged plant bytes and
excluded runtime scope. The same helper must be ported byte-identically to SEO
and sheleg-dev; their source-addressed packets are separate required work.

## Checks actually run

- `python3 -B test/audit_regressions/fw07_scratch_lock.py`: [30 controls](focused30.txt), exit0.
- `python3 -B test/runner_test.py`: [42 existing cases](runner42.txt), exit0.
- `git diff --check`: exit0 before source freeze.

Actual subprocesses with three owner labels/different TMPDIR/cwd contend on one
owned inode, wait, continue after release and retry after holder exit. Files retain
contents/modes; symlink, directory, FIFO, foreign-user identity (mocked UID), broad
mode, hardlink and replacement symlink refuse. The actual runner's unsafe-lock
refusal and healthy listing are exercised with only its namespace redirected to
an owned directory. No public plant or full suite was executed.

## Scope error preserved

An earlier `python3 -B test/negatives.py --list` invocation was mistakenly assumed
to be lock-free. It [listed439+15](public-list-observation.txt), exit0, but source
acquires the lock before listing. It briefly acquired the new public family lock
and left it present; the helper never truncates/writes/unlinks it. No scratch
plant ran. The coordinator was informed and the public lock was left untouched.
Subsequent runner probes redirect the lock into owned fixtures. That command is
not represented as an owned-namespace-only control.

## Next task

Independent exact-source review, identical helper/admission ports with each owner
fixture replay, then composed validation in the coordinator's serial slot. No
version, package, tag, hosted run or release acceptance is claimed by this slice.

## Independent canonical acceptance and portable listing assertion

[Root independent review](independent-peer-27b7e9.json) accepts exact27b7e9
source and replayed30+42 controls. Porting found the positive listing assertion
was needlessly TP-specific: sibling outputs have no property-check suffix. The
fixture now requires their common negative-self-test listing plus exit0; unsafe
lock refusal still requires exit1 and its actual admission diagnostic. The
[corrected canonical30 controls](focused30-portable.txt) pass. Helper code unchanged.
SEO/dev port receipts preserve their first assertion failures and source bindings.
