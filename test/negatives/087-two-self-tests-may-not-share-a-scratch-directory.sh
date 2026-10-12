#!/usr/bin/env bash
# name: Negative self-test (two self-tests may not share a scratch directory)
set -eu
rm -rf /tmp/scratchdupe-copy && cp -R . /tmp/scratchdupe-copy
python3 - <<'EOF'
import os, sys
sys.path.insert(0, "/tmp/scratchdupe-copy/test")
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
d = "/tmp/scratchdupe-copy/test/negatives"
old = "rm -rf /tmp/hyg-verdict-copy && cp -R . /tmp/hyg-verdict-copy"
# The file that RUNS the line, not one that quotes it inside a heredoc.
hits = [f for f in sorted(os.listdir(d))
        if old in [l.strip() for l in open(os.path.join(d, f), encoding="utf-8")]]
assert hits, "plant did not land: no check runs the hyg-verdict copy"
p = os.path.join(d, hits[0])
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(t.replace(old, "cp -R . /tmp/rel-copy", 1))
assert sum(l.count("cp -R . /tmp/rel-copy") for l in guard_view(d)) >= 2, "plant did not land"
EOF
if python3 /tmp/scratchdupe-copy/test/validate.py; then
  echo "ERROR: validator passed with two self-tests sharing a scratch dir"
  exit 1
else
  echo "OK: validator rejects a reused scratch directory"
fi
