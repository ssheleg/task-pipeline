#!/usr/bin/env bash
# name: Negative self-test (the hygiene gate catches a duplicated adjacent block)
set -eu
rm -rf /tmp/hyg5 && mkdir -p /tmp/hyg5
cp plugins/task-pipeline/skills/task-pipeline/templates/hygiene.sh /tmp/hyg5/gate.sh
echo "clean" > /tmp/hyg5/base.md
cd /tmp/hyg5
python3 - <<'EOF'
open('c5.md','w').write('# t\n\nalpha\nbeta\ngamma\n\nalpha\nbeta\ngamma\n\ntail\n')
EOF
test -s c5.md || { echo "ERROR: plant did not land — c5.md is empty"; exit 1; }
if bash gate.sh; then
  echo "ERROR: hygiene gate passed with a duplicated adjacent block present"
  exit 1
else
  echo "OK: hygiene gate rejects a duplicated adjacent block"
fi
