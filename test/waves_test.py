#!/usr/bin/env python3
"""Wave tooling (`scripts/waves.py`, inventory/1) and the wave templates — stdlib only.

MN §3.2, node M-3. Wave mode prescribed an inventory file, a canvas, a question queue and "a
committed deterministic script" for node and wave assignment, and shipped none of them, so
every run wrote its own. These cases drive the real script as a process over fixtures built
in temp directories:

  * `validate` exits 1 when one module row is removed from the table — an item that lands
    nowhere is a gap in the canvas, never a silent drop — and 0 on the complete table;
  * `merge` reproduces every item of the survey outputs, refuses a repeated id and an item
    without `evidence` (exit 2, every reason named), and skips what is not an item list;
  * `assign` writes `module`, `node`, `wave` and `release` from the two tables, the same bytes
    every run, and prints the counts;
  * `validate --plan` refuses a recorded wave the plan no longer says, and an open item no
    node closes;
  * `sync-graph` moves graph nodes through `graph.py wave`, and `graph.py validate` agrees
    afterwards; a move graph.py refuses is a refusal here too;
  * the templates ship, are listed, and waves.md links the schema instead of a field table.

Run bare: prints PASS and exits non-zero on the first failure.
"""
import atexit
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "plugins" / "task-pipeline" / "skills" / "task-pipeline"
SCRIPT = SKILL / "scripts" / "waves.py"
GRAPH = SKILL / "scripts" / "graph.py"
_TREES = []
atexit.register(lambda: [shutil.rmtree(t, ignore_errors=True) for t in _TREES])
CASES = 0


def ok(cond, what):
    global CASES
    CASES += 1
    if not cond:
        print(f"FAIL: {what}")
        sys.exit(1)


def tree():
    d = pathlib.Path(tempfile.mkdtemp(prefix="tp-waves-"))
    _TREES.append(d)
    return d


def run(*args, cwd=None):
    r = subprocess.run([sys.executable, str(SCRIPT), *args], cwd=cwd, capture_output=True,
                       text=True, timeout=60)
    return r.returncode, r.stdout, r.stderr


def item(i, **kw):
    base = {"id": i, "title": f"item {i}", "area": "core", "kind": "bug", "severity": "medium",
            "evidence": f"src/app.py:{len(i)} — reproduced", "proposed_fix": "fix it"}
    base.update(kw)
    return base


def survey(d):
    """Two survey outputs, a plans file, and one file that is not an item list."""
    raw = d / "raw"
    raw.mkdir()
    (raw / "audit-core.json").write_text(json.dumps(
        [item("COR-001"), item("COR-002", severity="high"), item("COR-003", kind="gap")]))
    (raw / "audit-docs.json").write_text(json.dumps(
        [item("DOC-001", kind="doc-wrong"), item("DOC-002", kind="doc-missing", status="fixed-elsewhere")]))
    (raw / "plans.json").write_text(json.dumps(
        [item("PLN-001", kind="plan", severity="low"), item("PLN-002", kind="plan", status="carried")]))
    (raw / "BRIEF.json").write_text(json.dumps({"not": "items"}))
    modules = {"A-core": ["COR-001", "COR-002", "COR-003"], "B-docs": ["DOC-001", "DOC-002"],
               "C-plans": ["PLN-001", "PLN-002"]}
    (d / "modules.json").write_text(json.dumps(modules, indent=1))
    # Canvas ids need not be graph.py's `N-001` shape: `graph_id` maps one to the other.
    plan = {"nodes": [{"id": "A-1", "graph_id": "N-001", "wave": 1, "closes": ["COR-001", "COR-002"]},
                      {"id": "A-2", "graph_id": "N-002", "wave": 2, "closes": ["COR-002", "COR-003"]},
                      {"id": "B-1", "graph_id": "N-003", "wave": 1, "closes": ["DOC-001"]},
                      {"id": "C-1", "graph_id": "N-004", "wave": 3, "closes": ["PLN-001"]},
                      {"id": "C-9", "wave": None, "closes": [], "release": "program"}]}
    (d / "plan.json").write_text(json.dumps(plan, indent=1))
    return raw


def main():
    d = tree()
    raw = survey(d)
    inv = d / "inventory.json"

    # --- merge: every item, nothing invented, the non-list skipped aloud
    rc, out, err = run("merge", str(raw), "--out", str(inv))
    ok(rc == 0, f"merge exits 0 on clean survey outputs ({rc} {err})")
    doc = json.loads(inv.read_text())
    ok(doc["schema"] == "inventory/1" and len(doc["items"]) == 7, f"merge reproduces 7 items ({len(doc['items'])})")
    ok({x["source_file"] for x in doc["items"]} == {"audit-core.json", "audit-docs.json", "plans.json"},
       "each item names the survey output it came from")
    ok("BRIEF.json" in out + err and "not an item list" in out + err, "a file that is not an item list is skipped aloud")

    bad = tree()
    (bad / "audit-x.json").write_text(json.dumps([item("X-001"), {k: v for k, v in item("X-002").items() if k != "evidence"}]))
    (bad / "audit-y.json").write_text(json.dumps([item("X-001")]))
    rc, out, err = run("merge", str(bad), "--out", str(bad / "inv.json"))
    ok(rc == 2 and "X-002" in err and "evidence" in err and "X-001" in err and "twice" in err,
       f"merge refuses a missing evidence and a repeated id, naming both ({rc} {err!r})")
    ok(not (bad / "inv.json").exists(), "a refused merge writes nothing")

    # --- validate: the module table is the claim
    rc, out, err = run("validate", "--inventory", str(inv), "--modules", str(d / "modules.json"))
    ok(rc == 0, f"validate exits 0 when every item is on exactly one module ({rc} {out} {err})")
    short = json.loads((d / "modules.json").read_text())
    del short["B-docs"]
    (d / "modules-short.json").write_text(json.dumps(short))
    rc, out, err = run("validate", "--inventory", str(inv), "--modules", str(d / "modules-short.json"))
    ok(rc == 1 and "DOC-001" in out + err and "DOC-002" in out + err,
       f"validate exits 1 and names the items when one module row is removed ({rc} {out!r} {err!r})")
    dbl = json.loads((d / "modules.json").read_text())
    dbl["B-docs"].append("COR-001")
    (d / "modules-double.json").write_text(json.dumps(dbl))
    rc, out, err = run("validate", "--inventory", str(inv), "--modules", str(d / "modules-double.json"))
    ok(rc == 2 and "COR-001" in err, "an id claimed by two modules is a table error (exit 2)")

    # --- the schema rejects an item without evidence, in an inventory too
    broken = json.loads(inv.read_text())
    del broken["items"][0]["evidence"]
    (d / "broken.json").write_text(json.dumps(broken))
    rc, out, err = run("validate", "--inventory", str(d / "broken.json"))
    ok(rc == 2 and "evidence" in err, "validate refuses an item without evidence (exit 2)")
    typo = json.loads(inv.read_text())
    typo["items"][0]["evidense"] = "x"
    (d / "typo.json").write_text(json.dumps(typo))
    rc, out, err = run("validate", "--inventory", str(d / "typo.json"))
    ok(rc == 2 and "evidense" in err, "an unknown field is refused by name; x- fields are the extension point")
    ext = json.loads(inv.read_text())
    ext["items"][0]["x-owner-team"] = "core"
    (d / "ext.json").write_text(json.dumps(ext))
    ok(run("validate", "--inventory", str(d / "ext.json"))[0] == 0, "an x- field is accepted")
    bare = d / "bare.json"
    bare.write_text(json.dumps(doc["items"]))
    ok(run("validate", "--inventory", str(bare))[0] == 0, "a bare array of items is read as inventory/1")

    # --- assign: deterministic, counts printed
    rc, out, err = run("assign", "--inventory", str(inv), "--modules", str(d / "modules.json"),
                       "--plan", str(d / "plan.json"), "--write")
    ok(rc == 0, f"assign --write ({rc} {err})")
    first = inv.read_bytes()
    rc, out2, _ = run("assign", "--inventory", str(inv), "--modules", str(d / "modules.json"),
                      "--plan", str(d / "plan.json"), "--write")
    ok(inv.read_bytes() == first and out2 == out, "assign writes the same bytes and counts every run")
    got = {x["id"]: x for x in json.loads(inv.read_text())["items"]}
    ok(got["COR-002"]["node"] == ["A-1", "A-2"] and got["COR-002"]["wave"] == 2
       and got["COR-002"]["release"] == "this", "an item two nodes close takes the later wave")
    ok(got["COR-001"]["module"] == "A-core" and got["COR-001"]["wave"] == 1, "module and wave are written")
    ok(got["PLN-002"]["release"] == "program" and got["PLN-002"].get("wave") is None,
       "a carried item no node closes goes to the program")
    ok("node" not in got["DOC-002"], "a terminal item no node closes stays off the canvas")
    counts = json.loads(out)
    ok(counts["by_wave"] == {"1": 2, "2": 2, "3": 1, "none": 2} and counts["unplaced"] == [],
       f"assign prints the counts per wave ({counts.get('by_wave')})")
    rc, out, _ = run("count", "--inventory", str(inv), "--by", "module", "--by", "release")
    c = json.loads(out)
    ok(rc == 0 and c["by_module"]["A-core"] == 3 and c["by_release"]["program"] == 1, f"count by field ({c})")

    # --- validate --plan: a wave the plan no longer says, an open item nothing closes
    rc, *_ = run("validate", "--inventory", str(inv), "--modules", str(d / "modules.json"),
                 "--plan", str(d / "plan.json"))
    ok(rc == 0, "validate --plan exits 0 on the assigned inventory")
    moved = json.loads((d / "plan.json").read_text())
    moved["nodes"][1]["wave"] = 3
    (d / "plan-moved.json").write_text(json.dumps(moved))
    rc, out, err = run("validate", "--inventory", str(inv), "--plan", str(d / "plan-moved.json"))
    ok(rc == 1 and "COR-002" in out + err, "a recorded wave the plan no longer says is refused (exit 1)")
    gap = json.loads((d / "plan.json").read_text())
    gap["nodes"] = [n for n in gap["nodes"] if n["id"] != "B-1"]
    (d / "plan-gap.json").write_text(json.dumps(gap))
    rc, out, err = run("assign", "--inventory", str(inv), "--modules", str(d / "modules.json"),
                       "--plan", str(d / "plan-gap.json"))
    ok(rc == 1 and "DOC-001" in out + err, "assign exits 1 on an open item no node closes")

    # --- round-1 fixes: one predicate, names unknown ids, title length
    short_title = json.loads(inv.read_text())
    short_title["items"][0]["title"] = "ab"
    (d / "short.json").write_text(json.dumps(short_title))
    rc, _, err = run("validate", "--inventory", str(d / "short.json"))
    ok(rc == 2 and "title" in err, "a title under 3 characters is refused, as the schema says")
    ghost_mod = json.loads((d / "modules.json").read_text())
    ghost_mod["A-core"].append("COR-404")
    (d / "modules-ghost.json").write_text(json.dumps(ghost_mod))
    rc, out, err = run("validate", "--inventory", str(inv), "--modules", str(d / "modules-ghost.json"))
    ok(rc == 1 and "COR-404" in err, "an id the module table names and the inventory lacks is named")
    ghost_plan = json.loads((d / "plan.json").read_text())
    ghost_plan["nodes"][0]["closes"].append("DOC-404")
    (d / "plan-ghost.json").write_text(json.dumps(ghost_plan))
    rc, out, err = run("validate", "--inventory", str(inv), "--plan", str(d / "plan-ghost.json"))
    ok(rc == 1 and "DOC-404" in err, "an id a node closes and the inventory lacks is named")
    escaped = json.loads(inv.read_text())
    for x in escaped["items"]:
        if x["id"] == "DOC-001":
            x.pop("node"); x["wave"] = None; x["release"] = "program"
    (d / "escaped.json").write_text(json.dumps(escaped))
    rc, out, err = run("validate", "--inventory", str(d / "escaped.json"), "--plan", str(d / "plan-gap.json"))
    ok(rc == 1 and "DOC-001" in err,
       "an open item is not excused by release: program — only status: carried is, in validate as in assign")

    # --- sync-graph: through graph.py wave, and graph.py validate agrees
    g = {"goal": "a goal", "requirements": ["REQ-001"], "edges": [
            {"from": "N-001", "to": "N-002", "payload": "the core fix"}],
         "nodes": [
            {"id": "N-001", "title": "t", "owner": "implementer", "status": "pending", "blocked_by": [],
             "serves": "REQ-001", "check": "npm test"},
            {"id": "N-002", "title": "t", "owner": "implementer", "status": "pending", "blocked_by": ["N-001"],
             "serves": "REQ-001", "check": "npm test"},
            {"id": "N-003", "title": "t", "owner": "implementer", "status": "pending", "blocked_by": [],
             "serves": "REQ-001", "check": "npm test"}]}
    gp = d / "graph.json"
    gp.write_text(json.dumps(g))
    rc, out, err = run("sync-graph", "--plan", str(d / "plan.json"), "--graph", str(gp),
                       "--why", "wave plan of the fixture")
    ok(rc == 1 and "N-004" in out + err, f"sync-graph names plan nodes the graph lacks and exits 1 ({rc} {out!r} {err!r})")
    waves = {n["id"]: n.get("wave") for n in json.loads(gp.read_text())["nodes"]}
    ok(waves == {"N-001": 1, "N-002": 2, "N-003": 1}, f"sync-graph wrote every wave it could ({waves})")
    revs = json.loads(gp.read_text()).get("revisions") or []
    ok(len(revs) == 3 and all(r.get("verb") == "wave" for r in revs), "each move is a graph.py revision")
    r = subprocess.run([sys.executable, str(GRAPH), "validate", "--graph", str(gp)], capture_output=True, text=True)
    ok(r.returncode == 0, f"graph.py validate agrees after sync-graph ({r.stdout} {r.stderr})")
    rc, out, err = run("sync-graph", "--plan", str(d / "plan.json"), "--graph", str(gp), "--why", "again",
                       "--only-present")
    ok(rc == 0 and "0 moved" in out, f"a second sync moves nothing ({rc} {out!r})")
    back = json.loads((d / "plan.json").read_text())
    back["nodes"][1]["wave"] = 1
    back["nodes"][0]["wave"] = 2
    (d / "plan-back.json").write_text(json.dumps(back))
    before = gp.read_bytes()
    rc, out, err = run("sync-graph", "--plan", str(d / "plan-back.json"), "--graph", str(gp),
                       "--why", "a re-cut graph.py refuses", "--only-present")
    ok(rc == 1 and "N-001" in err, f"an order-breaking move is refused through graph.py ({rc} {err!r})")
    ok(gp.read_bytes() == before, "a refused sync writes nothing: every move is tried on a copy first")
    r = subprocess.run([sys.executable, str(GRAPH), "validate", "--graph", str(gp)], capture_output=True, text=True)
    ok(r.returncode == 0, "graph.py validate still agrees after a refused sync")

    # --- templates and doctrine
    tpl = SKILL / "templates"
    for name in ("inventory.schema.json", "backlog-sources.schema.json", "canvas.md", "questions.md", "dossier.md"):
        ok((tpl / name).is_file(), f"templates/{name} ships")
        ok(name in (tpl / "README.md").read_text(), f"templates/README.md lists {name}")
    for name in ("inventory.schema.json", "backlog-sources.schema.json"):
        json.loads((tpl / name).read_text())
    waves_md = (SKILL / "references" / "waves.md").read_text()
    ok("templates/inventory.schema.json" in waves_md and "| `release` |" not in waves_md,
       "waves.md links the inventory schema instead of carrying a field table")
    ok("contract is owned by" not in waves_md and "templates/backlog-sources.schema.json" in waves_md,
       "waves.md gives public readers the manifest's shape, not a private owner")
    ok("scripts/waves.py" in waves_md, "waves.md names the script")
    dossier = (tpl / "dossier.md").read_text()
    ok("risk class" in dossier and "per node" in dossier.lower(), "the dossier template puts the risk class on each node")
    try:
        import jsonschema  # optional: the full conformance pass, where installed
    except ImportError:
        jsonschema = None
    if jsonschema:
        sch = json.loads((tpl / "inventory.schema.json").read_text())
        jsonschema.validate(json.loads(inv.read_text()), sch)
        bs = json.loads((tpl / "backlog-sources.schema.json").read_text())
        for ex in bs["examples"]:
            jsonschema.validate(ex, bs)
        bad_bs = {"schema": 1, "repository": "https://github.com/a/b",
                  "sources": [{"path": "docs/B.md", "goal": "reliable-work", "format": "table",
                               "idColumn": "id", "titleColumn": "t"}]}
        try:
            jsonschema.validate(bad_bs, bs)
            ok(False, "a table with neither statusColumn nor defaultStatus is refused by the schema")
        except jsonschema.ValidationError:
            ok(True, "a table with neither statusColumn nor defaultStatus is refused by the schema")
        for bad_path in ("../x.md", ".hidden/x.md", "/abs.md", "a//b.md"):
            src = {"path": bad_path, "goal": "shared-context", "kind": "context"}
            try:
                jsonschema.validate({"schema": 1, "repository": "https://github.com/a/b", "sources": [src]}, bs)
                ok(False, f"backlog-sources refuses the path {bad_path!r}")
            except jsonschema.ValidationError:
                ok(True, f"backlog-sources refuses the path {bad_path!r}")
    else:
        print("note: jsonschema not installed — the schema conformance pass was not run")
    print(f"PASS: waves.py — {CASES} cases")


if __name__ == "__main__":
    main()
