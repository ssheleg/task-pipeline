#!/usr/bin/env python3
"""CTX-01.02 — attempt and result schemas (sherlock audit, parent CTX-01;
depends on CTX-01.01's execution packet).

The answer half of the family's task contract: an AttemptGrant (issuer,
revision, fence, holder — a structured object a later reader can check) and a
ResultEnvelope (content-addressed candidate, honest checks, the
fact/defect/unknown-effect evidence union, the attempt's own status).

Acceptance, driven against the shipped validator as a process:

* a bare boolean confirmation is NOT a grant — rejected, naming why;
* a stale candidate (built against an older revision than current, or holding
  a superseded fence) cannot validate as current;
* NOT_RUN is a status, not a gap; 'completed' beside failing checks is a
  contradiction; the evidence union admits nothing outside its three classes;
* the shipped example is valid.

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
EXAMPLE = os.path.join(SKILL, "execution-result.example.json")
SCHEMA = os.path.join(SKILL, "execution-result.schema.json")

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


def run_validate(env, *extra):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(env, fh)
        path = fh.name
    try:
        return subprocess.run([sys.executable, SCRIPT, "validate-result", path, *extra],
                              capture_output=True, text=True, timeout=60)
    finally:
        os.unlink(path)


def example():
    with open(EXAMPLE, encoding="utf-8") as fh:
        return json.load(fh)


def t_contract_ships_and_example_is_valid():
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    for field in ("schema_version", "packet_id", "grant", "built_against_revision",
                  "candidate", "checks", "evidence", "status"):
        assert field in schema.get("required", []), f"schema no longer requires {field}"
    assert "attemptGrant" in schema.get("definitions", {}), "the grant definition is gone"
    r = run_validate(example())
    assert r.returncode == 0, f"the shipped example is rejected:\n{r.stdout}"
    assert "NOT_RUN" in r.stdout, "the summary hides the NOT_RUN check"
    skill_md = open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8").read()
    assert "execution-result.schema.json" in skill_md, "SKILL.md never names the contract"


def t_boolean_confirmation_is_not_a_grant():
    for fake in (True, False, None):
        env = example()
        env["grant"] = fake
        r = run_validate(env)
        assert r.returncode == 1, f"grant={fake!r} was accepted"
        assert "not a grant" in r.stdout, f"the rejection does not say why:\n{r.stdout}"
    env2 = example()
    del env2["grant"]["fence"]
    r2 = run_validate(env2)
    assert r2.returncode == 1 and "grant.fence" in r2.stdout, \
        f"a fenceless grant passed:\n{r2.stdout}"


def t_stale_candidate_cannot_validate_as_current():
    r = run_validate(example(), "--current-revision", "9")
    assert r.returncode == 1 and "STALE candidate" in r.stdout and "re-plan" in r.stdout, \
        f"a stale candidate landed:\n{r.stdout}"
    ok = run_validate(example(), "--current-revision", "7")
    assert ok.returncode == 0, f"a current candidate was rejected:\n{ok.stdout}"


def t_superseded_fence_is_rejected():
    r = run_validate(example(), "--current-fence", "13")
    assert r.returncode == 1 and "superseded" in r.stdout, \
        f"a superseded fence landed:\n{r.stdout}"
    ok = run_validate(example(), "--current-fence", "12")
    assert ok.returncode == 0


def t_check_and_evidence_unions_hold():
    env = copy.deepcopy(example())
    env["checks"][0]["status"] = "SKIPPED"
    r = run_validate(env)
    assert r.returncode == 1 and "NOT_RUN is a status" in r.stdout, \
        f"an out-of-union check status passed:\n{r.stdout}"

    env2 = copy.deepcopy(example())
    env2["evidence"][0]["class"] = "opinion"
    r2 = run_validate(env2)
    assert r2.returncode == 1 and "never blended" in r2.stdout, \
        f"an out-of-union evidence class passed:\n{r2.stdout}"


def t_completed_with_failing_checks_is_a_contradiction():
    env = copy.deepcopy(example())
    env["checks"][0]["status"] = "FAIL"
    r = run_validate(env)
    assert r.returncode == 1 and "contradiction" in r.stdout, \
        f"'completed' beside a FAIL landed:\n{r.stdout}"
    env["status"] = "partial"
    r2 = run_validate(env)
    assert r2.returncode == 0, f"an honest partial was rejected:\n{r2.stdout}"


def main():
    case("the contract ships, the example validates, SKILL.md names it",
         t_contract_ships_and_example_is_valid)
    case("a boolean confirmation is not a grant", t_boolean_confirmation_is_not_a_grant)
    case("a stale candidate cannot validate as current", t_stale_candidate_cannot_validate_as_current)
    case("a superseded fence is rejected", t_superseded_fence_is_rejected)
    case("the check and evidence unions hold", t_check_and_evidence_unions_hold)
    case("'completed' beside failing checks is a contradiction",
         t_completed_with_failing_checks_is_a_contradiction)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"OK ({checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
