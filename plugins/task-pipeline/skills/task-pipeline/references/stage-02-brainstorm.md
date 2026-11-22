# Stage 2 detail

The full gate and freedom level remain in [stages.md](stages.md).

## 2 — Brainstorm + decompose
- The spec loop starts here ([`spec-protocol.md`](spec-protocol.md) → *The loop*).
- **Size the spec** with `spec_protocol.py size` from the brief's facts; the size
  sets the sections and the research ([`spec-protocol.md`](spec-protocol.md) → *1*).
- **How it runs: [`brainstorm.md`](brainstorm.md)**: from the brief, explore,
  scope-check, 2–3 approaches with a recommendation, the design approved section by
  section. **Hard gate:** no code, no scaffolding, no implementation skill before
  the design is approved (by the operator or the brief's standing authorization),
  including on "obviously simple" tasks.
- **The capability map comes first, where the actor branch is armed**
  ([`agent-surface.md`](agent-surface.md)): REQ, then stories, then `CAP-` rows
  (actors, roles, gate, emits, automation, human surface or none), and the agent
  paths as call sequences with their states (pending, partial, denied, async job)
  and typed errors. Every `CAP` row has `Tools` or `Agent excluded`. Screens are
  designed after it, as clients of it ([`brainstorm.md`](brainstorm.md) → *The
  capability map, before the screens*).
- **UI detection (mandatory check):** decide whether the task touches any
  user-facing surface (web, mobile, CLI, TUI — new feature, new screen/command,
  or a change to user-visible behavior). Record the verdict; it arms the UX
  track in stage 3.
- **Decomposition (platforms only): [`decomposition.md`](decomposition.md).** If
  the brief describes a platform rather than a change — several independent
  capabilities, several surfaces that could ship separately, REQs no single
  deliverable satisfies — cut it into **modules** before any spec is written, and
  commit the module map (`specs/<topic>-modules.md`): what each module delivers,
  the entities it owns, what it depends on, the contracts it exposes, its REQs and
  its status, in build order with the walking skeleton first. Single-module work
  records `single module: <name>` in the design and moves on — a skipped
  decomposition is a decision, never an omission.
- **Where the queue is a work graph, it is WRITTEN here**
  ([`work-graph.md`](work-graph.md)): `.task-pipeline/graph.json`, carrying the frozen REQ
  ids so `serves` resolves, one node per unit of work with its owner, what it touches and
  **the check that will close it**, and an edge per dependency **naming what it hands
  over**. The check is the planner's job, not the verifier's: two closes disagree about a
  node whose test the closer picks, and `validate` refuses one that names none. Then
  `python3 scripts/graph.py validate`: `next` refuses to walk a graph that does not
  validate. Measured: a 400-node graph and a 4-node graph
  produce the same 27-byte frontier.
- **And the check is what THREE readings will run, not one**
  ([`certification.md`](certification.md)). A node is closed by `unit`, `seam` and `product`
  reports, dispatched blind and in parallel, and `certify` refuses the close until all three
  pass. That is a planning fact too: the seam and product tiers cannot scope a node whose
  blast radius nobody named, so `touches` and `serves` make those readings possible.
- **The queue exists here, so the loop arms here** ([`continuity.md`](continuity.md) →
  *Part 1a*). Where the loop is armed — `run.loop` with `arm: after-decomposition`, the
  operator's preflight answer, or a standing instruction the host carries (which arms here
  unless it says otherwise) — and the map holds more than one module, arm the mode at the
  close of this stage, cite the source as `loop: armed by <source:line>`, and print one
  line: the mode, and the job id with its cancel command (`interval`) or the delay and why
  (`dynamic`). Arming collapses no gate and authorizes no outward act; the run only stops
  asking *"shall I take the next one?"*. Single-module work arms nothing and says so.
