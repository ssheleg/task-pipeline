# v1.95.0 exact-tag admission: two unpublished attempts on 4fa7ec6

PR #127 merged as squash commit [4fa7ec6](https://github.com/ssheleg/task-pipeline/commit/4fa7ec6d27218dd240ae1e758d034db1543905f7)
(merge commits are refused by the repository ruleset); its tree equals the tested head
`b2dcdc1`'s tree `6b79a40`. Both attempts ran `scripts/release_candidate.py prepare`
then `check --tag v1.95.0` in a standalone clone with an owned TMPDIR. Neither local
annotation was pushed; both are retired. No `context` was bound, so `publish` was not
reachable through the helper in either attempt.

| Attempt | Local tag object | Result | Duration | Receipt |
|---|---|---|---|---|
| 1 | `303c1ff0` | `CHECK_FAILED`, exit -15, interruption `disk-stopped` | 3598s | [candidate](attempt1-candidate.json), [log](attempt1-suite.log.gz) |
| 2 | `6a68733c` | `CHECK_FAILED`, exit1 | 1710s | [candidate](attempt2-candidate.json), [log](attempt2-suite.log.gz) |

Attempt1: all 439 guards and 15 properties passed; free space then fell under the
helper's 400MB floor at the start of `test:certify`. The machine's swap had grown to
26.6GB from many concurrent agent sessions; nothing in the suite was at fault.

Attempt2 (after space recovered): every suite passed except `test:docs`. Its commit
reachability check found five backticked SHAs in two FW07 evidence READMEs that
squash integration made unreachable from `main` (`fw07-child-lock` lines 3 and 90,
`fw07-copy-cleanup` lines 93, 100, 101). The candidate branch's hosted checks could
not see this, because there those commits were ancestors. This change turns them
into immutable commit links, as #122 did; every target is on a pushed branch
(`compose/fw07-after-1941`, `fix/fw07-scratch-child-lifetime`, `fix/fw07-all-plant-copies`).
`docgate.sh` and `test/validate.py` pass on this change. The next attempt prepares a
fresh annotation on the resulting `main` commit; 1.95.0 was never published.
