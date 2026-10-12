#!/usr/bin/env bash
# name: Negative self-test (verdict count must not drift from the dev gate)
set -eu
rm -rf /tmp/verdict-copy && cp -R . /tmp/verdict-copy
python3 - <<'EOF'
p = "/tmp/verdict-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(t.replace("with **all three** verdicts", "with **both** verdicts"))
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: verdict-count-must-not-drift-from-th"
EOF
if python3 /tmp/verdict-copy/test/validate.py; then
  echo "ERROR: validator passed 'both verdicts' while the dev gate declares three"
  exit 1
else
  echo "OK: validator keeps the review verdict count consistent across surfaces"
fi
