#!/usr/bin/env bash
# name: Negative self-test (the acceptance policy losing its version)
set -eu
rm -rf /tmp/ap1-copy && cp -R . /tmp/ap1-copy
python3 - <<'EOF'
# B-091: a table accepted under v1.20 doctrine was indistinguishable from one
# accepted under v1.70, forever, in a pack where every SHA in the retro resolves.
p = "/tmp/ap1-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
t = open(p, encoding="utf-8").read()
assert "**Acceptance policy `AP-1`" in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace("AP-1", "the ladder"))
assert "AP-1" not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/ap1-copy/test/validate.py; then
  echo "ERROR: validator passed an acceptance policy with no version to cite"
  exit 1
else
  echo "OK: validator correctly FAILs — the acceptance standard is citable by version"
fi
