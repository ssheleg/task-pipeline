#!/usr/bin/env bash
# name: Negative self-test (the re-derivation axis stops printing its pair)
set -eu
rm -rf /tmp/axis5-copy && cp -R . /tmp/axis5-copy
python3 - <<'EOF'
p = "/tmp/axis5-copy/plugins/task-pipeline/skills/task-pipeline/references/audit.md"
t = open(p, encoding="utf-8").read()
needle = "   verdict:    REFUTED — the sentence and the corpus disagree; the corpus wins\n"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, "", 1))
assert "verdict:    REFUTED" not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/axis5-copy/test/validate.py; then
  echo "ERROR: validator passed an axis that demands a printed pair while showing none"
  exit 1
else
  echo "OK: validator correctly FAILs — the axis shows the pair it demands"
fi
