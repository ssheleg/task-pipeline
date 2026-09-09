#!/usr/bin/env python3
"""FIX-PF-01.02 — the authority boundary: a durable coordinator hands out one
claim, `next` stays advisory, unavailable arbitration blocks dispatch
(sherlock audit, PF-01).

The finding: `graph.py next` is advisory — it prints the frontier — and two
independent runs both dispatched N-001. Who MAY run a node is a durable,
arbitrated decision, and there was no coordinator to make it.

The fix under test:
* execution_authority.py — a local SQLite coordinator; `BEGIN IMMEDIATE` makes
  ready→claimed atomic, so two concurrent claims yield ONE winner; a grant
  carries owner/attempt/revision/fence/expiry; an expired hold is reclaimable
  with a higher fence; a stale-fence renew/release is refused; opening a bad
  path is fail-closed (AuthorityUnavailable);
* graph.py `claim` (external mode) turns one runnable node into a claim and
  BLOCKS (exit 1, no work) when the authority is unavailable; `next` issues no
  claim and touches no authority; `release` needs a matching fence.

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


# ---------------- the coordinator, directly


def t_two_local_claims_one_winner():
    d = tempfile.mkdtemp()
    db = os.path.join(d, "auth.db")
    a, b = A.authority_for(db), A.authority_for(db)
    g1 = a.claim("N-001", "sess-A", 0, now=1000.0)
    g2 = b.claim("N-001", "sess-B", 0, now=1000.5)
    assert g1 is not None, "the first claim did not win"
    assert g2 is None, "two independent claims both won — the finding itself"
    a.close(); b.close()


def t_fence_is_monotonic_and_expiry_reclaims():
    d = tempfile.mkdtemp()
    db = os.path.join(d, "auth.db")
    a = A.authority_for(db)
    g1 = a.claim("N-001", "sess-A", 0, now=1000.0, ttl_seconds=100)
    g3 = a.claim("N-001", "sess-B", 0, now=1200.0)  # after expiry → reclaim
    assert g3 is not None and g3["fence"] > g1["fence"], "expiry did not reclaim with a higher fence"
    assert g3["attempt"] == g1["attempt"] + 1, "the reclaim did not increment the attempt"
    a.close()


def t_stale_fence_is_refused():
    d = tempfile.mkdtemp()
    db = os.path.join(d, "auth.db")
    a = A.authority_for(db)
    g = a.claim("N-001", "sess-A", 0, now=1000.0)
    assert a.renew("N-001", "sess-A", g["fence"] + 99, now=1001.0) is None, \
        "a stale fence renewed the lease — the zombie guard failed"
    assert a.release("N-001", "sess-A", g["fence"] + 99) is False, \
        "a stale fence released a live hold"
    assert a.release("N-001", "sess-A", g["fence"]) is True
    a.close()


def t_unavailable_is_fail_closed():
    try:
        A.authority_for(os.path.join("/no", "such", "dir", "a.db"))
        raise AssertionError("a bad path did not fail closed")
    except A.AuthorityUnavailable:
        pass
    try:
        A.authority_for("")
        raise AssertionError("an empty path did not fail closed")
    except A.AuthorityUnavailable:
        pass


# ---------------- graph.py external mode, as a process


def graph_env():
    d = tempfile.mkdtemp()
    g = {
        "goal": "ship", "requirements": ["REQ-001"],
        "nodes": [
            {"id": "N-001", "title": "t", "owner": "implementer", "status": "pending",
             "serves": "REQ-001", "check": "true"},
        ],
        "edges": [],
    }
    gp = os.path.join(d, "graph.json")
    with open(gp, "w") as fh:
        json.dump(g, fh)
    return d, gp


def run_graph(*argv):
    return subprocess.run([sys.executable, GRAPH, *argv],
                          capture_output=True, text=True, timeout=60)


def t_claim_wins_then_second_loses():
    d, gp = graph_env()
    db = os.path.join(d, "auth.db")
    r1 = run_graph("claim", "--graph", gp, "--authority", db, "--owner", "sess-A", "--node", "N-001")
    assert r1.returncode == 0, f"first claim did not win: {r1.stderr}"
    grant = json.loads(r1.stdout)
    assert grant["owner"] == "sess-A" and grant["state"] == "claimed"
    r2 = run_graph("claim", "--graph", gp, "--authority", db, "--owner", "sess-B", "--node", "N-001")
    assert r2.returncode == 5, f"second claim should lose (5), got {r2.returncode}: {r2.stderr}"
    assert "already claimed" in r2.stderr


def t_unavailable_authority_blocks_dispatch():
    d, gp = graph_env()
    bad = os.path.join(d, "missing-dir", "auth.db")
    r = run_graph("claim", "--graph", gp, "--authority", bad, "--owner", "sess-A", "--node", "N-001")
    assert r.returncode == 1, f"an unavailable authority should BLOCK (1), got {r.returncode}"
    assert "no work started" in r.stderr, "the block did not say no work started"


def t_next_is_advisory_no_claim():
    d, gp = graph_env()
    db = os.path.join(d, "auth.db")
    r = run_graph("next", "--graph", gp)
    assert r.returncode == 0 and "N-001" in r.stdout, "next did not print the frontier"
    # next must not have created any authority state
    assert not os.path.exists(db), "next issued an execution claim — it must stay advisory"
    # and a claim is still available afterwards
    r2 = run_graph("claim", "--graph", gp, "--authority", db, "--owner", "sess-A", "--node", "N-001")
    assert r2.returncode == 0, "next consumed the claim it was supposed to leave advisory"


def main():
    case("two independent local claims yield one winner", t_two_local_claims_one_winner)
    case("the fence is monotonic and expiry reclaims", t_fence_is_monotonic_and_expiry_reclaims)
    case("a stale fence is refused on renew and release", t_stale_fence_is_refused)
    case("an unavailable authority fails closed", t_unavailable_is_fail_closed)
    case("graph claim: first wins, second loses (5)", t_claim_wins_then_second_loses)
    case("an unavailable authority blocks dispatch (1, no work)",
         t_unavailable_authority_blocks_dispatch)
    case("next is advisory: it issues no claim", t_next_is_advisory_no_claim)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
