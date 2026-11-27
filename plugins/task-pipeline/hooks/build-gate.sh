#!/usr/bin/env bash
# PreToolUse: editing the product before its spec is judged, or before the plan is agreed.
#
# **`deny` when the run's spec does not verify (S0, the spec protocol, 2026-11-27).** The
# owner's rule: no product file is edited until a judge of another model family read the
# spec cold and found nothing a builder would have to ask. The current run's ledger names
# its spec (`spec: <dir>`); `spec_judge.py check --verify <dir>` must exit 0 (its verdict
# on file matches the content). No spec, or one that does not verify: `deny`, with the
# command that lifts it. A typo or a one-line fix is not exempt INSIDE a run (an incident
# gets an S spec, one page, one judge call); outside a run this hook says nothing at all.
# Runs started before 2026-11-28 with no `spec:` line keep the old question below, so an
# upgrade never strands a run in flight.
#
# **`ask` once the spec verifies but the run has not entered the build stage.** The routing
# boundary says a mechanical rename does not go through the pipeline, and no hook can tell
# one from a feature; with a judged spec the remaining risk is order, not content, and a
# question answered once costs a keystroke.
#
# **The build stage is resolved by ROLE, never by number.** v1.50.0 matched
# `stage: 6` literally and blocked every release in a six-stage project; the same
# mistake here would put a prompt in front of every edit in any project whose flow
# is numbered differently. `pipeline.json` -> a stage whose `state` is `build`, else
# one whose name says build. Unresolvable -> no question, because a question nobody can
# act on is worse than none.
#
# **The pipeline's own artefacts are never gated.** Stages 0-4 exist to WRITE
# things: the brief, the spec, the plan, the ledger. `docs/`, `.task-pipeline/`,
# `.claude/` and the root `*.md` files are never asked about or refused.
#
# **Fails silent.** A malformed payload or a crash of this script lets the edit through
# (the house rule: a hook never breaks another session); a spec that cannot be read is
# a refusal, because that is a finding about the spec, not about the hook.
set -uo pipefail

input=$(cat 2>/dev/null || true)
project="${CLAUDE_PROJECT_DIR:-$PWD}"
hook_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
ledger="$project/.task-pipeline/run.md"
if [ ! -f "$ledger" ]; then
  # `run-<slug>.md` ledgers (S0): the newest one is the current run.
  ledger=$(ls -t "$project"/.task-pipeline/run-*.md 2>/dev/null | head -1)
  [ -n "$ledger" ] && [ -f "$ledger" ] || exit 0
fi

HOOK_INPUT="$input" python3 - "$ledger" "$project" "$hook_dir" <<'PY' 2>/dev/null || exit 0
import json, os, re, subprocess, sys

ledger, project, hook_dir = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    data = json.loads(os.environ.get("HOOK_INPUT", ""))
except Exception:
    raise SystemExit(0)

ti = data.get("tool_input") if isinstance(data, dict) else None
if not isinstance(ti, dict):
    raise SystemExit(0)
if data.get("tool_name") == "apply_patch":
    # Codex edits through apply_patch, the patch text in `command` (hub B-211, CODEX-4):
    # every file it adds, updates, deletes or moves to is a path this gate decides.
    txt = ti.get("command") or ti.get("input") or ""
    if not isinstance(txt, str):
        raise SystemExit(0)
    paths = [a or b for a, b in re.findall(
        r"^\*\*\* (?:Add|Update|Delete) File: (.+)$|^\*\*\* Move to: (.+)$", txt, re.M)]
else:
    paths = [ti.get("file_path") or ti.get("notebook_path") or ""]


def gated(path):
    if not isinstance(path, str) or not path.strip():
        return False
    path = path.strip()
    rel = os.path.relpath(path, project) if os.path.isabs(path) else path
    rel = rel.replace(os.sep, "/")
    # The run writes these; gating them would fire on the work stages 0-4 are for.
    return not (rel.startswith("..") or re.match(
        r"^(docs/|\.task-pipeline/|\.claude/)", rel) or re.match(r"^[^/]+\.md$", rel))


# One gated path is enough: a patch that also touches docs/ still edits the product.
if not any(gated(p) for p in paths):
    raise SystemExit(0)

try:
    text = open(ledger, encoding="utf-8").read()
except Exception:
    raise SystemExit(0)

# Only the CURRENT run speaks: everything after the last `Run:` header. A previous
# run that entered dev in a reused, append-only ledger silenced this gate (B-151).
_lines = text.splitlines()
_starts = [i for i, l in enumerate(_lines) if l.strip().startswith("Run:")]
text = "\n".join(_lines[_starts[-1]:] if _starts else _lines)

stage_lines = [l.strip() for l in text.splitlines() if l.strip().startswith("stage:")]


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason}}))
    raise SystemExit(0)


# The spec gate (S0). `spec: <dir>` in the current run names the spec directory.
STRICT_FROM = "2026-11-28"
spec_m = re.search(r"^\s*spec:\s*`?([^`\s]+)`?\s*$", text, re.M)
started = re.search(r"started\s+`?(\d{4}-\d{2}-\d{2})", text)
strict = bool(started) and started.group(1) >= STRICT_FROM
if spec_m:
    spec_dir = spec_m.group(1)
    if not os.path.isabs(spec_dir):
        spec_dir = os.path.join(project, spec_dir)
    tool = os.path.join(os.path.dirname(hook_dir), "skills", "task-pipeline", "scripts", "spec_judge.py")
    if not os.path.isfile(tool):
        raise SystemExit(0)      # a broken install is not a finding about the spec
    try:
        r = subprocess.run([sys.executable, tool, "check", spec_dir, "--verify", "--project", project],
                           capture_output=True, text=True, timeout=15, cwd=project)
    except Exception:
        raise SystemExit(0)
    if r.returncode != 0:
        said = " ".join((r.stdout or "").strip().splitlines()[:3])[:600]
        deny("The run's spec does not verify, so no product file is edited yet: %s\n\n"
             "Judge it (`spec_judge.py check %s`), revise it until the judge passes it, or, "
             "after three rounds, take the open questions to the owning project's coordinator. "
             "The pipeline's own artefacts (docs/, .task-pipeline/, root *.md) stay open."
             % (said or "exit %d" % r.returncode, spec_m.group(1)))
elif strict:
    deny("This run (started %s) names no spec: no product file is edited until a spec "
         "describes the finished product and a judge of another model family passed it. "
         "Write it (`spec_judge.py init docs/specs/<date>-<slug> --id <id> --author-family "
         "<yours>`), judge it (`spec_judge.py check <dir>`), then record `spec: <dir>` in "
         "%s. An incident or a one-line fix gets an S spec: one page, one judge call."
         % (started.group(1), ledger))

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
        "The pipeline's own artefacts (docs/, .task-pipeline/, the root *.md files) "
        "are never gated." % (now, build_id, build_id, ledger),
}}))
PY
exit 0
