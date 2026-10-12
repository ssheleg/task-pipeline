#!/usr/bin/env bash
# name: Negative self-test (a pushing stage must name the CI verdict)
set -eu
rm -rf /tmp/ci03-copy && cp -R . /tmp/ci03-copy
python3 - <<'EOF'
p = "/tmp/ci03-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
i, j = t.index("## 7 — "), t.index("## 8 — ")
sec = t[i:j]
block = ("**Before\n  tagging, the CI verdict for what was just pushed is READ, not assumed**\n"
         "  ([`conventions.md`](conventions.md) → *The CI verdict*) — a tag on a commit whose\n"
         "  run nobody read is how a red `main` ships.")
assert block in sec, "PLANT DID NOT LAND: the stage-7 CI block is absent before edit"
open(p, "w", encoding="utf-8").write(t[:i] + sec.replace(block, "") + t[j:])
EOF
if python3 /tmp/ci03-copy/test/validate.py; then
  echo "ERROR: validator passed with a pushing stage no longer naming the CI verdict"
  exit 1
else
  echo "OK: validator correctly FAILs — a pushing stage must name the CI verdict"
fi
