# Skill card — task-pipeline

**What a reviewer needs before deploying this skill, in one page.** The fields are
the registry entry Anthropic's [Skills for enterprise](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise)
guidance asks every organisation to keep, plus an honest pass over its risk-tier
table. Written so somebody who did not build this can decide, not so it looks
harmless.

## Registry entry

| Field | Value |
|---|---|
| **Purpose** | Runs a substantial task through ten gated delivery stages — intake grill, docs study, brainstorm, spec, plan, subagent build, tests, lint/deploy, post-deploy, docs+registers, acceptance — refusing to advance until each gate passes |
| **Owner** | ssheleg ([github.com/ssheleg/task-pipeline](https://github.com/ssheleg/task-pipeline)) |
| **Version** | 1.8.1 |
| **Surface** | Claude Code (filesystem skill + plugin) and the vercel `skills` CLI. **Not** uploaded to the Skills API; custom Skills do not sync across surfaces |
| **Dependencies** | None required. Optional: `context7` (MCP), `figma` (MCP), super-ux, agent-sync, graphify, obsidian-wiki. Every stage's doctrine ships in-repo; the one conditional requirement is super-ux for the stage-3 UX track on a user-facing task |
| **Evaluation status** | Suite authored (13 evals, 5 categories). **Never executed** — see [`evals/RESULTS.md`](evals/RESULTS.md) |

## Risk-tier disclosure

Every indicator from the enterprise risk table, answered — including the ones that
apply.

| Indicator | Applies? | What exactly |
|---|---|---|
| **Code execution** | **Yes — High** | Ships `templates/docgate.sh` (seeded into the host project as its documentation gate), `bin/task-pipeline.js` and `install.sh` (installers), `test/*.py` and `evals/run.py` (repo checks). None run automatically; the gate is seeded and run by the host project |
| **MCP server references** | **Yes — High** | Instructions name `context7`, `figma`, `graphify`, `wiki-query`, `wiki-update`. All optional; absence degrades a stage, never blocks one, except super-ux on a UI task |
| **Tool invocations** | **Yes — Medium** | Instructs bash (git, test runners, the host's lint/deploy commands), file reads and writes, and a `PreToolUse` hook example that runs the docs gate before a commit |
| **Filesystem access scope** | **Yes — Medium** | Reads and writes inside the host project: `docs/`, `scripts/check-docs.sh`, `.task-pipeline/` scratch, `CONTEXT.md`. Stage 5 creates and removes git worktrees. Writing to **another repository** is treated as outward and requires an explicit go |
| **Instruction manipulation** | No | Nothing instructs Claude to bypass safety rules, hide actions, or behave conditionally on hidden inputs. Outward and irreversible actions (deploy, publish, PR, editing a shared design file) explicitly require operator authorization |
| **Network access patterns** | Minimal | No `curl`/`fetch`/`requests` in shipped code. The doctrine tells the agent to fetch **library documentation** at stage 1 and to re-fetch the hook contract; both are reads of vendor docs, named in the text |
| **Hardcoded credentials** | No | None. Release automation uses repository secrets in CI, never files in the skill |

## What to check before you trust it

1. Read `SKILL.md` and the 23 files under `references/` — that is the whole
   instruction surface, and every one is linked directly from `SKILL.md`.
2. Read `templates/docgate.sh` before seeding it; it is the only shipped script a
   host project will run on its own repository.
3. Run `npm run test:all` — 53 guards, each with a negative self-test that plants a
   defect and requires rejection.
4. Run `python3 evals/run.py` for the behavioural protocol, and read
   `evals/RESULTS.md` for what has actually been observed.

## Posture, stated rather than implied

- **Separation of duties is not in place.** The author and the reviewer are the same
  person. The enterprise guidance asks for separation; a consumer should treat this
  repository's own review as an author's self-review and do their own.
- **Commits are unsigned**, so provenance rests on GitHub account control rather than
  cryptographic signature. Integrity verification by checksum is possible today
  (`npm pack` / tag archives) and is not automated.
- **Versions are pinned by git tag** and mirrored into `sshlg-skills`'s catalogue.
  Rollback is `git checkout v<previous>` or pinning the previous plugin version;
  the previous version is never deleted.
- **Behavioural evidence is missing, not merely thin.** 53 structural guards prove
  the skill is well-formed. Until `evals/RESULTS.md` carries a dated run, nothing in
  this repository proves it *behaves* — triggers correctly, stays quiet on a
  question, or performs the steps it documents.
