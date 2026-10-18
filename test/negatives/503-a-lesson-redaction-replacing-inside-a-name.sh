#!/usr/bin/env bash
# name: Negative self-test (a lesson redaction replacing inside a name)
set -eu
rm -rf /tmp/r13-redact-whole-copy && cp -R . /tmp/r13-redact-whole-copy
python3 - <<'EOF'
# Round 13, N2: redaction replaces whole path components only. Replace every occurrence.
p = "/tmp/r13-redact-whole-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        text = re.sub(r"(?<![\\w.~/-])" + re.escape(path) + r"(?![\\w.~-])", lambda _m: name, text)\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        text = text.replace(path, name)\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='N2: only whole path components are replaced'
out=$(python3 /tmp/r13-redact-whole-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r13-redact-whole-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a path replaced inside a longer name"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — only whole path components are replaced"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
