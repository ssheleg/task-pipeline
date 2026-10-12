#!/usr/bin/env bash
# name: Negative self-test (the hygiene gate catches an empty section)
set -eu
rm -rf /tmp/hyg6 && mkdir -p /tmp/hyg6
cp plugins/task-pipeline/skills/task-pipeline/templates/hygiene.sh /tmp/hyg6/gate.sh
echo "clean" > /tmp/hyg6/base.md
cd /tmp/hyg6
python3 - <<'EOF'
open('c6.md','w').write('# t\n\n## One\n\n## Two\n\nbody\n')
EOF
test -s c6.md || { echo "ERROR: plant did not land — c6.md is empty"; exit 1; }
if bash gate.sh; then
  echo "ERROR: hygiene gate passed with an empty section present"
  exit 1
else
  echo "OK: hygiene gate rejects an empty section"
fi
