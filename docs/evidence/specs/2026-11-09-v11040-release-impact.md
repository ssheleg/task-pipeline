# Release impact: task-pipeline v1.104.0

schema: release-impact/1
release: v1.104.0
users: external
date: 2026-11-09

## 1. Who is affected and how

- **Segments:** every agent that runs task-pipeline from an install of this package: the operator's machines through sshlg-skills (Claude Code plugin, Codex plugin, skills CLI) and anyone who installs `task-pipeline-skill` from npm; the download count was not read for this card
- **What changes:** stage 0's user-facing question becomes an actor question (`capability_change`, `contract_change`, `agent_surface`; `surface_class` per human surface); stages 2 to 5 order capabilities and the contract before screens; gates 0, 2, 3, 6, 7, 8 and 10 gain short checks for an agent surface (the proving call, the snapshot diff, "called, not curled", the `C→B` row); a new optional node field `agent_surface` and a fifth certification reading `agent`, owed only by `public` and `internal`; `agents/agent-tester.md` and `agents/verifier-agent.md`; `short_path.py --agent-facing`; the doctrine in `references/agent-surface.md`
- **Breaks for existing users:** nothing that worked before: a graph without `agent_surface` validates and certifies exactly as in 1.103.1 (182 graph cases, the 173 old ones unchanged); `short_path.py` without `--agent-facing` decides as before (the flag defaults to `no`); a task with no capability or contract change owes nothing new; stage numbers are unchanged, so custom profiles and `plan_audit.py` are untouched
- **Rollout:** all at once: npm publish, then the sshlg-skills pin (1.87.0), then `npx sshlg-skills update` on each machine
- **Timing:** 2026-11-09

## 2. Tracking

- **Signals:** the tag's release run conclusion; `npm view task-pipeline-skill version`; a run that asks the actor question for a task with no capability or contract change, or certifies a `public`/`internal` node without an `agent` report; new issues on ssheleg/task-pipeline
- **Baseline:** v1.103.1 on npm; `test/graph_test.py` 173 cases on 1.103.1 and 182 on 1.104.0; `test/certify_mutations.py` 27 of 27 noticed; negative plants 551 to 556 each rejected
- **Where:** `gh run list -R ssheleg/task-pipeline -b v1.104.0`; `npm view task-pipeline-skill version`; `python3 test/graph_test.py`; `gh issue list -R ssheleg/task-pipeline`
- **Watch window:** 24 hours after the hub pins v1.104.0, and the first executed run of the pipeline on a product (hub board row B-329)

## 3. Alerting

- **Fires when:** the release run fails, a session reports the actor branch firing on a task with no capability change, or a new issue is opened on the repository
- **Receives:** the operator, by GitHub's email for failed runs and new issues; the agent running the release reads the run and the checks directly
- **Seen firing:** yes: release run 42365245798 for v1.103.0 failed on 2026-11-06 and was read the same day

## 4. Rollback or hotfix

- **Rollback:** re-pin task-pipeline 1.103.1 in sshlg-skills with a hub patch release, run `npx --yes sshlg-skills@latest update`, and `npm deprecate task-pipeline-skill@1.104.0` with the reason
- **Time to roll back:** about two hours (one hub release and one update on a loaded machine)
- **Data reversible:** yes: doctrine, an optional graph field and agent definitions; 1.103.1's schema declares `additionalProperties: false` on a node, so a graph written with `agent_surface` may be refused there; whether 1.103.1's `graph.py validate` refuses it was not measured for this card, and a rollback removes the field first
- **Kill switch:** none needed beyond the rollback: every new obligation is keyed on an optional field or a recorded capability change
- **Hotfix path:** a patch release v1.104.1 through the same flow
- **Decision trigger:** roll back if, within 24 hours of the hub pin, a run is blocked by the `agent` tier on a node that never declared `agent_surface`, or `short_path.py` without the new flag answers differently from 1.103.1
