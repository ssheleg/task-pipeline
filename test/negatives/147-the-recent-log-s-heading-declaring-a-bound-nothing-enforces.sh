#!/usr/bin/env bash
# name: Negative self-test (the Recent log's heading declaring a bound nothing enforces)
set -eu
rm -rf /tmp/rlog1-copy && cp -R . /tmp/rlog1-copy
python3 - <<'EOF'
# The heading read «entries from the last five run stamps» over 25 entries reaching
# back nine days, while the doctrine one file over said the section is capped by
# nothing. B-060 and B-069 were the same defect filed twice, and the file disclosed
# it about itself in its own honest-gaps section.
p = "/tmp/rlog1-copy/docs/evidence/retro.md"
t = open(p, encoding="utf-8").read()
needle = "## Recent log — narrative entries, uncapped and queried rather than read (newest first)"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, "## Recent log — entries from the last five run stamps (newest first)", 1))
assert "last five run stamps (newest first)" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rlog1-copy/test/validate.py; then
  echo "ERROR: validator passed a heading declaring a bound nothing enforces"
  exit 1
else
  echo "OK: validator correctly FAILs — a stated bound needs a mechanism, not a neighbour's wording"
fi
