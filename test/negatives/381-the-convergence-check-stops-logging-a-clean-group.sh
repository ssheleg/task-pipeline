#!/usr/bin/env bash
# name: Negative self-test (the convergence check stops logging a clean group)
set -eu
rm -rf /tmp/cv4-copy && cp -R . /tmp/cv4-copy
python3 - <<'EOF'
import re
p = "/tmp/cv4-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^### 4\.2a The group convergence check.*?(?=^#{2,3} )", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: cv4 — no 4.2a section"
_sec = re.sub(r"(?i)clean", "silent", m.group(0))
assert _sec != m.group(0), "PLANT DID NOT LAND: cv4 — section never said clean"
open(p, "w", encoding="utf-8").write(t[:m.start()] + _sec + t[m.end():])
EOF
if python3 /tmp/cv4-copy/test/validate.py 2>&1 | grep -q "a clean group logs nothing"; then
  echo "OK: validator FAILs — a check whose silence looks like not running is not evidence"
else
  echo "ERROR: the clean-group line can go and the check becomes unobservable"
  exit 1
fi
