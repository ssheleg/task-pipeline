#!/usr/bin/env bash
# name: Negative self-test (canons must keep naming their enforcement)
set -eu
rm -rf /tmp/cn3-copy && cp -R . /tmp/cn3-copy
python3 - <<'EOF'
import re
p = "/tmp/cn3-copy/plugins/task-pipeline/skills/task-pipeline/references/documentation.md"
t = open(p, encoding="utf-8").read()
# The guard wants an arrow inside EACH canon's span. This probe matched one
# exact citation and broke the day that line rewrapped — the needle was still
# there, one newline further on. Operate on the span the guard reads instead.
m = re.search(r"\*\*5\..*?(?=\*\*6\.)", t, re.S)
assert m, "PLANT DID NOT LAND: canon 5 span not found"
assert "\u2192" in m.group(0), "PLANT DID NOT LAND: canon 5 names no enforcement already"
_planted = t[:m.start()] + m.group(0).replace("\u2192", "to") + t[m.end():]
assert _planted != t, "PLANT DID NOT LAND"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/cn3-copy/test/validate.py; then
  echo "ERROR: validator passed with canons must keep naming their enforcement broken"
  exit 1
else
  echo "OK: validator correctly FAILs — canons must keep naming their enforcement"
fi
