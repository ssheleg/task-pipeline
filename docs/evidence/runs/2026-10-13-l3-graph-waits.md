# L3 TP-2 watched graph waits

Status: implemented locally; independent review, owner aggregate and integration
remain pending. No publication, installed-host or original-goal completion claim.
The [frozen plan](../plans/2026-10-13-l3-graph-waits.md) is the context packet;
[the lock prerequisite](2026-10-13-l3-graph-lock.md) was independently accepted at
[d369942dfaa9d9c9c5fc5aca2a73cbdb433c8510](https://github.com/ssheleg/task-pipeline/commit/d369942dfaa9d9c9c5fc5aca2a73cbdb433c8510) before this implementation.

## Counterexamples and correction

On the lock-only baseline, three new real-process controls failed: a waiting node
was printed as runnable with exit 0; unknown status `mystery` was also runnable;
`wait` was not a recognized verb. Six existing lock controls passed. The source
fixtures are in `test/audit_regressions/l3_graph_waits.py`; the original local
run output was retained as `/tmp/tp2-wait-red.log`.

Waiting nodes now require a closed record containing generated identity, external
kind and nonblank single-line watcher locator. Runtime validation and JSON Schema
admit the same wait shapes. `wait` and `resume --wait-id` use the existing exclusive
read/modify/write lock; duplicate or stale resumes refuse without writing. A new
identity on each wait prevents an old event resolving a later wait even when both
use the same watcher locator. The locator is inert data and is never executed.

`next` excludes waits and returns 6 only when recorded waits hold all remaining
dependency leaves, following cross-wave dependencies. Runnable siblings still get
0; mixed running, parked or unclassified barriers get 4. Existing all-terminal
exit 3 is unchanged and includes deliberately parked nodes. Park and invalidation
archive prior wait records; close/certify refuse unresolved waits.

An additional real-process red control found `recover` bypassed the frontier and
created an execution grant for a waiting node, even without an existing authority
DB. Its output was retained in `/tmp/tp2-recover-red.log`. Recovery now validates
the graph and refuses an unresolved wait before opening the authority. `claim`
already refuses through the frontier. Four exact owned failure fixtures were
inspected and removed; their run logs remain, and no foreign temporary trees were
removed.

## Checks actually run

- `python3 -B test/audit_regressions/l3_graph_waits.py`: 15 cases PASS, 60 owned
  temporary trees created/removed. Covers lock failures/concurrency; runtime and
  actual JSON Schema malformed-wait controls; transition admission and byte
  preservation; cross-wave/mixed barriers; history; no claim/recover/certify/close;
  same-identity concurrent resumes with exactly one success.
- `python3 -B test/graph_test.py`: 171 cases PASS, 200 owned trees created/removed.
- `python3 -B test/continuity_doc_test.py`: 31 cases PASS.
- `python3 -B test/waves_test.py`: 85 cases PASS.
- `python3 -B test/validate.py`: exit 0 after synchronizing its admitted status
  enum; three existing unlooked coordination/citation/routing conditions retained.
  The preceding structural refusal of the old five-status enum was real, not
  counted as a pass.

The optional JSON Schema engine was present for this replay. Without it the
focused suite explicitly reports that schema-engine validation is NOT_RUN while
retaining runtime controls; runtime ships with standard-library dependencies only.

## Boundaries and next task

This is a graph-local wait record, not a watcher launcher, liveness monitor,
approval grant or transaction spanning the separate SQLite execution authority.
An unrecorded external grant cannot be discovered from graph JSON. External-mode
coordinators must stop/release their grant and serialize dispatch before recording
a wait; this packet does not promise cross-store fencing. Human-only actions and
act-specific standing authority remain governed by L3.

Exact next task: independently review this bounded contract, run a serialized owner aggregate, then merge normally into
`feat/release-iteration` through exact-head eligible CI. Reconcile final feature
requirements including the original working-budget headroom definition before
claiming PR112 complete.


## Independent review and accepted-base composition

Parent/root independently reviewed [adb82f7c97a4a82b7d2bd8f8f17fee97a111ab8b](https://github.com/ssheleg/task-pipeline/commit/adb82f7c97a4a82b7d2bd8f8f17fee97a111ab8b)
and returned bounded PASS: source/schema/transitions/docs read; 15 focused cases
replayed with 60 owned trees removed; five additional real CLI observations
covered an inert shell-like watcher, a runnable sibling, cross-node stale-ID
refusal with byte preservation, wait-only exit 6, and concurrent waits with exactly
one success. Cross-store and watcher-liveness limits remain explicit.

The separate R09 prose change [dac8bc9aaf7ef98f554917f38d6780cd0d948ee0](https://github.com/ssheleg/task-pipeline/commit/dac8bc9aaf7ef98f554917f38d6780cd0d948ee0) also
received parent/root bounded PASS. It was fast-forwarded into this branch before
merging independently reviewed PR114 composition
[31e0f5aeacb709639c37e621c9fe73dec0f11f2e](https://github.com/ssheleg/task-pipeline/commit/31e0f5aeacb709639c37e621c9fe73dec0f11f2e). Merge
[24e745e3d35781d8421b0cbecfe20767a3e39970](https://github.com/ssheleg/task-pipeline/commit/24e745e3d35781d8421b0cbecfe20767a3e39970) had one conflict: the old paragraph
saying distinct wait states did not yet exist versus TP2's exit-6 paragraph.
The reviewed TP2 paragraph was retained. Other incoming executable files belong
to PR114; the diff against 31e0 contains only TP2/R09-owned paths and receipts.
Post-composition focused replays passed: graph-wait 15, continuity 31, approval 41.
A single serialized aggregate on the composed frozen candidate remains pending.


## Composed owner aggregate

`npm test` exited 0 on clean frozen source
[71ff0f07189854a8373113ee21435262ddc723b3](https://github.com/ssheleg/task-pipeline/commit/71ff0f07189854a8373113ee21435262ddc723b3).
[Exact source, output hash and skips](2026-10-13-l3-graph-waits-full.json) bind
[the compressed full output](2026-10-13-l3-graph-waits-full.log.gz). The engine
redactor case was explicitly skipped because OBSERVATORY_ENGINE_DIR was unset;
that absence is not a redactor pass. No source files changed during the run.
Final SKILL.md bytes equal the accepted R09 dac8bc9 body (4639/4750 cl100k),
so composition retains111 working-budget tokens. Hosted exact-head integration
remains pending.


## Accepted PR114 base admission

PR114 merged normally at25dc4f898c143d410cb8cc0b8f17e4edd73da6eb.
It was merged without conflicts into this branch at
6173a3caf0ae087f09cfaa3631fd430d30836ab2. `git diff --name-only
71ff0f0..6173a3c` contains only seven evidence files under docs/evidence/runs;
all executable, schema, skill, reference and workflow bytes equal the source
that passed the composed owner aggregate. Incoming PR114 changes relative to
already-composed31e0 are its three aggregate receipt files only. Final hosted
checks bind the promoted PR119 head separately; no repeated local aggregate
is claimed or required by this byte-equivalent evidence-only admission.


## Hosted property correction

The first exact-head PR119 validation38350663707 failed shard4 despite the
local aggregate passing. `test/property_graph_conditionals.py` is a hosted
property corpus entry: node conditionals must remain behind definitions refs
so the validator dereference branch stays exercised. TP2 had inlined the new
wait conditional. A direct replay on3f60b2e exited1 with the same diagnostic.
The rule is now moved without changing its parsed content into
`definitions.rule_waiting_needs_watcher`, and node.allOf references it. The
existing property is also invoked by the local graph-wait regression, closing
the local-gate omission. Direct property replay and16 graph-wait cases pass,
with60 owned trees created and removed. The failed hosted run remains evidence;
a corrected frozen candidate requires its own genuine hosted verdict.
