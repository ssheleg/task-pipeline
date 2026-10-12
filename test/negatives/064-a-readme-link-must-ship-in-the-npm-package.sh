#!/usr/bin/env bash
# name: Negative self-test (a README link must ship in the npm package)
set -eu
rm -rf /tmp/pkg-copy && cp -R . /tmp/pkg-copy
python3 - <<'EOF'
import json
p = "/tmp/pkg-copy/package.json"
d = json.load(open(p, encoding="utf-8"))
assert "evals" in d["files"], "PLANT MISSED"
d["files"] = [f for f in d["files"] if f != "evals"]
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/pkg-copy/test/validate.py; then
  echo "ERROR: validator passed a README that links to something files[] does not publish — the link dangles for every npm install"
  exit 1
else
  echo "OK: validator holds README links to the published package"
fi
