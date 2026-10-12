#!/usr/bin/env bash
# name: Negative self-test (doctrine that stops naming the script must fail)
set -eu
rm -rf /tmp/exp2-copy && cp -R . /tmp/exp2-copy
python3 - <<'EOF'
p = "/tmp/exp2-copy/plugins/task-pipeline/skills/task-pipeline/references/exposure.md"
t = open(p, encoding="utf-8").read()
assert "exposure.sh" in t, "PLANT DID NOT LAND: exposure.md never named the script"
open(p, "w", encoding="utf-8").write(t.replace("exposure.sh", "the-script"))
EOF
if python3 /tmp/exp2-copy/test/validate.py 2>&1 | grep -q "no longer names templates/exposure.sh"; then
  echo "OK: validator FAILs — a seeded script nothing points at is never copied"
else
  echo "ERROR: the doctrine can stop naming it and nothing notices"
  exit 1
fi
