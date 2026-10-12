#!/usr/bin/env bash
# PostToolUse — a stage gate returned and no workflow-memory line follows it.
#
# The checkpoint doctrine (references/continuity.md, Part 3) asked every returned gate to
# write an Observatory checkpoint, or to record that memory is unavailable. It was a step
# the agent had to remember, and the measured adoption was one write in 293 sessions over
# fourteen days (sshlg-skills waves, 2026-10-11). This hook reminds at the moment it
# matters: once per stage line, as context the model reads, and never again for the same
# line. It decides nothing and blocks nothing.
#
# Silent everywhere else: no ledger means exit 0 after one file test.
set -uo pipefail
ledger="${CLAUDE_PROJECT_DIR:-$PWD}/.task-pipeline/run.md"
[ -f "$ledger" ] || exit 0
python3 - "$ledger" <<'PY' 2>/dev/null || true
import hashlib, json, os, re, sys
ledger = sys.argv[1]
try:
    lines = open(ledger, encoding="utf-8").read().splitlines()
except OSError:
    sys.exit(0)
last_stage = last_mem = -1
for i, l in enumerate(lines):
    if re.match(r"^stage:\s*\S+\s", l):
        last_stage = i
    elif l.startswith("event: memory"):
        last_mem = i
if last_stage < 0 or last_mem > last_stage:
    sys.exit(0)
line = lines[last_stage]
mark = os.path.join(os.path.dirname(ledger), ".memory-nudged")
key = hashlib.sha256(line.encode()).hexdigest()[:16]
try:
    if open(mark).read().strip() == key:
        sys.exit(0)
except OSError:
    pass
try:
    open(mark, "w").write(key + "\n")
except OSError:
    pass
sid = re.match(r"^stage:\s*(\S+)", line).group(1)
msg = (f"task-pipeline: stage {sid}'s gate returned and no workflow-memory line follows it. "
       "With Observatory's tools: `scripts/stage_checkpoint.py emit` → observatory_checkpoint_write "
       "→ `stage_checkpoint.py record --answer -`. Without them: "
       "`stage_checkpoint.py record --unavailable \"<why>\"`. (references/continuity.md, Part 3)")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}}))
PY
exit 0
