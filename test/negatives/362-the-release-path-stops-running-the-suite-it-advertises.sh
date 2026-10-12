#!/usr/bin/env bash
# name: Negative self-test (the release path stops running the suite it advertises)
set -eu
rm -rf /tmp/rel1-copy && cp -R . /tmp/rel1-copy
python3 - <<'EOF'
p = "/tmp/rel1-copy/.github/workflows/release.yml"
t = open(p, encoding="utf-8").read()
n = 'npm run test:all'
assert n in t, "PLANT DID NOT LAND: rel1"
_planted = t.replace(n, 'npm test', 1)
assert _planted != t, "PLANT DID NOT LAND: rel1"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/rel1-copy/test/validate.py 2>&1 | grep -q 'publishes without running'; then
  echo "OK: validator FAILs — a tag is not evidence"
else
  echo "ERROR: the release path can ship a red suite again, which it has done twice"
  exit 1
fi
