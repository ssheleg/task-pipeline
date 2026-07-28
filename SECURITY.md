# Security policy

## What this project is

`task-pipeline` ships **markdown doctrine plus two small installers**. There is no
server, no network client and no runtime service. The executable surface is:

| Surface | What it does |
|---|---|
| `bin/task-pipeline.js` | copies the skill directory into `~/.claude/` (zero dependencies) |
| `install.sh` | the same, in POSIX shell |
| `test/validate.py` | reads repo files and exits 0/1; run in CI |
| `.github/workflows/*.yml` | CI and the toggleable release job |

The skill's doctrine, however, is **instructions an agent will act on** inside your
repository — including running your test and lint commands and, at stage 7, your
deploy. Treat a change to `references/*.md` with the same care as a change to a
deploy script.

## Supported versions

The latest released version is supported. Fixes ship in a new release rather than
as patches to older tags.

## Reporting a vulnerability

**Do not open a public issue for a security problem.**

- Preferred: [GitHub private vulnerability reporting](https://github.com/ssheleg/task-pipeline/security/advisories/new)
  (Security → Report a vulnerability).
- Alternative: Telegram [@sshlg](https://t.me/sshlg).

Please include what you found, how to reproduce it, and the impact you see. You'll
get an acknowledgement within **72 hours** and a fix or a decision with reasoning
within **14 days** for anything confirmed. Coordinated disclosure is welcome — tell
me the timeline you'd like and I'll work to it.

## In scope

- The installers writing outside `~/.claude/skills/task-pipeline` and
  `~/.claude/commands/task-pipeline.md`, or overwriting files without `--force`.
- Anything in the shipped doctrine that would lead an agent to exfiltrate secrets,
  push to a repository the task never named, deploy without the operator's go, or
  bypass a gate that exists to require one.
- Command injection or path traversal through the validator or the workflows.
- A CI workflow that could be made to leak repository secrets.

## Out of scope

- The behavior of the AI agent that reads the skill. Agents are non-deterministic;
  a model ignoring an instruction is a doctrine-quality bug — please file it as a
  normal issue.
- Third-party companions (`super-ux`, `context7`, `obsidian-wiki`). Report those to
  their own maintainers.
- Anything requiring an attacker who already controls the operator's machine or
  their agent's configuration.

## Hardening notes for operators

- **Deploy authorization has a floor by design.** The pipeline treats deploy,
  publish and PR-opening as outward actions that need an explicit go, or a standing
  authorization that names the target *and* the preconditions. Do not record a
  blanket "do everything" in a brief — it is specifically rejected.
- **Writes to another repository are always proposal + PR**, never a direct push.
- The build stage keeps its scratch state in a git-ignored `.task-pipeline/`
  directory; confirm that directory is ignored before you run it in a repo with
  strict commit hooks.
