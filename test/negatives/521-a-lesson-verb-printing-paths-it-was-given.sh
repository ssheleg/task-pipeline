#!/usr/bin/env bash
# name: Negative self-test (a lesson verb printing the paths it was given)
set -eu
rm -rf /tmp/r14-main-copy && cp -R . /tmp/r14-main-copy
python3 - <<'EOF'
# Round 14, L3: every verb names the index, its directory, the root and the files it was given. Name none of them.
p = "/tmp/r14-main-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    for known in (idx, idx.parent, legacy, legacy.parent):\n        _show(known, home_relative=True)\n    _show(pathlib.Path(getattr(a, "root", None) or "."))\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='the index is moved once, and the move is said'
out=$(python3 /tmp/r14-main-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r14-main-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed an add refusal printing absolute paths"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — add names its files"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
