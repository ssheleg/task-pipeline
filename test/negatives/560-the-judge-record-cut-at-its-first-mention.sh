#!/usr/bin/env bash
# name: Negative self-test (the judge record cut at its first mention)
set -eu
rm -rf /tmp/jr-copy && cp -R . /tmp/jr-copy
# Replace the line-anchored, fence-aware strip with a first-occurrence search: the
# defect that cut fabric-workspace's S0 spec (42ed5bc) at fact 7, whose prose MENTIONS
# the heading. The suite must catch it.
python3 - <<'EOF2'
p = "/tmp/jr-copy/plugins/task-pipeline/skills/task-pipeline/scripts/spec_judge.py"
t = open(p, encoding="utf-8").read()
needle = "def strip_judge_record(text):\n"
assert t.count(needle) == 1, "PLANT DID NOT LAND: jr: strip_judge_record moved"
t = t.replace(needle, needle + "    i = text.find('## Judge record')\n"
              "    return (text[:i] if i >= 0 else text).rstrip() + '\\n'\n", 1)
open(p, "w", encoding="utf-8").write(t)
EOF2
if python3 /tmp/jr-copy/test/spec_judge_test.py >/dev/null 2>&1; then
  echo "ERROR: a first-occurrence strip passed the suite"; exit 1
fi
echo "OK: the suite FAILs a judge record cut at its first mention"
