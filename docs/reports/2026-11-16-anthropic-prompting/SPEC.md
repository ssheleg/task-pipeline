# Overall spec: task-pipeline's prompts, to Anthropic's current practices

Date: 2026-11-16. Owner: this repository. Checklist: [`README.md`](README.md)
(P-01..P-14). Component specs: [`specs/`](specs/).

## Objective

Every file of the pipeline an agent loads says what done looks like, names the stops it
wants and the four it does not, carries no history, keeps emphasis for what a reader must
not miss, and treats pasted and fetched text as data. The gates, the kernel, the verifier
tiers and every script contract keep their behaviour: this work changes how the doctrine
is said, not what it requires.

## Component specs

| Spec | Components |
|---|---|
| [`specs/entry-and-grill.md`](specs/entry-and-grill.md) | SKILL.md, `/task-pipeline`, stage 0, grill, intake split, knowledge sources, doctrine map |
| [`specs/stages-and-gates.md`](specs/stages-and-gates.md) | stages, gates, stage details, finish line, residue, loop guard, certification, learned, acceptance, build, planning, spec, review, tdd |
| [`specs/modes.md`](specs/modes.md) | `waves`, `iteration`, `setup`, `checkup`, continuity, progress (hand-back) |
| [`specs/agents.md`](specs/agents.md) | the eight subagents and the five tier asset copies |
| [`specs/evidence-docs-and-project-audit.md`](specs/evidence-docs-and-project-audit.md) | evidence-docs, project-audit, `/project-audit` |
| [`specs/hub-routing-and-hooks.md`](specs/hub-routing-and-hooks.md) | the hub's routing block and session note (sshlg-skills), the plugin's hook messages |

## Waves

| Wave | Content | Repository | Exit check |
|---|---|---|---|
| W0 | Prompt lint and ratchet in `npm test`; this report | task-pipeline | `npm test` green (done: commit a8c6686) |
| W1 | The run contract: SKILL.md Done when / Stop only when / Not a stop and glossary; the grill's unconditional stop fixed and P-14 line; `continuity.md` "what is not a stop" with the cap of three continuations; the fifteen unwanted stops rewritten; `/task-pipeline` mode finish lines and the checkup pointer; `unwanted-stop` lint rule | task-pipeline | `npm test` green; `grep -rn "confirms the brief"` shows only the new wording; lint rule selftest |
| W2 | The eight subagents and their asset copies: descriptions, common skeleton, "read only your report", Done when, `Write` for the testers | task-pipeline | `npm test` (host-portability, graph, design gate) green |
| W3 | Hand-back order (blocked on you first); evidence-docs and project-audit descriptions, Done when / Stop only when, P-14 line, close order; `/project-audit` command corrected | task-pipeline | `npm test` and `test:audit-regressions` green |
| W4 | History removed from loaded files where no test pins it; capitals softened where no test pins them; lint rebaseline lowered | task-pipeline | `prompt_lint.py rebaseline` lowers every changed metric |
| W5 | Release: version, CHANGELOG, PR, merge, tag, published package, hub pin, local install update | task-pipeline, sshlg-skills | release run green; `npm view task-pipeline-skill version`; installed bytes match |
| H0 | Blocker: the hub's tests write fixture text into the operator's routing block; isolation fix and guard; recovery of the three routers with `--adopt` | sshlg-skills | sentinel guard test; `grep -c "Пакетный текст\|ux body\|copy body" ~/.claude/CLAUDE.md` prints 0 |
| H1 | The task-pipeline router text, the session note, the family preamble | sshlg-skills | hub `npm test`; three `routers --update` runs hash-equal |

Out of this unit, filed as board rows with evidence: the incident archive
(`references/incidents.md`), splitting the stage 0 and stage 10 gate bullets, the
`lessons.py` internals out of `iteration.md`, reordering stage 0's phases, the design
destination as its own reference, the waves script mechanics out of `waves.md`, plugin
hook message rewording.

## Risks across the waves

- Tests pin exact text in many files; every removal is grepped against `test/` first and
  every wave ends on a full `npm test`.
- Five tier agents have byte-equal asset copies; they are edited together.
- The hub writes into operator files; only its own `--adopt` path replaces authored text,
  and only for the three entries proven to be fixtures.

## Done when

W0-W5 and H0-H1 have their exit checks green, the deferred rows are on the board, the
installed plugin and hub match the released versions, and sessions can be reloaded.
