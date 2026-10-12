#!/usr/bin/env bash
# name: Negative self-test (the hygiene gate catches an unterminated fence)
set -eu
rm -rf /tmp/hyg3 && mkdir -p /tmp/hyg3
cp plugins/task-pipeline/skills/task-pipeline/templates/hygiene.sh /tmp/hyg3/gate.sh
echo "clean" > /tmp/hyg3/base.md
cd /tmp/hyg3
python3 - <<'EOF'
open('c3.md','w').write('# t\n\n```python\nx = 1\n')
EOF
test -s c3.md || { echo "ERROR: plant did not land — c3.md is empty"; exit 1; }
if bash gate.sh; then
  echo "ERROR: hygiene gate passed with an unterminated fence present"
  exit 1
else
  echo "OK: hygiene gate rejects an unterminated fence"
fi
