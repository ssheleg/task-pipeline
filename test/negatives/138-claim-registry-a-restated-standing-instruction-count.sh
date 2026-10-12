#!/usr/bin/env bash
# name: Negative self-test (claim registry — a restated standing-instruction count)
set -eu
rm -rf /tmp/cr2-copy && cp -R . /tmp/cr2-copy
python3 - <<'EOF'
p = "/tmp/cr2-copy/docs/DOCMAP.md"
t = open(p, encoding="utf-8").read()
anchor = "## Ratchets"
assert anchor in t, "PLANT DID NOT LAND: anchor absent before edit"
t = t.replace(anchor, anchor + "\n\nThe retro currently holds 2 of a hard cap of 10.\n", 1)
open(p, "w", encoding="utf-8").write(t)
assert "2 of a hard cap of 10" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/cr2-copy/test/validate.py; then
  echo "ERROR: validator passed a standing-instruction count that disagrees with the retro"
  exit 1
else
  echo "OK: validator correctly FAILs — the claim registry caught a stale ratchet"
fi
