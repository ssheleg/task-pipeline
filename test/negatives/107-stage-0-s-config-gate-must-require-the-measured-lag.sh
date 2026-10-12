#!/usr/bin/env bash
# name: Negative self-test (stage 0's config gate must require the measured lag)
set -eu
rm -rf /tmp/gs01-copy && cp -R . /tmp/gs01-copy
python3 - <<'EOF'
p = "/tmp/gs01-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
t = open(p, encoding="utf-8").read()
assert "THE GRAPH'S ROW CARRIES ITS MEASURED LAG" in t, "PLANT DID NOT LAND: needle absent before edit"
t = t.replace("THE GRAPH'S ROW CARRIES ITS MEASURED LAG", "the graph's row carries its build date")
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/gs01-copy/test/validate.py; then
  echo "ERROR: validator passed with stage 0's gate no longer requiring the measured lag"
  exit 1
else
  echo "OK: validator correctly FAILs — stage 0's config gate must require the measured lag"
fi
