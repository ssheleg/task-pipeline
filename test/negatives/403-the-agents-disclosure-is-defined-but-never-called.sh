#!/usr/bin/env bash
# name: Negative self-test (the agents disclosure is defined but never called)
set -eu
rm -rf /tmp/agz1-copy && cp -R . /tmp/agz1-copy
python3 - <<'EOF'
p = "/tmp/agz1-copy/bin/task-pipeline.js"
t = open(p, encoding="utf-8").read()
needle = "  discloseAgents();\n  offerRouters();"
assert needle in t, "PLANT DID NOT LAND: agz1 — the disclosure call is not where expected"
open(p, "w", encoding="utf-8").write(t.replace(needle, "  offerRouters();", 1))
EOF
if python3 /tmp/agz1-copy/test/validate.py; then
  echo "ERROR: a disclosure defined and never called was accepted — a guard that
         reads the source instead of running it is satisfied by dead code"; exit 1
else
  echo "OK: the installers are RUN, not read"
fi
