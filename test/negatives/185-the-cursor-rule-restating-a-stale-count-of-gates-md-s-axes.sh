#!/usr/bin/env bash
# name: Negative self-test (the Cursor rule restating a stale count of gates.md's axes)
set -eu
rm -rf /tmp/axis7-copy && cp -R . /tmp/axis7-copy
python3 - <<'EOF'
p = "/tmp/axis7-copy/cursor/rules/task-pipeline.mdc"
t = open(p, encoding="utf-8").read()
needle = "## Gates: three axes, and how to build one that cannot lie"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, "## Gates: two axes, and how to build one that cannot lie", 1))
assert "Gates: two axes" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/axis7-copy/test/validate.py; then
  echo "ERROR: validator passed a shipped surface the claim registry could not see"
  exit 1
else
  echo "OK: validator correctly FAILs — the Cursor rule and the command are in the registry corpus"
fi
