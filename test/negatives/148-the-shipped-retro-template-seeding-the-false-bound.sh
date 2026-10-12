#!/usr/bin/env bash
# name: Negative self-test (the SHIPPED retro template seeding the false bound)
set -eu
rm -rf /tmp/rlog2-copy && cp -R . /tmp/rlog2-copy
python3 - <<'EOF'
# The template seeds the heading into every host project, which is how one file's
# defect stops being one file's defect.
p = "/tmp/rlog2-copy/plugins/task-pipeline/skills/task-pipeline/templates/retro.md"
t = open(p, encoding="utf-8").read()
needle = "## Recent log — narrative entries, uncapped and queried rather than read (newest first)"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, "## Recent log — the last 5 entries (newest first)", 1))
assert "the last 5 entries" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rlog2-copy/test/validate.py; then
  echo "ERROR: validator passed a shipped template seeding a bound nothing enforces"
  exit 1
else
  echo "OK: validator correctly FAILs — in the template too, digits or words"
fi
