#!/usr/bin/env bash
# name: Negative self-test (waiting decisions become a list instead of a question)
set -eu
rm -rf /tmp/hb02-copy && cp -R . /tmp/hb02-copy
python3 - <<'EOF'
p = "/tmp/hb02-copy/plugins/task-pipeline/skills/task-pipeline/references/progress.md"
t = open(p, encoding="utf-8").read()
n = "**DECISIONS WAITING are asked, not listed.**"
assert n in t, "PLANT DID NOT LAND: hb02 paragraph"
tpl = "DECISIONS WAITING  <n>   each as a question with options, asked HERE"
assert tpl in t, "PLANT DID NOT LAND: hb02 template line"
# The rule is stated twice — in the template and in the paragraph that owns it.
# Removing one leaves it stated, and the guard was right not to fire; this
# probe's first version tested the paragraph alone and called that a defect.
t = t.replace(n, "**DECISIONS WAITING are recorded for later.**", 1)
t = t.replace(tpl, "DECISIONS WAITING  <n>   each with options, for the record", 1)
t = t.replace("Ask it at the boundary, with options and a\nrecommendation, in the same breath as the report.",
              "Record it with options and a recommendation.", 1)
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/hb02-copy/test/validate.py 2>&1 | grep -q 'DECISIONS WAITING line does not say the question is ASKED'; then
  echo "OK: validator FAILs — a question parked in a report is answered days later, if at all"
else
  echo "ERROR: decisions became a list and the boundary stopped asking"
  exit 1
fi
