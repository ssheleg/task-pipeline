#!/usr/bin/env bash
# name: Negative self-test (Part 1a stops stating its precondition)
set -eu
rm -rf /tmp/lp12-copy && cp -R . /tmp/lp12-copy
python3 - <<'EOF'
p = "/tmp/lp12-copy/plugins/task-pipeline/skills/task-pipeline/references/continuity.md"
t = open(p, encoding="utf-8").read()
n = "**Where nothing is recorded, nothing arms.**"
assert n in t, "PLANT DID NOT LAND: lp12"
i = t.index(n); j = t.index("**What arming does NOT change", i)
t = t[:i] + t[j:]
t = t.replace("Where the mode\nis **recorded** and the queue", "Where the queue", 1)
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/lp12-copy/test/validate.py 2>&1 | grep -q 'arming is stated with no precondition'; then
  echo "OK: validator FAILs — unconditional arming overrides the default-off floor"
else
  echo "ERROR: Part 1a made arming unconditional and the floor three surfaces away did not object"
  exit 1
fi
