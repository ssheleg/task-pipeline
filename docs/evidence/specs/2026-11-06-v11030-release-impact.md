# Release impact: task-pipeline v1.103.0

schema: release-impact/1
release: v1.103.0
users: external
date: 2026-11-06

## 1. Who is affected and how

- **Segments:** every agent that runs task-pipeline from an install of this package: the operator's machines through sshlg-skills (Claude Code plugin, Codex plugin, skills CLI) and anyone who installs `task-pipeline-skill` from npm; the download count was not read for this card
- **What changes:** stage 0 gains phase 1a. A prompt that carries several asks is listed as `ASK-n`, triaged per ask, and past a threshold cut into modules researched in parallel (at most six at once), merged with a second pass, ranked; the top item becomes the brief and the rest are filed on the project's board before stage 1. `scripts/backlog_sources.py --discover` finds that board (manifest, instruction file, agent-sync register, known paths, a named tracker) and a board is seeded only when none exists
- **Breaks for existing users:** nothing that worked before: a single-ask prompt runs exactly as in 1.102.4, and `backlog_sources.py` without `--discover` keeps its output and exit codes (the 40 cases of 1.102.4 pass unchanged), except that a name the stdout's encoding cannot write no longer crashes a strict stdout (1.102.4 exited 1 with a traceback; on an ASCII stdout the escaped output is not valid JSON, `--discover` output always is), and a manifest nested deeper than 64 levels is refused with exit 1 and no traceback at every depth tested up to 1,000,000: the reason is `nested deeper than 64 levels`, or `not readable JSON (RecursionError)` past the parser's own limit. 1.102.4 exited 1 with other reasons below its interpreter's recursion limit and crashed with a traceback above it; that limit depends on the Python version, the platform, the C stack and the manifest's shape (measured by bisection on 2026-11-06 from about 990 levels on 3.9 and 3.11 to about 70,000 to 116,000 on macOS 3.14 and about 40,000 to 47,000 on Linux 3.14 with an 8 MB stack). Two more plain-CLI changes, each a class: any error looking up the manifest other than absent, not a directory, a link loop or a dangling link (a `docs/`, `--root` or parent directory that cannot be searched; a path past the platform's limit; any other OS error) now exits 1 `not readable (<error>)` with no traceback on every Python, where 1.102.4 raised a traceback with exit 1 on 3.9 to 3.13 and exited 0 "no manifest" on 3.14; and any error looking up a declared source (an unreadable directory on its way, a name past the platform's limit) reads as `missing, or reached through a symlink`, exit 1, where 1.102.4 raised a traceback with exit 1 on 3.9 to 3.13. Absent, not a directory, a link loop and a dangling link still read as no manifest, as before. A project that keeps `docs/backlog.md` and no `docs/evidence/backlog.md` no longer gets a second board seeded beside it; a project whose board sits elsewhere gets exit 5 and its signals instead of a seed
- **Rollout:** all at once: npm publish, then the sshlg-skills pin, then `npx sshlg-skills update` on each machine
- **Timing:** 2026-11-06

## 2. Tracking

- **Signals:** the tag's release run conclusion; `npm view task-pipeline-skill version`; a run that seeds a second board beside an existing one, or files a split item outside the discovered home; new issues on ssheleg/task-pipeline
- **Baseline:** v1.102.4 on npm; `test/backlog_sources_test.py` 40 cases on 1.102.4 and 284 on 1.103.0 (Python 3.9, 3.11, 3.12, 3.13 and 3.14); `--discover` read back on 2026-11-06 over 156 repositories (each direct child of `~/DATA` that is not a symlink and has a `.git` directory, except names starting with `_`, ending in `-data`, or containing `backup`, `-wt-` or `obsidian`; a 157th, go-to-market-strategy, was created at 18:23 that day, after the measurement, and exits 5): 14 manifest, 22 instruction, 3 tracker, 39 known path, 69 signals (exit 5, read before seeding), 9 with no instruction file and nothing else (exit 4); 30 homes outside both artifact paths plus at least 10 boards or trackers reported as signals, each of which 1.102.4 would have duplicated
- **Where:** `gh run list -R ssheleg/task-pipeline -b v1.103.0`; `npm view task-pipeline-skill version`; `python3 test/backlog_sources_test.py`; `gh issue list -R ssheleg/task-pipeline`
- **Watch window:** 24 hours after the hub pins v1.103.0

## 3. Alerting

- **Fires when:** the release run fails, a session reports a duplicate board or a split item filed in the wrong place, or a new issue is opened on the repository
- **Receives:** the operator, by GitHub's email for failed runs and new issues; the agent running the release reads the run and the checks directly
- **Seen firing:** yes: release run 40241842429 for v1.102.1 failed on 2026-10-25 and was read the same night

## 4. Rollback or hotfix

- **Rollback:** re-pin task-pipeline 1.102.4 in sshlg-skills with a hub patch release, run `npx --yes sshlg-skills@latest update`, and `npm deprecate task-pipeline-skill@1.103.0` with the reason
- **Time to roll back:** about two hours (one hub release and one update on a loaded machine)
- **Data reversible:** yes: the change is doctrine and a read-only discovery script; rows it caused to be filed stay valid rows on the project's own board
- **Kill switch:** none needed beyond the rollback: `--discover` writes nothing, and the doctrine is read, not executed
- **Hotfix path:** a patch release v1.103.1 through the same flow
- **Decision trigger:** roll back if, within 24 hours of the hub pin, a run seeds a duplicate board or `backlog_sources.py` without `--discover` answers differently from 1.102.4
