#!/usr/bin/env bash
# name: Negative self-test (a rule leaves learned.md with no logged line)
set -eu
rm -rf /tmp/lrn1-copy && cp -R . /tmp/lrn1-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): rule 12 was a literal in a table that this
# repository adds a row to every time it learns something, so the needle
# was one release from matching nothing. What the guard is about is a
# GAP in the sequence, so the plant needs any rule that is not the first
# or the last — removing the highest leaves the numbers contiguous and
# trips the high-water guard next door instead.
import re
p = "/tmp/lrn1-copy/plugins/task-pipeline/skills/task-pipeline/references/learned.md"
t = open(p, encoding="utf-8").read()
rows = [mm for mm in re.finditer(r"(?m)^\|\s*(\d+)\s*\|\s*\*\*.*$", t)]
assert len(rows) >= 3, "PLANT DID NOT LAND: fewer than three rules to gap"
m = rows[len(rows) // 2]
num = m.group(1)
open(p, "w", encoding="utf-8").write(t[:m.start()] + t[m.end() + 1:])
assert re.search(r"(?m)^\|\s*%s\s*\|" % num,
                 open(p, encoding="utf-8").read()) is None, "PLANT DID NOT LAND"
EOF
if python3 /tmp/lrn1-copy/test/validate.py; then
  echo "ERROR: validator passed a rule that vanished, taking its incident with it"
  exit 1
else
  echo "OK: validator correctly FAILs — a gap the Retired log does not name is a silent deletion"
fi
