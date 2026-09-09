#!/usr/bin/env python3
"""CTX-02.04 — pre-dispatch freshness and budget (sherlock audit, closing
stage of the packet compiler, parent CTX-02).

The contract under test, as behaviour against scripts/context_packets.py:

* a leaf whose inputs still hash to their declared digests, whose
  prerequisites are materialized, whose primary fits its budget and whose
  capability + claim are present is CLEAR;
* source drift (bytes changed on disk) blocks and names the file;
* a missing prerequisite output blocks;
* an oversized PRIMARY context blocks — never a silent truncation (the
  primary items are all still there after the block);
* a missing capability and edit targets with no claim each block.

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


def make(root_files=None):
    root = tempfile.mkdtemp()
    files = root_files or {"docs/brief.md": b"# brief\n"}
    for rel, data in files.items():
        os.makedirs(os.path.join(root, os.path.dirname(rel)), exist_ok=True)
        with open(os.path.join(root, rel), "wb") as fh:
            fh.write(data)
    inputs = [{"address": rel, "sha256": hashlib.sha256(data).hexdigest()}
              for rel, data in sorted(files.items())]
    leaf = {
        "schema_version": "execution-packet/1", "id": "L-1", "module": "m",
        "intent": "do", "inputs": inputs,
        "depends_on": [{"task_id": "UP-1", "kind": "data", "rationale": "needs it"}],
        "budgets": {"context_bytes": 100000},
        "primary": [{"role": "spec", "text": "small"}],
        "required_capabilities": ["python3"],
        "source_scope": {"edit_targets": [{"address": "lib/x.py", "mode": "Create"}],
                         "claim": "L-1"},
    }
    return root, leaf


def t_clear_when_everything_holds():
    root, leaf = make()
    problems = M.predispatch(leaf, root, capabilities=["python3"], produced=["UP-1"])
    assert problems == [], f"a dispatchable leaf was blocked: {problems[:3]}"


def t_source_drift_blocks_by_name():
    root, leaf = make()
    with open(os.path.join(root, "docs", "brief.md"), "ab") as fh:
        fh.write(b"drifted\n")
    problems = M.predispatch(leaf, root, capabilities=["python3"], produced=["UP-1"])
    assert any("brief.md" in p and "DRIFT" in p for p in problems), \
        f"source drift did not block: {problems[:2]}"


def t_missing_prerequisite_blocks():
    root, leaf = make()
    problems = M.predispatch(leaf, root, capabilities=["python3"], produced=[])
    assert any("UP-1" in p and "not materialized" in p for p in problems), \
        "a missing prerequisite output did not block"


def t_oversized_primary_blocks_without_truncating():
    root, leaf = make()
    leaf["budgets"] = {"context_bytes": 50}
    leaf["primary"] = [{"role": "spec", "text": "x" * 500},
                       {"role": "spec2", "text": "y" * 500}]
    before = len(leaf["primary"])
    problems = M.predispatch(leaf, root, capabilities=["python3"], produced=["UP-1"])
    assert any("over the" in p and "never primary" in p for p in problems), \
        f"an oversized primary did not block: {problems[:2]}"
    assert len(leaf["primary"]) == before, \
        "the primary list was truncated — the block must not mutate it"


def t_missing_capability_and_claim_block():
    root, leaf = make()
    problems = M.predispatch(leaf, root, capabilities=[], produced=["UP-1"])
    assert any("python3" in p and "not available" in p for p in problems), \
        "a missing capability did not block"
    root2, leaf2 = make()
    leaf2["source_scope"].pop("claim")
    problems2 = M.predispatch(leaf2, root2, capabilities=["python3"], produced=["UP-1"])
    assert any("no coordination claim" in p for p in problems2), \
        "edit targets with no claim did not block"


def t_cli_blocks_and_clears():
    root, leaf = make()
    d = tempfile.mkdtemp()
    lp = os.path.join(d, "leaf.json")
    json.dump(leaf, open(lp, "w"))
    ok = subprocess.run([sys.executable, SCRIPT, "predispatch", lp, root,
                         "--capabilities", "python3", "--produced", "UP-1"],
                        capture_output=True, text=True)
    assert ok.returncode == 0 and "CLEAR" in ok.stdout, ok.stderr[:200]
    bad = subprocess.run([sys.executable, SCRIPT, "predispatch", lp, root,
                          "--capabilities", "python3"],
                         capture_output=True, text=True)
    assert bad.returncode == 1 and "BLOCKED" in bad.stderr


def main():
    case("a fully fresh, budgeted, capable leaf is CLEAR",
         t_clear_when_everything_holds)
    case("source drift blocks and names the file", t_source_drift_blocks_by_name)
    case("a missing prerequisite output blocks", t_missing_prerequisite_blocks)
    case("an oversized primary blocks without truncating",
         t_oversized_primary_blocks_without_truncating)
    case("a missing capability and a missing claim each block",
         t_missing_capability_and_claim_block)
    case("the CLI blocks and clears", t_cli_blocks_and_clears)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"OK ({checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
