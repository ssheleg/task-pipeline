#!/usr/bin/env bash
# name: Negative self-test (a step wiping a scratch dir it does not own)
set -eu
rm -rf /tmp/mm-copy && cp -R . /tmp/mm-copy
python3 - <<'EOF'
import os, sys
sys.path.insert(0, "/tmp/mm-copy/test")
import negatives
def guard_view(d):
    # The guard's own reading: every body, heredocs stripped, because a plant that
    # QUOTES a scratch path as test data is not a step that uses it.
    out, inh = [], False
    for l in "\n".join(s for _n, s in negatives.load_checks(d)).splitlines():
        if "<<'EOF'" in l:
            inh = True
            continue
        if inh:
            if l.strip() == "EOF":
                inh = False
            continue
        out.append(l)
    return out
d = "/tmp/mm-copy/test/negatives"
needle = "rm -rf /tmp/sweep-copy-2 && cp -R . /tmp/sweep-copy-2"
planted = "rm -rf /tmp/sweep-copy && cp -R . /tmp/sweep-copy-2"
# The file that RUNS the pair — this plant quotes it too, inside its heredoc.
hits = [f for f in sorted(os.listdir(d))
        if needle in [l.strip() for l in open(os.path.join(d, f), encoding="utf-8")]]
assert hits, "PLANT DID NOT LAND: the repaired pair is not where the guard reads it"
p = os.path.join(d, hits[0])
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(t.replace(needle, planted, 1))
assert planted in guard_view(d), "PLANT DID NOT LAND: the guard's view holds no such step"
EOF
if python3 /tmp/mm-copy/test/validate.py; then
  echo "ERROR: a step deleting a directory it does not own passed — harmless serially, a race in parallel"
  exit 1
else
  echo "OK: validator correctly FAILs — rm and cp in one step name the same directory"
fi
