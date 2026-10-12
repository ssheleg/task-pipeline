#!/usr/bin/env bash
# name: Negative self-test (a seeded matrix without the meta-row has a hole)
set -eu
rm -rf /tmp/meta-copy && cp -R . /tmp/meta-copy
python3 - <<'EOF'
p = "/tmp/meta-copy/plugins/task-pipeline/skills/task-pipeline/templates/docmap.md"
t = open(p, encoding="utf-8").read()
assert "A new document or rule" in t, "PLANT MISSED"
t = t.replace("A new document or rule", "A different change type", 1)
t = t.replace("adding a document", "adding a thing")
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/meta-copy/test/validate.py; then
  echo "ERROR: validator passed a propagation matrix with no row for adding a document — nine findings across five audits were that one missing row"
  exit 1
else
  echo "OK: the seeded matrix must carry the meta-row"
fi
