#!/usr/bin/env bash
# name: Negative self-test (a percentage reaching the exposure line)
set -eu
rm -rf /tmp/pct-copy && cp -R . /tmp/pct-copy
python3 - <<'EOF'
p = "/tmp/pct-copy/test/validate.py"
t = open(p, encoding="utf-8").read()
needle = 'f"  exposure: {_VERIF_NEVER} unverified'
assert needle in t, "PLANT DID NOT LAND: the exposure print is not where the guard reads it"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, 'f"  exposure: {_VERIF_NEVER}% unverified', 1))
EOF
if python3 /tmp/pct-copy/test/validate.py; then
  echo "ERROR: the exposure line rendered as a percentage — P(defect) is not computable from these inputs"
  exit 1
else
  echo "OK: validator correctly FAILs — the one rendering this line may never take"
fi
