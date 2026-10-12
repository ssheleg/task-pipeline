#!/usr/bin/env bash
# name: Negative self-test (a stated count of the rotation axes, the dormant class proven)
set -eu
rm -rf /tmp/axis8-copy && cp -R . /tmp/axis8-copy
python3 - <<'EOF'
p = "/tmp/axis8-copy/README.md"
t = open(p, encoding="utf-8").read()
needle = "when the second overtakes the first, **rotate the axis**."
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, needle + " There are five rotation axes.", 1))
assert "five rotation axes" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/axis8-copy/test/validate.py; then
  echo "ERROR: validator passed a restated axis count — a class that is dormant is not a class that works"
  exit 1
else
  echo "OK: validator correctly FAILs — the dormant class has now been watched firing"
fi
