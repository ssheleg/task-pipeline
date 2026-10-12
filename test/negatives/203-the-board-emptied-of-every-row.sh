#!/usr/bin/env bash
# name: Negative self-test (the board emptied of every row)
set -eu
rm -rf /tmp/bd4-copy && cp -R . /tmp/bd4-copy
python3 - <<'EOF'
import re
p = "/tmp/bd4-copy/docs/evidence/backlog.md"
t = open(p, encoding="utf-8").read()
assert re.search(r"B-\d+", t), "PLANT DID NOT LAND: no ids before the edit"
open(p, "w", encoding="utf-8").write(re.sub(r"B-(\d+)", r"X-\1", t))
assert not re.search(r"B-\d+", open(p, encoding="utf-8").read()), "PLANT DID NOT LAND"
EOF
if python3 /tmp/bd4-copy/test/validate.py; then
  echo "ERROR: an empty board passed — it reads exactly like a board with nothing queued"
  exit 1
else
  echo "OK: validator correctly FAILs — the plant lands in the file that DEFINES the board"
fi
