#!/usr/bin/env bash
# name: Negative self-test (stage 10's verdict drops the publish line)
set -eu
rm -rf /tmp/ri12-copy && cp -R . /tmp/ri12-copy
python3 - <<'EOF'
p = "/tmp/ri12-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
n = 'Either way the verdict carries a `publish:`'
assert n in t, "PLANT DID NOT LAND: ri12"
_planted = t.replace(n, 'Publication is optional and', 1)
assert _planted != t, "PLANT DID NOT LAND: ri12"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ri12-copy/test/validate.py 2>&1 | grep -q 'carries no `publish:` line'; then
  echo "OK: validator FAILs — disclosed at the only moment anyone is reading"
else
  echo "ERROR: the rule went missing and nothing objected — disclosed at the only moment anyone is reading"
  exit 1
fi
