#!/usr/bin/env bash
# name: Negative self-test (the Human column renamed away)
set -eu
rm -rf /tmp/vf6-copy && cp -R . /tmp/vf6-copy
python3 - <<'EOF'
p = "/tmp/vf6-copy/docs/evidence/verification.md"
t = open(p, encoding="utf-8").read()
# The literal moved when `Environment` arrived (B-099). A plant that spells the
# whole header describes the table it was written against — which is the same
# lesson the property check below already carries about cell CONTENT.
needle = "| Observed at | Environment | Auto | Human | Note |"
assert needle in t, "PLANT DID NOT LAND: the header is not where the guard reads it"
open(p, "w", encoding="utf-8").write(t.replace(needle, "| Auto | Person | Note |", 1))
EOF
if python3 /tmp/vf6-copy/test/validate.py; then
  echo "ERROR: the guard could not find its subject and passed everything"
  exit 1
else
  echo "OK: validator correctly FAILs — a guard that cannot locate its column says so"
fi
