#!/usr/bin/env bash
# name: Negative self-test (a graph that cannot be measured needs its own state)
set -eu
rm -rf /tmp/gs04-copy && cp -R . /tmp/gs04-copy
python3 - <<'EOF'
p = "/tmp/gs04-copy/plugins/task-pipeline/skills/task-pipeline/references/knowledge-graph.md"
t = open(p, encoding="utf-8").read()
assert "**unresolvable**" in t, "PLANT DID NOT LAND: needle absent before edit"
t = t.replace("**unresolvable**", "**probably fine**")
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/gs04-copy/test/validate.py; then
  echo "ERROR: validator passed with the unresolvable state removed"
  exit 1
else
  echo "OK: validator correctly FAILs — a graph that cannot be measured needs its own state"
fi
