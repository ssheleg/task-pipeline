#!/usr/bin/env bash
# name: Negative self-test (the distrust marker gets no second spelling)
set -eu
rm -rf /tmp/gs07-copy && cp -R . /tmp/gs07-copy
python3 - <<'EOF'
p = "/tmp/gs07-copy/plugins/task-pipeline/skills/task-pipeline/references/knowledge-graph.md"
t = open(p, encoding="utf-8").read()
needle = "signal: none — ⚠ not trusted for reach until refreshed"
assert needle in t, "PLANT DID NOT LAND: the unresolvable row's marker is absent before edit"
t = t.replace(needle, "signal: none — treat as stale until refreshed")
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/gs07-copy/test/validate.py; then
  echo "ERROR: validator passed with a second spelling of the distrust marker"
  exit 1
else
  echo "OK: validator correctly FAILs — the distrust marker gets no second spelling"
fi
