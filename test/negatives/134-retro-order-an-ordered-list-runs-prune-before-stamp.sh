#!/usr/bin/env bash
# name: Negative self-test (retro order — an ordered list runs prune before stamp)
set -eu
rm -rf /tmp/ord2-copy && cp -R . /tmp/ord2-copy
python3 - <<'EOF'
p = "/tmp/ord2-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
t = open(p, encoding="utf-8").read()
a, b = "1. **Stamp the run first**", "2. **Then prune.**"
assert a in t and b in t, "PLANT DID NOT LAND: list anchors absent before edit"
t = t.replace(a, "1. **Prune the list first**", 1).replace(b, "2. **Then stamp the run.**", 1)
open(p, "w", encoding="utf-8").write(t)
s = open(p, encoding="utf-8").read()
assert "1. **Prune the list first**" in s and "2. **Then stamp the run.**" in s, "PLANT DID NOT LAND"
EOF
if python3 /tmp/ord2-copy/test/validate.py; then
  echo "ERROR: validator passed an ordered list running prune before stamp"
  exit 1
else
  echo "OK: validator correctly FAILs — the ordered-list shape is covered"
fi
