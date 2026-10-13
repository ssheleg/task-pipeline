# Dossier <letter> — <module name>

One dossier per cluster of inventory items (`references/iteration.md` → *Module dossiers*),
written in parallel with the others, read-only on every repository: the dossier is the only
write. **A dossier is a design, not a plan** — it does not cut waves. Evidence for every
claim: `file:line @commit`, or a command and its output. No secret values, ever.

Written <date> against: <repository @ commit, one per repository read>.

## Contents

- 1. Items
- 2. As-is
- 3. To-be
- 4. Options considered
- 5. Contracts touched
- 6. Nodes
- 7. Deletes
- 8. Questions
- 9. Out of scope / program

## 1. Items

Every inventory item the module table assigns here, verified against the code before it is
trusted. An item that does not reproduce is marked so, with the evidence, and closed in its
owning register.

| id | title (short) | still holds? (yes / no + evidence / changed) | severity |
|---|---|---|---|
| <ID-001> | <…> | <…> | <…> |

## 2. As-is

How the module works today, in the few facts that matter, each with `file:line`.

## 3. To-be

The design of the next version: contracts, data, behaviour, failure handling and logs. One
coherent design that answers every item; say which items each part answers.

## 4. Options considered

| Choice | Options | Chosen | Why |
|---|---|---|---|
| <the real choice> | (a) … (b) … | <…> | <the reason, with the measurement where there is one> |

## 5. Contracts touched

| Contract | Owner (repository / session) | Change | Owner must agree first? |
|---|---|---|---|
| <interface, schema, wire format, doc of record, register> | <…> | <additive / breaking / new> | <yes / no> |

## 6. Nodes

The design cut into build nodes. **The risk class is per node**, never one class for the
whole dossier: one R3 node beside four R1 nodes is five classes, and a dossier-wide class
either over-checks the four or under-checks the one (`references/iteration.md` →
*Verification starts when a node lands*). Files owned by one node only, where possible.

| id | repo | owns (files) | does | tests (★ = fails today) | risk | deps | one pass? |
|---|---|---|---|---|---|---|---|
| <X-1> | <…> | <paths> | <…> | ★ <the test that fails today>; <…> | <R1 / R2 / R3> | <node ids> | <yes / no> |

Count by risk: <R1 n · R2 n · R3 n>.

## 7. Deletes

What the new version removes — code, docs, rows, files — by node.

## 8. Questions

Only what the sources cannot answer: the operator's recorded decisions, ADRs and
principles, the code and the neighbours' contracts were tried first.

| id | question | options → consequence | recommendation | whose (operator / peer: name it) | blocks |
|---|---|---|---|---|---|
| Q1 | <…> | (a) … → … (b) … → … | <…> | <…> | <node ids> |

## 9. Out of scope / program

Items recommended for a later release, each with its reason (`release: program` in the
inventory).
