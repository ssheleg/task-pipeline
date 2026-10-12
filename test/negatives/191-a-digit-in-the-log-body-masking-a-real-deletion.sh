#!/usr/bin/env bash
# name: Negative self-test (a digit in the log body masking a real deletion)
set -eu
rm -rf /tmp/hw2-copy && cp -R . /tmp/hw2-copy
python3 - <<'EOF'
import re
p = "/tmp/hw2-copy/plugins/task-pipeline/skills/task-pipeline/references/learned.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^\|\s*9\s*\|\s*\*\*.*$", t, re.M)
assert m, "PLANT DID NOT LAND: rule 9's row absent before edit"
t = t[:m.start()] + t[m.end() + 1:]
needle = "*None retired yet.*"
assert needle in t, "PLANT DID NOT LAND: log anchor absent"
# The leading number must NOT be a live table row, or the plant trips the
# resurrection check instead and the test can no longer tell a working anchor
# from a regressed one — verified by reverting the anchor and still failing.
t = t.replace(needle, "- **99 · Something** — trigger: subsumed by 9; `deadbeef`\n\n" + needle, 1)
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/hw2-copy/test/validate.py; then
  echo "ERROR: a bare digit anywhere in the log masked a genuine silent deletion"
  exit 1
else
  echo "OK: validator correctly FAILs — the log match is anchored to each line's leading number"
fi
