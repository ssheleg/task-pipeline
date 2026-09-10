#!/usr/bin/env python3
"""Validate an execution packet — the family's versioned task/context contract.

`execution-packet.schema.json` states the shape; this script is the
dependency-free runtime half every consumer runs BEFORE acting on a packet
(CTX-01). Python stdlib only, like everything else here: a validator that
needs a package install is a validator half the hosts never run.

    python3 scripts/packet.py validate <packet.json>   # exit 0 clean, 1 rejected
    python3 scripts/packet.py canon <packet.json>      # canonical bytes digest
    python3 scripts/packet.py validate-result <envelope.json> \\
        [--current-revision N] [--current-fence F]     # the answer half (CTX-01.02)

Three rejections are the contract's whole point, each watched failing in
`test/audit_regressions/ctx-01.01.py`:

* an UNKNOWN MANDATORY MAJOR — a consumer that does not know
  `execution-packet/9` must refuse the packet, not skim the fields it likes;
* a MISSING REF/DIGEST — an input or baseline without its sha256 cannot be
  checked fresh, and stale context must block, never silently pass;
* an UNBOUND DECISION — a decision named without address+digest is a rumour,
  and two agents reading rumours build two different things from one plan.

Round-trip: `canon` serializes with sorted keys and stable separators, so the
same packet always hashes the same — the id a receipt can carry.

The RESULT half (`execution-result.schema.json`) answers with an AttemptGrant
and a ResultEnvelope, and two rejections carry that contract's whole point:
a bare boolean is NOT a grant (it names no issuer, revision or fence), and a
candidate built against an older revision than the current one is STALE — it
re-plans, it never lands as current. A grant whose fence the authority has
since superseded is rejected the same way.
"""
import hashlib
import json
import re
import sys

KNOWN_MAJORS = {1}
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
EDIT_MODES = {"Edit", "Create", "Create_or_extend"}
DEP_KINDS = {"data", "control", "resource"}


OUTPUT_KINDS = {"artifact", "report", "decision", "metric"}


def _ref_problems(ref, where, need_id=False):
    out = []
    if not isinstance(ref, dict):
        return [f"{where}: not an object"]
    if need_id and not ref.get("id"):
        out.append(f"{where}: decision without an id")
    if not ref.get("address"):
        out.append(f"{where}: missing address — a ref that points nowhere")
    sha = ref.get("sha256", "")
    if not sha:
        out.append(f"{where}: missing sha256 digest — freshness cannot be checked, "
                   "so this blocks dispatch")
    elif not SHA_RE.match(str(sha)):
        out.append(f"{where}: sha256 is not 64 hex chars")
    return out


def problems(packet):
    """Every reason this packet must not dispatch. Empty list = valid."""
    out = []
    if not isinstance(packet, dict):
        return ["the packet is not a JSON object"]

    version = str(packet.get("schema_version", ""))
    m = re.match(r"^execution-packet/(\d+)$", version)
    if not m:
        out.append(f"schema_version {version!r} is not 'execution-packet/<major>' — "
                   "a packet without a mandatory version is unversioned, rejected")
    elif int(m.group(1)) not in KNOWN_MAJORS:
        out.append(f"schema_version major {m.group(1)} is unknown to this consumer "
                   f"(knows: {sorted(KNOWN_MAJORS)}) — rejected, never skimmed; "
                   "upgrade the consumer or re-issue the packet at a known major")

    for field in ("id", "module", "intent"):
        if not packet.get(field):
            out.append(f"missing {field}")

    inputs = packet.get("inputs")
    if not isinstance(inputs, list):
        out.append("inputs must be a list (empty is allowed, absent is not)")
    else:
        for i, ref in enumerate(inputs):
            out.extend(_ref_problems(ref, f"inputs[{i}]"))

    decisions = packet.get("decision_refs")
    if not isinstance(decisions, list):
        out.append("decision_refs must be a list (empty is allowed, absent is not)")
    else:
        for i, ref in enumerate(decisions):
            out.extend(_ref_problems(ref, f"decision_refs[{i}]", need_id=True))

    scope = packet.get("source_scope")
    if not isinstance(scope, dict) or not isinstance(scope.get("edit_targets"), list):
        out.append("source_scope.edit_targets must be a list — a packet that names no "
                   "files it may touch has an unbounded blast radius")
    else:
        for i, t in enumerate(scope["edit_targets"]):
            where = f"source_scope.edit_targets[{i}]"
            if not isinstance(t, dict) or not t.get("address"):
                out.append(f"{where}: missing address")
                continue
            mode = t.get("mode")
            if mode not in EDIT_MODES:
                out.append(f"{where}: mode {mode!r} is not one of {sorted(EDIT_MODES)}")
            if mode == "Edit":
                sha = t.get("baseline_sha256", "")
                if not sha:
                    out.append(f"{where}: an Edit target without baseline_sha256 — "
                               "'the source moved under the plan' would be undetectable")
                elif not SHA_RE.match(str(sha)):
                    out.append(f"{where}: baseline_sha256 is not 64 hex chars")

    budgets = packet.get("budgets")
    if not isinstance(budgets, dict) or not budgets:
        out.append("budgets must carry at least one bound")
    else:
        cb = budgets.get("context_bytes")
        if cb is not None and (not isinstance(cb, int) or cb < 1):
            out.append("budgets.context_bytes must be a positive integer")

    seen_edges = set()
    for i, dep in enumerate(packet.get("dependencies") or []):
        where = f"dependencies[{i}]"
        if not isinstance(dep, dict) or not dep.get("task_id"):
            out.append(f"{where}: missing task_id")
            continue
        if dep.get("kind") not in DEP_KINDS:
            out.append(f"{where}: kind {dep.get('kind')!r} is not one of {sorted(DEP_KINDS)}")
        if not dep.get("rationale"):
            out.append(f"{where}: missing rationale — an edge nobody can explain is an "
                       "edge nobody dares remove or trust")
        edge = (dep["task_id"], dep.get("kind"))
        if edge in seen_edges:
            out.append(f"{where}: duplicate edge to {dep['task_id']} ({dep.get('kind')})")
        seen_edges.add(edge)
        # A CONTROL edge with no satisfaction is VALID and PRESERVED: ordering is
        # its whole payload. Only data/resource edges owe a satisfaction.
        if dep.get("kind") in ("data", "resource") and not dep.get("satisfaction"):
            out.append(f"{where}: a {dep['kind']} edge without satisfaction — what would "
                       "mark it met? A control edge may omit this; a payload edge may not")

    return out


RESULT_MAJORS = {1}
CHECK_STATUSES = {"PASS", "FAIL", "ERROR", "NOT_RUN"}
EVIDENCE_CLASSES = {"fact", "defect", "unknown_effect"}
RESULT_STATUSES = {"completed", "partial", "blocked", "abandoned"}


def result_problems(env, current_revision=None, current_fence=None):
    """Every reason this envelope must not land. Empty list = valid."""
    out = []
    if not isinstance(env, dict):
        return ["the envelope is not a JSON object"]

    version = str(env.get("schema_version", ""))
    m = re.match(r"^execution-result/(\d+)$", version)
    if not m:
        out.append(f"schema_version {version!r} is not 'execution-result/<major>' — rejected")
    elif int(m.group(1)) not in RESULT_MAJORS:
        out.append(f"schema_version major {m.group(1)} is unknown to this consumer "
                   f"(knows: {sorted(RESULT_MAJORS)}) — rejected, never skimmed")

    grant = env.get("grant")
    if isinstance(grant, bool) or grant is None or not isinstance(grant, dict):
        out.append(f"grant is {grant!r} — a boolean confirmation is not a grant: it names "
                   "no issuer, no revision, no fence; nothing a later reader could check")
    else:
        for field in ("grant_id", "packet_id", "holder"):
            if not grant.get(field):
                out.append(f"grant.{field} is missing")
        for field in ("revision", "fence"):
            if not isinstance(grant.get(field), int):
                out.append(f"grant.{field} must be an integer — the grant is checkable "
                           "or it is not a grant")
        if env.get("packet_id") and grant.get("packet_id") \
                and env["packet_id"] != grant["packet_id"]:
            out.append("the envelope and its grant name different packets")
        if current_fence is not None and isinstance(grant.get("fence"), int) \
                and grant["fence"] < current_fence:
            out.append(f"grant fence {grant['fence']} is superseded (current {current_fence}) "
                       "— exclusivity was lost mid-flight; this result must not land")

    rev = env.get("built_against_revision")
    if not isinstance(rev, int):
        out.append("built_against_revision must be an integer")
    elif current_revision is not None and rev < current_revision:
        out.append(f"STALE candidate: built against revision {rev}, current is "
                   f"{current_revision} — re-plan, never land as current")

    cand = env.get("candidate")
    if not isinstance(cand, dict) or not isinstance(cand.get("changed"), list):
        out.append("candidate.changed must be a list of content-addressed paths")
    else:
        for i, row in enumerate(cand["changed"]):
            if not isinstance(row, dict) or not row.get("address"):
                out.append(f"candidate.changed[{i}]: missing address")
            elif not SHA_RE.match(str(row.get("sha256", ""))):
                out.append(f"candidate.changed[{i}]: missing or malformed sha256")

    checks = env.get("checks")
    failing = 0
    if not isinstance(checks, list):
        out.append("checks must be a list (empty is allowed, absent is not)")
    else:
        for i, c in enumerate(checks):
            if not isinstance(c, dict) or not c.get("name") or not c.get("command"):
                out.append(f"checks[{i}]: needs name and command — an unnamed check "
                           "cannot be re-run")
                continue
            if c.get("status") not in CHECK_STATUSES:
                out.append(f"checks[{i}]: status {c.get('status')!r} is not one of "
                           f"{sorted(CHECK_STATUSES)} — NOT_RUN is a status, not a gap")
            elif c["status"] in ("FAIL", "ERROR"):
                failing += 1

    for i, row in enumerate(env.get("evidence") or []):
        if not isinstance(row, dict) or row.get("class") not in EVIDENCE_CLASSES:
            out.append(f"evidence[{i}]: class must be one of {sorted(EVIDENCE_CLASSES)} — "
                       "fact, defect and unknown effect are three verdicts, never blended")

    secretish = re.compile(r"(?i)^(?:.*[_-])?(token|secret|password|passwd|api[_-]?key|"
                           r"apikey|credential|authorization|cookie|private[_-]?key)s?$")
    for i, row in enumerate(env.get("outputs") or []):
        if not isinstance(row, dict) or not row.get("name") or not row.get("address"):
            out.append(f"outputs[{i}]: needs name, kind, address, sha256 — an untyped "
                       "output cannot be consumed by digest")
            continue
        if row.get("kind") not in OUTPUT_KINDS:
            out.append(f"outputs[{i}]: kind {row.get('kind')!r} is not one of "
                       f"{sorted(OUTPUT_KINDS)}")
        if not SHA_RE.match(str(row.get("sha256", ""))):
            out.append(f"outputs[{i}]: missing or malformed sha256")
        if secretish.match(str(row["name"])):
            out.append(f"outputs[{i}]: {row['name']!r} names a credential — a result "
                       "outlives its session exactly like the packet; reference the "
                       "store by name, never carry the value (FIX-PF-05.03)")
    pd = env.get("packet_digest")
    if pd is not None and not SHA_RE.match(str(pd)):
        out.append("packet_digest: malformed — the tie to the dispatch packet must be "
                   "a sha256 or absent, never a guess")
    for i, row in enumerate(env.get("consumed") or []):
        if not isinstance(row, dict) or not row.get("name")                 or not SHA_RE.match(str(row.get("sha256", ""))):
            out.append(f"consumed[{i}]: needs name + sha256 — freshness is a comparison, "
                       "and an unpinned consumption cannot be compared")

    status = env.get("status")
    if status not in RESULT_STATUSES:
        out.append(f"status {status!r} is not one of {sorted(RESULT_STATUSES)}")
    elif status == "completed" and failing:
        out.append(f"status 'completed' beside {failing} failing check(s) — a completed "
                   "attempt with red checks is a contradiction, not a nuance")

    return out


def consumed_stale(env, current_outputs):
    """Which of this result's consumed inputs have moved (FIX-PF-05.03).

    `current_outputs`: {name: sha256} — the predecessors' outputs as they are
    NOW. A name whose digest differs is returned; a non-empty list means this
    result is STALE and the node rebuilds at a new revision. A consumed name
    the predecessors no longer produce is stale too — an input that vanished
    is not fresher than one that changed.
    """
    stale = []
    for row in env.get("consumed") or []:
        name = row.get("name")
        if current_outputs.get(name) != row.get("sha256"):
            stale.append(name)
    return stale


def graph_problems(packets):
    """Closure over a packet SET: unique ids, every edge resolves, no cycles.
    A control edge participates in the cycle check like any other — ordering
    that loops is still a loop."""
    out = []
    if not isinstance(packets, list) or not packets:
        return ["the graph is not a non-empty list of packets"]
    ids = [p.get("id") for p in packets if isinstance(p, dict)]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        out.append(f"duplicate packet id {dup!r} — two packets, one name, no arbitration")
    known = set(ids)
    edges = {}
    for p in packets:
        if not isinstance(p, dict):
            continue
        edges[p.get("id")] = []
        for dep in p.get("dependencies") or []:
            tid = dep.get("task_id") if isinstance(dep, dict) else None
            if tid is None:
                continue
            if tid not in known:
                out.append(f"{p.get('id')}: depends on {tid!r}, which is not in the graph")
                continue
            edges[p.get("id")].append(tid)
    state = {}
    def visit(node, stack):
        state[node] = "visiting"
        for nxt in edges.get(node, []):
            if state.get(nxt) == "visiting":
                cycle = stack[stack.index(nxt):] + [nxt] if nxt in stack else [node, nxt]
                out.append("cycle: " + " -> ".join(cycle))
                continue
            if nxt not in state:
                visit(nxt, stack + [nxt])
        state[node] = "done"
    for node in edges:
        if node not in state:
            visit(node, [node])
    return out


def canon(packet):
    """Canonical bytes: sorted keys, stable separators — same packet, same hash."""
    return json.dumps(packet, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def main(argv):
    if len(argv) < 3 or argv[1] not in ("validate", "canon", "validate-result",
                                        "validate-graph"):
        print(__doc__.strip().splitlines()[0])
        print("usage: packet.py validate <packet.json> | packet.py canon <packet.json> | "
              "packet.py validate-result <envelope.json> [--current-revision N] "
              "[--current-fence F]")
        return 2
    try:
        with open(argv[2], encoding="utf-8") as fh:
            packet = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"REJECTED: cannot read the packet — {exc}")
        return 1
    if argv[1] == "validate-graph":
        found = graph_problems(packet)
        for p_ in packet if isinstance(packet, list) else []:
            for pr in problems(p_) if isinstance(p_, dict) else []:
                found.append(f"{p_.get('id')}: {pr}")
        if found:
            for pr in found:
                print(f"REJECTED: {pr}")
            return 1
        n_ctrl = sum(1 for p_ in packet for dep in (p_.get("dependencies") or [])
                     if dep.get("kind") == "control")
        print(f"ok: {len(packet)} packet(s), acyclic, every edge resolves; "
              f"{n_ctrl} control edge(s) preserved")
        return 0
    if argv[1] == "validate-result":
        opts = argv[3:]
        current_revision = current_fence = None
        while opts:
            flag = opts.pop(0)
            if flag == "--current-revision" and opts:
                current_revision = int(opts.pop(0))
            elif flag == "--current-fence" and opts:
                current_fence = int(opts.pop(0))
            else:
                print(f"unknown option: {flag}")
                return 2
        found = result_problems(packet, current_revision, current_fence)
        if found:
            for pr in found:
                print(f"REJECTED: {pr}")
            return 1
        checks = packet.get("checks") or []
        not_run = sum(1 for c in checks if c.get("status") == "NOT_RUN")
        green = sum(1 for c in checks if c.get("status") == "PASS")
        print(f"ok: {packet['packet_id']} ({packet['status']}) — {green} PASS, "
              f"{not_run} NOT_RUN of {len(checks)} check(s); "
              f"revision {packet['built_against_revision']}, fence {packet['grant']['fence']}")
        return 0
    if argv[1] == "canon":
        bytes_ = canon(packet)
        if json.loads(bytes_.decode("utf-8")) != packet:
            print("REJECTED: the packet does not round-trip canonically")
            return 1
        print(hashlib.sha256(bytes_).hexdigest())
        return 0
    found = problems(packet)
    if found:
        for p in found:
            print(f"REJECTED: {p}")
        return 1
    print(f"ok: {packet['id']} ({packet['schema_version']}) — "
          f"{len(packet['inputs'])} input(s), {len(packet['decision_refs'])} decision(s), "
          f"{len(packet['source_scope']['edit_targets'])} edit target(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
