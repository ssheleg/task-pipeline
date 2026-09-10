#!/usr/bin/env python3
"""CTX-01.01 — packet and context schemas (sherlock audit, parent CTX-01).

The family's versioned task/context contract: `execution-packet.schema.json`
states the shape (ExecutionPacket + ContextRef: version, id, parent, module,
decision refs, inputs, source scope, budgets), and `scripts/packet.py` is the
dependency-free runtime validation every consumer runs before acting.

Acceptance, driven against the shipped validator as a process:

* an unknown mandatory major is rejected, named, with a remedy;
* a missing ref/digest (input sha256, Edit baseline) is rejected;
* an unbound decision (named without address+digest) is rejected;
* the shipped example is valid and round-trips canonically — same packet,
  same digest, twice.

Standard library only.
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline")
SCRIPT = os.path.join(SKILL, "scripts", "packet.py")
SCHEMA = os.path.join(SKILL, "execution-packet.schema.json")
EXAMPLE = os.path.join(SKILL, "execution-packet.example.json")

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


def run_validate(packet):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(packet, fh)
        path = fh.name
    try:
        return subprocess.run([sys.executable, SCRIPT, "validate", path],
                              capture_output=True, text=True, timeout=60)
    finally:
        os.unlink(path)


def example():
    with open(EXAMPLE, encoding="utf-8") as fh:
        return json.load(fh)


def t_contract_ships_and_example_is_valid():
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    assert schema.get("$schema", "").endswith("draft-07/schema#"), "schema is not draft-07"
    for field in ("schema_version", "id", "module", "intent", "inputs",
                  "decision_refs", "source_scope", "budgets"):
        assert field in schema.get("required", []), f"schema no longer requires {field}"
    assert "contextRef" in schema.get("definitions", {}), "ContextRef definition is gone"
    r = run_validate(example())
    assert r.returncode == 0, f"the shipped example is rejected:\n{r.stdout}"
    skill_md = open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8").read()
    assert "execution-packet.schema.json" in skill_md, "SKILL.md never names the contract"


def t_unknown_mandatory_major_rejects():
    p = example()
    p["schema_version"] = "execution-packet/9"
    r = run_validate(p)
    assert r.returncode == 1, "an unknown major was accepted"
    assert "major 9 is unknown" in r.stdout, f"the rejection does not name the major:\n{r.stdout}"
    assert "re-issue" in r.stdout or "upgrade" in r.stdout, "the rejection names no remedy"
    p["schema_version"] = "not-a-version"
    r2 = run_validate(p)
    assert r2.returncode == 1 and "unversioned" in r2.stdout, \
        f"a versionless packet passed:\n{r2.stdout}"


def t_missing_ref_or_digest_rejects():
    p = copy.deepcopy(example())
    del p["inputs"][0]["sha256"]
    r = run_validate(p)
    assert r.returncode == 1 and "missing sha256" in r.stdout, \
        f"an input without a digest passed:\n{r.stdout}"

    p2 = copy.deepcopy(example())
    p2["inputs"][0]["address"] = ""
    r2 = run_validate(p2)
    assert r2.returncode == 1 and "missing address" in r2.stdout, \
        f"an addressless ref passed:\n{r2.stdout}"

    p3 = copy.deepcopy(example())
    del p3["source_scope"]["edit_targets"][0]["baseline_sha256"]
    r3 = run_validate(p3)
    assert r3.returncode == 1 and "baseline_sha256" in r3.stdout, \
        f"an Edit target without a baseline passed:\n{r3.stdout}"


def t_unbound_decision_rejects():
    p = copy.deepcopy(example())
    p["decision_refs"] = [{"id": "DEC-0007"}]  # named, no address, no digest — a rumour
    r = run_validate(p)
    assert r.returncode == 1, "an unbound decision was accepted"
    assert "missing address" in r.stdout and "missing sha256" in r.stdout, \
        f"the rejection does not name what is unbound:\n{r.stdout}"


def t_valid_round_trip():
    r1 = subprocess.run([sys.executable, SCRIPT, "canon", EXAMPLE],
                        capture_output=True, text=True, timeout=60)
    r2 = subprocess.run([sys.executable, SCRIPT, "canon", EXAMPLE],
                        capture_output=True, text=True, timeout=60)
    assert r1.returncode == 0 and r2.returncode == 0, "canon failed on the example"
    assert r1.stdout == r2.stdout and len(r1.stdout.strip()) == 64, \
        "the canonical digest is not stable"
    # key order must not change the digest — same packet, same bytes
    reordered = dict(reversed(list(example().items())))
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(reordered, fh)
        path = fh.name
    try:
        r3 = subprocess.run([sys.executable, SCRIPT, "canon", path],
                            capture_output=True, text=True, timeout=60)
    finally:
        os.unlink(path)
    assert r3.stdout == r1.stdout, "key order changed the canonical digest"


def t_budgets_must_bound_something():
    p = copy.deepcopy(example())
    p["budgets"] = {}
    r = run_validate(p)
    assert r.returncode == 1 and "at least one bound" in r.stdout, \
        f"an empty budget passed:\n{r.stdout}"


def main():
    case("the contract ships, the example validates, SKILL.md names it",
         t_contract_ships_and_example_is_valid)
    case("an unknown mandatory major is rejected with a remedy", t_unknown_mandatory_major_rejects)
    case("a missing ref/digest is rejected", t_missing_ref_or_digest_rejects)
    case("an unbound decision is rejected", t_unbound_decision_rejects)
    case("a valid packet round-trips to one canonical digest", t_valid_round_trip)
    case("budgets must bound something", t_budgets_must_bound_something)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"OK ({checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
