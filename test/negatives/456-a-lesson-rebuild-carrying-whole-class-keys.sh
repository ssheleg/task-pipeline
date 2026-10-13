#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild carrying whole class keys instead of origins)
set -eu
rm -rf /tmp/rebuild-classkey-copy && cp -R . /tmp/rebuild-classkey-copy
python3 - <<'EOF'
# Carrying is per origin. Decide for the whole class instead: an origin its own checkout shows gone then survives because another origin of the class was not read.
p = "/tmp/rebuild-classkey-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                still = [c for c in prov if not _gone_from(c, ck, o, run)]\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                still = [c for x in e["origins"] for c in (x.get("checkouts") or []) if not _gone_from(c, ck, x, run)]\n', 1))
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
