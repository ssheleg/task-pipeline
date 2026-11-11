#!/usr/bin/env bash
# name: Negative self-test (an em dash in a string a script prints)
set -eu
rm -rf /tmp/em2-copy && cp -R . /tmp/em2-copy
python3 - <<'EOF2'
p = "/tmp/em2-copy/plugins/task-pipeline/skills/task-pipeline/scripts/short_path.py"
t = open(p, encoding="utf-8").read()
needle = 'return False, "full flow: " + "; ".join(why)'
assert t.count(needle) == 1, "PLANT DID NOT LAND: em2: the full-flow line moved"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, 'return False, "full flow — " + "; ".join(why)', 1))
EOF2
if python3 /tmp/em2-copy/test/validate.py 2>&1 | grep -q "scripts/short_path.py"; then
  echo "OK: validator FAILs: a printed string carries no em dash"
else
  echo "ERROR: an em dash in a printed string passed"; exit 1
fi
