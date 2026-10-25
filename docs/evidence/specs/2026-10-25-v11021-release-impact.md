# Release impact: task-pipeline v1.102.1

schema: release-impact/1
release: v1.102.1
users: external
date: 2026-10-25

## 1. Who is affected and how

- **Segments:** every agent that runs task-pipeline from an install of this package: the operator's machines through sshlg-skills (Claude Code plugin, Codex plugin, skills CLI) and anyone who installs `task-pipeline-skill` from npm; the download count was not read for this card
- **What changes:** the three skills' front-matter descriptions shrink to the family's 300-character budget (hub board row B-255 (a)): task-pipeline 388 to 294, project-audit 401 to 295, evidence-docs 397 to 283 (hub measure). No doctrine, script or file format changes; the full trigger lists stay in each SKILL.md's `## Triggers`
- **Breaks for existing users:** nothing breaks; routing could change only if a host chose a skill from description words that left the description, and those words remain in the body the family routing hook matches
- **Rollout:** all at once: npm publish, then the sshlg-skills pin, then `npx sshlg-skills update` on each machine
- **Timing:** 2026-10-25, with the other family members' description trims, so the hub pins them in one release

## 2. Tracking

- **Signals:** the tag's release run conclusion; `npm view task-pipeline-skill version`; the hub's `node test/route_coverage.js` and `node test/triggers_test.js` on the pinned tree; new issues on ssheleg/task-pipeline
- **Baseline:** v1.102.0 release run success; npm 1.102.0; route coverage 125 named an expected route, 0 spoke where silence was right, of 140 prompts; triggers_test 70 checks OK; 0 open issues on task-pipeline
- **Where:** `gh run list -R ssheleg/task-pipeline -b v1.102.1`; `npm view task-pipeline-skill version`; `node test/route_coverage.js` in sshlg-skills; `gh issue list -R ssheleg/task-pipeline`
- **Watch window:** 24 hours after the hub pins v1.102.1

## 3. Alerting

- **Fires when:** the release run fails, the hub's route coverage or trigger suite drops on the pinned tree, `update` reports task-pipeline failed, or a new issue is opened on the repository
- **Receives:** the operator, by GitHub's email for failed runs and new issues; the agent running the release reads the run and the hub suites directly
- **Seen firing:** yes: release run attempt 1 for v1.101.1 failed on 2026-10-23 (B-156)

## 4. Rollback or hotfix

- **Rollback:** re-pin task-pipeline 1.102.0 in sshlg-skills with a hub patch release, run `npx --yes sshlg-skills@latest update`, and `npm deprecate task-pipeline-skill@1.102.1` with the reason
- **Time to roll back:** about two hours (one hub release and one update on a loaded machine)
- **Data reversible:** yes: the release changes three description strings only
- **Kill switch:** none needed beyond the re-pin; the descriptions are text
- **Hotfix path:** a patch release v1.102.2 restoring a description word through the same flow
- **Decision trigger:** roll back if, within 24 hours of the hub pin, the hub's route coverage loses a prompt it named before or `update` fails for task-pipeline
