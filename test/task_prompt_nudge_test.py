#!/usr/bin/env python3
"""task-prompt-nudge.sh: the real hook as a process. It notes a working task that is
missing a part, stays silent otherwise, never blocks and never fails."""
import json
import os
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parent.parent
HOOK = ROOT / "plugins" / "task-pipeline" / "hooks" / "task-prompt-nudge.sh"
CASES = 0
WHOLE = ("Goal: the export returns CSV. Fix src/export/csv.py. Done when pytest passes. "
         "Then a second pass over every caller for what was missed; list what you did not examine. "
         "Report the commits.")


def ok(cond, what):
    global CASES
    CASES += 1
    if not cond:
        print(f"FAIL: {what}")
        sys.exit(1)


def hook(stdin, env=None):
    r = subprocess.run(["bash", str(HOOK)], input=stdin, capture_output=True, text=True,
                       env=dict(os.environ, **(env or {})), timeout=30)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def payload(prompt, agent="general-purpose"):
    return json.dumps({"tool_name": "Agent", "tool_input": {"prompt": prompt, "subagent_type": agent}})


code, out, err = hook(payload(WHOLE.replace("Then a second pass over every caller for what was missed; list what you did not examine. ", "")))
ok(code == 0 and out, "a working task without a closing pass gets a note")
note = json.loads(out)["hookSpecificOutput"]
ok(note["hookEventName"] == "PreToolUse" and "sweep" in note["additionalContext"], "the note names the missing part")
ok("permissionDecision" not in note, "the note never decides the call")
code, out, err = hook(payload(WHOLE))
ok(code == 0 and out == "", "a whole task is silent")
code, out, err = hook(payload("Find where the limit is read. Return a table of readers.", "Explore"))
ok(code == 0 and out == "", "a lookup is silent")
code, out, err = hook(payload("Fix the export."), {"TASK_PROMPT_NUDGE": "off"})
ok(code == 0 and out == "", "the switch silences it")
for bad in ("garbage", "", json.dumps({"tool_input": {"prompt": 7}}), json.dumps({"tool_input": None})):
    code, out, err = hook(bad)
    ok(code == 0 and out == "" and err == "", "a malformed payload is silent: %r" % bad[:20])
hooks = json.loads((ROOT / "plugins/task-pipeline/hooks/hooks.json").read_text())
wired = [h for e in hooks["hooks"]["PreToolUse"] if "Agent" in e["matcher"] for h in e["hooks"]]
ok(wired and "task-prompt-nudge.sh" in wired[0]["command"], "hooks.json runs it before the subagent tool")
print(f"PASS: task-prompt-nudge.sh — {CASES} cases")
