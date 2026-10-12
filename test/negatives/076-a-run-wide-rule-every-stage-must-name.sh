#!/usr/bin/env bash
# name: Negative self-test (a run-wide rule every stage must name)
set -eu
rm -rf /tmp/reach-copy-2 && cp -R . /tmp/reach-copy-2
python3 - <<'EOF'
p = "/tmp/reach-copy-2/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
assert "[`continuity.md`](continuity.md)" in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(
    t.replace("[`continuity.md`](continuity.md)", "`elsewhere`"))
EOF
if python3 /tmp/reach-copy-2/test/validate.py; then
  echo "ERROR: validator passed a stage doctrine that never names continuity.md — the continuous-execution rule sat inside build.md for nine releases and did not work for exactly this reason"
  exit 1
else
  echo "OK: every stage that could be misled by the run mode names it"
fi
