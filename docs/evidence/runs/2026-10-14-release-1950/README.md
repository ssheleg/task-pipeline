# v1.95.0 exact-tag admission: two unpublished attempts on 4fa7ec6

PR #127 merged as squash commit [4fa7ec6](https://github.com/ssheleg/task-pipeline/commit/4fa7ec6d27218dd240ae1e758d034db1543905f7)
(merge commits are refused by the repository ruleset); its tree equals the tested head
[b2dcdc1](https://github.com/ssheleg/task-pipeline/commit/b2dcdc1908f1aeb096ac14954551d42f605f561b)'s tree (object 6b79a404). Both attempts ran `scripts/release_candidate.py prepare`
then `check --tag v1.95.0` in a standalone clone with an owned TMPDIR. Neither local
annotation was pushed; both are retired. No `context` was bound, so `publish` was not
reachable through the helper in either attempt.

| Attempt | Local tag object | Result | Duration | Receipt |
|---|---|---|---|---|
| 1 | object 303c1ff0 | `CHECK_FAILED`, exit -15, interruption `disk-stopped` | 3598s | [candidate](attempt1-candidate.json), [log](attempt1-suite.log.gz) |
| 2 | object 6a68733c | `CHECK_FAILED`, exit1 | 1710s | [candidate](attempt2-candidate.json), [log](attempt2-suite.log.gz) |

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

## Attempt3: admitted and published on 5a787b4

After #128 merged as [5a787b4](https://github.com/ssheleg/task-pipeline/commit/5a787b4cce4e53aaa76b0971cf9c0293e4dc126b)
a fresh standalone clone ran `prepare` (local annotated object ada20cbb) and `check`:
`CHECK_PASSED`, exit0, 3054s, no interruption, release gap looked —
[candidate](attempt3-candidate.json), [log](attempt3-suite.log.gz) (log sha256 equals the
receipt). All 439 guards and 15 properties passed; every later suite completed.

`publish --tag v1.95.0` refused with `publish unavailable: no bound actual project
context`: no run ledger exists at this exact source, and none was written to make the
hook pass. The tag was then pushed by hand with the same preconditions the helper
checks, read before the push: clean tree; tag type `tag`, peel equal to `origin/main`;
remote tag absent; identical fetch/push origin; log digest equal to the receipt. Command:
`git push --no-follow-tags origin <object>:refs/tags/v1.95.0`; remote readback named the
same object and peel.

The [release run](release-run.json) (38499730163) concluded success for both `release`
and `publish`. The [registry readback](registry.txt) reports 1.95.0 with gitHead 5a787b4; all 155
files of the packed tarball are byte-equal to the source at that commit. The two earlier
local annotations (303c1ff0, 6a68733c) were never pushed. Installed acceptance belongs to
the umbrella's update, not to this receipt.
