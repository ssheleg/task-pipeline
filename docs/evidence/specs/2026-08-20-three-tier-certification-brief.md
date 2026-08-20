# Brief — a node is closed by three readings, not one

**Run** `2026-08-20-three-tier-certification`
**Requested by** the operator, in these words: three subagents at different levels of
visibility; the first takes apart the exact business logic where the change landed —
classes, functions, code, concrete details — and checks nothing broke; the second looks
one level up at related classes, functions and modules; the third rises again to the
documentation and the product, and understands how the changed functionality interacts
with the rest. All three must pass to confirm the task is fixed. If one fails, the task
goes back for correction and the cycle runs again.

**Why it was asked for, in the operator's own diagnosis:** *"не хватает видимости — агент
часто делает какие-то правки, не обращая внимания на более высокоуровневые связанные
вещи."* That is a statement about context, not about care, and it is correct: a verifier
reads the diff it was handed, and a change can be correct where it was made and wrong one
level out.

## Source ledger

| Source | What it gave |
|---|---|
| `plugins/task-pipeline/agents/verifier.md` | the existing single verdict and its seven keys — the contract this must not break |
| `scripts/graph.py` → `verdict_violations`, `cmd_close` | what `close` already refuses, and the commit-stamp law |
| `graph.schema.json` → `definitions.node` | `additionalProperties: false`, so a new node field is a schema change |
| `references/loop-guard.md` | the ceiling idiom: measure rather than stop, and the ledger that makes detection mechanical |
| `references/work-graph.md` | the verb table, its exit codes, and where a new verb is documented |
| `test/graph_test.py` | the fixture idiom (`@case`, temp-dir graphs) — 129 cases before this run |
| `docs/evidence/backlog.md` | 110 rows; no row for this, so B-111 was opened by this run |
| `docs/evidence/retro.md` | standing instructions, read in full |

## The REQ table

Frozen. Adding is free; removing needs the operator.

| REQ | What must be true | Verified by |
|---|---|---|
| REQ-045 | A node is closed by **three** independent readings — `unit`, `seam`, `product` — and the close is refused until all three pass | `certify` fixtures: all three present, exactly once each, all naming one node |
| REQ-046 | The three run **blind**: no tier reads another's report, and a report citing another tier's verdict is refused | a fixture plants a citation; `CROSS_TIER` refuses it |
| REQ-047 | A tier **cannot pass on an empty `scope`** — the anti-rubber-stamp rule | a fixture plants a pass with `scope: []` |
| REQ-048 | A tier cannot pass while carrying a `breaks` finding, and cannot fail without naming one | two fixtures, one per direction |
| REQ-049 | Every `breaks` finding names the `check` that will prove its fix | a fixture plants a blank `check` |
| REQ-050 | `close`'s contract is **unchanged**, and a certification's assembled verdict is one `close` accepts | a fixture round-trips `certify` → `close` and requires exit 0 |
| REQ-051 | A failing round **records itself** and leaves the node open; rounds accumulate so churn is countable | two `certify` calls on one graph → `round: 2`, `status: pending` |
| REQ-052 | At the ceiling the gate **measures rather than stops**, naming the tier that failed every round | a fixture runs two failing rounds at `--ceiling 2` and asserts the tier name and the doctrine pointer |
| REQ-053 | Every rule of the gate is **watched failing** | `npm run test:certify` — one mutation per rule, killed only by a `certify:` fixture |
| REQ-054 | The doctrine has a single home, and every surface that ships it says so | `references/certification.md`, in the SKILL.md index, `portability.md`'s manifest and the README |

## Carry-over

| What | State | Home |
|---|---|---|
| Whether `close` should refuse a verdict for a node with no `certification.round` | open — it is a migration for any graph mid-run, and this release already changes how every node closes | B-112 |
| Whether the shipped agent prose yields a schema-valid report | **measured by live dispatch in this run**, and recorded in the ledger rather than assumed | `verification.md` |

## What this run deliberately did not do

**It did not remove the single verifier.** `agents/verifier.md` still documents the
hand-written verdict, because a verdict already in flight when this ships has to be
closable. It now opens by pointing at the three tiers.

**It did not make certification mechanically obligatory.** `certify` refuses an incomplete
certification, which is the half a script can enforce; that a run *uses* `certify` at all
is doctrine. Making it obligatory is B-112, and it is filed rather than done because the
flag is a migration.
