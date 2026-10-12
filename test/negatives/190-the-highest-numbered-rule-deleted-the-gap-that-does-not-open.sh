#!/usr/bin/env bash
# name: Negative self-test (the HIGHEST-numbered rule deleted — the gap that does not open)
set -eu
rm -rf /tmp/hw1-copy && cp -R . /tmp/hw1-copy
python3 - <<'EOF'
import re
p = "/tmp/hw1-copy/plugins/task-pipeline/skills/task-pipeline/references/learned.md"
t = open(p, encoding="utf-8").read()
nums = [int(n) for n in re.findall(r"^\|\s*(\d+)\s*\|\s*\*\*", t, re.M)]
assert nums, "PLANT DID NOT LAND: no rule rows found"
m = re.search(r"^\|\s*%d\s*\|\s*\*\*.*$" % max(nums), t, re.M)
assert m, "PLANT DID NOT LAND: highest row absent before edit"
open(p, "w", encoding="utf-8").write(t[:m.start()] + t[m.end() + 1:])
after = [int(n) for n in re.findall(r"^\|\s*(\d+)\s*\|\s*\*\*", open(p, encoding="utf-8").read(), re.M)]
assert max(after) < max(nums), "PLANT DID NOT LAND"
EOF
if python3 /tmp/hw1-copy/test/validate.py; then
  echo "ERROR: deleting the highest rule shrinks max() with it and opens no gap — the false negative this guard shipped with"
  exit 1
else
  echo "OK: validator correctly FAILs — the high-water mark comes from the file, not from max()"
fi
