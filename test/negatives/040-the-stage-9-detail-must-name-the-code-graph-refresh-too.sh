#!/usr/bin/env bash
# name: Negative self-test (the stage-9 detail must name the code-graph refresh too)
set -eu
rm -rf /tmp/graph-doc-copy && cp -R . /tmp/graph-doc-copy
python3 - <<'EOF'
import re
p = "/tmp/graph-doc-copy/plugins/task-pipeline/skills/task-pipeline/references/stage-09-docs-wiki.md"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
m = re.search(r"^## 9 — .*?(?=^## |\Z)", t, re.M | re.S)
open(p, "w", encoding="utf-8").write(
    t[:m.start()] + re.sub(r"graph", "doc", m.group(0), flags=re.I) + t[m.end():])
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: the-stage-9-detail-must-name-the-cod"
EOF
if python3 /tmp/graph-doc-copy/test/validate.py; then
  echo "ERROR: validator passed a stage-9 section that never mentions the graph — an agent reading the stage detail is never told to refresh it"
  exit 1
else
  echo "OK: validator requires stages.md stage 9 to name the code-graph refresh"
fi
