#!/usr/bin/env bash
# name: Negative self-test (the Retired log itself removed from learned.md)
set -eu
rm -rf /tmp/lrn2-copy && cp -R . /tmp/lrn2-copy
python3 - <<'EOF'
import re
p = "/tmp/lrn2-copy/plugins/task-pipeline/skills/task-pipeline/references/learned.md"
t = open(p, encoding="utf-8").read()
assert re.search(r"^### Retired\s*$", t, re.M), "PLANT DID NOT LAND: heading absent before edit"
open(p, "w", encoding="utf-8").write(re.sub(r"^### Retired\s*$", "### Departures", t, count=1, flags=re.M))
assert "### Retired" not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/lrn2-copy/test/validate.py; then
  echo "ERROR: validator passed with no departure log — an absent log reads exactly like an empty one"
  exit 1
else
  echo "OK: validator correctly FAILs — the log exists, so 'nothing retired' is a statement"
fi
