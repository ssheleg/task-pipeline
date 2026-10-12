#!/usr/bin/env bash
# name: Negative self-test (stages.md's stage-5 heading is renamed away)
set -eu
rm -rf /tmp/cv10-copy && cp -R . /tmp/cv10-copy
python3 - <<'EOF'
p = "/tmp/cv10-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
old = "## 5 — Dev"
assert old in t, "PLANT DID NOT LAND: cv10 — no stage 5 heading"
# NOT "## 5 — Development": `_section` matches by prefix, so extending the name
# still resolves the section and the None branch is never reached. The plant has
# to make the heading genuinely unfindable, which is what a real rename does.
open(p, "w", encoding="utf-8").write(t.replace(old, "## 5 — Implementation", 1))
EOF
out=$(python3 /tmp/cv10-copy/test/validate.py 2>&1 || true)
if echo "$out" | grep -q "references/stages.md: no .5 — Dev. section"; then
  echo "OK: validator FAILs by name — the stage-list guard catches the rename too, and this branch is now proven in its own right"
else
  echo "ERROR: the None branch of the stages.md site is unproven"
  exit 1
fi
