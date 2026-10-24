# Release impact: TODO release name or version

schema: release-impact/1
release: TODO the tag or version this card is for
users: TODO external | internal | none (the value in pipeline.json, release.users)
date: TODO YYYY-MM-DD

<!-- Seeded to <artifacts>/specs/YYYY-MM-DD-<topic>-release-impact.md at stage 7, before the
first outward act. Replace every TODO. A section or a field that does not apply says
`n/a: <reason>`; a bare `n/a` is refused. Gate:
python3 scripts/release_impact.py check <this file> --pipeline pipeline.json
The doctrine is references/release-impact.md in the task-pipeline skill. -->

## 1. Who is affected and how

- **Segments:** TODO who uses what ships, with a rough count of each
- **What changes:** TODO behaviour, data, API or file format compatibility, migrations
- **Breaks for existing users:** TODO no, or what breaks and for whom
- **Rollout:** TODO all at once, staged percentage, canary or feature flag
- **Timing:** TODO when it goes out, and why then

## 2. Tracking

- **Signals:** TODO the metrics, dashboards, logs or error rates that show it going well
- **Baseline:** TODO each signal's value now
- **Where:** TODO the URL, command or query that reads each signal
- **Watch window:** TODO how long after the release the signals are watched

## 3. Alerting

- **Fires when:** TODO the threshold or condition
- **Receives:** TODO who gets it, and where
- **Seen firing:** TODO yes (when), or never

## 4. Rollback or hotfix

- **Rollback:** TODO the exact procedure, or a link to the runbook's rollback section
- **Time to roll back:** TODO minutes or hours
- **Data reversible:** TODO yes (backup, down migration), or no and what is lost
- **Kill switch:** TODO the flag or switch, or n/a: <reason>
- **Hotfix path:** TODO how an urgent fix ships
- **Decision trigger:** TODO roll back if <signal crosses X> within <Y>

<!-- Stage 8 adds the section below once the watch window is read; check it with --outcome.

## Outcome

- **Read:** the signals against their baselines, and any alert that fired
- **Result:** held | rolled back | hotfixed | watching (until <when>, watcher <who or what>)
-->
