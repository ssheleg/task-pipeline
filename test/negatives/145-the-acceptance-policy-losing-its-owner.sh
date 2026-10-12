#!/usr/bin/env bash
# name: Negative self-test (the acceptance policy losing its owner)
set -eu
rm -rf /tmp/ap2-copy && cp -R . /tmp/ap2-copy
python3 - <<'EOF'
p = "/tmp/ap2-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
t = open(p, encoding="utf-8").read()
needle = "owner: the operator of the project running this pipeline"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, "the operator decides", 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/ap2-copy/test/validate.py; then
  echo "ERROR: validator passed an acceptance policy nobody owns"
  exit 1
else
  echo "OK: validator correctly FAILs — a decision with no owner is one each run makes for itself"
fi
