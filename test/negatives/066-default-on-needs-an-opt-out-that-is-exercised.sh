#!/usr/bin/env bash
# name: Negative self-test (default-on needs an opt-out that is exercised)
set -eu
rm -rf /tmp/optout-copy && cp -R . /tmp/optout-copy
python3 - <<'EOF'
import json
p = "/tmp/optout-copy/evals/task-pipeline.evals.json"
d = json.load(open(p, encoding="utf-8"))
n = len(d["evals"])
d["evals"] = [e for e in d["evals"] if "без пайплайна" not in e.get("query", "")]
assert len(d["evals"]) < n, "PLANT MISSED"
json.dump(d, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
EOF
if python3 /tmp/optout-copy/test/validate.py; then
  echo "ERROR: validator passed a description promising an opt-out phrase that no eval exercises — an escape hatch nobody tests is a trap"
  exit 1
else
  echo "OK: validator ties the description's opt-out to an eval that uses it"
fi
