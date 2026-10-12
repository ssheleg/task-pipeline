#!/usr/bin/env bash
# name: Negative self-test (the autonomy sweep must not drift between its two homes)
set -eu
rm -rf /tmp/sweep-copy && cp -R . /tmp/sweep-copy
python3 - <<'EOF'
p = "/tmp/sweep-copy/plugins/task-pipeline/skills/task-pipeline/templates/brief.md"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
t = "\n".join(l for l in t.splitlines() if not l.startswith("| 8 Post-deploy"))
open(p, "w", encoding="utf-8").write(t + "\n")
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: the-autonomy-sweep-must-not-drift-be"
EOF
if python3 /tmp/sweep-copy/test/validate.py; then
  echo "ERROR: validator passed a brief template whose sweep drops a stage the grill asks about"
  exit 1
else
  echo "OK: validator keeps grill.md's sweep and brief.md's sweep covering the same stages"
fi
