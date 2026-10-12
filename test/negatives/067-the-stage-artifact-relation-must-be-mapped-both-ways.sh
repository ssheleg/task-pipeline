#!/usr/bin/env bash
# name: Negative self-test (the stage/artifact relation must be mapped both ways)
set -eu
rm -rf /tmp/artmap-copy && cp -R . /tmp/artmap-copy
python3 - <<'EOF'
p = "/tmp/artmap-copy/plugins/task-pipeline/skills/task-pipeline/references/artifacts.md"
t = open(p, encoding="utf-8").read()
h = "### Project-saved rules, and where each one binds"
assert h in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(t.replace(h, "### Other notes", 1))
EOF
if python3 /tmp/artmap-copy/test/validate.py; then
  echo "ERROR: validator passed an artifact map with only the write direction — a stage whose inputs are unnamed reads whatever the context happens to hold"
  exit 1
else
  echo "OK: validator requires stage->inputs, stage->writes and the project-rules map"
fi
