# v1.96.0 — finish line: admitted, published and read back

PR #131 merged as squash commit [2674147](https://github.com/ssheleg/task-pipeline/commit/2674147ccfc5eab19aab8f9d7334909cc22f64b2)
after two independent review rounds (ACCEPT-WITH-FIXES with 11 findings, all fixed; then ACCEPT
with five deferred findings, now board rows B-136 to B-140). Before the merge a simulated squash
of the branch passed `docgate.sh`, so the 1.95.0 failure mode (squash-unreachable evidence SHAs)
did not recur.

- Exact-tag admission: fresh standalone clone, `release_candidate.py prepare` then `check` —
  `CHECK_PASSED`; [candidate](candidate.json), [log](suite.log.gz).
- `publish` refused (`no bound actual project context`); no run ledger was written to make it
  pass. The annotated object d6233c68 was pushed with `--no-follow-tags` after the helper's
  preconditions were read (clean tree, peel equal to `origin/main`, remote tag absent, log
  digest equal to the receipt). The first push attempt failed on a shell quoting error in the
  operator's command (`$OBJ:refs` read as a zsh modifier), not on the remote.
- Release run 38722488907: `release` and `publish` success. [Registry readback](registry.txt):
  1.96.0, gitHead 2674147; all 162 tarball files byte-equal to the tagged source.

Finish line applied to this iteration: rounds 2/3, releases 1/2, blocking 0 open, deferred 5
(B-136…B-140, none at blast 3).
