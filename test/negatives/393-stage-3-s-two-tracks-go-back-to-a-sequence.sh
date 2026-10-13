#!/usr/bin/env bash
# name: Negative self-test (stage 3's two tracks go back to a sequence)
set -eu
rm -rf /tmp/cx4-copy && cp -R . /tmp/cx4-copy
python3 - <<'EOF'
import re
p = "/tmp/cx4-copy/plugins/task-pipeline/skills/task-pipeline/references/stage-03-spec.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^## 3 — Spec.*?(?=^## |\Z)", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: cx4 — no stage 3 section"
sec = re.sub(r"(?i)parallel", "ordered", m.group(0))
assert sec != m.group(0), "PLANT DID NOT LAND: cx4 — stage 3 never named it"
assert "converge" in sec, "PLANT OVERREACHED: cx3's subject must survive"
open(p, "w", encoding="utf-8").write(t[:m.start()] + sec + t[m.end():])
EOF
if python3 /tmp/cx4-copy/test/validate.py 2>&1 | grep -q "still written as a sequence"; then
  echo "OK: validator FAILs — a false order teaches a run to wait for a result that never arrives"
else
  echo "ERROR: the fake edge can come back"
  exit 1
fi
