#!/usr/bin/env bash
# name: Negative self-test (the SURFACED zero stops being checked against what the run filed)
set -eu
rm -rf /tmp/sf1-copy && cp -R . /tmp/sf1-copy
python3 - <<'EOF'
p = "/tmp/sf1-copy/plugins/task-pipeline/skills/task-pipeline/references/progress.md"
t = open(p, encoding="utf-8").read()
n = 'is checked against what the run filed'
assert n in t, "PLANT DID NOT LAND: sf1"
_planted = t.replace(n, 'is worth writing carefully', 1)
assert _planted != t, "PLANT DID NOT LAND: sf1"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/sf1-copy/test/validate.py 2>&1 | grep -q 'no longer checked against the artefacts'; then
  echo "OK: validator FAILs — the one hand-back field with no lower bound needs the check DEC-0001 decided"
else
  echo "ERROR: SURFACED went back to a zero nobody can disagree with"
  exit 1
fi
