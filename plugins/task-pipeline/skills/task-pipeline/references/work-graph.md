# The work graph — the queue a script walks so the model never reads it

**One job: hold what is left to do, in a form whose cost does not grow with the
programme.**

A plan is prose. A prose plan for a real release is hundreds of lines, and a model that
re-reads it every iteration spends its context on ground it has already walked — so the
cost of knowing *what is next* rises with the size of the work, which is exactly backwards.

`.task-pipeline/graph.json` is the same information as a typed graph, and
[`scripts/graph.py`](../scripts/graph.py) answers one question against it: **which nodes are
runnable right now.** What enters a context each iteration is then bounded by the
**frontier's width**, not by the graph's size.

Measured on this build: a 400-node graph (51 KB) and a 4-node graph produce the same
**27-byte** frontier. That property is the whole reason the file exists, and it is why
`next` prints the frontier and nothing else — anything else printed there is paid on every
turn of every loop.

---

## Contents

- What is in it, and what each field is for
- The verbs, and their exit codes
- The three things a schema cannot state
- What it deliberately does NOT do
- Rationalizations

## What is in it, and what each field is for

`graph.schema.json` is the contract; this is why each part is there.

| Field | Why |
|---|---|
| `goal` | echoed from `pipeline.json` → `release.goal`, so the graph carries the thing it serves rather than pointing at a file that may have moved on |
| `requirements` | the REQ ids the brief froze. **`serves` resolves against these** — without them it was a non-empty string and nothing more, and that field is the one edge joining the intent graph to this one |
| `goal_clauses` | release work no requirement names. Enumerated, never matched against the goal's prose: substring-matching a sentence produces confidence without correctness |
| `nodes[].owner` | which role does it. A node nobody can dispatch never leaves the frontier and nothing says why |
| `nodes[].serves` | the REQ or goal clause it exists for. A node serving neither is **parked with that as the reason** |
| `nodes[].blocked_by` | what must close first. This is what the frontier obeys |
| `nodes[].touches` | what it **mutates**. Two runnable nodes writing one file is the false parallelism [`planning.md`](planning.md) refuses — *distinct is not the same as independent, and the check is what they touch, never what they are called* |
| `nodes[].check` | **how this node will be closed** — one command, or the named judgement where no command can decide it. Required on every node except a `parked` one. `agents/verifier.md` runs it and reports its output as the evidence row; before this field existed that instruction pointed at an absence, leaving the verifier the two things it forbids — invent a check, or run everything (B-080) |
| `nodes[].evidence` | required when `status` is `done`. A node called done by assertion is what evidence exists to prevent |
| `nodes[].parked_reason` | required when `status` is `parked`. A park with no reason is indistinguishable, a week later, from work quietly dropped |
| `edges[].payload` | what the dependency hands over. **An edge carrying no named artifact is chronology drawn as architecture** |
| `revisions` | why the graph is not the graph stage 2 wrote. A graph that changed for reasons nobody recorded can explain its own completion by appealing to a plan that existed only at the end |

## The verbs, and their exit codes

Exit codes are the contract, per standing instruction `R-004`: **the next command is
conditional on the code, never merely sequenced after it.**

| Verb | Prints | Codes |
|---|---|---|
| `validate` | every violation, in a stable order | `0` clean · `1` any |
| `next` | the frontier, ordered by how much each node unblocks — **and nothing else** | `0` printed · `3` all done · `4` nothing runnable |
| `coverage` | each requirement with the nodes serving it | `0` covered · `1` a gap, named |
| `goal` | the release goal | `0` · `3` unstated |
| `add` | the id it allocated | `0` · `1` refused |
| `park` | the id and the reason | `0` · `1` refused |
| `certify` | the round, and on a failure every `breaks` finding with its fix and its check | `0` all three tiers passed · `1` a tier failed, or a report is malformed |
| `close` | the goal, the new frontier count, and what was not verified | `0` · `1` refused **or the verdict stops the run** |
| `producer` | what produced this proof — actor, model, runtime, skill, config, commit, trace | `0` |
| `doctrine` | how many of the bundle's reference files this run opened | `0` |

**`next` is ordered by what each node unblocks, transitively, and the number is computed.**
A `priority` field is something somebody typed once and nobody revisits; this one moves when
the graph does. Ties break on declaration order, so the frontier is stable between runs —
an unstable one costs more than it looks, because an agent calling `next` twice starts the
other node.

**One node, one completion test.** `check` is a string rather than a list, because the
requirement is singular throughout — one input, one job, one output, one owner, one
completion test. A node needing two unrelated checks is a node doing two jobs, and the
answer is to split it; one gate made of two commands is `a && b`, which is still one gate.
A **`parked`** node is the single exemption: it is the one node nobody will close, and
*n/a — parked* in that field is confidence without correctness. `park` never removes what
the node said it would run.

**A node is closed by three readings, not one.** `certify` takes one tier report from each of `unit`, `seam` and `product` — dispatched blind and in parallel — requires all three to pass, and assembles the seven-key verdict `close` consumes. `close`'s contract is unchanged; what changed is that the verdict is now built from three readings at different distances instead of written from one, because a change can be correct where it was made and wrong one level out. A failing round records itself and leaves the node open. Doctrine: [`certification.md`](certification.md).

**`close` stamps the commit; the verifier never supplies it.** A verdict written after the
tree moved is evidence about a different tree, and an agent cannot name the wrong commit if
it is never the one naming one.

**A stop closes its node and refuses the next step.** `replan.possible: false` says the run
cannot continue *around* what it found — not that the work just verified did not happen.

## The three things a schema cannot state

The split is where the format actually puts it, which is not where the first draft drew it.
`graph.schema.json` states everything JSON Schema can, including `done → evidence` and
`parked → parked_reason` — the first version claimed those were beyond it and was wrong.

What genuinely cannot be expressed is cross-document and cross-node, and lives in
`violations()`:

1. **Whether `owner` names a role that exists** — with a near-miss hint, because an agent
   told only *no* will try a synonym.
2. **Whether `serves` resolves**, and whether every `blocked_by` and edge end is in the
   graph at all.
3. **Whether the edges cycle** — the one failure of this design that looks exactly like slow
   progress: a frontier can be non-empty forever while nothing is runnable.

And one more that is not about expressiveness: **the schema is never applied to a live
graph.** `graph.py` is stdlib-only by design, so `violations()` also enforces the rules the
format states — because a rule checked only against the shipped example is a rule the run
does not have.

## What it deliberately does NOT do

- **It is not committed.** `.task-pipeline/graph.json` is a run artifact. That is a live
  tension, not a settled question: a graph deleted with its run cannot be inspected
  afterwards, and `docs/evidence/backlog.md` carries it rather than this file pretending it
  is resolved.
- **It does not decide the module map.** Stage 2 does ([`decomposition.md`](decomposition.md));
  the graph is where that decision becomes walkable.
- **It does not schedule.** `next` says what *may* run. Whether two runnable nodes are
  dispatched together is the dispatcher's call, and the collision warning on stderr is what
  that call is made against.
- **It does not read like a plan.** If you want to know why the work is shaped this way, the
  brief and the spec say so. The graph says what is left.

## Rationalizations

| The excuse | Why it is wrong |
|---|---|
| *"The verifier will work out what to run."* | Then the node's completion test is decided by whoever happens to close it, and two closes of one node disagree. The field is where the planner says it, and `validate` refuses a node that does not |
| *"I'll just read the graph, it's only forty nodes."* | Forty is the number today. The property being protected is that four hundred costs the same, and it stops being true the first time the model reads the file |
| *"The frontier is short; one extra line won't matter."* | It is paid on every iteration of every loop. That is what *the frontier and nothing else* means |
| *"`blocked_by` already says the dependency, the edge is bookkeeping."* | The edge carries the **payload**. A dependency handing over nothing named is the fake edge with a field around it |
| *"I'll add the node now and record why later."* | Later is the run that cannot say why its plan changed, which is the run whose completion claim cannot be falsified |
| *"The graph validates, so the mutation was fine."* | `validate` is stdlib and the format is richer. Both were made to agree once, and the disagreement returned within a day — check the two against each other, not the result against one |
