#!/usr/bin/env bash
# name: Negative self-test (a release entry that talks about guards without a readable count)
set -eu
rm -rf /tmp/cl9-copy && cp -R . /tmp/cl9-copy
python3 - <<'EOF'
import re
p = "/tmp/cl9-copy/CHANGELOG.md"
t = open(p, encoding="utf-8").read()
# DERIVED, not literal. This probe held `Guards: A -> **B**` as a hard-coded
# string and broke on three consecutive releases, once letting a red CI reach
# main. A needle that has to be maintained is a needle that goes stale between
# the change and the run.
# Same scope as the guard: the TOPMOST `## ` section, `## Unreleased` since B-104.
heads = [m.start() for m in re.finditer(r"^## ", t, re.M)]
assert len(heads) >= 2, "PLANT DID NOT LAND: fewer than two `## ` sections"
top = t[heads[0]:heads[1]]
# SEED THE PRECONDITION, never inherit it. Both of this file's CHANGELOG
# count probes asserted that the topmost section already stated a guard
# count — and a release whose entry legitimately says nothing about guards
# (v1.78.0 removed a name from two printed lines) left them with nothing to
# plant. They reported BROKEN and held the release, correctly as a signal
# and wrongly as a finding: the sibling probe at `## Unreleased` had already
# learned this and says so in its own comment. The count written here is
# DERIVED from the same thing the guard counts, because a literal is what
# went stale on three consecutive releases.
# Counted by the runner's own loader over the directory the guard counts —
# the workflow held these steps until v1.93.0.
import sys
sys.path.insert(0, "/tmp/cl9-copy/test")
import negatives
neg = sum(1 for n, _s in negatives.load_checks("/tmp/cl9-copy/test/negatives")
          if n.startswith(negatives.MARKER))
if not re.search(r"Guards:\s*\d+\s*(?:\u2192|->)\s*\*{0,2}\d+", top):
    top = top.rstrip("\n") + f"\n\nGuards: {neg - 1} \u2192 **{neg}**.\n\n"
    t = t[:heads[0]] + top + t[heads[1]:]
    heads = [x.start() for x in re.finditer(r"^## ", t, re.M)]
top = t[heads[0]:heads[1]]
m = re.search(r"Guards:\s*(\d+)\s*(?:\u2192|->)\s*(\*{0,2})(\d+)(\*{0,2})", top)
assert m, "PLANT DID NOT LAND: the topmost section states no readable guard count"
# Talks about guards, states NO readable count — which is the finding. Dropping
# only the colon left `Guards 390 -> 412`, and the guard's own regex tolerates
# that, so the plant read as accepted when the guard was working: a plant weaker
# than the check it probes reports a hole that is not there.
patched = top[:m.start()] + "the guard suite grew again" + top[m.end():]
open(p, "w", encoding="utf-8").write(t[:heads[0]] + patched + t[heads[1]:])
EOF
if python3 /tmp/cl9-copy/test/validate.py 2>&1 | grep -q "states no .Guards: N"; then
  echo "OK: validator FAILs — a count-shaped sentence with no readable count is not silence"
else
  echo "ERROR: the guard went dormant on a reworded entry and the suite stayed green"
  exit 1
fi
