#!/usr/bin/env python3
"""FIX-TP-03.02 — profile-only gate dispatch (sherlock audit, TP-03, second
leaf).

The fix under test (SKILL.md + pipeline.schema.json):
* the selected profile is compiled ONCE and only ITS declared stages/gates
  run — no hidden stage 0/7/10 injected from the default profile;
* a custom profile does NOT bypass the kernel (scope/evidence/deps/resume);
* an unknown MANDATORY capability (must_understand entry the runtime lacks)
  BLOCKS the compile;
* the dispatch rule run as behaviour.

Standard library only.
"""
import json
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline",
                     "SKILL.md")
SCHEMA = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline",
                      "pipeline.schema.json")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def flat():
    with open(SKILL, encoding="utf-8") as fh:
        return " ".join(fh.read().split())


def t_compile_once_declared_only():
    d = flat()
    assert "The SELECTED profile is compiled once, at preflight, and only ITS declared stages and gates run" in d
    assert "no hidden stage\n 0, 7 or 10 is injected".replace("\n ", " ") in d \
        or "no hidden stage 0, 7 or 10 is injected" in d


def t_kernel_not_bypassed():
    d = flat()
    assert "What a custom\n profile does NOT escape is the KERNEL".replace("\n ", " ") in d \
        or "does NOT escape is the KERNEL" in d
    assert "dropping stages never drops the evidence gate" in d


def t_unknown_mandatory_blocks():
    d = flat()
    assert "an unknown MANDATORY capability blocks the compile" in d
    assert "refused, never run with the capability silently absent" in d
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    mu = schema["properties"]["must_understand"]["description"]
    assert "BLOCKS the compile" in mu


# ---- the dispatch as behaviour


def compile_profile(profile, runtime_caps):
    """Compile once: return the gates to run, or a refusal."""
    for cap in profile.get("must_understand", []):
        if cap not in runtime_caps:
            return {"ok": False, "reason": f"unknown mandatory capability: {cap}"}
    gates = [s["gate"] for s in profile["stages"]]
    return {"ok": True, "gates": gates, "kernel_required": True}


def t_three_stage_profile_runs_three_gates():
    prof = {"stages": [
        {"state": "spec", "gate": {"type": "auto", "check": "x"}},
        {"state": "build", "gate": {"type": "auto", "check": "y"}},
        {"state": "verify", "gate": {"type": "manual", "check": "z"}},
    ]}
    r = compile_profile(prof, {"auto", "manual"})
    assert r["ok"] and len(r["gates"]) == 3, "a 3-stage profile did not run exactly 3 gates"
    # kernel still required — evidence not bypassed
    assert r["kernel_required"] is True


def t_unknown_capability_blocks_compile():
    prof = {"stages": [{"state": "x", "gate": {"type": "auto", "check": "c"}}],
            "must_understand": ["holographic-consensus"]}
    r = compile_profile(prof, {"auto"})
    assert r["ok"] is False and "holographic-consensus" in r["reason"], \
        "an unknown mandatory capability was run instead of blocking"


def main():
    case("the selected profile compiles once; only its gates run",
         t_compile_once_declared_only)
    case("a custom profile does not bypass the kernel", t_kernel_not_bypassed)
    case("an unknown mandatory capability blocks the compile", t_unknown_mandatory_blocks)
    case("fixture: a 3-stage profile runs 3 gates, kernel still required",
         t_three_stage_profile_runs_three_gates)
    case("fixture: an unknown capability blocks the compile",
         t_unknown_capability_blocks_compile)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
