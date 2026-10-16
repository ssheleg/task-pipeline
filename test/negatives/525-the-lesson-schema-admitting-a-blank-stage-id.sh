#!/usr/bin/env bash
# name: Negative self-test (the lesson schema admitting a blank stage id)
set -eu
rm -rf /tmp/r14-schema-copy && cp -R . /tmp/r14-schema-copy
python3 - <<'EOF'
# Round 14, L6: the schema's string stage ids are not blank. Drop the pattern.
p = "/tmp/r14-schema-copy/plugins/task-pipeline/skills/task-pipeline/templates/lesson.schema.json"
t = open(p, encoding="utf-8").read()
needle = ',\n          "pattern": "\\\\S"\n        },\n        "surfaced"'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '\n        },\n        "surfaced"', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r14-schema-copy/test/lessons_test.py; then
  rm -rf /tmp/r14-schema-copy
  echo "ERROR: lessons_test passed a schema admitting a blank stage id"
  exit 1
else
  rm -rf /tmp/r14-schema-copy
  echo "OK: lessons_test correctly FAILs — the schema refuses a blank stage id"
fi
