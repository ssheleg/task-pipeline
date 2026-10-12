#!/usr/bin/env bash
# name: Negative self-test (the another-agent section is deleted outright)
set -eu
rm -rf /tmp/ag4-copy && cp -R . /tmp/ag4-copy
python3 - <<'EOF'
import re
p = "/tmp/ag4-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^## 1a\. Another agent may be in this repository right now.*?(?=^## )", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: ag4"
_planted = t[:m.start()] + t[m.end():]
assert _planted != t, "PLANT DID NOT LAND: ag4"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ag4-copy/test/validate.py 2>&1 | grep -q "nothing tells a run that another agent"; then
  echo "OK: validator FAILs — ag1-ag3 mutate inside the section and never reach this branch"
else
  echo "ERROR: the whole rule was removed and only its phrases were guarded"
  exit 1
fi
