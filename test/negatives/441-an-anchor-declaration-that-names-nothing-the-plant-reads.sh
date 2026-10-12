#!/usr/bin/env bash
# name: Negative self-test (an anchor declaration that names nothing the plant reads)
set -eu
rm -rf /tmp/anc3-copy && cp -R . /tmp/anc3-copy
python3 - <<'EOF'
# The escape hatch may not become a silencer. A declaration naming a value
# this plant never looks for explains nothing and would silence the needle
# beside it — so the declaration has to resolve, the same rule this family
# applies to every other address a live document carries.
import os, re, sys
sys.path.insert(0, "/tmp/anc3-copy/test")
import anchors, negatives
d = "/tmp/anc3-copy/test/negatives"
m = name = None
for f, n, _s in negatives.scan(d)[0]:
    p = os.path.join(d, f)
    t = open(p, encoding="utf-8").read()
    m = re.search(r"(?m)^(\s*#\s*anchor:\s*)(\S+)", t)
    if m:
        name = n
        open(p, "w", encoding="utf-8").write(
            t[:m.start(2)] + "nothing-this-plant-reads" + t[m.end(2):])
        break
assert m, "PLANT DID NOT LAND: no anchor declaration to break"
st = [s for s in anchors.census(d) if s.name == name]
assert st and any(tg == "nothing-this-plant-reads" for tg, _r in st[0].declarations), \
    "PLANT DID NOT LAND: the census reads no such declaration"
EOF
if python3 /tmp/anc3-copy/test/validate.py 2>&1 | grep -q "names nothing this plant looks for"; then
  echo "OK: validator FAILs — a declaration is an explanation, and one that resolves to nothing is a switch"
else
  echo "ERROR: an anchor declaration could name anything at all and still exempt the needle beside it"
  exit 1
fi
