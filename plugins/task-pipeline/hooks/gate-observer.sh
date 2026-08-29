#!/usr/bin/env bash
# PostToolUse — record what the gate command actually did.
#
# `stage: 6 tests — gate manual — verdict pass` is typed by the agent. The stage-7
# release gate reads that line, so on its own it corroborates a claim with the same
# claim, made by the party it constrains. Nothing in the pipeline observed the
# suite; it observed a sentence about the suite.
#
# This appends the observation:
#
#     gate:  <stage id> — command "<cmd>" — exit <N> — <ISO-8601>
#
# and `release-gate.sh` then requires the claim and the observation to agree.
#
# **Only a command the project declared.** `pipeline.json` → the stage whose
# `gate.command` is set. Nothing is guessed from the shape of a command line: a
# heuristic over strings the environment also produces is `learned.md` rule 15,
# and a gate built on one would record `npm test` from a `README` example.
#
# **It records, it never judges.** A failing run is written down as a failing run.
# A hook that quietly declined to record a red result would be worse than no hook,
# because the absence would read as "the suite was never run".
#
# Silent everywhere else: no ledger, no declaration, no match — exit 0 having done
# nothing, so enabling this plugin changes nothing in a repository that is not
# running a pipeline.
set -uo pipefail

input=$(cat 2>/dev/null || true)
project="${CLAUDE_PROJECT_DIR:-$PWD}"
ledger="$project/.task-pipeline/run.md"
[ -f "$ledger" ] || exit 0

HOOK_INPUT="$input" python3 - "$ledger" "$project" <<'PY' 2>/dev/null || true
import json, os, re, sys, datetime

ledger, project = sys.argv[1], sys.argv[2]
try:
    data = json.loads(os.environ.get("HOOK_INPUT", ""))
except Exception:
    raise SystemExit(0)

cmd = ((data.get("tool_input") or {}).get("command") or "").strip()
if not cmd:
    raise SystemExit(0)

try:
    cfg = json.load(open(os.path.join(project, "pipeline.json"), encoding="utf-8"))
except Exception:
    raise SystemExit(0)

# EVERY stage that declares a command, not the first. A first-match scan meant
# a lint stage declared before the tests stage was the only one ever observed,
# so the real suite's runs left no trace for the release gate to corroborate —
# the same first-match break the release gate's own stage scan shipped with,
# fixed together (sweep the class, not the instance).
declared = [(str(s.get("id")), (s.get("gate") or {})["command"].strip())
            for s in cfg.get("stages") or []
            if isinstance(s, dict) and (s.get("gate") or {}).get("command")]
if not declared:
    raise SystemExit(0)

# Compared on the normalised command line, not on a substring: `echo "npm test"`
# and `npm test --watch` are not the project's gate, and treating them as one puts
# a fabricated observation in the ledger the release gate trusts.
def norm(s):
    return " ".join(s.split())

matches = [(sid, d) for sid, d in declared if norm(cmd) == norm(d)]
if not matches:
    raise SystemExit(0)

# PostToolUse fires on success; PostToolUseFailure carries the error. Both are
# wired to this script, and `error` present means the command did not exit 0.
failed = bool(data.get("error")) or data.get("hook_event_name") == "PostToolUseFailure"
out = data.get("tool_output") or {}
if isinstance(out, dict) and out.get("exit_code") is not None:
    code = int(out["exit_code"])
else:
    code = 1 if failed else 0

stamp = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

# Append-only, like every other line in this file. A ledger that is rewritten is a
# ledger whose history can be edited to say the suite passed. One line per stage
# that declared this exact command: two stages declaring the same command is two
# observations, because each stage's gate is corroborated separately.
with open(ledger, "a", encoding="utf-8") as fh:
    for stage_id, decl in matches:
        fh.write('gate:  %s — command "%s" — exit %d — %s\n' % (stage_id, norm(decl), code, stamp))
PY
exit 0
