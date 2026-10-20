#!/usr/bin/env bash
# name: Negative self-test (a colon-space in frontmatter must be rejected)
set -eu
rm -rf /tmp/ed5-copy && cp -R . /tmp/ed5-copy
python3 - <<'EOF'
import re
p = "/tmp/ed5-copy/plugins/task-pipeline/skills/evidence-docs/SKILL.md"
t = open(p, encoding="utf-8").read()
# The hazard is a colon-space in an UNQUOTED scalar — that is what YAML
# truncates. This probe used to plant one inside the description and stopped
# reproducing anything the day that description was quoted: `: ` between
# quotes is legal and loses nothing, so the guard fell silent for the right
# reason and the probe called it a failure. Strip the quotes first, then
# plant, so the plant recreates the hazard rather than a legal string.
m = re.search(r'^description: "(.*)"\s*$', t, re.M)
assert m, "PLANT DID NOT LAND: description is not a quoted scalar"
_unquoted = "description: " + m.group(1)
# Since 1.98.0 the description itself carries `read as true: a decision record`, legal
# between quotes; unquoting it is the plant.
needle = "read as true: a decision record"
assert needle in _unquoted, "PLANT DID NOT LAND: needle absent before edit"
_planted = t[:m.start()] + _unquoted + t[m.end():]
assert _planted != t, "PLANT DID NOT LAND"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ed5-copy/test/validate.py; then
  echo "ERROR: validator passed frontmatter that YAML drops silently"
  exit 1
else
  echo "OK: validator correctly FAILs — a colon-space in frontmatter"
fi
