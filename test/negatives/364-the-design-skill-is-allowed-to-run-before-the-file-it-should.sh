#!/usr/bin/env bash
# name: Negative self-test (the design skill is allowed to run before the file it should follow)
set -eu
rm -rf /tmp/fig1-copy && cp -R . /tmp/fig1-copy
python3 - <<'EOF'
p = "/tmp/fig1-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
n = 'runs **after** the file, never instead of it'
assert n in t, "PLANT DID NOT LAND: fig1"
_planted = t.replace(n, 'is also worth consulting', 1)
assert _planted != t, "PLANT DID NOT LAND: fig1"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/fig1-copy/test/validate.py 2>&1 | grep -q 'order of authority is gone'; then
  echo "OK: validator FAILs — sheleg-design after the frame, never instead of it"
else
  echo "ERROR: the visual skill may now invent what the frame already decided"
  exit 1
fi
