#!/usr/bin/env bash
# name: Negative self-test (the spec must keep asking whether a named check is real)
set -eu
rm -rf /tmp/readback-spec-copy && cp -R . /tmp/readback-spec-copy
python3 - <<'EOF'
p = "/tmp/readback-spec-copy/plugins/task-pipeline/skills/task-pipeline/references/spec.md"
t = open(p, encoding="utf-8").read()
n = "Every check this spec names resolves"
assert n in t, "plant would not land: needle absent"
t2 = t.replace(n, "removed-by-probe", 1)
assert n not in t2, "plant did not land"
open(p, "w", encoding="utf-8").write(t2)
EOF
if python3 /tmp/readback-spec-copy/test/validate.py; then
  echo "ERROR: validator passed without 'Every check this spec names resolves'"
  exit 1
else
  echo "OK: validator requires it"
fi
