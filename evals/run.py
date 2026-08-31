#!/usr/bin/env python3
"""Validate the evaluation suite and print the run protocol.

**This script does not run a model, and it never reports a pass.** Anthropic's
guidance ships no runner for Skill evaluations ("There is not currently a built-in
way to run these evaluations"), and a script that claimed to have executed one
would be the exact failure this repository's own doctrine is written against — a
tool describing a world it is not looking at.

What it does:
  * checks the suite is well-formed and covers every required category;
  * prints each query with its expected behaviours, ready to run;
  * checks RESULTS.md exists and says, honestly, when the suite last ran.

    python3 evals/run.py           # validate + print the protocol
    python3 evals/run.py --list    # ids and categories only

Zero dependencies, same as the validator.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# EVERY suite, discovered — the directory held one suite per skill from
# 2026-08-31 (evidence-docs and project-audit joined task-pipeline), and a
# runner pinned to one filename would validate a third of what ships.
SUITES = sorted(glob.glob(os.path.join(ROOT, "evals", "*.evals.json")))
SUITE = os.path.join(ROOT, "evals", "task-pipeline.evals.json")
RESULTS = os.path.join(ROOT, "evals", "RESULTS.md")

# The enterprise guidance requires coverage of triggering (both directions) and
# ambiguity. The last two are ours: instruction following is where a ten-stage
# skill actually fails, and coexistence is what a broad description breaks.
REQUIRED = ("should_trigger", "should_not_trigger", "ambiguous",
            "instruction_following", "coexistence")
MIN_EVALS = 3          # Anthropic: "At least three evaluations created"


def validate_suite(path):
    """Every gap in one suite, in a stable order. The rules are the same for
    every skill's suite — a second rule set would drift."""
    errors = []
    suite = json.load(open(path, encoding="utf-8"))
    evals = suite.get("evals") or []
    seen = set()
    for e in evals:
        where = e.get("id", "<no id>")
        if not e.get("id"):
            errors.append("an eval has no id")
        elif e["id"] in seen:
            errors.append(f"duplicate eval id {e['id']}")
        seen.add(e.get("id"))
        if e.get("category") not in REQUIRED:
            errors.append(f"{where}: category {e.get('category')!r} is not one of {list(REQUIRED)}")
        if not (e.get("query") or "").strip():
            errors.append(f"{where}: empty query")
        beh = e.get("expected_behavior") or []
        if len(beh) < 2:
            errors.append(f"{where}: needs at least two expected behaviours — one is a hope, "
                          "two is a rubric")
        if not (e.get("why") or "").strip():
            errors.append(f"{where}: no `why` — an eval whose failure mode is unstated "
                          "cannot tell you what broke")

    if len(evals) < MIN_EVALS:
        errors.append(f"{len(evals)} eval(s); at least {MIN_EVALS} are required")
    covered = {e.get("category") for e in evals}
    for cat in REQUIRED:
        if cat not in covered:
            errors.append(f"no eval covers {cat!r}")
    return suite, evals, errors


def main(argv):
    if not os.path.isfile(SUITE):
        print(f"FAIL: no suite at {os.path.relpath(SUITE, ROOT)}")
        return 2
    parsed, errors = [], []
    for _sp in SUITES:
        _suite, _evals, _errs = validate_suite(_sp)
        parsed.append((os.path.basename(_sp), _suite, _evals))
        errors += [f"{os.path.basename(_sp)}: {e}" for e in _errs]

    if errors:
        print("FAIL: evaluation suite invalid")
        for e in errors:
            print("  - " + e)
        return 1

    suite = next(s for n, s, ev in parsed if n == "task-pipeline.evals.json")
    evals = [e for _, _, ev in parsed for e in ev]
    by_cat = {}
    for e in evals:
        by_cat.setdefault(e["category"], []).append(e)

    if "--list" in argv:
        for name, _s, ev in parsed:
            print(f"{name} — {_s.get('skill', '?')}")
            for cat in REQUIRED:
                for e in ev:
                    if e["category"] == cat:
                        print(f"  {e['id']:<10} {cat:<22} {e['query'][:60]}")
        print(f"\n{len(evals)} evals across {len(by_cat)} categories, "
              f"{len(parsed)} suite(s)")
        return 0

    print("=" * 72)
    print("task-pipeline plugin evaluation protocol (one section per suite)")
    print("=" * 72)
    print("Run each query in a FRESH session with the pack installed, once per")
    print("model in", suite.get("models", []), "— effectiveness varies by model.")
    print("Record every verdict in evals/RESULTS.md with the date and the model.")
    print("A query you did not run is not a pass; leave it blank and say so.\n")
    for name, _s, ev in parsed:
        print(f"\n=== {name} — {_s.get('skill', '?')} ===")
        for cat in REQUIRED:
            group = [e for e in ev if e["category"] == cat]
            if not group:
                continue
            print(f"\n--- {cat} ---")
            for e in group:
                print(f"\n[{e['id']}] {e['query']}")
                print(f"    why: {e['why']}")
                for b in e["expected_behavior"]:
                    print(f"    [ ] {b}")

    print("\n" + "=" * 72)
    if not os.path.isfile(RESULTS):
        print("NO RESULTS FILE — the suite has never been recorded as run.")
        return 1
    body = open(RESULTS, encoding="utf-8").read()
    # Count RUN HEADINGS only, outside fenced blocks. Counting every date in the
    # file swept up the ratchet table and the fenced example and reported five runs
    # against zero — a reporting tool that overstates its own subject, which is the
    # one thing this script exists not to do.
    outside, infence = [], False
    for ln in body.split("\n"):
        if re.match(r"^\s*(```|~~~)", ln):
            infence = not infence
            continue
        if not infence:
            outside.append(ln)
    runs = [l for l in outside if re.match(r"^## 20\d{2}-\d{2}-\d{2}\b", l)]
    print("suites: " + " · ".join(f"{n.replace('.evals.json', '')} {len(ev)}"
                                    for n, _s, ev in parsed))
    print(f"suite: {len(evals)} evals · recorded runs: {len(runs)}")
    if not runs:
        print("RESULTS.md carries no dated run — the suite is authored and unexecuted.")
    print("OK: suite valid. Execution is a human/agent step; this script never")
    print("    reports a pass it did not observe.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
