#!/usr/bin/env bash
# name: Negative self-test (the record stops naming the times it never observed)
set -eu
rm -rf /tmp/res22-copy && cp -R . /tmp/res22-copy
python3 - <<'EOF'
p = "/tmp/res22-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
n = "the wall-clock times"
assert n in t, "PLANT DID NOT LAND: res22"
_planted = t.replace(n, "the exact hours", 1)
assert _planted != t, "PLANT DID NOT LAND: res22"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res22-copy/test/validate.py 2>&1 | grep -q "wall-clock times.* is gone"; then
  echo "OK: validator FAILs — a record silent about its own limit invites a reader to supply an hour nobody measured"
else
  echo "ERROR: the record lost the statement of what it did not observe"
  exit 1
fi
