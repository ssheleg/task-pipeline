# Certification — three readings at three distances, and all three must pass

A node is not closed by one agent's opinion. It is closed by **three independent
readings at escalating visibility**, and the run may not advance until all three
pass.

## Contents

- Why one verifier is not enough, stated as the failure it produces
- The three tiers
- Blind, and it is the whole design
- A pass has to mean something, so two rules have teeth
- The report, and where each field lands
- The commands
- The fix cycle, and its ceiling
- What this costs, said out loud
- Rationalizations

## Why one verifier is not enough, stated as the failure it produces

A verifier reads the diff it was handed. That is not a shortcoming of the agent; it
is the definition of its context. And it means a whole class of defect is invisible
to it by construction:

- the change is correct where it was made, and a **caller's contract moved** under it
- a **second implementation of the same rule** did not get the fix
- a **documented behaviour** is now false, and the document still reads as true
- **another feature** reaches the same path and nobody considered the interaction

None of these is a bug in the changed lines. All of them ship. Each is found by
looking one level further out than the change — which is a different reading, not a
longer one, because the context that finds it is the context that excludes the diff.

## The three tiers

| Tier | Subject | Characteristic finding |
|---|---|---|
| `unit` | the changed functions, classes and branches, plus the node's own `check` | a branch nothing exercises; a boundary that moved |
| `seam` | everything that can reach the change — callers, callees, implementors, shared state, the neighbours' tests | a contract that moved under a dependent; the duplicate that did not get the fix |
| `product` | documentation, scenarios, user-visible strings, and the neighbouring features that share this path | a documented behaviour that is now false; an interaction nobody listed |

Agents: [`../../../agents/verifier-unit.md`](../../../agents/verifier-unit.md),
[`verifier-seam.md`](../../../agents/verifier-seam.md),
[`verifier-product.md`](../../../agents/verifier-product.md).

## Blind, and it is the whole design

**The three run in parallel and no tier reads another's report.** Three readings
that inform each other are one opinion with three signatures — and the failure mode
is specific: an agent that has just read a convincing account of the implementation
will paraphrase it back as product truth. The disagreement between blind readings is
the instrument, so `graph.py certify` refuses a report whose prose cites another
tier's verdict.

Dispatch all three in one message so they run concurrently. Give each the node id,
its `serves`, and the diff — nothing else, and never another tier's output.

## A pass has to mean something, so two rules have teeth

**A tier cannot pass on an empty `scope`.** `scope` is what the tier actually
opened, with `file:line`. A report that names nothing it read is a rubber stamp, and
three rubber stamps cost three times one verifier while reading as three times the
assurance — strictly worse than the single verdict it replaced. `certify` refuses it
by name.

**A tier cannot pass while carrying a `breaks` finding.** There are two severities
and no third, because a certification that admits a maybe admits everything:

- **`breaks`** — the node is not done. Carries a `check`: the command or judgement
  that will prove the fix, for the same reason `replan.add` does. The finding
  becomes a node the next round has to close, and handing that node the absence is
  how the defect returns one round later.
- **`risk`** — found, judged survivable, and named. It ships, and it reaches the
  closing verdict as a blocker with `can_continue_around: true`, which is exactly
  what a named survivable finding is.

## The report, and where each field lands

Eight keys, all required, `[]` a valid answer and silence not one. On a pass
`certify` assembles the canonical seven-key verdict that
[`work-graph.md`](work-graph.md) already specifies, and no field is used for
something it does not mean:

| Tier field | Becomes | Because |
|---|---|---|
| `confirms` | `done` | asked for, and now true |
| `not_examined` | `not_verified` | present, and no check touched it |
| `findings` at `risk` | `blockers`, `can_continue_around: true` | found, judged survivable, named |
| `evidence` | `evidence`, prefixed with the tier | the command and what it printed |

`certify` runs the assembled verdict through the same `verdict_violations` gate
`close` will apply, so a certification cannot hand the run a verdict its own
consumer refuses.

## The commands

```bash
# three reports in, one verdict out — exits 1 if any tier failed
graph.py certify --node N-007 \
    --tier unit.json --tier seam.json --tier product.json

# unchanged, and still the only thing that moves the graph
graph.py close --verdict .task-pipeline/verdict-N-007.json
```

## The fix cycle, and its ceiling

A failing round **records itself and leaves the node open.** `certification` on the
node carries the round number, this round's three verdicts and the history of every
round — written on failure too, because a failing round that wrote nothing would
erase the only evidence that a node is churning.

The cycle is: `certify` → fail → the `breaks` findings become nodes (each already
carrying its `check`) → fix → `certify` again, round `N+1`. Same three tiers, same
blind dispatch. A tier that passed in an earlier round is **re-run**, because the
fix is a new change and the level it passed on is not the level it now faces.

**At the ceiling the gate measures rather than stops** —
[`loop-guard.md`](loop-guard.md). `--ceiling` defaults to 3. At or over it, `certify`
still runs and still reports the tiers; what it adds is the name of the tier that
has failed **every** round. A run spinning on one level needs the operator to see
*which* level:

- the same tier every round → the level is being misread, or the node is the wrong
  shape. Not one fix away. Re-plan the node, do not attempt round four.
- different tiers each round → churn across levels. Usually one requirement that
  was never decided, surfacing at whichever distance looks at it.

## What this costs, said out loud

Three agents per node instead of one. That is the price of the visibility, and it is
paid per node rather than per run. The three are dispatched in parallel, so the
wall-clock cost is roughly one reading; the token cost is three. A node whose
`check` is mechanical and whose blast radius is genuinely nil still pays it — and a
tier with nothing to find says so in `scope` and `not_examined` rather than being
skipped, because **a skipped level and a clean level are indistinguishable
afterwards**, and only one of them is evidence.

## Rationalizations

| Temptation | Why it is wrong |
|---|---|
| «All three would say the same thing» | Then all three say it, at a cost you already know, and the run has three signatures instead of one guess about what the other two would have found |
| «The seam tier can read the unit report first — it saves tokens» | It saves tokens by removing the second opinion. The reports are cheap; the independence is the product |
| «Tier 3 passed last round, skip it» | The fix is a new change. A tier's pass is about the tree it read, and that tree moved |
| «Round 4 will get it» | Read the ceiling's output. The same tier failing three times is a planning defect wearing a verification failure's clothes |
