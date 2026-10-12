#!/usr/bin/env bash
# name: Negative self-test (the hygiene gate catches a blank line inside a table)
set -eu
rm -rf /tmp/hyg7 && mkdir -p /tmp/hyg7
cp plugins/task-pipeline/skills/task-pipeline/templates/hygiene.sh /tmp/hyg7/gate.sh
cd /tmp/hyg7
python3 - <<'EOF'
open('t7.md','w').write(
    '# Ledger\n\n| id | what |\n|---|---|\n| 1 | first |\n\n| 2 | second |\n')
EOF
test -s t7.md || { echo "ERROR: plant did not land — t7.md is empty"; exit 1; }
if bash gate.sh; then
  echo "ERROR: hygiene gate passed with a blank line splitting a table"
  exit 1
else
  echo "OK: hygiene gate rejects a blank line inside a table"
fi
