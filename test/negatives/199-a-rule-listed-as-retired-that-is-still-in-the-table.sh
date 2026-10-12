#!/usr/bin/env bash
# name: Negative self-test (a rule listed as retired that is still in the table)
set -eu
rm -rf /tmp/hw8-copy && cp -R . /tmp/hw8-copy
python3 - <<'EOF'
p = "/tmp/hw8-copy/plugins/task-pipeline/skills/task-pipeline/references/learned.md"
t = open(p, encoding="utf-8").read()
needle = "*None retired yet.*"
assert needle in t, "PLANT DID NOT LAND: log anchor absent before edit"
t = t.replace(needle, "- **12 · Tests create what they assert on** — trigger: subsumed; `deadbeef`\n\n" + needle, 1)
open(p, "w", encoding="utf-8").write(t)
assert "**12 · Tests create" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/hw8-copy/test/validate.py; then
  echo "ERROR: a rule was logged as retired while its row still stands — the reverse direction nobody checked"
  exit 1
else
  echo "OK: validator correctly FAILs — a gap has one side and so does a resurrection"
fi
