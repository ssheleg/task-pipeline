#!/usr/bin/env bash
# name: Negative self-test (neighbour probe — Part 1a loses the floor while the file keeps it)
set -eu
rm -rf /tmp/nb02-copy && cp -R . /tmp/nb02-copy
python3 - <<'EOF'
p = "/tmp/nb02-copy/plugins/task-pipeline/skills/task-pipeline/references/continuity.md"
t = open(p, encoding="utf-8").read()
# This probe DELETES from Part 1a and relies on the copies next door. Assert
# they exist, or a later edit silently demotes it to a delete-only probe.
assert " ".join(t.split()).count("generic flag is not a specific authorization") >= 3, \
    "PLANT DID NOT LAND: nb02 — fewer neighbour copies than this probe assumes"
head = "## Part 1a"
i = t.index(head); j = t.index("\n## ", i + len(head))
sec = t[i:j]
n = "*a generic flag is not a specific authorization*, and arming a"
assert n in sec, "PLANT DID NOT LAND: nb02"
# Break the subject; the phrase survives twice elsewhere in the file — in the
# section written twenty-nine releases earlier and in a Rationalizations row,
# which is exactly what kept the first version of this guard green.
open(p, "w", encoding="utf-8").write(t[:i] + sec.replace(n, "arming a", 1) + t[j:])
EOF
if python3 /tmp/nb02-copy/test/validate.py 2>&1 | grep -q 'Part 1a.: the sentence that keeps arming'; then
  echo "OK: validator FAILs — a copy elsewhere in the file is not the copy this section's reader meets"
else
  echo "ERROR: Part 1a lost the floor and two copies elsewhere kept the guard green"
  exit 1
fi
