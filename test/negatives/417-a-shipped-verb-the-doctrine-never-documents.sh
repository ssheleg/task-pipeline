#!/usr/bin/env bash
# name: Negative self-test (a shipped verb the doctrine never documents)
set -eu
rm -rf /tmp/wg1-copy && cp -R . /tmp/wg1-copy
python3 - <<'EOF'
p = "/tmp/wg1-copy/plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"
t = open(p, encoding="utf-8").read()
needle = '    "goal": (cmd_goal,'
assert needle in t, "PLANT DID NOT LAND: wg1 — the verb table moved"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, '    "tally": (cmd_goal, "count"),\n' + needle, 1))
EOF
if python3 /tmp/wg1-copy/test/validate.py; then
  echo "ERROR: a verb shipped with no doctrine row was accepted — T-7: the doctrine
         and the script are two homes for one list, and a verb nobody documents is
         one an agent finds by reading the source"; exit 1
else
  echo "OK: the verb list is discovered from the script and compared to the doctrine"
fi
