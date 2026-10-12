#!/usr/bin/env bash
# name: Negative self-test (the shipped ledger template losing its `Environment` column)
set -eu
rm -rf /tmp/env3-copy && cp -R . /tmp/env3-copy
python3 - <<'EOF'
p = "/tmp/env3-copy/plugins/task-pipeline/skills/task-pipeline/templates/verification.md"
t = open(p, encoding="utf-8").read()
needle = "| REQ | What | Run | Shipped in | Observed at | Environment | Auto | Human | Note |"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, needle.replace(" Environment |", ""), 1))
assert "| Observed at | Auto |" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/env3-copy/test/validate.py; then
  echo "ERROR: validator passed a shipped template whose ledger cannot record an environment"
  exit 1
else
  echo "OK: validator correctly FAILs — every project seeding this ledger gets the column"
fi
