#!/usr/bin/env bash
# name: Negative self-test (the gate must require the observation, not just the claim)
set -eu
rm -rf /tmp/gate-obs-copy && cp -R . /tmp/gate-obs-copy
# Disarm the corroboration: make the gate accept the agent's claim alone.
# Anchored on the structural marker — the `if command:` branch — rather
# than on any prose around it.
python3 - <<'EOF'
import pathlib
p = pathlib.Path('/tmp/gate-obs-copy/plugins/task-pipeline/hooks/release-gate.sh')
s = p.read_text()
needle = 'if command:'
assert needle in s, "PLANT NO-OP: the corroboration branch moved — re-anchor this plant"
p.write_text(s.replace(needle, 'if False:', 1))
EOF
if python3 /tmp/gate-obs-copy/test/release_gate_test.py; then
  echo "ERROR: the fixtures passed against a gate that trusts the claim alone"; exit 1
fi
echo "OK: the fixtures require the observation, not only the claim"
