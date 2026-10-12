#!/usr/bin/env bash
# name: Negative self-test (a redaction rule added without the count moving)
set -eu
rm -rf /tmp/rp1-copy && cp -R . /tmp/rp1-copy
python3 - <<'EOF'
p = "/tmp/rp1-copy/plugins/task-pipeline/skills/task-pipeline/references/retrospective.md"
t = open(p, encoding="utf-8").read()
needle = "5. **The title states the class"
assert needle in t, "PLANT DID NOT LAND: the rule list moved"
open(p, "w", encoding="utf-8").write(t.replace(
    needle,
    "5. **No timestamps.** A wall-clock time narrows a repository to a person's day.\n"
    "6. **The title states the class", 1))
EOF
if python3 /tmp/rp1-copy/test/validate.py; then
  echo "ERROR: an enumeration counted in prose drifted from its own items"
  exit 1
else
  echo "OK: validator correctly FAILs — the rule count is computed from the rules"
fi
