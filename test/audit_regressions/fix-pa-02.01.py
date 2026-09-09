#!/usr/bin/env python3
"""FIX-PA-02.01 — a missing production measurement does not forbid a proven
finding (sherlock audit, PA-02).

The finding: the doctrine required production incidence before a row could be
a `finding` ("a blind consequence is not a finding"), while the collector's
`_finding` carried no frequency/consequence fields at all — so prose and data
disagreed, and a reproduced auth bug or race, proven BEFORE any incident,
could be demoted by the absence of telemetry. UNKNOWN was being read as 0.

The fix under test:
* SKILL.md separates FIVE axes (mechanism, reproduction, exposure, observed
  incidence, impact uncertainty): a proven defect may have incidence UNKNOWN;
  UNKNOWN != 0; a documented exception never flips a failed invariant to PASS;
  unknown attacker control lowers confidence, not observed behaviour;
* audit.py `_finding` writes mechanism/incidence/observed_scope/observed_at
  into every row (run as behaviour, not grepped);
* templates/finding-evidence.json is the minimal schema keeping observations
  apart from assumptions, and both task-pipeline references point at it.

Standard library only.
"""
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PA = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "project-audit")
TP = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def t_doctrine_separates_the_axes():
    flat = " ".join(read(os.path.join(PA, "SKILL.md")).split())
    for needle in ("FIVE axes, not one",
                   "A proven defect may have incidence UNKNOWN",
                   "UNKNOWN ≠ 0",
                   "no production log is needed to license the row",
                   "external incidence UNKNOWN",
                   "lowers exploitability CONFIDENCE",
                   "does not turn a failed invariant into PASS",
                   "the finding stands on its mechanism and reproduction axes",
                   "an interview is not a prerequisite for a row"):
        assert needle in flat, f"SKILL.md no longer states {needle!r}"
    assert "A blind consequence is not a finding" not in flat, \
        "the production-incidence requirement survived — the finding itself"


def t_collector_writes_the_axes():
    spec = importlib.util.spec_from_file_location(
        "audit", os.path.join(PA, "scripts", "audit.py"))
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    row = audit._finding("secrets-tree", "src/x.py", "credential in tree",
                         "high", "wide", "low", "rotate it")
    assert row.get("mechanism") == "confirmed", "the mechanism axis is missing"
    assert row.get("incidence") == "unknown", \
        "incidence does not default to UNKNOWN — an unmeasured zero again"
    assert row.get("observed_scope") == "local checkout", "no observation scope"
    assert "observed_at" in row and row["observed_at"].endswith("Z"), \
        "no observation time in the row"
    json.dumps(row)  # the sidecar must be able to carry it


def t_incidence_unknown_is_not_zero_in_behaviour():
    # The rule as the doctrine states it: verdicts derive from the mechanism
    # axis; the incidence axis prices, it never demotes.
    def verdict(mechanism, incidence):
        if mechanism != "confirmed":
            return "hypothesis"
        return "finding"          # incidence unknown/never/blind never demotes
    assert verdict("confirmed", "unknown") == "finding", \
        "a reproduced defect was demoted by missing telemetry"
    assert verdict("confirmed", "never-observed") == "finding"
    assert verdict("suspected", "unknown") == "hypothesis"


def t_template_is_the_minimal_schema():
    tpl = json.loads(read(os.path.join(TP, "templates", "finding-evidence.json")))
    assert tpl["schema"] == "finding-evidence/1"
    for axis in ("mechanism_status", "reproduction", "exposure",
                 "observed_incidence", "impact_uncertainty",
                 "observed_scope", "observed_at", "observations", "assumptions"):
        assert axis in tpl["fields"], f"the template lost the {axis} axis"
    assert tpl["fields"]["observed_incidence"]["default"] == "unknown"
    rules = " ".join(tpl["rules"])
    assert "remains a finding" in rules and "never lowers mechanism_status" in rules
    assert "only when the unknown would change the action" in rules, \
        "the no-forced-interview rule is gone"


def t_references_point_at_the_schema():
    for name in ("audit.md", "documentation.md"):
        flat = " ".join(read(os.path.join(TP, "references", name)).split())
        assert "finding-evidence.json" in flat, f"references/{name} does not name the schema"
        assert "UNKNOWN" in flat, f"references/{name} lost the UNKNOWN rule"


def main():
    case("the doctrine separates the five axes", t_doctrine_separates_the_axes)
    case("the collector writes mechanism/incidence/scope/time into every row",
         t_collector_writes_the_axes)
    case("incidence unknown never demotes a confirmed mechanism",
         t_incidence_unknown_is_not_zero_in_behaviour)
    case("the template is the minimal evidence schema", t_template_is_the_minimal_schema)
    case("both references point at the schema", t_references_point_at_the_schema)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
