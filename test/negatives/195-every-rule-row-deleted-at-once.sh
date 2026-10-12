#!/usr/bin/env bash
# name: Negative self-test (every rule row deleted at once)
set -eu
rm -rf /tmp/hw7-copy && cp -R . /tmp/hw7-copy
python3 - <<'EOF'
import re
p = "/tmp/hw7-copy/plugins/task-pipeline/skills/task-pipeline/references/learned.md"
t = open(p, encoding="utf-8").read()
out = re.sub(r"^\|\s*\d+\s*\|\s*\*\*.*$\n", "", t, flags=re.M)
assert out != t, "PLANT DID NOT LAND: no rule rows removed"
open(p, "w", encoding="utf-8").write(out)
EOF
if python3 /tmp/hw7-copy/test/validate.py; then
  echo "ERROR: emptying the table made the rule list falsy and skipped the whole check"
  exit 1
else
  echo "OK: validator correctly FAILs — wholesale deletion is the loudest case, not an exemption"
fi
