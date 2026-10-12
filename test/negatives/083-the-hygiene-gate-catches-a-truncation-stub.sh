#!/usr/bin/env bash
# name: Negative self-test (the hygiene gate catches a truncation stub)
set -eu
rm -rf /tmp/hyg4 && mkdir -p /tmp/hyg4
cp plugins/task-pipeline/skills/task-pipeline/templates/hygiene.sh /tmp/hyg4/gate.sh
echo "clean" > /tmp/hyg4/base.md
cd /tmp/hyg4
python3 - <<'EOF'
open('c4.js','w').write('function a() {}\n// ... existing code ...\n')
EOF
test -s c4.js || { echo "ERROR: plant did not land — c4.js is empty"; exit 1; }
if bash gate.sh; then
  echo "ERROR: hygiene gate passed with a truncation stub present"
  exit 1
else
  echo "OK: hygiene gate rejects a truncation stub"
fi
