#!/usr/bin/env bash
# name: Negative self-test (the distrust marker keeps its sigil, even wrapped)
set -eu
rm -rf /tmp/gs06-copy && cp -R . /tmp/gs06-copy
python3 - <<'EOF'
p = "/tmp/gs06-copy/README.md"
t = open(p, encoding="utf-8").read()
needle = "`⚠ not trusted for reach until\nrefreshed`"
assert needle in t, "PLANT DID NOT LAND: the wrapped marker is absent before edit"
t = t.replace(needle, "`not trusted for reach until\nrefreshed`")
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/gs06-copy/test/validate.py; then
  echo "ERROR: validator passed with the marker's sigil dropped across a line wrap"
  exit 1
else
  echo "OK: validator correctly FAILs — the distrust marker keeps its sigil, even wrapped"
fi
