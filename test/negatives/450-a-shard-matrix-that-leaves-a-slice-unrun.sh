#!/usr/bin/env bash
# name: Negative self-test (a shard matrix that leaves a slice of the suite unrun)
set -eu
rm -rf /tmp/shd1-copy && cp -R . /tmp/shd1-copy
python3 - <<'EOF'
# `--shard I/N` cuts by position modulo N. Drop the last matrix value and one
# slice of the suite is started by no runner, under a job that reports green.
import re
p = "/tmp/shd1-copy/.github/workflows/validate.yml"
t = open(p, encoding="utf-8").read()
m = re.search(r"(?m)^(\s*shard:\s*\[)([^\]]*)(\])", t)
assert m, "PLANT DID NOT LAND: no shard matrix to shrink"
vals = [v.strip() for v in m.group(2).split(",") if v.strip()]
assert len(vals) >= 2, "PLANT DID NOT LAND: a one-shard matrix has no slice to drop"
open(p, "w", encoding="utf-8").write(t[:m.start(2)] + ", ".join(vals[:-1]) + t[m.end(2):])
m2 = re.search(r"(?m)^\s*shard:\s*\[([^\]]*)\]", open(p, encoding="utf-8").read())
assert m2 and len(re.findall(r"\d+", m2.group(1))) == len(vals) - 1, \
    "PLANT DID NOT LAND: the matrix still lists every shard"
EOF
if python3 /tmp/shd1-copy/test/validate.py 2>&1 | grep -q "the shard matrix is"; then
  echo "OK: validator FAILs — every slice the runner cuts has a runner"
else
  echo "ERROR: a slice of the negative self-tests runs nowhere and the gate said nothing"
  exit 1
fi
