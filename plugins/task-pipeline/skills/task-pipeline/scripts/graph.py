#!/usr/bin/env python3
"""The work graph, walked by a script so the model never reads it.

`.task-pipeline/graph.json` is the queue. A graph for a real release is hundreds of
nodes; a model that re-reads it every iteration spends its context on ground it has
already walked, and the cost grows with the programme. This script answers one
question — *which nodes are runnable right now* — and prints the answer. What enters
a context each iteration is then bounded by the **frontier's width**, not by the
graph's size: four hundred nodes and four cost the same to walk.

That is the whole design rationale, and it is why `next` prints the frontier and
nothing else. Anything else printed there is paid on every turn of every loop.

**Stdlib only.** `references/portability.md`: `scripts/` is the one Claude-Code
capability that travels, because it lives inside the skill directory and every
channel ships it. A dependency here would make the graph Claude-Code-shaped.

**What this file checks, and what it deliberately does not.** `graph.schema.json`
states everything JSON Schema can — the required fields, `owner` non-empty, an edge's
payload, and `done` implying non-empty evidence. What a schema cannot reach is
cross-document and cross-node: whether an `owner` names a role that EXISTS, whether
`serves` resolves, and whether the edges cycle. Those three are here. The split is
where the format actually puts it, which is not where the first draft drew it.

Exit codes are the contract (standing instruction R-004 — the next command is
conditional on the code, never merely sequenced after it):

    0  the verb succeeded; for `next`, runnable nodes were printed
    1  a refusal — an invariant violated, a malformed verdict, a missing reason
    2  usage
    3  nothing left to do: every node is done
    4  nothing runnable: what remains is blocked or parked
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# Who may OWN a node — which is a different axis from who ships as a subagent.
#
# The brief closed the role set at thirteen and the first draft of this set held ten,
# because it silently conflated "is an agent" with "can own work". `manager` and
# `business-analyst` are main-thread doctrine precisely BECAUSE their job is talking
# to the operator, and that is still work a node can be owned by — the refusal message
# below even named the manager while this set rejected it.
#
# `project` is the one deliberate absence: the brief defers it for having no bounded
# job stated, and a role that cannot say what it does cannot own a node either.
#
# It is the ONE place the set lives; a second copy is what
# `references/documentation.md` calls a fact with two homes.
ROLES = {
    # execution — references/build.md
    "implementer", "reviewer", "fixer",
    # main-thread doctrine: these own nodes, they just are not dispatched as agents,
    # because a subagent cannot reach the operator and their job is to ask
    "manager", "business-analyst",
    # dispatched as agents — voluminous reading, small answer
    "verifier", "decomposer", "ux", "ui", "researcher", "market-analyst", "bug-analyst",
}

TERMINAL = {"done", "parked"}


def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def load(path):
    if not os.path.isfile(path):
        die(f"no graph at {path} — stage 2 writes it", 2)
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except ValueError as e:
        die(f"{path}: not readable as JSON — {e}")


def save(path, graph):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(graph, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


# --- the three a schema cannot reach ------------------------------------------

def violations(graph):
    """Every cross-node and cross-document violation, in a stable order.

    All of them, not the first: a caller that fixes one and re-runs to find the next
    is a caller doing the loop this function exists to do once.
    """
    out = []
    nodes = graph.get("nodes") or []
    ids = [n.get("id") for n in nodes]
    known = set(ids)

    seen = set()
    for i in ids:
        if i in seen:
            out.append(f"duplicate node id {i} — two nodes with one id is a graph "
                       "nobody can cite, and a verdict naming it would close the wrong one")
        seen.add(i)

    for n in nodes:
        owner = n.get("owner")
        if owner not in ROLES:
            near = [r for r in sorted(ROLES) if r[:4] == (owner or "")[:4]]
            hint = f" — did you mean {near[0]}?" if near else ""
            out.append(f"{n.get('id')}: owner {owner!r} is not a role this pipeline "
                       f"ships{hint}. A node nobody can dispatch never leaves the frontier, "
                       "and nothing says why")
        for b in n.get("blocked_by") or []:
            if b not in known:
                out.append(f"{n.get('id')}: blocked_by names {b}, which is not in this graph")

    for e in graph.get("edges") or []:
        for end in ("from", "to"):
            if e.get(end) not in known:
                out.append(f"edge {e.get('from')}→{e.get('to')}: {end} names "
                           f"{e.get(end)}, which is not in this graph")

    out.extend(cycles(nodes))
    return out


def cycles(nodes):
    """Cycles, named by the nodes in them.

    A cycle is why a frontier can be non-empty forever while nothing is runnable —
    the one failure of this design that looks exactly like slow progress.
    """
    dep = {n.get("id"): [b for b in (n.get("blocked_by") or [])] for n in nodes}
    found, state = [], {}

    def walk(nid, stack):
        if state.get(nid) == "done":
            return
        if state.get(nid) == "open":
            ring = stack[stack.index(nid):]
            found.append("cycle: " + " → ".join(ring + [nid]))
            return
        state[nid] = "open"
        for nxt in dep.get(nid, []):
            if nxt in dep:
                walk(nxt, stack + [nid])
        state[nid] = "done"

    for nid in dep:
        walk(nid, [])
    # One ring reports once however many entry points reach it.
    return sorted(set(found))


def frontier(graph):
    nodes = graph.get("nodes") or []
    by_id = {n.get("id"): n for n in nodes}
    ready = []
    for n in nodes:
        if n.get("status") in TERMINAL or n.get("status") == "running":
            continue
        blockers = n.get("blocked_by") or []
        if all(by_id.get(b, {}).get("status") in TERMINAL for b in blockers):
            ready.append(n)
    return ready


# --- the verdict ---------------------------------------------------------------

VERDICT_KEYS = ("node", "done", "not_done", "blockers", "replan", "evidence")
NODE_ID = "N-"


def verdict_violations(v):
    """Everything wrong with a verdict, in a stable order.

    The verifier's output is the one artifact in this design a human does not read
    before it acts: `close` consumes it and the graph moves. So the shape is checked
    rather than trusted, and every refusal names the key, because a verdict rejected
    without naming its fault is a verdict the next attempt reproduces.

    The rule that matters most is the smallest: **a `done` claim with no evidence is
    refused.** Everything else here is structure; that one is the difference between
    a node that was verified and a node that was asserted.
    """
    out = []
    if not isinstance(v, dict):
        return ["verdict is not an object"]

    for k in VERDICT_KEYS:
        if k not in v:
            out.append(f"verdict has no `{k}` — all six are required, because a "
                       "verdict that omits one is silent about it rather than clear")
    if out:
        return out

    if not isinstance(v["node"], str) or not v["node"].startswith(NODE_ID):
        out.append(f"verdict `node` is {v['node']!r}, which is not a node id")

    for k in ("done", "not_done", "evidence"):
        if not isinstance(v[k], list):
            out.append(f"verdict `{k}` must be a list")

    if isinstance(v.get("done"), list) and isinstance(v.get("evidence"), list):
        if v["done"] and not v["evidence"]:
            out.append("verdict claims `done` with empty `evidence` — the field exists "
                       "for exactly this, and a node closed on an unevidenced claim is "
                       "the thing the whole ledger is built to prevent")
        # And each entry must be a non-empty string, because `graph.schema.json`
        # requires exactly that of the node this verdict closes. The first draft
        # checked only that the list was non-empty — so `['', '   ']` passed here and
        # was refused by the schema, and `close` would have written a node its own
        # shipped schema rejects. That is the same class the schema's own prose
        # records fixing one level up: a rule stated about the container while the
        # contents go unchecked. Found by the wave-2 convergence check, not by the
        # per-task review that had already read this function.
        for i, e in enumerate(v["evidence"]):
            if not isinstance(e, str) or not e.strip():
                out.append(f"verdict `evidence[{i}]` is {e!r} — every entry must be a "
                           "non-empty string, and a list of blanks is the shape a script "
                           "emitting an empty command output produces")

    for b in v.get("blockers") or []:
        if not isinstance(b, dict) or "what" not in b:
            out.append("a blocker must say `what` it is")
            continue
        if "blocks" not in b or "can_continue_around" not in b:
            out.append(f"blocker {b.get('what')!r} does not say what it `blocks` and "
                       "whether the run `can_continue_around` it — without both, the "
                       "manager cannot tell a pause from a stop")

    rp = v.get("replan")
    if not isinstance(rp, dict):
        out.append("verdict `replan` must be an object")
    else:
        if "possible" not in rp:
            out.append("verdict `replan` does not say whether a re-plan is `possible`")
        elif rp.get("possible") is False and not (rp.get("why") or "").strip():
            out.append("verdict says a re-plan is not possible and gives no `why` — a "
                       "stop with no reason is indistinguishable from a stall")
        for nid in rp.get("park") or []:
            if not isinstance(nid, str) or not nid.startswith(NODE_ID):
                out.append(f"replan.park names {nid!r}, which is not a node id")
        for nid in rp.get("add") or []:
            if not isinstance(nid, dict) or "title" not in nid:
                out.append("replan.add entries must be nodes with at least a `title`")
    return out


# --- verbs --------------------------------------------------------------------

def cmd_validate(graph, args):
    bad = violations(graph)
    for line in bad:
        print(line, file=sys.stderr)
    return 1 if bad else 0


def cmd_next(graph, args):
    if violations(graph):
        die("graph does not validate — run `validate` first", 1)
    nodes = graph.get("nodes") or []
    if nodes and all(n.get("status") in TERMINAL for n in nodes):
        return 3
    ready = frontier(graph)
    if not ready:
        return 4
    # The frontier and nothing else. This is the line that enters a context on
    # every iteration of every loop, so every word here is paid for repeatedly.
    for n in ready:
        print(f"{n['id']}  {n['owner']}  {n['title']}")
    return 0


def cmd_goal(graph, args):
    goal = (graph.get("goal") or "").strip()
    if not goal:
        return 3
    print(goal)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="graph.py", description=__doc__.split("\n")[0])
    ap.add_argument("verb", choices=["validate", "next", "goal"])
    ap.add_argument("--graph", default=os.path.join(".task-pipeline", "graph.json"))
    args = ap.parse_args(argv)
    graph = load(args.graph)
    return {"validate": cmd_validate, "next": cmd_next, "goal": cmd_goal}[args.verb](graph, args)


if __name__ == "__main__":
    sys.exit(main())
