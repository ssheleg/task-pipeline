#!/usr/bin/env bash
# name: Negative self-test (SKILL.md teaching a gate-type vocabulary the schema outgrew)
set -eu
rm -rf /tmp/gt1-copy && cp -R . /tmp/gt1-copy
python3 - <<'EOF'
# The incident: pipeline.schema.json gained `judgment` in v1.73.0 and
# SKILL.md taught auto/manual for seven releases. The plant re-creates
# it by removing the type from the teaching sentence, not the schema —
# the schema is the contract, the sentence is what drifts.
import re
p = "/tmp/gt1-copy/plugins/task-pipeline/skills/task-pipeline/SKILL.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"Each gate has a \*\*type\*\*.*?(?:\n\n)", t, re.S)
assert m and "`judgment`" in m.group(0), "PLANT DID NOT LAND: the teaching sentence moved"
span = m.group(0).replace("`judgment`", "`auto`", 1)
t2 = t[:m.start()] + span + t[m.end():]
assert t2 != t, "PLANT DID NOT LAND: nothing changed"
open(p, "w", encoding="utf-8").write(t2)
EOF
if python3 /tmp/gt1-copy/test/validate.py 2>&1 | grep -q 'the gate-type sentence does not name'; then
  echo "OK: validator FAILs — the schema's vocabulary must reach the sentence that teaches it"
else
  echo "ERROR: SKILL.md taught a stale gate-type vocabulary and nothing objected"
  exit 1
fi
# The reverse direction, from the R-005 reader: the enum is pinned by an
# earlier guard, so the reachable drift is SKILL.md teaching a type the
# schema does not hold — and the first draft left it unguarded.
rm -rf /tmp/gt1b-copy && cp -R . /tmp/gt1b-copy
python3 - <<'EOF'
import re
p = "/tmp/gt1b-copy/plugins/task-pipeline/skills/task-pipeline/SKILL.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"Each gate has a \*\*type\*\*.*?(?:\n\n)", t, re.S)
assert m and "`judgment`" in m.group(0), "PLANT DID NOT LAND: gt1b"
span = m.group(0).replace("`judgment` (no complete", "`advisory` (a made-up ruling), `judgment` (no complete", 1)
t2 = t[:m.start()] + span + t[m.end():]
assert t2 != t, "PLANT DID NOT LAND: gt1b"
open(p, "w", encoding="utf-8").write(t2)
EOF
if python3 /tmp/gt1b-copy/test/validate.py 2>&1 | grep -q 'a taught type no config can declare'; then
  echo "OK: validator FAILs — a taught type the schema lacks is doctrine about nothing"
else
  echo "ERROR: SKILL.md taught a gate type the schema does not hold and nothing objected"
  exit 1
fi
