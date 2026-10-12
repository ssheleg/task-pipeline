#!/usr/bin/env bash
# name: Negative self-test (a stage demanding the look with no mechanism to point at)
set -eu
rm -rf /tmp/br1-copy && cp -R . /tmp/br1-copy
python3 - <<'EOF'
p = "/tmp/br1-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
needle = "either one ([`browser.md`](browser.md)) — load the deployed URL"
assert needle in t, "PLANT DID NOT LAND: stage 8's browser pointer moved"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, "either one — load the deployed URL", 1))
EOF
if python3 /tmp/br1-copy/test/validate.py; then
  echo "ERROR: a stage can demand a look at the rendered surface and name no mechanism"
  exit 1
else
  echo "OK: validator correctly FAILs — every stage asking for a browser points at browser.md"
fi
