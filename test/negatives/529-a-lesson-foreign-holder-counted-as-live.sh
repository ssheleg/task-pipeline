#!/usr/bin/env bash
# name: Negative self-test (a lesson foreign holder counted as live)
set -eu
rm -rf /tmp/r15-m10-copy && cp -R . /tmp/r15-m10-copy
python3 - <<'EOF'
# Round 15, m10: an origin carried as `checkout holds another project` is not a live holder of its id. Count it.
p = "/tmp/r15-m10-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            if o.get("memory") and o.get("carried") != CARRY_FOREIGN:\n                live.setdefault'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            if o.get("memory"):\n                live.setdefault', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r15-m10-copy/test/lessons_test.py; then
  rm -rf /tmp/r15-m10-copy
  echo "ERROR: lessons_test passed a re-attached id stripped from its new origin"
  exit 1
else
  rm -rf /tmp/r15-m10-copy
  echo "OK: lessons_test correctly FAILs — a foreign holder is not live"
fi
