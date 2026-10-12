#!/usr/bin/env bash
# name: Negative self-test (the review cap with no config key)
set -eu
rm -rf /tmp/rc3-copy && cp -R . /tmp/rc3-copy
python3 - <<'EOF'
p = "/tmp/rc3-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
assert "`run.review.maxRounds`" in t, "PLANT DID NOT LAND: the config key moved"
open(p, "w", encoding="utf-8").write(t.replace("`run.review.maxRounds`", "the config", 1))
EOF
if python3 /tmp/rc3-copy/test/validate.py; then
  echo "ERROR: a default nobody can change is a default everybody overrides in their head"
  exit 1
else
  echo "OK: validator correctly FAILs — the cap names the key that changes it"
fi
