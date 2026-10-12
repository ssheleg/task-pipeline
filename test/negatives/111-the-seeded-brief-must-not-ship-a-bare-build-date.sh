#!/usr/bin/env bash
# name: Negative self-test (the seeded brief must not ship a bare build date)
set -eu
rm -rf /tmp/gs05-copy && cp -R . /tmp/gs05-copy
python3 - <<'EOF'
p = "/tmp/gs05-copy/plugins/task-pipeline/skills/task-pipeline/templates/brief.md"
t = open(p, encoding="utf-8").read()
needle = "built `<sha>` — N commits / M days behind HEAD, signal: built_at_commit (exact) — ⚠ not trusted for reach until refreshed"
assert needle in t, "PLANT DID NOT LAND: needle absent before edit"
t = t.replace(needle, "built YYYY-MM-DD")
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/gs05-copy/test/validate.py; then
  echo "ERROR: validator passed with the seeded brief shipping a bare build date"
  exit 1
else
  echo "OK: validator correctly FAILs — the seeded brief must not ship a bare build date"
fi
