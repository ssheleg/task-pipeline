#!/usr/bin/env bash
# name: Negative self-test (a long seeded template needs its own Contents)
set -eu
rm -rf /tmp/tpltoc-copy && cp -R . /tmp/tpltoc-copy
python3 - <<'EOF'
p = "/tmp/tpltoc-copy/plugins/task-pipeline/skills/task-pipeline/templates/docmap.md"
t = open(p, encoding="utf-8").read()
assert "## Contents" in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(t.replace("## Contents", "## Overview", 1))
EOF
if python3 /tmp/tpltoc-copy/test/validate.py; then
  echo "ERROR: validator passed a 100+ line seeded template with no Contents — a host project reads that file and a partial read shows whichever sections come first"
  exit 1
else
  echo "OK: seeded templates over 100 lines carry a Contents list"
fi
