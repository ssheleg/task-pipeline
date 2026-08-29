#!/usr/bin/env bash
# PreToolUse — editing the product before the plan is agreed.
#
# `stages.md` says no stage advances until its gate passes, and stage 5 is where
# code gets written. Editing the product during intake, docs, brainstorm, spec or
# plan is the pipeline's own discipline being skipped — and it is the skip nobody
# notices, because the work looks like progress.
#
# **`ask`, never `deny`, and the reason is this file's own doctrine.** The routing
# boundary says a typo, a one-line edit or a mechanical rename does not go through
# the pipeline, and no hook can tell a typo from a feature. A refusal here would
# fight the honest cases daily and be removed inside a week; a question answered
# once costs a keystroke.
#
# **The build stage is resolved by ROLE, never by number.** v1.50.0 matched
# `stage: 6` literally and blocked every release in a six-stage project; the same
# mistake here would put a prompt in front of every edit in any project whose flow
# is numbered differently. `pipeline.json` → a stage whose `state` is `build`, else
# one whose name says build. Unresolvable → silence, because a question nobody can
# act on is worse than none.
#
# **The pipeline's own artefacts are never gated.** Stages 0-4 exist to WRITE
# things — the brief, the spec, the plan, the ledger. A gate that asked about those
# would fire on the very work it is protecting.
set -uo pipefail

input=$(cat 2>/dev/null || true)
project="${CLAUDE_PROJECT_DIR:-$PWD}"
ledger="$project/.task-pipeline/run.md"
[ -f "$ledger" ] || exit 0

HOOK_INPUT="$input" python3 - "$ledger" "$project" <<'PY' 2>/dev/null || exit 0
import json, os, re, sys

ledger, project = sys.argv[1], sys.argv[2]
try:
    data = json.loads(os.environ.get("HOOK_INPUT", ""))
except Exception:
    raise SystemExit(0)

ti = data.get("tool_input") or {}
path = ti.get("file_path") or ti.get("notebook_path") or ""
if not path:
    raise SystemExit(0)

rel = os.path.relpath(path, project) if os.path.isabs(path) else path
rel = rel.replace(os.sep, "/")
# The run writes these; gating them would fire on the work stages 0-4 are for.
if rel.startswith("..") or re.match(r"^(docs/|\.task-pipeline/|\.claude/|CHANGELOG\.md|README\.md)", rel):
    raise SystemExit(0)

try:
    text = open(ledger, encoding="utf-8").read()
except Exception:
    raise SystemExit(0)

stage_lines = [l.strip() for l in text.splitlines() if l.strip().startswith("stage:")]
if not stage_lines:
    raise SystemExit(0)


def build_stage_id():
    """By role, never by number — the mistake v1.50.0 shipped in the release gate."""
    try:
        cfg = json.load(open(os.path.join(project, "pipeline.json"), encoding="utf-8"))
        for s in cfg.get("stages") or []:
            # `build` OR `dev` — mirroring this hook's own ledger fallback
            # (`build|dev`) below. Matching only `build` meant the shipped
            # pipeline.example.json, whose build stage is `state: "dev"`, never
            # armed this gate: the canonical config disarmed the hook it ships
            # beside.
            if isinstance(s, dict) and s.get("state") in ("build", "dev"):
                return str(s.get("id"))
    except Exception:
        pass
    for l in stage_lines:
        m = re.match(r"stage:\s*(\S+)\s+([^—]*)", l)
        if m and re.search(r"build|dev\b", m.group(2), re.I):
            return m.group(1)
    return None


build_id = build_stage_id()
if build_id is None:
    raise SystemExit(0)          # unresolvable: a question nobody can act on

# Has the run entered the build stage at all? Entering is enough — the gate is
# about editing BEFORE the plan is agreed, not about the build's own verdict.
entered = any(re.match(r"stage:\s*%s\b" % re.escape(build_id), l) for l in stage_lines)
if entered:
    raise SystemExit(0)

last = stage_lines[-1]
m = re.match(r"stage:\s*(\S+)\s+([^—]*)", last)
now = "%s %s" % (m.group(1), m.group(2).strip()) if m else "an early stage"

print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason":
        "This run is at stage %s and has not entered the build stage (%s). Editing "
        "the product before the plan is agreed is the pipeline's own discipline "
        "being skipped — and it is the skip nobody notices, because the work looks "
        "like progress.\n\n"
        "Allow if this is a typo, a one-line fix or a mechanical rename, which the "
        "routing boundary says never went through the pipeline anyway. Otherwise "
        "finish the plan and record stage %s in %s.\n\n"
        "The pipeline's own artefacts — docs/, .task-pipeline/, README, CHANGELOG — "
        "are never gated." % (now, build_id, build_id, ledger),
}}))
PY
exit 0
