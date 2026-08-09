# M6 — the cap that would have measured the wrong axis

Last module of the `audit-followup` programme. Branch `m6-learned-shape`, ships as a
minor.

## The premise, and what four measurements did to it

Written down as *"give `learned.md` a retirement rule, like the retro's"*. The retro
caps its standing instructions at ten and retires them on three triggers; the audit's
finding was that `learned.md` has neither and grows forever.

Four measurements, each with a differently-shaped command — the axis this programme
shipped one release ago, turned on its own backlog:

| # | The belief | The command | Result |
|---|---|---|---|
| 1 | rules accumulate | table rows per tag: 15 → 18 → 21 → 21 → 21 | **flat for four releases** |
| 2 | the file grows | words per tag: 2165 → 2987 → 3696 → 3919 | it does — see 3 |
| 3 | growth *is* rules | words per **section**, v1.23.0 → HEAD | **+223, every word of it in the binding map** |
| 4 | the long incidents duplicate the retro | each incident's distinctive tokens against the whole retro corpus (10 405 words) | **zero hits** — the incidents are other projects' events; this repo's retro never held them |

A cap of N would have fired on the axis that has not moved in four releases. A word
budget would have cut the incidents — 1940 words, 49.5% of the file — which
measurement 4 shows are the **only** record of those events anywhere in this
repository.

**The finding was right that something was missing. It was wrong about what.**

## Why the retro is capped and this file is not

The asymmetry is already in the doctrine, unstated as a reason:

- `retrospective.md` — *"A file that is read **in full** every run"* must be bounded by
  construction. `knowledge-sources.md` source 7: read in full, not queried, capped at
  ten.
- `learned.md` is **never read in full**. It is reached by citation from 23 surfaces,
  and its own binding map routes each stage to the rules that bind it.

A cap belongs to the file you must finish reading. A file you enter through an index
needs its index to be right, not its length to be short. Nobody had written that
down — which is why the proposal came back, and why it is written down here.

## REQ

| # | Requirement | Verified by |
|---|---|---|
| R1 | `learned.md` states **why it has no cap**, with the measurement, next to the retirement rules it *does* get | the section exists; `npm test` green |
| R2 | Two retirement triggers that fit a **lesson** rather than an instruction: the conditions can no longer occur in any project the skill runs on, or the rule is **subsumed** — a merge, where the absorbing rule names the absorbed one so the binding map keeps working | doctrine states both; a deletion without a logged line fails |
| R3 | Every rule deletion is logged as one line, the same discipline as the retro's prune | guard over the prune log |
| R4 | The file's **shape** is printed beside the validator's verdict as a disclosure — rules, incidents, incident words, binding rows. No floor, no direction, **never a target** | the shape line prints; the numbers are computed, never restated |
| R5 | Each new guard is proven against a planted defect | `npm run test:negatives` |

## Out of scope

- A cap, a budget, or any target on any of the four numbers. Measurement 3 is the
  argument: the growth is in the section that makes a rule **reachable**, and shrinking
  that is shrinking the index of a file nobody reads end to end.
- Trimming the incidents. Measurement 4 makes that a deletion, not a compression.

## The numbers this module ships with

Re-derived on the branch commit, not carried from the note that proposed the module:

```
rules=21  incidents=18  incident_words=1940  binding_rows=16  total_words=3919
```
