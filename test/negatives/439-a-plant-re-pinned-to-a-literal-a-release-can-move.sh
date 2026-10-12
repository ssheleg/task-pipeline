#!/usr/bin/env bash
# name: Negative self-test (a plant re-pinned to a literal a release can move)
set -eu
rm -rf /tmp/anc1-copy && cp -R . /tmp/anc1-copy
python3 - <<'EOF'
# B-113, the class this plant guards: a needle pinned to a value the tree
# will move is a check the next release switches off, and it reports green
# while it does. Four confirmations, three of them caused by the repository
# getting HEALTHIER — a re-derived board, the first blind eval runs, the
# first honest run stamp.
#
# The plant un-derives one needle: it finds a `\d+` inside a plant's own
# regex and writes digits over it, which is precisely the edit the guard
# exists to refuse. The needle here is the escape `\d+` and carries no
# value of its own, so this plant cannot pin the thing it plants.
#
# It does not trust the FIRST such regex to be the right one. A plant that
# picks a position and hopes is the class this whole release is about: the
# first `\d+` in the file may sit on the write side, or in a look whose
# subject is not file text, and pinning it would change something real
# while proving nothing. So each candidate is tried and the census itself
# is asked whether a new refusal appeared — R-001's landed-mutation rule,
# applied to the check that enforces it.
import os, re, sys
sys.path.insert(0, "/tmp/anc1-copy/test")
import anchors
# The census reads test/negatives/, one file per check, since v1.93.0.
d = "/tmp/anc1-copy/test/negatives"
before = len(anchors.findings(d))
planted = None
for f in sorted(os.listdir(d)):
    p = os.path.join(d, f)
    orig = open(p, encoding="utf-8").read()
    for m in re.finditer(r'r"([^"\n]{4,}?)\\d\+([^"\n]*)"', orig):
        cand = orig[:m.start()] + 'r"%s22%s"' % (m.group(1), m.group(2)) + orig[m.end():]
        open(p, "w", encoding="utf-8").write(cand)
        if len(anchors.findings(d)) > before:
            planted = m.group(0)
            break
        open(p, "w", encoding="utf-8").write(orig)
    if planted:
        break
assert planted, ("PLANT DID NOT LAND: no derived regex needle could be "
                 "re-pinned into a needle the census reads")
print("re-pinned %s" % planted[:60])
EOF
if python3 /tmp/anc1-copy/test/validate.py 2>&1 | grep -q "is anchored on a value a release can move"; then
  echo "OK: validator FAILs — the cheap gate refuses a pinned anchor, instead of a 35-minute suite finding it a release later"
else
  echo "ERROR: a plant was re-pinned to a literal and the gate said nothing — the four B-113 confirmations were each found this way, one release after the damage"
  exit 1
fi
