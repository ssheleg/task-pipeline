# Canvas — <topic> (YYYY-MM-DD)

The target state of the next version, laid over today's logic: wave mode's committed
target-state spec (`references/waves.md` → *The canvas*), written at step 3 of an iteration
(`references/iteration.md` → *Integration, until it converges*). The machine-readable plan
is `<topic>-plan.json` (or the work graph), the inventory is `<topic>-inventory.json`
(inventory/1), and the question queue is `<topic>-questions.md`. This page cites the
dossiers by section and does not repeat them.

**Read at:** <repository @ commit, one per repository the canvas touches — the state this
design was laid over>.

**Decisions applied without re-opening:** <each recorded decision this canvas rests on, with
its citation>.

## Contents

- 1. As-is → to-be
- 2. The integration seams
- 3. Item → module → node → wave
- 4. Deleted or superseded
- 5. Remaining conflicts → questions
- The waves

## 1. As-is → to-be

### Per module

| Module | As-is (the facts that matter) | To-be | Dossier |
|---|---|---|---|
| A <name> | <today, with file:line> | <the next version> | <dossier § sections> |

### Per contract

| Contract | Owner | Change | Nodes |
|---|---|---|---|
| <schema, wire format, doc of record, register> | <owning repository or Project on the board> | <additive / breaking / new> | <node ids> |

## 2. The integration seams

How each integration happens, who owns each side, and what crosses it. Two dossiers that
change one seam were designed together; a ★ marks a seam that re-designed a dossier.

| Seam | What | Sides | Rule | Nodes |
|---|---|---|---|---|
| S1 | <seam> | <module ↔ module> | <the one rule both sides follow> | <node ids> |

## 3. Item → module → node → wave

Generated, not hand-written: `scripts/waves.py assign --modules <modules.json> --plan
<plan.json> --write`, then `waves.py count`. Every inventory item is a row. An item on no
node is closed with its receipt, carried (`release: program`, with the reason), or a gap in
this canvas — `waves.py validate` exits 1 on the last.

| Item | Module | Node(s) | Wave(s) | Status |
|---|---|---|---|---|
| <ID-001> | <A> | <A-1> | <1> | <holds / changed / fixed: receipt / carried: reason> |

## 4. Deleted or superseded

What the next version removes — code, screens, contracts, docs, rows — and which node
removes it. A removal nobody wrote down survives the release.

| Node | Removes |
|---|---|
| <A-1> | <the old path, the doc sentence, the register row> |

## 5. Remaining conflicts → questions

What integration could not settle, each a row in `<topic>-questions.md` with both designs
attached.

1. <conflict> → <question id>

---

## The waves

Cut per `references/waves.md` → *Cutting the waves*: a wave holds only items closable in one
pass; wave 1 is the walking skeleton; lanes run in parallel inside a wave and respect file
ownership. Each node carries its own risk class (`references/iteration.md` → *Verification
starts when a node lands*): R1 one passing round on one tier, R2 one, R3 two, one of them recorded adversarial.

**Counts:** <from `waves.py count` and the graph: nodes by risk, by wave, out of waves>.

### Wave 1: <name>

**Exit criteria, written before the wave starts:**
- <the tests, the live walk, the gates and the documents that will prove it closed>

**Nodes by lane:**

| Lane | Nodes |
|---|---|
| <lane> | <A-1 R2 → A-2 R1> |

**Seam checks:** <{node, node} the seam group checked once its last node lands>.
