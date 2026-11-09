#!/usr/bin/env bash
# name: Negative self-test (the short path blind to an agent-only change)
set -eu
rm -rf /tmp/sp3-copy && cp -R . /tmp/sp3-copy
python3 - <<'EOF2'
p = "/tmp/sp3-copy/plugins/task-pipeline/skills/task-pipeline/scripts/short_path.py"
t = open(p, encoding="utf-8").read()
needle = "    if agent_facing:\n"
assert t.count(needle) == 1, "PLANT DID NOT LAND: sp3: the anchor moved or multiplied"
open(p, "w", encoding="utf-8").write(t.replace(needle, "    if False:\n", 1))
EOF2
if python3 /tmp/sp3-copy/test/audit_regressions/diet_proportional.py >/dev/null 2>&1; then
  echo "ERROR: a change only an agent observes took the short path"; exit 1
else
  echo "OK: diet_proportional.py FAILs: answer 3 is a user or an agent"
fi
