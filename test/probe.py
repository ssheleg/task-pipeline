#!/usr/bin/env python3
"""probe.py — plant, run, restore, and prove the plant reached the check that owns it.

R-001 has said since 2026-08-03: *when a check stays silent against a planted defect,
prove the plant landed in the text the check actually parses before touching the check.*
Its retirement condition, written at birth, was "a probe harness exists that asserts the
plant changed the parsed text, making this mechanical." This is that harness.

Three assertions per plant, and the third is the one hand-rolled probes keep missing:

1. **The substitution landed.** `str.replace` that matches nothing returns the string
   unchanged and raises nothing, so a probe can run to completion having planted
   nothing at all.
2. **The validator rejects.** Asserted on the exit code, never on a `FAIL` line in
   stdout — CI reads `$?`, and a gate has shipped that printed FAIL and exited 0.
3. **The guard that fired is the guard under test.** A plant that trips some *other*
   check proves that other check works. Three probes in one day passed this way:
   one removed 1 of 3 identical lines and left the shape intact, one decremented a
   number in an already-released section, one deleted the shouted spelling of a
   phrase and left the lowercase one. Each landed somewhere real and proved nothing.

Usage as a library:

    from probe import Plant, run_probes
    run_probes([
        Plant("the rail glyph must be in the legend",
              "…/references/progress.md", "3 ▶", "3 »",
              expect="the legend does not define it"),
    ])

Usage as a command: `python3 test/probe.py --self-test` runs the harness against
itself — including a plant that must NOT land, because a harness whose failure branch
has never executed is the thing this file exists to stop.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IGNORE = shutil.ignore_patterns("node_modules", "graphify-out", ".git", "__pycache__",
                                ".worktrees", ".task-pipeline")


@dataclass
class Plant:
    """One planted defect and the guard it is supposed to wake up.

    `expect` is a substring of that guard's own message. It is required, not optional:
    without it the probe asserts only that *something* broke, which is the false
    success this harness exists to remove.
    """
    label: str
    rel_path: str
    old: str
    new: str
    expect: str
    count: int = 1


def _validator_output(cwd: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, "test/validate.py"], cwd=cwd,
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def run_probes(plants, root: str = ROOT, verbose: bool = True) -> int:
    """Return 0 when every plant is rejected by the guard it names."""
    snap = tempfile.mkdtemp(prefix="tp-probe-")
    base = os.path.join(snap, "repo")
    shutil.copytree(root, base, ignore=IGNORE, symlinks=True)
    bad = 0
    try:
        rc, _ = _validator_output(base)
        if verbose:
            print(f"{'clean control':<54} exit={rc} (want 0)")
        if rc != 0:
            print("  the base is RED — a guard added here would pass for the wrong "
                  "reason (gates.md -> Before you run a check, precondition 1)")
            return 1

        for p in plants:
            work = os.path.join(snap, "w")
            shutil.rmtree(work, ignore_errors=True)
            shutil.copytree(base, work, symlinks=True)
            target = os.path.join(work, p.rel_path)
            if not os.path.isfile(target):
                print(f"{p.label:<54} PLANT TARGET MISSING: {p.rel_path}")
                bad += 1
                continue
            src = open(target, encoding="utf-8").read()
            out = src.replace(p.old, p.new, p.count)
            if out == src:
                # Assertion 1. Doubt the probe before the check (R-001).
                print(f"{p.label:<54} PLANT DID NOT LAND — the probe is wrong, "
                      "not the guard")
                bad += 1
                continue
            open(target, "w", encoding="utf-8").write(out)

            rc, output = _validator_output(work)
            hits = [ln for ln in output.splitlines() if ln.lstrip().startswith("- ")]
            own = [ln for ln in hits if p.expect in ln]
            if rc == 0:
                verdict = "NOT REJECTED"
                bad += 1
            elif not own:
                # Assertion 3. Something broke; it was not the guard under test.
                verdict = f"WRONG GUARD FIRED (wanted {p.expect!r})"
                bad += 1
            else:
                verdict = "rejected by its own guard"
            if verbose:
                print(f"{p.label:<54} exit={rc}  {verdict}")
                for ln in (own or hits)[:1]:
                    print(f"     {ln.strip()[:108]}")
    finally:
        shutil.rmtree(snap, ignore_errors=True)
    return 1 if bad else 0


def _self_test() -> int:
    """Probe the harness. Its failure branches must be seen executing, like any check."""
    S = "plugins/task-pipeline/skills/task-pipeline"
    print("harness self-test — the failure branches must fire\n")

    good = [Plant("a plant that lands and wakes its own guard",
                  f"{S}/references/progress.md", "3 ▶", "3 »",
                  expect="the legend does not define it")]
    rc_good = run_probes(good)
    print(f"  -> expected 0, got {rc_good}\n")

    print("a plant that CANNOT land (the needle is not in the file):")
    miss = [Plant("a plant that cannot land",
                  f"{S}/references/progress.md",
                  "this string is not in the file", "x",
                  expect="never reached")]
    rc_miss = run_probes(miss)
    print(f"  -> expected 1, got {rc_miss}\n")

    print("a plant that lands but wakes a DIFFERENT guard:")
    wrong = [Plant("a plant that trips someone else's check",
                   f"{S}/references/progress.md", "3 ▶", "3 »",
                   expect="a message no guard in this repository prints")]
    rc_wrong = run_probes(wrong)
    print(f"  -> expected 1, got {rc_wrong}\n")

    ok = (rc_good, rc_miss, rc_wrong) == (0, 1, 1)
    print("PASS: the harness rejects a no-op plant and a wrong-guard plant"
          if ok else "FAIL: the harness did not behave as documented")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_self_test() if "--self-test" in sys.argv else
             print("usage: python3 test/probe.py --self-test  "
                   "(or import Plant/run_probes)") or 0)
