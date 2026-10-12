#!/usr/bin/env bash
# name: Negative self-test (the hygiene gate refuses an undeclared floor)
set -eu
rm -rf /tmp/hyg8 && mkdir -p /tmp/hyg8
cp plugins/task-pipeline/skills/task-pipeline/templates/hygiene.sh /tmp/hyg8/gate.sh
cd /tmp/hyg8
python3 - <<'EOF'
p = 'gate.sh'
t = open(p, encoding='utf-8').read()
needle = 'HYGIENE_FLOOR_7=${HYGIENE_FLOOR_7:-0}\n'
assert needle in t, "PLANT DID NOT LAND: floor 7 is not declared in the gate"
open(p, 'w', encoding='utf-8').write(t.replace(needle, ''))
open('t8.md','w').write('# Ledger\n\n| id | what |\n|---|---|\n| 1 | first |\n\n| 2 | second |\n')
EOF
if bash gate.sh; then
  echo "ERROR: hygiene gate passed while judging a check whose floor is undeclared"
  exit 1
else
  echo "OK: hygiene gate refuses an undeclared floor instead of printing ok"
fi
