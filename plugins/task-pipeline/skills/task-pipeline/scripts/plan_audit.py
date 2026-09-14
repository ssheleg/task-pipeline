#!/usr/bin/env python3
"""Plan audit — the stage-4 gate that reads the plan the way the NEXT agent will.

Stage 4 already refuses a plan that drops a REQ, carries a placeholder, or draws an
edge that hands nothing over. What it could not refuse until now is the failure the
operator named on 2026-09-13: **an agent that was not there cannot execute a task
whose context lives in the planning conversation.** Agents change between sessions;
whatever a task does not say, the next one re-derives or gets wrong.

So this reads the work graph and asks four questions no other gate asks:

1. **Context** — is every node's packet answerable by a cold reader? The eight
   questions are `context_packets.py`'s, imported rather than re-listed: one home for
   the contract, so the gate cannot drift from the compiler that produces it.
2. **Contradiction** — do two nodes with no ordering between them name the same edit
   target? The parallel-group rule catches the same file inside ONE group; two nodes
   in different groups with no path between them race just as hard, and nothing looked.
3. **Priority** — computed, never declared: how many nodes each one unblocks,
   transitively. A hand-assigned number is an opinion wearing a number's clothes
   (`references/prioritisation.md`); this one is derived from the graph and printed,
   so the order a run takes is a fact the plan states rather than a choice it makes
   silently.
4. **Model** — when the run records a per-stage model map, the map is checked against
   the stages this pipeline has, so a profile naming a stage that does not exist
   fails here instead of at the boundary it was written for.

Exit 0 when the plan can be handed to a stranger, 1 when it cannot, 2 on usage.

    python3 scripts/plan_audit.py [--graph .task-pipeline/graph.json]
                                  [--packets <dir>] [--models <map.json>]
                                  [--json] [--self-test]

Standard library only, like every script in this bundle.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# One home for the cold-reader contract. A second copy of the eight questions is a
# second thing to drift, and this gate exists to catch drift.
from context_packets import COLD_READER_QUESTIONS, leaf_readiness  # noqa: E402

STAGES = tuple(str(i) for i in range(11))
DEFAULT_GRAPH = os.path.join(".task-pipeline", "graph.json")
# A node in one of these states is finished or deliberately out of the run; its packet
# is history, and demanding one would refuse a plan for work nobody will do.
SETTLED = {"done", "parked", "waived", "closed", "superseded"}


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _dependents(nodes):
    """node id → the ids that directly wait on it."""
    out = {n.get("id"): set() for n in nodes}
    for n in nodes:
        for b in n.get("blocked_by") or []:
            if b in out:
                out[b].add(n.get("id"))
    return out


def unblocks(nodes):
    """How many nodes each one unblocks, transitively. The computed priority."""
    dep = _dependents(nodes)
    memo = {}

    def reach(nid, seen):
        if nid in memo:
            return memo[nid]
        if nid in seen:          # a cycle is graph.py's finding, not this one's
            return set()
        acc = set()
        for nxt in dep.get(nid, ()):  # direct dependents first
            acc.add(nxt)
            acc |= reach(nxt, seen | {nid})
        memo[nid] = acc
        return acc

    return {nid: len(reach(nid, set())) for nid in dep}


def _ordered_before(nodes):
    """(a, b) pairs where a is reachable from b or b from a — i.e. ordered."""
    dep = {n.get("id"): set(n.get("blocked_by") or []) for n in nodes}
    ancestors = {}

    def anc(nid, seen):
        if nid in ancestors:
            return ancestors[nid]
        if nid in seen:
            return set()
        acc = set()
        for b in dep.get(nid, ()):
            if b in dep:
                acc.add(b)
                acc |= anc(b, seen | {nid})
        ancestors[nid] = acc
        return acc

    return {nid: anc(nid, set()) for nid in dep}


def edit_targets(packet):
    """What a packet says it will edit or create — the scope a collision is about."""
    scope = (packet or {}).get("source_scope") or {}
    out = set()
    for key in ("edit_targets", "create_targets"):
        for t in scope.get(key) or []:
            if isinstance(t, str):
                out.add(t)
            elif isinstance(t, dict) and t.get("path"):
                out.add(t["path"])
    return out


def collisions(nodes, packets):
    """Two nodes that touch one file with no ordering between them.

    Not the same rule as the parallel-group check in `planning.md`: that one reads a
    group the planner declared, this one reads the GRAPH. Two nodes the planner never
    put in one group, and never connected either, race exactly as hard — and the run
    finds out by losing an edit.
    """
    anc = _ordered_before(nodes)
    ids = [n.get("id") for n in nodes if n.get("id")]
    out = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if b in anc.get(a, ()) or a in anc.get(b, ()):
                continue
            shared = edit_targets(packets.get(a)) & edit_targets(packets.get(b))
            for path in sorted(shared):
                out.append((a, b, path))
    return out


def packets_by_node(directory):
    """Every execution packet under `directory`, keyed by the node it serves.

    A packet names its node in `node` or `parent_node`; one that names neither is
    reported rather than guessed at, because a packet nothing can attach to is
    indistinguishable from a node with no packet — and those two failures have
    different fixes.
    """
    found, orphans = {}, []
    if not directory or not os.path.isdir(directory):
        return found, orphans
    for root, _dirs, files in os.walk(directory):
        for name in sorted(files):
            if not name.endswith(".json"):
                continue
            path = os.path.join(root, name)
            try:
                doc = load_json(path)
            except Exception as e:
                orphans.append((path, f"does not parse ({e})"))
                continue
            if not isinstance(doc, dict):
                orphans.append((path, "is not an object"))
                continue
            nid = doc.get("node") or doc.get("parent_node")
            if not nid:
                orphans.append((path, "names no node (`node` / `parent_node`)"))
                continue
            found[nid] = doc
    return found, orphans


def audit(graph, packets, orphans=(), model_map=None):
    """Every finding, as (kind, node, message). Pure: no I/O, no exit."""
    findings = []
    nodes = [n for n in (graph.get("nodes") or []) if isinstance(n, dict)]
    if not nodes:
        findings.append(("plan", "-", "the graph declares no nodes — a plan with no "
                                      "tasks is not a plan this gate can hand to anyone"))
        return findings
    live = [n for n in nodes if str(n.get("status", "")).lower() not in SETTLED]

    for path, why in orphans:
        findings.append(("packet", "-", f"{path} {why}"))

    for n in live:
        nid = n.get("id") or "?"
        pkt = packets.get(nid)
        if pkt is None:
            findings.append((
                "context", nid,
                "no execution packet — the next agent would start from the title. "
                "Compile one with `context_packets.py compile-leaf`; the eight "
                "questions it must answer are " + ", ".join(COLD_READER_QUESTIONS)))
            continue
        for problem in leaf_readiness(pkt):
            findings.append(("context", nid, problem))

    for a, b, path in collisions(live, packets):
        findings.append((
            "contradiction", f"{a}+{b}",
            f"both name {path} as an edit target and the graph orders neither before "
            "the other — whichever runs second overwrites the first, and no gate "
            "before this one looked outside a declared parallel group"))

    if model_map is not None:
        if not isinstance(model_map, dict):
            findings.append(("model", "-", "the model map is not an object"))
        else:
            for stage in sorted(model_map):
                if str(stage) not in STAGES:
                    findings.append((
                        "model", "-",
                        f"the model map names stage {stage!r}, which this pipeline does "
                        f"not have (stages are {STAGES[0]}–{STAGES[-1]}) — a profile that "
                        "names a stage nobody runs is an override that never fires"))
                elif not str(model_map[stage] or "").strip():
                    findings.append((
                        "model", "-",
                        f"stage {stage} maps to {model_map[stage]!r} — an entry with no "
                        "model is silence wearing a record's clothes"))
    return findings


def report(graph, packets, findings, stream=sys.stdout):
    nodes = [n for n in (graph.get("nodes") or []) if isinstance(n, dict)]
    live = [n for n in nodes if str(n.get("status", "")).lower() not in SETTLED]
    rank = unblocks(live)
    print("plan audit — %d node(s), %d live" % (len(nodes), len(live)), file=stream)
    print("\n  priority (computed: how many nodes each unblocks, transitively)",
          file=stream)
    for n in sorted(live, key=lambda x: (-rank.get(x.get("id"), 0), x.get("id") or "")):
        nid = n.get("id") or "?"
        print("    %-8s unblocks %-3d packet %-7s %s"
              % (nid, rank.get(nid, 0), "yes" if nid in packets else "NO",
                 (n.get("title") or "")[:54]), file=stream)
    if not findings:
        print("\nPASS: every live node carries a packet a cold reader can execute, "
              "no two unordered nodes edit one file, and the model map (if any) names "
              "stages this pipeline has", file=stream)
        return
    print("", file=stream)
    for kind, nid, msg in findings:
        print("  %-13s %-10s %s" % (kind.upper(), nid, msg), file=stream)
    kinds = sorted({k for k, _, _ in findings})
    print("\nFAIL: %d finding(s) across %s — stage 5 does not open. The plan is fixed "
          "here, not worked around there." % (len(findings), ", ".join(kinds)),
          file=stream)


def _self_test():
    """Each case is a plan that would have reached an executor, and the finding it earns."""
    cases, failures = [], []

    def case(name, fn):
        cases.append(name)
        try:
            fn()
            print("  ok  %s" % name)
        except AssertionError as e:
            failures.append("%s: %s" % (name, e))
            print("FAIL  %s: %s" % (name, e))

    def pkt(node, targets=(), full=True):
        p = {"schema_version": "execution-packet/1", "node": node,
             "intent": "do the thing", "inputs": [{"address": "a", "sha256": "0" * 64}],
             "decision_refs": [{"address": "d", "sha256": "1" * 64}],
             "source_scope": {"edit_targets": list(targets)},
             "outputs": ["x"], "acceptance": [{"kind": "positive"}, {"kind": "negative"}],
             "guards": ["g"], "resume": "from the top"}
        if not full:
            p.pop("acceptance")
        return p

    def graph(nodes):
        return {"nodes": nodes}

    def t_missing_packet():
        g = graph([{"id": "N-001", "title": "t", "status": "pending"}])
        f = audit(g, {})
        assert any(k == "context" and "no execution packet" in m for k, _, m in f), f

    def t_packet_missing_an_answer():
        g = graph([{"id": "N-001", "title": "t", "status": "pending"}])
        f = audit(g, {"N-001": pkt("N-001", full=False)})
        assert any("acceptance" in m for _, _, m in f), f

    def t_unordered_nodes_sharing_a_file():
        g = graph([{"id": "N-001", "status": "pending"}, {"id": "N-002", "status": "pending"}])
        p = {"N-001": pkt("N-001", ["src/a.py"]), "N-002": pkt("N-002", ["src/a.py"])}
        f = audit(g, p)
        assert any(k == "contradiction" for k, _, _ in f), f

    def t_ordered_nodes_sharing_a_file_are_fine():
        g = graph([{"id": "N-001", "status": "pending"},
                   {"id": "N-002", "status": "pending", "blocked_by": ["N-001"]}])
        p = {"N-001": pkt("N-001", ["src/a.py"]), "N-002": pkt("N-002", ["src/a.py"])}
        assert not audit(g, p), "an ordered pair is a sequence, not a race"

    def t_settled_nodes_need_no_packet():
        g = graph([{"id": "N-001", "status": "done"}, {"id": "N-002", "status": "parked"}])
        assert not audit(g, {}), "finished work is history, not a plan to hand over"

    def t_priority_is_transitive():
        g = graph([{"id": "N-001", "status": "pending"},
                   {"id": "N-002", "status": "pending", "blocked_by": ["N-001"]},
                   {"id": "N-003", "status": "pending", "blocked_by": ["N-002"]}])
        r = unblocks(g["nodes"])
        assert r["N-001"] == 2 and r["N-002"] == 1 and r["N-003"] == 0, r

    def t_priority_survives_a_cycle():
        g = graph([{"id": "N-001", "status": "pending", "blocked_by": ["N-002"]},
                   {"id": "N-002", "status": "pending", "blocked_by": ["N-001"]}])
        r = unblocks(g["nodes"])  # graph.py reports the cycle; this must not hang
        assert set(r) == {"N-001", "N-002"}, r

    def t_model_map_naming_a_stage_that_does_not_exist():
        g = graph([{"id": "N-001", "status": "done"}])
        f = audit(g, {}, model_map={"11": "opus"})
        assert any(k == "model" for k, _, _ in f), f

    def t_a_real_model_map_passes():
        g = graph([{"id": "N-001", "status": "done"}])
        assert not audit(g, {}, model_map={"4": "fable", "5": "opus"})

    def t_an_orphan_packet_is_reported_not_guessed():
        g = graph([{"id": "N-001", "status": "done"}])
        f = audit(g, {}, orphans=[("x.json", "names no node (`node` / `parent_node`)")])
        assert any(k == "packet" for k, _, _ in f), f

    def t_an_empty_graph_is_a_finding():
        f = audit({"nodes": []}, {})
        assert any(k == "plan" for k, _, _ in f), "an empty plan passed"

    case("a live node with no packet is refused", t_missing_packet)
    case("a packet missing one of the eight answers is refused", t_packet_missing_an_answer)
    case("two unordered nodes editing one file are refused", t_unordered_nodes_sharing_a_file)
    case("an ordered pair editing one file is not a collision", t_ordered_nodes_sharing_a_file_are_fine)
    case("a done or parked node needs no packet", t_settled_nodes_need_no_packet)
    case("priority counts what a node unblocks transitively", t_priority_is_transitive)
    case("priority terminates on a cycle instead of hanging", t_priority_survives_a_cycle)
    case("a model map naming a stage this pipeline lacks is refused",
         t_model_map_naming_a_stage_that_does_not_exist)
    case("a model map over real stages passes", t_a_real_model_map_passes)
    case("a packet attached to no node is reported, never guessed",
         t_an_orphan_packet_is_reported_not_guessed)
    case("an empty graph is a finding, not a pass", t_an_empty_graph_is_a_finding)

    if failures:
        print("\n%d of %d failed" % (len(failures), len(cases)))
        return 1
    print("\nSELF-TEST PASS: %d case(s)" % len(cases))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--graph", default=DEFAULT_GRAPH)
    p.add_argument("--packets", default=os.path.join(".task-pipeline", "packets"))
    p.add_argument("--models", default=None,
                   help="a JSON object mapping stage number → model, as the "
                        "per-stage override map the brief records")
    p.add_argument("--json", action="store_true")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args(argv)

    if args.self_test:
        return _self_test()

    if not os.path.isfile(args.graph):
        print("no work graph at %s — stage 2 writes it and stage 4 audits it. Nothing "
              "was read." % args.graph, file=sys.stderr)
        return 2
    graph = load_json(args.graph)
    packets, orphans = packets_by_node(args.packets)
    model_map = load_json(args.models) if args.models else None
    findings = audit(graph, packets, orphans, model_map)
    if args.json:
        nodes = [n for n in (graph.get("nodes") or []) if isinstance(n, dict)]
        live = [n for n in nodes if str(n.get("status", "")).lower() not in SETTLED]
        print(json.dumps({
            "nodes": len(nodes), "live": len(live),
            "priority": unblocks(live),
            "packets": sorted(packets),
            "findings": [{"kind": k, "node": n, "message": m} for k, n, m in findings],
        }, indent=2, sort_keys=True))
    else:
        report(graph, packets, findings)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
