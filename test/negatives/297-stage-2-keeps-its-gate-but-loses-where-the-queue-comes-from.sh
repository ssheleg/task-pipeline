#!/usr/bin/env bash
# name: Negative self-test (stage 2 keeps its gate but loses where the queue comes from)
set -eu
rm -rf /tmp/lp07-copy && cp -R . /tmp/lp07-copy
python3 - <<'EOF'
p = "/tmp/lp07-copy/plugins/task-pipeline/skills/task-pipeline/references/stage-02-brainstorm.md"
t = open(p, encoding="utf-8").read()
head = "- **The queue exists here, so the loop arms here**"
tail = None  # The gate stays in the spine, outside this detail.
assert head in t, "PLANT DID NOT LAND: lp07"
# The GATE clause is left INTACT. Rekeying the guard onto the gate silently
# dropped this case — deleting the whole bullet passed, and this probe kept
# firing only because it used to delete the gate clause too, which made it a
# duplicate of nb03. The obligation and its reason are two statements of one
# rule, and a probe that tests both tests neither.
i = t.index(head); j = len(t)
open(p, "w", encoding="utf-8").write(t[:i] + t[j:])
EOF
if python3 /tmp/lp07-copy/test/validate.py 2>&1 | grep -q "no longer explains where the queue comes from"; then
  echo "OK: validator FAILs — the gate's obligation without its reason is half a rule"
else
  echo "ERROR: the queue bullet vanished while the gate kept its clause, and nothing objected"
  exit 1
fi
