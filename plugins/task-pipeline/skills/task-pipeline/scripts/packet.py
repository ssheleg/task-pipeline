#!/usr/bin/env python3
"""Validate an execution packet — the family's versioned task/context contract.

`execution-packet.schema.json` states the shape; this script is the
dependency-free runtime half every consumer runs BEFORE acting on a packet
(CTX-01). Python stdlib only, like everything else here: a validator that
needs a package install is a validator half the hosts never run.

    python3 scripts/packet.py validate <packet.json>   # exit 0 clean, 1 rejected
    python3 scripts/packet.py canon <packet.json>      # canonical bytes digest

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


def canon(packet):
    """Canonical bytes: sorted keys, stable separators — same packet, same hash."""
    return json.dumps(packet, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def main(argv):
    if len(argv) != 3 or argv[1] not in ("validate", "canon"):
        print(__doc__.strip().splitlines()[0])
        print("usage: packet.py validate <packet.json> | packet.py canon <packet.json>")
        return 2
    try:
        with open(argv[2], encoding="utf-8") as fh:
            packet = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"REJECTED: cannot read the packet — {exc}")
        return 1
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
