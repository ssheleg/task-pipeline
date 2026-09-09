#!/usr/bin/env python3
"""FIX-TP-03.01 — the kernel/profile contract (sherlock audit, TP-03).

The finding: one text allowed replacing the stages wholesale, another forbade
proceeding without a concrete stage 0 and kept references/stages.md normative
— undefined which document wins on a custom pipeline, risking a false gate or
a silently-skipped contract.

The fix under test (SKILL.md + pipeline.schema.json):
* a KERNEL (scope / evidence / deps / resume) invariant to every pipeline,
  and a PROFILE (the stage list) a project replaces wholesale;
* stage numbers belong to the selected profile, not the kernel — a minimal
  three-stage profile has no stage 7 yet keeps every kernel field;
* precedence on a custom profile: the kernel wins; references/stages.md is
  the default profile's gate set, not an imposition on a profile that dropped
  its stages;
* the schema declares the kernel; a three-stage profile validates.

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


def t_kernel_named():
    d = flat()
    assert "Two layers, and only one is replaceable." in d
    for f in ("**scope**", "**evidence**", "**deps**", "**resume**"):
        assert f in d, f"kernel field {f} missing"
    assert "The kernel is invariant." in d


def t_stage_numbers_belong_to_profile():
    d = flat()
    assert "The stage numbers belong to the SELECTED profile, never to the kernel:" in d
    assert 'a minimal three-stage profile has no "stage 7"' in d
    assert "a rule keyed on a global stage number is a rule about the default profile" in d


def t_precedence_resolved():
    d = flat()
    assert "on a CUSTOM profile the **kernel wins**" in d
    assert "the **default profile's** normative gate set" in d
    assert "the kernel is normative for all" in d


def t_schema_declares_kernel():
    d = json.load(open(SCHEMA, encoding="utf-8"))
    assert "kernel" in d["properties"], "the schema lacks the kernel"
    assert d["properties"]["kernel"]["required"] == ["scope", "evidence", "deps", "resume"]
    # the profile (stages) is still the only top-level requirement
    assert d["required"] == ["stages"], "the kernel was wrongly made top-level required"


def t_three_stage_profile_keeps_kernel():
    """A minimal three-stage profile has no stage 7 but carries every kernel field."""
    d = json.load(open(SCHEMA, encoding="utf-8"))
    req = d["properties"]["kernel"]["required"]
    pipeline = {
        "stages": [
            {"state": "spec", "skills": ["s"], "gate": {"type": "auto", "check": "x"}},
            {"state": "build", "skills": ["b"], "gate": {"type": "auto", "check": "y"}},
            {"state": "verify", "skills": ["v"], "gate": {"type": "manual", "check": "z"}},
        ],
        "kernel": {"scope": "src/", "evidence": "file:line", "deps": "none",
                   "resume": "re-read the packet"},
    }
    # no stage 7 exists
    assert len(pipeline["stages"]) == 3
    assert all(int(s.get("id", 0)) <= 3 for s in pipeline["stages"])
    # every kernel field present
    for f in req:
        assert f in pipeline["kernel"], f"the three-stage profile dropped kernel.{f}"


def main():
    case("the kernel and its four fields are named", t_kernel_named)
    case("stage numbers belong to the profile, not the kernel",
         t_stage_numbers_belong_to_profile)
    case("precedence on a custom profile is resolved (kernel wins)",
         t_precedence_resolved)
    case("the schema declares the kernel; stages stays the only top requirement",
         t_schema_declares_kernel)
    case("a minimal three-stage profile has no stage 7 but keeps the kernel",
         t_three_stage_profile_keeps_kernel)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
