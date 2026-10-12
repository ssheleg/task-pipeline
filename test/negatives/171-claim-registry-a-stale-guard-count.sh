#!/usr/bin/env bash
# name: Negative self-test (claim registry — a stale guard count)
set -eu
rm -rf /tmp/cr6-copy && cp -R . /tmp/cr6-copy
python3 - <<'EOF'
p = "/tmp/cr6-copy/README.md"
t = open(p, encoding="utf-8").read()
anchor = "## Contributing"
assert anchor in t, "PLANT DID NOT LAND: anchor absent before edit"
t = t.replace(anchor, "The suite carries 46 guards.\n\n" + anchor, 1)
open(p, "w", encoding="utf-8").write(t)
assert "46 guards" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/cr6-copy/test/validate.py; then
  echo "ERROR: validator passed a guard count that disagrees with the workflow"
  exit 1
else
  echo "OK: validator correctly FAILs — the founding class is still armed"
fi
