# L3 TP-2: watched waits in the work graph

Source baseline: `61871e6c35945596b236011ceadda5073f48ff25` (TP-6 stacked
on independently reviewed L3; TP-6 has not yet been independently accepted).
Owner: task-pipeline. Implementation worktree: `fix/l3-graph-waits`.
This packet records a design and measured counterexamples, not implementation.

## Required result

A queue containing only recorded external waits must not look like a human gate,
a runnable task or completion. A wait records `kind` and a concrete watcher or
durable-trigger locator. It neither proves the watcher is alive nor authorizes
its eventual action. Human-only actions and act-specific authority retain L3's
boundaries. No model or provider calls are needed for this packet.

Source request: TP-2 in the hub's
[principles gap table](https://github.com/ssheleg/sshlg-skills/blob/392e8f3787d37a32ca1ebc261addee3cdea6994e/docs/evidence/specs/2026-10-13-pipeline-principles-gaps.md).
Existing homes:
[graph.py](../../../plugins/task-pipeline/skills/task-pipeline/scripts/graph.py),
[graph.schema.json](../../../plugins/task-pipeline/skills/task-pipeline/graph.schema.json),
[work-graph.md](../../../plugins/task-pipeline/skills/task-pipeline/references/work-graph.md),
[continuity.md](../../../plugins/task-pipeline/skills/task-pipeline/references/continuity.md),
[waves.md](../../../plugins/task-pipeline/skills/task-pipeline/references/waves.md).

## Counterexamples measured before changes

Both probes used synthetic data and an owned temporary directory, removed at exit.
No real graph or project configuration was touched.

1. A otherwise-valid single node with `status: waiting` and
   `waiting_on: {kind: ci, watcher: synthetic-watch}` produces
   `violations=[]` and `frontier=['N-001']`. The schema currently lacks the status,
   while the live validator does not reject unknown status values. Merely adding
   the schema enum would leave this node runnable.
2. Place a directory at the synthetic graph's `.graph.lock`, then call the real
   `graph.py add` process. It exits **0**, emits `proceeding unlocked`, and changes
   the graph bytes. `held.__enter__` deliberately continues after lock-open or
   flock errors and when `fcntl` is missing. Reusing it is not evidence of safe
   serialization on those paths.

## Bounded implementation sequence

1. Add failure controls for lock refusal before any mutation. Make the shared
   mutation lock fail closed when locking is unavailable or fails; preserve the
   graph bytes and name the cause. The existing read-only verbs remain available.
   Unsupported platforms must be disclosed rather than silently treated as
   single-writer. Test real lock-path collision plus injected unavailable-lock
   and flock failure paths, and a valid-lock positive. This changes the existing
   warning-only compatibility behavior and must be explicit in review/docs.
2. Define the complete admitted status set, including `waiting`, in runtime
   validation and schema. A waiting node requires an object with closed `kind`
   (`ci`, `review`, `peer`, `release`, `time`, `lease`) and a nonblank single-line
   `watcher`. Non-waiting nodes must not carry a live `waiting_on` object. Reject
   malformed/unknown status instead of dispatching it.
3. Add locked, reasoned wait/resume transitions for pending or edge-blocked
   nodes without a recorded execution claim. Refuse running and terminal nodes;
   do not steal or cancel execution grants. Resume names the recorded watcher
   it is completing so a stale watcher cannot release a replaced wait. Preserve
   the prior wait in the revision record. No command in a watcher field is run.
4. Exclude waits from `frontier` and therefore `claim`. `next` returns **6** only
   when every unresolved dependency leaf for the requested scope is a recorded
   watched wait. Pending descendants may be held transitively, including across
   `--wave` boundaries. A running, parked prerequisite or other unclassified
   blocker keeps exit **4**; a runnable node still returns **0**. Existing
   terminal handling and exit **3** remain unchanged. Exit **5** already means
   lease contention for external-authority verbs and is not reused.
5. Audit transitions that invalidate, park, certify or close nodes: no stale
   `waiting_on` may survive a changed status, and certification/close cannot
   silently treat an unresolved wait as success. Preserve unrelated node bytes
   semantically and refuse before writing on all invalid requests. Document
   graph-local wait state separately from the external SQLite execution lease;
   this packet must not claim atomic coordination across those two stores.
6. Update the command/exit tables and remove L3's temporary statement that no
   distinct wait state exists. Keep stdout limited to runnable frontier rows;
   wait diagnostics belong on stderr. Check waves/continuity consumers and the
   existing graph/audit fixtures, then independent review before integration.

## Acceptance and negatives

- Real process: wait -> next(6, no runnable rows) -> matching resume -> next(0).
- Single wait, wait plus pending descendants, cross-wave held consumer, multiple
  waits, independent runnable sibling, mixed parked/running barrier, empty graph.
- Missing/blank/multiline/invalid watcher and kind; unknown status; stale metadata.
- Wrong watcher cannot resume a newer wait; terminal/running/claimed admission
  refuses with graph bytes unchanged. Missing node/reason also refuses.
- Park/invalidate/close/certify boundaries preserve a truthful wait history and
  never leave contradictory active metadata.
- Failed lock cannot write; two valid concurrent mutations retain both updates.
- Full graph fixtures and affected wave tests pass; schema and runtime agree on
  new shapes. A full owner gate is serialized with other agents, not duplicated.

## Integration and remaining boundary

Keep this branch separate from the frozen L3/TP-6 candidates. Parent independently
reviews the implementation and controls; normal eligible CI and exact-source local
gates precede merge. No tag, installation, external execution-authority wire change,
watcher-liveness guarantee or final original-goal completion is part of this packet.
