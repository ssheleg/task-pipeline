#!/usr/bin/env bash
# name: Negative self-test (claim registry — a restated rule count that disagrees)
set -eu
rm -rf /tmp/cr1-copy && cp -R . /tmp/cr1-copy
python3 - <<'EOF'
p = "/tmp/cr1-copy/README.md"
t = open(p, encoding="utf-8").read()
anchor = "## Contributing"
assert anchor in t, "PLANT DID NOT LAND: anchor absent before edit"
t = t.replace(anchor, "The doctrine ships 15 rules earned by failure.\n\n" + anchor, 1)
open(p, "w", encoding="utf-8").write(t)
assert "15 rules earned by failure" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/cr1-copy/test/validate.py; then
  echo "ERROR: validator passed a restated rule count that disagrees with learned.md"
  exit 1
else
  echo "OK: validator correctly FAILs — the claim registry caught a stale rule count"
fi
