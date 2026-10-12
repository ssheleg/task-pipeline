#!/usr/bin/env bash
# name: Negative self-test (the high-water mark lowered in a COMMITTED change)
set -eu
rm -rf /tmp/hw4-copy && cp -R . /tmp/hw4-copy
python3 - <<'EOF'
import re
p = "/tmp/hw4-copy/plugins/task-pipeline/skills/task-pipeline/references/learned.md"
t = open(p, encoding="utf-8").read()
nums = [int(n) for n in re.findall(r"^\|\s*(\d+)\s*\|\s*\*\*", t, re.M)]
hi = max(nums)
m = re.search(r"^\|\s*%d\s*\|\s*\*\*.*$" % hi, t, re.M)
assert m, "PLANT DID NOT LAND: highest row absent before edit"
t = t[:m.start()] + t[m.end() + 1:]
old = "**Numbers issued so far: %d.**" % hi
assert old in t, "PLANT DID NOT LAND: mark absent"
open(p, "w", encoding="utf-8").write(t.replace(old, "**Numbers issued so far: %d.**" % (hi - 1), 1))
EOF
# COMMIT it. The first version of this test left the edit uncommitted, and the
# check compared the working tree against HEAD — identical on a committed
# checkout, which is what CI runs. The test passed while the check was blind.
git -C /tmp/hw4-copy add -A
git -C /tmp/hw4-copy -c user.email=t@t -c user.name=t commit -q -m "coordinated edit"
if python3 /tmp/hw4-copy/test/validate.py; then
  echo "ERROR: a committed coordinated edit passed — the check compares against the checkout it is in"
  exit 1
else
  echo "OK: validator correctly FAILs — the mark is compared against every value this file has held"
fi
