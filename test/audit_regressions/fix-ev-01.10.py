#!/usr/bin/env python3
"""FIX-EV-01.09 — the outcome corpus for project-audit (sherlock audit, parent
FIX-EV-01; depends on the family harness of FIX-EV-01.01).

The corpus (evals/cases/project-audit.json) holds a positive (a receipt per
claim), a negative (routing), an unsupported-claim case (prove "docs are in
sync" by an exit code or mark it unsupported), a chat-answer no-op, and the
ED-01 case (an unresolvable dependency prints capability unavailable, never
"all links resolve") — judged on ARTIFACTS through the family's outcome-case
contract, so project-audit can no longer pass an eval by its name being picked.

Standard library only.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CASES = os.path.join(ROOT, "evals", "cases", "project-audit.json")
HARNESS = os.path.expanduser("~/DATA/sshlg-skills/test/outcome_harness.py")

failures = []
not_run = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def manifest():
    with open(CASES, encoding="utf-8") as fh:
        return json.load(fh)


def t_cases_are_structurally_valid():
    m = manifest()
    ids = [c["id"] for c in m["cases"]]
    assert len(ids) == len(set(ids)) and len(ids) >= 5
    for c in m["cases"]:
        assert c["schema_version"] == "outcome-case/1"
        assert c["skill"] == "project-audit"
        assert c["environment"]["case_digest"] == \
            hashlib.sha256(c["prompt"]["text"].encode()).hexdigest(), \
            f"{c['id']}: case_digest does not pin the frozen prompt"
        assert c["checks"]["outcome"], f"{c['id']}: no outcome checks"


def t_negative_forbids_loading():
    neg = next(c for c in manifest()["cases"] if "negative" in c["id"])
    assert "project-audit" in neg["checks"]["load_trace"]["expect_not_loaded"]


def t_adr_reproduced_and_report_cases():
    m = manifest()
    adr = next(c for c in m["cases"] if "adr-does-not-excuse" in c["id"])
    assert any((o.get("expect") or "") == "exposure" for o in adr["checks"]["outcome"]), \
        "the ADR case does not keep the exposure a finding (PA-01)"
    rep = next(c for c in m["cases"] if "reproduced-mechanism" in c["id"])
    assert any((o.get("expect") or "") == "production" for o in rep["checks"]["outcome"]), \
        "the reproduced-mechanism case does not stay a finding (PA-02)"
    noop = next(c for c in m["cases"] if "no-report-completes" in c["id"])
    assert any("report.html" in (o.get("target") or "") for o in noop["checks"]["outcome"]), \
        "the no-report case does not assert no HTML (PA-03)"
    withrep = next(c for c in m["cases"] if "report-requires" in c["id"])
    assert any((o.get("expect") or "") == "render" for o in withrep["checks"]["outcome"]), \
        "the --report case does not require the HTML render status (PA-03)"
    flat = " ".join(json.dumps(m, ensure_ascii=False).split())
    for needle in ("actual output oracle", "raw result", "with/without-skill",
                   "grader convenience"):
        assert needle in flat, f"the manifest no longer records {needle!r}"


def t_family_harness_validates_each_case_where_present():
    if not os.path.isfile(HARNESS):
        not_run.append("family harness absent — case validation NOT_RUN (never PASS)")
        return
    for c in manifest()["cases"]:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(c, fh)
            path = fh.name
        try:
            r = subprocess.run([sys.executable, HARNESS, path],
                               capture_output=True, text=True, timeout=60)
            assert r.returncode == 0, f"{c['id']} rejected:\n{r.stdout}"
        finally:
            os.unlink(path)


def main():
    case("every case is structurally valid, none is name-picking",
         t_cases_are_structurally_valid)
    case("the negative case forbids the skill from loading",
         t_negative_forbids_loading)
    case("the ADR/reproduced/report cases are pinned",
         t_adr_reproduced_and_report_cases)
    case("the family harness validates each case (where present)",
         t_family_harness_validates_each_case_where_present)
    for n in not_run:
        print(f"  NOT_RUN  {n}")
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
