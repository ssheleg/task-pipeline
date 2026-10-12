#!/usr/bin/env bash
# name: Negative self-test (a citation must name a section that exists)
set -eu
rm -rf /tmp/cite-copy && cp -R . /tmp/cite-copy
python3 - <<'EOF'
p = "/tmp/cite-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
assert "→ *Axis C*" in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(t.replace("→ *Axis C*", "→ *Axis Q*", 1))
EOF
if python3 /tmp/cite-copy/test/validate.py; then
  echo "ERROR: validator passed a citation whose file resolves and whose section does not — the one a link checker cannot catch and a reader believes"
  exit 1
else
  echo "OK: validator checks section-qualified citations against the target's headings"
fi
