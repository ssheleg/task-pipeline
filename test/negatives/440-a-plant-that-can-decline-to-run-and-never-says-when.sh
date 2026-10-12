#!/usr/bin/env bash
# name: Negative self-test (a plant that can decline to run and never says when)
set -eu
rm -rf /tmp/anc2-copy && cp -R . /tmp/anc2-copy
python3 - <<'EOF'
# Dormant is not passing. A plant that prints SKIP proved nothing, and until
# B-113 the local runner folded such a plant into *all N guards provably
# reject* — the exact sentence the row is about. The half that is checkable
# in CI, where each plant is its own green step, is the declaration.
import os, re, sys
sys.path.insert(0, "/tmp/anc2-copy/test")
import anchors, negatives
d = "/tmp/anc2-copy/test/negatives"
m = name = None
for f, n, _s in negatives.scan(d)[0]:
    p = os.path.join(d, f)
    t = open(p, encoding="utf-8").read()
    m = re.search(r"(?m)^\s*#\s*dormant-when:.*\n(?:\s*#\s{2,}.*\n)*", t)
    if m:
        name = n
        open(p, "w", encoding="utf-8").write(t[:m.start()] + t[m.end():])
        break
assert m, "PLANT DID NOT LAND: no dormancy declaration to remove"
# On the value the guard reads: the census still calls it skip-capable, and now
# finds no dormancy declaration on it.
st = [s for s in anchors.every_check(d) if s.name == name]
assert st and st[0].skip_capable and not (st[0].dormancy or "").strip(), \
    "PLANT DID NOT LAND: the census still reads a dormancy declaration"
EOF
if python3 /tmp/anc2-copy/test/validate.py 2>&1 | grep -q "declares no .# dormant-when:"; then
  echo "OK: validator FAILs — a plant that declines to run says which state makes it decline, and what that costs"
else
  echo "ERROR: a plant kept its SKIP branch with nothing naming the state behind it"
  exit 1
fi
