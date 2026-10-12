#!/usr/bin/env bash
# name: Negative self-test (a description that drops the final stage must fail)
set -eu
rm -rf /tmp/blurb-copy && cp -R . /tmp/blurb-copy
python3 - <<'EOF'
import json
p = "/tmp/blurb-copy/package.json"
_orig_bytes = open(p, "rb").read()
d = json.load(open(p))
d["description"] = d["description"].replace(", acceptance)", ")")
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: a-description-that-drops-the-final-s"
EOF
if python3 /tmp/blurb-copy/test/validate.py; then
  echo "ERROR: validator passed a description that stops one stage short"
  exit 1
else
  echo "OK: validator requires every description to name the flow's final stage"
fi
