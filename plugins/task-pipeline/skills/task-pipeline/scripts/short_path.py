#!/usr/bin/env python3
"""short_path.py: stage 0's proportional decision, computed rather than proposed.

`references/stage-00-intake.md` -> Phase 1d. Until 1.98.0 the short path was only
*proposed*, and silence took the full flow; under a standing "decide and act"
instruction silence is the normal answer, so a small fix met eleven stages every time.
This script takes the five triage answers and DECIDES, printing the one line the run
shows the operator.

    short_path.py --files PATH [PATH ...] --contract yes|no --user-facing yes|no
                  --deploy yes|no --risk R1|R2|R3 [--unknowns N]

Exit 0: the short path (brief in the run ledger, build with tests, one verification,
docs and handoff). Exit 3: the full flow, with every answer that ruled the short path
out. Exit 2: usage. Standard library only.
"""
import argparse
import sys

MAX_FILES = 5
SMALL_RISK = "R1"


def decide(files, contract, user_facing, deploy, risk, unknowns=0):
    """(short?, line) for the five answers plus the gap check's unknowns."""
    n = len(set(files))
    why = []
    if unknowns:
        why.append("%d material unknown(s) left by the gap check" % unknowns)
    if n > MAX_FILES:
        why.append("%d files, over %d" % (n, MAX_FILES))
    if n == 0:
        why.append("no file named, so the change is not bounded")
    if contract:
        why.append("a public contract is touched")
    if user_facing:
        why.append("a user-observable change")
    if deploy:
        why.append("a deploy target")
    if risk != SMALL_RISK:
        why.append("risk %s" % risk)
    if why:
        return False, "full flow: " + "; ".join(why)
    return True, ("short path: %s · %d file%s · no contract · no user-facing change · "
                  "no deploy" % (risk, n, "" if n == 1 else "s"))


def yes_no(v):
    v = v.strip().lower()
    if v not in ("yes", "no"):
        raise argparse.ArgumentTypeError("answer yes or no, not %r" % v)
    return v == "yes"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--files", nargs="*", default=[], help="the paths the change touches")
    p.add_argument("--contract", type=yes_no, required=True)
    p.add_argument("--user-facing", type=yes_no, required=True)
    p.add_argument("--deploy", type=yes_no, required=True)
    p.add_argument("--risk", choices=("R1", "R2", "R3"), required=True)
    p.add_argument("--unknowns", type=int, default=0)
    a = p.parse_args(argv)
    short, line = decide(a.files, a.contract, a.user_facing, a.deploy, a.risk, a.unknowns)
    print(line)
    return 0 if short else 3


if __name__ == "__main__":
    sys.exit(main())
