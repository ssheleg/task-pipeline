#!/usr/bin/env python3
"""CTX-02.01 — finding-to-parent mapper (sherlock audit, parent CTX-02).

The contract under test, as behaviour against scripts/context_packets.py:

* a corpus shaped like the real one (115 findings + 4 capabilities) compiles
  to exactly 119 parents, every one traced, and a REPEATED compile — even
  from a shuffled report — is byte-identical: ids are derived, not positional;
* evidence/limits/priority land in their own fields, status is born
  `parent_planned`, and a report that tries to smuggle a status is refused;
* nothing is dropped silently: a duplicate id, a missing module, and a
  parents file missing one parent are each a named refusal, and a compile
  with problems produces NO partial plan.

Standard library only; drives the module and the CLI.
"""
import importlib.util
import json
import os
import random
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


def corpus():
    """115 findings + 4 capabilities, the real plan's shape and id grammar."""
    groups = [("RT", 12), ("SY", 14), ("TP", 15), ("UX", 12), ("DS", 12),
              ("CW", 10), ("DV", 12), ("AG", 10), ("TG", 9), ("SE", 9)]
    findings = []
    for prefix, n in groups:
        for i in range(1, n + 1):
            fid = f"{prefix}-{i:02d}"
            findings.append({
                "id": fid,
                "title": f"finding {fid}",
                "module": {"RT": "sshlg-skills", "SY": "agent-sync",
                           "TP": "task-pipeline"}.get(prefix, "family"),
                "priority": "P1" if i <= 3 else "P2",
                "priority_rank": 1 if i <= 3 else 2,
                "priority_reason": "invariant" if i <= 3 else "quality",
                "evidence": [f"repo://{prefix.lower()}/file.py:{i}"],
                "limits": [f"not verified on host {i}"],
            })
    assert len(findings) == 115
    capabilities = [
        {"id": f"CTX-{i:02d}", "title": f"capability {i}", "module": "task-pipeline",
         "priority": "P1", "evidence": ["audit://extension/work-brief.md"]}
        for i in range(1, 5)
    ]
    return {"findings": findings, "capabilities": capabilities}


def t_119_parents_every_one_traced():
    result, problems = M.compile_parents(corpus())
    assert problems == [], f"a clean corpus was refused: {problems[:3]}"
    parents = result["parents"]
    assert len(parents) == 119, f"expected 119 parents, got {len(parents)}"
    ids = [p["id"] for p in parents]
    assert len(set(ids)) == 119, "duplicate parent ids"
    assert result["trace"]["FIX-RT-01"] == "RT-01"
    assert result["trace"]["CTX-01"] is None
    fix = [p for p in parents if p["finding_id"]]
    assert len(fix) == 115 and all(p["id"] == "FIX-" + p["finding_id"] for p in fix), \
        "a derived id does not follow the FIX-<finding> rule"


def t_repeated_and_shuffled_compile_is_byte_identical():
    a, _ = M.compile_parents(corpus())
    b, _ = M.compile_parents(corpus())
    assert M.canon(a) == M.canon(b), "two compiles of one corpus differ"
    shuffled = corpus()
    random.Random(7).shuffle(shuffled["findings"])
    c, problems = M.compile_parents(shuffled)
    assert problems == []
    assert M.canon(a) == M.canon(c), \
        "a shuffled report changed the plan — ids or order are positional"


def t_axes_stay_separate():
    result, _ = M.compile_parents(corpus())
    p = next(x for x in result["parents"] if x["id"] == "FIX-SY-05")
    assert p["status"] == "parent_planned" and p["revision"] == 1
    assert p["evidence"] == ["repo://sy/file.py:5"], "evidence was not carried"
    assert p["limits"] == ["not verified on host 5"], "limits were not carried"
    assert p["priority"] == "P2", "priority was not carried"

    smuggler = corpus()
    smuggler["findings"][0]["status"] = "done"
    result2, problems = M.compile_parents(smuggler)
    assert result2 is None and any("smuggle" in p for p in problems), \
        f"a report smuggled a status into a parent: {problems[:2]}"


def t_nothing_dropped_silently():
    dup = corpus()
    dup["findings"].append(dict(dup["findings"][0]))
    result, problems = M.compile_parents(dup)
    assert result is None, "a duplicate id still produced a (partial) plan"
    assert any("duplicate" in p or "already mapped" in p for p in problems)

    hole = corpus()
    del hole["findings"][50]["module"]
    result2, problems2 = M.compile_parents(hole)
    assert result2 is None, "an unmappable finding was silently dropped"
    assert any("missing module" in p for p in problems2)

    collide = corpus()
    collide["capabilities"][0]["id"] = "FIX-RT-99"
    result3, problems3 = M.compile_parents(collide)
    assert result3 is None and any("collides" in p for p in problems3), \
        "a capability squatted the derived FIX-* namespace"


def t_verify_catches_a_dropped_and_a_mutated_parent():
    report = corpus()
    plan, _ = M.compile_parents(report)
    assert M.verify_parents(report, plan) == []

    dropped = json.loads(M.canon(plan))
    dropped["parents"] = [p for p in dropped["parents"] if p["id"] != "FIX-TG-05"]
    problems = M.verify_parents(report, dropped)
    assert any("FIX-TG-05" in p and "dropped" in p for p in problems), \
        f"a dropped parent went unnoticed: {problems[:2]}"

    mutated = json.loads(M.canon(plan))
    next(p for p in mutated["parents"] if p["id"] == "FIX-SE-01")["priority"] = "P3"
    problems2 = M.verify_parents(report, mutated)
    assert any("FIX-SE-01" in p and "mutated" in p for p in problems2)

    invented = json.loads(M.canon(plan))
    invented["parents"].append({"id": "FIX-ZZ-01", "finding_id": "ZZ-01"})
    problems3 = M.verify_parents(report, invented)
    assert any("FIX-ZZ-01" in p and "no finding" in p for p in problems3)


def t_cli_round_trip():
    d = tempfile.mkdtemp()
    rp = os.path.join(d, "report.json")
    pp = os.path.join(d, "parents.json")
    with open(rp, "w") as fh:
        json.dump(corpus(), fh)
    r = subprocess.run([sys.executable, SCRIPT, "compile", rp],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"compile failed: {r.stderr[:200]}"
    with open(pp, "w") as fh:
        fh.write(r.stdout)
    v = subprocess.run([sys.executable, SCRIPT, "verify", rp, pp],
                       capture_output=True, text=True)
    assert v.returncode == 0 and "119 parents" in v.stdout, \
        f"verify refused a faithful plan: {v.stderr[:200]}"
    bad = subprocess.run([sys.executable, SCRIPT, "compile", "/nonexistent.json"],
                         capture_output=True, text=True)
    assert bad.returncode == 1 and "REJECTED" in bad.stderr


def main():
    case("115 findings + 4 capabilities compile to 119 traced parents",
         t_119_parents_every_one_traced)
    case("repeated and shuffled compiles are byte-identical",
         t_repeated_and_shuffled_compile_is_byte_identical)
    case("evidence/limits/priority are separate fields; a smuggled status is refused",
         t_axes_stay_separate)
    case("a duplicate, a hole and a namespace squat each block the whole compile",
         t_nothing_dropped_silently)
    case("verify catches a dropped, a mutated and an invented parent",
         t_verify_catches_a_dropped_and_a_mutated_parent)
    case("the CLI round-trips and refuses an unreadable report", t_cli_round_trip)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"OK ({checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
