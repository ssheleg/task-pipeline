#!/usr/bin/env bash
# name: Negative self-test (a preflight silent about the skill's own evidence)
set -eu
rm -rf /tmp/pf1-copy && cp -R . /tmp/pf1-copy
python3 - <<'EOF'
# The guard fires only while evals/RESULTS.md claims no blind run — a state
# the 2026-08-31 blind runs ended, which disarmed this plant the honest way
# (the gapmention class: a plant that inherits its precondition switches
# itself off when the repository gets healthier). Construct the state: a
# copy whose RESULTS claims no blind run AND whose preflight says nothing.
p = "/tmp/pf1-copy/evals/RESULTS.md"
t = open(p, encoding="utf-8").read()
t = "**Status note (planted): no blind run has been made on any model.**\n\n" + t
open(p, "w", encoding="utf-8").write(t)
p = "/tmp/pf1-copy/plugins/task-pipeline/skills/task-pipeline/references/companion-skills.md"
t = open(p, encoding="utf-8").read()
n = "This skill's own behaviour is unverified"
assert n in t, "PLANT DID NOT LAND: the behaviour line moved"
open(p, "w", encoding="utf-8").write(t.replace(n, "This skill is ready", 1))
EOF
if python3 /tmp/pf1-copy/test/validate.py; then
  echo "ERROR: a skill silent about its own evidence is read as tested"
  exit 1
else
  echo "OK: validator correctly FAILs — the preflight states what has not been measured"
fi
