#!/usr/bin/env python3
"""Wave mode's inventory, assigned by tables rather than by hand (`references/waves.md`).

Wave 0 ends with one machine-readable inventory (`templates/inventory.schema.json`,
inventory/1) and every item on a canvas node. Seven hundred hand-edited rows cannot be
reviewed; a table and a re-run can. This script is that re-run:

    waves.py merge DIR [--glob PATTERN ...] [--out FILE]
        every survey output in DIR (a JSON array of items, or an inventory/1 document)
        merged into one inventory/1 document; each item keeps `source_file`. A file that is
        not an item list is skipped and named. Refuses (exit 2, every reason) an item that
        fails inventory/1 and an id that appears twice; a refused merge writes nothing.
    waves.py assign --inventory FILE --modules FILE [--plan FILE] [--write]
        writes `module` from the module table ({module: [ids]}) and, with a plan, `node`
        (the nodes whose `closes` name the item, in wave order), `wave` (the last of their
        waves) and `release` (`this`, or `program` when a node is carried). A carried item
        no node closes goes to `program`; a terminal one stays off the canvas. Prints the
        counts. Exit 1 when an item lands on no module, or an open item on no node.
    waves.py count --inventory FILE [--by FIELD ...]
        counts per field (default: module, wave, release, kind, severity).
    waves.py validate --inventory FILE [--modules FILE] [--plan FILE]
        exit 2 on a schema error; exit 1 when an item is on no module or on two, when its
        recorded module, node or wave is not what the tables now say, or when an open item
        lands nowhere. 0 otherwise.
    waves.py sync-graph --plan FILE --graph FILE --why TEXT [--only-present]
        writes each plan node's wave and risk class onto the work graph with graph.py's own
        lock, loader and revision log (one `wave` or `risk` revision per change; lowering a
        risk class is refused without --lower-why), applying every move together and
        judging the end state once with graph.py's order rule, so a valid re-cut is never
        refused halfway and a refused one writes nothing. Plan nodes the graph lacks are named and exit 1, unless --only-present
        (a plan that spans several repositories' graphs).

**The plan** is any JSON whose `nodes` list `{id, wave, closes}` — a work graph that carries
`closes` on its nodes is one, and so is a short hand-written table. A node may carry
`graph_id`, the work-graph id it is built as, where the canvas id is not graph.py's `N-001`. A node whose wave is
not an integer is carried to a later release (`release: program`). Both tables are
described in `templates/inventory.schema.json` (`$defs.modules`, `$defs.plan`).

**Deterministic.** The same inputs give the same bytes: items keep their merge order, nodes
are listed in (wave, id) order, counts are sorted. A re-cut is a diff to a table and a
re-run, which a reviewer can read.

Exit codes: 0 done; 1 an item lands nowhere, or the tables and the inventory disagree, or a
graph move was refused; 2 a schema error, a table error (an id on two modules), usage, or an
unreadable file. Stdlib only (`references/portability.md`).
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import pathlib
import re
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
SCHEMA = HERE.parent / "templates" / "inventory.schema.json"
GRAPH_PY = HERE / "graph.py"
REQUIRED = ("id", "title", "area", "kind", "severity", "evidence", "proposed_fix")
OPTIONAL = ("status", "source", "source_file", "repo", "module", "node", "wave", "release",
            "register_id", "blocked_by", "closable_in_one_pass", "needs_operator", "notes")
SEVERITY = ("critical", "high", "medium", "low", "info")
STATUS = ("open", "changed", "closed", "fixed", "fixed-elsewhere", "duplicate", "moved", "stale",
          "not-reproduced", "carried")
OPEN = ("open", "changed")
ID = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,63}$")
KIND = re.compile(r"^[a-z][a-z0-9-]*$")
EXT = re.compile(r"^x-[a-z0-9-]+$")
DEFAULT_COUNTS = ("module", "wave", "release", "kind", "severity")


class Fail(Exception):
    def __init__(self, code: int, reasons: list[str]):
        super().__init__("\n".join(reasons))
        self.code, self.reasons = code, reasons


# ---------------------------------------------------------------------------- inventory/1


def item_errors(x: object) -> list[str]:
    """Every reason inventory/1 refuses one item (empty = valid)."""
    if not isinstance(x, dict):
        return ["an item is a JSON object"]
    iid = x.get("id", "?")
    errs = [f"{iid}: missing `{k}`" for k in REQUIRED if k not in x]
    errs += [f"{iid}: unknown field `{k}` — inventory/1 names its fields, and a project's own go "
             "under an `x-` prefix" for k in x if k not in REQUIRED + OPTIONAL and not EXT.match(k)]
    if "id" in x and (not isinstance(x["id"], str) or not ID.match(x["id"])):
        errs.append(f"{iid}: `id` is not an id (a letter, then letters, digits, . _ -)")
    for k, least in (("title", 3), ("area", 1), ("proposed_fix", 1)):
        if k in x and (not isinstance(x[k], str) or len(x[k].strip()) < least):
            errs.append(f"{iid}: `{k}` is shorter than {least} character{'s' if least > 1 else ''}")
    if "kind" in x and (not isinstance(x["kind"], str) or not KIND.match(x["kind"])):
        errs.append(f"{iid}: `kind` is not a lowercase word")
    if "severity" in x and x["severity"] not in SEVERITY:
        errs.append(f"{iid}: `severity` {x['severity']!r} is not one of {', '.join(SEVERITY)}")
    ev = x.get("evidence")
    if "evidence" in x and not ((isinstance(ev, str) and len(ev.strip()) >= 3) or (
            isinstance(ev, list) and ev and all(isinstance(e, str) and len(e.strip()) >= 3 for e in ev))):
        errs.append(f"{iid}: `evidence` is empty — a finding is a fact with a receipt")
    if "status" in x and x["status"] not in STATUS:
        errs.append(f"{iid}: `status` {x['status']!r} is not one of {', '.join(STATUS)}")
    if "node" in x and (not isinstance(x["node"], list) or not all(isinstance(n, str) for n in x["node"])):
        errs.append(f"{iid}: `node` is not a list of node ids")
    if "wave" in x and x["wave"] is not None and (not isinstance(x["wave"], int)
                                                  or isinstance(x["wave"], bool) or x["wave"] < 1):
        errs.append(f"{iid}: `wave` is not an integer from 1, or null")
    if "release" in x and x["release"] not in ("this", "program"):
        errs.append(f"{iid}: `release` is neither this nor program")
    for k in ("closable_in_one_pass", "needs_operator"):
        if k in x and not isinstance(x[k], bool):
            errs.append(f"{iid}: `{k}` is not a boolean")
    return errs


def schema_errors(items: list) -> list[str]:
    """inventory/1 itself, applied where `jsonschema` is installed. `item_errors` is the
    hand copy every install has; test/waves_test.py holds the two to one verdict."""
    try:
        import jsonschema
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    except (ImportError, OSError, ValueError):
        return []
    v = jsonschema.Draft202012Validator(schema)
    out = []
    for e in sorted(v.iter_errors({"schema": "inventory/1", "items": items}), key=lambda e: list(e.path)):
        where = "/".join(str(x) for x in e.path) or "(top)"
        out.append(f"schema: {where}: {e.message[:200]}")
    return out


def read_json(path: pathlib.Path, what: str):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise Fail(2, [f"{what} {path} cannot be read ({type(exc).__name__})"])


def items_of(doc) -> list | None:
    if isinstance(doc, list) and all(isinstance(x, dict) for x in doc):
        return doc
    if isinstance(doc, dict) and doc.get("schema") == "inventory/1" and isinstance(doc.get("items"), list):
        return doc["items"]
    return None


def load_inventory(path: pathlib.Path) -> tuple[dict, list[dict]]:
    doc = read_json(path, "the inventory")
    items = items_of(doc)
    if items is None:
        raise Fail(2, [f"{path} is neither an inventory/1 document nor an array of items"])
    errs = [e for x in items for e in item_errors(x)]
    errs += schema_errors(items)
    ids = [x.get("id") for x in items]
    errs += [f"{i}: appears {ids.count(i)} times — an id is unique across the inventory"
             for i in sorted({i for i in ids if ids.count(i) > 1}, key=str)]
    if errs:
        raise Fail(2, errs)
    out = doc if isinstance(doc, dict) else {"schema": "inventory/1", "items": items}
    return out, items


def write_json(path: pathlib.Path, doc) -> None:
    path = pathlib.Path(os.path.realpath(path))
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".inventory-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------- tables


def load_modules(path: pathlib.Path) -> dict[str, str]:
    table = read_json(path, "the module table")
    if not isinstance(table, dict) or not all(isinstance(v, list) for v in table.values()):
        raise Fail(2, [f"{path}: the module table is {{module: [item ids]}}"])
    owner: dict[str, str] = {}
    errs = []
    for mod in sorted(table):
        for i in table[mod]:
            if i in owner and owner[i] != mod:
                errs.append(f"{i}: claimed by both {owner[i]} and {mod} — an item sits in exactly "
                            "one module")
            owner.setdefault(i, mod)
    if errs:
        raise Fail(2, errs)
    return owner


def load_plan(path: pathlib.Path) -> list[dict]:
    doc = read_json(path, "the plan")
    nodes = doc.get("nodes") if isinstance(doc, dict) else None
    if isinstance(nodes, dict):
        nodes = [dict(v, id=k) for k, v in nodes.items()]
    if not isinstance(nodes, list) or not all(isinstance(n, dict) and isinstance(n.get("id"), str)
                                              for n in nodes):
        raise Fail(2, [f"{path}: a plan is an object whose `nodes` list {{id, wave, closes}}"])
    return nodes


def _wave(n: dict) -> int | None:
    w = n.get("wave")
    return w if isinstance(w, int) and not isinstance(w, bool) and w >= 1 else None


def placement(nodes: list[dict]) -> dict[str, dict]:
    """item id -> {node, wave, release}, from the plan's `closes`."""
    by_item: dict[str, list[dict]] = {}
    for n in nodes:
        for i in n.get("closes") or []:
            by_item.setdefault(i, []).append(n)
    out = {}
    for i, ns in by_item.items():
        ns = sorted(ns, key=lambda n: (_wave(n) is None, _wave(n) or 0, n["id"]))
        waves = [_wave(n) for n in ns]
        carried = any(w is None for w in waves)
        out[i] = {"node": list(dict.fromkeys(n["id"] for n in ns)),
                  "wave": None if carried else max(waves),
                  "release": "program" if carried else "this"}
    return out


def _status(x: dict) -> str:
    return x.get("status", "open")


def _carried(x: dict) -> bool:
    """The ONE predicate for an item that goes to the program without a node. `assign`
    writes `release: program` from it and `validate` excuses an item by it — the same
    test in both, so a hand-written `release: program` on an open item excuses nothing."""
    return _status(x) == "carried"


def _needs_node(x: dict) -> bool:
    return _status(x) in OPEN


def counts(items: list[dict], fields) -> dict:
    out = {}
    for f in fields:
        c: dict[str, int] = {}
        for x in items:
            v = x.get(f)
            k = "none" if v is None else (",".join(v) if isinstance(v, list) else str(v))
            c[k] = c.get(k, 0) + 1
        out[f"by_{f}"] = dict(sorted(c.items(), key=lambda kv: (kv[0] == "none", _natural(kv[0]))))
    return out


def _natural(s: str):
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", s)]


# ---------------------------------------------------------------------------- verbs


def cmd_merge(a) -> int:
    src = pathlib.Path(a.dir)
    if not src.is_dir():
        raise Fail(2, [f"{src} is not a directory"])
    globs = a.glob or ["*.json"]
    files = sorted(p for p in src.iterdir() if p.is_file() and any(fnmatch.fnmatch(p.name, g) for g in globs))
    items, errs, skipped = [], [], []
    for f in files:
        got = items_of(read_json(f, "the survey output"))
        if got is None:
            skipped.append(f.name)
            continue
        for x in got:
            x = dict(x)
            x.setdefault("source_file", f.name)
            errs += [f"{f.name}: {e}" for e in item_errors(x)]
            items.append(x)
    seen: dict[str, list[str]] = {}
    for x in items:
        seen.setdefault(x.get("id"), []).append(x.get("source_file"))
    errs += [f"{i}: appears twice — in {', '.join(fs)}; an id is unique across the inventory"
             for i, fs in seen.items() if len(fs) > 1]
    for s in skipped:
        print(f"waves: skipped {s} — not an item list", file=sys.stderr)
    if errs:
        raise Fail(2, errs)
    doc = {"schema": "inventory/1", "items": items}
    if a.out:
        write_json(pathlib.Path(a.out), doc)
        print(json.dumps({"items": len(items), "files": len(files) - len(skipped),
                          "skipped": skipped, **counts(items, ("kind", "severity"))}, ensure_ascii=False))
    else:
        print(json.dumps(doc, ensure_ascii=False, indent=1))
    return 0


def _assign(items: list[dict], owner: dict[str, str], nodes: list[dict] | None) -> tuple[list, list, list]:
    unclaimed, unplaced, out = [], [], []
    place = placement(nodes) if nodes is not None else {}
    for x in items:
        x = dict(x)
        mod = owner.get(x["id"])
        if mod is None:
            unclaimed.append(x["id"])
            x.pop("module", None)
        else:
            x["module"] = mod
        if nodes is not None:
            for k in ("node", "wave", "release"):
                x.pop(k, None)
            p = place.get(x["id"])
            if p:
                x.update(node=p["node"], wave=p["wave"], release=p["release"])
            elif _carried(x):
                x.update(wave=None, release="program")
            elif _needs_node(x):
                unplaced.append(x["id"])
        out.append(x)
    return out, unclaimed, unplaced


def cmd_assign(a) -> int:
    path = pathlib.Path(a.inventory)
    doc, items = load_inventory(path)
    owner = load_modules(pathlib.Path(a.modules))
    nodes = load_plan(pathlib.Path(a.plan)) if a.plan else None
    new, unclaimed, unplaced = _assign(items, owner, nodes)
    if a.write:
        write_json(path, {**doc, "items": new})
    fields = ("module", "wave", "release") if nodes is not None else ("module",)
    print(json.dumps({"items": len(new), **counts(new, fields), "unclaimed": unclaimed,
                      "unplaced": unplaced}, ensure_ascii=False))
    for i in unclaimed:
        print(f"waves: {i} lands on no module — the canvas has a gap, or the module table a "
              "missing row", file=sys.stderr)
    for i in unplaced:
        print(f"waves: {i} is open and no node closes it — put it on a node, carry it "
              "(`status: carried`), or close it with its receipt", file=sys.stderr)
    return 1 if unclaimed or unplaced else 0


def cmd_count(a) -> int:
    _, items = load_inventory(pathlib.Path(a.inventory))
    print(json.dumps({"items": len(items), **counts(items, a.by or DEFAULT_COUNTS)}, ensure_ascii=False))
    return 0


def cmd_validate(a) -> int:
    _, items = load_inventory(pathlib.Path(a.inventory))
    problems = []
    known = {x["id"] for x in items}
    if a.modules:
        owner = load_modules(pathlib.Path(a.modules))
        problems += [f"{i}: the module table puts it on {owner[i]}, and the inventory has no "
                     "such item" for i in sorted(set(owner) - known)]
        for x in items:
            mod = owner.get(x["id"])
            if mod is None:
                problems.append(f"{x['id']}: on no module — every item lands in exactly one")
            elif "module" in x and x["module"] != mod:
                problems.append(f"{x['id']}: recorded on {x['module']}, the table says {mod} — re-run assign")
    if a.plan:
        plan_nodes = load_plan(pathlib.Path(a.plan))
        problems += [f"{i}: node {n['id']} closes it, and the inventory has no such item"
                     for n in plan_nodes for i in (n.get("closes") or []) if i not in known]
        place = placement(plan_nodes)
        for x in items:
            p = place.get(x["id"])
            if p:
                for k in ("node", "wave", "release"):
                    if k in x and x[k] != p[k]:
                        problems.append(f"{x['id']}: `{k}` is {x[k]!r}, the plan now says {p[k]!r} — "
                                        "re-run assign")
            elif "node" in x and x["node"]:
                problems.append(f"{x['id']}: recorded on {', '.join(x['node'])}, which no longer "
                                "close it")
            elif _needs_node(x):
                problems.append(f"{x['id']}: open, and no node closes it — it lands nowhere "
                                "(carry it with `status: carried`, or put it on a node)")
            elif _carried(x) and x.get("release") != "program":
                problems.append(f"{x['id']}: carried, and its release is not program — re-run assign")
    for p in problems:
        print(f"waves: {p}", file=sys.stderr)
    print(json.dumps({"items": len(items), "problems": len(problems)}))
    return 1 if problems else 0


def _graph_module():
    """graph.py, imported: its lock, its loader, its revision log and its order rule."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("tp_graph", GRAPH_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cmd_sync_graph(a) -> int:
    why = " ".join((a.why or "").split())
    if not why:
        raise Fail(2, ["--why needs a reason: each move enters the graph's revision log"])
    nodes = load_plan(pathlib.Path(a.plan))
    gpath = os.path.realpath(a.graph)
    G = _graph_module()
    # ALL MOVES AT ONCE, JUDGED ONCE. Applied one at a time through `graph.py wave`, a valid
    # re-cut could be refused halfway: moving A(w1)->B(w2) to A:3, B:4 passes through A:3,
    # B:2, which breaks the order rule although the end state keeps it. So every move is
    # applied in memory, under graph.py's own lock, each with its revision entry, and
    # graph.py's `violations` judges the end state once. A refusal writes nothing.
    with G.held(gpath):
        try:
            graph = G.shape(G.load(gpath), gpath)
        except SystemExit as exc:
            raise Fail(2, [f"the work graph {gpath} cannot be read ({exc})"])
        before = G.violations(graph)
        if before:
            raise Fail(1, [f"{gpath} was already invalid — nothing was written:"] + before)
        current = {n.get("id"): n for n in graph.get("nodes") or [] if isinstance(n, dict)}

        def gid(n: dict) -> str:  # a canvas id need not be graph.py's `N-001` shape
            return n.get("graph_id") or n["id"]

        absent = [gid(n) for n in nodes if _wave(n) is not None and gid(n) not in current]
        moves = sorted(((gid(n), _wave(n)) for n in nodes if _wave(n) is not None
                        and gid(n) in current and current[gid(n)].get("wave") != _wave(n)
                        and current[gid(n)].get("status") != "done"))
        # RISK, from the plan: the class `close` enforces (graph.py `owed_shortfall`). Nothing
        # else writes it onto a graph node, so without this the gate fired only on a
        # hand-edited graph. A lowering owes its own reason — a class is never lowered to save
        # time (references/iteration.md) — so it is refused without --lower-why.
        rank = {"R1": 1, "R2": 2, "R3": 3}
        risk_moves, lowered = [], []
        for n in nodes:
            r, nid = n.get("risk"), gid(n)
            if r not in rank or nid not in current or current[nid].get("risk") == r:
                continue
            was = current[nid].get("risk")
            if was in rank and rank[r] < rank[was]:
                lowered.append(f"{nid}: {was} → {r}")
            risk_moves.append((nid, was, r))
        lower_why = " ".join((a.lower_why or "").split())
        if lowered and not lower_why:
            raise Fail(1, ["lowering a risk class needs its own reason (--lower-why) — nothing "
                           "was written: " + ", ".join(lowered)])
        lines = []
        for nid, was, r in sorted(risk_moves):
            current[nid]["risk"] = r
            low = was in rank and rank[r] < rank[was]
            G.revise(graph, "risk", nid, f"{why}; lowered: {lower_why}" if low else why)
            lines.append(f"{nid}: risk {was or 'none'} → {r}")
        for nid, wave in moves:
            old = current[nid].get("wave")
            current[nid]["wave"] = wave
            G.revise(graph, "wave", nid, why)
            lines.append(f"{nid}: wave {old if old is not None else 'none'} → {wave}: {why}")
        bad = G.violations(graph)
        if bad:
            raise Fail(1, ["the re-cut would break the graph — nothing was written:"] + bad)
        if moves or risk_moves:
            G.save(gpath, graph)
    for ln in lines:
        print(ln)
    print(f"waves: {len(moves)} moved · {len(risk_moves)} risk class(es) set · graph.py's order "
          "rule holds on the result")
    if absent and not a.only_present:
        for nid in absent:
            print(f"waves: {nid} is in the plan and not in {pathlib.Path(gpath).name} — add it, or "
                  "pass --only-present for a plan that spans several graphs", file=sys.stderr)
        return 1
    return 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="waves.py", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("merge", help="merge survey outputs into one inventory/1 document")
    m.add_argument("dir")
    m.add_argument("--glob", action="append", default=[], help="file pattern; repeatable (default *.json)")
    m.add_argument("--out", help="write the inventory here (default: print it)")
    asg = sub.add_parser("assign", help="write module, node, wave and release from the tables")
    asg.add_argument("--inventory", required=True)
    asg.add_argument("--modules", required=True)
    asg.add_argument("--plan")
    asg.add_argument("--write", action="store_true", help="write the inventory back (default: counts only)")
    c = sub.add_parser("count", help="counts per field")
    c.add_argument("--inventory", required=True)
    c.add_argument("--by", action="append", default=[])
    v = sub.add_parser("validate", help="schema, then every item on one module and one placement")
    v.add_argument("--inventory", required=True)
    v.add_argument("--modules")
    v.add_argument("--plan")
    s = sub.add_parser("sync-graph", help="write the plan's waves onto the work graph via graph.py wave")
    s.add_argument("--plan", required=True)
    s.add_argument("--graph", required=True)
    s.add_argument("--why", required=True)
    s.add_argument("--lower-why", help="the reason a node's risk class is lowered; without it "
                                        "a lowering is refused")
    s.add_argument("--only-present", action="store_true",
                   help="ignore plan nodes this graph does not hold")
    a = p.parse_args(argv)
    verbs = {"merge": cmd_merge, "assign": cmd_assign, "count": cmd_count, "validate": cmd_validate,
             "sync-graph": cmd_sync_graph}
    try:
        return verbs[a.cmd](a)
    except Fail as exc:
        for r in exc.reasons:
            print(f"waves: {r}", file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
