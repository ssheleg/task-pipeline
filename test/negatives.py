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
# A format change that silently matched nothing would report "0 failures" and look
# like success. Refuse to be that quiet.
#
# Raise this when guards are added. It sat at 20 while the workflow carried 34,
# which is the floor doing half its job: it would have caught a total collapse and
# not the loss of a third of the suite. Set it to the real count, and treat a
# mismatch as a finding rather than as noise to be lowered away.
MIN_EXPECTED = 146


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

    tests = [(n, s) for n, s in parse_steps(WORKFLOW) if MARKER in n]
    if len(tests) < MIN_EXPECTED:
        print(f"FAIL: found only {len(tests)} negative self-tests in the workflow "
              f"(expected at least {MIN_EXPECTED}). The parser or the workflow "
              f"format changed — a run that quietly tests nothing is the failure "
              f"this check exists to prevent.")
        return 2
    if only:
        tests = [(n, s) for n, s in tests if only in n.lower()]
        if not tests:
            print(f"FAIL: no negative self-test matches {only!r}")
            return 2

    label = lambda n: n.replace(MARKER, "").strip().strip("()")
    if listing:
        for n, _ in tests:
            print(" ", label(n))
        print(f"\n{len(tests)} negative self-tests")
        return 0

    # A leftover copy from an interrupted run would make the next one lie.
    sweep([copy_dir_of(s) for _, s in tests])

    failed, broken = [], []
    print(f"running {len(tests)} negative self-tests\n")
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

    print()
    for title, rows, why in (
        ("BROKEN — the planted defect changed nothing, so the test proves nothing", broken,
         "fix the corruption in .github/workflows/validate.yml"),
        ("FAIL — the validator accepted a planted defect", failed,
         "the guard does not actually fire"),
    ):
        if rows:
            print(f"{title}:")
            for n, out, err in rows:
                print(f"\n  * {n} — {why}")
                for line in (out + err).strip().splitlines()[-6:]:
                    print("      " + line)
            print()

    if failed or broken:
        print(f"FAIL: {len(failed)} guard(s) did not fire, {len(broken)} test(s) broken")
        return 1
    print(f"PASS: all {len(tests)} guards provably reject their planted defect")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
