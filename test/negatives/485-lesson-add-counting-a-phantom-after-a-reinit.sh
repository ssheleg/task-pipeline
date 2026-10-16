#!/usr/bin/env bash
# name: Negative self-test (lesson add counting a phantom project after a re-init)
set -eu
rm -rf /tmp/add-foreign-copy && cp -R . /tmp/add-foreign-copy
python3 - <<'EOF'
# Round 12, G: add marks this checkout's old-key origin, whose commit no longer resolves, as `checkout holds another project`. Stop: add counts a phantom until the next rebuild.
p = "/tmp/add-foreign-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                      if o["project"] != project and here in (o.get("checkouts") or [])\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                      if False and here in (o.get("checkouts") or [])\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/add-foreign-copy/test/lessons_test.py; then
  rm -rf /tmp/add-foreign-copy
  echo "ERROR: lessons_test passed add counting a phantom project"
  exit 1
else
  rm -rf /tmp/add-foreign-copy
  echo "OK: lessons_test correctly FAILs — add applies the stranger rule"
fi
