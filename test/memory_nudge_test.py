#!/usr/bin/env python3
"""memory-nudge.sh — a returned gate with no workflow-memory line is reminded once (R11).

Runs the real hook as a process against a temp project. Every tree goes at exit.
"""
import atexit
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parent.parent
HOOK = ROOT / "plugins" / "task-pipeline" / "hooks" / "memory-nudge.sh"
_TREES = []
atexit.register(lambda: [shutil.rmtree(t, ignore_errors=True) for t in _TREES])
CASES = 0


def ok(cond, what):
    global CASES
    CASES += 1
    if not cond:
        print(f"FAIL: {what}")
        sys.exit(1)


def project(ledger_text=None):
    d = pathlib.Path(tempfile.mkdtemp(prefix="tp-nudge-"))
    _TREES.append(d)
    if ledger_text is not None:
        (d / ".task-pipeline").mkdir()
        (d / ".task-pipeline" / "run.md").write_text(ledger_text, encoding="utf-8")
    return d


def hook(d):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(d))
    r = subprocess.run(["bash", str(HOOK)], input='{"tool_name":"Bash"}', env=env,
                       capture_output=True, text=True, timeout=60)
    ok(r.returncode == 0, f"the hook never blocks (exit {r.returncode})")
    return r.stdout.strip()


HEAD = "# Run ledger\n\nRun: `x` · started `2026-10-12`\n\n## Log\n\n"
STAGE = "stage: 3 Spec — gate manual — verdict pass — 2026-10-12T10:00Z\n"


def main():
    ok(hook(project()) == "", "no ledger: silent")
    ok(hook(project(HEAD)) == "", "no stage line yet: silent")
    d = project(HEAD + STAGE)
    out = hook(d)
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    ok("stage 3" in ctx and "stage_checkpoint.py" in ctx, "a returned gate without memory is reminded")
    ok(hook(d) == "", "once per stage line, never again for the same line")
    (d / ".task-pipeline" / "run.md").write_text(
        HEAD + STAGE + "event: memory — unavailable — no tools — 2026-10-12T10:01Z\n", encoding="utf-8")
    ok(hook(d) == "", "a memory line after the stage: silent")
    with (d / ".task-pipeline" / "run.md").open("a", encoding="utf-8") as f:
        f.write("stage: 4 Plan — gate manual — verdict pass — 2026-10-12T11:00Z\n")
    ok("stage 4" in hook(d), "the next returned gate is reminded")
    print(f"PASS: memory-nudge.sh — {CASES} cases")


if __name__ == "__main__":
    main()
