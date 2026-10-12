#!/usr/bin/env bash
# name: Negative self-test (the stage-4 gate stops reading the Edges count)
set -eu
rm -rf /tmp/fe6-copy && cp -R . /tmp/fe6-copy
python3 - <<'EOF'
import re
p = "/tmp/fe6-copy/plugins/task-pipeline/skills/task-pipeline/references/planning.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^## GATE \(auto\).*", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: fe6 — no GATE section"
_gate = re.sub(r"(?i)edges", "arrows", m.group(0))
assert _gate != m.group(0), "PLANT DID NOT LAND: fe6 — the GATE never named it"
_planted = t[:m.start()] + _gate
assert "Edges:" in _planted, "PLANT OVERREACHED: the self-review template must survive"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/fe6-copy/test/validate.py 2>&1 | grep -q "does not read the .Edges.. count"; then
  echo "OK: validator FAILs — the template can keep the line while the gate stops requiring it"
else
  echo "ERROR: only one half of the stage-4 gate text is guarded"
  exit 1
fi
