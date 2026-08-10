# Routing measurement — results

Method: `evals/routing/render.py`. Ten queries, **one fresh agent per query**, holding
nothing but the competing skill descriptions and one user sentence.

> **Limits, stated before the numbers.** This measures the **descriptions'**
> discriminating power, not Claude Code's selection machinery, which sees more than a
> description. A subagent is fresh in *context*, not blind in *disposition* — this is
> **not** the multi-model blind run board row `B-002` asks for and no line here may be
> quoted as one. And see §3: **one sample per cell is too few**, which this measurement
> found out about itself by being run twice.

## 1. The three runs

| id | query | expected | **A** before | **B** after | **C** after + prod pair |
|---|---|---|---|---|---|
| AUD-01 | сделай аудит модуля оплат | task-pipeline | ✓ *(stretch)* | ✓ | ✓ |
| BUG-01 | проверь, нет ли ошибок в обработчике вебхуков | task-pipeline | **none** | ✓ | ✓ |
| PRD-01 | проверь, всё ли живо в проде после вчерашнего релиза | task-pipeline | **none** | **none** | **none** |
| PRR-01 | посмотри PR #24 и скажи, что там не так | task-pipeline | **none** | ✓ | ✓ |
| FEA-01 | добавь экспорт в CSV на страницу отчётов | task-pipeline | ✓ | ✓ | **none** |
| QST-01 | объясни, как наш auth middleware решает… | none | ✓ | ✓ | ✓ |
| TYP-01 | поправь опечатку в заголовке README | none | ✓ | ✓ | ✓ |
| SEO-01 | сделай аудит лендинга — почему упал трафик | seo-aeo-audit | ✓ | ✓ | ✓ |
| UXA-01 | проверь, что код соответствует UX-сценариям | ux-audit | ✓ | ✓ | ✓ |
| SKL-01 | проверь, соответствует ли этот скил стандарту | make-skill | ✓ | ✓ | ✓ |
| | | | **7 / 10** | **9 / 10** | **8 / 10** |

- **A** — `9f67dcd`, description 956/1024, before any edit.
- **B** — the findings clause added, description 1004/1024.
- **C** — `production check` given its Russian pair, description 1008/1024.

## 2. What is robust, and what is one sample

**Robust — the same result in both after-runs, for the stated reason:**

- **BUG-01 and PRR-01: `none` → `task-pipeline`, 2/2.** In A both agents *quoted this
  skill's own exclusion clause* as the reason they refused — *"matching task-pipeline's
  own exclusion 'Not for: … explaining or reading code'"*, *"task-pipeline's is scoped to
  'work changes the repository', not 'explaining or reading code'"*. In B and C both
  quote the new clause instead. The mechanism named in the refusal is the mechanism the
  change removed.
- **AUD-01's *reason* changed, 2/2.** It routed in A too — by stretching the build verb
  `hardening`, with nothing in the description naming an audit. In B and C it quotes
  `audit/аудит`. The answer did not move; the ground under it did.
- **PRD-01 never routed: 0/2 after.** Adding `/проверь прод` did not fix it. In C the
  agent said the request has *"no repository change and no matching trigger"* and
  reached for `checkup` before rejecting it. The production-check class is **named and
  still unreachable** — the vocabulary was necessary and is not sufficient.

**One sample, and therefore not a result:**

- **FEA-01 flipped to `none` in C** on reasoning that does not parse — *"no such change
  applies here because none of the listed skills is task-pipeline's own trigger"*. This
  is a control that passed in A and B with the same description clause C did not touch.
  Read as run-to-run variance, **not** as a regression caused by the edit — and the
  measurement as built cannot prove that reading, which is the point of §3.

## 3. The measurement's own defect, found by running it twice

**One agent per query cannot separate an effect from noise.** Three runs produced three
totals — 7, 9, 8 — and one of the moves between them (FEA-01) is almost certainly the
sampler, not the surface. Had the run stopped at B, this file would have reported
**9/10 and a clean win**, and the claim would have rested on single samples exactly like
the one that flipped.

What a next version needs, in order of value:

1. **N ≥ 3 per cell, majority-scored**, so a flip is visible as a split rather than a
   result. Cost scales linearly and the queries are tiny.
2. **The controls scored separately from the targets.** A false-positive control that
   flips is a different fact from a target that does not move.
3. **The reason recorded, not only the answer.** Every real finding in this file came
   from *why* an agent chose, not from what it chose — AUD-01 passed in A for a reason
   that was one rewording from failing.

Filed as a board row rather than fixed here: the run that needed the harness is the run
that found the harness too thin, and rebuilding it mid-run would leave the before-numbers
measured by a different instrument than the after-numbers.
