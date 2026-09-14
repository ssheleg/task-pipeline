#!/usr/bin/env python3
"""FIX-HK-20 — stage 4 refuses a plan the next agent cannot execute.

The operator's finding, 2026-09-13: agents change between sessions, and a task whose
context lives in the planning conversation is a task the next agent re-derives or gets
wrong. The doctrine for this already existed — the cold reader's eight questions, the
leaf compiler, executor-sized tasks and their budgets — and none of it was MECHANICAL:
nothing read the plan and refused it.

`scripts/plan_audit.py` is that gate. This suite proves the three things a regression
can prove about it: it runs and its own guards pass, the doctrine that sends a run to
it says what it does, and the gate is wired into the stage-4 gate in both homes that
state it.

Standard library only.
"""
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline")
GATE = os.path.join(SKILL, "scripts", "plan_audit.py")
PLANNING = os.path.join(SKILL, "references", "planning.md")
STAGES = os.path.join(SKILL, "references", "stages.md")
TIERING = os.path.join(SKILL, "references", "model-tiering.md")
SKILL_MD = os.path.join(SKILL, "SKILL.md")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def flat(path):
    with open(path, encoding="utf-8") as fh:
        return " ".join(fh.read().split())


def t_the_gate_guards_itself():
    r = subprocess.run([sys.executable, GATE, "--self-test"], capture_output=True,
                       text=True, timeout=300)
    assert r.returncode == 0, f"the gate's own guards fail:\n{r.stdout}{r.stderr}"
    assert "SELF-TEST PASS" in r.stdout, r.stdout


def t_it_refuses_a_plan_whose_context_is_missing():
    """The failure the operator named, run end to end through the CLI."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        g = os.path.join(tmp, "graph.json")
        json.dump({"nodes": [{"id": "N-001", "title": "do it", "status": "pending"}]},
                  open(g, "w", encoding="utf-8"))
        r = subprocess.run([sys.executable, GATE, "--graph", g, "--packets",
                            os.path.join(tmp, "none")], capture_output=True, text=True,
                           timeout=300)
        assert r.returncode == 1, f"a node with no packet passed:\n{r.stdout}"
        assert "no execution packet" in r.stdout, r.stdout
        assert "stage 5 does not open" in r.stdout, "the refusal does not say what it blocks"


def t_a_missing_graph_is_a_usage_error_not_a_pass():
    r = subprocess.run([sys.executable, GATE, "--graph", "/nonexistent/graph.json"],
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 2, "a plan nobody could read must not report clean"
    assert "Nothing was read" in (r.stdout + r.stderr)


def t_one_home_for_the_cold_reader_contract():
    """The gate imports the eight questions; it does not restate them.

    A second copy is a second thing to drift, and this gate exists to catch drift.
    """
    src = open(GATE, encoding="utf-8").read()
    assert "from context_packets import COLD_READER_QUESTIONS" in src, \
        "the gate no longer imports the contract it checks against"
    assert '"goal", "inputs", "decisions"' not in src, \
        "the eight questions are restated in the gate — one home, or they drift"


def t_the_doctrine_names_what_the_gate_does():
    t = flat(PLANNING)
    assert "Plan audit — the plan read as the NEXT agent will read it" in t
    for needle in ("cold reader", "never connected either race", "computed, never declared"):
        assert needle in t, f"planning.md does not state {needle!r}"
    assert "python3 scripts/plan_audit.py" in t, "planning.md names no runnable command"


def t_both_gate_statements_name_it():
    assert "scripts/plan_audit.py" in flat(SKILL_MD), \
        "the stage table does not name the gate — a gate nobody is sent to is prose"
    assert "scripts/plan_audit.py" in flat(STAGES), \
        "stages.md's stage-4 GATE does not name it"


def t_the_model_profile_is_named_and_has_a_basis():
    t = flat(TIERING)
    assert "plan-then-execute" in t, "the profile the operator asked for is not named"
    assert "Its basis" in t, "a profile with no basis is a preference, and the rule above "\
                             "requires a recorded basis"
    assert "Task size still switches nothing" in t, \
        "the profile must not quietly repeal the rule it sits under"


def t_settled_nodes_do_not_block_a_plan():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        g = os.path.join(tmp, "graph.json")
        json.dump({"nodes": [{"id": "N-001", "title": "done work", "status": "done"}]},
                  open(g, "w", encoding="utf-8"))
        r = subprocess.run([sys.executable, GATE, "--graph", g, "--packets",
                            os.path.join(tmp, "none")], capture_output=True, text=True,
                           timeout=300)
        assert r.returncode == 0, f"finished work was demanded to carry a packet:\n{r.stdout}"


def main():
    case("the gate's own guards pass", t_the_gate_guards_itself)
    case("a node whose context is missing is refused, end to end",
         t_it_refuses_a_plan_whose_context_is_missing)
    case("a graph that cannot be read exits 2, never 0", t_a_missing_graph_is_a_usage_error_not_a_pass)
    case("the cold-reader contract has one home", t_one_home_for_the_cold_reader_contract)
    case("planning.md states what the gate does and how to run it", t_the_doctrine_names_what_the_gate_does)
    case("both stage-4 gate statements name the script", t_both_gate_statements_name_it)
    case("the model profile is named and carries its basis", t_the_model_profile_is_named_and_has_a_basis)
    case("a settled node does not block the plan", t_settled_nodes_do_not_block_a_plan)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
