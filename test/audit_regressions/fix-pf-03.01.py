#!/usr/bin/env python3
"""FIX-PF-03.01 — the completion gate lives in the store mutation
(sherlock audit, PF-03).

The finding, reproduced by the audit: certify recorded unit=fail and exited 1;
a DIRECT close with a structurally valid verdict then returned 0 and marked
the node done. close checked the verdict's shape and blockers, never whether a
certification of the current candidate succeeded.

The fix under test (graph.py cmd_close):
* a node whose certification has a failing tier cannot be closed — the direct
  close is refused with the tiers named;
* a certification earned at a DIFFERENT candidate (another commit) is refused;
* a successful certification at the current head closes normally;
* a node with NO certification record closes as before (the verifier's
  judgement), so the gate adds no new confirmation where certify never ran.

Standard library only (git via subprocess).
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


def git(d, *a):
    return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True)


def repo(certification=None):
    d = tempfile.mkdtemp()
    git(d, "init", "-q"); git(d, "config", "user.email", "t@t"); git(d, "config", "user.name", "t")
    with open(os.path.join(d, "code.txt"), "w") as fh:
        fh.write("v1\n")
    git(d, "add", "-A"); git(d, "commit", "-qm", "v1")
    head = git(d, "rev-parse", "HEAD").stdout.strip()
    node = {"id": "N-001", "title": "t", "owner": "implementer", "status": "pending",
            "serves": "REQ-001", "check": "true"}
    if certification is not None:
        cert = dict(certification)
        if cert.get("at") == "<HEAD>":
            cert["at"] = head
        node["certification"] = cert
    g = {"goal": "ship", "requirements": ["REQ-001"], "nodes": [node], "edges": []}
    gp = os.path.join(d, "graph.json")
    with open(gp, "w") as fh:
        json.dump(g, fh)
    return d, gp, head


def close(d, gp, head):
    v = {"node": "N-001", "done": ["built"], "not_done": [], "not_verified": [],
         "blockers": [], "replan": {"possible": True, "add": [], "park": [], "why": ""},
         "evidence": ["npm test → PASS"], "tested": {"head": head}}
    vp = os.path.join(d, "verdict.json")
    with open(vp, "w") as fh:
        json.dump(v, fh)
    return subprocess.run([sys.executable, GRAPH, "close", "--graph", gp, "--verdict", vp],
                          capture_output=True, text=True, cwd=d)


def status(gp):
    return json.loads(open(gp).read())["nodes"][0]["status"]


def t_failed_certification_blocks_direct_close():
    d, gp, head = repo({"round": 1, "at": "<HEAD>",
                        "tiers": {"unit": "fail", "seam": "pass", "product": "pass"},
                        "history": []})
    r = close(d, gp, head)
    assert r.returncode != 0, "a direct close stepped around a FAILED certification — the finding"
    assert "failing tier(s): unit" in r.stderr, r.stderr
    assert status(gp) == "pending", "the node was closed anyway"


def t_stale_candidate_certification_blocks():
    d, gp, head = repo({"round": 1, "at": "0" * 40,
                        "tiers": {"unit": "pass", "seam": "pass", "product": "pass"},
                        "history": []})
    r = close(d, gp, head)
    assert r.returncode != 0, "a certification of another candidate was accepted"
    assert "different candidate" in r.stderr, r.stderr


def t_current_successful_certification_closes():
    d, gp, head = repo({"round": 1, "at": "<HEAD>",
                        "tiers": {"unit": "pass", "seam": "pass", "product": "pass"},
                        "history": []})
    r = close(d, gp, head)
    assert r.returncode == 0, f"a current successful certification was refused: {r.stderr}"
    assert status(gp) == "done"


def t_no_certification_closes_as_before():
    d, gp, head = repo(None)
    r = close(d, gp, head)
    assert r.returncode == 0, f"a node certify never touched was refused: {r.stderr}"
    assert status(gp) == "done"


def main():
    case("a failed certification blocks a direct close",
         t_failed_certification_blocks_direct_close)
    case("a certification of another candidate blocks",
         t_stale_candidate_certification_blocks)
    case("a current successful certification closes normally",
         t_current_successful_certification_closes)
    case("a node with no certification closes as before",
         t_no_certification_closes_as_before)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
