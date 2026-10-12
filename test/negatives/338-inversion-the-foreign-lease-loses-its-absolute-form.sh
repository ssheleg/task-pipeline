#!/usr/bin/env bash
# name: Negative self-test (INVERSION — the foreign lease loses its absolute form)
set -eu
rm -rf /tmp/res6-copy && cp -R . /tmp/res6-copy
python3 - <<'EOF'
p = "/tmp/res6-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
n = '- **A lease held by another agent is never released by this run**'
assert n in t, "PLANT DID NOT LAND: res6"
_planted = t.replace(n, '- **A lease held by another agent may be released once it looks stale**', 1)
assert _planted != t, "PLANT DID NOT LAND: res6"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res6-copy/test/validate.py 2>&1 | grep -q 'lost its absolute form'; then
  echo "OK: validator FAILs — 'never released' is guarded as a sentence, not as a topic"
else
  echo "ERROR: another agent's lease became releasable and the topic-level check saw no change"
  exit 1
fi
