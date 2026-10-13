#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild that drops origins it could not re-derive)
set -eu
rm -rf /tmp/rebuild-loss-copy && cp -R . /tmp/rebuild-loss-copy
python3 - <<'EOF'
# Round 7: rebuild never loses what it cannot re-derive. Remove the carry-forward.
p = "/tmp/rebuild-loss-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                (pruned if a.prune_carried else carried).append((ck, rec))\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                removed.append((ck, o))\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-loss-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-loss-copy
  echo "ERROR: lessons_test passed a rebuild that drops origins it could not re-derive"
  exit 1
else
  rm -rf /tmp/rebuild-loss-copy
  echo "OK: lessons_test correctly FAILs — an unread or unresolved origin is carried"
fi
