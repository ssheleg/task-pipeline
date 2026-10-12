#!/usr/bin/env bash
# name: Negative self-test (the release gate must be able to block)
set -eu
rm -rf /tmp/gate-hook-copy && cp -R . /tmp/gate-hook-copy
# Disarm the gate the way it was actually broken once: make the decision
# unreachable, so every act classifies as "not a release". Anchored on the
# env handoff — a structural marker — rather than on any prose around it.
python3 - <<'EOF'
import pathlib
p = pathlib.Path('/tmp/gate-hook-copy/plugins/task-pipeline/hooks/release-gate.sh')
s = p.read_text()
needle = 'HOOK_INPUT="$input" python3 -'
assert needle in s, "PLANT NO-OP: the payload handoff moved — re-anchor this plant"
p.write_text(s.replace(needle, 'HOOK_INPUT="" python3 -'))
EOF
if python3 /tmp/gate-hook-copy/test/release_gate_test.py; then
  echo "ERROR: the fixtures passed against a gate that blocks nothing"; exit 1
fi
echo "OK: the release-gate fixtures detect a gate that fails open"
