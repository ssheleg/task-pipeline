#!/usr/bin/env bash
# name: Negative self-test (an abandoned run must be told from a finished one)
set -eu
rm -rf /tmp/lifecycle-copy && cp -R . /tmp/lifecycle-copy
# Disarm the check that keeps a run which reached acceptance out of the
# abandoned report. Anchored on the structural branch, not on prose: since
# v1.104.2 it is the early exit shared by all three events, not a `closed`
# flag inside the SessionEnd branch.
python3 - <<'EOF'
import pathlib
p = pathlib.Path('/tmp/lifecycle-copy/plugins/task-pipeline/hooks/run-lifecycle.sh')
s = p.read_text()
needle = 'if any(re.search(r"verdict\\s+pass", l) and re.search(r"accept", l, re.I) for l in stages):'
assert s.count(needle) == 1, "PLANT NO-OP: the acceptance branch moved — re-anchor this plant"
p.write_text(s.replace(needle, 'if False:', 1))
EOF
if python3 /tmp/lifecycle-copy/test/release_gate_test.py; then
  echo "ERROR: the fixtures passed while every finished run was filed as abandoned"; exit 1
fi
echo "OK: the fixtures tell an abandoned run from a finished one"
