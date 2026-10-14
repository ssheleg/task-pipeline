#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild removing an origin by a project-level read set)
set -eu
rm -rf /tmp/rebuild-readset-copy && cp -R . /tmp/rebuild-readset-copy
python3 - <<'EOF'
# Round 9: implicit removal needs positive evidence from the SAME checkout. Let any checkout of the project that read the same retro path decide instead.
p = "/tmp/rebuild-readset-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    if c not in run["project"]:\n        main = (o.get("worktreeOf") or {}).get(c)\n        return bool(main) and main in run["complete"] and main in run["trees"] and c not in run["trees"][main]\n    rel = o["retro"].split("#", 1)[0]\n    if (c not in run["complete"] or run["project"][c] != o["project"]\n            or rel not in run["files"].get(c, ())):\n        return False\n    return (ck, o["retro"]) not in run["held"].get(c, ()) and o["retro"] not in run["refused"].get(c, ())\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    rel = o["retro"].split("#", 1)[0]\n    if not any(run["project"].get(x) == o["project"] and x in run["complete"]\n               and rel in run["files"].get(x, ()) for x in run["project"]):\n        return False\n    return not any((ck, o["retro"]) in run["held"].get(x, ()) for x in run["project"])\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-readset-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-readset-copy
  echo "ERROR: lessons_test passed a rebuild that removes by a project-level read set"
  exit 1
else
  rm -rf /tmp/rebuild-readset-copy
  echo "OK: lessons_test correctly FAILs — only the origin's own checkouts decide"
fi
