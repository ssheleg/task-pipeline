#!/usr/bin/env bash
# name: Negative self-test (a findings class has no eval query)
set -eu
rm -rf /tmp/rt08-copy && cp -R . /tmp/rt08-copy
python3 - <<'EOF'
p = "/tmp/rt08-copy/evals/task-pipeline.evals.json"
t = open(p, encoding="utf-8").read()
n = 'нет ли ошибок в обработчике вебхуков'
assert n in t, "PLANT DID NOT LAND: rt08"
open(p, "w", encoding="utf-8").write(t.replace(n, 'is the webhook handler sound', 1))
EOF
if python3 /tmp/rt08-copy/test/validate.py 2>&1 | grep -q 'with no should_trigger query'; then
  echo "OK: validator FAILs — named and untested is the state B-046 measured"
else
  echo "ERROR: a class lost its only eval and nothing objected"
  exit 1
fi
