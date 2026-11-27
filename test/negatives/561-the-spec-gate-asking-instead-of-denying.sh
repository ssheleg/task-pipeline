#!/usr/bin/env bash
# name: Negative self-test (the spec gate asking instead of denying)
set -eu
rm -rf /tmp/sg-copy && cp -R . /tmp/sg-copy
# Turn the spec gate's refusal back into a question: S0 says a product edit without a
# verified spec is denied, and a question is one keystroke away from the skip.
python3 - <<'EOF2'
p = "/tmp/sg-copy/plugins/task-pipeline/hooks/build-gate.sh"
t = open(p, encoding="utf-8").read()
needle = '"permissionDecision": "deny",'
assert t.count(needle) == 1, "PLANT DID NOT LAND: sg: the deny decision moved"
open(p, "w", encoding="utf-8").write(t.replace(needle, '"permissionDecision": "ask",', 1))
EOF2
if python3 /tmp/sg-copy/test/spec_judge_test.py >/dev/null 2>&1; then
  echo "ERROR: a spec gate that only asks passed the suite"; exit 1
fi
echo "OK: the suite FAILs a spec gate that asks instead of denying"
