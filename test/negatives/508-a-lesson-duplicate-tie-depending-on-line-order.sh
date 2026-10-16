#!/usr/bin/env bash
# name: Negative self-test (a lesson duplicate tie depending on line order)
set -eu
rm -rf /tmp/r13-tie-break-copy && cp -R . /tmp/r13-tie-break-copy
python3 - <<'EOF'
# Round 13, Q: a same-revision tie keeps the lexically smaller id. Let the line order decide.
p = "/tmp/r13-tie-break-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                -mem_rev(x.get("memory") or ""), x.get("memory") or "", json.dumps(x, sort_keys=True)))\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                -mem_rev(x.get("memory") or ""),))\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r13-tie-break-copy/test/lessons_test.py; then
  rm -rf /tmp/r13-tie-break-copy
  echo "ERROR: lessons_test passed a kept id that depends on the order of lines"
  exit 1
else
  rm -rf /tmp/r13-tie-break-copy
  echo "OK: lessons_test correctly FAILs — a same-revision tie is deterministic"
fi
