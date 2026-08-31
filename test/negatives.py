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
# shared-mechanism: negatives.py — 3 copies in this family, kept as one file
#   rather than 3 dialects. The umbrella's gate computes which module-level
#   constants actually differ between the copies and refuses a difference this line
#   does not name: on 2026-08-24 an undeclared success-vocabulary constant made a
#   ported runner report twenty healthy guards as broken, and nothing could see it.
# diverges: MIN_EXPECTED, MIN_PROPS, SUCCESS_MARKERS
import concurrent.futures
import tempfile
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = os.path.join(ROOT, ".github/workflows/validate.yml")
MARKER = "Negative self-test"
PROP_MARKER = "Property check"
MIN_PROPS = 15
# A format change that silently matched nothing would report "0 failures" and look
# like success. Refuse to be that quiet.
#
# Raise this when guards are added. It sat at 20 while the workflow carried 34,
# which is the floor doing half its job: it would have caught a total collapse and
# not the loss of a third of the suite. Set it to the real count, and treat a
# mismatch as a finding rather than as noise to be lowered away.
MIN_EXPECTED = 423


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


def verdict(returncode, stdout, noop):
    """One plant's status, as a function of what it did. PURE on purpose (B-113).

    The `SKIP` branch cannot be reached on a healthy machine — all four skip-capable
    plants run and fire here — so calling this directly is the only way to watch the
    arithmetic that separates a dormant plant from a passing one. `test/runner_test.py`
    does exactly that.
    """
    ok = returncode == 0 and any(k in stdout for k in ("OK:", "SKIP:"))
    skipped = returncode == 0 and "SKIP:" in stdout
    if noop and not skipped:
        return "BROKEN"
    return "SKIP" if skipped else ("PASS" if ok else "FAIL")


def claim(n_tests, n_dormant, n_props, n_prop_dormant):
    """The aggregate sentence. A dormant check is never inside *provably reject*."""
    ran, pran = n_tests - n_dormant, n_props - n_prop_dormant
    parts = []
    if ran:
        parts.append(("all %d" % ran if not n_dormant else "%d of %d" % (ran, n_tests))
                     + " guards provably reject their planted defect")
    if n_dormant:
        parts.append("%d DORMANT, named above — not counted as passing" % n_dormant)
    if pran:
        parts.append("%d property check(s) printed what they assert" % pran)
    if n_prop_dormant:
        parts.append("%d property check(s) DORMANT, named above" % n_prop_dormant)
    if not ran and not pran:
        # Everything that ran declined to run. "PASS: K dormant" is a pass over an
        # empty set, which this file's own comment forbids one paragraph down.
        return None
    return " · ".join(parts)


def copy_dir_of(script):
    """The scratch copy a step makes, so we can tell a real defect from a no-op."""
    m = re.search(r"cp -R \. (\S+)", script)
    return m.group(1) if m else None


def differs_from_repo(path):
    r = subprocess.run(
        ["diff", "-rq", "--exclude=.git", "--exclude=node_modules", "--exclude=graphify-out", path, ROOT],
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

    # Every step copies the repo to a FIXED `/tmp` name. In CI that is correct — one
    # runner per job, no neighbours. On a developer machine two suite runs share those
    # paths and overwrite each other mid-copy: four runs over an unchanged tree once
    # returned four different answers (1, 2, 3 and 4 guards "not firing"), and the cause
    # was never the tree. Board row B-075.
    #
    # The first fix rewrote every `/tmp/...` in the script text to a per-run name, and it
    # broke two plants whose PAYLOAD IS THE WORKFLOW TEXT — they search the copied
    # workflow for a literal path in order to duplicate it. A mechanical rewrite cannot
    # tell a path being used from a path being discussed, which is the umbrella's standing
    # instruction #7, met for the second time in two days.
    #
    # So the paths stay exactly as CI has them, and the runs are serialised instead. An
    # exclusive lock for the duration of the suite: the second run waits rather than
    # corrupting the first, and says so instead of producing a number nobody can trust.
    _LOCK_PATH = os.path.join(tempfile.gettempdir(), "tp-negatives.lock")
    _lock = open(_LOCK_PATH, "w")
    try:
        import fcntl
        try:
            fcntl.flock(_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            print("another run of this suite holds the scratch paths — waiting for it.\n"
                  "  (every step copies the repo to a fixed /tmp name, so two runs at once\n"
                  "   overwrite each other and both report about a tree neither one saw)")
            fcntl.flock(_lock, fcntl.LOCK_EX)
    except ImportError:
        # No flock (Windows): say what is not guaranteed rather than implying it is.
        print("note: no file locking available here — do not run two suites at once")

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

    # Every test does `cp -R .` — from the CURRENT WORKING DIRECTORY. Run with cwd=ROOT
    # that is the live tree, so editing a file mid-run hands some tests a half-written
    # copy and the suite reports on a state the repo was never in. It happened twice in
    # one session, and board row B-023 predicted both.
    #
    # So the suite copies ROOT once into a snapshot and runs every test with cwd there.
    # Editing while it runs is now harmless.
    _snap = tempfile.mkdtemp(prefix="tp-negatives-snap-")
    _base = os.path.join(_snap, "repo")
    shutil.copytree(ROOT, _base, ignore=shutil.ignore_patterns(
        "node_modules", "graphify-out", ".git"), symlinks=True)
    # `.git` is skipped for speed and restored for the two tests that commit a plant.
    #
    # **Ask git where the repository is; do not parse the pointer.** `.git` has three shapes
    # and this repository is consumed in all of them: a directory in a normal clone, a FILE
    # holding `gitdir: …/.git/modules/skills/task-pipeline` in the **submodule** checkout the
    # `sshlg-skills` umbrella ships (which is how most work on this pack happens), and a FILE
    # pointing at a per-worktree directory in a **linked worktree** — which `build.md` itself
    # tells every run to work in.
    #
    # Handling only the directory meant both git-dependent guards ran against a tree with no
    # repository, reported `fatal: not a git repository`, and were counted as *did not fire*:
    # exit 1 with two guards silently disarmed, while CI — which clones normally — stayed
    # green and said nothing. Measured 2026-08-15. Handling the pointer by hand fixed the
    # submodule and left the worktree broken in the identical way, because a per-worktree
    # directory holds HEAD and index while `objects`, `refs` and `config` live wherever its
    # `commondir` points.
    #
    # So BOTH are needed, and asking for only the common one is the trap the first fix fell
    # into: from a worktree on `feature`, a copy of the common dir alone reports
    # `git branch --show-current` = the main checkout's branch and a `git log` missing every
    # commit the worktree made. The common dir is copied first and the per-worktree dir
    # overlaid on top, which is exactly what git resolves at runtime.
    #
    # The result is COPIED rather than pointed at, for two reasons that both bite: a plant
    # that commits would otherwise move the real branch, and a submodule's config carries
    # `core.worktree` aimed back at the live checkout, which would make every git command
    # inside the snapshot operate on the tree the snapshot exists to protect. So the copy is
    # made, that one key is stripped, and `commondir` is dropped because the copy is now
    # self-contained and a dangling pointer is worse than none.
    _git_dst = os.path.join(_base, ".git")

    def _git_path(_flag):
        try:
            _r = subprocess.run(["git", "rev-parse", _flag],
                                cwd=ROOT, capture_output=True, text=True)
        except OSError:
            return None         # no git on PATH: the two git guards will say so themselves
        if _r.returncode != 0 or not _r.stdout.strip():
            return None
        return os.path.normpath(os.path.join(ROOT, _r.stdout.strip()))

    _common = _git_path("--git-common-dir")
    _priv = _git_path("--git-dir")
    if _common and os.path.isdir(_common):
        shutil.copytree(_common, _git_dst, symlinks=True)
        if _priv and os.path.isdir(_priv) and os.path.realpath(_priv) != os.path.realpath(_common):
            # A linked worktree: HEAD, index, logs and the rest of the per-worktree state
            # win over the main checkout's copies of the same names.
            shutil.copytree(_priv, _git_dst, symlinks=True, dirs_exist_ok=True)
            for _stale in ("commondir", "gitdir"):
                _p = os.path.join(_git_dst, _stale)
                if os.path.exists(_p):
                    os.remove(_p)
        _cfg = os.path.join(_git_dst, "config")
        if os.path.isfile(_cfg):
            with open(_cfg, encoding="utf-8") as _fh:
                _kept = [ln for ln in _fh if not re.match(r"\s*worktree\s*=", ln)]
            with open(_cfg, "w", encoding="utf-8") as _fh:
                _fh.writelines(_kept)

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

    # 187 tests x (copy + validate) is thirteen minutes serially, long enough that the
    # suite gets backgrounded and stops being run before a commit — board row B-021.
    # They are independent and each owns a distinct scratch name, so they run in
    # parallel. Collisions only happen between two SUITE runs, which is a different row.
    _WORKERS = min(8, (os.cpu_count() or 4))

    failed, broken, prop_failed, dormant, prop_dormant = [], [], [], [], []
    print(f"running {len(tests)} negative self-tests"
          + (f" + {len(props)} property checks\n" if props else "\n"))
    def _run_one(name_script):
        name, script = name_script
        cdir = copy_dir_of(script)
        sweep([cdir])
        r = subprocess.run(["bash", "-c", script], cwd=_base,
                           capture_output=True, text=True)
        return name, script, cdir, r

    with concurrent.futures.ThreadPoolExecutor(max_workers=_WORKERS) as _ex:
        _results = list(_ex.map(_run_one, tests))
    for name, script, cdir, r in _results:
        # A probe that cannot run says SKIP and exits 0. Counting only "OK:" turned
        # res8's honest degradation into a failure on any machine without PyYAML —
        # the regression this release claimed to have closed, still open one layer up.
        # The trap this runner exists to avoid: a corruption that quietly changed
        # nothing still makes the validator pass, which reads as "the guard is
        # broken" when in fact the *test* is. Tell them apart.
        # A probe that DECLARED a skip changed nothing on purpose. Reading that as a
        # corruption is the same conflation one layer up: "could not look" reported as
        # "the guard is broken". Skips get their own status so they stay visible — and
        # since B-113 their own BUCKET, because `bucket = None` meant the aggregate
        # counted a dormant plant inside *all N guards provably reject*.
        noop = bool(cdir and os.path.isdir(cdir) and not differs_from_repo(cdir))
        status = verdict(r.returncode, r.stdout, noop)
        bucket = {"BROKEN": broken, "SKIP": dormant, "FAIL": failed}.get(status)
        print(f"  {status:<7}{label(name)}")
        if bucket is not None:
            bucket.append((label(name), r.stdout[-500:], r.stderr[-500:]))
        sweep([cdir])

    for name, script in props:
        cdir = copy_dir_of(script)
        sweep([cdir])
        r = subprocess.run(["bash", "-c", script], cwd=_base, capture_output=True, text=True)
        # B-113, the half the first pass left: a property check that printed `SKIP:`
        # counted as one that "printed what it asserts". Same sentence, same defect,
        # one category over — found by the independent reader.
        _st = verdict(r.returncode, r.stdout, False)
        print(f"  {'PASS' if _st == 'PASS' else _st:<7}[property] " + _plabel(name))
        if _st == "SKIP":
            prop_dormant.append((_plabel(name), r.stdout[-500:], r.stderr[-500:]))
        elif _st != "PASS":
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

    shutil.rmtree(_snap, ignore_errors=True)

    if failed or broken or prop_failed:
        print(f"FAIL: {len(failed)} guard(s) did not fire, {len(broken)} test(s) broken"
              + (f", {len(prop_failed)} property check(s) silent" if prop_failed else ""))
        return 1
    # "all 0 guards ... provably reject" is a pass over an empty set, which is the
    # shape this repository calls a refused measurement. Say what actually ran.
    # Named, never merely counted: a number alone invites the reader to assume the
    # skips are the harmless ones, and on 2026-08-30 the harmless one was the plant
    # guarding the release gate.
    for _title, _rows in (("DORMANT — the plant could not construct its precondition in "
                           "this environment, so it proved nothing:", dormant),
                          ("DORMANT — the property check declined to run, so nothing was "
                           "asserted:", prop_dormant)):
        if _rows:
            print(_title)
            for _n, _o, _e in _rows:
                _why = next((_l.strip() for _l in (_o or "").splitlines()
                             if "SKIP:" in _l), "")
                print(f"  * {_n}\n      {_why[:150]}")
            print()
    _line = claim(len(tests), len(dormant), len(props), len(prop_dormant))
    if _line is None:
        # Two ways to reach here and both are the same verdict: everything that ran
        # declined to run, or nothing was present. `PASS: nothing ran` used to be
        # printed with exit 0 for the second one — a pass over an empty set, which
        # this file's own comment three lines up calls a refused measurement.
        print("INCONCLUSIVE: nothing that ran proved anything — "
              + ("no check matched the filter" if not tests and not props else
                 "every check present declined to run")
              + ". A pass over an empty set is not a result")
        return 2
    print("PASS: " + _line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
