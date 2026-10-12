#!/usr/bin/env bash
# name: Negative self-test (npm test must run the validator)
set -eu
rm -rf /tmp/script-copy && cp -R . /tmp/script-copy
python3 - <<'EOF'
import json
p = "/tmp/script-copy/package.json"
_orig_bytes = open(p, "rb").read()
d = json.load(open(p))
d["scripts"] = {"test": "echo ok"}
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: npm-test-must-run-the-validator"
EOF
if python3 /tmp/script-copy/test/validate.py; then
  echo "ERROR: validator passed a package.json whose test script skips the validator"
  exit 1
else
  echo "OK: validator requires npm test to run test/validate.py"
fi
