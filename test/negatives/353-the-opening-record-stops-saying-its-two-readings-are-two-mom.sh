#!/usr/bin/env bash
# name: Negative self-test (the opening record stops saying its two readings are two moments)
set -eu
rm -rf /tmp/res21-copy && cp -R . /tmp/res21-copy
python3 - <<'EOF'
p = "/tmp/res21-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
n = "taken at two different moments"
assert n in t, "PLANT DID NOT LAND: res21"
_planted = t.replace(n, "taken during the run", 1)
assert _planted != t, "PLANT DID NOT LAND: res21"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res21-copy/test/validate.py 2>&1 | grep -q "two readings are two moments"; then
  echo "OK: validator FAILs — the finding is that both observations were accurate at different moments"
else
  echo "ERROR: the externally cited record went back to reading as a single instant"
  exit 1
fi
