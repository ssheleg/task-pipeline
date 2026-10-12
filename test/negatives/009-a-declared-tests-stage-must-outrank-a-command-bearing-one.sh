#!/usr/bin/env bash
# name: Negative self-test (a declared tests stage must outrank a command-bearing one)
set -eu
rm -rf /tmp/gate-twopass-copy && cp -R . /tmp/gate-twopass-copy
# Kill the first pass of the stage scan, so the gate falls back to the
# first command-bearing stage — the shape that let a green lint stage
# declared before the tests stage release a tag with the suite never
# run. Anchored on the pass-one condition, a structural marker.
python3 - <<'EOF'
import pathlib
p = pathlib.Path('/tmp/gate-twopass-copy/plugins/task-pipeline/hooks/release-gate.sh')
s = p.read_text()
needle = 'if s.get("state") == "tests":'
assert needle in s, "PLANT NO-OP: the two-pass scan moved — re-anchor this plant"
p.write_text(s.replace(needle, 'if False:', 1))
EOF
if python3 /tmp/gate-twopass-copy/test/release_gate_test.py; then
  echo "ERROR: the fixtures passed while a lint stage could capture the tests gate"; exit 1
fi
echo "OK: the fixtures require the declared tests stage to win"
