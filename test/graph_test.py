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
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import residue  # noqa: E402 -- one ledger, copied not rewritten

GRAPH = ROOT / "plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"

cases = 0
failures = []
# What this run could NOT look at. A skip that prints nothing reads exactly
# like a check that looked and found nothing — canon 9, and `validate.py`
# already discloses its own the same way.
skipped = []


def case(name):
    def deco(fn):
        global cases
        cases += 1
        residue.open_case(name)
        try:
            fn()
            residue.close_case(name)
            print("  ok  %s" % name)
        except AssertionError as e:
            failures.append("%s: %s" % (name, e))
            print("  FAIL  %s: %s" % (name, e))
        except Exception as e:                      # noqa: BLE001 — deliberate
            # A fixture that raises anything else used to abort the whole suite, so one
            # `KeyError` hid every case after it. A harness that stops on the first crash
            # reports fewer failures than exist and reads like fewer problems.
            failures.append("%s: CRASH %s: %s" % (name, type(e).__name__, e))
            print("  CRASH  %s: %s: %s" % (name, type(e).__name__, e))
    return deco


def run(graph, *args):
    """Run graph.py against a graph written to a temp file. Returns (code, out)."""
    d = residue.workspace("graph")
    p = pathlib.Path(d) / "graph.json"
    p.write_text(json.dumps(graph))
    r = subprocess.run([sys.executable, str(GRAPH), *args, "--graph", str(p)],
                       capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)


_AUTO = object()


def g(nodes=None, edges=_AUTO, goal="a goal", reqs=_AUTO, clauses=None):
    """A graph. Edges are DERIVED from `blocked_by` unless given explicitly.

    Every dependency needs an edge carrying what it hands over (B-084), so a helper that
    built `blocked_by` and no edges would make every fixture invalid. Pass `edges=[]` to
    build the graph that has a dependency and no edge — which is exactly what one
    fixture is for.
    """
    nodes = nodes or []
    if edges is _AUTO:
        edges = [{"from": b, "to": n.get("id"), "payload": "what %s hands over" % b}
                 for n in nodes for b in (n.get("blocked_by") or [])]
    out = {"goal": goal, "nodes": nodes, "edges": edges}
    out["requirements"] = (sorted({n.get("serves") for n in nodes
                                   if str(n.get("serves", "")).startswith("REQ-")})
                           if reqs is _AUTO else reqs)
    if clauses:
        out["goal_clauses"] = clauses
    return out


def node(nid, owner="implementer", status="pending", blocked=None, serves="REQ-001",
         evidence=None, title="t", check="npm test"):
    """A node. `check` is on by default and `check=None` builds the B-080 defect.

    Every node the verifier will close has to say how it will be closed, so a helper
    that omitted it would make every fixture invalid — the same reason `g()` derives an
    edge per `blocked_by`. Pass `check=None` for the one fixture that needs the absence.
    """
    n = {"id": nid, "title": title, "owner": owner, "status": status,
         "blocked_by": blocked or [], "serves": serves}
    if check is not None:
        n["check"] = check
    if evidence is not None:
        n["evidence"] = evidence
    return n


def run_out(graph, *args):
    """stdout ONLY. The frontier's width contract is about stdout — `next` writes its
    collision and undeclared disclosures to stderr precisely so the rows stay parseable,
    and a helper that merges the two cannot tell the contract from its violation."""
    d = residue.workspace("graph")
    p = pathlib.Path(d) / "graph.json"
    p.write_text(json.dumps(graph))
    r = subprocess.run([sys.executable, str(GRAPH), *args, "--graph", str(p)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout


def run_at_out(path, *args):
    """stdout only, against a persistent graph — the width contract's unit."""
    r = subprocess.run([sys.executable, str(GRAPH), *args, "--graph", str(path)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout


def run_at(path, *args):
    """Run against a graph that PERSISTS, so a mutation can be read back.

    `run()` writes to a temp file and drops it — right for `validate` and `next`,
    useless for `add` and `park`, whose whole contract is what the file says
    afterwards. The mutation verbs are tested through this one.
    """
    r = subprocess.run([sys.executable, str(GRAPH), *args, "--graph", str(path)],
                       capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)


def _flat(text):
    """Collapse ~80-column wrapping and emphasis before matching a phrase.

    A sentence broken across two lines is the shape that has defeated guards in this
    corpus repeatedly, and a doctrine fixture matching prose needs the same treatment
    `test/validate.py` gives its own.
    """
    return re.sub(r"\s+", " ", re.sub(r"[*_`]+", "", text))


def written(graph):
    """A graph on disk, plus its path. The caller mutates it and reads it back."""
    d = residue.workspace("graph")
    p = pathlib.Path(d) / "graph.json"
    p.write_text(json.dumps(graph))
    return p


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
    _, out = run_out(g([node("N-001", owner="ux", title="check the funnel")]), "next")
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
    v = {"node": "N-001", "done": ["a thing"], "not_done": [], "not_verified": [],
         "blockers": [],
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


@case("every one of the seven keys is required, and the message names the missing one")
def _():
    # `not_verified` is the seventh, added by T-5: the six said what is built and what is
    # not, and none said what was BUILT AND NOT CHECKED. `npm test` prints `unlooked: N` one
    # level up, so the pipeline named the concept everywhere except in the verdict that
    # closes work with it.
    for key in ("node", "done", "not_done", "not_verified", "blockers", "replan", "evidence"):
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



# --- T-3: park, and the reason that is the whole point -------------------------
#
# R-008 — the shapes the defect can take, enumerated before the fix was written.
# `park` refuses without a reason, and "without" has four shapes, not one:
# the flag absent, the flag empty, the flag whitespace, and a reason already
# recorded that a second park would overwrite. Only the first is argparse's.

@case("park with no --reason at all is a usage error, not a silent park")
def _():
    p = written(g([node("N-001")]))
    code, out = run_at(p, "park", "N-001")
    assert code == 2, "park without --reason did not exit 2 (usage): %s" % out
    assert json.loads(p.read_text())["nodes"][0]["status"] == "pending", "it parked anyway"


@case("park with an EMPTY --reason is refused — the flag present is not a reason given")
def _():
    p = written(g([node("N-001")]))
    code, out = run_at(p, "park", "N-001", "--reason", "")
    assert code == 1, "an empty reason was accepted: %s" % out
    assert json.loads(p.read_text())["nodes"][0]["status"] == "pending", "it parked anyway"


@case("park with a WHITESPACE --reason is refused — the shape that satisfies argparse")
def _():
    p = written(g([node("N-001")]))
    code, out = run_at(p, "park", "N-001", "--reason", "   ")
    assert code == 1, "a whitespace reason was accepted: %s" % out


@case("park records the reason, and it reads back off the file — REQ-012")
def _():
    p = written(g([node("N-001"), node("N-002")]))
    reason = "serves module 2, not this release's goal"
    code, out = run_at(p, "park", "N-001", "--reason", reason)
    assert code == 0, "a well-formed park was refused: %s" % out
    n = json.loads(p.read_text())["nodes"][0]
    assert n["status"] == "parked", n
    assert n.get("parked_reason") == reason, ("the reason is not on the node — REQ-012 is "
                                              "the reason being recorded, not the status: %s" % n)


@case("a parked node leaves the frontier")
def _():
    p = written(g([node("N-001"), node("N-002")]))
    run_at(p, "park", "N-001", "--reason", "not this release")
    code, out = run_at(p, "next")
    assert code == 0, out
    assert "N-001" not in out, "a parked node is still offered as runnable: %s" % out
    assert "N-002" in out, out


@case("park names a node that does not exist — refused, and the message names the id")
def _():
    p = written(g([node("N-001")]))
    code, out = run_at(p, "park", "N-404", "--reason", "x")
    assert code == 1, "parking a node that does not exist was accepted: %s" % out
    assert "N-404" in out, "the refusal does not name the id: %s" % out


@case("parking a DONE node is refused — a closed result is not re-openable this way")
def _():
    p = written(g([node("N-001", status="done", evidence=["npm test → PASS"])]))
    code, out = run_at(p, "park", "N-001", "--reason", "changed my mind")
    assert code == 1, "a done node was parked, destroying its close: %s" % out
    assert json.loads(p.read_text())["nodes"][0]["status"] == "done"


@case("re-parking is refused, and the refusal quotes the reason already recorded")
def _():
    p = written(g([node("N-001")]))
    run_at(p, "park", "N-001", "--reason", "waiting on the operator's pricing call")
    code, out = run_at(p, "park", "N-001", "--reason", "something else")
    assert code == 1, "a second park overwrote the first reason: %s" % out
    assert "pricing call" in out, ("the refusal does not quote the reason it protected: %s" % out)
    assert json.loads(p.read_text())["nodes"][0]["parked_reason"].endswith("pricing call")


# --- T-3: add, the dynamic backlog ---------------------------------------------

@case("add appends a node and allocates the next id")
def _():
    p = written(g([node("N-001")]))
    code, out = run_at(p, "add", "--title", "a thing found mid-run",
                       "--owner", "implementer", "--serves", "REQ-001",
                       "--check", "npm test", "--why", "a fixture")
    assert code == 0, "a well-formed add was refused: %s" % out
    nodes = json.loads(p.read_text())["nodes"]
    assert len(nodes) == 2, nodes
    assert nodes[1]["id"] == "N-002", nodes[1]
    assert nodes[1]["status"] == "pending", nodes[1]
    assert "N-002" in out, "add does not print the id it allocated: %s" % out


@case("the id is allocated from the MAXIMUM, not from the count")
def _():
    # Ids are not contiguous once anything has been renumbered or imported. Counting
    # nodes hands out an id that already exists, and two nodes with one id is a graph
    # nobody can cite — the exact defect `validate` reports as a duplicate.
    p = written(g([node("N-001"), node("N-050")]))
    code, out = run_at(p, "add", "--title", "t", "--owner", "implementer", "--serves", "REQ-001", "--check", "npm test", "--why", "a fixture")
    assert code == 0, out
    assert json.loads(p.read_text())["nodes"][-1]["id"] == "N-051", out


@case("an explicit --id that already exists is refused")
def _():
    p = written(g([node("N-001")]))
    code, out = run_at(p, "add", "--id", "N-001", "--title", "t",
                       "--owner", "implementer", "--serves", "REQ-001",
                       "--check", "npm test", "--why", "a fixture")
    assert code == 1, "a duplicate id was accepted: %s" % out
    assert len(json.loads(p.read_text())["nodes"]) == 1, "it was written anyway"


@case("add with an unknown owner is refused and NOTHING is written")
def _():
    p = written(g([node("N-001")]))
    before = p.read_text()
    code, out = run_at(p, "add", "--title", "t", "--owner", "architect", "--serves", "REQ-001", "--check", "npm test", "--why", "a fixture")
    assert code == 1, "an unknown owner was added: %s" % out
    assert p.read_text() == before, "the file changed on a refusal"


@case("add --blocked-by naming a node that does not exist is refused")
def _():
    p = written(g([node("N-001")]))
    code, out = run_at(p, "add", "--title", "t", "--owner", "implementer",
                       "--serves", "REQ-001", "--blocked-by", "N-404", "--carries", "what it hands over", "--check", "npm test", "--why", "a fixture")
    assert code == 1, "a dangling blocked_by was added: %s" % out
    assert len(json.loads(p.read_text())["nodes"]) == 1


@case("add with an empty title is refused")
def _():
    p = written(g([node("N-001")]))
    code, out = run_at(p, "add", "--title", "  ", "--owner", "implementer", "--serves", "REQ-001", "--check", "npm test", "--why", "a fixture")
    assert code == 1, "an empty title was accepted: %s" % out


@case("add with an empty --serves is refused — a node serving nothing is REQ-012's case")
def _():
    p = written(g([node("N-001")]))
    code, out = run_at(p, "add", "--title", "t", "--owner", "implementer", "--serves", " ", "--check", "npm test", "--why", "a fixture")
    assert code == 1, "a node serving nothing was added rather than refused: %s" % out


@case("a mutation on an ALREADY-invalid graph says so, rather than blaming the new node")
def _():
    p = written(g([node("N-001", owner="architect")]))
    code, out = run_at(p, "add", "--title", "t", "--owner", "implementer", "--serves", "REQ-001", "--check", "npm test", "--why", "a fixture")
    assert code == 1, out
    assert "already" in out.lower(), ("the refusal reads as though the caller's node were "
                                      "the problem: %s" % out)
    assert len(json.loads(p.read_text())["nodes"]) == 1


@case("a refused mutation leaves the file byte-identical")
def _():
    p = written(g([node("N-001")]))
    before = p.read_bytes()
    for args in (("park", "N-404", "--reason", "x"),
                 ("add", "--id", "N-001", "--title", "t", "--owner", "implementer",
                  "--serves", "REQ-001", "--check", "npm test", "--why", "a fixture")):
        run_at(p, *args)
        assert p.read_bytes() == before, "a refusal wrote to the file: %s" % (args,)


# --- T-3: the frontier re-prioritises, and the fixture proves the ORDER moves ---

@case("the frontier is ordered by how much each node unblocks")
def _():
    # N-002 blocks two nodes, N-001 blocks none. Declaration order puts N-001 first;
    # priority must put N-002 first, or the ordering claim is decoration.
    p = written(g([node("N-001"), node("N-002"),
                   node("N-003", blocked=["N-002"]), node("N-004", blocked=["N-002"])]))
    code, out = run_at(p, "next")
    assert code == 0, out
    ids = [l.split()[0] for l in out.strip().splitlines()]
    assert ids[0] == "N-002", "the frontier is not ordered by what it unblocks: %s" % ids


@case("a node added mid-walk re-prioritises the NEXT frontier — REQ-011")
def _():
    p = written(g([node("N-001"), node("N-002")]))
    first = [l.split()[0] for l in run_at_out(p, "next")[1].strip().splitlines()]
    assert first == ["N-001", "N-002"], first
    # The dynamic backlog: a task run finds work that depends on N-002.
    for _i in range(2):
        code, out = run_at(p, "add", "--title", "found mid-run", "--owner", "implementer",
                           "--serves", "REQ-001", "--blocked-by", "N-002", "--carries", "what it hands over", "--check", "npm test", "--why", "a fixture")
        assert code == 0, out
    second = [l.split()[0] for l in run_at_out(p, "next")[1].strip().splitlines()]
    assert second[0] == "N-002", ("the frontier did not re-prioritise after the backlog "
                                  "grew: %s → %s" % (first, second))


@case("the order is deterministic — the same graph gives the same frontier twice")
def _():
    p = written(g([node("N-00%d" % i) for i in range(1, 6)]))
    a = run_at_out(p, "next")[1]
    b = run_at_out(p, "next")[1]
    assert a == b, "the frontier flickers between runs:\n%s\n---\n%s" % (a, b)


@case("next prints the frontier and nothing else, priority or not")
def _():
    p = written(g([node("N-001"), node("N-002", blocked=["N-001"])]))
    code, out = run_at_out(p, "next")
    assert code == 0, out
    lines = [l for l in out.strip().splitlines() if l.strip()]
    assert len(lines) == 1, "next printed more than the frontier: %r" % out
    assert lines[0].split()[0] == "N-001", out


@case("a mutated graph still validates against graph.schema.json itself")
def _():
    try:
        import jsonschema
    except ImportError:
        skipped.append("the mutated-graph schema cross-check")
        return
    schema = json.loads((ROOT / "plugins/task-pipeline/skills/task-pipeline"
                              / "graph.schema.json").read_text())
    p = written(g([node("N-001"), node("N-002")]))
    # The exit codes are the point. Without them this fixture passed with BOTH verbs
    # replaced by `die()` — an unmutated graph validates, so it reported `ok` while
    # proving nothing about mutations. Demonstrated by the R-005 reader, not by me.
    code, out = run_at(p, "add", "--title", "t", "--owner", "ui", "--serves", "REQ-001",
                       "--blocked-by", "N-001", "--blocked-by", "N-001", "--carries", "what it hands over", "--carries", "what it hands over", "--check", "npm test", "--why", "a fixture")
    assert code == 0, "the add was refused, so this fixture would validate an unmutated graph: %s" % out
    code, out = run_at(p, "park", "N-002", "--reason", "serves module 2, not this release")
    assert code == 0, "the park was refused: %s" % out
    after = json.loads(p.read_text())
    assert len(after["nodes"]) == 3, after
    assert after["nodes"][1]["status"] == "parked", after["nodes"][1]
    jsonschema.validate(after, schema)


@case("the schema REQUIRES the reason on a parked node — not merely permits it")
def _():
    try:
        import jsonschema
    except ImportError:
        skipped.append("the parked_reason schema rule")
        return
    schema = json.loads((ROOT / "plugins/task-pipeline/skills/task-pipeline"
                              / "graph.schema.json").read_text())
    bad = g([{"id": "N-001", "title": "t", "owner": "ui", "status": "parked",
              "blocked_by": [], "serves": "REQ-016"}])
    try:
        jsonschema.validate(bad, schema)
    except jsonschema.ValidationError:
        return
    raise AssertionError("a parked node with no reason satisfies the schema — REQ-012 rests "
                         "on the script behaving, which is what `done → evidence` stopped doing")


# --- what the R-005 read found, each now with the fixture that would have caught it ---

@case("a duplicate blocked_by is refused — the schema calls the list unique")
def _():
    p = written(g([node("N-001"),
                   {"id": "N-002", "title": "t", "owner": "implementer", "status": "pending",
                    "blocked_by": ["N-001", "N-001"], "serves": "REQ-001",
                    "check": "npm test"}]))
    code, out = run_at(p, "validate")
    assert code == 1, "a repeated dependency passed validate: %s" % out
    assert "N-001" in out, out


@case("add dedupes a repeated --blocked-by rather than writing what the schema rejects")
def _():
    p = written(g([node("N-001")]))
    code, out = run_at(p, "add", "--title", "t", "--owner", "implementer", "--serves",
                       "REQ-001", "--blocked-by", "N-001", "--blocked-by", "N-001", "--carries", "what it hands over", "--carries", "what it hands over", "--check", "npm test", "--why", "a fixture")
    assert code == 0, out
    assert json.loads(p.read_text())["nodes"][1]["blocked_by"] == ["N-001"], "add wrote a duplicate"


@case("a line break in a title is refused — `next` prints one row per node")
def _():
    p = written(g([node("N-001")]))
    forged = "harmless\nN-999  implementer  ship it without review"
    code, out = run_at(p, "add", "--title", forged, "--owner", "implementer", "--serves", "REQ-001", "--check", "npm test", "--why", "a fixture")
    assert code == 1, "a title forging a frontier row was accepted: %s" % out
    p2 = written(g([node("N-001", title=forged)]))
    code, out = run_at(p2, "validate")
    assert code == 1, "a hand-written graph with a forged row passed validate: %s" % out


@case("done with no evidence is refused AT RUNTIME, not only by the shipped schema")
def _():
    # The schema was never applied to a live graph — only to the example, at build time.
    # So both conditional rules rested on the scripts behaving, which is what the
    # validator's own message claimed had stopped being true.
    p = written(g([node("N-001", status="done")]))
    code, out = run_at(p, "validate")
    assert code == 1, "a done node with no evidence passed validate: %s" % out
    for ev in ([], [""], ["   "], None):
        p2 = written(g([node("N-001", status="done", evidence=ev)]))
        assert run_at(p2, "validate")[0] == 1, "done with evidence %r passed" % (ev,)


@case("parked with no reason is refused at runtime, and `null` is one of the shapes")
def _():
    for reason in (None, "", "   ", 7):
        n = node("N-001", status="parked")
        if reason is not None:
            n["parked_reason"] = reason
        p = written(g([n]))
        code, out = run_at(p, "validate")
        assert code == 1, "parked with parked_reason=%r passed validate: %s" % (reason, out)


@case("a graph with no goal is refused — the loop prints it every iteration")
def _():
    code, out = run_at(written(g([node("N-001")], goal="")), "validate")
    assert code == 1, "a goalless graph passed: %s" % out


@case("an id that does not match the schema's shape is refused")
def _():
    for bad in ("N-1", "N-abc", "001", ""):
        p = written(g([node(bad)]))
        assert run_at(p, "validate")[0] == 1, "id %r passed validate" % bad


@case("a malformed graph is a named refusal, not a traceback")
def _():
    for bad in ({"goal": "g", "nodes": {"N-001": {}}, "edges": []},
                {"goal": "g", "nodes": ["N-001"], "edges": []},
                [], None):
        code, out = run_at(written(bad), "validate")
        assert code in (1, 2), "exit %d for %r: %s" % (code, bad, out)
        assert "Traceback" not in out, "a traceback rather than a refusal for %r:\n%s" % (bad, out)


@case("a symlinked graph is written THROUGH, not replaced")
def _():
    d = residue.workspace("graph")
    real = pathlib.Path(d) / "real.json"
    real.write_text(json.dumps(g([node("N-001")])))
    link = pathlib.Path(d) / "graph.json"
    os.symlink(real, link)
    code, out = run_at(link, "add", "--title", "t", "--owner", "implementer", "--serves", "REQ-001", "--check", "npm test", "--why", "a fixture")
    assert code == 0, out
    assert link.is_symlink(), "os.replace replaced the link — the queue forks in two"
    assert len(json.loads(real.read_text())["nodes"]) == 2, "the target did not receive the node"


@case("two concurrent adds do not share one temp file")
def _():
    # A fixed `path + '.tmp'` made two writers share an inode: exit 0 with the node
    # absent, and exit 1 with it present — the second is what makes a retry double-add.
    p = written(g([node("N-001")]))
    procs = [subprocess.Popen([sys.executable, str(GRAPH), "add", "--title", "t%d" % i,
                               "--owner", "implementer", "--serves", "REQ-001",
                               "--check", "npm test",
                               "--why", "a concurrent fixture", "--graph", str(p)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
             for i in range(4)]
    codes = [pr.wait() for pr in procs]
    after = json.loads(p.read_text())          # must still parse
    titles = {n["title"] for n in after["nodes"]}
    assert codes == [0, 0, 0, 0], "a concurrent add failed: %s" % codes
    assert len(after["nodes"]) == 5, ("%d nodes where 5 were expected — a lost update: two "
                                      "processes read the same graph and the second write "
                                      "dropped the first node, both exiting 0"
                                      % len(after["nodes"]))
    for i in range(4):
        assert "t%d" % i in titles, "run %d exited 0 and its node is absent" % i
    assert len({n["id"] for n in after["nodes"]}) == 5, "two nodes got the same id"


# --- B-084: the edge must carry something, and `add` must write one ---------------
#
# The graph stored a dependency twice in two unlinked places: `blocked_by`, which is
# what `frontier()` obeys, and `edges`, which carries the payload and which nothing
# read. `add` wrote the first and never the second, so every node added mid-run made a
# dependency whose payload was unnamed BY CONSTRUCTION — the manifesto's own named
# teeth, violated by this pipeline's own mutation verb. Found by a four-way audit,
# 2026-08-17; measured then as 5 nodes, 2 edges, `validate` exit 0.

@case("an edge with no payload is refused — the schema said so and nothing enforced it")
def _():
    g2 = g([node("N-001"), node("N-002", blocked=["N-001"])],
           edges=[{"from": "N-001", "to": "N-002"}])
    code, out = run(g2, "validate")
    assert code == 1, "an edge carrying nothing passed validate: %s" % out
    assert "payload" in out, out


@case("an edge whose payload is blank is refused too — presence is not content")
def _():
    for pay in ("", "   "):
        g2 = g([node("N-001"), node("N-002", blocked=["N-001"])],
               edges=[{"from": "N-001", "to": "N-002", "payload": pay}])
        assert run(g2, "validate")[0] == 1, "payload %r passed" % pay


@case("a blocked_by pair with no edge is refused — a dependency that hands over nothing")
def _():
    code, out = run(g([node("N-001"), node("N-002", blocked=["N-001"])], edges=[]), "validate")
    assert code == 1, "a dependency with no edge passed validate: %s" % out
    assert "N-001" in out and "N-002" in out, out


@case("the edge must run blocker → blocked, not the other way")
def _():
    g2 = g([node("N-001"), node("N-002", blocked=["N-001"])],
           edges=[{"from": "N-002", "to": "N-001", "payload": "backwards"}])
    code, out = run(g2, "validate")
    assert code == 1, "an edge pointing the wrong way satisfied the dependency: %s" % out


@case("a matched dependency and edge validate")
def _():
    g2 = g([node("N-001"), node("N-002", blocked=["N-001"])],
           edges=[{"from": "N-001", "to": "N-002", "payload": "the schema it validates against"}])
    code, out = run(g2, "validate")
    assert code == 0, "a well-formed pair was refused: %s" % out


@case("an empty title or serves is refused at runtime, not only by the schema")
def _():
    for field, val in (("title", ""), ("title", "  "), ("serves", ""), ("serves", "   ")):
        n = node("N-001")
        n[field] = val
        assert run(g([n]), "validate")[0] == 1, "%s=%r passed validate" % (field, val)


@case("add --blocked-by requires --carries, and says so")
def _():
    p = written(g([node("N-001")]))
    code, out = run_at(p, "add", "--title", "t", "--owner", "implementer", "--serves",
                       "REQ-001", "--blocked-by", "N-001", "--check", "npm test", "--why", "found mid-run")
    assert code == 1, "a dependency was added with no payload: %s" % out
    assert "carries" in out.lower(), "the refusal does not name the missing flag: %s" % out
    assert len(json.loads(p.read_text())["nodes"]) == 1, "it was written anyway"


@case("add writes the edge with the node, and the payload is what was given")
def _():
    p = written(g([node("N-001")]))
    code, out = run_at(p, "add", "--title", "t", "--owner", "implementer", "--serves",
                       "REQ-001", "--blocked-by", "N-001", "--carries", "the parsed frontier",
                       "--check", "npm test", "--why", "the audit found it")
    assert code == 0, out
    after = json.loads(p.read_text())
    assert len(after["nodes"]) == 2, after
    edges = [e for e in after["edges"] if e["to"] == "N-002"]
    assert len(edges) == 1, "add did not write the edge: %s" % after["edges"]
    assert edges[0] == {"from": "N-001", "to": "N-002", "payload": "the parsed frontier"}, edges[0]
    assert run_at(p, "validate")[0] == 0, "add wrote a graph that does not validate"


@case("--carries and --blocked-by must pair up, and a mismatch names both counts")
def _():
    p = written(g([node("N-001"), node("N-002")]))
    code, out = run_at(p, "add", "--title", "t", "--owner", "implementer", "--serves", "REQ-001",
                       "--blocked-by", "N-001", "--blocked-by", "N-002",
                       "--carries", "only one", "--check", "npm test", "--why", "w")
    assert code == 1, "a count mismatch was accepted: %s" % out
    assert "2" in out and "1" in out, "the refusal does not name both counts: %s" % out


@case("add requires --why, and refuses a blank one")
def _():
    p = written(g([node("N-001")]))
    code, out = run_at(p, "add", "--title", "t", "--owner", "implementer", "--serves", "REQ-001",
                       "--check", "npm test")
    assert code == 2, "add without --why is a usage error: got %d — %s" % (code, out)
    code, out = run_at(p, "add", "--title", "t", "--owner", "implementer", "--serves",
                       "REQ-001", "--check", "npm test", "--why", "   ")
    assert code == 1, "a blank --why was accepted: %s" % out


@case("every mutation appends a revision carrying its reason — B-084, and the graph says why it changed")
def _():
    p = written(g([node("N-001")]))
    run_at(p, "add", "--title", "t", "--owner", "implementer", "--serves", "REQ-001",
           "--check", "npm test",
           "--why", "the reader found a gap the plan had no node for")
    run_at(p, "park", "N-001", "--reason", "serves module 2, not this release")
    rev = json.loads(p.read_text()).get("revisions")
    assert isinstance(rev, list) and len(rev) == 2, "revisions: %r" % (rev,)
    assert rev[0]["verb"] == "add" and rev[0]["node"] == "N-002", rev[0]
    assert "no node for" in rev[0]["why"], rev[0]
    assert rev[1]["verb"] == "park" and rev[1]["node"] == "N-001", rev[1]
    assert "module 2" in rev[1]["why"], rev[1]


@case("a revision with a blank why is refused by validate — the log is not decoration")
def _():
    g2 = g([node("N-001")])
    g2["revisions"] = [{"verb": "add", "node": "N-001", "why": "  "}]
    assert run(g2, "validate")[0] == 1, "a blank revision reason passed validate"


@case("the shipped example still validates with the tightened rules")
def _():
    ex = json.loads((ROOT / "plugins/task-pipeline/skills/task-pipeline"
                          / "graph.example.json").read_text())
    code, out = run(ex, "validate")
    assert code == 0, "graph.example.json no longer validates: %s" % out


# --- B-085 / B-077: the edge between intent and execution, and the relation over it --
#
# `serves` was a non-empty string and nothing more, so `serves: "REQ-999"` and
# `serves: "asdf"` passed every gate identically — the one edge joining the intent graph
# to the execution graph, unchecked. And the coverage relation the pipeline defines
# precisely (`references/acceptance.md`: decision → spec → contract → task → change →
# executed test → surface) was walked by an agent with a checklist and computed by
# nothing.

@case("a serves that names no declared requirement is refused, and the message names it")
def _():
    g2 = g([node("N-001", serves="REQ-999")], reqs=["REQ-001"])
    code, out = run(g2, "validate")
    assert code == 1, "an unresolvable serves passed: %s" % out
    assert "REQ-999" in out, out


@case("a serves naming a declared goal clause resolves")
def _():
    g2 = g([node("N-001", serves="the loop advances without a human")],
           reqs=["REQ-001"], clauses=["the loop advances without a human"])
    assert run(g2, "validate")[0] == 0, run(g2, "validate")[1]


@case("a graph declaring no requirements is refused — the intent side cannot be empty")
def _():
    g2 = g([node("N-001")], reqs=[])
    code, out = run(g2, "validate")
    assert code == 1, "a graph with no declared requirements passed: %s" % out
    assert "requirement" in out.lower(), out


@case("coverage prints each requirement and the nodes serving it")
def _():
    g2 = g([node("N-001", serves="REQ-001", status="done", evidence=["npm test → PASS"]),
            node("N-002", serves="REQ-002")], reqs=["REQ-001", "REQ-002"])
    code, out = run(g2, "coverage")
    assert code == 0, "a fully covered graph was refused: %s" % out
    assert "REQ-001" in out and "N-001" in out, out
    assert "REQ-002" in out and "N-002" in out, out


@case("coverage refuses a requirement no node serves, and names it")
def _():
    g2 = g([node("N-001", serves="REQ-001")], reqs=["REQ-001", "REQ-002"])
    code, out = run(g2, "coverage")
    assert code == 1, "an uncovered requirement passed coverage: %s" % out
    assert "REQ-002" in out, "the uncovered requirement is not named: %s" % out


@case("coverage reports a requirement whose every node is parked — covered on paper only")
def _():
    g2 = g([{"id": "N-001", "title": "t", "owner": "ui", "status": "parked",
             "blocked_by": [], "serves": "REQ-002",
             "parked_reason": "serves module 2, not this release"},
            node("N-002", serves="REQ-001")],
           reqs=["REQ-001", "REQ-002"])
    code, out = run(g2, "coverage")
    assert code == 1, "a requirement served only by a parked node passed: %s" % out
    assert "REQ-002" in out and "parked" in out.lower(), out


@case("coverage names a done node whose evidence is empty rather than counting it")
def _():
    # `validate` already refuses this, so coverage must not be the only place it is
    # caught — but a coverage report that counted it as covered would be the lie.
    g2 = g([node("N-001", serves="REQ-001", status="done", evidence=[])], reqs=["REQ-001"])
    assert run(g2, "validate")[0] == 1, "done with no evidence passed validate"


@case("coverage says plainly what it cannot see")
def _():
    g2 = g([node("N-001", serves="REQ-001", status="done", evidence=["npm test → PASS"])],
           reqs=["REQ-001"])
    code, out = run(g2, "coverage")
    assert code == 0, out
    low = out.lower()
    assert "ledger" in low or "not read" in low or "cannot" in low, (
        "coverage claims a completeness it does not have — the fourth direction (an "
        "evidence row closing no requirement) lives in the ledger, which this script "
        "does not read, and a report silent about that reads as the whole relation: %s" % out)


@case("the shipped example declares its requirements and covers them")
def _():
    ex = json.loads((ROOT / "plugins/task-pipeline/skills/task-pipeline"
                          / "graph.example.json").read_text())
    assert ex.get("requirements"), "the example declares no requirements"
    code, out = run(ex, "validate")
    assert code == 0, "the example no longer validates: %s" % out


@case("add refuses a serves the brief never froze, and says who may add one")
def _():
    p = written(g([node("N-001", serves="REQ-001")]))
    code, out = run_at(p, "add", "--title", "t", "--owner", "implementer",
                       "--serves", "REQ-042", "--check", "npm test", "--why", "found mid-run")
    assert code == 1, "a node invented its own requirement: %s" % out
    assert "REQ-042" in out and "brief" in out.lower(), (
        "the refusal does not say the brief owns the REQ table: %s" % out)
    assert len(json.loads(p.read_text())["nodes"]) == 1, "it was written anyway"


# --- B-086: what produced the proof --------------------------------------------------
#
# Every artifact recorded what was done, what proved it and whether a person looked.
# None recorded what PRODUCED it. Two runs six months apart, one under v1.40 doctrine and
# one under v1.69, produced indistinguishable coverage tables — so a defect traced to a
# doctrine change could not be scoped to the runs that carried it.

def producer(env=None, cwd=None):
    e = dict(os.environ)
    for k in list(e):
        if k.startswith("TASK_PIPELINE_"):
            del e[k]
    e.update(env or {})
    r = subprocess.run([sys.executable, str(GRAPH), "producer"],
                       capture_output=True, text=True, env=e, cwd=cwd)
    fields = dict(l.split(": ", 1) for l in r.stdout.splitlines() if ": " in l)
    return r.returncode, fields, r.stdout + r.stderr


@case("producer prints every field, and needs no graph to do it")
def _():
    code, f, out = producer()
    assert code == 0, "producer exited %d: %s" % (code, out)
    for k in ("actor", "model", "runtime", "skill", "config", "commit", "trace"):
        assert k in f, "producer omits `%s` — an omitted field is indistinguishable from " \
                       "one that was checked and found empty: %s" % (k, out)


@case("an unresolved field says WHY it is unavailable, never blank and never absent")
def _():
    code, f, out = producer()
    for k, v in f.items():
        assert v.strip(), "producer printed `%s` with an empty value" % k
        if v.startswith("unavailable"):
            assert ":" in v[len("unavailable"):], (
                "`%s: %s` says unavailable and not why — the reason is what tells an "
                "operator whether it is wirable" % (k, v))


@case("the harness's values are passed through when it sets them")
def _():
    code, f, out = producer(env={"TASK_PIPELINE_ACTOR": "coding-agent",
                                 "TASK_PIPELINE_TRACE": "trace://run/1842"})
    assert f["actor"] == "coding-agent", f
    assert f["trace"] == "trace://run/1842", f


@case("commit resolves inside a checkout and says so outside one")
def _():
    code, f, out = producer(cwd=str(ROOT))
    assert re.match(r"^[0-9a-f]{40}$", f["commit"]), "commit inside a checkout: %r" % f["commit"]
    code, f2, out2 = producer(cwd=residue.workspace("graph"))
    assert f2["commit"].startswith("unavailable"), (
        "outside a checkout `commit` must say unavailable, not invent one: %r" % f2["commit"])


@case("config is a digest of the project's pipeline.json, and it moves when the file does")
def _():
    d = residue.workspace("graph")
    cfg = pathlib.Path(d) / "pipeline.json"
    cfg.write_text('{"stages": []}')
    _, a, _ = producer(cwd=d)
    cfg.write_text('{"stages": [], "run": {}}')
    _, b, _ = producer(cwd=d)
    assert a["config"] != b["config"], "the digest did not move when pipeline.json did"
    assert re.match(r"^sha256:[0-9a-f]{12,}$", a["config"]), a["config"]


@case("producer names no vendor model id of its own")
def _():
    src = GRAPH.read_text()
    for bad in ("claude-3", "claude-opus", "claude-sonnet", "gpt-4", "gemini-"):
        assert bad not in src, "graph.py hardcodes a vendor model id: %s" % bad


@case("the output is deterministic — the same environment gives the same block")
def _():
    _, a, _ = producer(cwd=str(ROOT))
    _, b, _ = producer(cwd=str(ROOT))
    assert a == b, "the producer block flickers: %s vs %s" % (a, b)


@case("without a plugin manifest the skill version says unavailable rather than guessing")
def _():
    # The branch `validate.py` cannot observe, because this repository always has the
    # manifest. Copy the bundle alone — which is exactly what a plain-skill install is —
    # and the version must say why it is absent instead of inventing one.
    d = residue.workspace("graph")
    bundle = pathlib.Path(d) / "task-pipeline"
    shutil.copytree(ROOT / "plugins/task-pipeline/skills/task-pipeline", bundle)
    lone = bundle / "scripts" / "graph.py"
    r = subprocess.run([sys.executable, str(lone), "producer"],
                       capture_output=True, text=True, cwd=d)
    f = dict(l.split(": ", 1) for l in r.stdout.splitlines() if ": " in l)
    assert r.returncode == 0, r.stdout + r.stderr
    assert f["skill"].startswith("unavailable"), (
        "a plain-skill install invented a version instead of saying it has none: %r"
        % f["skill"])
    assert "plugin manifest" in f["skill"], f["skill"]


# --- B-093: two runnable nodes, one mutable target ---------------------------------------
#
# `references/planning.md` states the rule with the right teeth — *«distinct is not the same
# as independent; the check is what they touch, never what they are called»* — and it lived
# entirely in the markdown plan. The role-agent design replaces the plan with `graph.json`
# as the thing that decides what runs next, and the node had no field for what it touches.
# So `frontier()` ranked by `blocked_by` alone and could hand two agents two runnable nodes
# that write the same file, and nothing could even report it.

def _touch_node(nid, touches, **kw):
    n = node(nid, **kw)
    n["touches"] = touches
    return n


@case("two runnable nodes sharing a touched target are named on stderr")
def _():
    g2 = g([_touch_node("N-001", ["src/export.ts"]), _touch_node("N-002", ["src/export.ts"])])
    code, out = run(g2, "next")
    assert code == 0, out
    assert "N-001" in out and "N-002" in out, out
    assert "src/export.ts" in out, "the shared target is not named: %s" % out


@case("the collision goes to stderr and never into the frontier rows")
def _():
    d = residue.workspace("graph")
    p = pathlib.Path(d) / "graph.json"
    p.write_text(json.dumps(g([_touch_node("N-001", ["a.ts"]), _touch_node("N-002", ["a.ts"])])))
    r = subprocess.run([sys.executable, str(GRAPH), "next", "--graph", str(p)],
                       capture_output=True, text=True)
    rows = [l for l in r.stdout.splitlines() if l.strip()]
    assert len(rows) == 2, ("the frontier print is the one line paid for on every iteration "
                            "of every loop, so a warning may not enter it: %r" % r.stdout)
    for l in rows:
        assert l.split()[0].startswith("N-"), l
    assert "a.ts" in r.stderr, "the collision is not on stderr: %r" % r.stderr


@case("disjoint targets raise nothing")
def _():
    g2 = g([_touch_node("N-001", ["a.ts"]), _touch_node("N-002", ["b.ts"])])
    code, out = run(g2, "next")
    assert code == 0 and "collision" not in out.lower(), out


@case("nodes that cannot run at once do not collide")
def _():
    # N-002 waits on N-001, so they never hold the file at the same time. Reporting them
    # would be a warning nobody can act on, which is how a warning becomes noise.
    g2 = g([_touch_node("N-001", ["a.ts"]),
            _touch_node("N-002", ["a.ts"], blocked=["N-001"])])
    code, out = run(g2, "next")
    assert code == 0, out
    assert "collision" not in out.lower(), "a sequential pair was reported: %s" % out


@case("a frontier whose nodes declare no targets says so — silence is not 'no collision'")
def _():
    g2 = g([node("N-001"), node("N-002")])
    code, out = run(g2, "next")
    assert code == 0, out
    low = out.lower()
    assert "undeclared" in low or "declare no" in low, (
        "two runnable nodes with no `touches` produce no warning and no disclosure, so a "
        "quiet run reads as a checked one — the same shape `doctrine` refuses to print 0 "
        "for: %s" % out)


@case("a partially-declared frontier discloses how many said nothing")
def _():
    g2 = g([_touch_node("N-001", ["a.ts"]), node("N-002"), node("N-003")])
    code, out = run(g2, "next")
    assert code == 0, out
    assert "2" in out, "the count of undeclared nodes is not reported: %s" % out


@case("the schema binds `touches` — non-empty unique strings")
def _():
    try:
        import jsonschema
    except ImportError:
        skipped.append("the `touches` schema rule")
        return
    schema = json.loads((ROOT / "plugins/task-pipeline/skills/task-pipeline"
                              / "graph.schema.json").read_text())
    ok = g([_touch_node("N-001", ["src/a.ts", "docs/DECISIONS.md"])])
    jsonschema.validate(ok, schema)
    for bad in ([""], ["   "], ["a", "a"], "a-string-not-a-list"):
        doc = g([_touch_node("N-001", bad)])
        try:
            jsonschema.validate(doc, schema)
        except jsonschema.ValidationError:
            continue
        raise AssertionError("the schema accepts touches=%r" % (bad,))


@case("add --touches writes what the node will mutate")
def _():
    p = written(g([node("N-001", serves="REQ-001")]))
    code, out = run_at(p, "add", "--title", "t", "--owner", "implementer", "--serves",
                       "REQ-001", "--check", "npm test", "--why", "found mid-run",
                       "--touches", "src/a.ts", "--touches", "src/b.ts")
    assert code == 0, out
    assert json.loads(p.read_text())["nodes"][1]["touches"] == ["src/a.ts", "src/b.ts"], \
        json.loads(p.read_text())["nodes"][1]


# --- T-5: `close` consumes a verdict and re-plans -----------------------------------------
#
# `verdict_violations()` had no CLI verb, so the gate the module docstring calls *the thing
# `close` consumes* was reachable only from this file. And `agents/verifier.md` told an agent
# to run `graph.py close` — shipped doctrine pointing at an absence, the same class as B-080.

def full_verdict(node="N-001", **over):
    v = {"node": node,
         "done": ["the thing was built"],
         "not_done": [],
         "not_verified": [],
         "blockers": [],
         "replan": {"possible": True, "add": [], "park": [], "why": ""},
         "evidence": ["npm test → PASS: 3 cases"]}
    v.update(over)
    return v


def close_at(path, v, *extra):
    d = pathlib.Path(path).parent
    vp = d / "verdict.json"
    vp.write_text(json.dumps(v))
    return run_at(path, "close", "--verdict", str(vp), *extra)


@case("close marks the node done and records the evidence")
def _():
    p = written(g([node("N-001", serves="REQ-001"), node("N-002", serves="REQ-001")]))
    code, out = close_at(p, full_verdict())
    assert code == 0, "a well-formed verdict was refused: %s" % out
    n = json.loads(p.read_text())["nodes"][0]
    assert n["status"] == "done", n
    assert any("npm test" in e for e in n["evidence"]), n


@case("close STAMPS the commit — the verifier never supplies it")
def _():
    # An agent cannot claim the wrong tree if it is never the one naming it.
    p = written(g([node("N-001", serves="REQ-001")]))
    code, out = close_at(p, full_verdict())
    assert code == 0, out
    n = json.loads(p.read_text())["nodes"][0]
    stamped = [e for e in n["evidence"] if re.search(r"\bobserved at\b", e)]
    assert stamped, "close recorded no commit stamp: %s" % n["evidence"]
    assert re.search(r"[0-9a-f]{7,40}|unavailable", stamped[0]), stamped[0]


@case("a verdict omitting `not_verified` is refused — all seven keys")
def _():
    p = written(g([node("N-001", serves="REQ-001")]))
    v = full_verdict()
    del v["not_verified"]
    code, out = close_at(p, v)
    assert code == 1, "a six-key verdict was accepted: %s" % out
    assert "not_verified" in out, out
    assert json.loads(p.read_text())["nodes"][0]["status"] == "pending", "it closed anyway"


@case("done with empty evidence is refused, and nothing is written")
def _():
    p = written(g([node("N-001", serves="REQ-001")]))
    before = p.read_bytes()
    code, out = close_at(p, full_verdict(evidence=[]))
    assert code == 1, out
    assert p.read_bytes() == before, "a refused close wrote to the file"


@case("replan.add appends the nodes the verifier asked for")
def _():
    p = written(g([node("N-001", serves="REQ-001")]))
    v = full_verdict(replan={"possible": True, "why": "the reader found a gap",
                        "add": [{"title": "close the gap", "owner": "implementer",
                                 "serves": "REQ-001", "check": "npm test"}],
                        "park": []})
    code, out = close_at(p, v)
    assert code == 0, out
    nodes = json.loads(p.read_text())["nodes"]
    assert len(nodes) == 2, nodes
    assert nodes[1]["title"] == "close the gap", nodes[1]
    assert nodes[1]["status"] == "pending", nodes[1]


@case("replan.park parks the nodes it names, carrying the verdict's why")
def _():
    p = written(g([node("N-001", serves="REQ-001"), node("N-002", serves="REQ-001")]))
    v = full_verdict(replan={"possible": True, "why": "N-002 serves module 2", "add": [],
                        "park": ["N-002"]})
    code, out = close_at(p, v)
    assert code == 0, out
    n2 = json.loads(p.read_text())["nodes"][1]
    assert n2["status"] == "parked", n2
    assert "module 2" in n2.get("parked_reason", ""), n2


@case("replan.possible false stops, and prints the verdict's own why")
def _():
    p = written(g([node("N-001", serves="REQ-001"), node("N-002", serves="REQ-001")]))
    v = full_verdict(replan={"possible": False, "why": "the operator must choose a price", "add": [], "park": []})
    code, out = close_at(p, v)
    assert code == 1, "a stop must not exit 0 — the loop would carry on: %s" % out
    assert "choose a price" in out, "the printed reason is not the verdict's own: %s" % out
    assert json.loads(p.read_text())["nodes"][0]["status"] == "done", (
        "the node it closed must still close — the stop is about what comes NEXT")


@case("close prints the goal and the new frontier count")
def _():
    p = written(g([node("N-001", serves="REQ-001"), node("N-002", serves="REQ-001")],
                  goal="the loop advances without a human"))
    code, out = close_at(p, full_verdict())
    assert code == 0, out
    assert "without a human" in out, "the goal is not printed: %s" % out
    assert re.search(r"frontier[^\n]*\b1\b", out), "the new frontier count is not printed: %s" % out


@case("close records a revision carrying the verdict's why")
def _():
    p = written(g([node("N-001", serves="REQ-001")]))
    close_at(p, full_verdict(replan={"possible": True, "why": "nothing further needed", "add": [], "park": []}))
    rev = json.loads(p.read_text()).get("revisions") or []
    assert any(r["verb"] == "close" and r["node"] == "N-001" for r in rev), rev


@case("close refuses a node that is not runnable, and says why")
def _():
    p = written(g([node("N-001", serves="REQ-001"),
                   node("N-002", serves="REQ-001", blocked=["N-001"])]))
    code, out = close_at(p, full_verdict(node="N-002"))
    assert code == 1, "a blocked node was closed: %s" % out
    assert "N-001" in out, "the refusal does not name what it waits on: %s" % out


@case("the graph after a close still validates")
def _():
    p = written(g([node("N-001", serves="REQ-001"), node("N-002", serves="REQ-001")]))
    close_at(p, full_verdict(replan={"possible": True, "why": "w", "add": [], "park": ["N-002"]}))
    code, out = run_at(p, "validate")
    assert code == 0, "close wrote a graph that does not validate: %s" % out


@case("the revision verb set agrees between the script and the schema")
def _():
    # `close` wrote `verb: "close"` while the schema enumerated only add and park, and the
    # fixture asserting *the graph after a close still validates* passed anyway, because
    # `violations()` never reached an enum. Same class as B-084, one field over — so the two
    # homes are compared directly.
    schema = json.loads((ROOT / "plugins/task-pipeline/skills/task-pipeline"
                              / "graph.schema.json").read_text())
    declared = set(schema["definitions"]["revision"]["properties"]["verb"]["enum"])
    sys.path.insert(0, str(GRAPH.parent))
    import importlib
    mod = importlib.reload(importlib.import_module("graph"))
    assert declared == mod.REVISION_VERBS, (
        "the schema enumerates %s and the script knows %s" % (sorted(declared),
                                                              sorted(mod.REVISION_VERBS)))


@case("a close writes a graph its own schema accepts — checked with jsonschema")
def _():
    try:
        import jsonschema
    except ImportError:
        skipped.append("the post-close schema cross-check")
        return
    schema = json.loads((ROOT / "plugins/task-pipeline/skills/task-pipeline"
                              / "graph.schema.json").read_text())
    p = written(g([node("N-001", serves="REQ-001"), node("N-002", serves="REQ-001")]))
    code, out = close_at(p, full_verdict(replan={"possible": True, "why": "w", "add": [
        {"title": "found", "owner": "implementer", "serves": "REQ-001",
         "check": "npm test"}], "park": ["N-002"]}))
    assert code == 0, out
    jsonschema.validate(json.loads(p.read_text()), schema)


# --- B-080: a node says how it will be closed, and the doctrine reads a field that exists --
#
# `agents/verifier.md` told the verifier to run *«the checks the task named. Not a check you
# invented, and not `npm test` alone if the task named something narrower»* — while the node
# had no field in which a task could name one. So the instruction pointed at an absence and
# left the verifier exactly the two options that same paragraph forbids. The contradiction
# shipped in two files on one day; nothing compared them, because a sentence with no field
# name in it resolves against nothing a guard can look up.
#
# R-008 — the shapes the defect takes, enumerated before the fix. «Cannot say how it will be
# closed» has five: the field absent; the field blank; the field whitespace; the field
# carrying a line break, which is two commands pretending to be one gate; and the field
# present on a node the schema never binds, which is the shape the `parked` exemption could
# have opened. Each has a fixture.

@case("a node the verifier will close must name its `check`, and the refusal names the node")
def _():
    g2 = g([node("N-001", check=None)])
    code, out = run(g2, "validate")
    assert code == 1, "a node that cannot say how it closes passed validate: %s" % out
    assert "N-001" in out and "check" in out, (
        "the refusal does not name the node and the field: %s" % out)


@case("a blank or whitespace `check` is refused AT RUNTIME, not only by the shipped schema")
def _():
    # `minLength: 1` counts a space — the gap this repository has now found on three
    # separate fields. The runtime strips, so both shapes are one refusal here.
    for bad in ("", "   ", "\t"):
        g2 = g([node("N-001", check=bad)])
        code, out = run(g2, "validate")
        assert code == 1, "check=%r passed validate: %s" % (bad, out)


@case("a line break in a `check` is refused — two commands cannot be one completion test")
def _():
    g2 = g([node("N-001", check="npm test\nrm -rf /")])
    code, out = run(g2, "validate")
    assert code == 1, "a two-command check passed validate: %s" % out
    assert "N-001" in out, out


@case("a parked node needs no `check` — the one node nobody will close")
def _():
    g2 = g([{"id": "N-001", "title": "t", "owner": "ui", "status": "parked",
             "blocked_by": [], "serves": "REQ-001",
             "parked_reason": "serves module 2, not this release"}])
    code, out = run(g2, "validate")
    assert code == 0, ("a parked node was required to name a check it will never run — a "
                       "placeholder there is the confidence-without-correctness this schema "
                       "refuses everywhere else: %s" % out)


@case("a park does not remove what the node said it would run")
def _():
    p = written(g([node("N-001", check="python3 test/graph_test.py")]))
    code, out = run_at(p, "park", "N-001", "--reason", "the operator must choose a price")
    assert code == 0, out
    n = json.loads(p.read_text())["nodes"][0]
    assert n.get("check") == "python3 test/graph_test.py", (
        "parking dropped the node's own completion test: %s" % n)


@case("the schema refuses a node with no `check` where one is owed")
def _():
    try:
        import jsonschema
    except ImportError:
        skipped.append("the `check` schema rule")
        return
    schema = json.loads((ROOT / "plugins/task-pipeline/skills/task-pipeline"
                              / "graph.schema.json").read_text())
    bad = g([node("N-001", check=None)])
    try:
        jsonschema.validate(bad, schema)
    except jsonschema.ValidationError:
        return
    raise AssertionError("a node with no `check` satisfies the schema — B-080 would then rest "
                         "entirely on `graph.py` behaving, which is what `done → evidence` "
                         "stopped doing once already")


@case("the schema accepts a parked node with no `check` — the exemption is stated, not assumed")
def _():
    try:
        import jsonschema
    except ImportError:
        skipped.append("the parked `check` exemption")
        return
    schema = json.loads((ROOT / "plugins/task-pipeline/skills/task-pipeline"
                              / "graph.schema.json").read_text())
    ok = g([{"id": "N-001", "title": "t", "owner": "ui", "status": "parked",
             "blocked_by": [], "serves": "REQ-001", "parked_reason": "serves module 2"}])
    jsonschema.validate(ok, schema)


@case("the `check` pattern REFUSES whitespace — measured, not read")
def _():
    # A pattern being present is not a pattern doing anything: `^.*$` is a pattern and it
    # accepts the empty string. This runs the regex the schema actually ships.
    schema = json.loads((ROOT / "plugins/task-pipeline/skills/task-pipeline"
                              / "graph.schema.json").read_text())
    pat = schema["definitions"]["node"]["properties"]["check"].get("pattern")
    assert pat, "node.check declares no `pattern` — `minLength: 1` counts a space"
    rx = re.compile(pat)
    assert not rx.search("") and not rx.search("   "), (
        "node.check's pattern %r accepts whitespace" % pat)
    assert rx.search("npm test"), "node.check's pattern %r rejects a real command" % pat


@case("add requires --check, and refuses a blank one")
def _():
    p = written(g([node("N-001")]))
    code, out = run_at(p, "add", "--title", "t", "--owner", "implementer",
                       "--serves", "REQ-001", "--why", "a fixture")
    assert code == 2, "add without --check is a usage error: got %d — %s" % (code, out)
    code, out = run_at(p, "add", "--title", "t", "--owner", "implementer", "--serves",
                       "REQ-001", "--check", "   ", "--why", "a fixture")
    assert code == 1, "a blank --check was accepted: %s" % out
    assert len(json.loads(p.read_text())["nodes"]) == 1, "it was written anyway"


@case("add writes the check on the node, and the graph still validates")
def _():
    p = written(g([node("N-001")]))
    code, out = run_at(p, "add", "--title", "t", "--owner", "implementer", "--serves",
                       "REQ-001", "--check", "python3 test/negatives.py -k b080",
                       "--why", "the audit found it")
    assert code == 0, out
    assert json.loads(p.read_text())["nodes"][1]["check"] == \
        "python3 test/negatives.py -k b080", json.loads(p.read_text())["nodes"][1]
    assert run_at(p, "validate")[0] == 0, "add wrote a graph that does not validate"


@case("a verdict whose replan.add names no check is refused, and nothing is written")
def _():
    p = written(g([node("N-001", serves="REQ-001")]))
    before = p.read_bytes()
    v = full_verdict(replan={"possible": True, "why": "the reader found a gap",
                             "add": [{"title": "close the gap", "owner": "implementer",
                                      "serves": "REQ-001"}], "park": []})
    code, out = close_at(p, v)
    assert code == 1, "a replanned node with no completion test was written: %s" % out
    assert "check" in out, "the refusal does not name the key: %s" % out
    assert p.read_bytes() == before, (
        "the close wrote before refusing — the refusal has to land in the verdict gate, or "
        "one missing field aborts a whole close after the node was already marked done")


@case("close writes the replanned node with its own check")
def _():
    p = written(g([node("N-001", serves="REQ-001")]))
    v = full_verdict(replan={"possible": True, "why": "the reader found a gap",
                             "add": [{"title": "close the gap", "owner": "implementer",
                                      "serves": "REQ-001",
                                      "check": "python3 test/graph_test.py"}], "park": []})
    code, out = close_at(p, v)
    assert code == 0, out
    n = json.loads(p.read_text())["nodes"][1]
    assert n["check"] == "python3 test/graph_test.py", n
    assert run_at(p, "validate")[0] == 0, "close wrote a graph that does not validate"


@case("the verifier is told to run a field the node ACTUALLY carries — B-080's own shape")
def _():
    # The defect was not a missing field, it was two files disagreeing with nobody
    # comparing them. So the comparison is the fixture: whatever `agents/verifier.md`
    # tells the verifier to read has to be a property `graph.schema.json` declares.
    txt = (ROOT / "plugins/task-pipeline/agents/verifier.md").read_text()
    schema = json.loads((ROOT / "plugins/task-pipeline/skills/task-pipeline"
                              / "graph.schema.json").read_text())
    props = set(schema["definitions"]["node"]["properties"])
    assert "check" in props, "the schema's node declares no `check`"
    named = set(re.findall(r"the node's `([a-z_]+)`", txt))
    assert named, ("agents/verifier.md names no node field in the form ``the node's `x``` — "
                   "an instruction with no field in it resolves against nothing, which is "
                   "exactly how B-080 shipped")
    unknown = sorted(named - props)
    assert not unknown, ("agents/verifier.md tells the verifier to read %s, which the node "
                         "does not carry — shipped doctrine pointing at an absence is the "
                         "defect this fixture exists for" % unknown)
    assert "check" in named, ("agents/verifier.md does not tell the verifier to read the "
                              "node's `check` — the field exists and the doctrine has to "
                              "name it, or the instruction is back to naming nothing")


@case("the fieldless phrasing is gone — «the checks the task named» named no field")
def _():
    txt = _flat((ROOT / "plugins/task-pipeline/agents/verifier.md").read_text())
    for bad in ("run the checks the task named", "the check the task named"):
        assert bad not in txt.lower(), (
            "agents/verifier.md still says %r — the sentence B-080 filed, which points at a "
            "field rather than naming one" % bad)


@case("every node in the shipped example that will be closed names its check")
def _():
    ex = json.loads((ROOT / "plugins/task-pipeline/skills/task-pipeline"
                          / "graph.example.json").read_text())
    for n in ex["nodes"]:
        if n.get("status") == "parked":
            assert "check" not in n, ("the example's parked node names a check it will never "
                                      "run — the example has to DEMONSTRATE the exemption, "
                                      "not merely permit it: %s" % n["id"])
        else:
            assert (n.get("check") or "").strip(), (
                "%s in graph.example.json names no check — the example is what every project "
                "copies the shape from" % n["id"])
    assert run(ex, "validate")[0] == 0, "the example no longer validates"


# --- certification: three tiers, one node ------------------------------------
#
# `certify` is a gate in FRONT of `close`, so these fixtures prove two different
# things and both matter: that a malformed or contradictory tier report is refused
# by name, and that a certification which passes hands `close` a verdict `close`
# itself accepts. The second is the one a unit test of either half would miss.


def tier(t, verdict="pass", node="N-001", scope=("read src/x.py:10-40",),
         confirms=("the requirement holds",), findings=(),
         evidence=("ran the check: 1 passed",), not_examined=(), drop=None):
    """One tier report. `drop` removes a key, which is the only way to test absence."""
    r = {"node": node, "tier": t, "verdict": verdict, "scope": list(scope),
         "confirms": list(confirms), "findings": list(findings),
         "evidence": list(evidence), "not_examined": list(not_examined)}
    if drop:
        r.pop(drop)
    return r


def breaks(check="pytest tests/test_x.py -q"):
    return {"what": "the caller still expects the old return", "where": "api/x.py:44",
            "severity": "breaks", "fix": "update the caller", "check": check}


def risk():
    return {"what": "one caller has no test", "where": "jobs/y.py:19",
            "severity": "risk", "fix": "add one", "check": "pytest tests/test_y.py -q"}


def certify(graph, reports, *extra, workdir=None):
    """Write a graph and its tier reports to one directory and run `certify`.

    Returns (code, output, workdir) so a second round can run against the SAME
    directory — which is the only way to prove the round count accumulates rather
    than being recomputed from nothing each time.
    """
    d = workdir or residue.workspace("graph")
    gp = pathlib.Path(d) / "graph.json"
    if graph is not None:
        gp.write_text(json.dumps(graph))
    paths = []
    for i, r in enumerate(reports):
        tp = pathlib.Path(d) / ("tier%d.json" % i)
        tp.write_text(json.dumps(r))
        paths.append(str(tp))
    argv = [sys.executable, str(GRAPH), "certify", "--node", "N-001"]
    for tp in paths:
        argv += ["--tier", tp]
    argv += list(extra) + ["--graph", str(gp)]
    r = subprocess.run(argv, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr), d


def three(**kw):
    """The three passing reports — the shape every fixture below deviates from."""
    return [tier("unit", **kw), tier("seam", **kw), tier("product", **kw)]


ONE = g([node("N-001")])


@case("certify: three passing tiers write a verdict close accepts")
def _():
    code, out, d = certify(ONE, three())
    assert code == 0, out
    vp = pathlib.Path(d) / "verdict-N-001.json"
    assert vp.exists(), "no verdict was written: " + out
    v = json.loads(vp.read_text())
    # The mapping, field by field. A verdict that merely validates is not the
    # claim -- the claim is that each tier's field lands where it means the same.
    assert len(v["done"]) == 3, v["done"]
    assert v["not_done"] == [], v["not_done"]
    assert all(e.split(":")[0] in ("unit", "seam", "product") for e in v["evidence"]), v
    r = subprocess.run([sys.executable, str(GRAPH), "close", "--verdict", str(vp),
                        "--graph", str(pathlib.Path(d) / "graph.json")],
                       capture_output=True, text=True)
    assert r.returncode == 0, "close refused the verdict certify assembled: " + \
        r.stdout + r.stderr


@case("certify: not_examined becomes not_verified, a risk becomes a survivable blocker")
def _():
    reports = three()
    reports[1]["not_examined"] = ["the broker integration test"]
    reports[1]["findings"] = [risk()]
    code, out, d = certify(ONE, reports)
    assert code == 0, out
    v = json.loads((pathlib.Path(d) / "verdict-N-001.json").read_text())
    assert any("broker" in x for x in v["not_verified"]), v["not_verified"]
    assert len(v["blockers"]) == 1 and v["blockers"][0]["can_continue_around"] is True, v


@case("certify: a tier passing on an empty scope is refused as a rubber stamp")
def _():
    reports = three()
    reports[0]["scope"] = []
    code, out, _ = certify(ONE, reports)
    assert code != 0 and "rubber stamp" in out, out


@case("certify: a tier passing with empty evidence is refused")
def _():
    reports = three()
    reports[2]["evidence"] = []
    code, out, _ = certify(ONE, reports)
    assert code != 0 and "empty `evidence`" in out, out


@case("certify: a pass carrying a `breaks` finding is a contradiction, refused")
def _():
    reports = three()
    reports[0]["findings"] = [breaks()]
    code, out, _ = certify(ONE, reports)
    assert code != 0 and "cannot both be true" in out, out


@case("certify: a fail naming no `breaks` finding is refused")
def _():
    reports = three()
    reports[1].update(verdict="fail", confirms=[], findings=[risk()])
    code, out, _ = certify(ONE, reports)
    assert code != 0 and "does not say what broke" in out, out


@case("certify: a `breaks` finding with no check is refused — it becomes a node")
def _():
    reports = three()
    reports[1].update(verdict="fail", confirms=[], findings=[breaks(check="  ")])
    code, out, _ = certify(ONE, reports)
    assert code != 0 and "names no `check`" in out, out


@case("certify: a report missing one of the eight keys is refused, and the key is named")
def _():
    for key in ("node", "tier", "verdict", "scope", "confirms", "findings",
                "evidence", "not_examined"):
        reports = three()
        reports[0] = tier("unit", drop=key)
        code, out, _ = certify(ONE, reports)
        assert code != 0 and ("has no `%s`" % key) in out, (key, out)


@case("certify: a third verdict value is refused — no maybe")
def _():
    reports = three()
    reports[0]["verdict"] = "partial"
    code, out, _ = certify(ONE, reports)
    assert code != 0 and "must be `pass` or `fail`" in out, out


@case("certify: two readings at one distance leave another unread, refused")
def _():
    code, out, _ = certify(ONE, [tier("unit"), tier("unit"), tier("product")])
    assert code != 0 and "second `unit` report" in out, out


@case("certify: a missing tier is refused and named")
def _():
    code, out, _ = certify(ONE, [tier("unit"), tier("seam")])
    assert code != 0 and "`product`" in out, out


@case("certify: a report about another node is not evidence about this one")
def _():
    reports = three()
    reports[0]["node"] = "N-009"
    code, out, _ = certify(ONE, reports)
    assert code != 0 and "about another node" in out, out


@case("certify: a report citing another tier's verdict was not written blind")
def _():
    reports = three()
    reports[2]["confirms"] = ["as the seam tier passed, the docs hold"]
    code, out, _ = certify(ONE, reports)
    assert code != 0 and "cites another tier" in out, out


@case("certify: a failing tier exits 1, prints the fix and its check, and the node stays open")
def _():
    reports = three()
    reports[1].update(verdict="fail", confirms=[], findings=[breaks()])
    code, out, d = certify(ONE, reports)
    assert code == 1, out
    assert "update the caller" in out and "pytest tests/test_x.py" in out, out
    n = json.loads((pathlib.Path(d) / "graph.json").read_text())["nodes"][0]
    assert n["status"] == "pending", n
    assert n["certification"]["round"] == 1, n["certification"]
    assert n["certification"]["tiers"]["seam"] == "fail", n["certification"]
    assert not (pathlib.Path(d) / "verdict-N-001.json").exists(), \
        "a failing certification wrote a verdict"


@case("certify: the round accumulates across attempts, so churn is countable")
def _():
    failing = three()
    failing[1].update(verdict="fail", confirms=[], findings=[breaks()])
    code, out, d = certify(ONE, failing)
    assert code == 1, out
    code, out, d = certify(None, failing, workdir=d)
    assert code == 1, out
    n = json.loads((pathlib.Path(d) / "graph.json").read_text())["nodes"][0]
    assert n["certification"]["round"] == 2, n["certification"]
    assert len(n["certification"]["history"]) == 2, n["certification"]


@case("certify: at the ceiling the output names the tier that failed every round")
def _():
    failing = three()
    failing[1].update(verdict="fail", confirms=[], findings=[breaks()])
    code, out, d = certify(ONE, failing, "--ceiling", "2")
    assert code == 1 and "ceiling" not in out, "round 1 is not at a ceiling of 2: " + out
    code, out, d = certify(None, failing, "--ceiling", "2", workdir=d)
    assert code == 1, out
    assert "`seam`" in out and "failed every round" in out, out
    assert "loop-guard" in out, "the ceiling does not point at the doctrine: " + out


@case("certify: churn across levels is reported as such, not as one stuck tier")
def _():
    a = three(); a[0].update(verdict="fail", confirms=[], findings=[breaks()])
    b = three(); b[1].update(verdict="fail", confirms=[], findings=[breaks()])
    code, out, d = certify(ONE, a, "--ceiling", "2")
    assert code == 1, out
    code, out, d = certify(None, b, "--ceiling", "2", workdir=d)
    assert code == 1, out
    assert "churn across levels" in out, out


@case("certify: a node that is already done cannot be certified again")
def _():
    done = g([node("N-001", status="done", evidence=["it was closed"])])
    code, out, _ = certify(done, three())
    assert code != 0 and "already done" in out, out


@case("certify: a node whose blocker is open certifies nothing")
def _():
    blocked = g([node("N-000"), node("N-001", blocked=["N-000"])])
    code, out, _ = certify(blocked, three())
    assert code != 0 and "waits on N-000" in out, out


@case("certify: the graph still validates after a round is recorded on a node")
def _():
    code, out, d = certify(ONE, three())
    assert code == 0, out
    gp = pathlib.Path(d) / "graph.json"
    r = subprocess.run([sys.executable, str(GRAPH), "validate", "--graph", str(gp)],
                       capture_output=True, text=True)
    assert r.returncode == 0, "the certification field broke the graph: " + \
        r.stdout + r.stderr

# Before the verdict, and the position matters: `report()` is idempotent (the atexit
# registration would find `_reported` already set), so a case defined BELOW this line
# is created after the accounting and never appears in it. Found by planting a failing
# case at the end of the file and watching the report say `left nothing` while the
# suite exited 1. Every case in this file is above.
residue.report()

print("\nPASS: graph.py — %d cases%s"
      % (cases, (" (%d unlooked)" % len(skipped)) if skipped else ""))


if failures:
    print("\n%d failure(s) out of %d cases" % (len(failures), cases))
    sys.exit(1)
if skipped:
    print("\nunlooked: %d — %s" % (len(skipped), "; ".join(skipped)))
