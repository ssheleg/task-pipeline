#!/usr/bin/env bash
# name: Negative self-test (a run missing a declared stage must fail)
set -eu
rm -rf /tmp/stagecov && mkdir -p /tmp/stagecov/.task-pipeline /tmp/stagecov/scripts
cp plugins/task-pipeline/skills/task-pipeline/templates/stage-coverage.sh /tmp/stagecov/scripts/
python3 - <<'PY'
# The incident: a run closed with 0,1,2,5,6,7,8,9,10 recorded and 3 and 4 never
# stamped. The status line printed `3· 4·` and 73% and was right; nothing read it.
# Stage 7's release gate could not have caught it — it fires before 8, 9 and 10
# exist and asks only about the tests stage.
import json
cfg = {"version": 1, "stages": [
    {"id": i, "state": s, "name": s.title(),
     "skills": ["x"], "gate": {"type": "auto", "check": "a criterion long enough to be real, stated"}}
    for i, s in enumerate(["intake", "docs", "brainstorm", "spec", "plan"])]}
json.dump(cfg, open("/tmp/stagecov/pipeline.json", "w"))
led = "\n".join(
    f"stage: {i} x — gate auto — verdict pass — 2026-01-01T00:00:00Z"
    for i in (0, 1, 2, 4))          # 3 is declared and never stamped
open("/tmp/stagecov/.task-pipeline/run.md", "w").write(led + "\n")
PY
cd /tmp/stagecov
if bash scripts/stage-coverage.sh; then
  echo "ERROR: a run missing a declared stage was accepted"
  exit 1
else
  echo "OK: the check refuses a ledger that does not account for stage 3"
fi
