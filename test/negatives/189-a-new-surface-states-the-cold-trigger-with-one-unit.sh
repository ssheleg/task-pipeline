#!/usr/bin/env bash
# name: Negative self-test (a NEW surface states the cold trigger with one unit)
set -eu
rm -rf /tmp/coldnew-copy && cp -R . /tmp/coldnew-copy
python3 - <<'EOF'
p = "/tmp/coldnew-copy/docs/DOCMAP.md"
t = open(p, encoding="utf-8").read()
t += "\n\nA rule retires when it has not fired in the last five run stamps.\n"
open(p, "w", encoding="utf-8").write(t)
assert "five run stamps" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/coldnew-copy/test/validate.py; then
  echo "ERROR: validator passed a surface that was never on any hand-written list"
  exit 1
else
  echo "OK: validator correctly FAILs — the corpus is discovered, so a new surface joins it by existing"
fi
