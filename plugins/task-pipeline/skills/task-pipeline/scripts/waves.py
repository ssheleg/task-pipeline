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
        counts. Exit 1 without writing when an item lands on no module, or an open item on no node.
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
        refused halfway and a refused one writes nothing. Plan nodes the graph lacks are named
        and exit 1 before any write, unless --only-present
        (a plan that spans several repositories' graphs).
    waves.py finish --inventory FILE --max-rounds N --max-releases M (--rounds K | --ledger RUN.md)
                    --checks K/M --artefact NAME@SHA [--releases R] [--operator-go]
                    [--clean-rounds 1|2] [--max-agents 2]
        the finish-line verdict (`references/finish-line.md`) from the triaged items, and the
        finish block printed. Only `triage: blocking` items count, less those closed as
        duplicate, stale or not-reproduced; deferred and noise never change the verdict. The
        round count is explicit: --rounds, or the ledger's `round: <N> — <reading> — new
        blocking <k>` lines, whose counts must match the inventory. Exit 0 done (the last
        --clean-rounds rounds found no new blocking item: one by default, two when the
        iteration carries an R3 or flagship node; none is open, --checks is all green, and the rounds
        are within --max-rounds or --operator-go is passed); 5 the budget reached before done
        (rounds at --max-rounds, releases at --max-releases with a blocker open, or done past
        the round budget without --operator-go); 6 diverging (the blocking count did not fall
        from one round that found some to the next, or it did not fall and the last round's
        self-inflicted >= new, from round 2 on); 3 continue (including no --checks); 1
        malformed (a schema error, a blocking item without `test` or `round`, B3 with
        base_repro yes, a round past the rounds run, no round count, a ledger that disagrees,
        --max-rounds below 2, an artefact that is not NAME@SHA). Since 1.100.0 the ledger's
        `agents: <N> — <k>` lines (the most sub-agents running at once in round N) are read
        too: a round over --max-agents (run.finish.maxAgents, 2 by default) is a budget
        verdict, exit 5, unless --operator-go.

**The plan** is any JSON whose `nodes` list `{id, wave, closes}` — a work graph that carries
`closes` on its nodes is one, and so is a short hand-written table. A node may carry
`graph_id`, the work-graph id it is built as, where the canvas id is not graph.py's `N-001`.
Both node ids and effective graph targets must be unique. A node whose wave is
not an integer is carried to a later release (`release: program`). Both tables are
described in `templates/inventory.schema.json` (`$defs.modules`, `$defs.plan`).

**Deterministic.** The same inputs give the same bytes: items keep their merge order, nodes
are listed in (wave, id) order, counts are sorted. A re-cut is a diff to a table and a
re-run, which a reviewer can read.

Exit codes (every verb but `finish`, whose own are above): 0 done; 1 an item lands nowhere, or the tables and the inventory disagree, or a
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
            "register_id", "blocked_by", "closable_in_one_pass", "needs_operator", "notes",
            "triage", "test", "round", "base_repro", "blast", "rung")
SEVERITY = ("critical", "high", "medium", "low", "info")
STATUS = ("open", "changed", "closed", "fixed", "fixed-elsewhere", "duplicate", "moved", "stale",
          "not-reproduced", "carried")
OPEN = ("open", "changed")
# The finish line's vocabulary (references/finish-line.md → Triage at discovery). The
# validator holds these to the doctrine, the run-ledger grammar and inventory/1's enums.
TRIAGE = ("blocking", "deferred", "noise")
TESTS = ("B1", "B2", "B3", "B4")
BASE_REPRO = ("yes", "no", "n/a")
RUNGS = ("I1", "I2", "I3", "I4", "I5")
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
    if "triage" in x and x["triage"] not in TRIAGE:
        errs.append(f"{iid}: `triage` {x['triage']!r} is not one of {', '.join(TRIAGE)}")
    if "test" in x and x["test"] not in TESTS:
        errs.append(f"{iid}: `test` {x['test']!r} is not one of {', '.join(TESTS)}")
    if "round" in x and not _posint(x["round"]):
        errs.append(f"{iid}: `round` is not an integer from 1")
    if "base_repro" in x and x["base_repro"] not in BASE_REPRO:
        errs.append(f"{iid}: `base_repro` {x['base_repro']!r} is not one of {', '.join(BASE_REPRO)}")
    if "blast" in x and not (_posint(x["blast"]) and x["blast"] <= 3):
        errs.append(f"{iid}: `blast` is not 1, 2 or 3")
    if "rung" in x and x["rung"] not in RUNGS:
        errs.append(f"{iid}: `rung` {x['rung']!r} is not one of {', '.join(RUNGS)}")
    if x.get("triage") == "blocking":
        errs += [f"{iid}: blocking without `{k}` — a blocking finding names the B test that "
                 "matched and the round that found it" for k in ("test", "round") if k not in x]
        if x.get("test") == "B3" and x.get("base_repro") == "yes":
            errs.append(f"{iid}: B3 says it passes at Base, and `base_repro: yes` says it fails "
                        "there — one of the two is wrong")
    elif "test" in x:
        errs.append(f"{iid}: `test` on an item that is not blocking — a B test is what makes a "
                    "finding blocking; without one it is deferred or noise")
    return errs


def _posint(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 1


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
    # The declared values, checked rather than skipped: a risk of `r1`, `high` or null was
    # silently ignored and the sync exited 0, leaving the node with no class to enforce.
    errs = []
    ids, targets = set(), set()
    for n in nodes:
        nid = n["id"]
        target = n.get("graph_id", nid)
        if not nid or nid in ids:
            errs.append(f"{path}: repeated or empty node id {nid!r}")
        ids.add(nid)
        if not isinstance(target, str) or not target:
            errs.append(f"{path}: node {nid}: graph_id must be a non-empty string")
        elif target in targets:
            errs.append(f"{path}: repeated effective graph target {target!r}")
        else:
            targets.add(target)
        if "risk" in n and n["risk"] not in ("R1", "R2", "R3"):
            errs.append(f"{path}: node {n['id']}: risk {n['risk']!r} is not R1, R2 or R3")
        if "wave" in n and n["wave"] is not None and _wave(n) is None:
            errs.append(f"{path}: node {n['id']}: wave {n['wave']!r} is not an integer from 1, or null")
        if "closes" in n and not (isinstance(n["closes"], list) and all(isinstance(i, str) for i in n["closes"])):
            errs.append(f"{path}: node {n['id']}: closes is not a list of item ids")
        if "release" in n and n["release"] not in ("this", "program"):
            errs.append(f"{path}: node {n['id']}: release {n['release']!r} is neither this nor program")
    if errs:
        raise Fail(2, errs)
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
    if a.write and not (unclaimed or unplaced):
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

        absent = [gid(n) for n in nodes if (_wave(n) is not None or "risk" in n)
                  and gid(n) not in current]
        if absent and not a.only_present:
            raise Fail(1, [f"{nid} is in the plan and not in {pathlib.Path(gpath).name} — "
                           "nothing was written; add it, or pass --only-present for a plan "
                           "that spans several graphs" for nid in absent])
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
    return 0


# ---------------------------------------------------------------------------- the finish line

# A blocking item closed as one of these was never a blocker: it counts in no round.
NOT_COUNTED = ("duplicate", "stale", "not-reproduced")
ROUND_LINE = re.compile(r"^round:\s*(\d+)\s*[—-]\s*(.*?)\s*[—-]\s*new blocking\s*(\d+)\s*$")
AGENTS_LINE = re.compile(r"^agents:\s*(\d+)\s*[—-]\s*(\d+)\b")
ARTEFACT = re.compile(r"^[^@\s]+@[0-9a-f]{7,40}$")


def _priority(x: dict):
    """Top priority first: the impact rung, then blast, then severity, then the id. Where an
    item was found is not an input — a fresh finding is not next because it is fresh."""
    rung = RUNGS.index(x["rung"]) + 1 if x.get("rung") in RUNGS else 0
    return (-rung, -(x.get("blast") or 0), SEVERITY.index(x["severity"]), _natural(x["id"]))


def _board_id(x: dict) -> str:
    return x.get("register_id") or x["id"]


def ledger_rounds(path: pathlib.Path) -> dict[int, int]:
    """{round: new blocking} from the run ledger's `round:` lines (templates/run.md)."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise Fail(1, [f"the run ledger {path} cannot be read ({type(exc).__name__})"])
    out, errs = {}, []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.startswith("round:"):
            continue
        m = ROUND_LINE.match(line.strip())
        if not m:
            errs.append(f"{path}:{n}: not `round: <N> — <reading> — new blocking <k>`")
            continue
        r = int(m[1])
        if r < 1 or r in out:
            errs.append(f"{path}:{n}: round {r} is below 1 or written twice")
        out[r] = int(m[3])
    if out and sorted(out) != list(range(1, max(out) + 1)):
        errs.append(f"{path}: rounds {sorted(out)} are not 1..{max(out)} — a round line is missing")
    if errs:
        raise Fail(1, errs)
    return out


def ledger_agents(path: pathlib.Path) -> dict[int, int]:
    """{round: most sub-agents at once} from the run ledger's `agents:` lines (since 1.100.0).
    A round written twice keeps its larger count: the budget is about the peak."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise Fail(1, [f"the run ledger {path} cannot be read ({type(exc).__name__})"])
    out, errs = {}, []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.startswith("agents:"):
            continue
        m = AGENTS_LINE.match(line.strip())
        if not m:
            errs.append(f"{path}:{n}: not `agents: <N> — <k>`")
            continue
        out[int(m[1])] = max(out.get(int(m[1]), 0), int(m[2]))
    if errs:
        raise Fail(1, errs)
    return out


def finish_verdict(items: list[dict], rounds: int, max_rounds: int, max_releases: int,
                   releases: int, checks: tuple[int, int] | None,
                   operator_go: bool = False, clean_rounds: int = 1) -> tuple[int, str, dict]:
    """(exit code, word, facts) — the finish line computed from the triaged items alone.
    Deferred and noise items are counted for the block and never read for the verdict."""
    triaged = [x for x in items if "triage" in x]
    late = [f"{x['id']}: found in round {x['round']}, and only {rounds} round(s) ran"
            for x in triaged if _posint(x.get("round")) and x["round"] > rounds]
    if late:
        raise Fail(1, late)
    blocking = [x for x in triaged if x["triage"] == "blocking" and _status(x) not in NOT_COUNTED]
    new = [sum(1 for x in blocking if x["round"] == r) for r in range(1, rounds + 1)]
    selfinf = sum(1 for x in blocking if x["round"] == rounds and x.get("base_repro") == "no")
    open_b = [x for x in blocking if _needs_node(x)]
    facts = {"rounds": rounds, "new": new, "open": open_b, "fixed": len(blocking) - len(open_b),
             "self_inflicted": selfinf}
    # One clean round ends an iteration; two only where it carries an R3 or flagship node
    # (`--clean-rounds 2`). Two for everything was the loop the 2026-10-20 cost audit measured.
    clean = rounds >= clean_rounds and all(n == 0 for n in new[-clean_rounds:]) and not open_b
    green = checks is not None and checks[0] == checks[1]
    if clean and green:
        if rounds <= max_rounds:
            return 0, "done", facts
        if operator_go:
            return 0, "done", dict(facts, why=f"past budget — rounds {rounds}/{max_rounds} on the "
                                              "operator's go")
        return 5, "budget", dict(facts, why=f"past budget — operator's go required: done at round "
                                            f"{rounds}/{max_rounds}")
    if rounds >= max_rounds:
        owed = (f"{len(open_b)} blocker(s) open" if open_b else
                "exit checks not supplied" if checks is None else
                "exit checks not all green" if not green else "a clean round still owed")
        return 5, "budget", dict(facts, why=f"rounds {rounds}/{max_rounds} reached before done — {owed}")
    if open_b and releases >= max_releases:
        return 5, "budget", dict(facts, why=f"releases {releases}/{max_releases} reached before "
                                            f"done — {len(open_b)} blocker(s) open")
    if rounds >= 2 and new[-1] >= new[-2] > 0:
        return 6, "blocked", dict(facts, why=f"diverging — new blocking {new[-2]} → {new[-1]} "
                                             "did not fall; run the loop guard's break protocol")
    if rounds >= 2 and new[-1] >= new[-2] and selfinf and selfinf >= new[-1] - selfinf:
        return 6, "blocked", dict(facts, why=f"diverging — round {rounds}: {selfinf} self-inflicted "
                                             f"≥ {new[-1] - selfinf} new, and the count did not "
                                             "fall; run the loop guard's break protocol")
    why = (f"{len(open_b)} blocker(s) open" if open_b else
           "exit checks not supplied — pass --checks K/M read on the artefact" if checks is None else
           "exit checks not all green" if not green else
           ("a second round with no new blocking finding is owed" if clean_rounds > 1 else
            "a round with no new blocking finding is owed"))
    return 3, "continue", dict(facts, why=why)


def cmd_finish(a) -> int:
    try:
        _, items = load_inventory(pathlib.Path(a.inventory))
    except Fail as exc:
        raise Fail(1, exc.reasons)  # a malformed inventory is malformed here, never usage
    if a.clean_rounds not in (1, 2):
        raise Fail(1, [f"--clean-rounds {a.clean_rounds} is not 1 or 2"])
    for flag, v, least in (("--max-rounds", a.max_rounds, a.clean_rounds),
                           ("--max-releases", a.max_releases, 1),
                           ("--releases", a.releases, 0), ("--rounds", a.rounds, 0)):
        if v is not None and v < least:
            raise Fail(1, [f"{flag} {v} is below {least}" + (
                f" — done needs {a.clean_rounds} clean rounds, so a smaller budget can never be met"
                if flag == "--max-rounds" else "")])
    # THE ROUND COUNT IS EXPLICIT. A clean round leaves no item, so a count derived from the
    # items can never see the two clean rounds `done` needs: the verdict would stay
    # `continue` for ever. It comes from --rounds or from the ledger's `round:` lines.
    led = ledger_rounds(pathlib.Path(a.ledger)) if a.ledger else None
    if led is not None and not led and a.rounds is None:
        raise Fail(1, [f"{a.ledger} carries no `round:` line and --rounds is absent — the round "
                       "count cannot be read"])
    if led is None and a.rounds is None:
        raise Fail(1, ["the round count is not given — pass --rounds N, or --ledger with the run "
                       "ledger's `round:` lines; clean rounds leave no item to count"])
    rounds = a.rounds if a.rounds is not None else max(led)
    if led and a.rounds is not None and a.rounds != max(led):
        raise Fail(1, [f"--rounds {a.rounds} and the ledger's {max(led)} round(s) disagree"])
    if led:
        counted = {r: sum(1 for x in items if x.get("triage") == "blocking" and x.get("round") == r)
                   for r in led}
        bad = [f"round {r}: the ledger says new blocking {k}, the inventory holds {counted[r]}"
               for r, k in sorted(led.items()) if counted[r] != k]
        if bad:
            raise Fail(1, bad)
    checks = None
    if a.checks:
        m = re.fullmatch(r"(\d+)/(\d+)", a.checks.strip())
        if not m or int(m[1]) > int(m[2]) or int(m[2]) == 0:
            raise Fail(1, [f"--checks {a.checks!r} is not K/M green of M exit checks"])
        checks = (int(m[1]), int(m[2]))
    if a.artefact and not ARTEFACT.match(a.artefact):
        raise Fail(1, [f"--artefact {a.artefact!r} is not NAME@SHA (a commit of 7-40 hex digits)"])
    code, word, f = finish_verdict(items, rounds, a.max_rounds, a.max_releases, a.releases, checks,
                                   a.operator_go, a.clean_rounds)
    # The parallel-agent budget (run.finish.maxAgents): a round that ran more sub-agents at
    # once than the budget allows stops the iteration like any other budget, said with the
    # numbers; the operator's go lifts it, out loud.
    agents = ledger_agents(pathlib.Path(a.ledger)) if a.ledger else {}
    if a.max_agents < 1:
        raise Fail(1, [f"--max-agents {a.max_agents} is below 1"])
    stray = sorted(r for r in agents if r < 1 or r > rounds)
    if stray:
        raise Fail(1, [f"{a.ledger}: an `agents:` line names round {r}, and only rounds 1..{rounds} ran"
                       for r in stray])
    over = sorted((r, k) for r, k in agents.items() if k > a.max_agents)
    named = ", ".join(f"round {r}: {k}/{a.max_agents}" for r, k in over)
    if over and not a.operator_go and code in (0, 3):
        code, word = 5, "budget"
        f = dict(f, why="agents over budget — " + named)
    elif over and a.operator_go and code in (0, 3):
        f = dict(f, why=((f.get("why") + "; ") if f.get("why") else "") + "agents over budget on the operator's go — " + named)
    deferred = sorted((x for x in items if x.get("triage") == "deferred"), key=_priority)
    noise = [x for x in items if x.get("triage") == "noise"]
    risks = [x for x in deferred if x.get("blast") == 3 or x.get("rung") in ("I4", "I5")]
    pool = sorted((x for x in items if x.get("triage") != "blocking" and _needs_node(x)
                   and x.get("triage") != "noise"), key=_priority)
    peak = max(agents.values()) if agents else None
    budget = (f"rounds {f['rounds']}/{a.max_rounds} — releases {a.releases}/{a.max_releases} — agents "
              + (f"{peak}/{a.max_agents}" if peak is not None else f"unrecorded/{a.max_agents}"))
    if word == "continue":
        print(f"next round: {f['rounds'] + 1}/{a.max_rounds} — {f['why']} — {budget}")
    else:
        print(f"finish: {word} — {budget}" + (f" — {f['why']}" if f.get("why") else ""))
    print("  exit checks: " + (f"{checks[0]}/{checks[1]} green on {a.artefact or '<artefact not named>'}"
                               if checks else "not supplied — read them on the artefact (--checks K/M)"))
    print(f"  blocking: {len(f['open'])} open · {f['fixed']} fixed — new per round "
          f"{' · '.join(str(n) for n in f['new']) or 'none'}"
          + (f" — open: {', '.join(x['id'] for x in f['open'])}" if f["open"] else ""))
    top = ", ".join(_board_id(x) for x in deferred[:5]) + (" …" if len(deferred) > 5 else "")
    print(f"  deferred: {len(deferred)}" + (f" → {top}" if deferred else ""))
    print(f"  noise: {len(noise)}")
    print("  known risks: " + (", ".join(_board_id(x) for x in risks) or "none"))
    print("  next: " + (f"{_board_id(pool[0])} (new iteration)" if pool
                         else "highest-priority board row (read the board)"))
    return code


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
    f = sub.add_parser("finish", help="the finish-line verdict from the triaged items, and the block")
    f.add_argument("--inventory", required=True)
    f.add_argument("--max-rounds", type=int, required=True,
                   help="run.finish.maxRounds (default 3, at least --clean-rounds)")
    f.add_argument("--clean-rounds", type=int, default=1,
                   help="run.finish.cleanRounds: clean rounds that end the iteration, 1 by "
                        "default, 2 when it carries an R3 or flagship node")
    f.add_argument("--max-releases", type=int, required=True, help="run.finish.maxReleases (default 2)")
    f.add_argument("--releases", type=int, default=0, help="releases this iteration made so far")
    f.add_argument("--rounds", type=int, help="rounds run, clean ones included")
    f.add_argument("--ledger", help="the run ledger; its `round:` lines are the round count")
    f.add_argument("--operator-go", action="store_true",
                   help="the operator's recorded go for rounds past --max-rounds and sub-agents past "
                        "--max-agents; the block says which budget it lifted")
    f.add_argument("--checks", help="K/M — exit checks green on the artefact")
    f.add_argument("--max-agents", type=int, default=2,
                   help="run.finish.maxAgents: sub-agents running at once in one round (default 2)")
    f.add_argument("--artefact", help="what they ran on, as NAME@SHA")
    a = p.parse_args(argv)
    verbs = {"merge": cmd_merge, "assign": cmd_assign, "count": cmd_count, "validate": cmd_validate,
             "sync-graph": cmd_sync_graph, "finish": cmd_finish}
    try:
        return verbs[a.cmd](a)
    except Fail as exc:
        for r in exc.reasons:
            print(f"waves: {r}", file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
