#!/usr/bin/env bash
# name: Negative self-test (the trigger regex renamed out from under its own comparison)
set -eu
rm -rf /tmp/tg3-copy && cp -R . /tmp/tg3-copy
python3 - <<'EOF'
p = "/tmp/tg3-copy/test/validate.py"
t = open(p, encoding="utf-8").read()
assert "_UNRES_RE = re.compile" in t, "PLANT DID NOT LAND: anchor absent"
open(p, "w", encoding="utf-8").write(
    t.replace("_UNRES_RE = re.compile", "_UNRESOLVED_RE = re.compile")
     .replace("_UNRES_RE.match", "_UNRESOLVED_RE.match"))
EOF
if python3 /tmp/tg3-copy/test/validate.py; then
  echo "ERROR: the comparison lost its source and passed everything in silence"
  exit 1
else
  echo "OK: validator correctly FAILs — a guard with no source says so"
fi
