#!/usr/bin/env bash
# name: Negative self-test (claim registry — a stale dated-eval-run count)
set -eu
rm -rf /tmp/cr7-copy && cp -R . /tmp/cr7-copy
python3 - <<'EOF'
p = "/tmp/cr7-copy/docs/DOCMAP.md"
t = open(p, encoding="utf-8").read()
anchor = "## Ratchets"
assert anchor in t, "PLANT DID NOT LAND: anchor absent before edit"
t = t.replace(anchor, anchor + "\n\nDated eval runs recorded: 0.\n", 1)
open(p, "w", encoding="utf-8").write(t)
assert "Dated eval runs recorded: 0" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/cr7-copy/test/validate.py; then
  echo "ERROR: validator passed a dated-run count that disagrees with evals/run.py"
  exit 1
else
  echo "OK: validator correctly FAILs — the eval-run class is armed"
fi
