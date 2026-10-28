# Release impact: task-pipeline v1.102.4

schema: release-impact/1
release: v1.102.4
users: external
date: 2026-10-28

## 1. Who is affected and how

- **Segments:** every agent that runs task-pipeline from an install of this package: the operator's machines through sshlg-skills (Claude Code plugin, Codex plugin, skills CLI) and anyone who installs `task-pipeline-skill` from npm; the download count was not read for this card
- **What changes:** the three Bash hooks start fewer processes per Bash call: 3 instead of 18 in a project with no `.task-pipeline/run.md`, 11 instead of 23 with a run in flight (PID delta, minimum of 25 runs). `release-gate.sh` tests for the ledger before reading stdin or starting python3 and splits its verdict in the shell; `gate-observer.sh` reads stdin after its ledger test; `memory-nudge.sh` finds its scripts directory without `cd` and `dirname`
- **Breaks for existing users:** nothing that worked before: a differential run of the 1.102.3 and 1.102.4 hooks over 4,950 cases gave the same exit code, stdout, stderr and ledger contents in every case
- **Rollout:** all at once: npm publish, then the sshlg-skills pin, then `npx sshlg-skills update` on each machine
- **Timing:** 2026-10-28, with the hub's board waves of the same day

## 2. Tracking

- **Signals:** the tag's release run conclusion; `npm view task-pipeline-skill version`; a release refused or allowed differently from its ledger in a project running a pipeline; new issues on ssheleg/task-pipeline
- **Baseline:** v1.102.3 release run 40528794932 success; npm 1.102.3; `test/release_gate_test.py` 71 checks green on 1.102.3; 0 open issues on task-pipeline
- **Where:** `gh run list -R ssheleg/task-pipeline -b v1.102.4`; `npm view task-pipeline-skill version`; `python3 test/release_gate_test.py`; `gh issue list -R ssheleg/task-pipeline`
- **Watch window:** 24 hours after the hub pins v1.102.4

## 3. Alerting

- **Fires when:** the release run fails, a session reports the release gate allowing an outward act its ledger does not admit (or refusing one it does), or a new issue is opened on the repository
- **Receives:** the operator, by GitHub's email for failed runs and new issues; the agent running the release reads the run and the checks directly
- **Seen firing:** yes: release run 40241842429 for v1.102.1 failed on 2026-10-25 and was read the same night

## 4. Rollback or hotfix

- **Rollback:** re-pin task-pipeline 1.102.3 in sshlg-skills with a hub patch release, run `npx --yes sshlg-skills@latest update`, and `npm deprecate task-pipeline-skill@1.102.4` with the reason
- **Time to roll back:** about two hours (one hub release and one update on a loaded machine)
- **Data reversible:** yes: the hooks write only the append-only ledger lines they wrote before, unchanged in form
- **Kill switch:** none needed beyond the rollback: the change is three shell scripts, and 1.102.3's copies restore the old behaviour exactly
- **Hotfix path:** a patch release v1.102.5 through the same flow
- **Decision trigger:** roll back if, within 24 hours of the hub pin, any hook verdict differs from 1.102.3's for the same ledger and payload
