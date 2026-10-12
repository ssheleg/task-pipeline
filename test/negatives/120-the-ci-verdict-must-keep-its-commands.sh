#!/usr/bin/env bash
# name: Negative self-test (the CI verdict must keep its commands)
set -eu
rm -rf /tmp/ci01-copy && cp -R . /tmp/ci01-copy
python3 - <<'EOF'
p = "/tmp/ci01-copy/plugins/task-pipeline/skills/task-pipeline/references/conventions.md"
t = open(p, encoding="utf-8").read()
assert "gh run list --branch" in t, "PLANT DID NOT LAND: needle absent before edit"
open(p, "w", encoding="utf-8").write(t.replace("gh run list --branch", "gh run glance --branch"))
EOF
if python3 /tmp/ci01-copy/test/validate.py; then
  echo "ERROR: validator passed with the CI-verdict commands gone"
  exit 1
else
  echo "OK: validator correctly FAILs — the CI verdict must keep its commands"
fi
