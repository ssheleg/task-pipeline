#!/usr/bin/env bash
# name: Negative self-test (a living document may not restate a stale count)
set -eu
rm -rf /tmp/count-copy && cp -R . /tmp/count-copy
python3 - <<'EOF'
p = "/tmp/count-copy/SKILL-CARD.md"
t = open(p, encoding="utf-8").read()
import re
# The guard rejects ANY hand-written guard count in a living document, so
# the plant INTRODUCES one rather than editing an existing number. The
# earlier plant edited the count in place and broke the day the prose
# stopped restating it — a test coupled to the defect it was written
# against instead of to the rule.
assert not re.search(r"\b\d+\+?\s+(?:structural\s+)?guards\b", t), \
    "PLANT MISSED: SKILL-CARD.md already restates a count, so this plants nothing"
anchor = "## What to check before you trust it"
assert anchor in t, "PLANT MISSED: anchor heading absent"
open(p, "w", encoding="utf-8").write(
    t.replace(anchor, anchor + "\n\nThis skill ships 3 guards.\n", 1))
EOF
if python3 /tmp/count-copy/test/validate.py; then
  echo "ERROR: validator passed a hand-written guard count that disagrees with the workflow"
  exit 1
else
  echo "OK: validator computes the guard count instead of trusting the prose"
fi
