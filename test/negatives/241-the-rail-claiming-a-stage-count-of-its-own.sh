#!/usr/bin/env bash
# name: Negative self-test (the rail claiming a stage count of its own)
set -eu
rm -rf /tmp/rail-copy && cp -R . /tmp/rail-copy
python3 - <<'EOF'
p = "/tmp/rail-copy/plugins/task-pipeline/skills/task-pipeline/references/progress.md"
t = open(p, encoding="utf-8").read()
needle = "come from the project's `pipeline.json`"
assert needle in t, "PLANT DID NOT LAND: the computed-rail clause moved"
open(p, "w", encoding="utf-8").write(t.replace(needle, "come from the eleven stages", 1))
EOF
if python3 /tmp/rail-copy/test/validate.py; then
  echo "ERROR: a rail hardcoding the example flow is wrong in every project that replaced it"
  exit 1
else
  echo "OK: validator correctly FAILs — the rail is computed, never eleven"
fi
