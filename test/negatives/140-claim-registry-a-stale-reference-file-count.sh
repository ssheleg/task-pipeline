#!/usr/bin/env bash
# name: Negative self-test (claim registry — a stale reference-file count)
set -eu
rm -rf /tmp/cr5-copy && cp -R . /tmp/cr5-copy
python3 - <<'EOF'
p = "/tmp/cr5-copy/SKILL-CARD.md"
t = open(p, encoding="utf-8").read()
anchor = "## What to check before you trust it"
assert anchor in t, "PLANT DID NOT LAND: anchor absent before edit"
t = t.replace(anchor, anchor + "\n\nThere are 26 files under `references/`.\n", 1)
open(p, "w", encoding="utf-8").write(t)
assert "26 files under" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/cr5-copy/test/validate.py; then
  echo "ERROR: validator passed a reference-file count that disagrees with the directory"
  exit 1
else
  echo "OK: validator correctly FAILs — the reference-file class is armed"
fi
