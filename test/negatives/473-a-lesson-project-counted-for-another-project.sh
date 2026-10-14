#!/usr/bin/env bash
# name: Negative self-test (a lesson counting an origin whose checkout holds another project)
set -eu
rm -rf /tmp/rebuild-countforeign-copy && cp -R . /tmp/rebuild-countforeign-copy
python3 - <<'EOF'
# Round 11: an origin carried as `checkout holds another project` is kept but not counted. Count it: a re-init or a stranger at the path makes a phantom second project.
p = "/tmp/rebuild-countforeign-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    counted = [o for o in origins if o.get("carried") != CARRY_FOREIGN]\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    counted = origins\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-countforeign-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-countforeign-copy
  echo "ERROR: lessons_test passed a phantom second project counted"
  exit 1
else
  rm -rf /tmp/rebuild-countforeign-copy
  echo "OK: lessons_test correctly FAILs — a foreign-carried origin is not counted"
fi
