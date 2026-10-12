#!/usr/bin/env bash
# name: Negative self-test (the retrospective must reach the surfaces that enforce stage 10)
set -eu
rm -rf /tmp/retro-anchor-copy && cp -R . /tmp/retro-anchor-copy
python3 - <<'EOF'
import re
p = "/tmp/retro-anchor-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(re.sub(r"retro", "post", t, flags=re.I))
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: the-retrospective-must-reach-the-sur"
EOF
if python3 /tmp/retro-anchor-copy/test/validate.py; then
  echo "ERROR: validator passed a close-out doctrine that never mentions the retro — the rule would be declared in SKILL.md and enforced nowhere"
  exit 1
else
  echo "OK: validator requires the retro to reach the stage-10 surfaces"
fi
