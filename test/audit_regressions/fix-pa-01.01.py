#!/usr/bin/env python3
"""FIX-PA-01.01 — a documented decision does not auto-justify a defect
(sherlock audit, PA-01).

The finding: the audit's "already decided" rule counted only (a) undecided and
(c) decided-but-not-propagated as work, treating any (b) decided-and-documented
as "the audit being wrong" — so a documented ADR permitting a security
violation was excluded from findings by definition, a systemic false-negative
source.

The fix under test: decision status and technical validity are DIFFERENT axes.
A documented decision splits into an accepted trade-off (a real named cost →
accepted limitation) and a documented violation (still breaks a
security/contract invariant → REMAINS a finding with decision_id, reason to
revisit, and counter-evidence). Documented in SKILL.md, and the classifier is
run as behaviour.

Standard library only.
"""
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "project-audit", "SKILL.md")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def t_doctrine_states_two_axes():
    flat = " ".join(open(SKILL, encoding="utf-8").read().split())
    for needle in ("decision status and\n  technical validity are DIFFERENT AXES".replace("\n  ", " "),
                   '"it\'s by design" is not a proof of correctness',
                   "accepted trade-off",
                   "documented violation",
                   "REMAINS a `finding`, carrying the `decision_id`, the reason to revisit,\n"
                   "    and the counter-evidence".replace("\n    ", " "),
                   "systemic source of false NEGATIVES"):
        assert needle in flat, f"the doctrine no longer states {needle!r}"
    assert "**(b)** is the audit being wrong, and recording that is worth more" not in flat, \
        "the 'documented ⇒ not a finding' rule survived"


# ---------------- the classifier, executed


def classify_row(row):
    """decision status × technical validity → verdict.
    row: {status: undecided|documented_here|elsewhere, valid: bool,
          breaks_contract: bool, accepted_cost: str|None}"""
    st = row["status"]
    if st == "undecided":
        return "finding"
    if st == "elsewhere":
        return "finding"                          # not propagated → work
    # documented_here: split by technical validity, not by the paper existing
    if row.get("breaks_contract") or not row.get("valid", True):
        return "finding"                          # documented violation
    if row.get("accepted_cost"):
        return "accepted-limitation"              # a real named cost
    return "not-a-defect"


def t_documented_violation_stays_a_finding():
    adr_logs_refresh_token = {
        "status": "documented_here", "valid": False, "breaks_contract": True,
        "decision_id": "ADR-014", "accepted_cost": None,
    }
    assert classify_row(adr_logs_refresh_token) == "finding", \
        "an ADR permitting a refresh-token leak was excluded as documented — the finding itself"


def t_accepted_trade_off_is_a_limitation_not_a_defect():
    single_browser = {
        "status": "documented_here", "valid": True, "breaks_contract": False,
        "accepted_cost": "only Chromium is supported; the contract states so",
    }
    assert classify_row(single_browser) == "accepted-limitation", \
        "a conscious trade-off with a named cost was flagged as a defect"


def t_undecided_and_unpropagated_are_findings():
    assert classify_row({"status": "undecided"}) == "finding"
    assert classify_row({"status": "elsewhere"}) == "finding"


def t_a_documented_valid_decision_with_no_cost_is_clean():
    ok = {"status": "documented_here", "valid": True, "breaks_contract": False,
          "accepted_cost": None}
    assert classify_row(ok) == "not-a-defect"


def main():
    case("the doctrine separates decision status from technical validity",
         t_doctrine_states_two_axes)
    case("a documented violation stays a finding", t_documented_violation_stays_a_finding)
    case("an accepted trade-off is a limitation, not a defect",
         t_accepted_trade_off_is_a_limitation_not_a_defect)
    case("undecided and unpropagated are findings",
         t_undecided_and_unpropagated_are_findings)
    case("a documented, valid, cost-free decision is clean",
         t_a_documented_valid_decision_with_no_cost_is_clean)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
