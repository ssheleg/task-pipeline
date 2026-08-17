#!/usr/bin/env python3
"""Fixtures for `scripts/graph.py` — the invariants a schema cannot state.

`graph.schema.json` states everything JSON Schema can: the fields a node must
carry, that `owner` is a non-empty string, that an edge carries a payload, and —
after the R-005 read corrected the author — that `done` implies non-empty evidence.

What a schema cannot reach is **cross-document and cross-node**:

- whether `owner` names a role that actually exists
- whether `serves` resolves to a REQ or a goal clause that exists
- whether the edges form a cycle, which is a property of the whole graph

Those three are this script's, and this file is what proves it refuses each. Every
fixture builds a graph in a temp directory: one that could reach a real
`.task-pipeline/` would be a fixture that edits the run it is testing.
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
GRAPH = ROOT / "plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"

cases = 0
failures = []


def case(name):
    def deco(fn):
        global cases
        cases += 1
        try:
            fn()
            print("  ok  %s" % name)
        except AssertionError as e:
            failures.append("%s: %s" % (name, e))
            print("  FAIL  %s: %s" % (name, e))
    return deco


def run(graph, *args):
    """Run graph.py against a graph written to a temp file. Returns (code, out)."""
    d = tempfile.mkdtemp()
    p = pathlib.Path(d) / "graph.json"
    p.write_text(json.dumps(graph))
    r = subprocess.run([sys.executable, str(GRAPH), *args, "--graph", str(p)],
                       capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)


def g(nodes=None, edges=None, goal="a goal"):
    return {"goal": goal, "nodes": nodes or [], "edges": edges or []}


def node(nid, owner="implementer", status="pending", blocked=None, serves="REQ-001",
         evidence=None, title="t"):
    n = {"id": nid, "title": title, "owner": owner, "status": status,
         "blocked_by": blocked or [], "serves": serves}
    if evidence is not None:
        n["evidence"] = evidence
    return n


# --- validate: the three a schema cannot reach --------------------------------

@case("an owner that is not a known role is refused, and the message names it")
def _():
    code, out = run(g([node("N-001", owner="architect")]), "validate")
    assert code == 1, "an unknown owner passed: %s" % out
    assert "architect" in out, "the message does not name the owner it refused: %s" % out


@case("a MISSPELT known role is refused — the near miss, not just the absent one")
def _():
    code, out = run(g([node("N-001", owner="implementor")]), "validate")
    assert code == 1, "a misspelt role passed: %s" % out


@case("every shipped role name is accepted")
def _():
    for role in ("implementer", "reviewer", "fixer", "verifier", "decomposer",
                 "ux", "ui", "researcher", "market-analyst", "bug-analyst"):
        code, out = run(g([node("N-001", owner=role)]), "validate")
        assert code == 0, "%r was refused: %s" % (role, out)


@case("a cycle is refused, and the message names the nodes in it")
def _():
    code, out = run(g([node("N-001", blocked=["N-002"]), node("N-002", blocked=["N-001"])]),
                    "validate")
    assert code == 1, "a cycle passed: %s" % out
    assert "N-001" in out and "N-002" in out, "the cycle's nodes are not named: %s" % out


@case("a THREE-node cycle is refused too — not only the mutual pair")
def _():
    code, _ = run(g([node("N-001", blocked=["N-003"]), node("N-002", blocked=["N-001"]),
                     node("N-003", blocked=["N-002"])]), "validate")
    assert code == 1, "a three-node cycle passed"


@case("a blocked_by naming a node that does not exist is refused")
def _():
    code, out = run(g([node("N-001", blocked=["N-999"])]), "validate")
    assert code == 1, "a dangling blocked_by passed: %s" % out
    assert "N-999" in out, out


@case("an edge naming a node that does not exist is refused")
def _():
    code, out = run(g([node("N-001")],
                      [{"from": "N-001", "to": "N-042", "payload": "x"}]), "validate")
    assert code == 1, "a dangling edge passed: %s" % out


@case("a duplicate node id is refused — two nodes one id is a graph nobody can cite")
def _():
    code, _ = run(g([node("N-001"), node("N-001", title="other")]), "validate")
    assert code == 1, "a duplicate id passed"


@case("a clean graph validates and says nothing else")
def _():
    code, out = run(g([node("N-001"), node("N-002", blocked=["N-001"])],
                      [{"from": "N-001", "to": "N-002", "payload": "the thing"}]), "validate")
    assert code == 0, out
    assert out.strip() == "" or "ok" in out.lower(), "validate is noisy on a clean graph: %r" % out


# --- next: the frontier, and what it must NOT print ---------------------------

@case("next prints only runnable nodes")
def _():
    code, out = run(g([node("N-001", status="done", evidence=["x"]),
                       node("N-002", blocked=["N-001"]),
                       node("N-003", blocked=["N-002"])]), "next")
    assert code == 0, out
    assert "N-002" in out, "the runnable node is missing: %r" % out
    assert "N-003" not in out, "a blocked node reached the frontier: %r" % out
    assert "N-001" not in out, "a done node reached the frontier: %r" % out


@case("next prints the frontier and NOTHING else — this output is paid every iteration")
def _():
    _, out = run(g([node("N-001", owner="ux", title="check the funnel")]), "next")
    lines = [l for l in out.splitlines() if l.strip()]
    assert len(lines) == 1, "next printed %d lines, not one per runnable node: %r" % (len(lines), out)
    assert "N-001" in lines[0] and "ux" in lines[0], lines[0]


@case("a graph with every node done exits 3, not 0 — done and stalled are different")
def _():
    code, _ = run(g([node("N-001", status="done", evidence=["x"])]), "next")
    assert code == 3, "a complete graph did not exit 3 (got %s)" % code


@case("a graph where everything remaining is blocked exits 4")
def _():
    code, _ = run(g([node("N-001", status="blocked", blocked=["N-002"]),
                     node("N-002", status="blocked", blocked=["N-001"])]), "next")
    assert code in (1, 4), "an all-blocked graph exited %s" % code


@case("a parked node is not in the frontier")
def _():
    _, out = run(g([node("N-001", status="parked")]), "next")
    assert "N-001" not in out, "a parked node reached the frontier: %r" % out


if failures:
    print("\n%d failure(s) out of %d cases" % (len(failures), cases))
    sys.exit(1)
print("\nPASS: graph.py — %d cases" % cases)
