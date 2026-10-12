#!/usr/bin/env bash
# name: Negative self-test (a hand-back with no NOT VERIFIED field)
set -eu
rm -rf /tmp/hnd1-copy && cp -R . /tmp/hnd1-copy
python3 - <<'EOF'
p = "/tmp/hnd1-copy/plugins/task-pipeline/skills/task-pipeline/references/progress.md"
t = open(p, encoding="utf-8").read()
needle = "NOT VERIFIED what was built and NOT checked"
assert needle in t, "PLANT DID NOT LAND: hnd1 — the hand-back field moved"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, "GAPS        what was built and NOT checked", 1))
EOF
if python3 /tmp/hnd1-copy/test/validate.py; then
  echo "ERROR: a hand-back block with no NOT VERIFIED field was accepted — B-092: the
         gates compute abstained and unlooked at every stage and none of it reaches
         the one artifact an operator reads, so an honest report and a run whose
         checks never looked are the same block"; exit 1
else
  echo "OK: the hand-back block and the ledger shape are read field by field"
fi
