# Routing measurement — results

Method and its limits: `evals/routing/render.py`. Ten queries, one fresh agent each,
holding nothing but the competing skill descriptions and one user sentence. **This
measures the descriptions' discriminating power, not Claude Code's selection machinery,
and a subagent is fresh in context rather than blind — it is not the multi-model blind
run `B-002` asks for and may not be quoted as one.**

## Before — `9f67dcd` (v1.38.0), description 956/1024

| id | query | expected | answered | |
|---|---|---|---|---|
| AUD-01 | сделай аудит модуля оплат | task-pipeline | task-pipeline | ✓ *(see note)* |
| BUG-01 | проверь, нет ли ошибок в обработчике вебхуков | task-pipeline | **none** | ✗ |
| PRD-01 | проверь, всё ли живо в проде после вчерашнего релиза | task-pipeline | **none** | ✗ |
| PRR-01 | посмотри PR #24 и скажи, что там не так | task-pipeline | **none** | ✗ |
| FEA-01 | добавь экспорт в CSV на страницу отчётов | task-pipeline | task-pipeline | ✓ |
| QST-01 | объясни, как наш auth middleware решает… | none | none | ✓ |
| TYP-01 | поправь опечатку в заголовке README | none | none | ✓ |
| SEO-01 | сделай аудит лендинга — почему упал трафик | seo-aeo-audit | seo-aeo-audit | ✓ |
| UXA-01 | проверь, что код соответствует UX-сценариям | ux-audit | ux-audit | ✓ |
| SKL-01 | проверь, соответствует ли этот скил стандарту | make-skill | make-skill | ✓ |

**7 / 10.** The three misses are the three the board row predicted, and each agent
**quoted the exclusion clause as its reason** rather than failing to find a match:

- BUG-01 — *"matching task-pipeline's own exclusion 'Not for: … explaining or reading code'"*
- PRD-01 — *"it fails task-pipeline's own scope test — 'Not for: …'"*
- PRR-01 — *"none of the descriptions offers a phrase for reviewing a PR's changes — task-pipeline's is scoped to 'work changes the repository', not 'explaining or reading code'"*

**Note on AUD-01 — a right answer from a wrong premise.** It routed, and its stated
reason was the build-verb list: *"a hardening/audit task"*. Nothing in the description
named an audit, so the answer rests on stretching `hardening`. Counted as a pass because
the measurement counts answers, and recorded here because a pass that depends on a
stretch is one rewording away from becoming a miss.
