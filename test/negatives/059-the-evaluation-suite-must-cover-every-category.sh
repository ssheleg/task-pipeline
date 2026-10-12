#!/usr/bin/env bash
# name: Negative self-test (the evaluation suite must cover every category)
set -eu
rm -rf /tmp/evals-copy && cp -R . /tmp/evals-copy
python3 - <<'EOF'
import json
p = "/tmp/evals-copy/evals/task-pipeline.evals.json"
d = json.load(open(p, encoding="utf-8"))
n = len(d["evals"])
d["evals"] = [e for e in d["evals"] if e["category"] != "coexistence"]
assert len(d["evals"]) < n, "PLANT MISSED"
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/evals-copy/test/validate.py; then
  echo "ERROR: validator passed an eval suite with a missing dimension — coexistence is where a broad description steals triggers from narrower skills"
  exit 1
else
  echo "OK: validator runs evals/run.py and requires all five dimensions"
fi
