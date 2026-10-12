#!/usr/bin/env bash
# name: Negative self-test (retro order — an adjacent enumeration puts prune before stamp)
set -eu
rm -rf /tmp/ord1-copy && cp -R . /tmp/ord1-copy
python3 - <<'EOF'
p = "/tmp/ord1-copy/plugins/task-pipeline/skills/task-pipeline/references/companion-skills.md"
t = open(p, encoding="utf-8").read()
needle = "last act: stamp, prune, entry"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
t = t.replace(needle, "last act: prune, stamp, entry", 1)
open(p, "w", encoding="utf-8").write(t)
assert "last act: prune, stamp, entry" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/ord1-copy/test/validate.py; then
  echo "ERROR: validator passed a surface enumerating prune before stamp"
  exit 1
else
  echo "OK: validator correctly FAILs — rule 21's order contradicted by a consumer"
fi
