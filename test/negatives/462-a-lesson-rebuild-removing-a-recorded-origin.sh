#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild removing an origin that holds a memory id)
set -eu
rm -rf /tmp/rebuild-dropmem-copy && cp -R . /tmp/rebuild-dropmem-copy
python3 - <<'EOF'
# An origin every checkout shows gone that still holds a memory id the run did not re-attach is carried — the store still has the record. Remove it instead.
p = "/tmp/rebuild-dropmem-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            if o.get("memory") and mem_base(o["memory"]) not in attached:\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            if False:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-dropmem-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-dropmem-copy
  echo "ERROR: lessons_test passed a rebuild that removes recorded origins"
  exit 1
else
  rm -rf /tmp/rebuild-dropmem-copy
  echo "OK: lessons_test correctly FAILs — a recorded origin is carried until --prune-carried"
fi
