#!/usr/bin/env bash
# name: Negative self-test (lesson rebuild problems attributed by path prefix)
set -eu
rm -rf /tmp/rebuild-prefix-copy && cp -R . /tmp/rebuild-prefix-copy
python3 - <<'EOF'
# Round 9: a problem has a structural owner. Attribute it by path prefix again: an unreadable sibling `x-old` then makes checkout `x` incomplete, and x's own deleted entry is carried.
p = "/tmp/rebuild-prefix-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    run["complete"] = {checkout_id(r) for r, whole in repos.items() if whole and r not in owners}\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    run["complete"] = {checkout_id(r) for r, whole in repos.items() if whole and r not in owners\n                       and not any(str(pathlib.Path(t.split(": ")[0]).resolve()).startswith(str(r))\n                                   for _, t in problems)}\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-prefix-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-prefix-copy
  echo "ERROR: lessons_test passed problems attributed by path prefix"
  exit 1
else
  rm -rf /tmp/rebuild-prefix-copy
  echo "OK: lessons_test correctly FAILs — problems carry a structural owner"
fi
