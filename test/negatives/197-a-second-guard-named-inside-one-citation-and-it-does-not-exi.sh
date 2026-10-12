#!/usr/bin/env bash
# name: Negative self-test (a second guard named inside one citation, and it does not exist)
set -eu
rm -rf /tmp/cite2-copy && cp -R . /tmp/cite2-copy
python3 - <<'EOF'
p = "/tmp/cite2-copy/CONTRIBUTING.md"
t = open(p, encoding="utf-8").read()
# The cited message lost its trailing "as <unit>" when the cold guard stopped
# naming a unit — naming one is what had tied it to a wording. The plant
# follows the citation; what it proves is unchanged: the SECOND literal in a
# `*(guard: A and B)*` parenthetical is checked too, not just the first.
needle = "`states the cold-retirement condition in one unit only`"
assert needle in t, "PLANT DID NOT LAND: second citation absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, "`this guard does not exist anywhere`", 1))
assert "this guard does not exist anywhere" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/cite2-copy/test/validate.py; then
  echo "ERROR: only the first literal in a citation was checked — the rest rode free"
  exit 1
else
  echo "OK: validator correctly FAILs — every literal inside a *(guard: ...)* parenthetical is checked"
fi
