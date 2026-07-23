# Model tiering

A **reminder**, not a hard block. Not every environment has every model — if you
lack one, keep your current model; the pipeline still runs.

| Stages | Recommended | id |
|---|---|---|
| 0–4 (intake grill, docs, brainstorm, spec, plan) | Fable 5 | `claude-fable-5` |
| 5–6 (subagent dev, tests) | Opus 4.8 | `claude-opus-4-8` |
| 7–9 (lint/deploy, logs, docs) | inherit current | — |

## Mechanic

At each stage boundary compare recommended vs current. If they differ, emit:

> ⏸ **Stage N (`<name>`) recommends `<model>` (`<id>`).** You're on `<current>`.
> Switch: `/model <id>` — then say "continue". *(Reminder only.)*

## Why manual

A skill runs inside the current context; it **cannot change the main-loop model**.
Only the operator can, via `/model` (or `/fast`). The stages that most benefit from
Fable (0–4) are interactive anyway (stage 0 is a live grill), so the operator is
present to switch.

Stage 5 spawns subagents; those **are** pinned to Opus by the orchestrator via the
`Agent` / `Workflow` model override — no operator action needed for subagents.

## Override

Set your own map if your task warrants it (e.g. a heavy design needs Opus at
stage 2). The recommendations are defaults, not rules.
