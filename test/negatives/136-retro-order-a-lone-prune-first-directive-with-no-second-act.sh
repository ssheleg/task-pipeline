#!/usr/bin/env bash
# name: Negative self-test (retro order — a lone prune-first directive with no second act)
set -eu
rm -rf /tmp/ord4-copy && cp -R . /tmp/ord4-copy
python3 - <<'EOF'
p = "/tmp/ord4-copy/plugins/task-pipeline/skills/evidence-docs/SKILL.md"
t = open(p, encoding="utf-8").read()
needle = "stamp first (the cold trigger reads it), then prune to a cap of ten"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
t = t.replace(needle, "prune first, cap of ten", 1)
open(p, "w", encoding="utf-8").write(t)
assert "prune first, cap of ten" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/ord4-copy/test/validate.py; then
  echo "ERROR: validator passed a lone prune-first directive — the table-cell shape"
  exit 1
else
  echo "OK: validator correctly FAILs — a one-act directive is covered"
fi
