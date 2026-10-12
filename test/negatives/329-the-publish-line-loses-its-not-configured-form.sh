#!/usr/bin/env bash
# name: Negative self-test (the publish line loses its not-configured form)
set -eu
rm -rf /tmp/ri11-copy && cp -R . /tmp/ri11-copy
python3 - <<'EOF'
p = "/tmp/ri11-copy/plugins/task-pipeline/skills/task-pipeline/references/retrospective.md"
t = open(p, encoding="utf-8").read()
n = 'not configured (N insight-grade entries stayed local)'
assert n in t, "PLANT DID NOT LAND: ri11"
_planted = t.replace(n, 'nothing to report', 1)
assert _planted != t, "PLANT DID NOT LAND: ri11"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ri11-copy/test/validate.py 2>&1 | grep -q 'the `not configured` form'; then
  echo "OK: validator FAILs — a blank where configuration is absent is the silence this ends"
else
  echo "ERROR: the rule went missing and nothing objected — a blank where configuration is absent is the silence this ends"
  exit 1
fi
