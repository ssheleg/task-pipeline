#!/usr/bin/env python3
"""The family member gate, run as an audit regression (hub B-108, B-109).

`test/family_gate.py` is a byte-for-byte copy of sshlg-skills `member-gate/family_gate.py`:
the board parses (every row as wide as its own header, no row id twice) and
`.github/workflows/release.yml` keeps `fetch-depth: 0` and `git merge-base --is-ancestor`.
It runs here, inside `npm run test:audit`, which the gate and CI already run, so adding it
needs no workflow edit. Both the check and its self-test (each defect planted in memory)
must pass. Standard library only.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GATE = os.path.join(ROOT, "test", "family_gate.py")

failed = 0
for args in ([], ["--self-test"]):
    r = subprocess.run([sys.executable, GATE] + args, cwd=ROOT, capture_output=True, text=True)
    print(r.stdout.rstrip())
    if r.returncode != 0:
        failed += 1
        print("FAIL  family_gate.py %s exit %d" % (" ".join(args) or "(check)", r.returncode))
sys.exit(1 if failed else 0)
