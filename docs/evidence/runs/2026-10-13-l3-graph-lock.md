<sub>ssheleg skills — task-pipeline · agent-sync · evidence-docs</sub>

# L3 TP-2 prerequisite: refuse unlocked graph mutation

Source baseline: `1af2e80`, the
[watched-wait packet](../plans/2026-10-13-l3-graph-waits.md), stacked on the
independently reviewed TP-6 implementation. This slice fixes the measured lock
failure before adding wait/resume mutations. **The waiting state is not yet
implemented.**

The real graph `add` process previously exited 0 and changed the graph when
`.graph.lock` was a directory, `fcntl` was unavailable, or `flock` raised an
`OSError`. Each emitted a warning and continued unlocked. The new focused
controls first failed in all three cases; the valid-lock positive passed.

`graph.py` now refuses those paths before reading/writing the graph and states
`nothing was written`. Read-only verbs remain available without locking.
This deliberately changes the old warning-only behavior on unsupported platforms;
no new unverified Windows locking implementation is claimed. It is local file
serialization, not an atomic transaction with the separate SQLite execution store.
The mutation's existing read-modify-write and atomic replacement remain intact.

## Verification

`python3 -B test/audit_regressions/l3_graph_waits.py`: **6** focused cases pass:
three failures preserve graph bytes; a valid lock permits the addition; read-only
validation works without locking; four simultaneous valid additions all survive
with unique ids. Its six owned temporary trees were removed. The three small
baseline-failure trees were removed explicitly after inspecting their synthetic
graphs; the red log was retained at the local run level.

`git diff --check`: exit 0. No full owner suite or full graph regression run was
performed for this prerequisite slice; they remain part of the completed TP-2
packet's gate. No real graph, provider, host configuration, release or installed
payload was changed.

## Next task

Independent review this compatibility change, then implement the remaining
[TP-2 packet](../plans/2026-10-13-l3-graph-waits.md). A wait needs a unique wait id
in addition to its kind and watcher; matching the id on resume prevents a stale
watcher from releasing a newer wait that reused the same watcher name. Preserve
retired wait metadata in the revision record. Graph-local waiting and external
execution claims remain separate contracts; do not claim cross-store atomicity.

---

**Made with [ssheleg skills](https://github.com/ssheleg/sshlg-skills)**

- [`task-pipeline`](https://github.com/ssheleg/task-pipeline) — conservative mutation prerequisite
- [`agent-sync`](https://github.com/ssheleg/agent-sync) — scoped task lease
- [`evidence-docs`](https://github.com/ssheleg/task-pipeline) — source-bound red/green evidence
