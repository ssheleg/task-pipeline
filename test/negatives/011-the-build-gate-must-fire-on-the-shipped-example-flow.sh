#!/usr/bin/env bash
# name: Negative self-test (the build gate must fire on the shipped example flow)
set -eu
rm -rf /tmp/build-dev-copy && cp -R . /tmp/build-dev-copy
# Narrow the build-stage match back to `build` alone. The shipped
# pipeline.example.json names its build stage `dev`, so this exact
# narrowing left the gate never firing on the flow the plugin ships.
# Anchored on the state tuple, a structural marker.
python3 - <<'EOF'
import pathlib
p = pathlib.Path('/tmp/build-dev-copy/plugins/task-pipeline/hooks/build-gate.sh')
s = p.read_text()
needle = 's.get("state") in ("build", "dev")'
assert needle in s, "PLANT NO-OP: the build-state match moved — re-anchor this plant"
p.write_text(s.replace(needle, 's.get("state") == "build"', 1))
EOF
if python3 /tmp/build-dev-copy/test/release_gate_test.py; then
  echo "ERROR: the fixtures passed while the shipped example never armed the build gate"; exit 1
fi
echo "OK: the fixtures require the gate to fire on the example's own dev stage"
