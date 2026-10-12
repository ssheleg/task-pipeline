#!/usr/bin/env bash
# name: Negative self-test (a gate-verdict example that omits what the rule mandates)
set -eu
rm -rf /tmp/wex1-copy && cp -R . /tmp/wex1-copy
python3 - <<'EOF'
p = "/tmp/wex1-copy/plugins/task-pipeline/skills/task-pipeline/templates/carryover.md"
t = open(p, encoding="utf-8").read()
needle = " · holds: 1 (container: pg-test, this run)"
assert needle in t, "PLANT DID NOT LAND: wex1 — the example's holds line moved"
open(p, "w", encoding="utf-8").write(t.replace(needle, "", 1))
EOF
if python3 /tmp/wex1-copy/test/validate.py; then
  echo "ERROR: a gate-verdict example omitting the mandated holds line was accepted —
         B-064: an agent copies the example literally and paraphrases the prose, so
         an example that omits what the rule mandates teaches the omission"; exit 1
else
  echo "OK: worked examples are read as blocks and checked against their own rule"
fi
