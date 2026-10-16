#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild removing an origin on its own)
set -eu
rm -rf /tmp/rebuild-implicit-copy && cp -R . /tmp/rebuild-implicit-copy
python3 - <<'EOF'
# Round 11: no implicit removal. Put back the removal of an origin its checkout read and no longer holds (the memory-less ones, as rounds 9–10 did).
p = "/tmp/rebuild-implicit-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                rec = dict(o, carried=_carry_reason(ck, o, run))\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                rec = dict(o, carried=_carry_reason(ck, o, run))  # planted\n                if rec["carried"] == CARRY_GONE and not o.get("memory"):\n                    continue\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-implicit-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-implicit-copy
  echo "ERROR: lessons_test passed a rebuild that removes origins on its own"
  exit 1
else
  rm -rf /tmp/rebuild-implicit-copy
  echo "OK: lessons_test correctly FAILs — only --prune-carried removes an origin"
fi
