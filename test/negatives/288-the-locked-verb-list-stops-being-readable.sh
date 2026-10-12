#!/usr/bin/env bash
# name: Negative self-test (the locked verb list stops being readable)
set -eu
rm -rf /tmp/rt12-copy && cp -R . /tmp/rt12-copy
python3 - <<'EOF'
p = "/tmp/rt12-copy/docs/evidence/specs/2026-08-03-default-routing-adoption-design.md"
t = open(p, encoding="utf-8").read()
n = '**work verbs, RU + EN:**'
assert n in t, "PLANT DID NOT LAND: rt12"
open(p, "w", encoding="utf-8").write(t.replace(n, '**work verbs (RU + EN):**', 1))
EOF
if python3 /tmp/rt12-copy/test/validate.py 2>&1 | grep -q 'must not be edited to suit a guard'; then
  echo "OK: validator FAILs — the anti-drift guard says so instead of going dormant"
else
  echo "ERROR: the locked list became unreadable and the guard went silent"
  exit 1
fi
