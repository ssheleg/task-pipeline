# Decomposition — cutting a platform into bricks

A one-feature task goes through the pipeline once. A **platform** — anything whose
brief describes more than one deliverable, more than one surface, or a system
rather than a change — must be cut into modules first, and then built one brick at
a time, each brick carrying its own documentation, spec, plan, build and gates.

Module mapping runs at the end of **stage 2**, before the spec; a single-module change skips that map explicitly.
Stage-4 leaf sizing still applies when work is handed to independent agents; skipping the map does not skip task sizing.

## Contents

- When it applies
- How to cut
- The module map — the artifact
- GATE (part of stage 2, manual)
- The program loop — one brick at a time
- Executor-sized tasks and context
- Program done

## When it applies

Decompose when any of these is true:

- the brief names several independent capabilities ("accounts, billing, reporting");
- the work spans several surfaces (API + web + worker) that could ship separately;
- the REQ table has requirements that no single deliverable satisfies together;
- the design's units have their own data and could plausibly be owned by different
  people.

Otherwise record one line in the design — `single module: <name>` — and go to
stage 3. A skipped decomposition is a decision, never an omission.

## How to cut

**By capability, not by layer.** "Ordering", "Billing", "Notifications" are
modules. "Controllers", "Services", "Database" are not: a layer cut forces every
feature to touch every module, which is the opposite of a brick.

A module is a **brick** when all of these hold:

1. **Independently specifiable** — you can write its dossier without deciding
   another module's internals.
2. **Independently buildable and testable** — its tests pass without another
   module's implementation present (stubs at the contract are fine).
3. **Owns its data** — the entities it is the source of truth for belong to it, and
   nothing else writes them.
4. **Talks through declared contracts only** — every cross-module interaction is a
   named API, event or schema, listed in both modules' dossiers.
5. **Deliverable on its own** — landing it leaves the system working, even if the
   capability is not yet reachable by users.

If a candidate fails (2) or (3), the cut is in the wrong place: either merge it
into its neighbor or move the disputed data to the module that truly owns it.

**Order the bricks:**

- **The walking skeleton first.** The first module is the thinnest end-to-end slice
  that proves the architecture — one real path through the system, however small.
  Building three "foundation" modules before anything runs end-to-end hides
  integration risk until the worst possible moment.
- Then topological order: nothing is built before what it depends on.
- **No cycles.** A cycle means the cut is wrong. Break it by moving the shared
  concept into its own module, or by turning one direction of the dependency into
  an event the other module subscribes to. Record which you chose and why.

## The module map — the artifact

Write `<artifacts>/specs/YYYY-MM-DD-<topic>-modules.md` and commit it. It is
the program's spine: every later run reads it, and its status column is how a
resumed session knows where the program stopped.

```markdown
# Module map — <platform>

Build order is top to bottom. Status: `planned` → `in progress` → `done` |
`deferred`. One row per module, no exceptions.

| # | Module | Delivers | Owns (entities) | Depends on | Contracts exposed | UI? | REQs | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | ordering | place and track an order | Order, OrderLine | — | `POST /orders`, `OrderPlaced` event | yes | REQ-001, REQ-004 | planned |
| 2 | billing | charge for a placed order | Invoice, Payment | ordering | `InvoiceIssued` event | no | REQ-002 | planned |

## Cut rationale

<why these seams and not others; what was merged or split, and what a cycle forced>

## Cross-module contracts

<one block per contract: owner module, consumer(s), exact shape (schema or
signature), and the failure behavior when the other side is unavailable>

## Deferred to later modules

<capabilities deliberately postponed, with the module that will carry them>
```

Every REQ from the brief appears in exactly one module's `REQs` cell. A REQ that
fits nowhere means the map is incomplete; a REQ in two modules means the seam runs
through a requirement — re-cut or split the REQ.

## GATE (part of stage 2, manual)

Together with the design approval:

1. Every module satisfies the brick criteria, or its exception is written down.
2. The dependency graph is acyclic and the build order is topological.
3. The first module is a walking skeleton, or the reason it isn't is recorded.
4. Every REQ maps to exactly one module.
5. Cross-module contracts are named (shape can be locked later, in each module's
   spec — but the *existence* and *owner* of each contract is decided here).
6. The operator approves the map and the order.

## The program loop — one brick at a time

After the map is approved, the pipeline runs **per module**, in build order:

```
module N → stage 3 (dossier/spec) → 4 plan → 5 build → 6 tests
         → 7 lint + deploy → 8 post-deploy → 9 docs + wiki → 10 acceptance
         → mark module done → module N+1 (back to stage 3)
```

Rules for the loop:

- **Stages 0–2 run once for the platform.** Modules do not re-grill and do not
  re-decompose. New information that changes the map goes back to stage 2
  deliberately, as a map revision with the operator's approval — not as a quiet
  edit mid-module.
- **Each module's spec is a full dossier** ([`spec.md`](spec.md)): architecture,
  entities, contracts in and out, business rules, edge and failure cases, UI/Figma
  chain when it has a surface.
- **The contract is the boundary.** A module may stub what a later module will
  provide, but it may not reach into another module's internals; if it needs to,
  the seam is wrong — back to the map.
- **Deploy cadence is the brief's call** (autonomy sweep): deploy each module as it
  lands, or build several and deploy once. Record it; don't decide it per module.
- **Update the map's status column as each module closes**, in the same commit as
  that module's acceptance. The map is the resume point after a lost context.
- **Loop discipline:** a module re-entering the same stage a third time trips the
  loop guard ([`loop-guard.md`](loop-guard.md)) — stop, name the oscillation, and
  fix the layer that owns it instead of iterating.

## Executor-sized tasks and context

The module map is not an execution queue. At stage 4, split each change into
small, reviewable outcomes before handing it to another agent. Keep the original
finding or feature as the parent; only its leaf tasks enter the dispatch queue.
Do not mark the parent done because its plan exists.

### Cut by outcome, with its proof

One leaf owns one observable behavior, invariant, or artifact contract. Include
the focused regression and necessary documentation with that outcome; do not
create separate "write tests" and "write docs" jobs by ritual. Split when a leaf
requires another independent decision, another resource owner, an unrelated
failure mechanism, or more primary context than its declared budget permits.
Do not split a transaction across tasks merely to reach a target task count.

For example, "fix the updater" is a parent. A leaf can make `--dry-run` return
an operation plan without mutation, proved by unchanged fixture bytes and no
mutating child calls. Atomic generation switching and replacement verification
are separate outcomes with their own prerequisites and tests.

Before dispatch, the planner records for every leaf:

- parent requirement/finding and module/interface owner;
- the concrete change, why it is needed, and the observable expected result;
- decisions already made, alternatives rejected, and explicit exclusions;
- exact existing edit targets and proposed create targets; historical evidence,
  migrations and ADRs remain read-only unless their own contract permits edits;
- inputs, required predecessor outputs, and data/control/resource edge reasons;
- ordered implementation steps and a focused positive and negative acceptance;
- primary context manifest, source/context digests, outputs and rollback;
- one integration owner and the claim/capability checks from
  [`planning.md`](planning.md) → Execution packets.

### Resolve material choices before implementation

An implementation leaf is not ready while product behavior, public interface,
data ownership, authorization, dependency policy, or failure semantics remain
undecided. Create a bounded decision task instead: one precise question, named
sources or experiment, time/context budget, required decision record, and the
criterion that resolves it. Its consumers wait for that record and receive a
new packet revision. Do not fill uncertainty with invented certainty.

Routine local implementation choices can remain with the executor. A plan need
not prescribe every variable name. New evidence that invalidates a recorded
decision returns to its owner with the smallest counterexample; the executor
does not silently redesign adjacent modules or restart the whole interview.

### Budget what the executor actually reads

Primary context contains the leaf brief, applicable module/interface decisions,
acceptance, and the relevant source ranges. The full audit, other modules,
alternative designs and historical discussion belong in an indexed appendix.
Keep every required reference resolvable and digest-bound, but do not inject
the entire reference closure into every prompt. Read deeper source on demand
when needed to verify the local change.

Set a primary-context budget for the chosen host before materialization. Record
the tokenizer/model when measuring tokens; a byte or character count is a byte
or character count, never a token measurement. If the materialized primary
context exceeds the budget, split the outcome or move truly optional material
to the appendix. Never truncate constraints, acceptance, error behavior or
dependency outputs to make a packet fit. No universal task duration, file count
or token limit establishes quality; use project defaults and report exceptions.

### Cold-start and completion checks

A fresh executor must be able to answer "what changes, where, why, under which
decision, and how success is observed" from the primary packet without reading
the planner's conversation. Validate this before dispatch; reading an ID or a
title alone is not the test. Recheck hashes and materialize predecessor outputs
after they exist. Planned input placeholders never count as satisfied inputs.

Review the leaf's actual candidate code and evidence. Then check the parent's
acceptance across its leaves so a collection of individually green tasks cannot
drop an end-to-end requirement. Parent close requires current child receipts,
cross-seam checks where applicable, and the integration result. Plan completeness,
dispatch readiness, implemented behavior and released availability are separate
states.

## Program done

The program is finished when every row is `done` or `deferred` with an agreed home,
the cross-module contracts are exercised by tests that cross the seam (not just
per-module unit tests), and the final acceptance covers the platform's REQ table as
a whole — not module by module.
