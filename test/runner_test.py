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


# --- the shard split (v1.93.0) -------------------------------------------------------
# CI runs one slice per matrix value. Two properties make that safe, and both are
# arithmetic a healthy run never exercises: every check lands in exactly one slice, and
# a spec read wrongly is refused rather than guessed. A slice nobody runs is a set of
# guards proven nowhere under a job that reports green.
_ITEMS = list(range(451))
_SLICES = [negatives.shard(_ITEMS, _i, 8) for _i in range(1, 9)]
case("eight slices cover every check exactly once",
     sorted(x for s in _SLICES for x in s), _ITEMS)
case("slices are balanced to within one check",
     max(map(len, _SLICES)) - min(map(len, _SLICES)) <= 1, True)
case("the split is a function of position, so the same tree splits the same way",
     negatives.shard(_ITEMS, 3, 8) == negatives.shard(list(_ITEMS), 3, 8), True)
case("one slice of one is the whole suite", negatives.shard(_ITEMS, 1, 1), _ITEMS)
case("`3/8` reads as the third of eight", negatives.parse_shard("3/8"), (3, 8))


def _refused(spec):
    try:
        negatives.parse_shard(spec)
    except ValueError:
        return True
    return False


for _spec in ("0/8", "9/8", "8", "a/b", "", "3/0", "-1/8"):
    case(f"`{_spec}` is refused, never guessed", _refused(_spec), True)


# CLI admission must precede directory scanning, locking and snapshots. The old
# parser treated --help/unknown flags as an instruction to run every plant.
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from unittest.mock import patch
import negative_lock


class _ScanReached(Exception):
    """Not a RuntimeError: main() reports lifecycle RuntimeErrors as a refusal."""


def _admission(args):
    with patch.object(negatives, "scan", side_effect=_ScanReached()), \
            redirect_stdout(StringIO()), redirect_stderr(StringIO()):
        try:
            negatives.main(["negatives.py", *args])
        except SystemExit as exc:
            return exc.code
        except _ScanReached:
            return "scan"
    return "returned"


for _args, _want in [(["--help"], 0), (["-h"], 0), (["--unknown"], 2),
                     (["--lis"], 2), (["-k"], 2), (["--shard"], 2),
                     (["--list"], "scan"), (["-k", "exclusion"], "scan"),
                     (["--shard", "1/8"], "scan")]:
    case(f"CLI {_args!r} is admitted before scanning or allocation",
         _admission(_args), _want)


def _selection(args):
    # Stop at the real shard function before any plant can run; the read-only list
    # path still uses the normal parser and selection. Locks live in an owned temp.
    import tempfile
    from pathlib import Path
    fixture = [("001-alpha.sh", "Negative self-test (alpha)", ""),
               ("002-beta.sh", "Negative self-test (beta)", "")]
    with tempfile.TemporaryDirectory(prefix="tp-runner-cli-") as folder, \
            patch.object(negatives, "scan", return_value=(fixture, [])), \
            patch.object(negatives, "MIN_EXPECTED", 2), \
            patch.object(negative_lock, "scratch_lock_path",
                         return_value=str(Path(folder) / "owned-family.lock")):
        out = StringIO()
        with redirect_stdout(out), redirect_stderr(StringIO()):
            code = negatives.main(["negatives.py", "--list", *args])
        return code, [x.strip() for x in out.getvalue().splitlines()
                      if x.strip() in ("alpha", "beta")]


for _args in (["-k", "alpha"], ["-kalpha"], ["--shard", "1/2"],
              ["--shard=1/2"], ["-kbeta", "-kalpha"],
              ["--shard=2/2", "--shard=1/2"]):
    case(f"CLI selection {_args!r} retains its parsed filter",
         _selection(_args), (0, ["alpha"]))


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
    steps = negatives.load_checks(negatives.NEG_DIR)
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
