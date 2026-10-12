#!/usr/bin/env bash
# name: Negative self-test (the probe harness losing its target-guard assertion)
set -eu
rm -rf /tmp/ph1-copy && cp -R . /tmp/ph1-copy
python3 - <<'EOF'
p = "/tmp/ph1-copy/test/probe.py"
t = open(p, encoding="utf-8").read()
assert "expect" in t, "PLANT DID NOT LAND: the harness moved"
open(p, "w", encoding="utf-8").write(t.replace("expect", "wanted"))
EOF
if python3 /tmp/ph1-copy/test/validate.py; then
  echo "ERROR: a probe that proves only that SOMETHING broke proves nothing about its guard"
  exit 1
else
  echo "OK: validator correctly FAILs — a plant names the guard it targets"
fi
