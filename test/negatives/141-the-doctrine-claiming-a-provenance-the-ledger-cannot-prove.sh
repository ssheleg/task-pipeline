#!/usr/bin/env bash
# name: Negative self-test (the doctrine claiming a provenance the ledger cannot prove)
set -eu
rm -rf /tmp/prov1-copy && cp -R . /tmp/prov1-copy
python3 - <<'EOF'
# B-014's class, committed by the mechanism built to close B-061: `read:` and
# `gate:` were declared «hook-written, never agent-written» while both land in
# `.task-pipeline/run.md` — the file the agent appends to at every stage — with no
# writer field and no provenance check in graph.py.
p = "/tmp/prov1-copy/plugins/task-pipeline/skills/task-pipeline/templates/run.md"
t = open(p, encoding="utf-8").read()
needle = "`read:` is **written by a hook rather than by the agent**"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, "`read:` is hook-written, never agent-written", 1))
assert "never agent-written," in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/prov1-copy/test/validate.py; then
  echo "ERROR: validator passed a provenance claim the ledger format cannot support"
  exit 1
else
  echo "OK: validator correctly FAILs — mark it unattested or do not claim it"
fi
