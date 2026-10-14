#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild doubling a project when its key changes)
set -eu
rm -rf /tmp/rebuild-rekey-copy && cp -R . /tmp/rebuild-rekey-copy
python3 - <<'EOF'
# Round 10, J1/J2: a checkout whose root commit changed (--unshallow, re-init) still holding the entry supersedes its old-key origin. Never supersede: a phantom second project.
p = "/tmp/rebuild-rekey-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                newkey = {c: _moved_in(c, ck, o, run) for c in prov}\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                newkey = {c: None for c in prov}\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-rekey-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-rekey-copy
  echo "ERROR: lessons_test passed a phantom second project after a key change"
  exit 1
else
  rm -rf /tmp/rebuild-rekey-copy
  echo "OK: lessons_test correctly FAILs — a key change supersedes, never doubles"
fi
