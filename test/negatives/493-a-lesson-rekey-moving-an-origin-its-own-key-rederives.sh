#!/usr/bin/env bash
# name: Negative self-test (a lesson re-key moving an origin its own key re-derives)
set -eu
rm -rf /tmp/r13-rekey-own-copy && cp -R . /tmp/r13-rekey-own-copy
python3 - <<'EOF'
# Round 13, K: an origin whose own key is re-derived this run is never re-keyed. Re-key it anyway.
p = "/tmp/r13-rekey-own-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            if _origin_key(o) in derived:\n                continue'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            if False:\n                continue', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r13-rekey-own-copy/test/lessons_test.py; then
  rm -rf /tmp/r13-rekey-own-copy
  echo "ERROR: lessons_test passed a re-key taking a live project's memory id"
  exit 1
else
  rm -rf /tmp/r13-rekey-own-copy
  echo "OK: lessons_test correctly FAILs — an origin whose own key is re-derived stays"
fi
