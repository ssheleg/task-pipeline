#!/usr/bin/env bash
# name: Negative self-test (the index must not drift from the canons)
set -eu
rm -rf /tmp/ed2-copy && cp -R . /tmp/ed2-copy
python3 - <<'EOF'
p = "/tmp/ed2-copy/plugins/task-pipeline/skills/evidence-docs/SKILL.md"
t = open(p, encoding="utf-8").read()
assert '**Silence is not a pass**' in t, "PLANT DID NOT LAND: needle absent before edit"
open(p, "w", encoding="utf-8").write(t.replace('**Silence is not a pass**', '**Vibes are fine**'))
EOF
if python3 /tmp/ed2-copy/test/validate.py; then
  echo "ERROR: validator passed with the index must not drift from the canons broken"
  exit 1
else
  echo "OK: validator correctly FAILs — the index must not drift from the canons"
fi
