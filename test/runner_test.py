#!/usr/bin/env python3
"""runner_test.py — the negatives runner's verdict arithmetic, watched from outside.

Board row **B-113**. `test/negatives.py` used to fold every plant that printed `SKIP:`
into *all N guards provably reject their planted defect* — a check that could not
construct its precondition, counted inside the claim that every check rejected one.

The fix cannot be watched by running the suite: on a healthy machine **no plant goes
dormant**. All four skip-capable plants ran and their guards fired when the independent
reader drove them end to end, because `negatives.py` reconstructs a real `.git` in its
snapshot even from a submodule pointer, PyYAML is installed and the checkout is not
shallow. A branch nobody can reach from the outside is exactly the branch that ships
wrong, so the arithmetic lives in two pure functions and this file calls them directly.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import negatives                                                     # noqa: E402

CASES = []


def case(name, got, want):
    CASES.append((name, got, want))


V = negatives.verdict
case("a plant whose validator refused the defect passes", V(0, "OK: refused", False), "PASS")
case("a plant whose validator accepted it fails", V(1, "ERROR: accepted", False), "FAIL")
case("a plant that changed nothing is BROKEN, not FAIL",
     V(0, "OK: refused", True), "BROKEN")
case("a plant that declared a skip is SKIP, not PASS", V(0, "SKIP: no tags", False), "SKIP")
case("a declared skip changed nothing on purpose, so it is not BROKEN",
     V(0, "SKIP: no tags", True), "SKIP")
case("an exit-0 run that printed neither marker is a FAIL, not a pass",
     V(0, "nothing to say", False), "FAIL")

C = negatives.claim
case("with no dormant plant the claim says `all N`",
     C(419, 0, 15, 0),
     "all 419 guards provably reject their planted defect · "
     "15 property check(s) printed what they assert")
case("a dormant plant is subtracted from the claim and named",
     C(419, 2, 15, 0),
     "417 of 419 guards provably reject their planted defect · "
     "2 DORMANT, named above — not counted as passing · "
     "15 property check(s) printed what they assert")
case("a dormant PROPERTY check is subtracted too — the same sentence, one category over",
     C(419, 0, 15, 3),
     "all 419 guards provably reject their planted defect · "
     "12 property check(s) printed what they assert · "
     "3 property check(s) DORMANT, named above")
case("everything dormant is not a pass over an empty set", C(4, 4, 0, 0), None)
case("everything dormant on both sides is not a pass either", C(4, 4, 2, 2), None)
case("nothing present at all is not a pass either — the `-k` matched-nothing path",
     C(0, 0, 0, 0), None)
case("one plant left standing still makes a claim, about one",
     C(4, 3, 0, 0),
     "1 of 4 guards provably reject their planted defect · "
     "3 DORMANT, named above — not counted as passing")


def _run() -> int:
    bad = 0
    for name, got, want in CASES:
        ok = got == want
        print(f"  {'ok ' if ok else 'FAIL':<5} {name}")
        if not ok:
            bad += 1
            print(f"        wanted {want!r}\n        got    {got!r}")
    # The floors the runner refuses to go below are claims about the corpus, and a
    # ratchet nobody reads is a ratchet that drifts. Compare them against the corpus.
    steps = negatives.parse_steps(negatives.WORKFLOW)
    tests = [1 for n, _s in steps if negatives.MARKER in n]
    props = [1 for n, _s in steps if negatives.PROP_MARKER in n]
    for label, floor, real in (("MIN_EXPECTED", negatives.MIN_EXPECTED, len(tests)),
                               ("MIN_PROPS", negatives.MIN_PROPS, len(props))):
        ok = floor == real
        print(f"  {'ok ' if ok else 'FAIL':<5} {label} is the counted number, not a "
              f"carried-over one ({floor} vs {real})")
        bad += 0 if ok else 1
    print()
    if bad:
        print(f"FAIL: {bad} of {len(CASES) + 2} runner cases behaved wrongly")
        return 1
    print(f"PASS: negatives runner — {len(CASES) + 2} cases, "
          f"{sum(1 for _n, _g, w in CASES if w is None)} of them the empty-set branch")
    return 0


if __name__ == "__main__":
    sys.exit(_run())
