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
# Silent for the rest of a run that recorded memory unavailable FOR THE RUN
# (`stage_checkpoint.py record --unavailable "<why>" --for-run` writes a marker into
# .task-pipeline/memory.json carrying the run's `Run:` topic; the marker is honoured only
# while the ledger names that same run, and a later `record --answer` clears it). Without that marker a
# machine with no Observatory paid about eleven nudges per run for one unchanging fact
# (CHANGELOG, Unreleased). The first nudge of a run also says where Observatory comes from, once.
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
here = os.path.dirname(ledger)
topic = next((m.group(1) for m in (re.match(r"^Run:\s*`([^`]+)`", l) for l in lines) if m), None)
try:
    marker = (json.load(open(os.path.join(here, "memory.json"), encoding="utf-8")).get("memory") or {})
    gone = marker.get("unavailable") or {}
    # Honoured only for the run that wrote it: a marker from another `Run:` is stale.
    if gone and topic is not None and gone.get("run") == topic:
        sys.exit(0)
except (OSError, ValueError, AttributeError):
    pass  # no marker, or one that cannot be read: nudge as before, never block
line = lines[last_stage]
mark = os.path.join(here, ".memory-nudged")
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
       "→ `stage_checkpoint.py record --answer -`. Without them, once for the whole run: "
       "`stage_checkpoint.py record --unavailable \"<why>\" --for-run`. (references/continuity.md, Part 3)")
# Once per run, keyed by the ledger's `Run:` line: where the tools come from.
run_line = next((l for l in lines if l.startswith("Run:")), ledger)
run_key = hashlib.sha256(run_line.encode()).hexdigest()[:16]
pointer = os.path.join(here, ".memory-pointer")
try:
    shown = open(pointer).read().strip() == run_key
except OSError:
    shown = False
if not shown:
    msg += (" Observatory is the public engine passioncode-ai/project-observatory-dashboard "
            "(its README: Install, MCP).")
    try:
        open(pointer, "w").write(run_key + "\n")
    except OSError:
        pass
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}}))
PY
exit 0
