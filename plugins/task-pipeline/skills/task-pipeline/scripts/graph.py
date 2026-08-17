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

**The mutation verbs never leave a half-written queue.** `add` and `park` write to a
temp file in the same directory and `os.replace` it into place, so a crash mid-write
loses the mutation rather than the graph. Both refuse before writing rather than
writing and repairing: a refusal leaves the file byte-identical, which is what lets a
caller retry without first checking what the failed attempt did.

And both refuse outright on a graph that was **already** invalid, naming it as such.
A mutation that reports the pre-existing damage as though the caller's node caused it
sends the next fix to the wrong place.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile

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
# Parking a node PROMOTES its dependents: `parked` is terminal, so anything
# blocked on it becomes runnable even though the payload it waited on never
# arrived. That is deliberate — `can_continue_around` in the verdict is the
# same idea — but it is a real consequence of parking a blocker rather than a
# leaf, and it is written here because the frontier will not explain it.


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


def shape(graph, path):
    """The graph is the shape the rest of this script assumes. Say so, do not crash.

    `nodes` as an object map, `nodes: ["N-001"]`, a top-level list and a top-level
    `null` each produced an `AttributeError` — a traceback carries the same exit code
    as a documented refusal and none of its information.
    """
    if not isinstance(graph, dict):
        die("%s: the graph must be a JSON object; this is a %s"
            % (path, type(graph).__name__))
    for key in ("nodes", "edges"):
        val = graph.get(key)
        if val is not None and not isinstance(val, list):
            die("%s: `%s` must be a list; this is a %s. An object map here is the shape "
                "that makes every per-element check vacuous" % (path, key, type(val).__name__))
        for i, item in enumerate(val or []):
            if not isinstance(item, dict):
                die("%s: %s[%d] is a %s, not an object"
                    % (path, key, i, type(item).__name__))
    return graph


def save(path, graph):
    """Write via a temp file in the same directory, then `os.replace`.

    `os.replace` is atomic on the same filesystem, so a reader either sees the old
    graph or the new one and never a truncated one. Writing in place is the version
    that costs a queue: this repository has destroyed a file that way twice, and both
    times what saved it was a copy somebody had made by hand.
    """
    # A FIXED temp name (`path + ".tmp"`) was the first draft, and the R-005 reader
    # measured what it costs: two concurrent `add`s share one inode, `os.replace`
    # installs whichever bytes were last in it, and the exit codes then lie in BOTH
    # directions — a run exiting 0 whose node is absent, and a run exiting 1 whose node
    # is present. The second is the dangerous one: the docstring promises a refusal
    # leaves the file untouched, so a caller retries and double-adds. A unique temp per
    # writer costs one call and removes the shared inode entirely.
    #
    # `realpath` first: `os.replace` replaces the LINK, not its target, so a graph that
    # is a symlink into a shared directory would silently fork into two queues.
    path = os.path.realpath(path)
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".graph-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(graph, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except OSError as e:
        # A traceback is indistinguishable from a documented refusal by exit code, and
        # this one is reachable from an ordinary read-only directory.
        try:
            os.unlink(tmp)
        except OSError:
            pass
        die("could not write %s — nothing was changed: %s" % (path, e))


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

    if not (graph.get("goal") or "").strip():
        out.append("the graph has no `goal` — every iteration is supposed to print it "
                   "above the frontier, and a queue that cannot say what it serves is a "
                   "queue nothing can be parked against")

    for n in nodes:
        nid = n.get("id")
        if not isinstance(nid, str) or not ID_SHAPE.match(nid):
            out.append(f"node id {nid!r} is not the shape `N-001` the schema requires — "
                       "and an id nothing can parse is an id no verdict can cite")
        owner = n.get("owner")
        if owner not in ROLES:
            near = [r for r in sorted(ROLES) if r[:4] == (owner or "")[:4]]
            hint = f" — did you mean {near[0]}?" if near else ""
            out.append(f"{nid}: owner {owner!r} is not a role this pipeline "
                       f"ships{hint}. A node nobody can dispatch never leaves the frontier, "
                       "and nothing says why")

        # `graph.schema.json` states the four rules below, and until the R-005 read
        # nothing applied that schema to a LIVE graph — only to the shipped example, at
        # build time. So both `done → evidence` and `parked → reason` rested entirely on
        # the scripts behaving, which is exactly what the validator's own message about
        # them claimed was no longer true. It is true here, where the run actually looks.
        blockers = n.get("blocked_by") or []
        if len(set(blockers)) != len(blockers):
            dupes = sorted({b for b in blockers if blockers.count(b) > 1})
            out.append(f"{nid}: blocked_by repeats {', '.join(dupes)} — the schema calls "
                       "the list unique, and a dependency counted twice is one nobody "
                       "removes on the first pass")
        for b in blockers:
            if b not in known:
                out.append(f"{nid}: blocked_by names {b}, which is not in this graph")

        for field in ("title", "serves"):
            val = n.get(field)
            if isinstance(val, str) and any(c in val for c in "\n\r"):
                out.append(f"{nid}: `{field}` contains a line break. `next` prints one row "
                           "per node and the loop reads those rows, so a break here forges "
                           "a row for a node that does not exist")

        if n.get("status") == "done":
            ev = n.get("evidence")
            if not isinstance(ev, list) or not [e for e in ev
                                                if isinstance(e, str) and e.strip()]:
                out.append(f"{nid}: status is done and `evidence` carries nothing readable "
                           "— a node called done by assertion is what evidence exists for")
        if n.get("status") == "parked":
            # `isinstance` rather than truthiness: `null` is the shape a schema whose
            # `parked_reason` was typed nullable would let through, and it satisfies
            # every string-only assertion vacuously.
            reason = n.get("parked_reason")
            if not isinstance(reason, str) or not reason.strip():
                out.append(f"{nid}: status is parked and `parked_reason` is {reason!r} — "
                           "REQ-012: a park without a reason is indistinguishable from "
                           "work that was quietly dropped")

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


def unblocks(nodes):
    """How many nodes each node stands in front of, transitively.

    This is the priority, and it is COMPUTED rather than declared. A `priority` field
    would be a number somebody typed once and nobody revisits; this one moves on its
    own when the graph does, which is what REQ-011 means by *re-prioritised after every
    task*. Add a node that waits on N-002 and N-002 rises — no re-ranking pass, no
    field to forget to update.
    """
    dependents = {}
    for n in nodes:
        for b in n.get("blocked_by") or []:
            dependents.setdefault(b, set()).add(n.get("id"))

    def reach(nid):
        seen, stack = set(), [nid]
        while stack:
            for d in dependents.get(stack.pop(), ()):
                if d not in seen:
                    seen.add(d)
                    stack.append(d)
        return seen

    return {n.get("id"): len(reach(n.get("id"))) for n in nodes}


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
    rank = unblocks(nodes)
    order = {n.get("id"): i for i, n in enumerate(nodes)}
    # Declaration order breaks the tie, so the frontier is stable across runs. An
    # unstable order costs more than it looks: an agent that re-reads `next` between
    # two ties gets a different first row and starts the other one.
    ready.sort(key=lambda n: (-rank.get(n.get("id"), 0), order.get(n.get("id"), 0)))
    return ready


# --- the verdict ---------------------------------------------------------------

VERDICT_KEYS = ("node", "done", "not_done", "blockers", "replan", "evidence")
NODE_ID = "N-"
ID_SHAPE = re.compile(r"^N-[0-9]{3,}$")


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


class held:
    """An exclusive lock around a mutation's whole read-modify-write.

    A unique temp file fixes CORRUPTION and the exit-1-with-the-node-present lie. It
    does not fix the lost update: two processes read the same graph, both append, and
    the second write drops the first node while both exit 0. Measured with four
    concurrent `add`s — 40001 nodes where 40004 had been added.

    That is not a theoretical concurrency: this programme is explicitly built for
    several agents walking one graph, so the queue has to survive two of them arriving
    at once. `flock` releases when the process dies, which is why it is preferred over a
    lock FILE somebody has to clean up after a crash.

    Where `fcntl` does not exist the mutation still runs and the run is TOLD it ran
    unlocked — a silent downgrade is how a queue loses a node and nobody learns why.
    """

    def __init__(self, path):
        self.path = os.path.realpath(path)
        self.fh = None

    def __enter__(self):
        try:
            import fcntl
        except ImportError:
            print("note: no file locking on this platform — a concurrent mutation of "
                  "%s could lose an update" % self.path, file=sys.stderr)
            return self
        d = os.path.dirname(self.path) or "."
        try:
            self.fh = open(os.path.join(d, ".graph.lock"), "a+")
            fcntl.flock(self.fh.fileno(), fcntl.LOCK_EX)
        except OSError as e:
            if self.fh:
                self.fh.close()
                self.fh = None
            print("note: could not take the graph lock (%s) — proceeding unlocked" % e,
                  file=sys.stderr)
        return self

    def __exit__(self, *exc):
        if self.fh:
            self.fh.close()
        return False


def guard(graph, path):
    """Refuse a mutation on a graph that was already invalid, and SAY it was already.

    Without this a caller adding a well-formed node to a broken graph reads the
    breakage as their own — and goes looking in the one place the fault is not.
    """
    bad = violations(graph)
    if bad:
        die("%s was ALREADY invalid before this mutation — nothing was written. Fix "
            "these first:\n  %s" % (path, "\n  ".join(bad)))


def cmd_park(graph, args):
    """Park one node, carrying the reason — REQ-012.

    Parking is not a soft delete. The reason is the artifact: a node parked without one
    is indistinguishable next week from work that was quietly dropped, which is the
    exact failure parking exists instead of.
    """
    guard(graph, args.graph)
    reason = (args.reason or "").strip()
    if any(c in reason for c in "\n\r"):
        die("--reason contains a line break, and a reason is read back beside the node "
            "it explains — nothing was written")
    if not reason:
        die("`park` needs a --reason with something in it. The flag being present is "
            "not a reason being given, and an empty one parks the node while recording "
            "nothing about why — which is the shape parking exists to prevent")

    node = next((n for n in graph.get("nodes") or [] if n.get("id") == args.node), None)
    if node is None:
        die("no node %s in this graph — nothing was written" % args.node)
    if node.get("status") == "done":
        die("%s is done — parking it would overwrite a closed result and its evidence. "
            "If the close was wrong, say so in a verdict rather than here" % args.node)
    if node.get("status") == "parked":
        die("%s is already parked, and the reason recorded is: %r. A second park would "
            "replace it, and the first reason is the one somebody wrote at the time"
            % (args.node, node.get("parked_reason")))

    node["status"] = "parked"
    node["parked_reason"] = reason
    bad = violations(graph)
    if bad:
        die("parking %s would break the graph — nothing was written:\n  %s"
            % (args.node, "\n  ".join(bad)))
    save(args.graph, graph)
    print("%s parked: %s" % (args.node, reason))
    return 0


def next_id(known):
    """The next id, from the MAXIMUM rather than from the count.

    Ids stop being contiguous the first time anything is renumbered or imported, and
    from that moment counting hands out one that already exists — the duplicate
    `validate` reports as a graph nobody can cite.
    """
    used = [int(i[2:]) for i in known if i and i.startswith(NODE_ID) and i[2:].isdigit()]
    return "N-%03d" % ((max(used) + 1) if used else 1)


def cmd_add(graph, args):
    """Add a node mid-flight — the dynamic backlog, REQ-011.

    Everything is checked BEFORE the append, so a refusal leaves the file untouched and
    the caller can retry without first working out what the failed attempt did.
    """
    guard(graph, args.graph)
    title = (args.title or "").strip()
    serves = (args.serves or "").strip()
    if not title:
        die("`add` needs a --title with something in it")
    if not serves:
        die("`add` needs --serves: the REQ or goal clause this node exists for. A node "
            "that serves nothing is not a node to add — it is REQ-012's park case, and "
            "adding it hides the decision that ought to be recorded")
    if args.owner not in ROLES:
        near = [r for r in sorted(ROLES) if r[:4] == (args.owner or "")[:4]]
        die("owner %r is not a role this pipeline ships%s — nothing was written"
            % (args.owner, (" — did you mean %s?" % near[0]) if near else ""))

    for name, val in (("--title", title), ("--serves", serves)):
        if any(c in val for c in "\n\r"):
            die("%s contains a line break. `next` prints one row per node and the loop "
                "reads those rows, so a break here forges a row for a node that does not "
                "exist — nothing was written" % name)

    nodes = graph.setdefault("nodes", [])
    known = {n.get("id") for n in nodes}
    # Dedupe rather than refuse: `argparse action="append"` makes a repeat trivially easy
    # to type, the intent is unambiguous, and the schema calls the list unique — so the
    # repair is exact. A hand-written graph with the same repeat is caught by `violations`.
    blocked = list(dict.fromkeys(args.blocked_by or []))
    for b in blocked:
        if b not in known:
            die("--blocked-by names %s, which is not in this graph — nothing was written" % b)

    nid = args.id or next_id(known)
    if not ID_SHAPE.match(nid):
        die("--id %r is not a node id; the shape is N-001 and the schema enforces it" % nid)
    if nid in known:
        die("node id %s already exists — nothing was written. Omit --id and one is "
            "allocated from the highest in use" % nid)

    nodes.append({"id": nid, "title": title, "owner": args.owner, "status": "pending",
                  "blocked_by": blocked, "serves": serves,
                  "evidence": None})
    bad = violations(graph)
    if bad:
        # Belt over the braces: every shape enumerated above is checked before this
        # point, so this fires only on one that was NOT enumerated — and the right
        # answer to an unenumerated shape is to refuse rather than to write and hope.
        die("adding %s would break the graph — nothing was written:\n  %s"
            % (nid, "\n  ".join(bad)))
    save(args.graph, graph)
    print("%s added: %s" % (nid, title))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="graph.py", description=__doc__.split("\n")[0])
    # `--graph` hangs off every verb rather than off the top level, so it can be passed
    # after the verb — which is the order every caller writes without thinking.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--graph", default=os.path.join(".task-pipeline", "graph.json"))
    sub = ap.add_subparsers(dest="verb", required=True)

    sub.add_parser("validate", parents=[common], help="every invariant a schema cannot state")
    sub.add_parser("next", parents=[common], help="the frontier, ordered by what it unblocks")
    sub.add_parser("goal", parents=[common], help="the release goal this graph serves")

    p_add = sub.add_parser("add", parents=[common], help="add a node mid-run")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--owner", required=True)
    p_add.add_argument("--serves", required=True)
    p_add.add_argument("--blocked-by", dest="blocked_by", action="append", default=[])
    p_add.add_argument("--id", default=None, help="omit to allocate the next one")

    p_park = sub.add_parser("park", parents=[common], help="park a node, carrying the reason")
    p_park.add_argument("node")
    # `required=True` makes the MISSING flag a usage error (exit 2). The empty and
    # whitespace ones reach `cmd_park`, which refuses them — argparse cannot tell a flag
    # that was given from a reason that was written, and only the second is REQ-012.
    p_park.add_argument("--reason", required=True)

    args = ap.parse_args(argv)
    verbs = {"validate": cmd_validate, "next": cmd_next, "goal": cmd_goal,
             "add": cmd_add, "park": cmd_park}
    if args.verb in ("add", "park"):
        # The READ happens inside the lock too. Loading first and locking second is the
        # same lost update with an extra step: the stale copy is already in memory.
        with held(args.graph):
            return verbs[args.verb](shape(load(args.graph), args.graph), args)
    return verbs[args.verb](shape(load(args.graph), args.graph), args)


if __name__ == "__main__":
    sys.exit(main())
