#!/usr/bin/env bash
# name: Negative self-test (the authorization floor leaves the file that defines the mode)
set -eu
rm -rf /tmp/lp05-copy && cp -R . /tmp/lp05-copy
python3 - <<'EOF'
p = "/tmp/lp05-copy/plugins/task-pipeline/skills/task-pipeline/references/continuity.md"
t = open(p, encoding="utf-8").read()
n = 'authorization'
assert t.count(n) >= 3, "PLANT DID NOT LAND: lp05 — fewer occurrences than expected"
# The guard reads _flatten()ed text, where a line-wrapped occurrence rejoins:
# replacing the single-line copies left the wrapped one matching and the guard
# silent. Plant on the word itself so no form of the phrase survives.
open(p, "w", encoding="utf-8").write(t.replace(n, 'permission', -1))
EOF
if python3 /tmp/lp05-copy/test/validate.py 2>&1 | grep -q 'keeps arming from reading as blanket permission'; then
  echo "OK: validator FAILs — arming may never read as blanket permission"
else
  echo "ERROR: the deploy floor's distinction vanished from continuity.md"
  exit 1
fi
