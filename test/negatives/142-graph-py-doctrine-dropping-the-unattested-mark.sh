#!/usr/bin/env bash
# name: Negative self-test (`graph.py doctrine` dropping the `unattested` mark)
set -eu
rm -rf /tmp/prov2-copy && cp -R . /tmp/prov2-copy
python3 - <<'EOF'
# Dropping the false claim without stating the gap leaves a reader believing the
# provenance is established, which is the same defect one register quieter.
p = "/tmp/prov2-copy/plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"
t = open(p, encoding="utf-8").read()
needle = 'reference files read — unattested"'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, 'reference files read"', 1))
out = open(p, encoding="utf-8").read()
assert 'reference files read — unattested"' not in out, "PLANT DID NOT LAND"
EOF
if python3 /tmp/prov2-copy/test/validate.py; then
  echo "ERROR: validator passed a doctrine verb printing a count with no unattested mark"
  exit 1
else
  echo "OK: validator correctly FAILs — the count says what the ledger says, not who wrote it"
fi
