#!/usr/bin/env python3
"""FIX-PF-01.03 — recovery and the late worker: renew/cancel/recover/complete
check the current attempt and the monotonic fence (sherlock audit, PF-01).

The finding's remaining risk after PF-01.02: an expired attempt must be
replaceable, a LATE OLD result must be rejected, and a retried completion by
the current holder must be idempotent — none of which held without a fence
check on every lifecycle verb.

The fix under test (execution_authority.py + graph.py):
* recover() reclaims an expired/absent node for a new owner with a HIGHER
  fence, and refuses a still-live claim;
* complete() records completion only from the CURRENT fence-holder — a late
  worker with a stale fence is refused, and the current holder completing
  twice is idempotent;
* renew()/cancel() already fence-check (PF-01.02);
* graph.py exposes recover/complete as processes with the same guarantees.

Standard library only (sqlite3).
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline")
GRAPH = os.path.join(SKILL, "scripts", "graph.py")
EA = os.path.join(SKILL, "scripts", "execution_authority.py")

_spec = importlib.util.spec_from_file_location("execution_authority", EA)
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def fresh_db():
    return os.path.join(tempfile.mkdtemp(), "auth.db")


def t_expired_attempt_can_be_recovered():
    a = A.authority_for(fresh_db())
    g1 = a.claim("N-001", "sess-A", 0, now=1000.0, ttl_seconds=100)
    assert a.recover("N-001", "sess-B", 0, now=1050.0) is None, \
        "a still-live claim was recovered — a working node stolen"
    g2 = a.recover("N-001", "sess-B", 0, now=1200.0)  # after expiry
    assert g2 is not None and g2["owner"] == "sess-B", "an expired attempt could not be recovered"
    assert g2["fence"] > g1["fence"], "recovery did not mint a higher fence"
    a.close()


def t_late_old_result_is_rejected():
    a = A.authority_for(fresh_db())
    g1 = a.claim("N-001", "sess-A", 0, now=1000.0, ttl_seconds=100)
    old_fence = g1["fence"]
    g2 = a.recover("N-001", "sess-B", 0, now=1200.0)   # A's node reclaimed by B
    # A wakes up late and tries to complete with its OLD fence:
    assert a.complete("N-001", "sess-A", old_fence, now=1250.0) is None, \
        "a late old worker completed the node — overwriting the run that took over"
    # B (current) can complete
    assert a.complete("N-001", "sess-B", g2["fence"], now=1260.0) is not None, \
        "the current holder could not complete"
    a.close()


def t_retry_completion_is_idempotent():
    a = A.authority_for(fresh_db())
    g = a.claim("N-001", "sess-A", 0, now=1000.0)
    r1 = a.complete("N-001", "sess-A", g["fence"], now=1001.0)
    r2 = a.complete("N-001", "sess-A", g["fence"], now=1002.0)
    assert r1 is not None and r2 is not None, "a retried completion by the current holder failed"
    assert r1["state"] == "completed" and r2["state"] == "completed"
    a.close()


def t_cancel_and_renew_fence_checked():
    a = A.authority_for(fresh_db())
    g = a.claim("N-001", "sess-A", 0, now=1000.0)
    assert a.cancel("N-001", "sess-A", g["fence"] + 9) is False, "cancel ignored the fence"
    assert a.renew("N-001", "sess-A", g["fence"] + 9, now=1001.0) is None, "renew ignored the fence"
    assert a.cancel("N-001", "sess-A", g["fence"]) is True
    a.close()


# ---------------- graph.py as processes


def graph_env():
    d = tempfile.mkdtemp()
    g = {"goal": "ship", "requirements": ["REQ-001"],
         "nodes": [{"id": "N-001", "title": "t", "owner": "implementer",
                    "status": "pending", "serves": "REQ-001", "check": "true"}],
         "edges": []}
    gp = os.path.join(d, "graph.json")
    with open(gp, "w") as fh:
        json.dump(g, fh)
    return d, gp


def run_graph(*argv):
    return subprocess.run([sys.executable, GRAPH, *argv], capture_output=True, text=True, timeout=60)


def t_graph_complete_refuses_stale_fence():
    d, gp = graph_env()
    db = os.path.join(d, "auth.db")
    r1 = run_graph("claim", "--graph", gp, "--authority", db, "--owner", "sess-A", "--node", "N-001")
    fence = json.loads(r1.stdout)["fence"]
    # a stale fence completion is refused (exit 5)
    bad = run_graph("complete", "--graph", gp, "--authority", db, "--owner", "sess-A",
                    "--node", "N-001", "--fence", str(fence + 99))
    assert bad.returncode == 5, f"a stale-fence complete should be refused (5), got {bad.returncode}"
    ok = run_graph("complete", "--graph", gp, "--authority", db, "--owner", "sess-A",
                   "--node", "N-001", "--fence", str(fence))
    assert ok.returncode == 0, f"the current holder could not complete: {ok.stderr}"
    assert json.loads(ok.stdout)["state"] == "completed"


def main():
    case("an expired attempt can be recovered, a live one cannot",
         t_expired_attempt_can_be_recovered)
    case("a late old result is rejected; the current holder completes",
         t_late_old_result_is_rejected)
    case("a retried completion by the current holder is idempotent",
         t_retry_completion_is_idempotent)
    case("cancel and renew are fence-checked", t_cancel_and_renew_fence_checked)
    case("graph complete refuses a stale fence, accepts the current",
         t_graph_complete_refuses_stale_fence)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
