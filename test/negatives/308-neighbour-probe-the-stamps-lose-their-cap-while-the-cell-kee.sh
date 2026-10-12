#!/usr/bin/env bash
# name: Negative self-test (neighbour probe — the stamps lose their cap while the cell keeps another)
set -eu
rm -rf /tmp/nb01-copy && cp -R . /tmp/nb01-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): both caps are numbers this repository can change
# — the stamp cap already moved once — and the needle named both, so a
# single cap edit would have taken the neighbour probe with it.
import re
p = "/tmp/nb01-copy/plugins/task-pipeline/skills/task-pipeline/references/retrospective.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"\*\*Standing instructions\*\* \(max \*\*(\d+)\*\*\) \u00b7 "
              r"\*\*Run stamps\*\* \(max \*\*\d+\*\*, oldest rotate out\)", t)
assert m, "PLANT DID NOT LAND: nb01"
# Break the subject AND leave the neighbour's cap in the same cell — on the
# other side of the separator, which is where the narrowed version fell.
open(p, "w", encoding="utf-8").write(t.replace(
    m.group(0),
    "**Run stamps** (one line each) \u00b7 **Standing instructions** (max **%s**)"
    % m.group(1), 1))
EOF
if python3 /tmp/nb01-copy/test/validate.py 2>&1 | grep -q 'run stamps are given no cap'; then
  echo "OK: validator FAILs — the neighbour's cap does not answer for the stamps, on either side of the separator"
else
  echo "ERROR: the stamps lost their cap and the standing instructions' own cap answered for them"
  exit 1
fi
