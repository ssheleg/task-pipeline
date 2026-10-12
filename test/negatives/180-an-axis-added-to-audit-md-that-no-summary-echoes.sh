#!/usr/bin/env bash
# name: Negative self-test (an axis added to audit.md that no summary echoes)
set -eu
rm -rf /tmp/axis2-copy && cp -R . /tmp/axis2-copy
python3 - <<'EOF'
p = "/tmp/axis2-copy/plugins/task-pipeline/skills/task-pipeline/references/audit.md"
t = open(p, encoding="utf-8").read()
needle = "\n**The crossover is measurable, so measure it.**"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
t = t.replace(needle, "\n7. **Adversarial reading** — an axis defined and never summarised.\n" + needle, 1)
open(p, "w", encoding="utf-8").write(t)
assert "Adversarial reading" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/axis2-copy/test/validate.py; then
  echo "ERROR: validator passed a new axis that reached the definition and no consumer"
  exit 1
else
  echo "OK: validator correctly FAILs — the plant lands in the file that DEFINES the axes"
fi
