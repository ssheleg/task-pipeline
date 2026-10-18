#!/usr/bin/env bash
# name: Negative self-test (a lesson project key taken from the checked-out branch)
set -eu
rm -rf /tmp/key-head-copy && cp -R . /tmp/key-head-copy
python3 - <<'EOF'
# Round 12: the project key is the repository's — the default branch's first-parent root, once per git common dir. Take HEAD's roots again: a checkout on gh-pages is a stranger.
p = "/tmp/key-head-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    if key in _KEYS:\n        return _KEYS[key]\n    refs: list[tuple[tuple[str, ...], str]] = []\n    head = _git(root, "symbolic-ref", "-q", "refs/remotes/origin/HEAD")\n    if head:\n        refs.append(((), head))\n    refs += [((), "refs/heads/main"), ((), "refs/heads/master")]\n    if common:\n        refs.append((("--git-dir", common), "HEAD"))  # the main worktree\'s HEAD\n    default = _git(root, "config", "--get", "init.defaultBranch")\n    if default:\n        refs.append(((), "refs/heads/" + default))\n    refs.append(((), "HEAD"))\n    for extra, ref in refs:\n        if _git(root, *extra, "rev-parse", "-q", "--verify", ref + "^{commit}") is None:\n            continue\n        roots = _git(root, *extra, "rev-list", "--max-parents=0", "--first-parent", ref)\n        if roots:\n            _KEYS[key] = "p-" + roots.split()[-1][:12]\n            return _KEYS[key]\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    roots = _git(root, "rev-list", "--max-parents=0", "HEAD")\n    if roots:\n        return "p-" + sorted(roots.split())[0][:12]\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='F: emit from a checkout on an orphan branch finds its origin'
# Also accepted: A detects the revert only when the merged history's root sorts lower, a coin toss per run.
also='A: worktrees of one repository are one project whatever branch they hold'
out=$(python3 /tmp/key-head-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/key-head-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a project key that follows the checked-out branch"
  exit 1
elif printf '%s\n' "$out" | grep -qF -e "FAIL: $expect" -e "FAIL: $also"; then
  echo "OK: lessons_test correctly FAILs — the key is the repository's"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
