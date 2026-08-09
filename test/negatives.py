#!/usr/bin/env python3
"""Run the CI negative self-tests locally. Exit 0 = every guard provably fails.

`test/validate.py` proves the repo is well-formed. This proves the *validator* is
not a decoration: each check is fed a planted defect and must reject it. A green
result from a check nobody has watched fail is worth nothing — the same law the
skill's own `references/audit.md` applies to every gate in a run.

The tests live in `.github/workflows/validate.yml` and are read from there, never
duplicated here: a second copy of a corruption is a second thing to drift.

    python3 test/negatives.py            # run them all
    python3 test/negatives.py --list     # just show what would run
    python3 test/negatives.py -k ladder  # only tests whose name matches

Zero dependencies, same as the validator.
"""
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = os.path.join(ROOT, ".github/workflows/validate.yml")
MARKER = "Negative self-test"
PROP_MARKER = "Property check"
MIN_PROPS = 4
# A format change that silently matched nothing would report "0 failures" and look
# like success. Refuse to be that quiet.
#
# Raise this when guards are added. It sat at 20 while the workflow carried 34,
# which is the floor doing half its job: it would have caught a total collapse and
# not the loss of a third of the suite. Set it to the real count, and treat a
# mismatch as a finding rather than as noise to be lowered away.
MIN_EXPECTED = 169


def parse_steps(path):
    """(name, script) per `- name: … / run: |` step. Deliberately not PyYAML —
    the validator ships dependency-free and so does this."""
    steps, name, body, indent = [], None, None, None
    for line in open(path, encoding="utf-8").read().splitlines():
        m = re.match(r"^\s*- name:\s*(.+?)\s*$", line)
        if m:
            if name is not None and body is not None:
                steps.append((name, "\n".join(body)))
            name, body, indent = m.group(1), None, None
            continue
        if name is not None and body is None and re.match(r"^\s*run:\s*\|\s*$", line):
            body = []
            continue
        if body is not None:
            if line.strip() == "":
                body.append("")
                continue
            cur = len(line) - len(line.lstrip())
            if indent is None:
                indent = cur
            if cur < indent:                      # dedent ends the block
                steps.append((name, "\n".join(body)))
                name, body, indent = None, None, None
                continue
            body.append(line[indent:])
    if name is not None and body is not None:
        steps.append((name, "\n".join(body)))
    return steps


def copy_dir_of(script):
    """The scratch copy a step makes, so we can tell a real defect from a no-op."""
    m = re.search(r"cp -R \. (\S+)", script)
    return m.group(1) if m else None


def differs_from_repo(path):
    r = subprocess.run(
        ["diff", "-rq", "--exclude=.git", "--exclude=node_modules", path, ROOT],
        capture_output=True, text=True,
    )
    return bool(r.stdout.strip()) or bool(r.stderr.strip())


def sweep(paths):
    for p in paths:
        if p and p.startswith("/tmp/"):
            shutil.rmtree(p, ignore_errors=True)


def main(argv):
    args = argv[1:]
    only = None
    if "-k" in args:
        only = args[args.index("-k") + 1].lower()
    listing = "--list" in args

    if not os.path.isfile(WORKFLOW):
        print(f"FAIL: no workflow at {WORKFLOW}")
        return 2

    _STEPS = parse_steps(WORKFLOW)          # parsed once; both filters read the same list
    tests = [(n, s) for n, s in _STEPS if MARKER in n]
    if len(tests) < MIN_EXPECTED:
        print(f"FAIL: found only {len(tests)} negative self-tests in the workflow "
              f"(expected at least {MIN_EXPECTED}). The parser or the workflow "
              f"format changed — a run that quietly tests nothing is the failure "
              f"this check exists to prevent.")
        return 2
    if only:
        tests = [(n, s) for n, s in tests if only in n.lower()]
        # The bail moved below the property filter: `-k property` matched no negative
        # self-test and errored out while the checks it named were sitting right there,
        # unrun. A selector that refuses the thing it selected is worse than no selector.
        if not tests and not [1 for _n, _ in _STEPS if PROP_MARKER in _n and only in _n.lower()]:
            print(f"FAIL: no negative self-test or property check matches {only!r}")
            return 2

    label = lambda n: n.replace(MARKER, "").strip().strip("()")
    _plabel = lambda n: n.replace(PROP_MARKER, "").strip().strip("()")
    if listing:
        for n, _ in tests:
            print(" ", label(n))
        # A listing that omits a whole category of test teaches that the category does
        # not exist. They run; they are listed.
        for n, _ in [(n, s) for n, s in _STEPS if PROP_MARKER in n
                     and (not only or only.lower() in n.lower())]:
            print("  [property]", _plabel(n))
        print(f"\n{len(tests)} negative self-tests")
        return 0

    # A leftover copy from an interrupted run would make the next one lie.
    sweep([copy_dir_of(s) for _, s in tests])

    # Property checks assert that something IS printed, so the validator passes inside
    # them and they cannot join the suite above. They still have to run somewhere the
    # author can see: a step that lives only in CI is a step the local gate is blind to,
    # and that is exactly how this runner shipped green while CI failed on a string this
    # very file had renamed.
    props = [(n, s) for n, s in _STEPS if PROP_MARKER in n]
    # Same floor, same reason as MIN_EXPECTED above, one level up: rename the sole
    # property step and this list empties, the runner skips it in silence and still
    # exits 0 — which is the failure property checks were added to close.
    if len(props) < MIN_PROPS:
        print(f"FAIL: found only {len(props)} property checks in the workflow "
              f"(expected at least {MIN_PROPS}). A category that quietly empties is "
              f"a category nobody notices is gone.")
        return 2
    if only:
        props = [(n, s) for n, s in props if only.lower() in n.lower()]

    failed, broken, prop_failed = [], [], []
    print(f"running {len(tests)} negative self-tests"
          + (f" + {len(props)} property checks\n" if props else "\n"))
    for name, script in tests:
        cdir = copy_dir_of(script)
        sweep([cdir])
        r = subprocess.run(["bash", "-c", script], cwd=ROOT,
                           capture_output=True, text=True)
        passed = r.returncode == 0 and "OK:" in r.stdout

        # The trap this runner exists to avoid: a corruption that quietly changed
        # nothing still makes the validator pass, which reads as "the guard is
        # broken" when in fact the *test* is. Tell them apart.
        noop = cdir and os.path.isdir(cdir) and not differs_from_repo(cdir)
        if noop:
            status, bucket = "BROKEN", broken
        elif passed:
            status, bucket = "PASS", None
        else:
            status, bucket = "FAIL", failed
        print(f"  {status:<7}{label(name)}")
        if bucket is not None:
            bucket.append((label(name), r.stdout[-500:], r.stderr[-500:]))
        sweep([cdir])

    for name, script in props:
        cdir = copy_dir_of(script)
        sweep([cdir])
        r = subprocess.run(["bash", "-c", script], cwd=ROOT, capture_output=True, text=True)
        ok = r.returncode == 0 and "OK:" in r.stdout
        print(f"  {'PASS' if ok else 'FAIL':<7}[property] " + _plabel(name))
        if not ok:
            prop_failed.append((_plabel(name), r.stdout[-500:], r.stderr[-500:]))
        sweep([cdir])

    print()
    for title, rows, why in (
        ("BROKEN — the planted defect changed nothing, so the test proves nothing", broken,
         "fix the corruption in .github/workflows/validate.yml"),
        ("FAIL — the validator accepted a planted defect", failed,
         "the guard does not actually fire"),
        ("FAIL — a property the run must print was not printed", prop_failed,
         "nothing was planted here: the check asserts an output, and the output is gone"),
    ):
        if rows:
            print(f"{title}:")
            for n, out, err in rows:
                print(f"\n  * {n} — {why}")
                for line in (out + err).strip().splitlines()[-6:]:
                    print("      " + line)
            print()

    if failed or broken or prop_failed:
        print(f"FAIL: {len(failed)} guard(s) did not fire, {len(broken)} test(s) broken"
              + (f", {len(prop_failed)} property check(s) silent" if prop_failed else ""))
        return 1
    # "all 0 guards ... provably reject" is a pass over an empty set, which is the
    # shape this repository calls a refused measurement. Say what actually ran.
    _parts = ([f"all {len(tests)} guards provably reject their planted defect"] if tests else [])
    _parts += ([f"{len(props)} property check(s) printed what they assert"] if props else [])
    print("PASS: " + " · ".join(_parts) if _parts else
          "PASS: nothing ran — no test matched, which is not a result")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
