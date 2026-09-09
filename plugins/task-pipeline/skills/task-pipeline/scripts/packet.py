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

    status = env.get("status")
    if status not in RESULT_STATUSES:
        out.append(f"status {status!r} is not one of {sorted(RESULT_STATUSES)}")
    elif status == "completed" and failing:
        out.append(f"status 'completed' beside {failing} failing check(s) — a completed "
                   "attempt with red checks is a contradiction, not a nuance")

    return out


def canon(packet):
    """Canonical bytes: sorted keys, stable separators — same packet, same hash."""
    return json.dumps(packet, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def main(argv):
    if len(argv) < 3 or argv[1] not in ("validate", "canon", "validate-result"):
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
