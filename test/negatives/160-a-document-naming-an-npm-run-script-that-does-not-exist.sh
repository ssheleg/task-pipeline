#!/usr/bin/env bash
# name: Negative self-test (a document naming an `npm run` script that does not exist)
set -eu
rm -rf /tmp/gloss2-copy && cp -R . /tmp/gloss2-copy
python3 - <<'EOF'
p = "/tmp/gloss2-copy/CLAUDE.md"
t = open(p, encoding="utf-8").read()
anchor = "## Commands"
assert anchor in t, "PLANT DID NOT LAND: anchor absent before edit"
t = t.replace(anchor, anchor + "\n\nRun `npm run test:negatives-fast` before pushing.\n", 1)
open(p, "w", encoding="utf-8").write(t)
assert "test:negatives-fast" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/gloss2-copy/test/validate.py; then
  echo "ERROR: validator passed a document quoting a dead npm script as runnable"
  exit 1
else
  echo "OK: validator correctly FAILs — a named npm script must exist in package.json"
fi
