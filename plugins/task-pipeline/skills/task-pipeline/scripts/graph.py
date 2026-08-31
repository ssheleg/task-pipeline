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
`serves` resolves, and whether the edges cycle. Those three are here. So is every rule
the format states, because the schema is never applied to a LIVE graph — including
B-080's `check`, without which `agents/verifier.md` instructs an agent to read a field
that does not exist. The split is
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
NO_GRAPH = {"producer", "doctrine"}
# One place, and the schema enumerates the same three. Two homes for this set is
# what let `close` write a verb the format forbade.
REVISION_VERBS = {"add", "park", "close"}
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

    declared = set(graph.get("requirements") or []) | set(graph.get("goal_clauses") or [])
    if not (graph.get("requirements") or []):
        out.append("the graph declares no `requirements` — `serves` then resolves against "
                   "nothing, and that field is the one edge joining the intent graph to "
                   "this one. Copy the REQ ids the brief froze")

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
            if not isinstance(val, str) or not val.strip():
                out.append(f"{nid}: `{field}` is {val!r}. The schema requires a non-empty "
                           "string and never ran against a live graph, so this passed — a "
                           "node with no title is a frontier row nobody can act on, and a "
                           "node serving nothing is REQ-012's park case")
            elif any(c in val for c in "\n\r"):
                out.append(f"{nid}: `{field}` contains a line break. `next` prints one row "
                           "per node and the loop reads those rows, so a break here forges "
                           "a row for a node that does not exist")
            elif field == "serves" and declared and val not in declared:
                near = [d for d in sorted(declared) if d[:5] == val[:5]]
                hint = f" — did you mean {near[0]}?" if near else ""
                out.append(f"{nid}: serves {val!r}, which is neither a declared requirement "
                           f"nor a declared goal clause{hint}. A node serving something "
                           "nobody asked for is work the brief cannot account for, and the "
                           "coverage relation cannot reach it")

        # B-080 — the node says HOW it will be closed, and shipped doctrine reads it.
        # `agents/verifier.md` told the verifier to run *the check the task named* while
        # the schema had no field to name one, so the instruction pointed at an absence
        # and the verifier's only options were the two that paragraph forbids: invent a
        # check, or run everything. A `parked` node is the one exemption — it is the one
        # node nobody will close, and a placeholder there would be worse than the gap.
        if n.get("status") != "parked":
            chk = n.get("check")
            if not isinstance(chk, str) or not chk.strip():
                out.append(f"{nid}: `check` is {chk!r} — B-080: a node that cannot say how "
                           "it will be closed leaves the verifier inventing a check or "
                           "running everything, and `agents/verifier.md` forbids both. Name "
                           "the command, or the judge where no command can decide it. Only a "
                           "`parked` node is exempt")
            elif any(c in chk for c in "\n\r"):
                out.append(f"{nid}: `check` contains a line break. A completion test that is "
                           "two commands cannot say which one closed the node, and the "
                           "verifier reports its output as one evidence row")

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

    # An edge with no payload, and a dependency with no edge. The graph stored the same
    # fact in two unlinked places — `blocked_by`, which `frontier()` obeys, and `edges`,
    # which carries the payload and which nothing read past a from/to existence check.
    # So `references/planning.md`'s fake-edge test was stated for the markdown plan and
    # unenforceable on the artifact that replaced it. Found by a four-way audit,
    # 2026-08-17, which measured this pipeline's own `add` producing one every run.
    carried = {}
    for e in graph.get("edges") or []:
        for end in ("from", "to"):
            if e.get(end) not in known:
                out.append(f"edge {e.get('from')}→{e.get('to')}: {end} names "
                           f"{e.get(end)}, which is not in this graph")
        pay = e.get("payload")
        if not isinstance(pay, str) or not pay.strip():
            out.append(f"edge {e.get('from')}→{e.get('to')}: `payload` is {pay!r}. An edge "
                       "carrying no named artifact is chronology drawn as architecture — "
                       "`references/planning.md`'s fake-edge test, on the graph rather than "
                       "on the plan")
        else:
            carried[(e.get("from"), e.get("to"))] = pay

    for n in nodes:
        for b in n.get("blocked_by") or []:
            if b in known and (b, n.get("id")) not in carried:
                out.append(f"{n.get('id')}: blocked_by names {b} and no edge {b}→"
                           f"{n.get('id')} carries a payload. The dependency the frontier "
                           "obeys and the payload that justifies it are separate fields, "
                           "and a dependency handing over nothing is the one this check "
                           "exists to refuse")

    for i, r in enumerate(graph.get("revisions") or []):
        if not isinstance(r, dict):
            out.append(f"revisions[{i}] is not an object")
            continue
        if r.get("verb") not in REVISION_VERBS:
            out.append(f"revisions[{i}] records verb {r.get('verb')!r}, which is not one of "
                       f"{sorted(REVISION_VERBS)} — the schema enumerates them and "
                       "`violations()` never reached the enum, so `close` wrote a revision "
                       "its own shipped schema rejected (found by a probe, not by the "
                       "fixture that asserts the graph still validates)")
        if not isinstance(r.get("why"), str) or not r["why"].strip():
            out.append(f"revisions[{i}] records {r.get('verb')} on {r.get('node')} with "
                       f"`why` = {r.get('why')!r} — a revision log whose reasons are blank "
                       "is the log's own failure mode, not a record")

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


def collisions(ready):
    """Pairs of simultaneously-runnable nodes that mutate the same thing — B-093.

    Only among nodes that are ready TOGETHER: a pair where one waits on the other never
    holds the target at once, and reporting it would be a warning nobody can act on, which
    is how a warning becomes noise.

    Returns (pairs, undeclared) — and the second is why this function returns two things.
    A frontier whose nodes declare no `touches` produces no pairs, which looks exactly like
    a frontier that was checked and found clean. So the count of nodes that said nothing is
    reported beside the pairs, for the same reason `doctrine` refuses to print `0`.
    """
    out, undeclared = [], []
    for n in ready:
        if not (n.get("touches") or []):
            undeclared.append(n.get("id"))
    for i, a in enumerate(ready):
        for b in ready[i + 1:]:
            shared = sorted(set(a.get("touches") or []) & set(b.get("touches") or []))
            if shared:
                out.append((a.get("id"), b.get("id"), shared))
    return out, undeclared


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

VERDICT_KEYS = ("node", "done", "not_done", "not_verified", "blockers", "replan", "evidence")
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
            out.append(f"verdict has no `{k}` — all seven are required, because a "
                       "verdict that omits one is silent about it rather than clear")
    if out:
        return out

    if not isinstance(v["node"], str) or not v["node"].startswith(NODE_ID):
        out.append(f"verdict `node` is {v['node']!r}, which is not a node id")

    for k in ("done", "not_done", "not_verified", "evidence"):
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
                continue
            # B-080 again, at the one place a node is created by a verdict rather than by
            # a person. Checked HERE so the refusal names the key before anything is
            # written: leaving it to `violations()` after the close would abort the whole
            # close over a field the verdict could have been asked for.
            _c = nid.get("check")
            if not isinstance(_c, str) or not _c.strip():
                out.append(f"replan.add entry {nid.get('title')!r} names no `check` — the "
                           "node it creates has to say how IT will be closed, or the next "
                           "verifier faces the absence this one was told to read")
    return out


# --- certification: three tiers, one node ------------------------------------
#
# One verifier reads the diff it was handed. That is the whole limitation this
# section exists for: a change can be correct where it was made, and wrong one
# level out — a caller whose contract moved, a module whose invariant the new
# branch breaks, a documented behaviour nobody re-read. The single verdict cannot
# see any of it, because the context it was given was the change.
#
# So a node is closed by THREE reports at escalating visibility, produced
# independently and blind to each other:
#
#   unit     the code that changed — the functions, classes and branches in the
#            diff, and the node's own `check`
#   seam     one level out — callers, callees, shared state, the contracts and
#            tests of the neighbours the change can reach
#   product  one level out again — the documentation, the scenarios, how this
#            behaviour interacts with the rest of the product
#
# **All three must pass, and blind is the point.** Three agents that read each
# other's reports are one opinion with three signatures; the disagreement is the
# instrument. `certify` refuses a report that cites another tier's verdict.
#
# **A tier cannot pass on an empty `scope`.** This is the rule the rest is built
# around: a report that names nothing it read is a rubber stamp, and a rubber
# stamp at three levels is worse than one verifier, because it costs three times
# as much and reads as three times the assurance.
TIERS = ("unit", "seam", "product")
TIER_KEYS = ("node", "tier", "verdict", "scope", "confirms", "findings",
             "evidence", "not_examined")
TIER_VERDICTS = ("pass", "fail")
SEVERITIES = ("breaks", "risk")
# A tier report that quotes another tier's verdict was not written blind. Cheap
# to detect and worth detecting: the failure it prevents is three reports that
# agree because the second two read the first.
CROSS_TIER = re.compile(r"\b(?:unit|seam|product)\s+tier\s+(?:passed|failed|says)"
                        r"|\btier\s+\d\s+(?:passed|failed)"
                        r"|as\s+the\s+(?:unit|seam|product)\s+tier", re.I)


def tier_violations(t):
    """Everything wrong with one tier report, in a stable order.

    Same law as `verdict_violations`: the shape is checked rather than trusted,
    and every refusal names the key, because a report rejected without naming its
    fault is a report the next attempt reproduces.
    """
    out = []
    if not isinstance(t, dict):
        return ["tier report is not an object"]

    for k in TIER_KEYS:
        if k not in t:
            out.append("tier report has no `%s` — all eight are required, because a "
                       "report that omits one is silent about it rather than clear" % k)
    if out:
        return out

    if not isinstance(t["node"], str) or not t["node"].startswith(NODE_ID):
        out.append("tier report `node` is %r, which is not a node id" % (t["node"],))
    if t["tier"] not in TIERS:
        out.append("tier report `tier` is %r — it must be one of %s"
                   % (t["tier"], ", ".join(TIERS)))
    if t["verdict"] not in TIER_VERDICTS:
        out.append("tier report `verdict` is %r — it must be `pass` or `fail`, because "
                   "a certification that admits a third state admits a maybe"
                   % (t["verdict"],))

    for k in ("scope", "confirms", "findings", "evidence", "not_examined"):
        if not isinstance(t[k], list):
            out.append("tier report `%s` must be a list" % k)
    if out:
        return out

    for k in ("scope", "confirms", "evidence", "not_examined"):
        for i, e in enumerate(t[k]):
            if not isinstance(e, str) or not e.strip():
                out.append("tier report `%s[%d]` is %r — every entry must be a non-empty "
                           "string, and a list of blanks is the shape a script emitting "
                           "empty output produces" % (k, i, e))

    findings = []
    for i, f in enumerate(t["findings"]):
        if not isinstance(f, dict):
            out.append("tier report `findings[%d]` is not an object" % i)
            continue
        for k in ("what", "where", "severity"):
            if not str(f.get(k, "")).strip():
                out.append("tier report `findings[%d]` does not say `%s`" % (i, k))
        sev = f.get("severity")
        if sev is not None and sev not in SEVERITIES:
            out.append("tier report `findings[%d].severity` is %r — it must be `breaks` "
                       "(the node is not done) or `risk` (found, judged survivable, and "
                       "named)" % (i, sev))
        # A break has to say how its fix will be PROVEN, for the same reason
        # `replan.add` does: the node it creates is one the next certification has
        # to close, and handing it the absence is how the defect returns a round
        # later.
        if sev == "breaks" and not str(f.get("check", "")).strip():
            out.append("tier report `findings[%d]` breaks the node and names no `check` "
                       "— the fix node it becomes has to say how IT will be closed" % i)
        findings.append(f)

    breaks = [f for f in findings if isinstance(f, dict) and f.get("severity") == "breaks"]
    if t["verdict"] == "pass":
        # The two rules that make a pass mean something.
        if not t["scope"]:
            out.append("tier report `%s` passes on an empty `scope` — a report that names "
                       "nothing it read is a rubber stamp, and three of those cost three "
                       "times one verifier and read as three times the assurance"
                       % t["tier"])
        if not t["evidence"]:
            out.append("tier report `%s` passes with empty `evidence` — the field exists "
                       "for exactly this" % t["tier"])
        if breaks:
            out.append("tier report `%s` passes while carrying %d finding(s) at severity "
                       "`breaks`: %s. Those two cannot both be true"
                       % (t["tier"], len(breaks),
                          "; ".join(str(f.get("what")) for f in breaks)))
    elif t["verdict"] == "fail":
        if not breaks:
            out.append("tier report `%s` fails and names no finding at severity `breaks` "
                       "— a fail that does not say what broke is a fail the next round "
                       "cannot act on" % t["tier"])

    # Blind, and checked. Only the prose fields can carry it.
    for k in ("confirms", "evidence", "not_examined"):
        for i, e in enumerate(t[k]):
            if isinstance(e, str) and CROSS_TIER.search(e):
                out.append("tier report `%s[%d]` cites another tier's verdict (%r) — the "
                           "three run blind, because three reports that read each other "
                           "are one opinion with three signatures" % (k, i, e.strip()[:70]))
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

    # On stderr, always. The frontier rows are the one line paid for on every iteration of
    # every loop, and a warning inside them would be paid for the same way — and read as a
    # node by anything parsing rows.
    pairs, undeclared = collisions(ready)
    for a, b, shared in pairs:
        print(f"collision: {a} and {b} are both runnable and both mutate "
              f"{', '.join(shared)} — dispatching them together is the false parallelism "
              "`references/planning.md` refuses: distinct is not independent, and the check "
              "is what they touch", file=sys.stderr)
    if undeclared:
        print(f"undeclared: {len(undeclared)} of {len(ready)} runnable node(s) declare no "
              f"`touches` ({', '.join(undeclared[:6])}) — a frontier nobody described cannot "
              "be checked for collisions, and no warning here is not the same as no "
              "collision", file=sys.stderr)
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


def revise(graph, verb, node, why):
    """Append the revision. Both verbs call it; neither may skip it.

    `park` demanded a reason from the start and `add` demanded nothing, so half the
    graph's revision surface was silent — and a graph that changed for reasons nobody
    recorded can always explain its own completion by appealing to a plan that existed
    only at the end.
    """
    graph.setdefault("revisions", []).append(
        {"verb": verb, "node": node, "why": why})


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
    revise(graph, "park", args.node, reason)
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
    declared = set(graph.get("requirements") or []) | set(graph.get("goal_clauses") or [])
    if declared and serves not in declared:
        die("--serves %r is neither a declared requirement nor a declared goal clause. The "
            "REQ table is frozen at stage 0 — adding to it is free and the BRIEF does it, "
            "not a node. Amend the brief and the graph's `requirements`, or serve one of: "
            "%s. Nothing was written" % (serves, ", ".join(sorted(declared)[:6])))

    if args.owner not in ROLES:
        near = [r for r in sorted(ROLES) if r[:4] == (args.owner or "")[:4]]
        die("owner %r is not a role this pipeline ships%s — nothing was written"
            % (args.owner, (" — did you mean %s?" % near[0]) if near else ""))

    check = (args.check or "").strip()
    if not check:
        die("`add` needs a --check with something in it: the command that closes this node, "
            "or the judge where no command can decide it. A node that cannot say how it "
            "will be closed leaves the verifier inventing a check or running everything — "
            "B-080, and `agents/verifier.md` forbids both. Nothing was written")

    for name, val in (("--title", title), ("--serves", serves), ("--check", check)):
        if any(c in val for c in "\n\r"):
            die("%s contains a line break. `next` prints one row per node and the loop "
                "reads those rows, so a break here forges a row for a node that does not "
                "exist — nothing was written" % name)

    nodes = graph.setdefault("nodes", [])
    known = {n.get("id") for n in nodes}
    # Dedupe rather than refuse: `argparse action="append"` makes a repeat trivially easy
    # to type, the intent is unambiguous, and the schema calls the list unique — so the
    # repair is exact. A hand-written graph with the same repeat is caught by `violations`.
    why = (args.why or "").strip()
    if not why:
        die("`add` needs a --why with something in it: a node appearing mid-run is a "
            "revision of the plan, and a revision nobody recorded a reason for is how a "
            "run explains its own completion by a plan that existed only at the end")
    if any(c in why for c in "\n\r"):
        die("--why contains a line break — nothing was written")

    # `dict.fromkeys` for the dependency, and the payloads must survive the same
    # deduplication or they stop pairing by index.
    raw_blocked = args.blocked_by or []
    raw_carries = args.carries or []
    if len(raw_blocked) != len(raw_carries):
        die("--blocked-by was given %d time(s) and --carries %d. Each dependency names "
            "what it hands over, and they pair in the order written — an edge carrying no "
            "named artifact is chronology drawn as architecture. Nothing was written"
            % (len(raw_blocked), len(raw_carries)))
    pairs, seen_b = [], set()
    for b, c in zip(raw_blocked, raw_carries):
        if b in seen_b:
            continue
        seen_b.add(b)
        if not c.strip():
            die("--carries for %s is blank. A payload nobody named is the fake edge with a "
                "field around it — nothing was written" % b)
        pairs.append((b, c.strip()))
    blocked = [b for b, _ in pairs]
    for b in blocked:
        if b not in known:
            die("--blocked-by names %s, which is not in this graph — nothing was written" % b)

    nid = args.id or next_id(known)
    if not ID_SHAPE.match(nid):
        die("--id %r is not a node id; the shape is N-001 and the schema enforces it" % nid)
    if nid in known:
        die("node id %s already exists — nothing was written. Omit --id and one is "
            "allocated from the highest in use" % nid)

    new = {"id": nid, "title": title, "owner": args.owner, "status": "pending",
           "blocked_by": blocked, "serves": serves, "check": check, "evidence": None}
    touches = list(dict.fromkeys(t.strip() for t in (args.touches or []) if t.strip()))
    if touches:
        new["touches"] = touches
    nodes.append(new)
    # The edge lands WITH the node. Writing `blocked_by` and leaving `edges` for later is
    # what made every mid-run node a fake edge by construction.
    edges = graph.setdefault("edges", [])
    for b, payload in pairs:
        edges.append({"from": b, "to": nid, "payload": payload})
    revise(graph, "add", nid, why)
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


def cmd_coverage(graph, args):
    """The coverage relation, computed rather than walked by hand.

    `references/acceptance.md` defines the path a requirement takes — decision, spec
    section, contract and its failure behaviour, task, change, executed test, surface —
    and until this verb existed an agent walked it one REQ at a time from a checklist,
    which is the pipeline's own definition of a rule that should have been a mechanism.

    **Three of the four directions are here. The fourth is not, and this says so.**
    An evidence row that closes no requirement lives in `docs/evidence/verification.md`,
    which this script does not read; a report silent about that reads as the whole
    relation and is the more dangerous half.
    """
    if violations(graph):
        die("graph does not validate — run `validate` first", 1)
    nodes = graph.get("nodes") or []
    reqs = list(graph.get("requirements") or []) + list(graph.get("goal_clauses") or [])
    by_req = {r: [] for r in reqs}
    for n in nodes:
        by_req.setdefault(n.get("serves"), []).append(n)

    bad = []
    for r in reqs:
        served = by_req.get(r) or []
        if not served:
            bad.append(f"{r}: no node serves it")
            continue
        live = [n for n in served if n.get("status") != "parked"]
        marks = " ".join(f"{n['id']}({n.get('status')})" for n in served)
        if not live:
            bad.append(f"{r}: every node serving it is parked — {marks}. Covered on paper "
                       "and by nothing that will run")
        else:
            print(f"{r}  {marks}")

    for line in bad:
        print(line, file=sys.stderr)
    print("not read here: whether an evidence row in docs/evidence/verification.md closes "
          "no requirement — that is the fourth direction of this relation and it lives in "
          "the ledger, not the graph", file=sys.stderr)
    return 1 if bad else 0


def cmd_producer(graph, args):
    """What produced this proof — B-086.

    Every artifact this pipeline writes records what was done, what proved it, and whether
    a person looked. None recorded what PRODUCED it, so two runs six months apart under
    different generations of this doctrine leave indistinguishable coverage tables, and a
    defect traced to a doctrine change cannot be scoped to the runs that carried it.

    **Every field prints, and one that cannot be resolved says why.** An omitted field is
    indistinguishable from a field that was checked and found empty — the same rule the
    gate disclosures live by. The reason is what tells an operator whether the value is
    wirable or genuinely absent here.

    Four values the harness owns are read from the environment, because a script cannot
    know its own model or trace id. The names are a contract a project wires once; unset,
    each says so rather than guessing. `model` is deliberately not inferred: naming a
    vendor id anywhere in a shipped skill is forbidden, and inferring the wrong one is
    worse than saying nothing.
    """
    import hashlib

    def env(var):
        v = os.environ.get(var, "").strip()
        return v or f"unavailable: {var} is not set by this harness"

    def skill_version():
        # `plugin.json` sits two levels above the bundle in a plugin install and does not
        # exist at all in a plain-skill install — so this resolves on one channel and
        # honestly does not on the others.
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        man = os.path.join(os.path.dirname(os.path.dirname(here)),
                           ".claude-plugin", "plugin.json")
        if not os.path.isfile(man):
            return ("unavailable: no plugin manifest above this bundle — the skill is "
                    "installed as a plain directory, which carries no version of its own")
        try:
            with open(man, encoding="utf-8") as fh:
                v = json.load(fh).get("version")
            return f"task-pipeline@{v}" if v else "unavailable: the manifest states no version"
        except (OSError, ValueError) as e:
            return f"unavailable: the plugin manifest is unreadable — {e}"

    def config_digest():
        for name in ("pipeline.json", os.path.join(".task-pipeline", "pipeline.json")):
            if os.path.isfile(name):
                with open(name, "rb") as fh:
                    return "sha256:" + hashlib.sha256(fh.read()).hexdigest()[:16]
        return ("unavailable: no pipeline.json in this directory — the run's stage and gate "
                "configuration cannot be fingerprinted")

    def commit():
        import subprocess
        try:
            r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
        except OSError as e:
            return f"unavailable: git is not runnable here — {e}"
        out = r.stdout.strip()
        if r.returncode or not out:
            return "unavailable: not inside a git checkout, so no commit identifies the tree"
        return out

    for key, val in (("actor", env("TASK_PIPELINE_ACTOR")),
                     ("model", env("TASK_PIPELINE_MODEL")),
                     ("runtime", env("TASK_PIPELINE_RUNTIME")),
                     ("skill", skill_version()),
                     ("config", config_digest()),
                     ("commit", commit()),
                     ("trace", env("TASK_PIPELINE_TRACE"))):
        print(f"{key}: {val}")
    return 0


def cmd_doctrine(graph, args):
    """Which doctrine this run actually read — B-061.

    The bundle is 38 reference files. A run reads some subset and nothing recorded which,
    so **a skipped file and a read one were indistinguishable** — the class every guard in
    this repository exists to catch, left standing over the doctrine itself.

    `read:` lines are written by a hook rather than by the agent, for the same reason `gate:`
    is: a claim about what somebody read, written by the party the claim is about, is not
    evidence.

    **And that is an intent, not a proof, so every line here is reported as UNATTESTED.**
    The ledger is `.task-pipeline/run.md` — the file the agent appends to at every stage —
    so nothing in it distinguishes a hook-written line from one an agent typed. The doctrine
    said *hook-written, never agent-written*, which is a provenance claim this script cannot
    check and no format here carries; B-014's class, committed by the mechanism built to
    close it. Until the ledger can attest a writer, the honest output is the count plus the
    word: read as *this is what the ledger says, and the ledger cannot say who wrote it*.

    **The one rule that matters here: no `read:` lines means UNMEASURED, never «read
    nothing».** Zero would be the reassuring answer to a question nobody asked, and this
    verb exists because that shape had gone unnoticed for a whole bundle.

    It reports and never scores. There is no per-file floor in this pipeline, and inventing
    one here would be a doctrine decision smuggled in as a measurement — stage 0's
    mandatory items are the floor that exists, and they are not per-file.
    """
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    refs_dir = os.path.join(here, "references")
    if not os.path.isdir(refs_dir):
        die("no references/ beside this script — cannot say what the bundle holds", 2)
    refs = sorted(f for f in os.listdir(refs_dir) if f.endswith(".md"))

    ledger = args.ledger
    if not os.path.isfile(ledger):
        print(f"doctrine: unmeasured — no run ledger at {ledger}")
        print(f"          the bundle holds {len(refs)} reference files; nothing records "
              "which of them this run opened")
        return 0

    read = set()
    with open(ledger, encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("read:"):
                continue
            val = line.split(":", 1)[1].strip().split(" ")[0]
            read.add(os.path.basename(val))
    read &= set(refs)

    if not read:
        # The whole point. An empty set here has two causes with opposite meanings and the
        # ledger cannot tell them apart, so this says so instead of printing 0.
        print("doctrine: unmeasured — the ledger carries no `read:` lines")
        print("          Either the hook that writes them is not installed (see "
              "templates/hooks.example.json) or this run opened no doctrine at all. Those "
              "are opposite facts and nothing here can separate them, so neither is claimed.")
        print(f"          the bundle holds {len(refs)} reference files")
        return 0

    unread = [r for r in refs if r not in read]
    print(f"doctrine: {len(read)} of {len(refs)} reference files read — unattested")
    print("          unattested: the ledger is the file the agent appends to at every stage, "
          "so nothing in it proves the hook wrote these lines rather than an agent. The "
          "count is what the ledger says; who wrote it is not recorded.")
    print("          a disclosure: no floor, no direction, never a target. A run that needs "
          "four files and reads four is not worse than one that reads thirty.")
    for r in unread:
        print(f"          unread: {r}")
    return 0


def cmd_certify(graph, args):
    """Require three independent tier reports, then emit the verdict `close` consumes.

    This is a gate in FRONT of `close`, not a replacement for it. `close`'s contract
    is unchanged and its seven keys are still the only thing that moves the graph —
    what changed is that the verdict is now assembled from three readings at
    different distances instead of written from one.

    **The round is recorded whether it passes or fails.** A failing round that
    wrote nothing would erase the only evidence that a node is churning, which is
    the number the ceiling below reads. The node stays `pending` on a failure; the
    round count is the trail.

    **The ceiling measures rather than stops** — `references/loop-guard.md`. At the
    ceiling `certify` still runs and still tells the truth about the tiers; what it
    adds is the name of the tier that keeps failing, because a run spinning on one
    level needs the operator to see WHICH level, not to be halted.
    """
    guard(graph, args.graph)

    nid = args.node
    by_id = {n.get("id"): n for n in graph.get("nodes") or []}
    node = by_id.get(nid)
    if node is None:
        die("no node %s in this graph — nothing was written" % nid)
    if node.get("status") in TERMINAL:
        die("%s is already %s — certifying it again would overwrite the record of the "
            "close that already happened" % (nid, node.get("status")))
    open_blockers = [b for b in node.get("blocked_by") or []
                     if by_id.get(b, {}).get("status") not in TERMINAL]
    if open_blockers:
        die("%s waits on %s, which %s not closed — certifying work that could not have "
            "run certifies nothing" % (nid, ", ".join(open_blockers),
                                       "is" if len(open_blockers) == 1 else "are"))

    reports, bad = {}, []
    for path in args.tier:
        try:
            with open(path, encoding="utf-8") as fh:
                t = json.load(fh)
        except OSError as e:
            die("cannot read the tier report at %s — %s" % (path, e), 2)
        except ValueError as e:
            die("%s: not readable as JSON — %s" % (path, e))
        v = tier_violations(t)
        if v:
            bad += ["%s: %s" % (os.path.basename(path), line) for line in v]
            continue
        if t["node"] != nid:
            bad.append("%s: reports on %s while this certification is for %s — a report "
                       "about another node is not evidence about this one"
                       % (os.path.basename(path), t["node"], nid))
            continue
        if t["tier"] in reports:
            bad.append("%s: a second `%s` report — the three tiers are three distances, "
                       "and two readings at one distance leave another unread"
                       % (os.path.basename(path), t["tier"]))
            continue
        reports[t["tier"]] = t
    if bad:
        die("the tier reports are malformed — nothing was written:\n  " + "\n  ".join(bad))

    missing = [x for x in TIERS if x not in reports]
    if missing:
        die("certification is missing the %s report(s) — all three are required, because "
            "the level nobody read is the level the defect survives at"
            % ", ".join("`%s`" % m for m in missing))

    # The stamp, read here and never accepted from a report — same law as `close`.
    import subprocess
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
        head = r.stdout.strip() if r.returncode == 0 else ""
    except OSError:
        head = ""

    prior = node.get("certification") or {}
    round_no = int(prior.get("round") or 0) + 1
    tiers_now = {x: reports[x]["verdict"] for x in TIERS}
    history = list(prior.get("history") or []) + [tiers_now]
    node["certification"] = {
        "round": round_no,
        "tiers": tiers_now,
        "at": head or "unavailable — not inside a git checkout",
        "history": history,
    }

    failed = [x for x in TIERS if tiers_now[x] == "fail"]

    # Churn, measured. A tier that has failed in every round so far is the one the
    # operator needs named; counting it here is what makes the loop visible.
    churning = [x for x in TIERS
                if len(history) >= 2 and all(h.get(x) == "fail" for h in history)]

    save(args.graph, graph)

    if failed:
        print("%s: certification round %d FAILED at %s"
              % (nid, round_no, ", ".join("`%s`" % f for f in failed)), file=sys.stderr)
        for tier in failed:
            for f in reports[tier]["findings"]:
                if f.get("severity") != "breaks":
                    continue
                print("  [%s] %s — %s" % (tier, f["where"], f["what"]), file=sys.stderr)
                print("      fix:   %s" % f.get("fix", "(not stated)"), file=sys.stderr)
                print("      check: %s" % f["check"], file=sys.stderr)
        if round_no >= args.ceiling:
            print("\n%s has been certified %d time(s), at or over the ceiling of %d."
                  % (nid, round_no, args.ceiling), file=sys.stderr)
            if churning:
                print("The same tier has failed every round: %s. That is not a fix "
                      "away — the level itself is being misread, or the node is the "
                      "wrong shape. references/loop-guard.md."
                      % ", ".join("`%s`" % c for c in churning), file=sys.stderr)
            else:
                print("No single tier is failing every round, so this is churn across "
                      "levels rather than one stuck level.", file=sys.stderr)
        print("\nThe node stays open. Round %d is recorded on it." % round_no,
              file=sys.stderr)
        return 1

    # Passed at all three. Assemble the canonical verdict.
    #
    # The mapping is deliberate and uses no field for something it does not mean:
    #   confirms      -> done          (asked for, and now true)
    #   not_examined  -> not_verified  (present, and no check touched it)
    #   risk findings -> blockers      (found, judged survivable, and named, which is
    #                                   exactly what `can_continue_around: true` says)
    verdict = {
        "node": nid,
        "done": [c for x in TIERS for c in reports[x]["confirms"]],
        "not_done": [],
        "not_verified": ["%s: %s" % (x, n)
                         for x in TIERS for n in reports[x]["not_examined"]],
        "blockers": [
            {"what": "%s (%s, found by the `%s` tier)" % (f["what"], f["where"], x),
             "blocks": [], "can_continue_around": True}
            for x in TIERS for f in reports[x]["findings"]
            if f.get("severity") == "risk"
        ],
        "replan": {"possible": True, "add": [], "park": [],
                   "why": "certified at all three tiers in round %d" % round_no},
        "evidence": ["%s: %s" % (x, e) for x in TIERS for e in reports[x]["evidence"]],
    }
    # Checked against the same gate `close` will apply, HERE, so a certification
    # cannot hand the run a verdict its own consumer refuses.
    broken = verdict_violations(verdict)
    if broken:
        die("all three tiers passed and the assembled verdict is still malformed — this "
            "is a defect in `certify`, not in the reports:\n  " + "\n  ".join(broken))

    out = args.verdict_out or os.path.join(os.path.dirname(args.graph) or ".",
                                          "verdict-%s.json" % nid)
    tmp = out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(verdict, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, out)
    print("%s: certified at unit, seam and product in round %d" % (nid, round_no))
    print("verdict written to %s — close it with:" % out)
    print("  graph.py close --verdict %s" % out)
    return 0


def cmd_close(graph, args):
    """Consume a verdict, close one node, and re-plan — T-5, REQ-007.

    The verdict is the one artifact in this design a human does not read before it acts, so
    its shape is checked rather than trusted. `verdict_violations()` had no CLI verb until
    now: the gate this module's docstring calls *the thing `close` consumes* was reachable
    only from the test suite, while `agents/verifier.md` told an agent to run this command.

    **`close` stamps the commit; the verifier never supplies it.** Evidence is prose, and a
    verdict written after the tree moved is evidence about a different tree. An agent cannot
    claim the wrong commit if it is never the one naming it. Outside a checkout the stamp
    says `unavailable` and why — canon 9a.

    **A stop closes the node and refuses the NEXT step.** `replan.possible: false` means the
    run cannot continue around what it found, not that the work just verified did not
    happen. Exiting 0 there would let the loop carry on past a stop; discarding the close
    would throw away a verdict somebody earned.
    """
    guard(graph, args.graph)
    try:
        with open(args.verdict, encoding="utf-8") as fh:
            v = json.load(fh)
    except OSError as e:
        die("cannot read the verdict at %s — %s" % (args.verdict, e), 2)
    except ValueError as e:
        die("%s: not readable as JSON — %s" % (args.verdict, e))

    bad = verdict_violations(v)
    if bad:
        die("the verdict is malformed — nothing was written:\n  " + "\n  ".join(bad))

    nid = v["node"]
    by_id = {n.get("id"): n for n in graph.get("nodes") or []}
    node = by_id.get(nid)
    if node is None:
        die("no node %s in this graph — nothing was written" % nid)
    if node.get("status") in TERMINAL:
        die("%s is already %s — a second close would overwrite the record of the first"
            % (nid, node.get("status")))
    open_blockers = [b for b in node.get("blocked_by") or []
                     if by_id.get(b, {}).get("status") not in TERMINAL]
    if open_blockers:
        die("%s waits on %s, which %s not closed — a verdict about work that could not have "
            "run is a verdict about nothing" % (nid, ", ".join(open_blockers),
                                                "is" if len(open_blockers) == 1 else "are"))

    # The stamp. Read here, never accepted from the verdict.
    import subprocess
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
        head = r.stdout.strip() if r.returncode == 0 else ""
    except OSError:
        head = ""
    stamp = ("observed at " + head) if head else \
        "observed at unavailable — not inside a git checkout, so no commit identifies the tree"

    node["status"] = "done"
    node["evidence"] = list(v["evidence"]) + [stamp]

    rp = v["replan"]
    why = (rp.get("why") or "").strip()
    added, parked = [], []
    for spec in rp.get("add") or []:
        title = str(spec.get("title", "")).strip()
        owner = str(spec.get("owner", "implementer")).strip()
        serves = str(spec.get("serves", node.get("serves"))).strip()
        check = str(spec.get("check", "")).strip()
        if not title:
            die("replan.add carries an entry with no title — nothing was written")
        if not check:
            die("replan.add carries an entry with no check — nothing was written")
        if owner not in ROLES:
            die("replan.add names owner %r, which is not a role this pipeline ships" % owner)
        new_id = next_id({n.get("id") for n in graph["nodes"]})
        graph["nodes"].append({"id": new_id, "title": title, "owner": owner,
                               "status": "pending", "blocked_by": [], "serves": serves,
                               "check": check, "evidence": None})
        revise(graph, "add", new_id, why or ("re-planned by the verdict on " + nid))
        added.append(new_id)
    for pid in rp.get("park") or []:
        target = by_id.get(pid)
        if target is None:
            die("replan.park names %s, which is not in this graph — nothing was written" % pid)
        if target.get("status") in TERMINAL:
            continue
        if not why:
            die("replan.park names %s and the verdict gives no `why` — a park without a "
                "reason is indistinguishable from work quietly dropped" % pid)
        target["status"] = "parked"
        target["parked_reason"] = why
        revise(graph, "park", pid, why)
        parked.append(pid)

    revise(graph, "close", nid, why or "closed with no re-plan")

    bad = violations(graph)
    if bad:
        die("closing %s would break the graph — nothing was written:\n  %s"
            % (nid, "\n  ".join(bad)))
    save(args.graph, graph)

    goal = (graph.get("goal") or "").strip()
    print("goal: %s" % (goal or "unstated"))
    print("%s closed · added %d · parked %d · frontier %d"
          % (nid, len(added), len(parked), len(frontier(graph))))
    if v.get("not_verified"):
        print("not verified: " + "; ".join(str(x) for x in v["not_verified"]))
    else:
        # Canon 9a, one artifact over: an empty list is a claim with a subject, and it says
        # so rather than printing nothing.
        print("not verified: none within the scope this verdict names")
    if rp.get("possible") is False:
        print("STOP — the run cannot continue around what this verdict found: %s"
              % (why or "no reason given"), file=sys.stderr)
        return 1
    return 0


VERBS = {
    "validate": (cmd_validate, "every invariant a schema cannot state"),
    "next": (cmd_next, "the frontier, ordered by what it unblocks"),
    "goal": (cmd_goal, "the release goal this graph serves"),
    "doctrine": (cmd_doctrine, "which of the bundle's reference files this run opened"),
    "producer": (cmd_producer, "what produced this proof: actor, model, runtime, skill, "
                               "config digest, commit, trace"),
    "coverage": (cmd_coverage, "every requirement and the nodes serving it; exits 1 on a gap"),
    "add": (cmd_add, "add a node mid-run"),
    "park": (cmd_park, "park a node, carrying the reason"),
    "certify": (cmd_certify, "require three independent tier reports, then emit "
                             "the verdict `close` consumes"),
    "close": (cmd_close, "consume a verdict, close one node and re-plan"),
}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="graph.py", description=__doc__.split("\n")[0])
    # `--graph` hangs off every verb rather than off the top level, so it can be passed
    # after the verb — which is the order every caller writes without thinking.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--graph", default=os.path.join(".task-pipeline", "graph.json"))
    sub = ap.add_subparsers(dest="verb", required=True)

    # The subparsers are built FROM the dispatch table, so a verb argparse accepts and the
    # dispatch lacks cannot exist. It could before: renaming one key raised KeyError, which
    # is a traceback where a named refusal belongs.
    made = {n: sub.add_parser(n, parents=[common], help=h)
            for n, (_, h) in VERBS.items()}

    p_add = made["add"]
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--owner", required=True)
    p_add.add_argument("--serves", required=True)
    p_add.add_argument("--check", required=True,
                       help="the command that closes this node, or the judge where no "
                            "command can decide it — the verifier runs it and reports its "
                            "output as the evidence row")
    p_add.add_argument("--blocked-by", dest="blocked_by", action="append", default=[])
    p_add.add_argument("--carries", action="append", default=[],
                       help="what each --blocked-by hands over; pairs in the order written")
    p_add.add_argument("--why", required=True,
                       help="why this node appeared mid-run — it enters the revision log")
    p_add.add_argument("--id", default=None, help="omit to allocate the next one")
    p_add.add_argument("--touches", action="append", default=[],
                       help="a path, register or resource this node mutates; repeat per target")

    made["doctrine"].add_argument(
        "--ledger", default=os.path.join(".task-pipeline", "run.md"),
        help="the run ledger whose `read:` lines record what was opened")

    made["close"].add_argument("--verdict", required=True,
                               help="path to the verifier's seven-key verdict JSON")

    p_cert = made["certify"]
    p_cert.add_argument("--node", required=True, help="the node being certified")
    p_cert.add_argument("--tier", action="append", required=True, default=[],
                        help="path to one tier report; pass three times, one per tier")
    p_cert.add_argument("--verdict-out", dest="verdict_out", default=None,
                        help="where to write the assembled verdict (default: beside the graph)")
    p_cert.add_argument("--ceiling", type=int, default=3,
                        help="rounds after which the output names the churning tier; it "
                             "measures rather than stops (references/loop-guard.md)")

    p_park = made["park"]
    p_park.add_argument("node")
    # `required=True` makes the MISSING flag a usage error (exit 2). The empty and
    # whitespace ones reach `cmd_park`, which refuses them — argparse cannot tell a flag
    # that was given from a reason that was written, and only the second is REQ-012.
    p_park.add_argument("--reason", required=True)

    args = ap.parse_args(argv)
    verbs = {k: v[0] for k, v in VERBS.items()}
    if args.verb in NO_GRAPH:
        return verbs[args.verb](None, args)
    if args.verb in ("add", "park", "close", "certify"):
        # The READ happens inside the lock too. Loading first and locking second is the
        # same lost update with an extra step: the stale copy is already in memory.
        with held(args.graph):
            return verbs[args.verb](shape(load(args.graph), args.graph), args)
    return verbs[args.verb](shape(load(args.graph), args.graph), args)


if __name__ == "__main__":
    sys.exit(main())
