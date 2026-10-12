#!/usr/bin/env bash
# name: Negative self-test (a version surface outside the guarded set)
set -eu
rm -rf /tmp/lse1-copy && cp -R . /tmp/lse1-copy
python3 - <<'EOF'
import json
p = "/tmp/lse1-copy/.claude/agent-sync.json"
d = json.load(open(p, encoding="utf-8"))
g = d["guardedFiles"]
assert "SKILL-CARD.md" in g, "PLANT DID NOT LAND: lse1 — the card is already unguarded"
d["guardedFiles"] = [x for x in g if x != "SKILL-CARD.md"]
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/lse1-copy/test/validate.py; then
  echo "ERROR: a file declaring the current version was accepted outside guardedFiles
         — B-065: the version-sync invariant makes these surfaces move together, so
         two agents bumping a version collide there with no lease. This project lost
         four version numbers and a files[] entry to exactly that"; exit 1
else
  echo "OK: the version surfaces are discovered and each must be lease-guarded"
fi
