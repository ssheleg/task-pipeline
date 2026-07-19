# task-pipeline

Full-cycle task delivery pipeline orchestrator for **Claude Code**. One skill that
runs any substantial task through **9 gated stages** — built on the
[superpowers](https://github.com/obra/superpowers) skills.

## What it does

`docs study → brainstorm → spec → plan → subagent build → tests → lint/deploy →
post-deploy log check → docs/wiki sync`

Each stage gates the next; each names the model to use.

| # | Stage | Model | Gate | Type |
|---|---|---|---|---|
| 1 | Docs study | Fable | contracts grounded on current docs | auto |
| 2 | Brainstorm | Fable | design approved | manual |
| 3 | Spec | Fable | committed + reviewed | manual |
| 4 | Plan | Fable | parallel-ready, DoD per task | auto |
| 5 | Dev | Opus | tasks DONE, TDD green per task | auto |
| 6 | Tests | Opus | full suite green, new code covered | auto |
| 7 | Lint + deploy | host | lint clean + suite green before deploy | manual |
| 8 | Post-deploy | host | clean boot / honest degradation | auto |
| 9 | Docs + wiki | host | docs + wiki synced | auto |

## Prerequisite

**superpowers** — https://github.com/obra/superpowers

```
/plugin marketplace add obra/superpowers
/plugin install superpowers@superpowers
```

## Install

**Plugin (recommended):**
```
/plugin marketplace add ssheleg/task-pipeline
/plugin install task-pipeline@task-pipeline
```

**Plain skill:**
```
git clone https://github.com/ssheleg/task-pipeline
cd task-pipeline && ./install.sh
```
(copies the skill into `~/.claude/skills/task-pipeline` and the `/task-pipeline`
command into `~/.claude/commands/`)

## Use

Say *"run this through the pipeline"* / *"полный цикл"* / *"прогони по конвейеру"*,
or `/task-pipeline`. The skill creates a per-stage TaskList and walks the gates.

## Model tiering

Stages 1–4 → Fable, stages 5–6 → Opus, 7–9 → inherit. **Reminders only** — a skill
can't switch the main-loop model; `/model` is the operator's. Stage-5 subagents are
pinned to Opus automatically.

## Configuration (`pipeline.json`)

A pipeline is a machine-readable config. The framework ships the **contract** —
`plugins/task-pipeline/skills/task-pipeline/pipeline.schema.json` — and a copy-and-rewrite **example**,
`pipeline.example.json` (which happens to encode this plugin's own default flow). It imposes no
specific stages, skills, or gate assignments. Two generic knobs, per the schema:

- **Bring your own skills / stages.** Copy `pipeline.example.json` → `pipeline.json` for the project
  you're running and rewrite it: its own stages (any count), each executed by your own skills/agents
  via `skills[]`. Validate against `pipeline.schema.json`.
- **Typed gates.** Each `gate` has a `type`: `auto` (the orchestrator verifies the `check` itself,
  pass/fail) or `manual` (it waits for your explicit go). Which stages are manual vs auto is your
  config, not the plugin's opinion.

```jsonc
{ "id": 5, "state": "dev", "model": "claude-opus-4-8",
  "skills": ["superpowers:using-git-worktrees", "superpowers:subagent-driven-development"],
  "gate": { "type": "auto", "check": "all plan tasks DONE; full test suite green" } }
```

## Portability

Stages 6–9 read the host project's `CLAUDE.md` conventions (tests / lint / deploy /
docs / wiki) with detection fallbacks, so the skill works in any repo.

## License

MIT © 2026 ssheleg.
