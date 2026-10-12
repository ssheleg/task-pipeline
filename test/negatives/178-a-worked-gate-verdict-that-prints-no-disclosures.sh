#!/usr/bin/env bash
# name: Negative self-test (a worked GATE verdict that prints no disclosures)
set -eu
rm -rf /tmp/disc-copy && cp -R . /tmp/disc-copy
python3 - <<'EOF'
p = "/tmp/disc-copy/plugins/task-pipeline/skills/task-pipeline/references/gates.md"
t = open(p, encoding="utf-8").read()
# Matched by SHAPE, not by the sentence: B-064 appended `· holds: 0` to this very
# line, and a literal needle went stale the same day. The plant removes whichever
# disclosure line sits under the GATE 9 example.
import re as _re
m = _re.search(r"^  abstained:[^\n]*\n", t, _re.M)
assert m, "PLANT DID NOT LAND: no disclosure line under a worked verdict"
open(p, "w", encoding="utf-8").write(t[:m.start()] + t[m.end():])
assert "abstained: 0 · unlooked: 4" not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/disc-copy/test/validate.py; then
  echo "ERROR: validator passed a GATE verdict that reads as 'verified' rather than as 'green, and here is what nobody claimed'"
  exit 1
else
  echo "OK: validator correctly FAILs — both disclosures print beside every worked verdict"
fi
