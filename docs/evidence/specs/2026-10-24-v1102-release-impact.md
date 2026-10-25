# Release impact: task-pipeline v1.102.0

schema: release-impact/1
release: v1.102.0
users: external
date: 2026-10-24

## 1. Who is affected and how

- **Segments:** every agent that runs task-pipeline from an install of this package: the operator's machines through sshlg-skills (Claude Code plugin, Codex plugin, skills CLI) and anyone who installs `task-pipeline-skill` from npm; the download count was not read for this card
- **What changes:** stage 7 now owes a release impact card before an outward act in a project with users, checked by `scripts/release_impact.py`; stage 8 watches the card's signals and records the outcome; `pipeline.json` gains the optional `release.users`; the repository's own validator reads a section's date from its heading and first block only (B-155)
- **Breaks for existing users:** no install or file format breaks; a run that releases a project with users without a card now reads NOT_RUN at stage 7, which is the intended new behaviour, and a project with no users declares `release.users: none`
- **Rollout:** all at once: npm publish, then the sshlg-skills pin, then `npx sshlg-skills update` on each machine
- **Timing:** 2026-10-24, right after v1.101.2, so the hub pins one version carrying both

## 2. Tracking

- **Signals:** the tag's release run conclusion; `npm view task-pipeline-skill version`; the hub's `update` readback (Claude verified, Codex current); new issues on ssheleg/task-pipeline
- **Baseline:** release runs green for v1.101.1; npm 1.101.1; `update` all green on hub 1.76.1 apart from Codex deferrals while Codex runs; 0 open issues on task-pipeline
- **Where:** `gh run list -R ssheleg/task-pipeline -b v1.102.0`; `npm view task-pipeline-skill version`; `npx --yes sshlg-skills@latest update`; `gh issue list -R ssheleg/task-pipeline`
- **Watch window:** 24 hours after the hub pins v1.102.0

## 3. Alerting

- **Fires when:** the release run fails, `update` reports task-pipeline failed or rolled back, or a new issue is opened on the repository
- **Receives:** the operator, by GitHub's email for failed runs and new issues; the agent running the release reads the run and the `update` result directly
- **Seen firing:** yes: release run attempt 1 for v1.101.1 failed on 2026-10-23 (B-156), and `update` reported PARTIAL on 2026-10-22 and 2026-10-24

## 4. Rollback or hotfix

- **Rollback:** re-pin task-pipeline 1.101.2 in sshlg-skills with a hub patch release, run `npx --yes sshlg-skills@latest update`, and `npm deprecate task-pipeline-skill@1.102.0` with the reason
- **Time to roll back:** about two hours (one hub release and one update on a loaded machine)
- **Data reversible:** yes: the release changes instructions and scripts only; cards written by runs stay as files in each project
- **Kill switch:** a project sets `release.users: none` in its `pipeline.json` and no card is owed there
- **Hotfix path:** a patch release v1.102.1 through the same `release_candidate.py` prepare, check and publish flow
- **Decision trigger:** roll back if, within 24 hours of the hub pin, `update` fails for task-pipeline or a run in a project without users is blocked by the card

## Outcome

- **Read:** 2026-10-24T06:35Z, the first reading after the hub pin (sshlg-skills 1.77.0): release run 40064387415 success; `npm view task-pipeline-skill version` 1.102.0; `npx --yes sshlg-skills@latest update` reports `task-pipeline: verified` for Claude, while Codex defers its move until no Codex process runs (the hub's generation-safety rule, not a failure); open issues on ssheleg/task-pipeline 0; no alert fired; the decision trigger did not fire
- **Read again:** 2026-10-25T20:30Z, after the window closed: the v1.102.0 release run still success; `npm view task-pipeline-skill version` 1.102.0; Claude installs 1.102.0, and Codex moved to 1.102.0 at 2026-10-25T20:26Z once no Codex process ran (`codex plugin list`: `task-pipeline@task-pipeline 1.102.0`); open issues on ssheleg/task-pipeline 0; no alert fired; the decision trigger did not fire
- **Result:** held
