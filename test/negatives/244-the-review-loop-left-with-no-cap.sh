#!/usr/bin/env bash
# name: Negative self-test (the review loop left with no cap)
set -eu
rm -rf /tmp/rc1-copy && cp -R . /tmp/rc1-copy
python3 - <<'EOF'
p = "/tmp/rc1-copy/plugins/task-pipeline/skills/task-pipeline/references/loop-guard.md"
t = open(p, encoding="utf-8").read()
needle = "**3 review rounds** per artifact"
assert needle in t, "PLANT DID NOT LAND: the cap is not where the guard reads it"
open(p, "w", encoding="utf-8").write(t.replace(needle, "review rounds per artifact", 1))
EOF
if python3 /tmp/rc1-copy/test/validate.py; then
  echo "ERROR: the loop this repository ran ten rounds of is capped by nothing again"
  exit 1
else
  echo "OK: validator correctly FAILs — the review loop carries a stated cap"
fi
