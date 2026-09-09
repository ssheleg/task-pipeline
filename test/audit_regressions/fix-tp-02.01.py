#!/usr/bin/env python3
"""FIX-TP-02.01 — gates check artifacts and their quality, never package
presence (sherlock audit, TP-02).

The finding: a missing family package turned into an unpassable UI gate even
when scenarios were already equivalently described, and a third-party design
workflow was declared "undesigned" merely because sheleg-design was absent —
substituting presence of a package for quality of the work.

The fix under test (SKILL.md + references/companion-skills.md):
* the stage-3 gate checks the scenario ARTIFACT — preferred provider,
  alternative provider with the same contract, or the inline fallback all
  pass; only the missing artifact stops the gate;
* a third-party design workflow is judged by its RESULT; "undesigned" is
  reserved for no design evidence at all;
* an absent tool is reported as the NAMED check not done;
* the gate rule run as behaviour on the packet's three fixtures.

Standard library only.
"""
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def flat(name):
    with open(os.path.join(SKILL, name), encoding="utf-8") as fh:
        return " ".join(fh.read().split())


def t_gate_checks_artifact_not_package():
    s = flat("SKILL.md")
    assert "the stage-3 gate checks the ARTIFACT, not the package" in s
    assert "Not installed on a UI task? The stage-3 spec gate stops" not in s, \
        "the package-presence gate survived"
    c = flat("references/companion-skills.md")
    assert "a gate checks artifacts and their quality, never package presence" in c


def t_three_providers_same_contract():
    c = flat("references/companion-skills.md")
    for way in ("preferred family provider", "alternative provider producing the same artifact contract",
                "inline fallback"):
        assert way in c, f"the {way} path is missing"
    assert "Artifact required for any user-facing task" in c


def t_foreign_design_judged_by_result():
    c = flat("references/companion-skills.md")
    assert "judge the visual layer by its RESULT" in c
    assert "only a layer with no design evidence at all ships **undesigned**" in c


def t_absent_tool_names_the_check():
    c = flat("references/companion-skills.md")
    assert "WHICH check was therefore not done" in c
    assert "scenario lint NOT_RUN" in c
    s = flat("SKILL.md")
    assert "NAMED check that was not done, never as a failed task" in s


# ---- the gate as behaviour


def stage3_gate(project):
    """project: {scenarios_artifact, scenarios_valid, provider}. → verdict."""
    if not project.get("scenarios_artifact"):
        return {"pass": False, "action": "create the scenario artifact",
                "preferred": "super-ux"}
    if not project.get("scenarios_valid"):
        return {"pass": False, "action": "fix the artifact against the contract"}
    return {"pass": True, "provider": project.get("provider")}


def t_valid_scenarios_without_superux_pass():
    v = stage3_gate({"scenarios_artifact": True, "scenarios_valid": True,
                     "provider": "hand-written"})
    assert v["pass"] is True, "valid scenarios failed the gate for lack of the package"


def t_no_artifact_requires_creation():
    v = stage3_gate({"scenarios_artifact": False})
    assert v["pass"] is False and v["action"] == "create the scenario artifact"
    assert v["preferred"] == "super-ux", "the preferred provider is not offered"


def t_foreign_design_fixture():
    def design_verdict(evidence):
        return "designed" if evidence else "undesigned"
    assert design_verdict(["tokens.css", "states table", "decision log"]) == "designed", \
        "a third-party workflow with full evidence was called undesigned"
    assert design_verdict([]) == "undesigned"


def main():
    case("the gate checks the artifact, not the package",
         t_gate_checks_artifact_not_package)
    case("three provider paths satisfy one contract", t_three_providers_same_contract)
    case("a foreign design workflow is judged by its result",
         t_foreign_design_judged_by_result)
    case("an absent tool is the named check not done", t_absent_tool_names_the_check)
    case("fixture: valid scenarios without super-ux pass",
         t_valid_scenarios_without_superux_pass)
    case("fixture: no artifact → create it, preferred provider offered",
         t_no_artifact_requires_creation)
    case("fixture: foreign design with evidence is designed", t_foreign_design_fixture)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
