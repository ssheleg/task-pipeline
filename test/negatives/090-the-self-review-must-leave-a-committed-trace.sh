#!/usr/bin/env bash
# name: Negative self-test (the self-review must leave a committed trace)
set -eu
rm -rf /tmp/readback-trace-copy && cp -R . /tmp/readback-trace-copy
python3 - <<'EOF'
p = "/tmp/readback-trace-copy/plugins/task-pipeline/skills/task-pipeline/references/spec.md"
t = open(p, encoding="utf-8").read()
n = "computed number, not a tick"
assert n in t, "plant would not land: needle absent"
t2 = t.replace(n, "removed-by-probe", 1)
assert n not in t2, "plant did not land"
open(p, "w", encoding="utf-8").write(t2)
EOF
if python3 /tmp/readback-trace-copy/test/validate.py; then
  echo "ERROR: validator passed without 'computed number, not a tick'"
  exit 1
else
  echo "OK: validator requires it"
fi
