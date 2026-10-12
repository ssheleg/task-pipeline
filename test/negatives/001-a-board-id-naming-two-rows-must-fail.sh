#!/usr/bin/env bash
# name: Negative self-test (a board id naming two rows must fail)
set -eu
rm -rf /tmp/dupid-copy && cp -R . /tmp/dupid-copy
python3 - <<'EOF'
# The incident, 2026-09-01: v1.82.0 shipped FOUR rows under TWO ids. The
# validator collected board ids into a SET, where a repeat collapses leaving
# nothing to see — so a run stamp saying "B-115 filed" and a CHANGELOG naming
# the range B-114..B-117 each pointed at two different findings, silently.
#
# The plant works on the COPY and LEAVES it mutated. The first version copied
# one file, mutated the live tree and restored it: correct as a workflow step,
# and invisible to `test/negatives.py`, which finds the scratch dir by looking
# for a literal `cp -R . <dir>` and then diffs it against the repo to tell a
# real defect from a no-op. No scratch dir meant no way to confirm the plant
# landed, and the harness reported the guard as one that DID NOT FIRE — which
# burned v1.82.3, because `negatives.py` is a CI step and not part of `npm test`.
import pathlib, re
p = pathlib.Path("/tmp/dupid-copy/docs/evidence/backlog.md")
lines = p.read_text(encoding="utf-8").split("\n")
rows, first, target = [], None, None
for i, ln in enumerate(lines):
    m = re.match(r"\|\s*(B-\d+[a-z]?)\s*\|", ln)
    if not m:
        continue
    rows.append(i)
    if first is None:
        first = m.group(1)
    else:
        target = i
assert first and target is not None, "PLANT DID NOT LAND: need two board rows to collide"
lines[target] = re.sub(r"^\|\s*B-\d+[a-z]?\s*\|", f"| {first} |", lines[target], count=1)
p.write_text("\n".join(lines), encoding="utf-8")
assert p.read_text(encoding="utf-8").count(f"| {first} |") >= 2, "PLANT DID NOT LAND"
EOF
if (cd /tmp/dupid-copy && python3 test/validate.py) > /tmp/dupid.out 2>&1; then
  echo "ERROR: a board id identifying two rows passed the validator"
  exit 1
fi
grep -q "identifies a second row" /tmp/dupid.out || {
  echo "ERROR: the validator refused, but not for the duplicate id:"; cat /tmp/dupid.out; exit 1; }
echo "OK: a duplicated board id is refused, and the refusal names both lines"
