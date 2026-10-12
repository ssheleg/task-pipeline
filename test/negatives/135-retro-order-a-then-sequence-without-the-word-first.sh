#!/usr/bin/env bash
# name: Negative self-test (retro order — a then-sequence without the word first)
set -eu
rm -rf /tmp/ord3-copy && cp -R . /tmp/ord3-copy
python3 - <<'EOF'
p = "/tmp/ord3-copy/plugins/task-pipeline/commands/task-pipeline.md"
t = open(p, encoding="utf-8").read()
needle = "**stamp the run first** (its commit"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
t = t.replace(needle, "**prune the list** before you add — every trigger — then stamp the run (its commit", 1)
open(p, "w", encoding="utf-8").write(t)
assert "then stamp the run (its commit" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/ord3-copy/test/validate.py; then
  echo "ERROR: validator passed a prune-then-stamp sequence written without the word 'first'"
  exit 1
else
  echo "OK: validator correctly FAILs — the bare then-sequence shape is covered"
fi
