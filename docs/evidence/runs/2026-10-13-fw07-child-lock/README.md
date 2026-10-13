# FW07 shared scratch lock: writing-child lifetime

Source `875c6e6a9a02c5c18e77945fc4fa56a43588cb5c`. Independent observer
[IO09](https://github.com/ssheleg/sshlg-skills/blob/868c9d7b3bade59ab834abaeb0110d50fd948365/docs/reports/2026-10-13-independent-observer-runtime-3898236/README.md#io-09-shared-scratch-lock-ends-before-orphan-plant-writers)
found that killing the parent releases its flock while its writing child lives.
[Actual replay](baseline.json), from the [portable original probe](baseline-probe.py),
confirms contender admission before the old child's write. Owned namespace only.
The original 30 controls cover parent lifetime; they do not cover this case.

## Frozen correction contract

The shared helper will pass the held descriptor into each plant Bash process and
retain it through ordinary exec into the corpus's synchronous writing commands.
The runner will own a separate process group for each Bash, stop admitting work
on interruption/failure and cancel/drain its owned groups before cleanup. Closing
a parent's descriptor never calls flock LOCK_UN, which would unlock descendants'
shared open-file description. The physical public lock is never unlinked/stolen.

The current TP corpus's shell/Python plant payloads do not invoke subprocess.Popen,
os.fork, nohup, setsid or background `&` commands. They run synchronous commands;
Python validator helpers can close descriptors when starting subprocesses, but
those helpers operate on their own temporary fixtures while the validator/Bash
ancestor remains. This bounded contract is not arbitrary-daemon containment.
A descendant that deliberately closes the lock and detaches is unsupported; any
new current-corpus example needs explicit admission and a lifetime control, not a
blanket all-descendant claim. No installed runtime code or release tag changes.

## Required controls before peer acceptance

1. Retain the existing 30 ownership/permission/namespace controls.
2. Actual owned runner parent SIGKILL: a live writing child excludes a contender
   until its final write and exit; preserve same-inode identity.
3. Actual Bash SIGKILL with a synchronous Python writing child: the child retains
   exclusion through its final write and exit.
4. Normal completion and SIGINT/SIGTERM cancellation drain owned groups and allow
   a subsequent runner; pending tasks cannot launch after cancellation.
5. Spawn/communicate exceptions cancel existing children, retain lock until drain,
   and never sweep a still-writing subtree as successful cleanup.
6. Current source helpers stay byte-identical across TP/SEO/dev after independent
   canonical peer review. Owner adapters and fixture-path overrides remain local.

The current complete gate continues on immutable 875c6e6 in another checkout. Its
result cannot accept this correction. Freeze focused red/green evidence first,
then independent peer, canonical ports, and a new composed gate in the serial slot.


## Implementation and observed checks

The common helper now owns the runner's process lifecycle: an inherited lock
file descriptor, separate groups for each Bash, cancellation before any new
admission and TERM/KILL drain before worker cleanup. Signals are recorded instead
of raising inside Popen before a child handle can be registered; result checks
refuse interruption. The parent closes its reference without LOCK_UN. Actual
Bash death is covered by the synchronous writing Python child retaining the fd.
[Corpus census](source-census.json) records the bounded lexical spawn inventory;
it is not a general shell parser or an arbitrary-descendant guarantee.

[Focused output](focused.json) records 30 existing lock controls, 42 runner
controls, 18 copy-cleanup tests and the earlier 44 child-lifetime controls, all exit 0.
[Final child controls](child-final.json) add actual INT/TERM cancellation while
waiting for another lock holder: 48 controls, exit 0.
The [new control on old source](new-control-red.json) fails at child descriptor
inheritance; its snapshot and writing processes are removed.
[Structural output](structural.json) records the separate validator result.

[Implementation failures](first-local-failure.json) preserve the first TERM
hang and the later exited-group signaling failure; neither is acceptance.
[Copy-fixture baseline](copy-fixture-first-failure.json) exposed its StringIO
lock fake lacking a real descriptor. It now uses an actual private owned lock and
injects the same post-child observation error at the lifecycle method. Its three
error assertions retain exact diagnostics and both-copy cleanup while expecting
the runner's explicit failure exit. The [remaining old exception expectation](focused-fixture-adapter-failure.json)
was preserved before that final assertion was corrected.

The earlier scratch-lock README's broad owned-namespace sentence was corrected:
six selectors in the historical 42-case run still acquired the public lock because
they patched TMPDIR, which the new helper deliberately ignores. Their prior logs
remain unchanged; `runner_test.py` now redirects the actual helper path before
replay. No public lock or public plant was used for this correction's focused tests.

Next: independent frozen-source peer review, byte-identical SEO/dev helper ports
and adapted runner lifecycle, then a fresh composed full gate after the active
875c6e6 pre-integration run completes. No release, native-host or final aggregate
acceptance is claimed here.


## Claude continuation after operator stop

The operator requested finishing this session and leaving context for Claude.
Implementation is frozen at `25fb09d1d7bfe59c9019584a581cb421718ba6c6` on
`fix/fw07-scratch-child-lifetime`, worktree
`/Users/sshlg/DATA/_wt/tp-fw07-child-lock`. The branch is pushed. It is a focused
candidate awaiting independent peer review; no whole-suite, merge or release
acceptance is claimed. The later handoff commit changes evidence/docs only.

**First next action:** inspect the already-running complete gate before launching
anything. [Active checkpoint](preintegration-active.json),
[owned driver](preintegration-driver.py) and [partial log](preintegration-partial.log.gz)
bind source 875c6e6, tree cc947755, start time, process, temporary directory and
absolute final-result/log paths. The driver continues separately, records the
final code/duration/hash/source/tag refs, removes only its own TMPDIR and stops its
own process group below 300 MiB free. Do not rerun this preserved driver: inspect
its current result first. Do not kill a process based only on an old PID or delete
the permanent public scratch lock. The current candidate checkout remains frozen.
This old-source pre-integration run cannot accept the new child-lifetime fix and
is never an accepted-commit local-tag release gate.

Then have an independent reader review immutable 25fb09d and replay the bounded
owned controls. The final child fixture48 passed; other focused source controls
30+42+18 passed and structural validation passed at the recorded source cut.
Historical failures remain in this packet. Review startup/cancellation/drain,
normal descriptor close versus LOCK_UN, actual parent/Bash death and helper
path overrides; do not infer arbitrary detached-descendant containment.

After correction acceptance, port the common helper bytes and lifecycle adapter
to SEO `/Users/sshlg/DATA/_wt/seo-fw07-scratch-lock` (branch
`fix/fw07-shared-scratch-lock`, policy packet78f2dd4) and sheleg-dev
`/Users/sshlg/DATA/_wt/sheleg-dev-fw07-scratch-lock` (same branch name, packet4678ef4).
Those two owner Git packets retain versions0.26.6/0.13.4 because all46/68 npm
payload files matched their base. No PR has been opened: owner policy requires
local gates first, and lifetime acceptance is held. Their original30-control
review remains historical and does not cover surviving children.

Compose the accepted correction into TP PR127 only after peer acceptance; preserve
PR123/PR124 and their historical receipts until normal integration. Coordinate a
fresh serial complete gate, then eligible frozen-candidate PR checks and normal
merge. No promotion, version/tag change or release was initiated at this stop.
The [performance source census](performance-source-census.json) is a future
measurement proposal only, not a time-saving result or permission to drop gates.
