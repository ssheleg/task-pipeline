#!/usr/bin/env bash
# name: Negative self-test (the containers measurement and the prose citing it disagree)
set -eu
rm -rf /tmp/res23-copy && cp -R . /tmp/res23-copy
python3 - <<'EOF'
p = "/tmp/res23-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
# The number is frozen — no command recomputes a container count from one
# afternoon — so what is policed is the record's agreement with itself. An
# external document quotes this number out of the prose, not out of the block.
# DERIVED anchor (B-113): the count is frozen but not immutable — a
# re-measurement would move it, and the plant would then mutate nothing.
# Read the number the prose states and write one that disagrees with it.
import re
m = re.search(r"The (\d+) containers above", t)
assert m, "PLANT DID NOT LAND: res23"
_planted = t.replace(m.group(0), "The %d containers above" % (int(m.group(1)) + 6), 1)
assert _planted != t, "PLANT DID NOT LAND: res23"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res23-copy/test/validate.py 2>&1 | grep -q "the two halves of one record cannot disagree"; then
  echo "OK: validator FAILs — the block and the sentence that carries it outward are one number"
else
  echo "ERROR: a cited measurement drifted from the prose citing it"
  exit 1
fi
