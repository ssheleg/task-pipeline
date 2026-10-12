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
  * a credential is a name, never a value, and a malformed one is refused;
  * a `review:` line (the contact sheet's human rounds) travels in the checkpoint of the
    stage it names, so the number of passes is measured rather than remembered;
  * a planned handoff's retry keeps its key across ledger appends that are not memory
    events (`gate:`, `stage:`, `unavailable`), and a recorded offer moves it.

Run bare: prints PASS lines and exits non-zero on the first failure.
"""
import json
import os
import pathlib
import stat
import subprocess
import sys
import shutil
import tempfile
import atexit

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


_TREES = []
# Every tree this suite makes goes at exit — 134 `tp-stage-ckpt-*` were left in one
# machine's $TMPDIR by 2026-10-12 (hub waves R07).
atexit.register(lambda: [shutil.rmtree(t, ignore_errors=True) for t in _TREES])


def _tree():
    d = pathlib.Path(tempfile.mkdtemp(prefix="tp-stage-ckpt-"))
    _TREES.append(d)
    return d


def fresh():
    d = _tree()
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


def case_review_rounds():
    d = fresh()
    with (d / ".task-pipeline" / "run.md").open("a", encoding="utf-8") as f:
        f.write("review: 6 — surface landing — rounds 1 — returned — 2026-10-05T13:10Z\n")
    stage(d, 6, "Tests", "pass", "2026-10-05T13:30Z")
    with (d / ".task-pipeline" / "run.md").open("a", encoding="utf-8") as f:
        f.write("review: 10 — surface landing — rounds 2 — approved — 2026-10-05T15:00Z\n")
    stage(d, 10, "Acceptance", "pass", "2026-10-05T15:10Z")
    a = emit(d)
    done = {x["step_id"]: x for x in a["body"]["done"]}
    ok("review: landing rounds 1 returned" in done["stage-6"]["evidence"],
       "the stage that returned the sheet carries its review round")
    ok("review: landing rounds 2 approved" in done["stage-10"]["evidence"],
       "acceptance carries the rounds it took to approve, so passes are measured")
    ok(not [e for e in done["stage-6"]["evidence"] if "rounds 2" in e],
       "a review line belongs to the stage it names, not to every stage")
    print("PASS: review rounds travel in the checkpoint of the stage that recorded them")


def case_planned_handoff():
    """R11 (sshlg-skills waves): a planned executor change OFFERS the workflow."""
    d = fresh()
    stage(d, 0, "Intake grill", "pass", "2026-10-05T10:00Z")
    code, _, err = run(d, "handoff", "--to-provider", "openai")
    ok(code != 0 and "write a checkpoint first" in err, "no workflow, nothing to hand off")
    emit(d)
    record(d, {"workflowId": "wf_0123456789abcdef", "leaseId": TOKEN, "stepId": "stage-0",
               "checkpoint": {"revision": 1}})
    code, out, _ = run(d, "handoff", "--to-provider", "openai", "--to-model", "gpt-x",
                       "--reason", "limit")
    a = json.loads(out)
    ok(a["workflowId"] == "wf_0123456789abcdef" and a["leaseId"] == TOKEN and a["reason"] == "limit"
       and a["to"] == {"provider": "openai", "model": "gpt-x"}, "the offer carries the workflow and lease")
    ok(json.loads(run(d, "handoff", "--to-provider", "openai", "--to-model", "gpt-x",
                      "--reason", "limit")[1])["idempotencyKey"] == a["idempotencyKey"],
       "a retried offer repeats its key")
    ok(json.loads(run(d, "handoff", "--to-provider", "openai", "--to-model", "gpt-x",
                      "--reason", "limit", "--offer-ttl", "600")[1])["idempotencyKey"]
       != a["idempotencyKey"], "another offer TTL is another offer, not an idempotency conflict")
    code, out, _ = record(d, {"handoffId": "handoff:abc123"})
    ok(json.loads(run(d, "handoff", "--to-provider", "openai", "--to-model", "gpt-x",
                      "--reason", "limit")[1])["idempotencyKey"] != a["idempotencyKey"],
       "an offer made again after one was recorded is new, so a lapsed offer is not replayed")
    ok(code == 0 and "event: memory — handoff offered handoff:abc123" in ledger(d),
       "the offer is one ledger line")
    ok(json.loads(run(d, "state")[1])["holdsLease"] is True, "the lease stays until the successor accepts")
    code, out, _ = run(d, "accept", "--handoff-id", "handoff:abc123", "--session", "s-1")
    b = json.loads(out)
    ok(b["handoffId"] == "handoff:abc123" and b["sessionId"] == "s-1", "the successor's accept arguments")
    new = "lt_" + "z" * 40
    code, out, _ = record(d, {"leaseId": new, "checkpoint": {"workflowId": "wf_0123456789abcdef",
                                                               "revision": 2}, "stepId": "stage-0"})
    ok(code == 0 and new not in out and new not in ledger(d), "accepting prints and logs no token")
    print("PASS: a planned executor change offers the workflow, the successor accepts it")


def case_handoff_retry_ignores_unrelated_appends():
    """A retry of an unaccepted offer keeps its key across appends that are not memory
    events. The key used to carry the ledger's whole length, so a `gate:` line from
    `hooks/gate-observer.sh` or a `record --unavailable` line turned the retry into a NEW
    offer — and Observatory replaces an unaccepted older offer with a new one."""
    d = fresh()
    stage(d, 0, "Intake grill", "pass", "2026-10-05T10:00Z")
    emit(d)
    record(d, {"workflowId": "wf_0123456789abcdef", "leaseId": TOKEN, "stepId": "stage-0",
               "checkpoint": {"revision": 1}})
    offer = ("handoff", "--to-provider", "openai", "--reason", "limit")
    k1 = json.loads(run(d, *offer)[1])["idempotencyKey"]
    with (d / ".task-pipeline" / "run.md").open("a", encoding="utf-8") as f:
        f.write('gate:  6 — command "npm test" — exit 0 — 2026-10-05T10:05:00Z\n')
    ok(json.loads(run(d, *offer)[1])["idempotencyKey"] == k1,
       "a gate line appended between retries does not make the retry a new offer")
    code, _, _ = run(d, "record", "--unavailable", "observatory restarting")
    ok(code == 0 and json.loads(run(d, *offer)[1])["idempotencyKey"] == k1,
       "an `unavailable` memory line does not make the retry a new offer either")
    stage(d, 1, "Docs study", "pass", "2026-10-05T10:30Z")
    ok(json.loads(run(d, *offer)[1])["idempotencyKey"] == k1,
       "a stage line is not a memory event and does not move the key")
    record(d, {"handoffId": "handoff:first"})
    ok(json.loads(run(d, *offer)[1])["idempotencyKey"] != k1,
       "after a recorded offer, offering again is a new offer")
    print("PASS: an offer's retry survives unrelated ledger appends; a recorded offer moves the key")


def case_unavailable_for_the_run():
    """USR-008: one run-level marker instead of one line per gate; a later answer clears it."""
    d = fresh()
    stage(d, 0, "Intake grill", "pass", "2026-10-05T10:00Z")
    code, out, _ = run(d, "record", "--unavailable", "no Observatory on this machine", "--for-run")
    ok(code == 0, "--for-run is a state, not a failure")
    lines = [ln for ln in ledger(d).splitlines() if ln.startswith("event: memory")]
    ok(len(lines) == 1 and "unavailable for this run — no Observatory on this machine" in lines[0],
       "--for-run appends exactly one line, naming the run scope")
    st_path = d / ".task-pipeline" / "memory.json"
    st = json.loads(st_path.read_text())
    ok(st["memory"]["unavailable"]["reason"] == "no Observatory on this machine"
       and st["memory"]["unavailable"]["ledger_line"] == lines[0], "the marker names its reason and its line")
    ok(stat.S_IMODE(os.stat(st_path).st_mode) == 0o600, "the marker file is 0600")
    code, out, _ = run(d, "state")
    ok(json.loads(out)["memoryUnavailable"] == "no Observatory on this machine", "state reports the marker")
    stage(d, 1, "Docs study", "pass", "2026-10-05T11:00Z")
    a = emit(d, "--project", "project:alpha-web")
    code, _, _ = record(d, {"workflowId": "wf:1", "leaseId": TOKEN, "stepId": a["stepId"],
                            "checkpoint": {"revision": 1}})
    ok(code == 0 and "memory" not in json.loads(st_path.read_text()),
       "a later successful answer clears the marker: Observatory came back")
    code, out, _ = run(d, "state")
    ok(json.loads(out)["memoryUnavailable"] is None, "state no longer reports it")
    print("PASS: memory unavailable for the run is one marker and one line; an answer clears it")


def case_no_ledger():
    d = _tree()
    code, _, err = run(d, "emit")
    ok(code != 0 and "cannot be read" in err, "no ledger is refused, not invented")
    print("PASS: no ledger, no checkpoint")


if __name__ == "__main__":
    for case in (case_first_boundary, case_idempotency, case_continue_and_never_leak,
                 case_provider_loss, case_stale_writer_and_successor, case_credentials_by_name,
                 case_failed_gate_and_acceptance, case_review_rounds, case_planned_handoff,
                 case_handoff_retry_ignores_unrelated_appends, case_unavailable_for_the_run, case_no_ledger):
        case()
    print(f"PASS: stage_checkpoint.py — {CASES} cases")
