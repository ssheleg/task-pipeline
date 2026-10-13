#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild carrying whole class keys instead of origins)
set -eu
rm -rf /tmp/rebuild-classkey-copy && cp -R . /tmp/rebuild-classkey-copy
python3 - <<'EOF'
# Carrying is per origin (project, retro). Carry the whole class instead: an origin whose
# readable retro no longer holds it then survives because another project's root was unread.
p = "/tmp/rebuild-classkey-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = "                reason = _carry_reason(o, seen)\n"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(
    needle, '                reason = next(filter(None, (_carry_reason(x, seen) for x in e["origins"])), None)\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-classkey-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-classkey-copy
  echo "ERROR: lessons_test passed a rebuild that carries whole class keys"
  exit 1
else
  rm -rf /tmp/rebuild-classkey-copy
  echo "OK: lessons_test correctly FAILs — carry-forward is per origin, not per class key"
fi
