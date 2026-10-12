# Release iteration — the loop around the waves

[`waves.md`](waves.md) closes one board in one release. This file is the loop around it:
**survey → design the next version → build in parallel → verify as each part lands →
document → release → check the release → show the operator the next pool → repeat.** A
project moves forward in whole releases. It does not move fix by fix.

Decided by the operator on 2026-10-12. The reason, in their words: a fix made alone
reproduces new defects and breaks earlier ones, and some fixes are already obsolete by the
time they land. Seeing every problem at once lets the next version solve them together.

## Contents

- No fix travels alone
- The cycle
- Module dossiers
- Integration, until it converges
- Question rounds — asked in batches, never blocking
- Verification starts when a node lands
- The token budget
- Release, then check the release
- The next pool
- The learning loop — every run reads what earlier runs learned
- What the operator sees, and when
- Rationalizations

## No fix travels alone

**A finding made mid-iteration joins the inventory. It is not fixed where it was found.**
A fix designed against today's state is the intermediate state that
[`waves.md`](waves.md) → *The rule it exists for* refuses: the next version moves the
seam, and the fix is then paid for twice. The finding gets an id in its owning register
and lands on a canvas node. Its wave decides when it is built.

**The hotfix lane is the only exception, and it is closed.** It has five entries:
- production is down;
- data is being lost or corrupted;
- a credential has leaked;
- a security hole is open to someone outside;
- money or a legal obligation is failing.

A hotfix is minimal and ships alone. Within the same hour its node joins the canvas. The
iteration then either designs the real fix or records the hotfix as final, with the
reason. "It is quick" is not one of the five entries.

## The cycle

| # | Step | Produces | Done when |
|---|---|---|---|
| 1 | Survey (wave 0) | audit agents per area, plus a harvest of every board → `<topic>-inventory.json` | every source in the ledger was read, and every finding has evidence and an id |
| 2 | Module dossiers | one dossier per cluster of items, written in parallel | every inventory item sits in exactly one dossier |
| 3 | Integration | the canvas of the next version ([`waves.md`](waves.md) → *The canvas*) | a pass changes no dossier, or the remaining conflict became a question |
| 4 | Question round | answers from the sources, then one batch to the operator | every question is answered, assumed, or blocks a named node |
| 5 | Plan | the work graph with waves, and one packet per node | every REQ lands on a node; [`planning.md`](planning.md)'s set comparison holds |
| 6 | Build | parallel agents, each owning disjoint files | each node is committed on its branch, with its own checks green |
| 7 | Verify | rounds per node, starting as each node lands | each node passes its risk class's rounds |
| 8 | Seam check | cross-module checks per seam group | every seam the canvas names is exercised end to end |
| 9 | Docs | stage 9 over everything the iteration shipped | the doc gate passes and the docs match the code |
| 10 | Release | versions, tags, pins, changelogs, in dependency order | the published artefacts resolve |
| 11 | Post-release check | the stage-8 trio on what was released | every item the release claims closed is checked on the released artefact |
| 12 | Next pool | the re-measured inventory and the proposal | the hand-back is sent |
| 13 | Retrospective | the project retro, plus the shared lesson store where one exists | written last ([`retrospective.md`](retrospective.md)) |

Steps 1–4 are stages 0–4 run once. Steps 6–8 are stages 5–8 per wave. Steps 9–13 are
stages 9–10 for the release. No gate in [`stages.md`](stages.md) is skipped. The cycle
changes when each stage runs, and over what.

## Module dossiers

**One dossier per cluster.** The inventory is grouped by the part of the system each item
touches, not by where it was found. One agent writes each dossier, all in parallel. A
dossier carries:
- the items it answers, by id;
- each module and contract as-is, and to-be;
- the options considered, with the choice and its reason;
- the contracts it changes, and who owns each side;
- the tests that will prove it, including one that fails today;
- the migration;
- what it deletes ([`waves.md`](waves.md) → *The canvas*, item 4);
- its open questions;
- its risk class.

**A dossier is a design, not a plan.** It does not cut waves. That is step 5, made once
over all the dossiers together.

## Integration, until it converges

The orchestrator lays every dossier onto the canvas and looks for two dossiers that change
one seam, one contract or one file. Each such pair is re-designed together: the two
agents, or one agent holding both dossiers.

**The pass repeats until it changes nothing**, capped at three passes. At the cap, the
conflict that remains becomes a question with both designs attached. Two designs left to
"meet in the build" are the intermediate state again.

## Question rounds — asked in batches, never blocking

**One queue:** `<artifacts>/specs/<topic>-questions.md`. Each row carries:
- an id;
- the node or nodes it blocks;
- who raised it;
- the sources tried, with citations;
- the recommended answer;
- the consequence of each answer.

**An agent that meets a question never waits on it:**
1. It closes the question from the sources if it can ([`waves.md`](waves.md) → *The
   questions*).
2. Otherwise it writes a row.
3. If the answer is internal and reversible, it proceeds on the recommendation, marked
   **assumed** on the node. Otherwise it parks the node `needs-operator`.
4. It takes another node.

**A round is called on the first of three triggers:**
- the whole frontier is blocked;
- five questions are open;
- a wave boundary is reached.

In a round, the orchestrator first re-closes from the sources, because a dossier or a
landed node may have answered the question since. The rest go to the operator as one
batch, each with its recommendation. Questions from peer sessions join the same queue.

## Verification starts when a node lands

**The checks are a pipeline, not a barrier.** A node is built when it is committed on its
branch with its own checks green. Its certification ([`certification.md`](certification.md))
starts at that moment, while other nodes are still being built. A wave never waits for
its slowest node before checking its fastest.

**The number of rounds follows the node's risk class.** The class is recorded on the node
as `risk`, computed from what the node touches. It is never lowered to save time.

| Class | Touches | Rounds |
|---|---|---|
| R1 | docs, config, a mechanical change, one isolated file | 1: the unit tier and the doc check |
| R2 | an ordinary feature or fix inside one module | 2: the blind tiers, then a re-read of the fix diff with its regression tests |
| R3 | security, cryptography, money, a data migration, a public contract, a seam across repositories, concurrency | 3: the first two, then an adversarial round that plants defects and tries abuse cases, on another model where one is available |

- Each round gets one fix cycle, inside [`loop-guard.md`](loop-guard.md)'s caps. A finding
  that cannot be fixed in the node is parked with a board row.
- R1 and R2 may stop early when a round finds nothing new. R3 always runs its adversarial
  round.
- Readers stay blind ([`certification.md`](certification.md) → *Blind*). Each reads the
  diff, the packet and the contract, never the builder's reasoning.

**Seam checks wait only for their seam group.** Nodes that share a seam are checked
together once the last of them lands. Nodes on other seams do not wait.

## The token budget

The method is cheap by construction. These rules keep it cheap:

- **The orchestrator holds the plan, not the work.** It reads each agent's structured
  output — findings JSON, eight-key verdicts — and never a transcript.
- **A packet is all the context an agent gets** ([`planning.md`](planning.md)): the node,
  the files it owns, the contracts, the exit criteria and the output schema. It gets no
  conversation history.
- **Diffs and their files, not repositories.** Ask the graph for reach
  ([`knowledge-graph.md`](knowledge-graph.md)) instead of sweeping with grep.
- **Machines first.** Tests, validators, schemas and linters run before any model reads
  anything. A model reviews only what they cannot decide.
- **An axis ends when its findings become restatements** ([`audit.md`](audit.md) → *Exit criterion — the part usually
  skipped*).
- **One agent per seam, not per file.** Keep the number in flight within the harness's
  size guideline and queue the rest.
- **An agent cut off by a rate limit or an outage is resumed with its context**, not
  relaunched from zero. Its output file is its checkpoint.

## Release, then check the release

**One release per iteration** carries every repository the iteration touched:
- versions, changelogs and tags;
- every pin moved, in dependency order — a contract before its consumers;
- every parent's submodule pointer ([`stages.md`](stages.md), stage 10).

**The release is checked in the same run.** Run stage 8's verification trio on what was
actually published, installed or deployed — never on the branch. Each item the release
claims closed is re-checked against the released artefact. A failure goes to the hotfix
lane if it is one of its five entries. Otherwise it goes to the next pool, with an id.

## The next pool

1. **Re-measure the inventory.** Items closed stay closed. Items open are re-checked
   against the code. New items join with ids: the post-release check's findings, peer
   requests, the operator's new asks.
2. **Re-prioritise** ([`prioritisation.md`](prioritisation.md)), then group by module the
   way the dossiers were grouped.
3. **Hand back once** ([`progress.md`](progress.md) → *The hand-back*). The message holds:
   - what the release shipped, with evidence;
   - what is still open, by module;
   - the proposed scope of the next iteration and its question batch.

The proposal is a recommendation. The next iteration starts on the operator's go, unless
a standing loop authorization is recorded ([`continuity.md`](continuity.md)).

## The learning loop — every run reads what earlier runs learned

**Every install has the first layer, and it needs no service:**
- the project's retro, read at stage 0 ([`retrospective.md`](retrospective.md));
- the shipped rule list in [`learned.md`](learned.md);
- the opt-in upstream publication (`retro.publish`), so the skill itself learns.

**Where the host has a shared lesson store, a second layer runs on top of the first.** An
Observatory or a Fabric estate is an example; the store is detected by the tools the
session lists, never assumed from a path.
- **Write, at step 13.** Each retro entry that is not private to the project is recorded
  as a *lesson*. A lesson carries:
  - its class, its trigger and the check that now catches it;
  - its evidence commit and its project's id.

  It never carries a transcript, a value, a private path or a person's name. It enters as
  a proposal, below full confidence, and the store's own rules decide who promotes it.
- **Read, at stage 0.** The harvest queries the store by the task's nouns: source 7b in
  [`knowledge-sources.md`](knowledge-sources.md). A lesson that fires is cited in the brief
  as `[lesson <id>]`, like any source.
- **Promote.** A lesson recorded by two or more projects is a candidate for
  [`learned.md`](learned.md), through `retro.publish`.

**When there is no store, the source ledger says so.** It prints `shared lessons:
absent`, and the first layer runs exactly as before. The store is never a hard dependency.

## What the operator sees, and when

An iteration has three planned touchpoints, plus every human gate:
1. **The planning gate** — the inventory summary, the canvas, the wave plan and the
   question batch, in one message ([`waves.md`](waves.md) → *How the stages map*).
2. **A question round** — only when one of its three triggers fires.
3. **The release hand-back**, with the next pool.

Sign-ins, consents, payments, sending to people and every outward or irreversible act stay
the operator's ([`waves.md`](waves.md) → *What stays human*).

## Rationalizations

| Excuse | Reality |
|---|---|
| "This bug is tiny, fix it now" | Tiny fixes are what move a seam twice. It joins the inventory, or it is one of the hotfix lane's five entries |
| "Wait for the whole wave, then verify" | A barrier idles every finished node. Each node is certified when it lands |
| "R3 found nothing in round 2, skip the adversarial round" | Round 3 asks a different question: it hunts for a planted defect. A clean round 2 does not answer it |
| "Ask the operator now, it is quick" | Each question is a human round. Queue it and take another node |
| "The agent hit a rate limit, start it again" | Resume it with its context. Relaunching pays for the same reading twice |
| "No Observatory here, so no learning loop" | The project retro and learned.md are the loop's first layer, and every install has them |
| "Release first, check later" | An unchecked release is the item the next iteration rediscovers. Step 11 is inside the run |
