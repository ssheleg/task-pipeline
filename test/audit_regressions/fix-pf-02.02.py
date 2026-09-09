#!/usr/bin/env python3
"""FIX-PF-02.02 — a REQ/interface/brief change invalidates downstream proofs
(sherlock audit, PF-02).

After PF-02.01 bound a proof to the tree it tested, one gap remained: when an
upstream contract (a REQ, an interface, a brief) changed, descendants certified
against the OLD contract stayed `done` — certified against a tree that no longer
exists.

The fix under test (graph.py `invalidate`):
* records a superseding revision on the changed node;
* resets the node and every `done` DESCENDANT to pending, clearing evidence /
  proof / certification;
* leaves UNRELATED nodes' proofs untouched;
* refuses without a --why.

Standard library only.
"""
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GRAPH = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline",
                     "scripts", "graph.py")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def graph_with_chain():
    return {
        "goal": "ship", "requirements": ["REQ-1"],
        "nodes": [
            {"id": "N-001", "title": "contract", "owner": "implementer", "status": "done",
             "serves": "REQ-1", "check": "true", "evidence": ["e"], "proof": {"head": "h1"}},
            {"id": "N-002", "title": "mid", "owner": "implementer", "status": "done",
             "blocked_by": ["N-001"], "serves": "REQ-1", "check": "true",
             "evidence": ["e"], "proof": {"head": "h1"}},
            {"id": "N-003", "title": "leaf", "owner": "implementer", "status": "done",
             "blocked_by": ["N-002"], "serves": "REQ-1", "check": "true",
             "evidence": ["e"], "proof": {"head": "h1"}},
            {"id": "N-009", "title": "unrelated", "owner": "implementer", "status": "done",
             "serves": "REQ-1", "check": "true", "evidence": ["e"], "proof": {"head": "h1"}},
        ],
        "edges": [
            {"from": "N-001", "to": "N-002", "payload": "contract"},
            {"from": "N-002", "to": "N-003", "payload": "impl"},
        ],
    }


def write(g):
    d = tempfile.mkdtemp()
    gp = os.path.join(d, "graph.json")
    with open(gp, "w") as fh:
        json.dump(g, fh)
    return gp


def run(gp, *argv):
    return subprocess.run([sys.executable, GRAPH, *argv, "--graph", gp],
                          capture_output=True, text=True, timeout=60)


def nodes(gp):
    return {n["id"]: n for n in json.loads(open(gp).read())["nodes"]}


def t_upstream_change_invalidates_all_descendants():
    gp = write(graph_with_chain())
    r = run(gp, "invalidate", "--node", "N-001", "--why", "REQ-1 interface changed")
    assert r.returncode == 0, f"invalidate failed: {r.stderr}"
    ns = nodes(gp)
    for nid in ("N-001", "N-002", "N-003"):
        assert ns[nid]["status"] == "pending", f"{nid} left {ns[nid]['status']}, not reset"
        assert not ns[nid].get("proof"), f"{nid} kept a stale proof"
        assert not ns[nid].get("evidence"), f"{nid} kept stale evidence"


def t_unrelated_node_keeps_its_proof():
    gp = write(graph_with_chain())
    run(gp, "invalidate", "--node", "N-001", "--why", "REQ-1 interface changed")
    ns = nodes(gp)
    assert ns["N-009"]["status"] == "done", "an unrelated node was reset"
    assert ns["N-009"].get("proof") == {"head": "h1"}, "an unrelated node lost its proof"


def t_mid_change_spares_upstream():
    # invalidating N-002 must reset N-002 and N-003, but NOT its upstream N-001
    gp = write(graph_with_chain())
    run(gp, "invalidate", "--node", "N-002", "--why", "brief for N-002 changed")
    ns = nodes(gp)
    assert ns["N-001"]["status"] == "done" and ns["N-001"].get("proof"), \
        "invalidating a node reset its UPSTREAM — invalidation must flow downstream only"
    assert ns["N-002"]["status"] == "pending" and ns["N-003"]["status"] == "pending"


def t_records_a_superseding_revision():
    gp = write(graph_with_chain())
    run(gp, "invalidate", "--node", "N-001", "--why", "REQ-1 interface changed")
    revs = json.loads(open(gp).read()).get("revisions", [])
    inv = [x for x in revs if x["verb"] == "invalidate"]
    assert inv, "no superseding revision was recorded"
    assert inv[0]["why"] == "REQ-1 interface changed"
    assert "precondition" in inv[0], "the superseding revision carries no precondition"


def t_refuses_without_why():
    gp = write(graph_with_chain())
    r = run(gp, "invalidate", "--node", "N-001", "--why", "   ")
    assert r.returncode != 0, "invalidate ran with an empty reason"
    ns = nodes(gp)
    assert ns["N-001"]["status"] == "done", "the graph was mutated despite the refusal"


def main():
    case("an upstream change invalidates all descendants' proofs",
         t_upstream_change_invalidates_all_descendants)
    case("an unrelated node keeps its proof", t_unrelated_node_keeps_its_proof)
    case("invalidation flows downstream only, sparing upstream", t_mid_change_spares_upstream)
    case("a superseding revision is recorded with a precondition",
         t_records_a_superseding_revision)
    case("invalidate refuses without a reason", t_refuses_without_why)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
