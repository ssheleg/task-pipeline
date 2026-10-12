#!/usr/bin/env bash
# name: Negative self-test (a commit id in the worked issue body)
set -eu
rm -rf /tmp/rp4-copy && cp -R . /tmp/rp4-copy
python3 - <<'EOF'
p = "/tmp/rp4-copy/plugins/task-pipeline/skills/task-pipeline/references/retrospective.md"
t = open(p, encoding="utf-8").read()
needle = "title: [retro] a queue is not a diagnosis"
assert needle in t, "PLANT DID NOT LAND: the worked issue moved"
open(p, "w", encoding="utf-8").write(t.replace(needle, needle + "\nfound at: 4233c3d", 1))
EOF
if python3 /tmp/rp4-copy/test/validate.py; then
  echo "ERROR: a host commit in a public issue body — rule 2, in the example itself"
  exit 1
else
  echo "OK: validator correctly FAILs — no host identifier in the worked body"
fi
