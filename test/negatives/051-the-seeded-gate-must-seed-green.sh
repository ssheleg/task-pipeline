#!/usr/bin/env bash
# name: Negative self-test (the seeded gate must seed GREEN)
set -eu
rm -rf /tmp/seedred-copy && cp -R . /tmp/seedred-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): the seeded next-free id moves the moment the
# template's worked example gains a decision. Read the id the template
# states, and write one that is not the successor of its last DEC row —
# the shape the seeded gate refuses, whatever the digits are today.
import re
p = "/tmp/seedred-copy/plugins/task-pipeline/skills/task-pipeline/templates/decisions.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"\*\*Next free ID:\*\* `DEC-(\d+)`", t)
assert m, "PLANT DID NOT LAND: the template states no next free ID"
skewed = "**Next free ID:** `DEC-%04d`" % (int(m.group(1)) + 7)
open(p, "w", encoding="utf-8").write(t.replace(m.group(0), skewed, 1))
EOF
if python3 /tmp/seedred-copy/test/validate.py; then
  echo "ERROR: validator passed templates whose own gate rejects them — a project that starts red learns on day one that the gate is noise"
  exit 1
else
  echo "OK: validator runs the seeded gate over a seeded project and requires exit 0"
fi
