# The consilium: a council of models judges, the strongest rules last

The operator, 2026-11-23 (requests `6f5b7054`, `62e0c402`): «консилиум сделать дефолтным вообще в нашем pipeline:
когда мы оцениваем, консилиум моделей, и финальные самые сильные … даже если она за токены, то финальное консилиум
решение выносит она». One model's opinion is a draft of a judgement, not a judgement.

## When it sits

By default, from size M up: the verification of a spec (stage 3), a choice between designs (stage 2, `decide`), the
plan of an L task (stage 4), a `judgment` gate with no person named, the acceptance of an L or outward task (stage
10), any delegated pick. Size S keeps one validator ([`spec-protocol.md`](spec-protocol.md)). A host may be
stricter, never looser.

## How a round runs

1. A blind panel: each panelist reads only the artefact and the brief, through its own lens, and answers a verdict,
   a score and findings with the exact change.
2. The judge, the strongest model of the host's map, reads the panel anonymised; accepts or rejects every finding
   with a reason and adds what all missed. A reason binds, a majority does not. A pass leaves no accepted blocker or
   major finding.
3. The author applies the ruling and records each accepted finding in the decision table.

`scripts/consilium.py review|decide` runs a round and writes `round-N/` (each verdict, `judge.json`, `ledger.json`,
`summary.md`); `consilium.py check DIR --round N` is the gate: at least three verdicts of three families, a parsable
ruling, spend within the cap.

## Panel, judge, money

Configuration, never code ([`model-tiering.md`](model-tiering.md), *Roles and money*): `--config`,
`$TASK_PIPELINE_CONSILIUM`, the host file `~/.config/task-pipeline/consilium.json`, else the shipped template
([`assets/consilium.example.json`](../assets/consilium.example.json)), whose placeholders the script refuses to call.
Validators answer by tokens, one call each (a lost reply retried once); a panelist with `"route": "subscription"` is an agent of
the session whose verdict comes in by `--import ID=FILE`. The map's strongest model judges, by tokens.
The author never sits on its panel. People's text goes only to models the map allows. Each round has a cap
(`max_usd_per_round`, the round's whole spend); over it the judge is skipped. Every call lands in the spend ledger
(`--task`).

## Rounds

Two; a third only for an accepted blocker or major finding left, never on unchanged input. After round 3 what is
open goes to the operator as one question with the judge's default, or to the backlog.

## What it is not

Not an authorisation (outward or paid acts stay `manual`), not a measurement, not the author
([`model-tiering.md`](model-tiering.md)). A failed judge is rerun alone with `--judge-only`.
