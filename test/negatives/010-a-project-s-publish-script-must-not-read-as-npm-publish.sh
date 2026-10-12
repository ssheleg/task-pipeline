#!/usr/bin/env bash
# name: Negative self-test (a project's publish script must not read as npm publish)
set -eu
rm -rf /tmp/gate-npmrun-copy && cp -R . /tmp/gate-npmrun-copy
# Restore the overmatch this gate shipped with: `publish` anywhere in
# npm's argument list classified `npm run publish` — a project's own
# script — as the registry act. Anchored on the subcommand scan.
python3 - <<'EOF'
import pathlib
p = pathlib.Path('/tmp/gate-npmrun-copy/plugins/task-pipeline/hooks/release-gate.sh')
s = p.read_text()
needle = 'for a in rest:'
assert needle in s, "PLANT NO-OP: the npm subcommand scan moved — re-anchor this plant"
p.write_text(s.replace(needle, 'for a in (["publish"] if "publish" in rest else []):', 1))
EOF
if python3 /tmp/gate-npmrun-copy/test/release_gate_test.py; then
  echo "ERROR: the fixtures passed while npm run publish was gated as npm publish"; exit 1
fi
echo "OK: the fixtures tell a project script from the registry act"
