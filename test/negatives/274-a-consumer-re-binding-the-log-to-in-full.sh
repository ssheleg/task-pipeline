#!/usr/bin/env bash
# name: Negative self-test (a consumer re-binding the log to "in full")
set -eu
rm -rf /tmp/rf2-copy && cp -R . /tmp/rf2-copy
python3 - <<'EOF'
p = "/tmp/rf2-copy/plugins/task-pipeline/skills/task-pipeline/references/knowledge-sources.md"
t = open(p, encoding="utf-8").read()
n = "the *Recent log* is queried by the task's nouns like the archive"
assert n in t, "PLANT DID NOT LAND: the harvest clause moved"
open(p, "w", encoding="utf-8").write(t.replace(n, "the *Recent log* is read in full", 1))
EOF
if python3 /tmp/rf2-copy/test/validate.py; then
  echo "ERROR: the harvest reads in full what nothing caps"
  exit 1
else
  echo "OK: validator correctly FAILs — every consumer agrees on what is read"
fi
