#!/usr/bin/env bash
# name: Negative self-test (the exposure doctrine dropping its never-checked rule)
set -eu
rm -rf /tmp/nc-copy && cp -R . /tmp/nc-copy
python3 - <<'EOF'
p = "/tmp/nc-copy/plugins/task-pipeline/skills/task-pipeline/references/exposure.md"
t = open(p, encoding="utf-8").read()
assert "never checked" in t, "PLANT DID NOT LAND: the rule is not in the doctrine"
open(p, "w", encoding="utf-8").write(t.replace("never checked", "zero days"))
EOF
if python3 /tmp/nc-copy/test/validate.py; then
  echo "ERROR: the doctrine lost the rule that zero days would read as 'checked today'"
  exit 1
else
  echo "OK: validator correctly FAILs — the decision lives where the next reader looks"
fi
