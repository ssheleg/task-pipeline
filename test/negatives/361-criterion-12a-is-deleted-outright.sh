#!/usr/bin/env bash
# name: Negative self-test (criterion 12a is deleted outright)
set -eu
rm -rf /tmp/r6b-copy && cp -R . /tmp/r6b-copy
python3 - <<'EOF'
p = "/tmp/r6b-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
t = open(p, encoding="utf-8").read()
# DERIVED anchor (B-113): criteria are renumbered — 12a is a criterion
# inserted between two others and the next insertion moves it. Read the
# number off the criterion this plant is about.
import re
m = re.search(r"(?m)^(\d+)[a-z]\. \*\*Every finding closed in this run records which changed", t)
assert m, "PLANT DID NOT LAND: r6b"
_planted = t.replace(m.group(0), "%sz. **Something else entirely" % m.group(1), 1)
assert _planted != t, "PLANT DID NOT LAND: r6b"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/r6b-copy/test/validate.py 2>&1 | grep -q 'no longer records, per finding'; then
  echo "OK: validator FAILs — R-006 has been in force for four releases with nothing able to read it"
else
  echo "ERROR: the distinction between fixing and reporting vanished and every close-out still passed"
  exit 1
fi
