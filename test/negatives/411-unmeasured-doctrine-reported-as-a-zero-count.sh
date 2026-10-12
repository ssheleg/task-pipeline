#!/usr/bin/env bash
# name: Negative self-test (unmeasured doctrine reported as a zero count)
set -eu
rm -rf /tmp/doc1-copy && cp -R . /tmp/doc1-copy
python3 - <<'EOF'
p = "/tmp/doc1-copy/plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"
t = open(p, encoding="utf-8").read()
needle = '        print("doctrine: unmeasured — the ledger carries no `read:` lines")'
assert needle in t, "PLANT DID NOT LAND: doc1 — the unmeasured branch moved"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, '        print("doctrine: 0 of %d reference files read" % len(refs))', 1))
EOF
if python3 /tmp/doc1-copy/test/validate.py; then
  echo "ERROR: a run that measured nothing reported 0 of 34 — B-061: the hook being
         absent and the run reading nothing are opposite facts the ledger cannot
         separate, and a number there is the reassuring answer to a question nobody
         asked"; exit 1
else
  echo "OK: graph.py doctrine is run over all three of its states"
fi
