#!/usr/bin/env bash
# name: Negative self-test (a rule numbered above the high-water mark)
set -eu
rm -rf /tmp/hw6-copy && cp -R . /tmp/hw6-copy
python3 - <<'EOF'
import re
p = "/tmp/hw6-copy/plugins/task-pipeline/skills/task-pipeline/references/learned.md"
t = open(p, encoding="utf-8").read()
rows = list(re.finditer(r"^\|\s*(\d+)\s*\|\s*\*\*.*$", t, re.M))
assert rows, "PLANT DID NOT LAND: no rule rows"
last = rows[-1]
new_no = int(last.group(1)) + 1
row = re.sub(r"^\|\s*\d+\s*\|", "| %d |" % new_no, last.group(0))
open(p, "w", encoding="utf-8").write(t[:last.end()] + "\n" + row + t[last.end():])
EOF
if python3 /tmp/hw6-copy/test/validate.py; then
  echo "ERROR: a rule was added without advancing the mark, so its later deletion would be invisible"
  exit 1
else
  echo "OK: validator correctly FAILs — the mark may not sit below the table"
fi
