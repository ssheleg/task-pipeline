#!/usr/bin/env bash
# name: Negative self-test (the False success section must exist)
set -eu
rm -rf /tmp/fs01-copy && cp -R . /tmp/fs01-copy
python3 - <<'EOF'
p = "/tmp/fs01-copy/plugins/task-pipeline/skills/task-pipeline/references/gates.md"
t = open(p, encoding="utf-8").read()
assert '## False success — when a mechanism reports a win it never checked' in t, "PLANT DID NOT LAND: needle absent before edit"
t = t.replace('## False success — when a mechanism reports a win it never checked', '## Something else entirely')
t = t.replace('- False success — when a mechanism reports a win it never checked', '- Something else entirely')
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/fs01-copy/test/validate.py; then
  echo "ERROR: validator passed with the False success section must exist broken"
  exit 1
else
  echo "OK: validator correctly FAILs — the False success section must exist"
fi
