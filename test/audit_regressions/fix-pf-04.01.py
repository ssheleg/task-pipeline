#!/usr/bin/env python3
"""FIX-PF-04.01 — the dependency-satisfaction predicate is separate from
terminal status: a park does not produce (sherlock audit, PF-04).

The finding, reproduced in scratch: TERMINAL={done,parked}, and frontier /
close / certify all treated a PARKED node as a satisfied dependency — parking
N-001 ("producer unavailable") made its consumer N-002 runnable WITHOUT the
required artifact.

The fix under test (graph.py + work-graph.md):
* a blocker satisfies only when `done`; a parked producer BLOCKS its consumer
  in the frontier, blocks its close, blocks its certification;
* `next` names each held consumer with the park's reason;
* the alternative-producer path is an explicit edge change (the doc says so);
* the graph's own lifecycle semantics survive: all-done-or-parked still exits
  3, a parked node still refuses a second park/close.

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
DOC = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline",
                   "references", "work-graph.md")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def write_graph(producer_status):
    d = tempfile.mkdtemp()
    g = {"goal": "ship", "requirements": ["REQ-001"],
         "nodes": [
             {"id": "N-001", "title": "producer", "owner": "implementer",
              "status": producer_status, "serves": "REQ-001", "check": "true",
              **({"parked_reason": "producer unavailable"} if producer_status == "parked" else {}),
              **({"evidence": ["made artifact-v1"]} if producer_status == "done" else {})},
             {"id": "N-002", "title": "consumer", "owner": "implementer",
              "status": "pending", "blocked_by": ["N-001"], "serves": "REQ-001",
              "check": "true"},
         ],
         "edges": [{"from": "N-001", "to": "N-002", "payload": "artifact-v1"}]}
    gp = os.path.join(d, "graph.json")
    json.dump(g, open(gp, "w"))
    return d, gp


def run(gp, *argv):
    return subprocess.run([sys.executable, GRAPH, *argv, "--graph", gp],
                          capture_output=True, text=True, timeout=60)


def t_parked_producer_blocks_the_frontier():
    d, gp = write_graph("parked")
    r = run(gp, "next")
    assert "N-002" not in r.stdout, \
        "a consumer became runnable off a PARKED producer — the finding itself"
    assert "held:" in r.stderr and "producer unavailable" in r.stderr, \
        f"the held consumer is not named with the park's reason:\n{r.stderr}"


def t_done_producer_unblocks():
    d, gp = write_graph("done")
    r = run(gp, "next")
    assert "N-002" in r.stdout, "a done producer no longer unblocks its consumer"


def t_close_refuses_over_a_parked_blocker():
    d, gp = write_graph("parked")
    v = {"node": "N-002", "done": ["x"], "not_done": [], "not_verified": [],
         "blockers": [], "replan": {"possible": True, "add": [], "park": [], "why": ""},
         "evidence": ["ran"]}
    vp = os.path.join(d, "verdict.json")
    json.dump(v, open(vp, "w"))
    r = subprocess.run([sys.executable, GRAPH, "close", "--graph", gp, "--verdict", vp],
                       capture_output=True, text=True, cwd=d)
    assert r.returncode != 0, "a consumer closed over a parked producer"
    assert "N-001" in r.stderr


def t_all_done_or_parked_still_exits_3():
    d, gp = write_graph("parked")
    g = json.load(open(gp))
    g["nodes"][1]["status"] = "parked"
    g["nodes"][1]["parked_reason"] = "blocked by parked producer, alternative refused"
    json.dump(g, open(gp, "w"))
    r = run(gp, "next")
    assert r.returncode == 3, f"all-done-or-parked no longer exits 3 (got {r.returncode})"


def t_doc_states_the_predicate():
    d = " ".join(open(DOC, encoding="utf-8").read().split())
    assert "only `done` satisfies" in d
    assert "a park is a decision not to produce, not a production" in d
    assert "explicit, versioned edge change, never an implicit unblock" in d


def main():
    case("a parked producer blocks the frontier, named with its reason",
         t_parked_producer_blocks_the_frontier)
    case("a done producer unblocks", t_done_producer_unblocks)
    case("close refuses over a parked blocker", t_close_refuses_over_a_parked_blocker)
    case("all-done-or-parked still exits 3", t_all_done_or_parked_still_exits_3)
    case("the doc states the satisfaction predicate", t_doc_states_the_predicate)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
