#!/usr/bin/env bash
# name: Negative self-test (the source ledger loses its contradictions line)
set -eu
rm -rf /tmp/cx1-copy && cp -R . /tmp/cx1-copy
python3 - <<'EOF'
import re
p = "/tmp/cx1-copy/plugins/task-pipeline/skills/task-pipeline/references/knowledge-sources.md"
t = open(p, encoding="utf-8").read()
planted = re.sub(r"(?i)contradictions:", "notes:", t)
assert planted != t, "PLANT DID NOT LAND: cx1"
open(p, "w", encoding="utf-8").write(planted)
EOF
if python3 /tmp/cx1-copy/test/validate.py 2>&1 | grep -q "no .Contradictions.. line"; then
  echo "OK: validator FAILs — nothing else compares the harvest's sources with each other"
else
  echo "ERROR: the harvest can converge unchecked"
  exit 1
fi
