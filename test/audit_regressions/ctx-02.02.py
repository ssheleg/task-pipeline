#!/usr/bin/env python3
"""CTX-02.02 — the leaf compiler (sherlock audit, parent CTX-02, on the
finding-to-parent mapper of CTX-02.01).

The contract under test, as behaviour against scripts/context_packets.py:

* a resolved parent + slice compiles to a leaf the COLD READER can read: the
  packet alone answers goal/inputs/decisions/scope/outputs/acceptance/
  guards/resume, and `readiness` says READY;
* an unresolved decision dispatches NO leaf; a missing output contract and a
  missing version each fail readiness; acceptance needs a positive AND a
  negative case;
* a budget cuts appendix material only, RECORDS the cut, and refuses a
  budget smaller than the primary material rather than trimming acceptance;
* a slice is selected by explicit id — selection by mtime/recency is
  refused, and no id is not "the newest one".

Standard library only.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPT = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline",
                      "scripts", "context_packets.py")
PLANNING = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline",
                        "references", "planning.md")

_spec = importlib.util.spec_from_file_location("context_packets", SCRIPT)
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)

checks = 0
failures = []


def case(name, fn):
    global checks
    try:
        fn()
        checks += 1
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


DIG = hashlib.sha256(b"decision bytes").hexdigest()


def parent():
    return {"id": "FIX-XX-01", "module": "task-pipeline",
            "non_goals": ["do not touch neighbours"]}


def slice_spec(**over):
    s = {
        "id": "FIX-XX-01.01", "module": "task-pipeline",
        "intent": "close the gap the finding names",
        "inputs": [{"address": "docs/brief.md", "sha256": DIG}],
        "decision_refs": [{"id": "D01", "address": "context/decisions.json",
                           "sha256": DIG}],
        "source_scope": {"edit_targets": [{"address": "lib/x.py", "mode": "Create"}]},
        "budgets": {"context_bytes": 100000},
        "acceptance": [
            {"kind": "positive", "text": "the fixture passes",
             "parent_acceptance": "A1"},
            {"kind": "negative", "text": "the planted defect is refused",
             "parent_acceptance": "A1"},
        ],
        "expected_result": "the validator refuses the defect and passes the fix",
        "outputs": [{"name": "candidate_change", "contract": "isolated commit"}],
        "primary": [{"role": "spec", "text": "the contract"}],
        "appendix": [{"role": "history", "text": "long background " * 50}],
    }
    s.update(over)
    return s


def t_resolved_slice_compiles_and_cold_reader_reads_it():
    leaf, problems = M.compile_leaf(parent(), slice_spec())
    assert problems == [], f"a resolved slice was refused: {problems[:2]}"
    assert leaf["parent_id"] == "FIX-XX-01"
    assert leaf["acceptance_map"]["the fixture passes"] == "A1", \
        "the parent acceptance mapping was lost"
    assert leaf["guards"] == ["do not touch neighbours"], \
        "the parent's guards did not reach the leaf"
    assert M.leaf_readiness(leaf) == [], \
        f"the cold reader was left with questions: {M.leaf_readiness(leaf)[:2]}"


def t_unresolved_decision_dispatches_no_leaf():
    bad = slice_spec(decision_refs=[{"id": "D01", "address": "decisions.json"}])
    leaf, problems = M.compile_leaf(parent(), bad)
    assert leaf is None and any("rumour" in p or "unresolved" in p for p in problems), \
        "an unresolved decision still dispatched a leaf — the finding itself"


def t_readiness_fails_on_missing_version_and_outputs():
    leaf, _ = M.compile_leaf(parent(), slice_spec())
    unversioned = dict(leaf)
    del unversioned["schema_version"]
    assert any("schema_version" in p for p in M.leaf_readiness(unversioned)), \
        "an unversioned packet passed readiness"
    no_out = slice_spec(outputs=[])
    l2, problems = M.compile_leaf(parent(), no_out)
    assert l2 is None and any("output contract" in p for p in problems), \
        "a missing output contract compiled"


def t_acceptance_needs_both_polarities():
    only_pos = slice_spec(acceptance=[{"kind": "positive", "text": "it works"}])
    leaf, problems = M.compile_leaf(parent(), only_pos)
    assert leaf is None and any("negative" in p for p in problems), \
        "success-only acceptance compiled — nothing testable refuses anything"


def t_budget_cuts_appendix_records_it_never_acceptance():
    tight = slice_spec()
    tight["budgets"] = {"context_bytes": 400}
    leaf, problems = M.compile_leaf(parent(), tight)
    assert problems == [], f"a tight budget refused the slice: {problems[:1]}"
    assert leaf["appendix"] == [] and leaf.get("appendix_dropped"), \
        "the appendix cut was silent — a dropped item must be recorded"
    assert len(leaf["acceptance"]) == 2, "the budget trimmed acceptance"

    impossible = slice_spec()
    impossible["budgets"] = {"context_bytes": 10}
    l2, p2 = M.compile_leaf(parent(), impossible)
    assert l2 is None and any("never decisions or acceptance" in p for p in p2), \
        "a budget below the primary material trimmed instead of refusing"


def t_slice_selection_is_by_id_never_mtime():
    slices = [slice_spec(), slice_spec(id="FIX-XX-01.02")]
    chosen = M.select_slice(slices, "FIX-XX-01.02")
    assert chosen["id"] == "FIX-XX-01.02"
    try:
        M.select_slice(slices, None)
        raise AssertionError("no-id selection fell back to something")
    except ValueError as e:
        assert "mtime" in str(e), f"the refusal does not name the trap: {e}"
    try:
        M.select_slice(slices, "FIX-XX-09.99")
        raise AssertionError("an absent id selected a slice")
    except ValueError:
        pass


def t_cli_round_trip_and_doctrine():
    d = tempfile.mkdtemp()
    pp, sp, lp = (os.path.join(d, n) for n in ("p.json", "s.json", "l.json"))
    json.dump(parent(), open(pp, "w"))
    json.dump(slice_spec(), open(sp, "w"))
    r = subprocess.run([sys.executable, SCRIPT, "compile-leaf", pp, sp],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"compile-leaf failed: {r.stderr[:200]}"
    open(lp, "w").write(r.stdout)
    v = subprocess.run([sys.executable, SCRIPT, "readiness", lp],
                       capture_output=True, text=True)
    assert v.returncode == 0 and "READY" in v.stdout, v.stderr[:200]
    flat = " ".join(open(PLANNING, encoding="utf-8").read().split())
    for needle in ("cold reader", "never by mtime", "parallel plan authority",
                   "records the cut, never acceptance"):
        assert needle in flat, f"planning.md no longer states {needle!r}"


def main():
    case("a resolved slice compiles; the cold reader answers all eight",
         t_resolved_slice_compiles_and_cold_reader_reads_it)
    case("an unresolved decision dispatches no leaf",
         t_unresolved_decision_dispatches_no_leaf)
    case("missing version and missing output contract fail readiness",
         t_readiness_fails_on_missing_version_and_outputs)
    case("acceptance needs a positive AND a negative case",
         t_acceptance_needs_both_polarities)
    case("a budget cuts appendix, records it, never acceptance",
         t_budget_cuts_appendix_records_it_never_acceptance)
    case("a slice is selected by id, never by mtime",
         t_slice_selection_is_by_id_never_mtime)
    case("the CLI round-trips and the doctrine states the rules",
         t_cli_round_trip_and_doctrine)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"OK ({checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
