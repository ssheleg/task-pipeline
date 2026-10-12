#!/usr/bin/env bash
# name: Negative self-test (a worked GATE verdict that omits only `unlooked`)
set -eu
rm -rf /tmp/disc2-copy && cp -R . /tmp/disc2-copy
python3 - <<'EOF'
p = "/tmp/disc2-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
t = open(p, encoding="utf-8").read()
needle = "  abstained: 2 (1 partial · 1 cannot-verify) · unlooked: 3 dormant"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
t = t.replace(needle, "  abstained: 2 (1 partial · 1 cannot-verify)", 1)
open(p, "w", encoding="utf-8").write(t)
s = open(p, encoding="utf-8").read()
assert "unlooked: 3 dormant" not in s and "abstained: 2" in s, "PLANT DID NOT LAND"
EOF
if python3 /tmp/disc2-copy/test/validate.py; then
  echo "ERROR: validator passed a verdict that discloses what was declined but not what was never looked at"
  exit 1
else
  echo "OK: validator correctly FAILs — each disclosure is required on its own"
fi
