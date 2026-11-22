#!/usr/bin/env bash
# PreToolUse on the subagent tool: a task handed to an executor is read before it leaves.
#
# scripts/task_prompt.py answers four questions about a task that changes something: is the
# end result stated, is the finish criterion named, is there a closing pass that looks for
# what was missed, and does anything stop for approval between steps. Measured on 1968
# subagent prompts of three days across the estate (2026-11-22): 105 of 1058 working tasks
# asked for such a pass. A rule in a reference did not reach the moment a task is written,
# so this hook does.
#
# It decides nothing and blocks nothing: the dispatch goes out as written, and the note
# arrives with the subagent's result, where the orchestrator can still ask for the missing
# pass or run it. Unlike the other hooks here it works without a run ledger: tasks are
# handed to subagents in every project. `TASK_PROMPT_NUDGE=off` silences it. Any failure of
# its own is silent.
set -uo pipefail
[ "${TASK_PROMPT_NUDGE:-on}" = "off" ] && exit 0
here=${BASH_SOURCE[0]}
case "$here" in */*) here=${here%/*} ;; *) here=. ;; esac
TP_SCRIPTS="$here/../skills/task-pipeline/scripts"
[ -f "$TP_SCRIPTS/task_prompt.py" ] || exit 0
TP_SCRIPTS="$TP_SCRIPTS" python3 -c '
import json, os, sys
sys.dont_write_bytecode = True
try:
    payload = json.load(sys.stdin)
    inp = payload.get("tool_input") or {}
    prompt = inp.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        sys.exit(0)
    sys.path.insert(0, os.environ["TP_SCRIPTS"])
    import task_prompt
    res = task_prompt.check(prompt, hint=inp.get("subagent_type") or "")
    if res["ok"] or res["kind"] != "work":
        sys.exit(0)
    names = "; ".join("%s (%s)" % (task_prompt.QUESTIONS[q][0], task_prompt.QUESTIONS[q][1]) for q in res["fails"])
    msg = ("task-pipeline: the task just handed to a subagent is missing: " + names + ". It went out "
           "as written. When the result returns, cover the missing part yourself or ask for it, and "
           "write the next task whole (scripts/task_prompt.py check).")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": msg}}))
except Exception:
    pass
' 2>/dev/null || true
exit 0
