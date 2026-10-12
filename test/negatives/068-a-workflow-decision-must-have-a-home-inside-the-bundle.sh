#!/usr/bin/env bash
# name: Negative self-test (a workflow decision must have a home inside the bundle)
set -eu
rm -rf /tmp/port-copy && cp -R . /tmp/port-copy
python3 - <<'EOF'
p = "/tmp/port-copy/plugins/task-pipeline/skills/task-pipeline/references/portability.md"
t = open(p, encoding="utf-8").read()
old = "`references/setup.md`"
assert old in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(t.replace(old, "`../../elsewhere/setup.md`", 1))
EOF
if python3 /tmp/port-copy/test/validate.py; then
  echo "ERROR: validator passed a manifest row pointing outside the bundle — a workflow decision that does not travel is a fork nobody named"
  exit 1
else
  echo "OK: every manifest path must resolve inside the bundle"
fi
