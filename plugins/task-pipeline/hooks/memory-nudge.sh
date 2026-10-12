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
# .task-pipeline/memory.json carrying a hash of the Run: line's topic and date; the marker
# is honoured only while the ledger names that same run and still carries the marker's own
# ledger line, and a later `record --answer` clears it). Without that marker a
# machine with no Observatory paid about eleven nudges per run for one unchanging fact
# (CHANGELOG, Unreleased). The first nudge of a run also says where Observatory comes from, once.
#
# Silent everywhere else: no ledger means exit 0 after one file test.
set -uo pipefail
ledger="${CLAUDE_PROJECT_DIR:-$PWD}/.task-pipeline/run.md"
[ -f "$ledger" ] || exit 0
TP_SCRIPTS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../skills/task-pipeline/scripts" 2>/dev/null && pwd)" \
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
# The run key comes from stage_checkpoint.py's own helper — one definition of "this run" for
# the marker it writes and the pointer below. Unimportable: no key, so the marker is not
# honoured and the nudge behaves as before (never blocks).
try:
    sys.path.insert(0, os.environ["TP_SCRIPTS"])
    import pathlib
    from stage_checkpoint import run_key, marker_for_this_run
    this_run = run_key(lines)
except Exception:
    this_run = marker_for_this_run = None
try:
    state = json.load(open(os.path.join(here, "memory.json"), encoding="utf-8"))
    # Honoured only for the run that wrote it — same topic and start date, and its own
    # `unavailable for this run` line still in this ledger (a reseeded ledger has none).
    if marker_for_this_run and marker_for_this_run(pathlib.Path(ledger), state):
        sys.exit(0)
except (OSError, ValueError, AttributeError, TypeError):
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
run_id = this_run or hashlib.sha256(ledger.encode()).hexdigest()[:16]
pointer = os.path.join(here, ".memory-pointer")
try:
    shown = open(pointer).read().strip() == run_id
except OSError:
    shown = False
if not shown:
    msg += (" Observatory is the public engine passioncode-ai/project-observatory-dashboard "
            "(its README: Install, MCP).")
    try:
        open(pointer, "w").write(run_id + "\n")
    except OSError:
        pass
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}}))
PY
exit 0
