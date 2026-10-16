#!/usr/bin/env bash
# name: Negative self-test (a lesson add re-key merging two memory ids)
set -eu
rm -rf /tmp/r13-rekey-two-add-copy && cp -R . /tmp/r13-rekey-two-add-copy
python3 - <<'EOF'
# Round 13, K: add never merges two different memory ids into one origin. Merge them.
p = "/tmp/r13-rekey-two-add-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                if n is None or (o.get("memory") and n.get("memory")\n                                 and mem_base(o["memory"]) != mem_base(n["memory"])):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                if n is None:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r13-rekey-two-add-copy/test/lessons_test.py; then
  rm -rf /tmp/r13-rekey-two-add-copy
  echo "ERROR: lessons_test passed add merging two store records into one origin"
  exit 1
else
  rm -rf /tmp/r13-rekey-two-add-copy
  echo "OK: lessons_test correctly FAILs — add keeps two memory ids two"
fi
