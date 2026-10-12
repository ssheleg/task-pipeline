#!/usr/bin/env bash
# name: Negative self-test (stage 2 must produce user paths and error paths)
set -eu
rm -rf /tmp/ux2-copy && cp -R . /tmp/ux2-copy
python3 - <<'EOF'
p = "/tmp/ux2-copy/plugins/task-pipeline/skills/task-pipeline/references/brainstorm.md"
t = open(p, encoding="utf-8").read()
assert "User paths are a design output" in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(t.replace("User paths are a design output", "Some other heading"))
EOF
if python3 /tmp/ux2-copy/test/validate.py; then
  echo "ERROR: validator passed a design stage that never names user paths or error paths — the hardest third gets invented at stage 5 by whoever implements it"
  exit 1
else
  echo "OK: the design stage owns paths, states and error paths"
fi
