#!/usr/bin/env bash
# name: Negative self-test (the hygiene gate catches conflict markers)
set -eu
rm -rf /tmp/hyg1 && mkdir -p /tmp/hyg1
cp plugins/task-pipeline/skills/task-pipeline/templates/hygiene.sh /tmp/hyg1/gate.sh
echo "clean" > /tmp/hyg1/base.md
cd /tmp/hyg1
python3 - <<'EOF'
open('c1.md','w').write('a\n<<<<<<< HEAD\nx\n=======\ny\n>>>>>>> b\n')
EOF
test -s c1.md || { echo "ERROR: plant did not land — c1.md is empty"; exit 1; }
if bash gate.sh; then
  echo "ERROR: hygiene gate passed with conflict markers present"
  exit 1
else
  echo "OK: hygiene gate rejects conflict markers"
fi
