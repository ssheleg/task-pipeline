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
