#!/usr/bin/env bash
# name: Negative self-test (an absolute host path in the worked issue body)
set -eu
rm -rf /tmp/rp3-copy && cp -R . /tmp/rp3-copy
python3 - <<'EOF'
p = "/tmp/rp3-copy/plugins/task-pipeline/skills/task-pipeline/references/retrospective.md"
t = open(p, encoding="utf-8").read()
needle = "title: [retro] a queue is not a diagnosis"
assert needle in t, "PLANT DID NOT LAND: the worked issue moved"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, needle + "\nwhere: /Users/someone/work/api", 1))
EOF
if python3 /tmp/rp3-copy/test/validate.py; then
  echo "ERROR: the doctrine's own example breaks rule 1 of the list beside it"
  exit 1
else
  echo "OK: validator correctly FAILs — the example obeys the rules it teaches"
fi
