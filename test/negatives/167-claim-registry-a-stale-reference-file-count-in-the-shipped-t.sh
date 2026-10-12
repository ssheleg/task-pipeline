#!/usr/bin/env bash
# name: Negative self-test (claim registry — a stale reference-file count in the SHIPPED template)
set -eu
rm -rf /tmp/cr5b-copy && cp -R . /tmp/cr5b-copy
python3 - <<'EOF'
# The incident this plant is for: three shipped surfaces said "34 reference files"
# over a directory of 35, and `npm test` printed `reference files: dormant`. Two
# holes at once — the pattern knew only the word order "N files under
# `references/`", and the corpus was eight named files plus references/**, so
# templates/ and scripts/ were never opened. Both are fixed; this proves it, in
# the template AND in the wording that was invisible.
p = "/tmp/cr5b-copy/plugins/task-pipeline/skills/task-pipeline/templates/run.md"
t = open(p, encoding="utf-8").read()
# DERIVED. Pinned to "The bundle is 35 reference files" this stopped landing
# the day a reference file was added -- `certification.md`, and the count went
# to 36 -- so the plant reported BROKEN and the guard it probes went unexercised
# on the release that changed the very number it guards.
import re as _re
m = _re.search(r"The bundle is (\d+) reference files", t)
assert m, "PLANT DID NOT LAND: the template states no reference-file count"
wrong = str(int(m.group(1)) - 1)
open(p, "w", encoding="utf-8").write(
    t[:m.start(1)] + wrong + t[m.end(1):])
assert f"The bundle is {wrong} reference files" in open(p, encoding="utf-8").read(), \
    "PLANT DID NOT LAND: the count did not change"
EOF
if python3 /tmp/cr5b-copy/test/validate.py; then
  echo "ERROR: validator passed '34 reference files' in a shipped template over a directory of 35"
  exit 1
else
  echo "OK: validator correctly FAILs — templates/ and scripts/ are in the corpus and the class reads any phrasing"
fi
