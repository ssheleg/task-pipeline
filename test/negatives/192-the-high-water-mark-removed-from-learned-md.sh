#!/usr/bin/env bash
# name: Negative self-test (the high-water mark removed from learned.md)
set -eu
rm -rf /tmp/hw3-copy && cp -R . /tmp/hw3-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): the high-water mark rises with every rule this
# repository learns, so the literal was guaranteed to go stale — and a
# needle that stops matching removes the check in silence.
import re
p = "/tmp/hw3-copy/plugins/task-pipeline/skills/task-pipeline/references/learned.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"\*\*Numbers issued so far: \d+\.\*\*", t)
assert m, "PLANT DID NOT LAND: high-water mark absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(m.group(0), "**A note.**", 1))
assert "Numbers issued so far" not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/hw3-copy/test/validate.py; then
  echo "ERROR: validator passed with no high-water mark — the gap guard has nothing to measure against"
  exit 1
else
  echo "OK: validator correctly FAILs — the mark is required, and it may not fall below the table"
fi
