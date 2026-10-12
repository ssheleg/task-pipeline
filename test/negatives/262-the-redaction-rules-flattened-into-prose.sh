#!/usr/bin/env bash
# name: Negative self-test (the redaction rules flattened into prose)
set -eu
rm -rf /tmp/rp2-copy && cp -R . /tmp/rp2-copy
python3 - <<'EOF'
p = "/tmp/rp2-copy/plugins/task-pipeline/skills/task-pipeline/references/retrospective.md"
t = open(p, encoding="utf-8").read()
assert "1. **No host paths.**" in t, "PLANT DID NOT LAND: rule 1 moved"
open(p, "w", encoding="utf-8").write(t.replace("1. **No host paths.**", "- **No host paths.**", 1))
EOF
if python3 /tmp/rp2-copy/test/validate.py; then
  echo "ERROR: a list nobody can point at an item of is advice, not a contract"
  exit 1
else
  echo "OK: validator correctly FAILs — the redaction rules stay an enumeration"
fi
