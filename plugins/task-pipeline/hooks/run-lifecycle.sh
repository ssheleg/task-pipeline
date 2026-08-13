#!/usr/bin/env bash
# PreCompact · SessionEnd · SubagentStop — the three moments the run's own record
# cannot see, written down as they happen.
#
# One line shape for all three:
#
#     event: <kind> — <detail> — <ISO-8601>
#
# **Why one shape and not three.** A ledger grammar is read by four documents and
# two hooks; every shape added is a shape each of them must learn. These three are
# the same kind of fact — something happened to the RUN rather than to a stage —
# and a `kind` field costs one word against three grammars.
#
# WHAT EACH ONE IS FOR
#
#   compact      — the ledger exists because compaction happens; `templates/run.md`
#                  says so in its own header. Until now the boundary itself was the
#                  one event the file could not show, so a resumed run could not
#                  tell "the context was compacted here" from "nothing happened".
#   session-end  — a run whose session ended without reaching acceptance is
#                  ABANDONED, and abandoned runs are exactly what
#                  `/task-pipeline checkup` exists to surface. Before this they
#                  were invisible: the ledger simply stopped, which looks identical
#                  to a run still in progress.
#   subagent     — stage 5 dispatches implementers as subagents, and the `hand:`
#                  line counts them. Both sides of that count are written by the
#                  same agent from the same memory, so the audit comparing them
#                  compares a number with itself.
#
# **It does NOT write `hand:` lines, and that is not a shortcut.** That shape
# carries `done`, `surfaced`, `decisions` and `amb` — judgements only the agent
# holds. A hook filling them in would be fabricating the very evidence the line
# exists to provide. So it records what it can actually see (a subagent of this
# type stopped) and leaves the accounting to whoever can account.
#
# Silent with no ledger, and never blocking: none of these events should ever cost
# a session. `SessionEnd` hooks share a 1.5-second budget, so this appends one line
# and exits.
set -uo pipefail

input=$(cat 2>/dev/null || true)
project="${CLAUDE_PROJECT_DIR:-$PWD}"
ledger="$project/.task-pipeline/run.md"
[ -f "$ledger" ] || exit 0

HOOK_INPUT="$input" python3 - "$ledger" <<'PY' 2>/dev/null || true
import json, os, sys, datetime, re

ledger = sys.argv[1]
try:
    data = json.loads(os.environ.get("HOOK_INPUT", ""))
except Exception:
    raise SystemExit(0)

event = data.get("hook_event_name")


def clean(text, limit=90):
    """One line, no separators that would break the ledger's own grammar."""
    s = re.sub(r"\s+", " ", str(text or "")).replace("—", "-").strip()
    return s[:limit]


if event == "PreCompact":
    kind, detail = "compact", clean(data.get("trigger") or "unknown")
elif event == "SessionEnd":
    # A run that reached acceptance is finished, not abandoned. Recording an end
    # for it would fill `checkup` with runs that closed exactly as intended.
    try:
        text = open(ledger, encoding="utf-8").read()
    except Exception:
        raise SystemExit(0)
    stages = [l.strip() for l in text.splitlines() if l.strip().startswith("stage:")]
    closed = any(re.search(r"verdict\s+pass", l) and re.search(r"accept", l, re.I) for l in stages)
    if closed:
        raise SystemExit(0)
    kind = "session-end"
    detail = "%s - run not closed, no acceptance recorded" % clean(data.get("reason") or "other", 40)
elif event == "SubagentStop":
    kind = "subagent"
    detail = clean(data.get("agent_type") or "unknown", 40)
else:
    raise SystemExit(0)

stamp = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
with open(ledger, "a", encoding="utf-8") as fh:
    fh.write('event: %s — %s — %s\n' % (kind, detail, stamp))
PY
exit 0
