#!/usr/bin/env bash
# name: Negative self-test (a gate script must keep its VERDICT block last)
set -eu
rm -rf /tmp/hyg-verdict-copy && cp -R . /tmp/hyg-verdict-copy
python3 - <<'EOF'
p = "/tmp/hyg-verdict-copy/plugins/task-pipeline/skills/task-pipeline/templates/hygiene.sh"
t = open(p, encoding="utf-8").read()
marker = "# ---------- VERDICT"
assert marker in t, "plant would not land: no VERDICT section marker"
t2 = t.replace(marker, "# ---------- verdict-renamed")
assert marker not in t2, "plant did not land"
open(p, "w", encoding="utf-8").write(t2)
EOF
if python3 /tmp/hyg-verdict-copy/test/validate.py; then
  echo "ERROR: validator passed with the VERDICT block renamed"
  exit 1
else
  echo "OK: validator requires the VERDICT block, on every gate script"
fi
