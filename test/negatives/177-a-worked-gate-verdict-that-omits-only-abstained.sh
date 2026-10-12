#!/usr/bin/env bash
# name: Negative self-test (a worked GATE verdict that omits only `abstained`)
set -eu
rm -rf /tmp/disc3-copy && cp -R . /tmp/disc3-copy
python3 - <<'EOF'
p = "/tmp/disc3-copy/plugins/task-pipeline/skills/task-pipeline/references/audit.md"
t = open(p, encoding="utf-8").read()
needle = "  abstained: 1 (1 cannot-verify) · unlooked: 2 dormant"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
t = t.replace(needle, "  unlooked: 2 dormant", 1)
open(p, "w", encoding="utf-8").write(t)
s = open(p, encoding="utf-8").read()
assert "abstained: 1" not in s and "unlooked: 2 dormant" in s, "PLANT DID NOT LAND"
EOF
if python3 /tmp/disc3-copy/test/validate.py; then
  echo "ERROR: validator passed a verdict that hides what the run declined to claim"
  exit 1
else
  echo "OK: validator correctly FAILs — each disclosure is required on its own"
fi
