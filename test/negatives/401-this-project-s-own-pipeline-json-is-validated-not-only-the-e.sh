#!/usr/bin/env bash
# name: Negative self-test (this project's own pipeline.json is validated, not only the example)
set -eu
rm -rf /tmp/gx4-copy && cp -R . /tmp/gx4-copy
python3 - <<'EOF'
import json
p = "/tmp/gx4-copy/pipeline.json"
d = json.load(open(p, encoding="utf-8"))
# `queue` is an enum in the schema, so a value outside it is refused — but
# only because something validates THIS file. The example conforming proves
# the example conforms, which is what this plant exists to keep true.
assert d["run"]["loop"]["queue"] != "not-a-queue", "PLANT DID NOT LAND: gx4"
d["run"]["loop"]["queue"] = "not-a-queue"
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/gx4-copy/test/validate.py; then
  echo "ERROR: the project's own config was never validated against its schema"; exit 1
else
  echo "OK: pipeline.json is validated against pipeline.schema.json"
fi
