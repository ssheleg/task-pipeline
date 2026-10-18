#!/usr/bin/env bash
# name: Negative self-test (a lesson re-key taking a commit from a merged history)
set -eu
rm -rf /tmp/r14-roots-copy && cp -R . /tmp/r14-roots-copy
python3 - <<'EOF'
# Round 14, F1: the re-keyed origin's commit must descend from the root the candidate's key names. Drop that.
p = "/tmp/r14-roots-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '\n                and n["project"][2:] in _roots_of(c, o["commit"]))\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, ')\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='K: without its commit in the checkout an old-key origin is not re-keyed'
out=$(python3 /tmp/r14-roots-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r14-roots-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a monorepo taking the merged repository's id"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — the commit's roots decide"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
