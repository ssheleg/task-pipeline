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
    # A profile's stage ids need not be numbers (the hub's run ledger takes any \S+ id).
    s = project(HEAD + "stage: spec Spec — gate manual — verdict pass — 2026-10-12T12:00Z\n")
    ok("stage spec" in hook(s), "a non-numeric stage id is reminded too")
    # A run that recorded memory unavailable FOR THE RUN is not nudged again.
    ck = ROOT / "plugins" / "task-pipeline" / "skills" / "task-pipeline" / "scripts" / "stage_checkpoint.py"
    r = project(HEAD + STAGE)
    first = json.loads(hook(r))["hookSpecificOutput"]["additionalContext"]
    ok("project-observatory-dashboard" in first, "the first nudge of a run says where Observatory comes from")
    ok("--for-run" in first, "the nudge names the run-level answer")
    subprocess.run([sys.executable, str(ck), "record", "--unavailable", "no Observatory here", "--for-run"],
                   cwd=r, check=True, capture_output=True)
    for n in (4, 5, 6):
        with (r / ".task-pipeline" / "run.md").open("a", encoding="utf-8") as f:
            f.write(f"stage: {n} S — gate auto — verdict pass — 2026-10-12T1{n}:00Z\n")
        ok(hook(r) == "", f"after record --unavailable --for-run, stage {n} is not nudged")
    subprocess.run([sys.executable, str(ck), "record", "--answer", "-"], cwd=r, check=True,
                   capture_output=True, text=True,
                   input=json.dumps({"workflowId": "wf:1", "stepId": "stage-6", "checkpoint": {"revision": 1}}))
    with (r / ".task-pipeline" / "run.md").open("a", encoding="utf-8") as f:
        f.write("stage: 7 S — gate auto — verdict pass — 2026-10-12T17:00Z\n")
    again = json.loads(hook(r))["hookSpecificOutput"]["additionalContext"]
    ok("stage 7" in again, "a later answer clears the marker and the next gate is nudged")
    ok("project-observatory-dashboard" not in again, "the install pointer is printed once per run")
    (r / ".task-pipeline" / "memory.json").write_text("{not json", encoding="utf-8")
    with (r / ".task-pipeline" / "run.md").open("a", encoding="utf-8") as f:
        f.write("stage: 8 S — gate auto — verdict pass — 2026-10-12T18:00Z\n")
    ok("stage 8" in hook(r), "an unreadable marker file nudges as before, never blocks")
    # The marker belongs to the run that wrote it: a new run (another `Run:` line) is nudged,
    # with the Observatory pointer, even when an old marker is still on disk.
    m = project(HEAD.replace("Run: `x`", "Run: `run-a`") + STAGE)
    hook(m)
    subprocess.run([sys.executable, str(ck), "record", "--unavailable", "no Observatory", "--for-run"],
                   cwd=m, check=True, capture_output=True)
    (m / ".task-pipeline" / "run.md").write_text(
        HEAD.replace("Run: `x`", "Run: `run-b`") + STAGE.replace("stage: 3", "stage: 1"), encoding="utf-8")
    fresh_run = hook(m)
    ok(fresh_run != "" and "stage 1" in fresh_run and "project-observatory-dashboard" in fresh_run,
       "a marker written under Run a does not silence Run b: nudged, with the pointer")
    print(f"PASS: memory-nudge.sh — {CASES} cases")


if __name__ == "__main__":
    main()
