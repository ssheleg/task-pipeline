# Design — the graph's ledger row states a measured lag

covers: REQ-001 REQ-002 REQ-003 REQ-004 REQ-005 REQ-006 REQ-007

## The problem, stated as the class it belongs to

`references/gates.md` → *False success* names the law: **an actor's own reply is
not evidence about the world**, and the test that separates a checked pass from a
silent one is *what does it print when it did not look?*

A build date is exactly that kind of reply. `built 2026-08-05` is true, self-reported
and says nothing about whether the graph describes the tree the run is about to
change. Twelve commits later it still reads `built 2026-08-05` — and reads *fresh*,
because a date without a comparison is a fact with no scale. The rationalization
table in `knowledge-graph.md` already anticipated half of this:

> "The graph is probably stale" → Then it has a build date and you can say so.
> Stale-and-dated is a finding; stale-and-unknown is what you get by not building one.

Stale-and-dated **is** better than stale-and-unknown. It is not yet a finding, because
nothing subtracts the date from today.

## The change, in one sentence

The `Fresh?` cell of the graph's ledger row stops carrying a date and starts carrying
a **measured distance from `HEAD`, the signal it was measured with, and — while that
distance is not zero — an explicit refusal to trust the graph for reach.**

## The three states — and why there are three

`gates.md` → *Progressive arming* already establishes that a mechanism with nothing to
look at must say so **distinctly** (`ok` / `dormant` / `skip` / `ERR`), because a state
that prints like success is how a mechanism reports a win it never checked. The same
applies here: `graph.json` carries `built_at_commit` **only when the caller passed it**,
and `graphify update` from the CLI does not pass it. So the honest design has three
states, not one, and each names its own signal:

| State | Condition | The `Fresh?` cell reads |
|---|---|---|
| **exact** | `built_at_commit` present and resolves in this checkout | ``built `3944593` — 12 commits / 2d behind HEAD, signal: built_at_commit (exact)`` |
| **approximate** | no `built_at_commit` in `graph.json` | ``built ≤ 2026-08-05T22:47Z — signal: file mtime (approximate; the graph carries no commit stamp, so this is a lower bound on the lag)`` |
| **unresolvable** | stamp present, does not resolve here (rebase, squash, shallow clone) | ``built `3944593` — UNRESOLVABLE in this checkout, signal: none — treat as stale until refreshed`` |

**Zero is stated, not omitted.** A current graph reads
``built `3944593` — current (0 commits behind), signal: built_at_commit (exact)``.
Printing nothing when the graph is fresh would make freshness indistinguishable from
a harvest that never looked — the exact failure this file cites `gates.md` for.

## The commands — so the number comes from git, not from judgement

`learned.md` rule 8 is *compute, never restate*. The doctrine therefore names the
commands rather than describing the intent:

```bash
git rev-parse --verify -q "<built_at_commit>^{commit}"   # which state applies
git rev-list --count "<built_at_commit>..HEAD"           # commits behind
git log -1 --format=%ct "<built_at_commit>"              # its timestamp → days behind
```

Three commands, no parsing, and the failure of the first one *is* the branch into the
third state rather than an error to handle.

## The distrust marker, and why it has no threshold

While the lag is anything other than `current`, the cell ends with
**`⚠ not trusted for reach until refreshed`**.

No threshold. `continuity.md` set the precedent when it refused a context-budget
number: an unmeasurable threshold becomes unconditional doctrine, not config. "Ten
commits is fine, eleven is not" is a number nobody can defend, and a number nobody can
defend is one every run argues its way under. One commit that moved the function the
task is about matters more than fifty that touched the README.

The marker does **not** block. Stage 0's gate is `manual` and this is a ledger row, not
a gate: it tells the harvest what it may lean on. The run continues; it just stops
quoting the graph as if it were current.

## Where it is enforced — both halves, by extending the sibling guard

`test/validate.py:1405` already carries this exact reasoning for stage 9:

> Shipping that doctrine while the surfaces that ENFORCE stage 9 say nothing about it
> is the same inert-gate failure … the file reads as law and the run never does it.

Standing instruction **R-003** requires running a fixed defect's definition against its
siblings. Stage 0 is the sibling: it *reads* the graph where stage 9 *refreshes* it, and
the same doctrine file ships both duties. So the guard is **extended** to cover stage 0
in both halves — `pipeline.example.json`'s stage-0 `gate.check` and `stages.md`'s stage-0
section — rather than copied into a second guard that would drift from the first.

## Rejected, recorded so it is not re-derived

- **A cadence mode (`always | major | manual`).** `major` produces a graph that is
  confidently wrong between releases, and the next run's harvest queries it first. The
  doctrine's whole argument is that a wrong doc gets argued with and a wrong graph gets
  believed; a mode that schedules wrongness is not a setting, it is the failure.
- **A shipped `templates/graph-staleness.sh`.** It would have to be seeded into a host
  project before it could run at the one stage that precedes seeding, and it adds a
  fourth file to the `npm test`-executed template contract for a three-command probe.
  Promotion to a script stays on the ladder with its trigger written down.
- **Blocking stage 0 on a stale graph.** The graph is *recommended, never required*
  everywhere else in this bundle; a blocking staleness check would make a graph that
  does not exist cheaper than one that is a week old.

## Self-review

- **Every check this design names is real:** `git rev-parse --verify`, `git rev-list
  --count`, `git log -1 --format=%ct` — all three run in this repo, and the worked
  example in the brief's ledger was produced by them.
- **Read back against the brief's `Decisions locked`:** D-1 (cadence untouched) — no
  section here changes stage 9. D-2/D-8 (compute) — the commands section. D-3 (no
  threshold) — stated with its precedent. D-4 (three states) — the table. D-5 (doctrine
  not script) — in *Rejected*. D-6 (extend the sibling guard) — in *Where it is
  enforced*. No decision is contradicted.
- **Read back against the alternatives stage 2 rejected:** all three are recorded above
  with the reason, not silently dropped.
- **Cost checkpoint, printed and not decided:** surfaces touched **7** (was 7 at intake,
  none discovered) · guards **95 → 97 expected** · REQ rows **13** (13 at intake).
  No growth to report; the operator's gate, not the agent's.
