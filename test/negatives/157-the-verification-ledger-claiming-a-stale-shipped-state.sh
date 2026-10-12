#!/usr/bin/env bash
# name: Negative self-test (the verification ledger claiming a stale shipped state)
set -eu
rm -rf /tmp/vh1-copy && cp -R . /tmp/vh1-copy
python3 - <<'EOF'
# The incident: `Shipped state — v1.72.0` sat six releases under a
# v1.79.1 tree. The plant re-creates the stale header by DERIVING a
# wrong version from the current one, so no release moves its anchor.
import json, re
p = "/tmp/vh1-copy/docs/evidence/verification.md"
t = open(p, encoding="utf-8").read()
cur = json.load(open("/tmp/vh1-copy/package.json"))["version"]
m = re.search(r"^## Shipped state — v(\d+\.\d+\.\d+)", t, re.M)
assert m and m.group(1) == cur, "PLANT DID NOT LAND: header != package.json before the plant"
major, minor, patch = cur.split(".")
wrong = f"{major}.{int(minor)-1}.0"
t2 = t.replace(m.group(0), f"## Shipped state — v{wrong}", 1)
assert t2 != t, "PLANT DID NOT LAND"
open(p, "w", encoding="utf-8").write(t2)
EOF
if python3 /tmp/vh1-copy/test/validate.py 2>&1 | grep -q 'the header sat six releases stale once already'; then
  echo "OK: validator FAILs — the ledger header moves with the version or the run stops"
else
  echo "ERROR: a stale shipped-state header passed and nothing objected"
  exit 1
fi
# Second shape, from the R-005 reader: DELETING the ledger passed the
# first draft while mis-heading it failed — an isfile precondition made
# the louder defect the quieter one.
rm -rf /tmp/vh1b-copy && cp -R . /tmp/vh1b-copy
rm /tmp/vh1b-copy/docs/evidence/verification.md
if python3 /tmp/vh1b-copy/test/validate.py 2>&1 | grep -q 'Removing the file must not be quieter'; then
  echo "OK: validator FAILs — a deleted ledger is louder than a stale one"
else
  echo "ERROR: deleting the verification ledger was quieter than mis-heading it"
  exit 1
fi
