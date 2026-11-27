#!/usr/bin/env bash
# PreToolUse: editing the product before the plan is agreed, or against a spec the
# judge has not passed.
#
# `stages.md` says no stage advances until its gate passes, and stage 5 is where
# code gets written. Editing the product during intake, docs, brainstorm, spec or
# plan is the pipeline's own discipline being skipped, and it is the skip nobody
# notices, because the work looks like progress.
#
# **`deny` since the spec protocol S0 (owner, 27.11.2026: "no product file is
# edited until the spec is judged").** Until then this hook asked, because no hook
# can tell a typo from a feature. The question is replaced by a recorded escape:
# a line `exempt: <reason>` in the CURRENT run lets the honest typo, one-line edit
# or mechanical rename through, and the reason stays in the ledger where a
# reviewer reads it. A keystroke left no trace; the line does.
#
# **The judged spec.** When the current run names its spec (`spec: <dir>`), every
# product edit, inside the build stage too, needs `spec_judge.py check --verify`
# to exit 0: a verdict that permits building, bound to the spec's content hash.
# Exit 1 (verdict does not permit), 2 (no verdict, or the spec changed after it)
# and 3 (the tool could not run) all deny: fail-closed, because a gate that opens
# when its checker breaks is not a gate.
#
# **The build stage is resolved by ROLE, never by number.** v1.50.0 matched
# `stage: 6` literally and blocked every release in a six-stage project; the same
# mistake here would put a refusal in front of every edit in any project whose flow
# is numbered differently. `pipeline.json` -> a stage whose `state` is `build`, else
# one whose name says build. Unresolvable -> silence, because a refusal nobody can
# act on is worse than none.
#
# **The pipeline's own artefacts are never gated.** Stages 0-4 exist to WRITE
# things: the brief, the spec, the plan, the ledger. A gate that refused those
# would fire on the very work it is protecting.
set -uo pipefail

project="${CLAUDE_PROJECT_DIR:-$PWD}"
ledger="$project/.task-pipeline/run.md"
[ -f "$ledger" ] || exit 0
input=$(cat 2>/dev/null || true)
plugin_root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)}"
judge="$plugin_root/skills/task-pipeline/scripts/spec_judge.py"

HOOK_INPUT="$input" python3 - "$ledger" "$project" "$judge" <<'PY' 2>/dev/null || exit 0
import json, os, re, subprocess, sys

ledger, project, judge = sys.argv[1], sys.argv[2], sys.argv[3]
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
        r"^(docs/|\.task-pipeline/|\.claude/|CHANGELOG\.md|README\.md)", rel))


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

lines = [l.strip() for l in text.splitlines()]


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    raise SystemExit(0)


# The recorded escape: `exempt: <reason>` in the current run, reason non-empty.
if any(re.match(r"exempt:\s*\S", l) for l in lines):
    raise SystemExit(0)

ESCAPE = ("If this is a typo, a one-line fix or a mechanical rename, which the "
          "routing boundary says never went through the pipeline, record "
          "`exempt: <reason>` in %s and retry." % ledger)

# The judged spec: named by the current run, checked on every product edit.
spec_lines = [l for l in lines if re.match(r"spec:\s*\S", l)]
if spec_lines:
    ref = spec_lines[-1].split(":", 1)[1].strip().strip("`")
    sdir = ref if os.path.isabs(ref) else os.path.join(project, ref)
    if os.path.basename(sdir) == "spec.md":
        sdir = os.path.dirname(sdir)
    if not os.path.isfile(judge):
        deny("This run names its spec (%s), and the judge tool is missing (%s), so "
             "no verdict can be verified. No product file is edited until the spec "
             "is judged (spec protocol S0). %s" % (ref, judge, ESCAPE))
    try:
        r = subprocess.run([sys.executable, judge, "check", "--verify", sdir],
                           capture_output=True, text=True, timeout=60)
        code, said = r.returncode, (r.stdout or r.stderr or "").strip()[-600:]
    except Exception as e:
        code, said = 3, str(e)
    if code != 0:
        why = {1: "its verdict does not permit building (fail, pass-with-fixes, or "
                  "judged-degraded where cross-family judging is required)",
               2: "it has no verdict, or the spec changed after the verdict (the "
                  "content hash no longer matches)"}.get(
            code, "the judge tool could not run (exit %s); the gate fails closed" % code)
        deny("The spec this run names (%s) is not judged: %s. No product file is "
             "edited until the spec is judged (spec protocol S0). Fix: run "
             "`spec_judge.py check %s`, revise until the verdict is pass, then "
             "retry.\n\nThe tool said: %s\n\n%s" % (ref, why, ref, said, ESCAPE))

stage_lines = [l for l in lines if l.startswith("stage:")]
if not stage_lines:
    raise SystemExit(0)


def build_stage_id():
    """By role, never by number: the mistake v1.50.0 shipped in the release gate."""
    try:
        cfg = json.load(open(os.path.join(project, "pipeline.json"), encoding="utf-8"))
        for s in cfg.get("stages") or []:
            # `build` OR `dev`, mirroring this hook's own ledger fallback
            # (`build|dev`) below. Matching only `build` meant the shipped
            # pipeline.example.json, whose build stage is `state: "dev"`, never
            # armed this gate: the canonical config disarmed the hook it ships
            # beside.
            if isinstance(s, dict) and s.get("state") in ("build", "dev"):
                return str(s.get("id"))
    except Exception:
        pass
    for l in stage_lines:
        m = re.match(r"stage:\s*(\S+)\s+([^\u2014]*)", l)
        if m and re.search(r"build|dev\b", m.group(2), re.I):
            return m.group(1)
    return None


build_id = build_stage_id()
if build_id is None:
    raise SystemExit(0)          # unresolvable: a refusal nobody can act on

# Has the run entered the build stage at all? Entering is enough: the gate is
# about editing BEFORE the plan is agreed, not about the build's own verdict.
entered = any(re.match(r"stage:\s*%s\b" % re.escape(build_id), l) for l in stage_lines)
if entered:
    raise SystemExit(0)

last = stage_lines[-1]
m = re.match(r"stage:\s*(\S+)\s+([^\u2014]*)", last)
now = "%s %s" % (m.group(1), m.group(2).strip()) if m else "an early stage"

deny("This run is at stage %s and has not entered the build stage (%s). Editing "
     "the product before the plan is agreed and the spec is judged is the "
     "pipeline's own discipline being skipped (spec protocol S0: no product file "
     "is edited until the spec is judged). Finish the plan and record stage %s "
     "in %s.\n\n%s\n\nThe pipeline's own artefacts (docs/, .task-pipeline/, "
     "README, CHANGELOG) are never gated." % (now, build_id, build_id, ledger, ESCAPE))
PY
exit 0
