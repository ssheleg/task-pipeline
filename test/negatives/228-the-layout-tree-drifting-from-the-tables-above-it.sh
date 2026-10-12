#!/usr/bin/env bash
# name: Negative self-test (the layout tree drifting from the tables above it)
set -eu
rm -rf /tmp/tr1-copy && cp -R . /tmp/tr1-copy
python3 - <<'EOF'
p = "/tmp/tr1-copy/plugins/task-pipeline/skills/task-pipeline/references/artifacts.md"
t = open(p, encoding="utf-8").read()
needle = "    verification.md                   # one row per shipped REQ; `Human` is a date or `never`\n"
assert needle in t, "PLANT DID NOT LAND: the tree line is not where the guard reads it"
open(p, "w", encoding="utf-8").write(t.replace(needle, "", 1))
EOF
if python3 /tmp/tr1-copy/test/validate.py; then
  echo "ERROR: one file states the same truth twice and the two drifted for two modules unnoticed"
  exit 1
else
  echo "OK: validator correctly FAILs — the tree is computed against the tables beside it"
fi
