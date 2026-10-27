# Release impact: task-pipeline v1.102.3

schema: release-impact/1
release: v1.102.3
users: external
date: 2026-10-27

## 1. Who is affected and how

- **Segments:** every agent that runs task-pipeline from an install of this package: the operator's machines through sshlg-skills (Claude Code plugin, Codex plugin, skills CLI) and anyone who installs `task-pipeline-skill` from npm; the download count was not read for this card
- **What changes:** `retro_budget.py migrate` shortens an over-long stamp row in its own table's shape (column count kept, date, commit and version cells whole, prose capped evenly, pointer at the end of the last cell) and merges a floor's several `Rotated out:` lines into one per archive quarter; `hooks/build-gate.sh` and `memory-nudge.sh` also fire on Codex's `apply_patch`; SKILL.md's `## Triggers` names three more phrases (write tests, cut a release, remove dead code) with the description unchanged
- **Breaks for existing users:** nothing that worked before: a migrated row's text differs from 1.102.2's shortening (the archive keeps the original verbatim either way), and a Codex session in a project whose run has not entered its build stage is now asked before editing product files, which is the gate's documented behaviour on Claude Code
- **Rollout:** all at once: npm publish, then the sshlg-skills pin, then `npx sshlg-skills update` on each machine
- **Timing:** 2026-10-27, with the hub's board waves of the same day

## 2. Tracking

- **Signals:** the tag's release run conclusion; `npm view task-pipeline-skill version`; `retro_budget.py check` and `verify` on the hub's and the members' retros after the pin; new issues on ssheleg/task-pipeline
- **Baseline:** v1.102.2 release run 40245813429 success; npm 1.102.2; this repository's own retro floor within budget with every pointer verified; 0 open issues on task-pipeline
- **Where:** `gh run list -R ssheleg/task-pipeline -b v1.102.3`; `npm view task-pipeline-skill version`; `python3 plugins/task-pipeline/skills/task-pipeline/scripts/retro_budget.py verify --retro docs/evidence/retro.md`; `gh issue list -R ssheleg/task-pipeline`
- **Watch window:** 24 hours after the hub pins v1.102.3

## 3. Alerting

- **Fires when:** the release run fails, `retro_budget.py verify` reports an unproved pointer on a floor this release migrated, a Codex session reports the build gate asking inside the build stage, or a new issue is opened on the repository
- **Receives:** the operator, by GitHub's email for failed runs and new issues; the agent running the release reads the run and the checks directly
- **Seen firing:** yes: release run 40241842429 for v1.102.1 failed on 2026-10-25 and was read the same night

## 4. Rollback or hotfix

- **Rollback:** re-pin task-pipeline 1.102.2 in sshlg-skills with a hub patch release, run `npx --yes sshlg-skills@latest update`, and `npm deprecate task-pipeline-skill@1.102.3` with the reason
- **Time to roll back:** about two hours (one hub release and one update on a loaded machine)
- **Data reversible:** yes: `migrate` keeps every moved row verbatim in the archive under its sha256, and a retro is a Git-tracked file
- **Kill switch:** remove `apply_patch` from the two matchers in `hooks/hooks.json`; `migrate` runs only when an agent calls it
- **Hotfix path:** a patch release v1.102.4 through the same flow
- **Decision trigger:** roll back if, within 24 hours of the hub pin, `verify` fails on a floor this release migrated or the build gate asks inside a build stage
