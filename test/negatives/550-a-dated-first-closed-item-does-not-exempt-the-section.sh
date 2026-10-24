#!/usr/bin/env bash
# name: Negative self-test (a dated first Closed item does not exempt the section)
set -eu
rm -rf /tmp/b155-copy && cp -R . /tmp/b155-copy
python3 - <<'PY'
# B-155: `_is_dated_record()` read a section as dated when its heading plus the first TWO
# blocks under it carried a date, and under `## Closed` the second block is the newest
# closed item. One date there exempted every number in the section and negative 442 went
# quiet on a 1.101.1 PR. Plant both: a dated first Closed item and a skewed fixture count.
import re
p = "/tmp/b155-copy/docs/evidence/backlog.md"
t = open(p, encoding="utf-8").read()
anchor = "Rows leave the table above only into this list, one line each, with the commit.\n\n"
assert t.count(anchor) == 1, "PLANT DID NOT LAND: the Closed lead paragraph moved"
t = t.replace(anchor, anchor + "- **B-000 · a planted item** (filed 2026-01-01): nothing.\n\n", 1)
m = re.search(r"(\d+) whole-workflow fixtures", t)
assert m, "PLANT DID NOT LAND: the closure line states no fixture count"
t = t.replace(m.group(0), "%d whole-workflow fixtures" % (int(m.group(1)) + 6), 1)
open(p, "w", encoding="utf-8").write(t)
PY
if python3 /tmp/b155-copy/test/validate.py 2>&1 | grep -q "anchor-census fixtures computes to"; then
  echo "OK: validator FAILs — a dated first Closed item stamps itself, not the section"
else
  echo "ERROR: a dated first Closed item exempted the section's numbers and the skewed count passed"
  exit 1
fi
