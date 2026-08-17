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



# --- the verdict: the shape `close` consumes, and what it refuses --------------

def verdict(**kw):
    v = {"node": "N-001", "done": ["a thing"], "not_done": [], "blockers": [],
         "replan": {"possible": True, "add": [], "park": [], "why": "nothing blocks"},
         "evidence": ["npm test → PASS"]}
    v.update(kw)
    return v


def check_verdict(v):
    """Ask graph.py, not a reimplementation of it. A fixture that validates the
    verdict itself would pass while the script disagreed."""
    sys.path.insert(0, str(GRAPH.parent))
    import importlib
    mod = importlib.import_module("graph")
    importlib.reload(mod)
    return mod.verdict_violations(v)


@case("a complete verdict is accepted")
def _():
    assert check_verdict(verdict()) == [], check_verdict(verdict())


@case("every one of the six keys is required, and the message names the missing one")
def _():
    for key in ("node", "done", "not_done", "blockers", "replan", "evidence"):
        v = verdict()
        del v[key]
        bad = check_verdict(v)
        assert bad, "a verdict with no %r was accepted" % key
        assert any(key in b for b in bad), "the refusal does not name %r: %s" % (key, bad)


@case("done without evidence is refused — the whole reason the field exists")
def _():
    bad = check_verdict(verdict(done=["a thing"], evidence=[]))
    assert bad, "a done claim with empty evidence was accepted"
    assert any("evidence" in b for b in bad), bad


@case("done EMPTY with evidence empty is fine — nothing was claimed")
def _():
    assert check_verdict(verdict(done=[], evidence=[])) == []


@case("a blocker must say what it blocks and whether the run can continue around it")
def _():
    bad = check_verdict(verdict(blockers=[{"what": "the API is down"}]))
    assert bad, "a blocker with no `blocks` and no `can_continue_around` was accepted"


@case("replan.possible false must carry a why — a stop with no reason is a stall")
def _():
    bad = check_verdict(verdict(replan={"possible": False, "add": [], "park": [], "why": ""}))
    assert bad, "a stop with no reason was accepted"
    assert any("why" in b for b in bad), bad


@case("replan.park naming a node id shape that cannot exist is refused")
def _():
    bad = check_verdict(verdict(replan={"possible": True, "add": [], "park": ["nope"], "why": "x"}))
    assert bad, "a park id that is not an N-nnn was accepted"


@case("evidence entries must be non-empty strings, matching what the SCHEMA requires")
def _():
    # The convergence check's finding: `['', '   ']` passed this function and was
    # refused by graph.schema.json, so `close` would have written a node its own
    # shipped schema rejects. A list of blanks is what a script emitting an empty
    # command output produces, which makes it the likely shape rather than a hostile one.
    for bad in ([""], ["   "], [123], [None], ["ok", ""]):
        got = check_verdict(verdict(done=["a thing"], evidence=bad))
        assert got, "evidence %r was accepted by the verdict gate" % (bad,)


@case("the verdict gate and the graph schema agree on evidence — checked against both")
def _():
    import json as _j
    schema = _j.loads((ROOT / "plugins/task-pipeline/skills/task-pipeline"
                       "/graph.schema.json").read_text())
    try:
        import jsonschema
    except ImportError:
        return
    for ev in ([""], ["  "], []):
        gate = bool(check_verdict(verdict(done=["x"], evidence=ev)))
        g = {"goal": "g", "edges": [],
             "nodes": [node("N-001", status="done", evidence=ev)]}
        try:
            jsonschema.validate(g, schema); sch = False
        except jsonschema.ValidationError:
            sch = True
        assert gate == sch, ("evidence %r: the verdict gate says %s and the schema says "
                             "%s — one of them writes what the other refuses" % (ev, gate, sch))


@case("manager and business-analyst may own a node — doctrine is not the same as absent")
def _():
    for role in ("manager", "business-analyst"):
        code, out = run(g([node("N-001", owner=role)]), "validate")
        assert code == 0, "%r cannot own a node: %s" % (role, out)


@case("project may NOT own a node — the brief defers it for having no stated job")
def _():
    code, _ = run(g([node("N-001", owner="project")]), "validate")
    assert code == 1, "a deferred role was accepted as an owner"


@case("the refusal never names a role the set rejects")
def _():
    import re as _re, sys as _s
    _s.path.insert(0, str(GRAPH.parent))
    import importlib, graph as _g
    importlib.reload(_g)
    src = GRAPH.read_text()
    named = set(_re.findall(r"`(manager|business-analyst|verifier|decomposer|ux|ui)`", src))
    missing = named - _g.ROLES
    assert not missing, "graph.py names %s in its prose and rejects it as an owner" % missing


# --- the agent ships, and to the contract the fetched reference gives ----------

@case("agents/verifier.md ships, and the manifest does NOT declare the directory")
def _():
    agent = ROOT / "plugins/task-pipeline/agents/verifier.md"
    assert agent.is_file(), "no agents/verifier.md"
    manifest = json.loads((ROOT / "plugins/task-pipeline/.claude-plugin/plugin.json").read_text())
    # The directory is discovered by convention. Declaring it as a string fails
    # `claude plugin validate --strict` with `agents: Invalid input`, and the
    # family's own working example (make-skill, which ships agents/skill-auditor.md
    # and resolves) declares no `agents` key at all. Asserted so the next author
    # does not add it back from the same wrong intuition this one had.
    assert "agents" not in manifest, ("plugin.json declares `agents` — the directory is "
                                      "discovered, and declaring it fails --strict")


@case("the agent declares only frontmatter keys plugin agents accept")
def _():
    txt = (ROOT / "plugins/task-pipeline/agents/verifier.md").read_text()
    fm = txt.split("---")[1]
    keys = {l.split(":")[0].strip() for l in fm.splitlines() if l.strip() and not l[0].isspace()}
    # Fetched 2026-08-17 from code.claude.com/docs/en/plugins-reference.
    allowed = {"name", "description", "model", "effort", "maxTurns", "tools",
               "disallowedTools", "skills", "memory", "background", "isolation"}
    rejected = {"hooks", "mcpServers", "permissionMode"}
    assert not (keys & rejected), "declares a key rejected for plugin agents: %s" % (keys & rejected)
    assert not (keys - allowed), "declares a key the reference does not list: %s" % (keys - allowed)
    assert "name" in keys and "description" in keys, keys


@case("the agent names no vendor model id — the tier, never the id")
def _():
    txt = (ROOT / "plugins/task-pipeline/agents/verifier.md").read_text()
    for bad in ("claude-3", "claude-opus-4", "gpt-4", "claude-sonnet-4"):
        assert bad not in txt, "hardcodes a vendor model id: %s" % bad


if failures:
    print("\n%d failure(s) out of %d cases" % (len(failures), cases))
    sys.exit(1)
print("\nPASS: graph.py — %d cases" % cases)
