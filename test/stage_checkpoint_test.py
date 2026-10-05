#!/usr/bin/env python3
"""The stage-boundary checkpoint writer (`scripts/stage_checkpoint.py`) — stdlib only.

PB-137 N-024. The script builds the arguments of Observatory's checkpoint tool from the run
ledger and keeps the workflow's id and lease between boundaries. These cases drive it the
way a run does, with the tool's answers simulated in the exact shapes Observatory returns:

  * a gate that returns produces one checkpoint whose goal, done, open and step come from
    the ledger, and nothing else;
  * a retry of the same boundary repeats the same idempotency key, and a stage that runs
    again (a new line) is a new key;
  * a first answer is kept (workflowId, leaseId) in a 0600 file beside the ledger and the
    next boundary continues the workflow; the lease token never reaches the ledger or stdout;
  * provider loss is one ledger line and exit 0 — the run continues without memory;
  * a stale writer (`LeaseLost`) drops its token after the first refusal, and the next agent
    that took the workflow continues it;
  * a credential is a name, never a value, and a malformed one is refused.

Run bare: prints PASS lines and exits non-zero on the first failure.
"""
import json
import os
import pathlib
import stat
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SCRIPT = ROOT / "plugins" / "task-pipeline" / "skills" / "task-pipeline" / "scripts" / "stage_checkpoint.py"
TOKEN = "lt_" + "q" * 40
RUN_HEAD = "# Run ledger\n\nRun: `ship the invoice exporter` · started `2026-10-05` · module map: none\n\n## Log\n\n"
CASES = 0


def ok(cond, what):
    global CASES
    CASES += 1
    if not cond:
        print(f"FAIL: {what}")
        sys.exit(1)


def run(cwd, *args, stdin=None):
    r = subprocess.run([sys.executable, str(SCRIPT), *args], cwd=cwd, capture_output=True,
                       text=True, input=stdin, timeout=60)
    return r.returncode, r.stdout, r.stderr


def fresh():
    d = pathlib.Path(tempfile.mkdtemp(prefix="tp-stage-ckpt-"))
    (d / ".task-pipeline").mkdir()
    (d / ".task-pipeline" / "run.md").write_text(RUN_HEAD, encoding="utf-8")
    return d


def stage(d, sid, name, verdict, at):
    with (d / ".task-pipeline" / "run.md").open("a", encoding="utf-8") as f:
        f.write(f"stage: {sid} {name} — gate auto — verdict {verdict} — {at}\n")


def emit(d, *extra):
    code, out, err = run(d, "emit", *extra)
    ok(code == 0, f"emit exits 0 ({err.strip()})")
    return json.loads(out)


def record(d, answer):
    return run(d, "record", "--answer", "-", stdin=json.dumps(answer))


def ledger(d):
    return (d / ".task-pipeline" / "run.md").read_text(encoding="utf-8")


def case_first_boundary():
    d = fresh()
    stage(d, 0, "Intake grill", "pass", "2026-10-05T10:00Z")
    a = emit(d, "--project", "project:alpha-web", "--constraint", "read-only: do not push")
    ok(a["owner"] == "agent:task-pipeline", "the writer names itself")
    ok(a["stepId"] == "stage-0" and a["status"] == "done", "the step is the gate that returned")
    ok(a["projectId"] == "project:alpha-web" and "workflowId" not in a, "the first write starts a workflow")
    ok(a["body"]["goal"] == "ship the invoice exporter", "the goal is the run's topic")
    ok(a["body"]["open"][0]["step_id"] == "stage-1" and "Docs study" in a["body"]["open"][0]["next_action"],
       "open names the next stage by its canonical name")
    ok(a["body"]["constraints"] == ["read-only: do not push"], "constraints come from the operator")
    ok(a["close"] is False, "only acceptance closes the workflow")
    print("PASS: a returned gate becomes one checkpoint built from the ledger")


def case_idempotency():
    d = fresh()
    stage(d, 0, "Intake grill", "pass", "2026-10-05T10:00Z")
    k1 = emit(d)["idempotencyKey"]
    ok(emit(d)["idempotencyKey"] == k1, "a retry of the same boundary repeats its key")
    stage(d, 0, "Intake grill", "pass", "2026-10-05T11:00Z")
    ok(emit(d)["idempotencyKey"] != k1, "a stage that runs again is a new checkpoint")
    print("PASS: retries replay, repeated stages are new")


def case_continue_and_never_leak():
    d = fresh()
    stage(d, 0, "Intake grill", "pass", "2026-10-05T10:00Z")
    emit(d, "--constraint", "read-only: do not push")
    code, out, _ = record(d, {"workflowId": "wf_0123456789abcdef", "leaseId": TOKEN,
                              "stepId": "stage-0", "checkpoint": {"revision": 1}})
    ok(code == 0 and TOKEN not in out, "recording prints no token")
    state = d / ".task-pipeline" / "memory.json"
    ok(stat.S_IMODE(state.stat().st_mode) == 0o600, "the lease lives in a 0600 file")
    ok("memory.json" in (d / ".task-pipeline" / ".gitignore").read_text(), "and it is git-ignored")
    ok(TOKEN not in ledger(d) and "event: memory — checkpoint stage-0 rev 1 wf_0123456789abcdef" in ledger(d),
       "the ledger names the checkpoint and never the token")
    stage(d, 1, "Docs study", "pass", "2026-10-05T10:30Z")
    a = emit(d)
    ok(a.get("workflowId") == "wf_0123456789abcdef" and a.get("leaseId") == TOKEN and "projectId" not in a,
       "the next boundary continues the workflow with its lease")
    ok([x["step_id"] for x in a["body"]["done"]] == ["stage-0", "stage-1"], "done grows with the ledger")
    ok(a["body"]["constraints"] == ["read-only: do not push"],
       "constraints stated at the first boundary travel to every later one")
    code, out, _ = run(d, "state")
    ok(TOKEN not in out and json.loads(out)["holdsLease"] is True, "state never prints the token")
    print("PASS: the workflow continues across boundaries; the token stays out of every output")


def case_provider_loss():
    d = fresh()
    stage(d, 0, "Intake grill", "pass", "2026-10-05T10:00Z")
    code, out, _ = run(d, "record", "--unavailable", "observatory tools are not connected")
    ok(code == 0, "unavailable memory is a state, not a failure")
    ok("event: memory — unavailable — observatory tools are not connected" in ledger(d), "and it is said")
    print("PASS: provider loss is one ledger line and the run goes on")


def case_stale_writer_and_successor():
    d = fresh()
    stage(d, 0, "Intake grill", "pass", "2026-10-05T10:00Z")
    record(d, {"workflowId": "wf_0123456789abcdef", "leaseId": TOKEN, "stepId": "stage-0"})
    stage(d, 1, "Docs study", "pass", "2026-10-05T10:30Z")
    code, _, _ = record(d, {"error": "LeaseLost", "detail": "another executor holds it",
                            "keptAs": "mem:abcdef0123456789"})
    ok(code == 0 and "refused LeaseLost (kept as mem:abcdef0123456789)" in ledger(d), "the refusal is recorded")
    a = emit(d)
    ok("leaseId" not in a, "a stale writer does not write with a lost token again")
    st = json.loads(run(d, "state")[1])
    ok(st["stale"] == "LeaseLost" and st["holdsLease"] is False, "state says the run must read before writing")
    # The successor accepted the handoff in another session and records its answer here.
    record(d, {"workflowId": "wf_0123456789abcdef", "leaseId": "lt_" + "s" * 40, "stepId": "stage-1"})
    a = emit(d)
    ok(a.get("leaseId") == "lt_" + "s" * 40, "the next agent continues the workflow with its own lease")
    print("PASS: a stale writer stops after one refusal; the successor continues")


def case_credentials_by_name():
    d = fresh()
    stage(d, 4, "Plan", "pass", "2026-10-05T12:00Z")
    a = emit(d, "--credential", "alpha-web/prod/STRIPE_KEY")
    ok(a["body"]["credentials"] == [{"project": "alpha-web", "env": "prod", "name": "STRIPE_KEY"}],
       "a credential is a name")
    code, _, err = run(d, "emit", "--credential", "sk_live_value")
    ok(code != 0 and "never a value" in err, "a bare value is refused")
    print("PASS: credentials travel by name only")


def case_failed_gate_and_acceptance():
    d = fresh()
    stage(d, 6, "Tests", "fail", "2026-10-05T13:00Z")
    a = emit(d)
    ok(a["status"] == "blocked" and a["body"]["open"][0]["step_id"] == "stage-6", "a failed gate stays open")
    stage(d, 10, "Acceptance", "pass", "2026-10-05T15:00Z")
    a = emit(d)
    ok(a["close"] is True and a["body"]["open"] == [], "acceptance closes the workflow")
    print("PASS: a failed gate stays open; acceptance closes")


def case_no_ledger():
    d = pathlib.Path(tempfile.mkdtemp(prefix="tp-stage-ckpt-"))
    code, _, err = run(d, "emit")
    ok(code != 0 and "cannot be read" in err, "no ledger is refused, not invented")
    print("PASS: no ledger, no checkpoint")


if __name__ == "__main__":
    for case in (case_first_boundary, case_idempotency, case_continue_and_never_leak,
                 case_provider_loss, case_stale_writer_and_successor, case_credentials_by_name,
                 case_failed_gate_and_acceptance, case_no_ledger):
        case()
    print(f"PASS: stage_checkpoint.py — {CASES} cases")
