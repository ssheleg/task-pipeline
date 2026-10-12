#!/usr/bin/env bash
# name: Negative self-test (the reader losing its NO READER state)
set -eu
rm -rf /tmp/rd1-copy && cp -R . /tmp/rd1-copy
python3 - <<'EOF'
p = "/tmp/rd1-copy/plugins/task-pipeline/skills/task-pipeline/references/review.md"
t = open(p, encoding="utf-8").read()
n = "reader: NO READER — <why>"
assert n in t, "PLANT DID NOT LAND: the reader states moved"
open(p, "w", encoding="utf-8").write(t.replace(n, "reader: unknown", 1))
EOF
if python3 /tmp/rd1-copy/test/validate.py; then
  echo "ERROR: a reader that never read is now indistinguishable from one that found nothing"
  exit 1
else
  echo "OK: validator correctly FAILs — NO READER is a printed state"
fi
