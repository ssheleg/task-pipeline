#!/usr/bin/env bash
# name: Negative self-test (the Doc Loop must reach the stages that settle decisions)
set -eu
rm -rf /tmp/docloop-copy && cp -R . /tmp/docloop-copy
python3 - <<'EOF'
p = "/tmp/docloop-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
s = open(p, encoding="utf-8").read()
assert "documentation.md" in s, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(s.replace("documentation.md", "somewhere-else.md"))
EOF
if python3 /tmp/docloop-copy/test/validate.py; then
  echo "ERROR: validator passed a stage doctrine that settles decisions and never names the Doc Loop"
  exit 1
else
  echo "OK: validator holds the five decision-settling stages to the Doc Loop"
fi
