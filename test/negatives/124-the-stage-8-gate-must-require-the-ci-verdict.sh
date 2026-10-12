#!/usr/bin/env bash
# name: Negative self-test (the stage-8 gate must require the CI verdict)
set -eu
rm -rf /tmp/ci05-copy && cp -R . /tmp/ci05-copy
python3 - <<'EOF'
import json, re
p = "/tmp/ci05-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
d = json.load(open(p, encoding="utf-8"))
s = [x for x in d["stages"] if x["state"] == "post-deploy"][0]
c = s["gate"]["check"]
assert "CI VERDICT" in c, "PLANT DID NOT LAND: the stage-8 gate does not require it before the edit"
s["gate"]["check"] = re.sub(r"(?i)ci verdict", "vibes check", c)
open(p, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
EOF
if python3 /tmp/ci05-copy/test/validate.py; then
  echo "ERROR: validator passed with the stage-8 gate no longer requiring the CI verdict"
  exit 1
else
  echo "OK: validator correctly FAILs — the stage-8 gate must require the CI verdict"
fi
