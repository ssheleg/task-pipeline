# Stage 2 detail

The full gate and freedom level remain in [stages.md](stages.md).

## 2 — Brainstorm + decompose
- **How it runs: [`brainstorm.md`](brainstorm.md)** — built into this skill. Read
  the brief first (stage 0 already answered scope/constraints/done-criteria), then
  explore the codebase, scope-check for decomposition, the open questions in one
  batch, 2–3 approaches with a recommendation, design presented in sections and
  approved section by section. **Hard gate:** no code, no scaffolding, no implementation
  skill before the operator approves the design — including on "obviously simple"
  tasks.
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
  over**. The check is the planner's job and not the verifier's: a node whose completion
  test is decided by whoever happens to close it is a node two closes will disagree about,
  and `validate` refuses one that names none. Then
  `python3 scripts/graph.py validate` — a graph that does not validate is not a queue, and
  `next` refuses to walk one. The reason to prefer it over a prose plan is measured, not
  aesthetic: a 400-node graph and a 4-node graph produce the same 27-byte frontier, so the
  cost of knowing what is next does not grow with the programme.
- **And the check is what THREE readings will run, not one**
  ([`certification.md`](certification.md)). A node is closed by `unit`, `seam` and `product`
  reports, dispatched blind and in parallel, and `certify` refuses the close until all three
  pass. That is a planning fact, not only a verification one: a node whose blast radius nobody
  can name is a node the seam and product tiers cannot scope, so `touches` and `serves` are
  what make the two outer readings possible at all.
- **The queue exists here, so the loop arms here** ([`continuity.md`](continuity.md) →
  *Part 1a*). Where the loop is armed — `run.loop` with `arm: after-decomposition`, the
  operator's preflight answer, or a standing instruction the host carries (which arms here
  unless it says otherwise) — and the map holds more than one module, arm the mode at the
  close of this stage, cite the source as `loop: armed by <source:line>`, and print one
  line: the mode, and
  either the job id and its cancel command (`interval`) or the delay chosen and why
  (`dynamic`). Arming collapses no gate and authorizes no outward act; it decides only
  that the run does not stop to ask *"shall I take the next one?"*. Single-module work
  arms nothing and says so — a loop with one item is a timer.
