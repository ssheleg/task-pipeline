#!/usr/bin/env bash
# name: Negative self-test (a stale guard count in the `## Unreleased` section)
set -eu
rm -rf /tmp/unr1-copy && cp -R . /tmp/unr1-copy
python3 - <<'EOF'
# B-104: the count guard read the newest `## vX.Y.Z` section, so between a tag and
# the next bump a commit adding guards had nowhere to state the count — and writing
# it into the shipped version's section would edit a released record. This proves
# `## Unreleased` is READ, not merely tolerated.
import re
p = "/tmp/unr1-copy/CHANGELOG.md"
t = open(p, encoding="utf-8").read()
# The plant WRITES the count it is about to make stale, instead of hoping the
# tree has one. Immediately after a release `## Unreleased` is empty by
# design — there is no unreleased work and therefore no guard count — so a
# plant that required one landed on the day it was written and reported
# BROKEN on the first release after it. Creating the precondition is the
# only version that exercises the guard on any day.
# The section may not exist: after a release the release absorbs it, which is
# this repository's stated convention and the assumption the sibling plant
# below is built on. So create it where it belongs — above every version
# heading — and then make its count stale.
# `^## Unreleased` as a HEADING, never as a substring: this file discusses
# the section in prose — "the `## Unreleased` section" — and a bare `find`
# matched that sentence inside a released section, planting the stale count
# below a version heading where the topmost-section guard never looks. The
# plant landed and the guard stayed silent, which is the exact shape this
# whole negative suite exists to refuse.
h = re.search(r"^## Unreleased\b", t, re.M)
i = h.start() if h else -1
if i < 0:
    v = re.search(r"^## v[0-9]", t, re.M)
    assert v, "PLANT DID NOT LAND: no version heading to sit above"
    t = t[:v.start()] + "## Unreleased\n\nGuards: 1 → **999**\n\n" + t[v.start():]
else:
    end = i + len("## Unreleased")
    t = t[:end] + "\n\nGuards: 1 → **999**\n" + t[end:]
open(p, "w", encoding="utf-8").write(t)
after = open(p, encoding="utf-8").read()
assert "→ **999**" in after, "PLANT DID NOT LAND: the stale count was not written"
hh = re.search(r"^## Unreleased\b", after, re.M)
assert hh and hh.start() < after.index("→ **999**"), \
    "PLANT DID NOT LAND: the count is not under the Unreleased HEADING"
EOF
if python3 /tmp/unr1-copy/test/validate.py; then
  echo "ERROR: validator passed a guard count in Unreleased that disagrees with the workflow"
  exit 1
else
  echo "OK: validator correctly FAILs — the Unreleased section is where the count lives before a bump"
fi
