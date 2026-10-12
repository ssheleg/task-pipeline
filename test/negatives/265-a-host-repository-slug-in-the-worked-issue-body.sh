#!/usr/bin/env bash
# name: Negative self-test (a host repository slug in the worked issue body)
set -eu
rm -rf /tmp/rp5-copy && cp -R . /tmp/rp5-copy
python3 - <<'EOF'
p = "/tmp/rp5-copy/plugins/task-pipeline/skills/task-pipeline/references/retrospective.md"
t = open(p, encoding="utf-8").read()
needle = "repo:  ssheleg/task-pipeline"
assert needle in t, "PLANT DID NOT LAND: the repo line moved"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, needle + "\nseen in: acme-corp/billing-api", 1))
EOF
if python3 /tmp/rp5-copy/test/validate.py; then
  echo "ERROR: the example names a repository that is not the skill's own"
  exit 1
else
  echo "OK: validator correctly FAILs — only the skill's own repo appears"
fi
