#!/usr/bin/env python3
"""Run the negative self-tests. Exit 0 = every guard provably fails.

`test/validate.py` proves the repo is well-formed. This proves the *validator* is
not a decoration: each check is fed a planted defect and must reject it. A green
result from a check nobody has watched fail is worth nothing — the same law the
skill's own `references/audit.md` applies to every gate in a run.

The tests live in `test/negatives/`, one file per check, and the directory is the
whole source of truth: no manifest, no second list. Each file is

    #!/usr/bin/env bash
    # name: Negative self-test (<what the planted defect is>)
    <the script, run from the repository root>

and a file whose name says `Property check` asserts that something IS printed
rather than planting a defect. They lived inline in `.github/workflows/validate.yml`
until v1.93.0, which put the workflow at 507,836 of GitHub's 512,000 bytes — past
the limit a workflow goes SILENT, it is not marked red — and ran all of them in one
job for 90–111 minutes. CI now runs this file once per shard of a matrix.

    python3 test/negatives.py              # run them all
    python3 test/negatives.py --list       # just show what would run
    python3 test/negatives.py -k ladder    # only checks whose name matches
    python3 test/negatives.py --shard 3/8  # the third of eight deterministic slices

Zero dependencies, same as the validator.
"""
# shared-mechanism: negatives.py — 3 copies in this family, kept as one file
#   rather than 3 dialects. The umbrella's gate computes which module-level
#   constants actually differ between the copies and refuses a difference this line
#   does not name: on 2026-08-24 an undeclared success-vocabulary constant made a
#   ported runner report twenty healthy guards as broken, and nothing could see it.
#   Since v1.93.0 this copy reads `test/negatives/` (NEG_DIR, NAME_HEADER, FILE_RE)
#   where the others read the workflow (WORKFLOW); measured against the sibling copies
#   on 2026-10-12, which also differ from each other on ENV_ERROR_SIGNS and STAGES.
# diverges: ENV_ERROR_SIGNS, FILE_RE, MIN_EXPECTED, MIN_PROPS, NAME_HEADER, NEG_DIR, STAGES, SUCCESS_MARKERS, WORKFLOW
import atexit
import concurrent.futures
import tempfile
import os
import re
import shutil
import subprocess
import sys
import stat
import shlex
from negative_lock import acquire_scratch_lock, ScratchProcesses

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# One file per check. The directory is the source of truth; nothing lists it.
NEG_DIR = os.path.join(ROOT, "test", "negatives")
# Line 2 of every file. Line 1 is the `#!/usr/bin/env bash` shebang, so a single
# file can also be run by hand from the repository root.
NAME_HEADER = "# name: "
# `NNN-slug.sh`: the number orders the files and the slug says what they plant.
FILE_RE = r"^\d{3}-[a-z0-9][a-z0-9-]*\.sh$"
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
MIN_EXPECTED = 527


def scan(path=NEG_DIR):
    """([(file, name, script)], [problem]) for the check directory, in file order.

    PURE over the directory: nothing runs. A file that does not have the shape is a
    PROBLEM, never a silent skip — a check the loader quietly drops is a guard that
    stopped being proven while every count still reads healthy, which is the failure
    MIN_EXPECTED exists to refuse one level up. `test/validate.py` fails on every
    problem; the runner refuses to start while one stands.
    """
    checks, problems, numbers, names = [], [], {}, {}
    if not os.path.isdir(path):
        return checks, [f"{path} is not a directory"]
    for fn in sorted(os.listdir(path)):
        full = os.path.join(path, fn)
        if fn.startswith(".") or os.path.isdir(full):
            problems.append(f"{fn}: not a check file — the directory holds checks only")
            continue
        if not re.match(FILE_RE, fn):
            problems.append(f"{fn}: the name is not `NNN-slug.sh`, so it would never be "
                            "read as a check")
            continue
        try:
            text = open(full, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError) as exc:
            problems.append(f"{fn}: unreadable ({type(exc).__name__})")
            continue
        lines = text.split("\n")
        if len(lines) < 3 or lines[0] != "#!/usr/bin/env bash" \
                or not lines[1].startswith(NAME_HEADER):
            problems.append(f"{fn}: line 1 must be `#!/usr/bin/env bash` and line 2 "
                            f"`{NAME_HEADER}<step name>`")
            continue
        name = lines[1][len(NAME_HEADER):].strip()
        if not (name.startswith(MARKER + " (") or name.startswith(PROP_MARKER + " (")) \
                or not name.endswith(")"):
            problems.append(f"{fn}: its name {name!r} is neither `{MARKER} (…)` nor "
                            f"`{PROP_MARKER} (…)`, so no count would include it")
            continue
        script = "\n".join(lines[2:])
        if not script.strip():
            problems.append(f"{fn}: no script under the header")
            continue
        num = fn[:3]
        if num in numbers:
            problems.append(f"{fn}: number {num} is also {numbers[num]}")
        numbers.setdefault(num, fn)
        if name in names:
            problems.append(f"{fn}: the name {name!r} is also {names[name]} — the runner "
                            "and `-k` select by name, so two would be one")
        names.setdefault(name, fn)
        checks.append((fn, name, script))
    return checks, problems


def load_checks(path=NEG_DIR):
    """(name, script) per check, in file order — what every reader of the corpus
    consumes: this runner, `test/anchors.py` and `test/validate.py`."""
    return [(n, s) for _f, n, s in scan(path)[0]]


def parse_shard(spec):
    """`I/N` -> (I, N), 1 <= I <= N. Anything else raises ValueError, never a guess:
    a shard spec read wrongly is a slice of the suite that silently never runs."""
    m = re.match(r"^\s*(\d+)\s*/\s*(\d+)\s*$", spec or "")
    if not m:
        raise ValueError(f"--shard wants I/N, got {spec!r}")
    i, n = int(m.group(1)), int(m.group(2))
    if n < 1 or not 1 <= i <= n:
        raise ValueError(f"--shard {spec}: I must be in 1..N")
    return i, n


def shard(items, i, n):
    """The I-th of N slices, by position modulo N. PURE and deterministic: every item
    lands in exactly one slice, and the same directory always splits the same way, so
    a red shard on CI is the same set of checks on a maintainer's machine."""
    return [x for k, x in enumerate(items) if k % n == i - 1]


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


def copy_dirs_of(script):
    """All literal plant copies in the corpus's bounded shell declaration grammar.

    Only standalone `rm -rf PATH && cp -R . PATH` (or bare `cp -R . PATH`)
    lines grant cleanup authority; the corpus's optional trailing removal of the
    same target's `.git` is admitted too. Ignore comments and heredoc payloads, never
    regex-search quoted test data. Unsupported executable copy spellings refuse.
    This is not a general shell parser or an ownership claim over arbitrary /tmp.
    """
    result, heredoc, pending = [], None, ""
    for line in script.splitlines():
        stripped = line.strip()
        if heredoc is not None:
            delimiter, tabs = heredoc
            if (line.lstrip('\t') if tabs else line) == delimiter:
                heredoc = None
            continue
        if not pending and (not stripped or stripped.startswith('#')):
            continue
        # Wait for a complete quoted/continued command before admitting a line;
        # a standalone-looking declaration inside an echo string is only data.
        pending += line + '\n'
        if (len(line) - len(line.rstrip('\\'))) % 2:
            continue
        try:
            words = shlex.split(pending, comments=True)
        except ValueError:
            continue
        stripped, pending = pending.strip(), ''
        # Corpus payloads use one literal heredoc per command. Do not interpret it.
        opener = re.search(r"<<(-?)[ \t]*(?:'([A-Za-z_][A-Za-z0-9_]*)'|\"([A-Za-z_][A-Za-z0-9_]*)\"|([A-Za-z_][A-Za-z0-9_]*))", stripped)
        if opener and re.match(r"(?:python3? -|cat)\s+<<", stripped):
            heredoc = (next(x for x in opener.groups()[1:] if x), bool(opener[1]))
            continue
        if any(word.startswith('<<') for word in words):
            raise ValueError('unsupported plant heredoc; refusing cleanup and execution')
        match = re.fullmatch(r"(?:rm -rf (\S+) && )?cp -R \. (\S+)(?: && rm -rf (\S+))?", stripped)
        if match:
            removed, target, strip_git = match.groups()
            parts = target.split('/')
            if (not target.startswith('/tmp/') or len(parts) < 3 or
                    any(not re.fullmatch(r'[A-Za-z0-9_.-]+', part) or part in ('.', '..')
                        for part in parts[2:]) or removed not in (None, target) or
                    strip_git not in (None, target + '/.git')):
                raise ValueError('ambiguous plant copy path; refusing cleanup and execution')
            if target not in result:
                result.append(target)
        elif re.match(r'(?:rm\b.*&&\s*)?cp\s+-R\s+\.(?:\s|$)', stripped):
            raise ValueError('unsupported plant copy declaration; refusing cleanup and execution')
    if heredoc is not None or pending:
        raise ValueError('unterminated plant quoting/heredoc; refusing cleanup and execution')
    return result


def run_plant(script, bash, *, check_noop=True):
    """Sweep every declared copy even if execution or no-op observation raises."""
    copies = copy_dirs_of(script)
    primary = copy_dir_of(script)  # preserve the existing first-copy verdict contract
    sweep(copies)
    try:
        result = bash(script)
        noop = bool(check_noop and primary and os.path.isdir(primary)
                    and not differs_from_repo(primary))
        return primary, (result, noop)
    finally:
        sweep(copies)


def differs_from_repo(path):
    r = subprocess.run(
        ["diff", "-rq", "--exclude=.git", "--exclude=node_modules", "--exclude=graphify-out", path, ROOT],
        capture_output=True, text=True,
    )
    return bool(r.stdout.strip()) or bool(r.stderr.strip())


def sweep(paths):
    # Admit the complete set before deleting anything. /tmp itself may be the
    # platform alias; no descendant symlink or non-directory grants authority.
    paths = list(dict.fromkeys(p for p in paths if p))
    for path in paths:
        parts = path.split('/')
        if (not path.startswith('/tmp/') or
                any(not re.fullmatch(r'[A-Za-z0-9_.-]+', part) or part in ('.', '..')
                    for part in parts[2:])):
            raise ValueError('unsafe plant cleanup path')
        current = os.path.realpath('/tmp')
        for part in parts[2:]:
            current = os.path.join(current, part)
            try:
                info = os.lstat(current)
            except FileNotFoundError:
                break
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
                raise ValueError('plant cleanup requires owned directory components, no symlinks')
    failures = []
    for path in paths:
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass
        except OSError as exc:
            failures.append(exc)
    if failures:
        # Attempt independent copies too; never turn incomplete cleanup into PASS.
        raise OSError(f'plant cleanup failed for {len(failures)} path(s)') from failures[0]


def _main(argv, plants):
    # Parse before scanning, locking or copying. Unknown flags must not silently
    # trigger the entire destructive-fixture suite (observed with --help).
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("-k", metavar="PATTERN")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--shard", metavar="INDEX/TOTAL")
    parsed = parser.parse_args(argv[1:])
    only = parsed.k.lower() if parsed.k is not None else None
    listing = parsed.list
    _shard = None
    if parsed.shard is not None:
        try:
            _shard = parse_shard(parsed.shard)
        except ValueError as exc:
            print(f"FAIL: {exc}")
            return 2

    _all, _problems = scan(NEG_DIR)
    if _problems:
        print(f"FAIL: {len(_problems)} file(s) in {os.path.relpath(NEG_DIR, ROOT)}/ are not "
              "checks this runner can read — refusing to run a suite that would quietly "
              "be smaller than the directory:")
        for _p in _problems:
            print("  * " + _p)
        return 2
    # Parsed once; both filters read the same list. The floors below are about the
    # WHOLE directory: a shard is a slice of a corpus that must first be complete.
    _STEPS = [(n, s) for _f, n, s in _all]
    _FILE = {n: f for f, n, _s in _all}

    # Every step copies the repo to a FIXED `/tmp` name. In CI that is correct — each
    # shard of the `negatives` job is its own runner, no neighbours. On a developer machine two suite runs share those
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
    # The shared helper binds physical /tmp across owners and TMPDIR settings.
    # Old runner versions and direct plant invocation do not participate.
    try:
        _lock = plants.hold(acquire_scratch_lock())
    except (OSError, RuntimeError) as exc:
        print(f"FAIL: cannot acquire family scratch lock ({type(exc).__name__}): {exc}")
        return 1

    tests = [(n, s) for n, s in _STEPS if MARKER in n]
    if len(tests) < MIN_EXPECTED:
        print(f"FAIL: found only {len(tests)} negative self-tests in "
              f"{os.path.relpath(NEG_DIR, ROOT)}/ (expected at least {MIN_EXPECTED}). "
              f"Files went missing or the header format changed — a run that quietly "
              f"tests nothing is the failure this check exists to prevent.")
        return 2
    _n_props_all = sum(1 for n, _s in _STEPS if PROP_MARKER in n)
    if _shard:
        _STEPS = shard(_STEPS, *_shard)
        tests = [(n, s) for n, s in _STEPS if MARKER in n]
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
        _np = len([1 for n, _ in _STEPS if PROP_MARKER in n
                   and (not only or only.lower() in n.lower())])
        print(f"\n{len(tests)} negative self-tests + {_np} property checks"
              + (f" (shard {_shard[0]}/{_shard[1]})" if _shard else ""))
        return 0

    # A leftover copy from an interrupted run would make the next one lie.
    sweep([path for _, script in tests for path in copy_dirs_of(script)])

    # Every test does `cp -R .` — from the CURRENT WORKING DIRECTORY. Run with cwd=ROOT
    # that is the live tree, so editing a file mid-run hands some tests a half-written
    # copy and the suite reports on a state the repo was never in. It happened twice in
    # one session, and board row B-023 predicted both.
    #
    # So the suite copies ROOT once into a snapshot and runs every test with cwd there.
    # Editing while it runs is now harmless.
    _snap = tempfile.mkdtemp(prefix="tp-negatives-snap-")
    # An interrupted or refused run must not leave a repository copy behind.
    atexit.register(shutil.rmtree, _snap, True)
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
    # exits 0 — which is the failure property checks were added to close. Counted on
    # the whole directory, before the shard slice.
    if _n_props_all < MIN_PROPS:
        print(f"FAIL: found only {_n_props_all} property checks in "
              f"{os.path.relpath(NEG_DIR, ROOT)}/ (expected at least {MIN_PROPS}). A "
              f"category that quietly empties is a category nobody notices is gone.")
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
          + (f" + {len(props)} property checks" if props else "")
          + (f" — shard {_shard[0]}/{_shard[1]} of {len(_all)} checks" if _shard else "")
          + "\n")

    # `bash -e`, because that is what GitHub ran: a `run:` block with no `shell:` is
    # `bash -e {0}`. The runner used plain `bash -c` while CI was the authority, and
    # since v1.93.0 CI runs THIS file — a plant whose construction errors halfway must
    # still stop where CI's step stopped, not run on into a validator over a tree it
    # never planted.
    def _bash(script):
        return plants.run(["bash", "-e", "-c", script], cwd=_base)

    def _run_one(name_script):
        name, script = name_script
        # Retire copies inside the worker, including secondary plants and errors;
        # waiting for the whole pool retains every tree at once.
        plants.check_running()
        try:
            cdir, outcome = run_plant(script, _bash)
            return name, script, cdir, outcome
        except BaseException:
            plants.cancel()
            raise

    with concurrent.futures.ThreadPoolExecutor(max_workers=_WORKERS) as _ex:
        _results = list(_ex.map(_run_one, tests))
    for name, script, cdir, (r, noop) in _results:
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
        status = verdict(r.returncode, r.stdout, noop)
        bucket = {"BROKEN": broken, "SKIP": dormant, "FAIL": failed}.get(status)
        print(f"  {status:<7}{label(name)}")
        if bucket is not None:
            bucket.append((label(name) + f" [{_FILE[name]}]", r.stdout[-500:], r.stderr[-500:]))

    for name, script in props:
        cdir, (r, _noop) = run_plant(script, _bash, check_noop=False)
        # B-113, the half the first pass left: a property check that printed `SKIP:`
        # counted as one that "printed what it asserts". Same sentence, same defect,
        # one category over — found by the independent reader.
        _st = verdict(r.returncode, r.stdout, False)
        print(f"  {'PASS' if _st == 'PASS' else _st:<7}[property] " + _plabel(name))
        if _st == "SKIP":
            prop_dormant.append((_plabel(name), r.stdout[-500:], r.stderr[-500:]))
        elif _st != "PASS":
            prop_failed.append((_plabel(name) + f" [{_FILE[name]}]", r.stdout[-500:],
                                r.stderr[-500:]))

    print()
    for title, rows, why in (
        ("BROKEN — the planted defect changed nothing, so the test proves nothing", broken,
         "fix the corruption in its file under test/negatives/"),
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
    print("PASS: " + _line + (f" — shard {_shard[0]}/{_shard[1]}" if _shard else ""))
    return 0


def main(argv):
    try:
        with ScratchProcesses() as plants:
            result = _main(argv, plants)
            plants.check_running()
        plants.check_running()
        return result
    except (InterruptedError, OSError, RuntimeError) as exc:
        print(f"FAIL: plant lifecycle refused ({type(exc).__name__}): {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
