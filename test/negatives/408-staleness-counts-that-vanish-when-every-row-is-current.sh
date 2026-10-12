#!/usr/bin/env bash
# name: Negative self-test (staleness counts that vanish when every row is current)
set -eu
rm -rf /tmp/stl1-copy && cp -R . /tmp/stl1-copy
python3 - <<'EOF'
p = "/tmp/stl1-copy/plugins/task-pipeline/skills/task-pipeline/templates/exposure.sh"
t = open(p, encoding="utf-8").read()
needle = '  echo "staleness — current $STALE_CURRENT'
assert needle in t, "PLANT DID NOT LAND: stl1 — the staleness line moved"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, '  [ "$STALE_BEHIND" -gt 0 ] && echo "staleness — current $STALE_CURRENT', 1))
EOF
if python3 /tmp/stl1-copy/test/validate.py; then
  echo "ERROR: staleness counts that print nothing when everything is current were
         accepted — B-081: state zero out loud, or freshness is indistinguishable
         from a check that never looked"; exit 1
else
  echo "OK: exposure.sh's staleness section is executed over four states"
fi
