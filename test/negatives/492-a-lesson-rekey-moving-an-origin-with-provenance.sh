#!/usr/bin/env bash
# name: Negative self-test (a lesson re-key moving an origin with provenance)
set -eu
rm -rf /tmp/r13-rekey-prov-copy && cp -R . /tmp/r13-rekey-prov-copy
python3 - <<'EOF'
# Round 13, K: only an origin with no provenance is re-keyed. Re-key any origin.
p = "/tmp/r13-rekey-prov-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    if o.get("checkouts"):\n        return None\n\n    def same_repository'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '\n    def same_repository', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r13-rekey-prov-copy/test/lessons_test.py; then
  rm -rf /tmp/r13-rekey-prov-copy
  echo "ERROR: lessons_test passed a re-key moving an origin that has provenance"
  exit 1
else
  rm -rf /tmp/r13-rekey-prov-copy
  echo "OK: lessons_test correctly FAILs — an origin with provenance is never moved"
fi
