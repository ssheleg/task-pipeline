# Decomposition — cutting a platform into bricks

A one-feature task goes through the pipeline once. A **platform** — anything whose
brief describes more than one deliverable, more than one surface, or a system
rather than a change — must be cut into modules first, and then built one brick at
a time, each brick carrying its own documentation, spec, plan, build and gates.

This runs at the end of **stage 2**, on the approved design, before any spec is
written. It is skipped — explicitly, in writing — when the work is a single module.

## Contents

- When it applies
- How to cut
- The module map — the artifact
- GATE (part of stage 2, manual)
- The program loop — one brick at a time
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

Write `docs/superpowers/specs/YYYY-MM-DD-<topic>-modules.md` and commit it. It is
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

## Program done

The program is finished when every row is `done` or `deferred` with an agreed home,
the cross-module contracts are exercised by tests that cross the seam (not just
per-module unit tests), and the final acceptance covers the platform's REQ table as
a whole — not module by module.
