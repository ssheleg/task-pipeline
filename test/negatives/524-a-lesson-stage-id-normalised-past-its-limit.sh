#!/usr/bin/env bash
# name: Negative self-test (a lesson stage id normalised past its limit)
set -eu
rm -rf /tmp/r14-fold-copy && cp -R . /tmp/r14-fold-copy
python3 - <<'EOF'
# Round 14, L5: a normalised stage id is cut to 32 characters. Do not cut it.
p = "/tmp/r14-fold-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    folded = " ".join(" ".join(v.splitlines()).split())[:32].strip()\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    folded = " ".join(" ".join(v.splitlines()).split()).strip()\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r14-fold-copy/test/lessons_test.py; then
  rm -rf /tmp/r14-fold-copy
  echo "ERROR: lessons_test passed a normalised stage id still over the limit"
  exit 1
else
  rm -rf /tmp/r14-fold-copy
  echo "OK: lessons_test correctly FAILs — a normalised id is cut to 32"
fi
