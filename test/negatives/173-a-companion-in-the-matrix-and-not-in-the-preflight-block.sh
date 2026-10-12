#!/usr/bin/env bash
# name: Negative self-test (a companion in the matrix and not in the preflight block)
set -eu
rm -rf /tmp/comp-copy && cp -R . /tmp/comp-copy
python3 - <<'EOF'
import re
p = "/tmp/comp-copy/plugins/task-pipeline/skills/task-pipeline/references/companion-skills.md"
t = open(p, encoding="utf-8").read()
assert "✗ chrome-devtools" in t, "PLANT DID NOT LAND: preflight line absent before edit"
t2 = re.sub(r"\n  ✗ chrome-devtools.*?(?=\n🧠)", "", t, flags=re.S)
assert t2 != t, "PLANT DID NOT LAND: the preflight line was not removed"
open(p, "w", encoding="utf-8").write(t2)
s = open(p, encoding="utf-8").read()
assert "✗ chrome-devtools" not in s, "PLANT DID NOT LAND"
assert "**chrome-devtools**" in s, "PLANT WRONG: the matrix row must survive"
EOF
if python3 /tmp/comp-copy/test/validate.py; then
  echo "ERROR: validator passed a companion the operator is never offered"
  exit 1
else
  echo "OK: validator correctly FAILs — the matrix and the preflight are compared"
fi
