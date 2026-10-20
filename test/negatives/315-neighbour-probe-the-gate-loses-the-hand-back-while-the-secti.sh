#!/usr/bin/env bash
# name: Negative self-test (neighbour probe — the gate loses the hand-back while the section keeps the word)
set -eu
rm -rf /tmp/hb05-copy && cp -R . /tmp/hb05-copy
python3 - <<'EOF'
p = "/tmp/hb05-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
n = "**the hand-back is written**"
i = t.index(n)
j = t.index("a run\n  that cannot say what happened has not finished, it has stopped;", i)
k = j + len("a run\n  that cannot say what happened has not finished, it has stopped;")
t = t[:i] + t[k:]
# Plant the CURRENT needle next door: same stage, not the gate bullet.
needle = "- **The hand-back** is described in progress.md and printed by the harness."
t = t.replace("- **GATE (auto):** the ladder walk ran", needle + "\n- **GATE (auto):** the ladder walk ran", 1)
assert needle in t, "PLANT DID NOT LAND: hb05 neighbour"
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/hb05-copy/test/validate.py 2>&1 | grep -q 'the GATE does not require the hand-back'; then
  echo "OK: validator FAILs — a sibling bullet naming the hand-back is not the gate requiring it"
else
  echo "ERROR: a neighbouring bullet answered for the gate"
  exit 1
fi
