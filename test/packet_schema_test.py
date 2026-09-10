#!/usr/bin/env python3
"""CTX-01.03 — typed dependencies and graph closure for the execution packet.

The schema (execution-packet.schema.json) gains typed edges — data / control /
resource, each with owner/rationale and (for payload edges) a satisfaction —
and `scripts/packet.py validate-graph` owns the SET properties: unique ids,
every edge resolves, no cycles.

The contract's teeth, each watched failing here:

* a CONTROL edge with no payload (no satisfaction) is VALID and PRESERVED —
  ordering is its whole payload, and pruning payload-less edges is the
  fake-edge defect the family's orchestrator doctrine forbids;
* a duplicate edge, a cycle, an unknown dependency and a payload edge without
  satisfaction are each rejected, by name.

Standard library only. Run by npm test.
"""
import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKILL = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline")
SCRIPT = os.path.join(SKILL, "scripts", "packet.py")

_spec = importlib.util.spec_from_file_location("packet", SCRIPT)
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)

checks = 0
failures = []


def case(name, fn):
    global checks
    try:
        fn()
        checks += 1
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def packet(pid, deps=None):
    base = json.load(open(os.path.join(SKILL, "execution-packet.example.json")))
    base["id"] = pid
    base["dependencies"] = deps or []
    return base


def edge(tid, kind="data", **over):
    d = {"task_id": tid, "kind": kind, "rationale": "consumes its output"}
    if kind in ("data", "resource"):
        d["satisfaction"] = "the artifact at docs/out.md exists with its receipt"
    d.update(over)
    return d


def run_graph(packets):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(packets, fh)
        path = fh.name
    try:
        return subprocess.run([sys.executable, SCRIPT, "validate-graph", path],
                              capture_output=True, text=True, timeout=60)
    finally:
        os.unlink(path)


def t_schema_declares_the_edge_shape():
    schema = json.load(open(os.path.join(SKILL, "execution-packet.schema.json")))
    dep = schema["properties"]["dependencies"]["items"]
    assert set(dep["required"]) == {"task_id", "kind", "rationale"}
    assert dep["properties"]["kind"]["enum"] == ["data", "control", "resource"]
    assert "owner" in dep["properties"] and "satisfaction" in dep["properties"]


def t_control_edge_without_payload_survives():
    a = packet("A")
    b = packet("B", deps=[edge("A", kind="control", rationale="A's decision must land first")])
    assert P.problems(b) == [], f"a payload-less control edge was rejected: {P.problems(b)}"
    r = run_graph([a, b])
    assert r.returncode == 0, f"the graph with a control edge failed:\n{r.stdout}"
    assert "1 control edge(s) preserved" in r.stdout, \
        f"the control edge was pruned from the receipt:\n{r.stdout}"


def t_payload_edge_needs_satisfaction():
    b = packet("B", deps=[{"task_id": "A", "kind": "data", "rationale": "needs the output"}])
    v = P.problems(b)
    assert any("without satisfaction" in x for x in v), f"a data edge with no satisfaction passed: {v}"


def t_duplicate_edge_rejected():
    b = packet("B", deps=[edge("A"), edge("A")])
    v = P.problems(b)
    assert any("duplicate edge" in x for x in v), f"a duplicate edge passed: {v}"
    # same target, DIFFERENT kind is two different statements — allowed
    b2 = packet("B", deps=[edge("A", kind="data"), edge("A", kind="control")])
    assert P.problems(b2) == [], f"data+control to one target was refused: {P.problems(b2)}"


def t_unknown_dep_rejected():
    r = run_graph([packet("A"), packet("B", deps=[edge("GHOST")])])
    assert r.returncode == 1 and "not in the graph" in r.stdout, \
        f"an unknown dependency passed:\n{r.stdout}"


def t_cycle_rejected():
    a = packet("A", deps=[edge("B", kind="control", rationale="loops")])
    b = packet("B", deps=[edge("A", kind="control", rationale="loops back")])
    r = run_graph([a, b])
    assert r.returncode == 1 and "cycle:" in r.stdout, f"a cycle passed:\n{r.stdout}"


def t_duplicate_ids_rejected():
    r = run_graph([packet("A"), packet("A")])
    assert r.returncode == 1 and "duplicate packet id" in r.stdout, \
        f"two packets with one id passed:\n{r.stdout}"


def t_unknown_kind_and_missing_rationale_rejected():
    b = packet("B", deps=[{"task_id": "A", "kind": "vibes", "rationale": "?"}])
    v = P.problems(b)
    assert any("not one of" in x for x in v), f"an unknown kind passed: {v}"
    b2 = packet("B", deps=[{"task_id": "A", "kind": "control", "rationale": ""}])
    v2 = P.problems(b2)
    assert any("missing rationale" in x for x in v2), f"a rationale-less edge passed: {v2}"


def main():
    case("the schema declares the edge shape", t_schema_declares_the_edge_shape)
    case("a control edge without payload survives, preserved", t_control_edge_without_payload_survives)
    case("a payload edge needs its satisfaction", t_payload_edge_needs_satisfaction)
    case("a duplicate edge is rejected; data+control to one target is two statements",
         t_duplicate_edge_rejected)
    case("an unknown dependency is rejected", t_unknown_dep_rejected)
    case("a cycle is rejected", t_cycle_rejected)
    case("duplicate packet ids are rejected", t_duplicate_ids_rejected)
    case("unknown kinds and missing rationales are rejected",
         t_unknown_kind_and_missing_rationale_rejected)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"OK ({checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
