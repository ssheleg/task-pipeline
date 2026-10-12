#!/usr/bin/env bash
# name: Negative self-test (the seam loses its unlooked fallback)
set -eu
rm -rf /tmp/ri07-copy && cp -R . /tmp/ri07-copy
python3 - <<'EOF'
p = "/tmp/ri07-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
t = open(p, encoding="utf-8").read()
n = 'the table says so under `unlooked`'
assert n in t, "PLANT DID NOT LAND: ri07"
_planted = t.replace(n, 'the table notes it', 1)
assert _planted != t, "PLANT DID NOT LAND: ri07"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ri07-copy/test/validate.py 2>&1 | grep -q 'the `unlooked` fallback'; then
  echo "OK: validator FAILs — where no check spans the seam, two green rows are a false whole"
else
  echo "ERROR: the rule went missing and nothing objected — where no check spans the seam, two green rows are a false whole"
  exit 1
fi
