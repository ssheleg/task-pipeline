#!/usr/bin/env bash
# name: Negative self-test (an `## Unreleased` section parked below a released version)
set -eu
rm -rf /tmp/unr2-copy && cp -R . /tmp/unr2-copy
python3 - <<'EOF'
# Under a release heading the section reads as a claim about the past, and the count
# check would never reach it — the silent shape B-104 was made of.
import re
# INSERTS the section rather than moving one. After a release there IS no
# `## Unreleased` — the release absorbs it — so a plant that relocates an existing
# one stops landing on every release commit, which is where it matters most.
p = "/tmp/unr2-copy/CHANGELOG.md"
t = open(p, encoding="utf-8").read()
# The candidate may already have a legitimate top Unreleased section. Remove it
# in this fixture before placing the single malformed section below a release.
t = re.sub(r"^## Unreleased[^\n]*\n.*?(?=^## |\Z)", "", t, flags=re.M | re.S)
m = re.search(r"^## v[0-9][^\n]*\n", t, re.M)
assert m, "PLANT DID NOT LAND: no released version heading to park below"
nxt = re.search(r"^## ", t[m.end():], re.M)
at = m.end() + nxt.start() if nxt else len(t)
open(p, "w", encoding="utf-8").write(
    t[:at] + "## Unreleased\n\nGuards: 1 -> 2, parked under a release.\n\n" + t[at:])
out = open(p, encoding="utf-8").read()
assert out.index("## Unreleased") > out.index(m.group(0)), "PLANT DID NOT LAND"
EOF
output=$(python3 /tmp/unr2-copy/test/validate.py 2>&1) && status=0 || status=$?
if [ "$status" -eq 0 ] || ! printf '%s\n' "$output" | grep -q 'an `## Unreleased` section sits below a released version'; then
  echo "ERROR: validator passed an Unreleased section sitting under a release"
  exit 1
else
  echo "OK: validator correctly FAILs — Unreleased above every version heading, or it is unreadable"
fi
