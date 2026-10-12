#!/usr/bin/env bash
# name: Negative self-test (the example must set run.loop.mode explicitly)
set -eu
rm -rf /tmp/runmode-copy && cp -R . /tmp/runmode-copy
python3 - <<'EOF'
import json
p = "/tmp/runmode-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
d = json.load(open(p, encoding="utf-8"))
# Planted through the parser, not a literal: the previous needle was the
# one-line `"loop": { "mode": "off", ... }` and it stopped matching the moment
# the block grew a queue and an arm point. A probe keyed to formatting tests
# the formatting.
assert d.get("run", {}).get("loop", {}).get("mode"), "PLANT DID NOT LAND: no run.loop.mode to remove"
del d["run"]["loop"]["mode"]
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
EOF
if python3 /tmp/runmode-copy/test/validate.py 2>&1 | grep -q "the schema's legal set is"; then
  echo "OK: the example must DEMONSTRATE the default, not rely on its absence"
else
  echo "ERROR: validator passed an example with no run.loop.mode — the example is what gets copied, so an absent field reads as an oversight rather than a decision"
  exit 1
fi
