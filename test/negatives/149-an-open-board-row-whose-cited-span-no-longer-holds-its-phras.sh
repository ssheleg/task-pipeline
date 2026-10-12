#!/usr/bin/env bash
# name: Negative self-test (an open board row whose cited span no longer holds its phrase)
set -eu
rm -rf /tmp/cite1-copy && cp -R . /tmp/cite1-copy
python3 - <<'EOF'
# Five `file:line-line` addresses in open rows resolved to real lines and pointed at
# the wrong text — B-094 cited gates.md:135-137 for «the check has been probed» when
# it sits at 180. A line number is the most fragile address a document carries:
# every edit above it moves it and nothing notices, because the file still exists
# and the line still exists.
import re
p = "/tmp/cite1-copy/docs/evidence/backlog.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"`references/gates\.md:(\d+)-(\d+)` makes \*«the check has been probed»\*", t)
assert m, "PLANT DID NOT LAND: B-094's cited span is not where this plant reads it"
moved = m.group(0).replace(m.group(1) + "-" + m.group(2), "135-137")
open(p, "w", encoding="utf-8").write(t.replace(m.group(0), moved, 1))
assert "gates.md:135-137" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/cite1-copy/test/validate.py; then
  echo "ERROR: validator passed a citation that resolves and points at the wrong text"
  exit 1
else
  echo "OK: validator correctly FAILs — a citation that resolves is not a citation that is current"
fi
