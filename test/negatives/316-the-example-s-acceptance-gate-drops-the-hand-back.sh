#!/usr/bin/env bash
# name: Negative self-test (the example's acceptance gate drops the hand-back)
set -eu
rm -rf /tmp/hb06-copy && cp -R . /tmp/hb06-copy
python3 - <<'EOF'
import json
p = "/tmp/hb06-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
d = json.load(open(p, encoding="utf-8"))
s = [x for x in d["stages"] if x.get("state") == "acceptance"][0]
c = s["gate"]["check"]
i = c.upper().index("THE HAND-BACK IS WRITTEN")
assert i > 0, "PLANT DID NOT LAND: hb06"
s["gate"]["check"] = c[:i].rstrip(". ") + "."
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
EOF
if python3 /tmp/hb06-copy/test/validate.py 2>&1 | grep -q 'its gate does not require the hand-back'; then
  echo "OK: validator FAILs — the two surfaces that state one rule may not drift"
else
  echo "ERROR: the machine-readable gate lost the hand-back while the prose kept it"
  exit 1
fi
