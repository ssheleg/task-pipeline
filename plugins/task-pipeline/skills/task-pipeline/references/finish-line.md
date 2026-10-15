# The finish line — when an iteration stops

An iteration stops when the work it promised is done **on the artefact the operator uses**.
It does not stop when a search runs dry, because a search never does: every reading finds
something, every fix is new surface for the next reading, and find → fix → find has no end of
its own. This file is that end. The verdict is computed by `scripts/waves.py finish`.

## Contents

- The contract, fixed at intake
- Triage at discovery
- Rounds and the stop
- Computing the verdict
- Stop is not idle
- The finish block
- Rationalizations

## The contract, fixed at intake

The brief's `## Finish line` ([`../templates/brief.md`](../templates/brief.md)) carries five
fields, written at stage 0 and confirmed with the brief:

- **Objective** — one sentence: what is true when this iteration is done.
- **Exit checks** — REQ ids, each with its command, run on the artefact the operator uses:
  released, installed or deployed. A branch is not that artefact.
- **Scope** — the modules, paths and REQ ids this iteration may change, as a list.
- **Budget** — `run.finish.maxRounds` (default 3) and `run.finish.maxReleases` (default 2),
  from `pipeline.json` ([`../pipeline.schema.json`](../pipeline.schema.json)).
- **Base** — the commit the iteration started from.

Widening the scope is a recorded revision of the brief, with the operator's go. A finding is
not one.

## Triage at discovery

Every finding that reaches a round is classed when it is found, before anyone fixes it. First
match wins. A defect in a node's own diff, caught before the node closes, follows
[`review.md`](review.md) instead: Critical and Important block that node.

**Blocking**, when:
- **B1** — an exit check is red.
- **B2** — it is, or once released would be, a hotfix-lane entry. The list's single home is [`iteration.md`](iteration.md)
  → *No fix travels alone*; restated here, kept equal by the validator:
  - production is down
  - data is being lost or corrupted
  - a credential has leaked
  - a security hole is open to someone outside
  - money or a legal obligation is failing
- **B3** — the failing scenario passes at Base: this iteration broke it.
- **B4** — a REQ marked `verified`, or a claim this iteration publishes, is false on the
  artefact. A published claim beyond the REQs may instead be narrowed in the same change.

**Deferred** — real, with a receipt, and no B test matches. It becomes a board row with its
evidence, its priority inputs ([`prioritisation.md`](prioritisation.md)) and
`found-in: <iteration>`. It is not fixed now.

**Noise** — no reproducible receipt; a duplicate (append its evidence to the existing row); a
Minor with no behavioural consequence; or an environment transient named by its cause. One
ledger line, nothing else.

Severity words, effort and "it is a one-line fix" never change the class. Each finding leaves
one line in the run ledger ([`../templates/run.md`](../templates/run.md)):

```
finding: <id> — blocking:B<n> | deferred:B-NNN | noise — round <N> — base-repro yes|no|n/a
```

## Rounds and the stop

A **round** is every exit check run once, plus one independent reading over the Scope: an
audit axis, an observer, or the post-release readback. Rotating the axis
([`audit.md`](audit.md)) never adds a round. Only new blocking findings count.

- **Done** — every exit check green on the artefact, and two consecutive rounds with no new
  blocking finding. The second of them may read only the last fix's diff.
- **Diverging** — new blocking findings did not fall from one round to the next, or
  self-inflicted ≥ new. Run [`loop-guard.md`](loop-guard.md)'s break protocol.
- **Budget spent** — `maxRounds` or `maxReleases` reached before done: a blocker open, or the
  second clean round still owed. Stop and hand the iteration back: each open blocker becomes a
  top board row marked `needs-operator`. No round runs past the budget without the operator's
  go, given with the numbers; a done reached past it without that go is still `budget`.

The finish word is one of three: `done`; `budget`, the budget reached before done; `blocked`,
the rounds diverging, handed to the loop guard. Deferred findings never extend an iteration.

Each round leaves one ledger line, clean rounds included, because a clean round leaves no
finding to count:

```
round: <N> — <reading> — new blocking <k>
```

## Computing the verdict

```
python3 scripts/waves.py finish --inventory <inventory.json> --ledger .task-pipeline/run.md \
  --max-rounds 3 --max-releases 2 --releases <n> --checks <k>/<m> --artefact <name>@<sha>
```

`--rounds N` may stand in for `--ledger`; with neither the count is unknown and the script
refuses. Exit codes:

- `0` — done: the last two rounds found no new blocking item, none is open, and every exit
  check is green on the artefact.
- `3` — continue: a blocker open, a second clean round owed, or no `--checks` given.
- `5` — budget: reached before done, or done past it without `--operator-go`.
- `6` — blocked: diverging; run the loop guard's break protocol.
- `1` — malformed: the inventory, the ledger or the arguments, each reason named.

## Stop is not idle

Reaching the finish line closes the iteration. It does not end the work.

1. Close it: stages 9–10, the hand-back ([`progress.md`](progress.md) → *The hand-back*), the
   retrospective.
2. On an armed loop ([`continuity.md`](continuity.md)), take the highest-priority board row as a
   **new** iteration with its own contract. Choose by priority, not recency: the row found last
   is not next because it is fresh.
3. Re-opening a closed iteration to polish it is the loop this rule ends.

## The finish block

Printed at stage 10, beside the verdict, and in the hand-back's `FINISH` field:

```
finish: done | budget | blocked — rounds <n>/<max> — releases <n>/<max>
  exit checks: <k>/<m> green on <artefact>@<sha>
  blocking: <n> open · <n> fixed
  deferred: <n> → <ids, top priority first>
  noise: <n>
  known risks: <deferred rows at blast 3 or rung I4+, or none>
  next: B-NNN (new iteration) | board empty
```

## Rationalizations

| Excuse | Reality |
|---|---|
| "One more pass, it keeps finding things" | Every reading finds something. Only a new blocking finding argues for another round |
| "It is a one-line fix, do it now" | Effort never changes the class. A deferred finding is a board row |
| "This one is critical" | A severity word is not a B test. Name B1–B4, or defer it |
| "Rotate the axis and keep going" | Rotation happens inside the round budget, never on top of it |
| "The budget is nearly enough, one more round" | A round past the budget needs the operator's go, with the numbers |
| "The deferred list is long, so we are not done" | Deferred findings never extend an iteration |
| "Re-open the last iteration, it is nearly perfect" | That is the loop this rule ends. Take the top board row as a new iteration |
