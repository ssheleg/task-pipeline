#!/usr/bin/env bash
# name: Negative self-test (the ratchet-matcher section is deleted)
set -eu
rm -rf /tmp/ri01-copy && cp -R . /tmp/ri01-copy
python3 - <<'EOF'
p = "/tmp/ri01-copy/plugins/task-pipeline/skills/task-pipeline/references/gates.md"
t = open(p, encoding="utf-8").read()
n = "## A ratchet's matcher is itself a check"
assert n in t, "PLANT DID NOT LAND: ri01"
_planted = t.replace(n, '## Matchers', 1)
assert _planted != t, "PLANT DID NOT LAND: ri01"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ri01-copy/test/validate.py 2>&1 | grep -q "no section on a ratchet's matcher"; then
  echo "OK: validator FAILs — a matcher looser than its subject shrinks the ratchet"
else
  echo "ERROR: the rule went missing and nothing objected — a matcher looser than its subject shrinks the ratchet"
  exit 1
fi
