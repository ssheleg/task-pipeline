#!/usr/bin/env bash
# name: Property check (a legitimate exception two rules away does not trip the carve-out guard)
set -eu
rm -rf /tmp/carve-ctl-copy && cp -R . /tmp/carve-ctl-copy
python3 - <<'EOF'
p = "/tmp/carve-ctl-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
# An `unless` that belongs to the ambiguous-ownership bullet, two rules away
# from the lease rule and in a different bullet from the foreign-item rule.
# Paragraph-wide scoping tripped on exactly this; a guard that fires on
# honest text is worse than one that sleeps, because it teaches evasion.
n = "than deleted, which is irreversible."
assert n in t, "PLANT DID NOT LAND: carve-ctl"
_planted = t.replace(n, "than deleted, which is irreversible unless the operator says otherwise.", 1)
assert _planted != t, "PLANT DID NOT LAND: carve-ctl"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/carve-ctl-copy/test/validate.py >/dev/null 2>&1; then
  echo "OK: the guard reads the rule's own item, so a neighbour's exception is not its business"
else
  echo "ERROR: a legitimate exception in an unrelated rule failed the suite — false positive"
  exit 1
fi
