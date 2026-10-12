#!/usr/bin/env bash
# name: Negative self-test (the convergence check stops saying it runs before integration)
set -eu
rm -rf /tmp/cv2-copy && cp -R . /tmp/cv2-copy
python3 - <<'EOF'
import re
p = "/tmp/cv2-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^### 4\.2a The group convergence check.*?(?=^#{2,3} )", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: cv2 — no 4.2a section"
_sec = re.sub(r"integrat\w*", "proceed", m.group(0), flags=re.I)
_planted = t[:m.start()] + _sec + t[m.end():]
assert _planted != t, "PLANT DID NOT LAND: cv2"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/cv2-copy/test/validate.py 2>&1 | grep -q "does not say it runs BEFORE"; then
  echo "OK: validator FAILs — after the first worktree lands, the group has stopped being a group"
else
  echo "ERROR: the check can lose its position in the order and still pass"
  exit 1
fi
