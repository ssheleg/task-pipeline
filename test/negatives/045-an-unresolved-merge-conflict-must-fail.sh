#!/usr/bin/env bash
# name: Negative self-test (an unresolved merge conflict must fail)
set -eu
rm -rf /tmp/conflict-copy && cp -R . /tmp/conflict-copy
python3 - <<'EOF'
# build the markers at runtime — spelling them here would trip the guard
# on this very file
o, c, s = "<" * 7, ">" * 7, "=" * 7
p = "/tmp/conflict-copy/README.md"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(
    t + f"\n{o} HEAD\nours\n{s}\ntheirs\n{c} branch\n")
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: an-unresolved-merge-conflict-must-fa"
EOF
if python3 /tmp/conflict-copy/test/validate.py; then
  echo "ERROR: validator passed a file with unresolved conflict markers — in a prose repo that ships as doctrine"
  exit 1
else
  echo "OK: validator rejects unresolved merge conflict markers"
fi
