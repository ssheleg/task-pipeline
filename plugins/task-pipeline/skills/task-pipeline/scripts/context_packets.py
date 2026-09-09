#!/usr/bin/env python3
"""Finding → parent mapper — the first stage of the packet compiler (CTX-02.01).

An audit report is a list of findings; a plan is a list of parent tasks. This
stage turns one into the other WITHOUT losing anything on the way, and its
contract is three sentences:

* **The id is derived, never invented.** A finding `RT-01` maps to parent
  `FIX-RT-01` on every compile, whatever order the report arrives in — a
  positional id renumbers when a row is inserted, and a renumbered id orphans
  every receipt that cited the old one. Capability requests (work the user
  asked for that no finding demanded) carry their own explicit ids.
* **Evidence, limits and priority are separate fields from status.** A parent
  is born `parent_planned` with `revision` 1; nothing a finding carries can
  smuggle a status or a revision in — approval, fact and outcome do not
  promote each other (parent decision D03/D04).
* **No finding is dropped, silently or otherwise.** A row the mapper cannot
  map is a named problem that blocks the WHOLE compile — a partial plan that
  quietly lost two findings reads exactly like a complete one.

    python3 scripts/context_packets.py compile <report.json>          # parents JSON on stdout
    python3 scripts/context_packets.py verify <report.json> <parents.json>

`compile` is deterministic: same corpus → byte-identical output (sorted keys,
sorted parents, stable separators), so a repeated compile can be compared with
`diff` and a receipt can pin the plan by digest. `verify` recompiles and
refuses a parents file that dropped, duplicated or mutated a mapping.

The SECOND stage (CTX-02.02) compiles one parent + one outcome slice into a
dispatchable leaf packet, and its contract is the COLD READER's: the packet
alone, with no author history, must answer eight questions — goal, inputs,
decisions, scope, outputs, acceptance, guards, resume. A broad parent with an
unresolved decision dispatches NO leaf; a missing version or output contract
fails readiness; acceptance carries at least one positive and one negative
case; a budget cuts appendix material only and RECORDS the cut, never the
acceptance; and a slice is selected by explicit id — never by mtime, because
"newest file" is an authority nobody granted. Neither a design flow nor a
.design/TASKS.md becomes a parallel plan authority: leaves come from the plan
through this compiler or they are not leaves.

    python3 scripts/context_packets.py compile-leaf <parent.json> <slice.json>
    python3 scripts/context_packets.py readiness <leaf.json>

Python stdlib only, like every validator here.
"""
import json
import sys

SCHEMA_VERSION = "audit-plan/1"
PARENT_PREFIX = "FIX-"
BORN_STATUS = "parent_planned"
SMUGGLED = ("status", "revision", "dispatch_state")
COPIED = ("title", "module", "priority", "priority_rank", "priority_reason",
          "evidence", "limits")
REQUIRED = ("id", "title", "module", "priority")


def _row_problems(row, where, need_explicit_id):
    out = []
    if not isinstance(row, dict):
        return [f"{where}: not an object"]
    for field in REQUIRED:
        if not row.get(field):
            out.append(f"{where}: missing {field} — an unmappable row is a "
                       "problem, never a silent drop")
    for field in SMUGGLED:
        if field in row:
            out.append(f"{where}: carries `{field}` — status axes are separate "
                       "fields the mapper assigns, a report cannot smuggle one")
    if need_explicit_id and isinstance(row.get("id"), str) \
            and row["id"].startswith(PARENT_PREFIX):
        out.append(f"{where}: capability id {row['id']!r} collides with the "
                   f"derived `{PARENT_PREFIX}*` namespace findings own")
    return out


def _parent(row, parent_id, finding_id):
    p = {"schema_version": SCHEMA_VERSION, "id": parent_id,
         "finding_id": finding_id, "revision": 1, "status": BORN_STATUS}
    for field in COPIED:
        if field in row:
            p[field] = row[field]
    return p


def compile_parents(report):
    """Map a report to parents. Returns (result, problems) — a non-empty
    problems list means NO parents were produced: all or nothing."""
    problems = []
    if not isinstance(report, dict):
        return None, ["report: not an object"]
    findings = report.get("findings", [])
    capabilities = report.get("capabilities", [])
    for name, rows in (("findings", findings), ("capabilities", capabilities)):
        if not isinstance(rows, list):
            problems.append(f"report.{name}: not a list")
    if problems:
        return None, problems

    parents, seen, sources = [], {}, {}
    for i, row in enumerate(findings):
        where = f"findings[{i}]"
        rp = _row_problems(row, where, need_explicit_id=False)
        if rp:
            problems.extend(rp)
            continue
        pid = PARENT_PREFIX + str(row["id"])
        if pid in seen:
            problems.append(f"{where}: finding id {row['id']!r} already mapped "
                            f"from {seen[pid]} — a duplicate id is two claims "
                            "to one receipt")
            continue
        seen[pid] = where
        sources[pid] = str(row["id"])
        parents.append(_parent(row, pid, str(row["id"])))
    for i, row in enumerate(capabilities):
        where = f"capabilities[{i}]"
        rp = _row_problems(row, where, need_explicit_id=True)
        if rp:
            problems.extend(rp)
            continue
        pid = str(row["id"])
        if pid in seen:
            problems.append(f"{where}: id {pid!r} already mapped from {seen[pid]}")
            continue
        seen[pid] = where
        sources[pid] = None
        parents.append(_parent(row, pid, None))
    if problems:
        return None, problems

    parents.sort(key=lambda p: p["id"])
    return {"schema_version": "development-plan/3",
            "parents": parents,
            "trace": {p["id"]: sources[p["id"]] for p in parents}}, []


def canon(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")) + "\n"


def verify_parents(report, plan):
    """Recompile and compare: every original parent preserved, none invented,
    none mutated. Returns a list of problems, empty when faithful."""
    fresh, problems = compile_parents(report)
    if problems:
        return [f"the report itself does not compile: {p}" for p in problems]
    if not isinstance(plan, dict) or not isinstance(plan.get("parents"), list):
        return ["parents file: no parents list"]
    got = {p.get("id"): p for p in plan["parents"] if isinstance(p, dict)}
    want = {p["id"]: p for p in fresh["parents"]}
    out = []
    if len(got) != len(plan["parents"]):
        out.append("parents file: duplicate or malformed parent ids")
    for pid in sorted(set(want) - set(got)):
        out.append(f"{pid}: dropped — its finding is still in the report")
    for pid in sorted(set(got) - set(want)):
        out.append(f"{pid}: present in the plan but derived from no finding or "
                   "declared capability")
    for pid in sorted(set(want) & set(got)):
        if canon(want[pid]) != canon(got[pid]):
            out.append(f"{pid}: mutated relative to a faithful compile")
    return out


LEAF_SCHEMA = "execution-packet/1"
COLD_READER_QUESTIONS = ("goal", "inputs", "decisions", "scope", "outputs",
                         "acceptance", "guards", "resume")
SHA_RE_STR = r"^[0-9a-f]{64}$"


def _bound(ref):
    import re as _re
    return (isinstance(ref, dict) and ref.get("address")
            and _re.match(SHA_RE_STR, str(ref.get("sha256", ""))))


def compile_leaf(parent, slice_spec):
    """One parent + one outcome slice → one dispatchable leaf packet, or
    problems. All or nothing: an unresolved parent dispatches no leaf."""
    problems = []
    if not isinstance(parent, dict) or not isinstance(slice_spec, dict):
        return None, ["parent and slice must be objects"]
    decisions = slice_spec.get("decision_refs", parent.get("decision_refs", []))
    for i, ref in enumerate(decisions):
        if not _bound(ref):
            problems.append(
                f"decision_refs[{i}]: unresolved — a decision without address+"
                "digest is a rumour, and a broad unresolved parent dispatches "
                "no leaf")
    acceptance = slice_spec.get("acceptance", [])
    kinds = {a.get("kind") for a in acceptance if isinstance(a, dict)}
    if "positive" not in kinds or "negative" not in kinds:
        problems.append("acceptance: needs at least one positive and one "
                        "negative case — a slice provable only by success is "
                        "not testable")
    if not slice_spec.get("expected_result"):
        problems.append("expected_result: missing — every slice has a concrete "
                        "expected result")
    if not slice_spec.get("outputs"):
        problems.append("outputs: missing — a leaf without an output contract "
                        "fails readiness")
    for field in ("id", "module", "intent"):
        if not slice_spec.get(field):
            problems.append(f"{field}: missing")
    for i, ref in enumerate(slice_spec.get("inputs", [])):
        if not _bound(ref):
            problems.append(f"inputs[{i}]: missing address or digest — an "
                            "unverifiable input does not dispatch")
    if problems:
        return None, problems

    primary = list(slice_spec.get("primary", []))
    appendix = list(slice_spec.get("appendix", []))
    budget = slice_spec.get("budgets", {}).get("context_bytes")
    dropped = []
    if isinstance(budget, int):
        def size(items):
            return sum(len(canon(x)) for x in items)
        while appendix and size(primary) + size(appendix) > budget:
            dropped.append(appendix.pop())
        if size(primary) > budget:
            return None, ["budgets.context_bytes: smaller than the primary "
                          "material — a budget cuts appendix, never decisions "
                          "or acceptance; raise it or split the slice"]

    leaf = {
        "schema_version": LEAF_SCHEMA,
        "id": slice_spec["id"],
        "parent_id": parent.get("id"),
        "module": slice_spec["module"],
        "intent": slice_spec["intent"],
        "inputs": slice_spec.get("inputs", []),
        "decision_refs": decisions,
        "source_scope": slice_spec.get("source_scope", {"edit_targets": []}),
        "budgets": slice_spec.get("budgets", {"context_bytes": 1}),
        "acceptance": [a["text"] for a in acceptance],
        "expected_result": slice_spec["expected_result"],
        "outputs": slice_spec["outputs"],
        "guards": slice_spec.get("guards", parent.get("non_goals", [])),
        "resume": slice_spec.get(
            "resume", "re-read this packet, verify input digests, continue at "
                      "the first unmet acceptance case"),
        "acceptance_map": {a["text"]: a.get("parent_acceptance")
                           for a in acceptance},
        "primary": primary,
        "appendix": appendix,
    }
    if dropped:
        leaf["appendix_dropped"] = dropped   # the cut is recorded, never silent
    return leaf, []


def leaf_readiness(leaf):
    """The cold reader's eight questions, answered from the packet ALONE."""
    problems = []
    if not isinstance(leaf, dict):
        return ["leaf: not an object"]
    if leaf.get("schema_version") != LEAF_SCHEMA:
        problems.append("schema_version: missing or unknown — an unversioned "
                        "packet fails readiness")
    answers = {
        "goal": leaf.get("intent"),
        "inputs": leaf.get("inputs"),
        "decisions": leaf.get("decision_refs"),
        "scope": (leaf.get("source_scope") or {}).get("edit_targets"),
        "outputs": leaf.get("outputs"),
        "acceptance": leaf.get("acceptance"),
        "guards": leaf.get("guards"),
        "resume": leaf.get("resume"),
    }
    for q in COLD_READER_QUESTIONS:
        if not answers.get(q):
            problems.append(f"cold reader cannot answer {q!r} from the packet "
                            "alone — readiness fails")
    return problems


def select_slice(slices, active_id):
    """A slice is chosen by explicit id. No id, no fallback — 'the newest
    file' is an authority nobody granted (never mtime)."""
    if not active_id:
        raise ValueError("no active slice id given — selection by mtime or "
                         "recency is refused; name the slice")
    matches = [s for s in slices if isinstance(s, dict) and s.get("id") == active_id]
    if not matches:
        raise ValueError(f"slice {active_id!r} is not in the set")
    if len(matches) > 1:
        raise ValueError(f"slice {active_id!r} appears {len(matches)} times")
    return matches[0]


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv):
    if len(argv) >= 2 and argv[0] == "compile":
        try:
            report = _load(argv[1])
        except (OSError, ValueError) as e:
            print(f"REJECTED: unreadable report — {e}", file=sys.stderr)
            return 1
        result, problems = compile_parents(report)
        if problems:
            for p in problems:
                print(f"REJECTED: {p}", file=sys.stderr)
            return 1
        sys.stdout.write(canon(result))
        return 0
    if len(argv) == 3 and argv[0] == "compile-leaf":
        try:
            parent, slice_spec = _load(argv[1]), _load(argv[2])
        except (OSError, ValueError) as e:
            print(f"REJECTED: {e}", file=sys.stderr)
            return 1
        leaf, problems = compile_leaf(parent, slice_spec)
        if problems:
            for pr in problems:
                print(f"REJECTED: {pr}", file=sys.stderr)
            return 1
        sys.stdout.write(canon(leaf))
        return 0
    if len(argv) == 2 and argv[0] == "readiness":
        try:
            leaf = _load(argv[1])
        except (OSError, ValueError) as e:
            print(f"REJECTED: {e}", file=sys.stderr)
            return 1
        problems = leaf_readiness(leaf)
        for pr in problems:
            print(f"REJECTED: {pr}", file=sys.stderr)
        if problems:
            return 1
        print("READY — the cold reader's eight questions are answered")
        return 0
    if len(argv) == 3 and argv[0] == "verify":
        try:
            report, plan = _load(argv[1]), _load(argv[2])
        except (OSError, ValueError) as e:
            print(f"REJECTED: {e}", file=sys.stderr)
            return 1
        problems = verify_parents(report, plan)
        for p in problems:
            print(f"REJECTED: {p}", file=sys.stderr)
        if problems:
            return 1
        print(f"OK — {len(plan['parents'])} parents, every one traced")
        return 0
    print(__doc__.strip().splitlines()[0], file=sys.stderr)
    print("usage: context_packets.py compile <report.json> | "
          "verify <report.json> <parents.json> | "
          "compile-leaf <parent.json> <slice.json> | readiness <leaf.json>",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
