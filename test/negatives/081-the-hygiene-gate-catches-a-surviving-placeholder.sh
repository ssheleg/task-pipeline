#!/usr/bin/env bash
# name: Negative self-test (the hygiene gate catches a surviving placeholder)
set -eu
rm -rf /tmp/hyg2 && mkdir -p /tmp/hyg2
cp plugins/task-pipeline/skills/task-pipeline/templates/hygiene.sh /tmp/hyg2/gate.sh
echo "clean" > /tmp/hyg2/base.md
cd /tmp/hyg2
python3 - <<'EOF'
open('c2.py','w').write('# TODO: finish this\ndef f(): pass\n')
EOF
test -s c2.py || { echo "ERROR: plant did not land — c2.py is empty"; exit 1; }
if bash gate.sh; then
  echo "ERROR: hygiene gate passed with a surviving placeholder present"
  exit 1
else
  echo "OK: hygiene gate rejects a surviving placeholder"
fi
