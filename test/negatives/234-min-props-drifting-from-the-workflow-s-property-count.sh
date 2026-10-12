#!/usr/bin/env bash
# name: Negative self-test (MIN_PROPS drifting from the workflow's property count)
set -eu
rm -rf /tmp/mp-copy && cp -R . /tmp/mp-copy
python3 - <<'EOF'
import re
p = "/tmp/mp-copy/test/negatives.py"
t = open(p, encoding="utf-8").read()
m = re.search(r"^MIN_PROPS\s*=\s*(\d+)", t, re.M)
assert m, "PLANT DID NOT LAND: MIN_PROPS is not where the guard reads it"
open(p, "w", encoding="utf-8").write(
    t[:m.start(1)] + str(int(m.group(1)) - 1) + t[m.end(1):])
EOF
if python3 /tmp/mp-copy/test/validate.py; then
  echo "ERROR: the property floor drifted below the count, exactly as MIN_EXPECTED did twice"
  exit 1
else
  echo "OK: validator correctly FAILs — both floors are tied to the workflow now, not only one"
fi
