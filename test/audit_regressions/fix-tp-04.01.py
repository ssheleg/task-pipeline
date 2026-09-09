#!/usr/bin/env python3
"""FIX-TP-04.01 — an unused rule is not automatically an unneeded one
(sherlock audit, TP-04).

The finding: five run stamps or sixty days without firing were declared proof
a standing instruction was situational and grounds to delete it — for a rare
emergency, a security invariant or a recovery procedure, the absence of the
event is not absence of value, and the archive keeps the text while removing
the active protection.

The fix under test (references/retrospective.md):
* three classes at birth — permanent (never retired by coldness),
  situational (cold counts EXPOSURE opportunities, and cold = review-needed,
  not deletion), temporary (TTL only here; archives once the replacing
  mechanism is verified present);
* every removal explainable — class + trigger + evidence on the archive line;
* the prune rule run as behaviour on the packet's fixtures.

Standard library only.
"""
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DOC = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline",
                   "references", "retrospective.md")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def flat():
    with open(DOC, encoding="utf-8") as fh:
        return " ".join(fh.read().split())


def t_three_classes_at_birth():
    d = flat()
    for cls in ("**permanent**", "**situational**", "**temporary**"):
        assert cls in d, f"class {cls} missing"
    assert "coldness never retires a permanent rule" in d
    assert "TTL only exists on this class" in d


def t_exposure_not_raw_runs():
    d = flat()
    assert "exposure opportunities, not raw runs" in d
    assert "five runs that never touched payments say nothing about a payment rule" in d
    assert "the denominator is runs that COULD have fired it" in d


def t_cold_is_review_not_deletion():
    d = flat()
    assert "cold is evidence worth reviewing, never an automatic deletion" in d
    assert "five runs without firing is the evidence it was situational" not in d, \
        "the old delete-on-cold doctrine survived"
    assert "marks **review-needed**" in d


def t_temporary_needs_verified_replacement():
    d = flat()
    assert "once the replacing mechanism is verified present" in d
    assert "an expired workaround whose replacement is absent is a live defect" in d


def t_removals_explainable():
    d = flat()
    assert "the archive line names the class, the trigger and the evidence" in d


# ---- the prune as behaviour


def prune(rule, now_days, exposures_fired, exposures_total, replacement_verified=False):
    """Returns the disposition per the doctrine."""
    if rule["class"] == "permanent":
        return "keep"
    if rule["class"] == "temporary":
        if now_days > rule["ttl_days"]:
            return "archive" if replacement_verified else "live-defect"
        return "keep"
    # situational
    if exposures_total >= 5 and exposures_fired == 0:
        return "review-needed"
    if exposures_total == 0 and now_days > 60:
        return "review-needed"
    return "keep"


def t_payment_safety_survives_paymentless_runs():
    # five runs, none touched payments → zero exposure opportunities
    verdict = prune({"class": "situational"}, now_days=30,
                    exposures_fired=0, exposures_total=0)
    assert verdict == "keep", \
        "five payment-less runs threatened the payment rule"
    perm = prune({"class": "permanent"}, now_days=400,
                 exposures_fired=0, exposures_total=100)
    assert perm == "keep", "a permanent safety rule was retired by coldness"


def t_expired_workaround_disposition():
    gone = prune({"class": "temporary", "ttl_days": 30}, now_days=45,
                 exposures_fired=0, exposures_total=0, replacement_verified=True)
    assert gone == "archive", "a replaced expired workaround did not archive"
    stuck = prune({"class": "temporary", "ttl_days": 30}, now_days=45,
                  exposures_fired=0, exposures_total=0, replacement_verified=False)
    assert stuck == "live-defect", \
        "an expired workaround with no replacement retired anyway"


def t_situational_cold_is_review():
    v = prune({"class": "situational"}, now_days=30,
              exposures_fired=0, exposures_total=7)
    assert v == "review-needed", "cold with real exposures did not ask for review"


def main():
    case("three classes declared at birth", t_three_classes_at_birth)
    case("situational counts exposure opportunities, not raw runs",
         t_exposure_not_raw_runs)
    case("cold means review-needed; the delete-on-cold doctrine is gone",
         t_cold_is_review_not_deletion)
    case("a temporary rule archives only with a verified replacement",
         t_temporary_needs_verified_replacement)
    case("every removal is explainable", t_removals_explainable)
    case("fixture: payment safety survives payment-less runs; permanent never cold-retired",
         t_payment_safety_survives_paymentless_runs)
    case("fixture: expired workaround — archive with replacement, live defect without",
         t_expired_workaround_disposition)
    case("fixture: situational cold with real exposures → review-needed",
         t_situational_cold_is_review)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
