#!/usr/bin/env bash
# name: Negative self-test (claim registry — a stale canon count in word form)
set -eu
rm -rf /tmp/cr4-copy && cp -R . /tmp/cr4-copy
python3 - <<'EOF'
p = "/tmp/cr4-copy/plugins/task-pipeline/skills/evidence-docs/SKILL.md"
t = open(p, encoding="utf-8").read()
needle = "## The ten canons"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, "## The nine canons", 1))
assert "## The nine canons" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/cr4-copy/test/validate.py; then
  echo "ERROR: validator passed a canon count stated as a WORD that disagrees with the doctrine"
  exit 1
else
  echo "OK: validator correctly FAILs — word-form numbers are read, not skipped"
fi
