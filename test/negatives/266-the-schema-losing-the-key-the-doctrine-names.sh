#!/usr/bin/env bash
# name: Negative self-test (the schema losing the key the doctrine names)
set -eu
rm -rf /tmp/rp6-copy && cp -R . /tmp/rp6-copy
python3 - <<'EOF'
p = "/tmp/rp6-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.schema.json"
t = open(p, encoding="utf-8").read()
assert '"publish"' in t, "PLANT DID NOT LAND: the publish key moved"
open(p, "w", encoding="utf-8").write(t.replace('"publish"', '"publish_disabled"', 1))
EOF
if python3 /tmp/rp6-copy/test/validate.py; then
  echo "ERROR: the key the doctrine tells an operator to set validates nothing"
  exit 1
else
  echo "OK: validator correctly FAILs — doctrine and schema name one key"
fi
