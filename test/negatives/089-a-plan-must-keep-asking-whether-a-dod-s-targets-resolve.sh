#!/usr/bin/env bash
# name: Negative self-test (a plan must keep asking whether a DoD's targets resolve)
set -eu
rm -rf /tmp/readback-plan-copy && cp -R . /tmp/readback-plan-copy
python3 - <<'EOF'
p = "/tmp/readback-plan-copy/plugins/task-pipeline/skills/task-pipeline/references/planning.md"
t = open(p, encoding="utf-8").read()
n = "Every command, path and file a DoD names resolves"
assert n in t, "plant would not land: needle absent"
t2 = t.replace(n, "removed-by-probe", 1)
assert n not in t2, "plant did not land"
open(p, "w", encoding="utf-8").write(t2)
EOF
if python3 /tmp/readback-plan-copy/test/validate.py; then
  echo "ERROR: validator passed without 'Every command, path and file a DoD names resolves'"
  exit 1
else
  echo "OK: validator requires it"
fi
