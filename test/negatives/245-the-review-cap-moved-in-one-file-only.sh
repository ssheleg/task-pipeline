#!/usr/bin/env bash
# name: Negative self-test (the review cap moved in one file only)
set -eu
rm -rf /tmp/rc2-copy && cp -R . /tmp/rc2-copy
python3 - <<'EOF'
p = "/tmp/rc2-copy/plugins/task-pipeline/skills/task-pipeline/references/loop-guard.md"
t = open(p, encoding="utf-8").read()
needle = "**3 review rounds** per artifact"
assert needle in t, "PLANT DID NOT LAND: the cap moved"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, "**4 review rounds** per artifact", 1))
EOF
if python3 /tmp/rc2-copy/test/validate.py; then
  echo "ERROR: the cap says one number in the file that owns it and another where the loop runs"
  exit 1
else
  echo "OK: validator correctly FAILs — the cap is computed from one file and required in the other"
fi
