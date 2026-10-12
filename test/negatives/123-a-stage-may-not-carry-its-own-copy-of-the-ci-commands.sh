#!/usr/bin/env bash
# name: Negative self-test (a stage may not carry its own copy of the CI commands)
set -eu
rm -rf /tmp/ci04-copy && cp -R . /tmp/ci04-copy
python3 - <<'EOF'
p = "/tmp/ci04-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
anchor = "- **Read the CI verdict for the deploy's own commit**"
assert anchor in t, "PLANT DID NOT LAND: anchor absent before edit"
assert "gh run list --branch" not in t, "PLANT DID NOT LAND: a copy already exists"
open(p, "w", encoding="utf-8").write(
    t.replace(anchor, "- run `gh run list --branch main --limit 1`\n" + anchor, 1))
EOF
if python3 /tmp/ci04-copy/test/validate.py; then
  echo "ERROR: validator passed with a second copy of the CI-verdict commands"
  exit 1
else
  echo "OK: validator correctly FAILs — a stage may not carry its own copy of the CI commands"
fi
