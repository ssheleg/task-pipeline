#!/usr/bin/env bash
# name: Negative self-test (the near-miss leaves the ratchet-matcher rule)
set -eu
rm -rf /tmp/ri02-copy && cp -R . /tmp/ri02-copy
python3 - <<'EOF'
p = "/tmp/ri02-copy/plugins/task-pipeline/skills/task-pipeline/references/gates.md"
t = open(p, encoding="utf-8").read()
n = 'feed its matcher a near-miss it must reject'
assert n in t, "PLANT DID NOT LAND: ri02"
_planted = t.replace(n, 'check that the matcher is sensible', 1)
assert _planted != t, "PLANT DID NOT LAND: ri02"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ri02-copy/test/validate.py 2>&1 | grep -q 'the near-miss is gone'; then
  echo "OK: validator FAILs — reacting is not discriminating"
else
  echo "ERROR: the rule went missing and nothing objected — reacting is not discriminating"
  exit 1
fi
