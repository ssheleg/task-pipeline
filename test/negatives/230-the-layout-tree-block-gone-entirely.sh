#!/usr/bin/env bash
# name: Negative self-test (the layout tree block gone entirely)
set -eu
rm -rf /tmp/tr2-copy && cp -R . /tmp/tr2-copy
python3 - <<'EOF'
import re
p = "/tmp/tr2-copy/plugins/task-pipeline/skills/task-pipeline/references/artifacts.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^  evidence/[^\n]*\n(?:    .*\n)+", t, re.M)
assert m, "PLANT DID NOT LAND: the tree block is not where the guard reads it"
open(p, "w", encoding="utf-8").write(t[:m.start()] + t[m.end():])
assert not re.search(r"^  evidence/[^\n]*\n    ", open(p, encoding="utf-8").read(), re.M), "PLANT DID NOT LAND"
EOF
if python3 /tmp/tr2-copy/test/validate.py; then
  echo "ERROR: the tree vanished and the guard comparing against it passed"
  exit 1
else
  echo "OK: validator correctly FAILs — the missing-block branch is watched too, not only the missing-line one"
fi
