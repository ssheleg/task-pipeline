# Evaluation results

**Status: trigger cases executed blind on three models on 2026-08-31; scenario
lines remain unexecuted.**

CI proves that the files are shaped correctly and that the validator catches a
planted invalid trigger class. It does not run an agent session. The rows below
were produced by the wave-3 subagent protocol: for each query, one FRESH
general-purpose subagent per model received the query verbatim, the family's 28
skill names-with-descriptions (built from the members' SKILL.md frontmatters),
and the instruction to answer with one skill name or `none`. Limits, stated:
the subagents run inside a Claude Code harness whose own installed-skill
inventory is also visible to the model — a live coexistence environment, not a
cleanroom — and a `hit` on a should_trigger case means the model NAMED
task-pipeline, not that a full session loaded and obeyed it. Scenario lines
need a full interactive run and are recorded as not reproducible from this
harness rather than guessed.

| Date | Version | Model | Trigger pass rate (train / validation) | Scenario lines passed | Installed alongside | Notes |
|---|---|---|---|---|---|---|
| 2026-08-31 | v1.80.0 | haiku | 6/6 / 6/6 | not run — needs a full interactive session | the ssheleg family, 28 skills (evidence-docs, project-audit, super-ux ×7, sheleg-design, sheleg-dev ×7, agent-stack ×4, telegram-dev ×3, seo-aeo-audit, agent-sync, make-skill) | blind subagent protocol; all 12 trigger cases hit |
| 2026-08-31 | v1.80.0 | sonnet | 6/6 / 6/6 | not run — needs a full interactive session | same 28-skill family list | blind subagent protocol; all 12 trigger cases hit |
| 2026-08-31 | v1.80.0 | opus | 6/6 / 6/6 | not run — needs a full interactive session | same 28-skill family list | blind subagent protocol; all 12 trigger cases hit |

