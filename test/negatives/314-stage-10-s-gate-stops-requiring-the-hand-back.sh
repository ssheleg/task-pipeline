#!/usr/bin/env bash
# name: Negative self-test (stage 10's gate stops requiring the hand-back)
set -eu
rm -rf /tmp/hb04-copy && cp -R . /tmp/hb04-copy
python3 - <<'EOF'
p = "/tmp/hb04-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
n = "**the hand-back is written**"
assert n in t, "PLANT DID NOT LAND: hb04"
i = t.index(n)
j = t.index("a run\n  that cannot say what happened has not finished, it has stopped;", i)
k = j + len("a run\n  that cannot say what happened has not finished, it has stopped;")
open(p, "w", encoding="utf-8").write(t[:i] + t[k:])
EOF
if python3 /tmp/hb04-copy/test/validate.py 2>&1 | grep -q 'the GATE does not require the hand-back'; then
  echo "OK: validator FAILs — an instruction to report with no gate behind it is 'copy it, tick it'"
else
  echo "ERROR: the gate dropped the hand-back and the doctrine kept it"
  exit 1
fi
