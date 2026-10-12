#!/usr/bin/env bash
# name: Negative self-test (a blind gate must fail closed, not skip)
set -eu
rm -rf /tmp/gate-blind-copy && cp -R . /tmp/gate-blind-copy
# Revert the blind branch to the shape it actually shipped with: an
# unreadable payload with a run in flight printed "skip" and exited 0,
# so the gate allowed every release for as long as its stdin plumbing
# was broken. Anchored on the structural verdict line, not on prose.
python3 - <<'EOF'
import pathlib
p = pathlib.Path('/tmp/gate-blind-copy/plugins/task-pipeline/hooks/release-gate.sh')
s = p.read_text()
needle = 'print("blind\\t%s" % why); raise SystemExit(0)'
assert needle in s, "PLANT NO-OP: the blind verdict moved — re-anchor this plant"
p.write_text(s.replace(needle, 'print("skip"); raise SystemExit(0)', 1))
EOF
if python3 /tmp/gate-blind-copy/test/release_gate_test.py; then
  echo "ERROR: the fixtures passed against a gate that skips when it cannot see"; exit 1
fi
echo "OK: the fixtures require a blind gate to fail closed"
