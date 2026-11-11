#!/usr/bin/env bash
# name: Negative self-test (an em dash in a seeded template's prose)
set -eu
rm -rf /tmp/em1-copy && cp -R . /tmp/em1-copy
python3 - <<'EOF2'
p = "/tmp/em1-copy/plugins/task-pipeline/skills/task-pipeline/templates/brief.md"
t = open(p, encoding="utf-8").read()
needle = "# Task brief: <topic>"
assert t.count(needle) == 1, "PLANT DID NOT LAND: em1: the brief heading moved"
open(p, "w", encoding="utf-8").write(t.replace(needle, "# Task brief — <topic>", 1))
EOF2
if python3 /tmp/em1-copy/test/validate.py 2>&1 | grep -q "em dash(es) in text a person reads"; then
  echo "OK: validator FAILs: a seeded template's prose carries no em dash"
else
  echo "ERROR: an em dash in a template a person reads passed"; exit 1
fi
