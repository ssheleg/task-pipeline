#!/usr/bin/env bash
# name: Negative self-test (a new reference must reach the README and the manifest)
set -eu
rm -rf /tmp/reach-copy && cp -R . /tmp/reach-copy
python3 - <<'EOF'
p = "/tmp/reach-copy/README.md"
t = open(p, encoding="utf-8").read()
assert "references/setup.md" in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(t.replace("references/setup.md", "references/gone.md"))
EOF
if python3 /tmp/reach-copy/test/validate.py; then
  echo "ERROR: validator passed a reference nothing tells a reader about — reachability from SKILL.md proves an agent can find it, not that anybody was told it exists"
  exit 1
else
  echo "OK: every reference must reach the README map and the portability manifest"
fi
