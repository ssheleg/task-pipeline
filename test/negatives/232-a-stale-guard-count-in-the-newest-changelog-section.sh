#!/usr/bin/env bash
# name: Negative self-test (a stale guard count in the newest CHANGELOG section)
set -eu
rm -rf /tmp/cl1-copy && cp -R . /tmp/cl1-copy
python3 - <<'EOF'
import re
p = "/tmp/cl1-copy/CHANGELOG.md"
t = open(p, encoding="utf-8").read()
# The guard reads the TOPMOST `## ` section, which since B-104 may be
# `## Unreleased` — the home the count needs between a tag and the next bump.
# Scoping this to `^## v` sent the plant into a released section, where the
# guard is correctly silent: a probe that lands somewhere real and proves
# nothing (R-001), which is the same mistake this comment already records one
# scope out. Derive the guard's own scope, never assume the heading's name.
heads = [x.start() for x in re.finditer(r"^## ", t, re.M)]
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
sys.path.insert(0, "/tmp/cl1-copy/test")
import negatives
neg = sum(1 for n, _s in negatives.load_checks("/tmp/cl1-copy/test/negatives")
          if n.startswith(negatives.MARKER))
if not re.search(r"Guards:\s*\d+\s*(?:\u2192|->)\s*\*{0,2}\d+", top):
    top = top.rstrip("\n") + f"\n\nGuards: {neg - 1} \u2192 **{neg}**.\n\n"
    t = t[:heads[0]] + top + t[heads[1]:]
    heads = [x.start() for x in re.finditer(r"^## ", t, re.M)]
top = t[heads[0]:heads[1]]
m = re.search(r"(Guards:\s*\d+\s*→\s*\*\*)(\d+)(\*\*)", top)
assert m, "PLANT DID NOT LAND: no guard count in the TOPMOST section"
patched = top[:m.start(2)] + str(int(m.group(2)) - 1) + top[m.end(2):]
open(p, "w", encoding="utf-8").write(t[:heads[0]] + patched + t[heads[1]:])
EOF
if python3 /tmp/cl1-copy/test/validate.py; then
  echo "ERROR: the release entry claimed a guard count test/negatives/ does not hold"
  exit 1
else
  echo "OK: validator correctly FAILs — the newest entry's counts are claims about now"
fi
