# Negative-runner lock namespace follow-up

Source: composed runner at [01b1928](https://github.com/ssheleg/task-pipeline/commit/01b1928e17c4b888d2f93f139425209dcf90388d),
`test/negatives.py:248`; the accepted1.94.1 runner has the same lock expression.
The active release worktree/source is untouched. This is a source-first finding
and proposed correction packet, not a claim that concurrent suites collided.

## Reproduced defect

The runner binds its flock to `tempfile.gettempdir()/tp-negatives.lock`, which
changes with TMPDIR. Plants retain fixed `/tmp/` scratch locations, for example
`test/negatives/001-a-board-id-naming-two-rows-must-fail.sh:4` writes
`/tmp/dupid-copy`. Thus process-specific TMPDIR does not identify the resource
being locked, despite the runner comment's unconditional serialization claim.

`python3 -B docs/evidence/plans/2026-10-13-negative-lock-namespace/probe.py`
extracts only the exact observed assignment, evaluates it in two child environments,
and exercises two owned lock paths. [Baseline](baseline.json): different TMPDIR
locks both admit an exclusive holder; a contender for the same lock refuses.
The source scan finds431 files containing both `/tmp/` and `-copy` literals;
that lexical count is not proof of431 distinct execution destinations. No suite,
plant, real `tp-negatives.lock` or shared scratch directory is executed/touched.

## Bounded next implementation

Bind the suite lock to the fixed scratch namespace independently of TMPDIR,
working directory and checkout. Preserve plant text, source-attribution behavior,
worker count and whole-suite locking lifetime. Do not mechanically rewrite shell
payload paths: existing plants also mutate/reference those paths as test input.
The implementation may expose a pure lock-path helper for offline controls,
while actual production lock acquisition must use that same path without a CLI
bypass. An unavailable flock platform retains an explicit no-guarantee outcome.

Acceptance, frozen before code:

1. Different TMPDIR and checkout roots yield the same lock identity for the same
   fixed scratch namespace; relative cwd cannot alter it.
2. In owned fixtures, a second process cannot enter while the first holds that
   identity, then can enter after release. Process exit releases the lock.
3. No plant bytes, selector semantics or validator invocation changes.
4. Symlink alias `/tmp` versus its physical path must not create distinct locks
   on the current platform; portability limits must be explicit.
5. Invalid/unavailable lock admission must not continue an apparently serialized
   suite silently; positive healthy acquisition remains usable.
6. Focused controls first, independent source review, then one serialized owner
   aggregate. No concurrent public plants are needed to prove the lock repair.

Check the existing negative-runner regression homes and shared-mechanism contract
before adding code. Keep this repair separate from the already frozen FW07
composition until reviewed. No release tag or production pin changes in this packet.

## Shared-owner namespace decision

[Current fetched-main census](owner-census.json) binds TP540679, SEO1e86edf
and sheleg-dev21e0c53. Literal `cp -R . /tmp/...` destinations overlap across all
three owner pairs: anchor/card/corrupt/count-copy (SEO/TP), drift/stray-copy
(SEO/dev), and desc-copy (dev/TP). Counts445/32/48 are distinct literal targets
in the scanned canonical workflow/plant homes, not executed operations.
An initial scan used stale local remote refs; it was superseded by fetch+this
source-bound census before choosing the design.

Therefore retaining three owner-specific lock filenames is insufficient. Use one
shared `sshlg-family-negatives.lock` under the physical `/tmp` directory, resolved
independently of TMPDIR, cwd, checkout and owner. Add the same pure path helper to
all three runner copies; no new divergent module-level constants. Keep the
existing exclusive whole-suite lock acquisition/release lifetime. The spelling
of the owner/test source does not select a separate lock namespace.

Focused fixtures evaluate the actual pure helper under different TMPDIR/cwd
contexts, then substitute only an owned physical scratch root to exercise the
actual flock block in child processes. They never acquire the live family lock
or create/remove a public plant. Same-holder refusal and post-release success,
exit release and unreadable/invalid path refusal must be observed.

Prepare source-addressed owner port packets for SEO and sheleg-dev with the
identical mechanism delta and each owner's local tests before integration. The
coordination rule remains necessary during migration: old binaries using old
lock names do not participate in the new lock. This does not claim safety for
unmigrated runners or direct manual plant invocation outside the runner.
