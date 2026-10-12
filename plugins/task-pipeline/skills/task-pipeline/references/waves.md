# Wave mode — closing a whole board in its final form

`/task-pipeline waves`. The request is not one change but **the whole board**: every open
item a project carries — the board and its lanes, carry-over ledgers, plan rows,
verification rows still at `never`, scenarios with no coverage, open PRs and unlanded
branches, asks from other products' sessions — plus the operator's new requests.

**It is a program mode of the existing stages, not a parallel cycle.** Stages 0–4 run
once, for the whole board. Stages 5–8 run once per wave. Stages 9–10 close the release.
Every gate in [`stages.md`](stages.md) still holds where its stage runs; what the mode
changes is how many times each stage runs, and over what.

Decided by the operator on 2026-10-11 and first applied that day to a board of 701 items.

## Contents

- The rule it exists for
- How the stages map
- Wave 0 — the survey and the inventory
- The questions — closed from sources, then one batch
- The canvas — the target state over the current logic
- Cutting the waves
- The wave loop
- The close pass, after every wave
- A board bigger than one release
- What stays human
- The graph carries the wave
- Rationalizations

## The rule it exists for

**Build the system in its final form, never through intermediate states.** An
intermediate state that a later task undoes is the most expensive thing an agent
produces: the build, the review, the migration and the operator's attention are each
paid twice, and the second payment is for removing the first. So every item is designed
against the target state of the whole system first, and only then cut into waves.

**No wave builds a shape a later wave undoes.** A stub is allowed only at a contract the
canvas declares, and the wave that removes it is named beside it. A stub with no named
removal is the intermediate state this mode exists to refuse.

What the mode buys, in the order the operator named it: transparency (the inventory,
the canvas and the wave plan live in the repository, so any agent can resume from them),
stability, autonomy, predictability (each wave says before it starts what it closes and
how that is proved), minimum operator time, fast real results, and a strategy corrected
on real agents, tasks and users rather than on the first guess.

## How the stages map

| Stage | In wave mode |
|---|---|
| 0 Intake | once, over the whole board: wave 0's survey is the harvest, the inventory is the work-list, and every in-scope item becomes or joins a REQ row in the operator's words |
| 1 Docs study | once, for every contract the canvas locks |
| 2 Brainstorm + decompose | once: the canvas extends the module map ([`decomposition.md`](decomposition.md)), and the work graph carries each node's wave |
| 3 Spec | once: the canvas is the committed target-state spec; a wave's dossier may deepen a section, never contradict it |
| 4 Plan | once: every wave's nodes, its exit criteria and the question batch. Re-cut at each wave boundary, as a recorded revision |
| 5–8 Build → post-deploy | per wave, then the close pass |
| 9 Docs + wiki · 10 Acceptance | once, to close the release, over everything the waves shipped |

**One planning gate, not three prompts.** The manual gates of stages 0, 2 and 3 are
presented together at the end of planning: the brief, the canvas, the wave plan and the
question batch in one message. Each gate's criteria are still checked and printed; the
operator is asked once, and the go names the gates it closes. Silence closes none.

## Wave 0 — the survey and the inventory

**Harvest every source of open work, by id** ([`knowledge-sources.md`](knowledge-sources.md)
supplies the sources; [`backlog.md`](backlog.md) the board). For whole-project scope, run
`project-audit` beside it as a read-only sidecar: its HTML and JSON are measured
findings, and its proposed rows join the inventory like any other source. Where the
product has users, walk their real path in the built app on a fresh profile with
disposable data. A finding is a fact with a receipt, never an impression.

**A declared source list outranks discovery.** Where the repository carries
`docs/backlog-sources.json` — the contract is owned by the Fabric workspace's
`knowledge/backlog.md` — the harvest reads exactly the sources it lists, as the board,
with the id, title and status columns it names. Status changes land only in those owning
files, under a lease. A new source joins the manifest in the same change. A generated
view of them, such as a published common backlog, is never edited. A source of open
work the manifest does not list is reported as a finding, not silently added.
`scripts/backlog_sources.py --root . [--found <path> ...]` reads the manifest first: it
prints the sources the harvest reads, refuses a manifest the harvest could not follow
(exit 1, every reason named) and reports each `--found` source it does not list (exit 3).
No manifest is discovery, said aloud (exit 0).

**One machine-readable inventory, nothing outside it.** A single committed file,
`<artifacts>/specs/YYYY-MM-DD-<topic>-inventory.json`, one entry per open item:

| Field | Carries |
|---|---|
| `id` | the item's id in its owning register; an item without one gets one there, in the same change |
| `source` | where it was found, as `file:line` |
| `status` | as measured, not as the register last said |
| `area` | the part of the system it touches |
| `node` | the canvas node it lands on |
| `wave` | the wave that closes it, or the release it is carried to |
| `release` | this release, or `program` |

`blocked_by`, `closable_in_one_pass` and `notes` are worth carrying beside them.

**Verify each open item against the code before trusting it.** A stale item is closed
in its owning register with the receipt that shows it done; duplicates are clustered,
both ids kept. A register that says *open* about shipped work is the commonest thing a
survey finds.

**Assign nodes and waves with a committed script, not by hand.** A deterministic script
reads the inventory and a short wave table and writes `node`, `wave` and `release` onto
every entry, then prints the counts per wave and per node. A re-cut is then a diff to a
table and a re-run, which a reviewer can read; seven hundred hand-edited rows are not.

## The questions — closed from sources, then one batch

**Close every question from the sources first**, in this order: the operator's recorded
decisions, ADRs and principles, the knowledge base, the code, the neighbours' contracts.
A question answered there is recorded with its citation — *resolved from the sources,
not asked* — and closed. What remains is only what is genuinely the operator's: access,
consent, money, a business or product direction, an outward or irreversible act.

**Those go once, as one batch, at the end of planning.** Each carries a recommended
answer and the consequence of each answer, ordered so prerequisite decisions come first
([`grill.md`](grill.md)). A go that leaves a question unanswered takes the
recommendation, recorded as **assumed** in the decisions table, and every wave that
depends on an assumption names it — so a different answer later re-plans exactly those
waves and no others. After planning, a question is asked only at a wave boundary, in the
hand-back's DECISIONS WAITING ([`progress.md`](progress.md)).

**An outward or irreversible act is never assumed.** Publishing, tagging, deploying
without a specific standing authorization, sending to a person, spending money,
deleting data: each waits for the operator's explicit go, asked with a verified direct
link. A recommendation is not an authorization.

## The canvas — the target state over the current logic

One committed spec, `<artifacts>/specs/YYYY-MM-DD-<topic>-canvas.md`, extending the module
map. It is the current system with every change laid over it:

1. **As-is → to-be per module and per contract** — data and events, screens and flows,
   cross-product links.
2. **The integration seams** — how each integration happens, who owns each side, what
   crosses it.
3. **REQ → module → wave**, one row per requirement.
4. **Deleted or superseded** — what the new version removes (code, screens, contracts,
   docs) and which wave removes it. A removal nobody wrote down survives the release.

**Every inventory item lands on a node.** An item that lands nowhere is either out of
scope — said, with a register row — or a gap in the canvas. **The canvas is reviewed for
coherence before any wave is cut:** two items that change one seam are designed together,
because designed apart they are the intermediate state the rule above forbids.

## Cutting the waves

**A wave holds only items closable in one pass.** All four, for every item in it:

- its dependencies are done, or inside the same wave;
- it touches one seam, or a few adjacent ones;
- its verification can run together with the rest of the wave;
- the wave leaves the system working — landable, with no half-built shape exposed.

**Wave 1 is the walking skeleton**: the thinnest end-to-end path of the target that
proves the spine, for the reason [`decomposition.md`](decomposition.md) gives for a
platform's first brick. **Each wave names its exit criteria before it starts** — the
tests, the live walk, the gates and the documents that will prove it closed. Criteria
written after the wave are a description of what happened.

An item that cannot close in one pass because it needs a person stays on its node,
marked `needs-operator`, out of every wave until it is unblocked.

## The wave loop

Each wave runs stages 5–8 as [`stages.md`](stages.md) states them, then the close pass.
Between waves the run does not ask whether to continue: it takes the next wave
([`continuity.md`](continuity.md)). A genuine ambiguity parks its node `needs-operator`
and the wave goes on with the nodes it does not block; the run stops only when the whole
frontier is blocked. When the board is empty, it says so once.

Research, the audit and the blind readings run in parallel agents; builds stay sequential
wherever two of them share a seam ([`planning.md`](planning.md) → file ownership).

## The close pass, after every wave

In this order, inside the wave rather than after it:

1. **Verify.** Every node the wave closes is certified ([`certification.md`](certification.md)),
   and [`audit.md`](audit.md)'s exit is re-measured over what the wave touched.
2. **Finish and fix — one fix round**, inside [`loop-guard.md`](loop-guard.md)'s caps.
   Every finding is fixed in the wave or parked with a board row and its reason; nothing
   is dropped silently.
3. **Document** — the Doc Loop and the stage-9 propagation matrix
   ([`documentation.md`](documentation.md)), scoped to the wave: scenarios, decisions,
   docs and registers in the same change as the code.
4. **Mark the canvas.** Each node the wave closed carries its status and the commit.
5. **Re-read the goal** ([`continuity.md`](continuity.md) → *The goal is re-read between
   items, not only the board*). A re-plan is a committed `revisions` entry plus a canvas
   edit, never a quiet change.
6. **Re-measure the inventory and re-cut the remaining waves** from the updated target —
   never from the original guess. New findings join the inventory with ids.

## A board bigger than one release

**It becomes a program.** The release takes the first waves; the rest stays on the
canvas by node, `release: program`, never dropped. The next release resumes from the
canvas: it re-measures the inventory rather than re-running wave 0 from nothing, and its
waves are cut from the nodes still open.

## What stays human

Sign-ins, consents, payments, sending to people, and every outward or irreversible act.
The mode removes *"shall I continue?"* between waves and *"what did you mean?"* where a
source already says; it never removes a person from a decision that is theirs. A
`manual` gate still waits for its go ([`continuity.md`](continuity.md) → *The limit,
before the capability*).

## The graph carries the wave

The work graph ([`work-graph.md`](work-graph.md)) carries `wave` on a node, an integer from
1. Three verbs read it:

- `graph.py validate` refuses an edge from a later wave's node into an earlier wave's
  node: an earlier wave that waits on a later one cannot close in its own pass.
- `graph.py next --wave N` prints wave N's frontier only. Exit `3` says the wave is done,
  `4` that nothing in it is runnable, `1` that no node is in wave N.
- `graph.py wave N-007 --to 3 --why "<reason>"` moves a node and writes the revision.
  It refuses a move that would break the order above.

Without python3 the same three facts live in the wave plan's table, checked by hand and
said to be checked by hand.

## Rationalizations

| Excuse | Reality |
|---|---|
| "Ship the simple version now, the real one later" | That is the intermediate state. Its removal is a second build nobody planned |
| "Ask each question as it comes up" | Each one is a human round. Close it from the sources, or put it in the batch |
| "The board is too big to inventory" | The inventory is the plan. Without it the waves are cut from memory |
| "Re-cutting waves makes the pipeline dynamic" | A re-cut is a committed revision and a canvas edit. The static-graph decision in [`planning.md`](planning.md) holds |
| "The recommendation is obviously right, so assume the deploy go" | An outward act is never assumed. Ask for the specific go once, in the batch |
| "Wave 3 can stub what wave 5 will build properly" | Only at a declared contract, with wave 5 named as the stub's removal |
