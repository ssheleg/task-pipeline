#!/usr/bin/env bash
# name: Negative self-test (the probe harness losing its entry point)
set -eu
rm -rf /tmp/ph2-copy && cp -R . /tmp/ph2-copy
python3 - <<'EOF'
p = "/tmp/ph2-copy/package.json"
t = open(p, encoding="utf-8").read()
n = "test/probe.py --self-test"
assert n in t, "PLANT DID NOT LAND: the script moved"
open(p, "w", encoding="utf-8").write(t.replace(n, "true", 1))
EOF
if python3 /tmp/ph2-copy/test/validate.py; then
  echo "ERROR: a harness with no entry point is a file, not a gate"
  exit 1
else
  echo "OK: validator correctly FAILs — the harness is runnable"
fi
