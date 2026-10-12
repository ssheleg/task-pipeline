#!/usr/bin/env bash
# name: Negative self-test (the mechanism file dropping one of the four moves)
set -eu
rm -rf /tmp/br2-copy && cp -R . /tmp/br2-copy
python3 - <<'EOF'
import re
p = "/tmp/br2-copy/plugins/task-pipeline/skills/task-pipeline/references/browser.md"
t = open(p, encoding="utf-8").read()
pat = re.compile(r"(playwright-cli (?:-s=\S+ )?)console(?=\s|$)", re.M)
assert pat.search(t), "PLANT DID NOT LAND: the console read moved"
open(p, "w", encoding="utf-8").write(pat.sub(r"\g<1>console-messages", t))
EOF
if python3 /tmp/br2-copy/test/validate.py; then
  echo "ERROR: the look is open + snapshot + console + requests and one went missing unnoticed"
  exit 1
else
  echo "OK: validator correctly FAILs — all four moves stay shown"
fi
