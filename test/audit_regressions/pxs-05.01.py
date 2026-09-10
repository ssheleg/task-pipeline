#!/usr/bin/env python3
"""PXS-05.01 — browser claims are linked to states and artifacts (sherlock
audit, PXS-05).

The fix under test:
* templates/browser-claims.json links REQ/scenario ids to state + kind,
  keeping the look/suite/library split;
* test/browser_claims_test.py (stdlib) refuses a missing artifact, a
  wrong-state artifact, and an incomplete toggle cycle;
* a functional PASS yields no visual PASS; no browser channel = NOT_RUN with
  a reason; browser.md names the contract; the gate runs the validator.

Standard library only.
"""
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline")
TPL = os.path.join(SKILL, "templates", "browser-claims.json")
VAL = os.path.join(ROOT, "test", "browser_claims_test.py")
BMD = os.path.join(SKILL, "references", "browser.md")

_spec = importlib.util.spec_from_file_location("bc", VAL)
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def t_template_shape():
    tpl = json.load(open(TPL, encoding="utf-8"))
    assert tpl["schema_version"] == "browser-claims/1"
    kinds = {c["kind"] for c in tpl["claims"]}
    assert "look" in kinds and "suite" in kinds, \
        "the template does not carry the look/suite split"
    for c in tpl["claims"]:
        assert c["req"] and c["scenario"] and c["state"], \
            "a template row is not linked to REQ/scenario/state"


def t_functional_pass_is_not_visual():
    v = M.claim_problems({"id": "X", "req": "R", "scenario": "S", "state": "opened",
                          "kind": "look", "status": "PASS", "artifact": None})
    assert any("wearing a visual verdict" in p for p in v)
    leak = M.suite_pass_closes_no_look([
        {"id": "S", "kind": "suite", "status": "PASS"},
        {"id": "V", "kind": "look", "status": "PASS", "artifact": None}])
    assert leak == ["V"]


def t_wrong_state_and_missing_artifact():
    wrong = M.claim_problems({"id": "X", "req": "R", "scenario": "S",
                              "state": "opened", "kind": "look", "status": "PASS",
                              "artifact": "a.png", "artifact_state": "initial"})
    assert any("cannot close a claim" in p for p in wrong)
    import tempfile
    ghost = M.claim_problems({"id": "X", "req": "R", "scenario": "S",
                              "state": "opened", "kind": "look", "status": "PASS",
                              "artifact": "a.png", "artifact_state": "opened"},
                             artifact_root=tempfile.mkdtemp())
    assert any("does not exist" in p for p in ghost)


def t_toggle_cycle_and_not_run():
    tpl = json.load(open(TPL, encoding="utf-8"))
    half = [dict(c, status="PASS") for c in tpl["claims"][:2]]
    assert M.toggle_cycle_gaps(half, "nav-menu") == ["closed-again"]
    v = M.claim_problems({"id": "X", "req": "R", "scenario": "S", "state": "opened",
                          "kind": "look", "status": "NOT_RUN"})
    assert any("its reason" in p for p in v), "a reasonless NOT_RUN passed"


def t_doc_and_gate_wired():
    with open(BMD, encoding="utf-8") as fh:
        d = " ".join(fh.read().split())
    assert "templates/browser-claims.json" in d and "browser_claims_test.py" in d
    pj = json.load(open(os.path.join(ROOT, "package.json"), encoding="utf-8"))
    assert "browser_claims_test.py" in pj["scripts"]["test"], \
        "the gate does not run the validator"


def main():
    case("the template links REQ/scenario to state and kind", t_template_shape)
    case("a functional PASS is never a visual PASS", t_functional_pass_is_not_visual)
    case("wrong-state and missing artifacts are refused",
         t_wrong_state_and_missing_artifact)
    case("the toggle cycle and reasoned NOT_RUN are enforced",
         t_toggle_cycle_and_not_run)
    case("browser.md names the contract; the gate runs the validator",
         t_doc_and_gate_wired)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
