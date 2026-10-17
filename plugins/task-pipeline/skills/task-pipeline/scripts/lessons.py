#!/usr/bin/env python3
"""The local lesson index — every project's retro lessons, readable from any project.

A retro entry is written per project and read by that project's next stage 0. An agent on
another project never sees it, unless a wiki or a shared store happens to be installed. This
script is the floor every install has (`references/iteration.md` → *The learning loop*): a
retro entry that carries a `**Lesson:**` line is a lesson (`templates/lesson.schema.json`,
lesson/1), and the index projects every such entry from every project on this machine into
one file that stage 0 queries by the task's nouns.

**The retro stays canonical; the index is a projection.** It can be lost and rebuilt from
the retros (`rebuild`). An entry is a pure function of its origins, so a complete rebuild of
the same retros from the same checkouts, with nothing carried and no memory id recorded,
equals the incremental index byte for byte. Otherwise the rebuild also holds what only the
previous index knew: carried origins, their provenance and memory ids.

    lessons.py add --retro FILE (--entry ANCHOR ... | --all) [--root DIR]
    lessons.py add --json FILE|-                              [--root DIR]
        validate lesson/1 and merge it into the index; a second project's copy of one
        classKey makes it a candidate, a repeat from the same project revises, never mints
    lessons.py query NOUN ... [--limit 5]
        at most --limit lines: `[lesson L-<sha12>] title — trigger — check (seen N, projects K)`
    lessons.py rebuild --roots DIR ... [--depth 3] [--prune-carried [--prune-carried-reason R]]
        re-derive the index from every retro found under the roots and their git worktrees.
        A rebuild never removes or moves anything on its own: every previous origin it does
        not re-derive is carried forward, marked `carried: <reason>`, and named, keeping its
        memory id — except an origin v1.95.0 wrote (no provenance) that this run proves is the
        same repository under a new key (its commit resolves in that checkout, descends from the
        new key's root, and v1.95.0 would have keyed that checkout as the origin; its project is
        not read this run): it is re-keyed, its memory id kept. One memory id stays on one live
        project (the earlier holder), in rebuild and add; the other is named.
        `--prune-carried` (optionally one reason) is the only way an origin leaves the index; --prune-carried-reason needs --prune-carried and takes only a reason a
        rebuild produces. An origin whose every checkout now holds another project, without
        the origin's own commit, is kept but not counted. A shallow clone — or one whose
        shallow check does not answer — is never a source. Memory ids follow (project,
        classKey). Messages — stdout and stderr, in every verb but `path` — name checkouts and
        files, never an absolute path. Exit 1, touching nothing, only when nothing could be
        read: every root missing or unreadable; a readable empty root exits 0 and writes the
        index
    lessons.py candidates [--min-projects 2]
        lessons two or more projects hold: the `retro.publish` queue for learned.md
    lessons.py show L-<sha12>
        one entry, with its origins (pseudonymous project keys, commits, retro anchors)
    lessons.py emit-observatory L-<sha12> [--tool observatory_record|observatory_lesson] [--root DIR]
        the store's arguments for this project's origin, as JSON: `observatory_lesson` where the
        session lists it, else `observatory_record` (the default; memoryId and expectedRevision
        once recorded). The same pseudonymous project key, never a `project:<slug>` id; the
        commit as `commit:` + 12 hex. The agent calls the tool
    lessons.py record L-<sha12> --answer FILE|- [--ledger PATH] [--root DIR] [--replace]
        keep the store's memory id beside this project's origin; a refusal becomes one ledger
        line (`event: lessons — store refused — <code>`) and the local entry stays. Replacing a
        different id this origin holds needs --replace; an id another project's or class's
        origin holds is refused (exit 1) — unless that origin is carried as `checkout holds
        another project` from this very checkout (the re-attach after a re-init) — and one the
        index cannot hold (`mem:<id>@<rev>`, no
        quote, backslash or space) exits 2. add, emit-observatory and record refuse in a
        shallow clone: its project key is not stable until it is deepened
    lessons.py path
        the index this invocation would use

**Where the index lives.** `--index PATH`, else `$TASK_PIPELINE_LESSONS`, else
`~/.sshlg-skills/lessons/index.jsonl` when `~/.sshlg-skills` already exists — the family's
machine-state home, which hosts `lessons/` as task-pipeline's (sshlg-skills board row B-181;
its `docs/working-rules/state-json.md`, "Other members' files under ~/.sshlg-skills/",
ssheleg/sshlg-skills#209) — and `~/.task-pipeline/lessons/index.jsonl`
otherwise, so a standalone install never creates the family's directory. When the family's
directory appears later, the first run merges the standalone index into it once — copying
only lessons it lacks, the family copy winning on any lesson both hold, newer-format lines
carried verbatim — renames the old file `.migrated`, and says so.

**Every index operation runs under one lock** (`session`): the index directory's `.lock`
(`flock`; `$TASK_PIPELINE_LESSONS_LOCK_TIMEOUT` seconds, default 10), and on the default path
the standalone directory's `.lock` too, family first. Reads, writes, the merge, setting a
corrupt file aside: all under it. An index that does not parse — the family's or the
standalone one — is a derived file gone bad, never a reason to exit 1: it is kept as
`.corrupt-<date>[-n]` and the run goes on; `rebuild --roots` re-derives it. One that cannot be
READ is the one refusal, since its contents may be good. Directories this script creates are
0700 (an existing one keeps its mode), the file 0600, written by a unique temp file and
`os.replace`. git gets
`$TASK_PIPELINE_GIT_TIMEOUT` seconds (default 60), and a git that does not answer is its own
refusal, never read as a missing commit.

**What a lesson may carry.** The fields of lesson/1 and nothing else. The text fields are one
line each and refused when they carry an absolute or home path, a URL, an e-mail address, a
credential shape or a long hex/base64 run: what a pattern can see. A RELATIVE path, a short
SHA or a repository name in text no pattern can tell from an ordinary word — those stay the
writer's duty, with names. A person's or a customer's
name a pattern cannot see; that stays the writer's duty (`references/retrospective.md` →
*What may leave the project*). The project is a pseudonymous key — `p-` and 12 hex digits
of the repository's root commit, the first-parent root of its default branch (else the main
worktree's HEAD, then init.defaultBranch), shared by every worktree of it — never its name, and the evidence commit must resolve in
the repository it came from.

**The retro line it reads**, inside a `### ` entry of the retro or its archive:

    - **Lesson:** `<class-key>` — <the class, one sentence> · **When:** <trigger> · **Nouns:** a, b, c

with the entry's own `**Surfaced at:** stage N · **Owned by:** stage M`, `**Fix:** grade G`,
`**The check:**` and `**Commit:** `<sha>`` lines. An entry with no Lesson line is private to
its project and is skipped, counted aloud.

Exit codes: 0 done (an absent index on `query` is a state, printed; a `rebuild` that named
what it skipped or carried); 1 a refusal — a lesson that fails lesson/1 or whose commit does
not resolve on `add`, a held lock, an unknown id, a `rebuild` whose every root was missing or
unreadable, a `record` naming an id another class or another project holds, an older
revision or (without --replace) a different id, and add/emit/record in a shallow clone; 2 usage
(--prune-carried-reason without --prune-carried, or a reason a rebuild never produces), a
memory id the index cannot hold, or an unreadable input. Stdlib only
(`references/portability.md`).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import stat
import sys
import tempfile
import time
from datetime import datetime, timezone

OWNER = "agent:task-pipeline"
DEFAULT_LEDGER = ".task-pipeline/run.md"
ENV_INDEX = "TASK_PIPELINE_LESSONS"
ENV_LOCK = "TASK_PIPELINE_LESSONS_LOCK_TIMEOUT"
FIELDS = ("schema", "classKey", "title", "trigger", "check", "grade", "stages", "nouns", "origin")
TEXT_CAPS = {"title": (8, 160), "trigger": (3, 200), "check": (3, 200)}
CLASS_KEY = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PROJECT = re.compile(r"^p-[0-9a-f]{12}$")
COMMIT = re.compile(r"^[0-9a-f]{7,40}$")
RETRO_REF = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_./-]*\.md#[^\W_]+(?:-[^\W_]+)*$")
LESSON_ID = re.compile(r"^L-[0-9a-f]{12}$")
# What a pattern can see. Each one names what it refuses, so a refusal is a sentence.
FORBIDDEN = (
    (re.compile(r"(?:^|[\s\"'(`=:])(?:/[A-Za-z0-9._-]+){2,}"), "an absolute path"),
    (re.compile(r"(?:^|[\s\"'(`=:])~[A-Za-z0-9._-]*/"), "a home path"),
    (re.compile(r"(?:^|[\s\"'(`])[A-Za-z]:\\"), "a drive path"),
    (re.compile(r"[a-z][a-z0-9+.-]*://", re.I), "a URL"),
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "an e-mail address"),
    (re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"), "a credential shape (cloud access key)"),
    (re.compile(r"\b(?:sk|pk|rk)-[A-Za-z0-9_-]{16,}"), "a credential shape (API key)"),
    (re.compile(r"\b(?:ghp|gho|ghs|ghu|github_pat|xox[abpr]|glpat)[_-][A-Za-z0-9_-]{10,}"),
     "a credential shape (service token)"),
    (re.compile(r"-----BEGIN [A-Z ]+-----"), "a private key block"),
    (re.compile(r"\b[0-9a-f]{32,}\b", re.I), "a long hex run (a hash or a secret: commits go in origin)"),
    (re.compile(r"(?=[A-Za-z0-9+/_-]*[a-z])(?=[A-Za-z0-9+/_-]*[A-Z])(?=[A-Za-z0-9+/_-]*[0-9])"
                r"[A-Za-z0-9+/_-]{40,}={0,2}"), "a long base64 run"),
)
ENTRY_HEAD = re.compile(r"^###\s+(.+?)\s*$")
LESSON_LINE = re.compile(
    r"^\s*-\s+\*\*Lesson:\*\*\s*`([^`]+)`\s*[—-]\s*(.+?)\s*·\s*\*\*When:\*\*\s*(.+?)\s*·\s*\*\*Nouns:\*\*\s*(.+?)\s*$")
SURFACED = re.compile(r"\*\*Surfaced at:\*\*\s*stage\s+([^\s·,()]+)")
OWNED = re.compile(r"\*\*Owned by:\*\*\s*stage\s+([^\s·,()]+)")
GRADE = re.compile(r"\*\*Fix:\*\*\s*grade\s+([1-3])\b")
CHECK = re.compile(r"^\s*-\s+\*\*The check:\*\*\s*(.+)$")
COMMIT_LINE = re.compile(r"\*\*Commit:\*\*\s*`([0-9a-f]{7,40})`")
ARTIFACT_KNOWN = ("docs/evidence", "docs/superpowers")
ARTIFACT_REGISTERS = ("retro.md", "backlog.md", "verification.md", "specs", "plans", "briefs", "retro")
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next",
             "target", ".cache"}


class Refused(Exception):
    """A refusal the caller can act on: exit 1, one sentence, nothing written."""


# ---------------------------------------------------------------------------- paths


def index_path(given: str | None) -> pathlib.Path:
    if given:
        return pathlib.Path(given).expanduser()
    env = os.environ.get(ENV_INDEX)
    if env:
        return pathlib.Path(env).expanduser()
    # The family's machine-state directory when it exists — it hosts `lessons/` as
    # task-pipeline's (sshlg-skills B-181; state-json.md "Other members' files under
    # ~/.sshlg-skills/", #209) — otherwise task-pipeline's own, so a standalone install never
    # creates the family's directory.
    family = pathlib.Path.home() / ".sshlg-skills"
    if family.is_dir():
        return family / "lessons" / "index.jsonl"
    return LEGACY_INDEX()


def LEGACY_INDEX() -> pathlib.Path:
    return pathlib.Path.home() / ".task-pipeline" / "lessons" / "index.jsonl"


def _unique(path: pathlib.Path, suffix: str) -> pathlib.Path:
    dest = path.with_name(f"{path.name}.{suffix}")
    n = 1
    while dest.exists():
        n += 1
        dest = path.with_name(f"{path.name}.{suffix}-{n}")
    return dest


def set_aside(path: pathlib.Path) -> pathlib.Path:
    """Rename a corrupt index to `<name>.corrupt-<UTC date>[-N]` beside it. Called only under
    `session`'s lock, so no other run can have moved it first; an OSError is still a refusal
    that names the file, never a traceback."""
    dest = _unique(path, "corrupt-" + datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    try:
        os.replace(path, dest)
    except OSError as exc:
        raise Refused(f"the corrupt index {path} could not be set aside ({type(exc).__name__}) — "
                      "nothing was written; move it away by hand")
    return dest


def open_index(idx: pathlib.Path, notes: list[str]) -> dict[str, dict]:
    """The index's entries — the same corrupt handling for the family index and the standalone
    one: a file that does not parse is a DERIVED file gone bad, never a reason to exit 1. It is
    set aside whole as `.corrupt-<date>[-n]`; every line that still parses (memory ids and
    carried origins included) is salvaged into the live index at once, and the run goes on from
    that; `rebuild --roots` re-derives the rest. A file that cannot be READ (permissions) is the
    one refusal: its contents may be good, so nothing replaces it."""
    try:
        mine: list[str] = []
        out = load(idx, mine)
        notes += mine
        return out
    except IndexCorrupt:
        good, future, bad, only = _salvage(idx, notes)
        dest = set_aside(idx)
        notes.append(f"the index {idx} could not be parsed — kept whole as {dest.name}; "
                     f"{len(good)} lesson line{'' if len(good) == 1 else 's'} salvaged into the "
                     f"live index, {bad} bad line{'' if bad == 1 else 's'} left only in {dest.name}; "
                     "`lessons.py rebuild --roots <dir>` re-derives the rest from the retros")
        if only:
            notes.append(f"memory id{'' if len(only) == 1 else 's'} held only by a bad line, kept "
                         f"in {dest.name} and nowhere else: {', '.join(sorted(only))}")
        _CORRUPT_ONLY[str(idx)] = (dest.name, only)
        _FUTURE[str(idx)] = future
        if good or future:
            save(idx, good)  # under the session's lock: a read-only verb keeps the salvage too
        return good


def _merge_legacy(idx: pathlib.Path, notes: list[str]) -> None:
    """Bring the standalone index into the family's, ONCE. Runs under BOTH directories' locks.

    A merge never overwrites: only lessons the family index lacks are copied, the family copy
    wins on any lesson in both, and newer-format lines from either file are carried verbatim.
    The old file is then renamed `.migrated` — so the notice is printed once, by one run."""
    legacy = LEGACY_INDEX()
    if idx == legacy or not legacy.is_file():
        return
    try:
        old = load(legacy)
    except IndexCorrupt:
        dest = set_aside(legacy)
        notes.append(f"the old index {legacy} is corrupt — kept as {dest.name}, not merged; "
                     "`lessons.py rebuild --roots <dir>` re-derives the lessons from the retros")
        return
    except IndexUnreadable as exc:
        notes.append(f"{exc} — the old index was not merged")
        return
    old_future = list(_FUTURE.get(str(legacy), []))
    both = idx.exists()
    new = open_index(idx, notes) if both else {}
    # A family file that did not parse was set aside by open_index: only one file was read.
    set_aside_family = both and not idx.exists()
    both = both and not set_aside_family
    copied = [k for k in sorted(old) if k not in new]
    for k in copied:
        new[k] = old[k]
    future = list(_FUTURE.get(str(idx), [])) if both else []
    future += [ln for ln in old_future if ln not in future]
    _FUTURE[str(idx)] = future
    save(idx, new)
    dest = _unique(legacy, "migrated")
    try:
        os.replace(legacy, dest)
    except OSError as exc:
        raise Refused(f"merged the old index into {idx} but could not rename {legacy} "
                      f"({type(exc).__name__}) — remove it by hand so one index is read")
    what = ("both index files existed — read both: merged" if both else
            "the family index was corrupt and set aside, so only the local one was read: moved"
            if set_aside_family else "moved the local index from")
    kept = "" if set_aside_family else ", the family copy kept wherever both had one"
    notes.append(f"{what} {legacy} into {idx} — {len(copied)} of {len(old)} lessons copied"
                 f"{kept}; the old file is kept as {dest.name}")


class session:
    """Every index operation, under one lock. `with session(idx, default) as s:` takes the
    index directory's lock — and, on the default path, the standalone directory's too (family
    first, always in that order) — then merges the standalone index once, sets a corrupt index
    aside, and loads. `s.entries` is the index; `s.save()` writes it. Notes print on exit."""

    def __init__(self, idx: pathlib.Path, default: bool):
        self.idx, self.default = idx, default
        self.notes: list[str] = []
        self.locks: list[locked] = []
        self.entries: dict[str, dict] = {}

    def __enter__(self):
        dirs = [self.idx.parent]
        legacy = LEGACY_INDEX()
        if self.default and legacy != self.idx and legacy.parent.is_dir():
            dirs.append(legacy.parent)
        try:
            for d in dirs:
                lk = locked(d)
                lk.__enter__()
                self.locks.append(lk)
            if self.default:
                _merge_legacy(self.idx, self.notes)
            self.entries = open_index(self.idx, self.notes)
        except BaseException:
            self._release()
            raise
        return self

    def save(self) -> None:
        save(self.idx, self.entries)

    def _release(self) -> None:
        for lk in reversed(self.locks):
            lk.__exit__(None, None, None)
        self.locks = []
        for n in self.notes:
            print(f"lessons: {_say(n)}", file=sys.stderr)
        self.notes = []

    def __exit__(self, *exc):
        self._release()
        return False


def _git(root: pathlib.Path, *args: str) -> str | None:
    """git's answer, or None when git answered "no". A git that did not answer is NOT a
    "no": until round 2 a timeout returned None too, so on a loaded machine a lesson was
    refused as "no commit" or "does not resolve" — two of twelve verification runs failed
    that way. A timeout or a missing git is its own refusal now."""
    try:
        timeout = float(os.environ.get("TASK_PIPELINE_GIT_TIMEOUT", "60"))
    except ValueError:
        timeout = 60.0
    try:
        r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        raise Refused(f"git {args[0]} did not answer within {timeout:g}s — the machine is "
                      "busy, not the lesson wrong; nothing was written, retry")
    except OSError as exc:
        raise Refused(f"git cannot be run ({type(exc).__name__}) — a lesson needs its commit")
    return r.stdout.strip() if r.returncode == 0 else None


def repo_root(start: pathlib.Path) -> pathlib.Path:
    top = _git(start, "rev-parse", "--show-toplevel")
    if not top:
        raise Refused(f"{start} is not inside a git repository — a lesson carries its evidence "
                      "commit, and a commit needs a repository")
    _show(pathlib.Path(top))
    return pathlib.Path(top)


_KEYS: dict[str, str] = {}
# Absolute paths a message shows by name (round 12, E; round 13, O): `rebuild` fills it, and
# every line it prints — stdout, the session's notes, a refusal — goes through `_say`.
_SHOWN: dict[str, str] = {}


def _show(path: pathlib.Path, home_relative: bool = False) -> None:
    """Show `path` — as given and as resolved — by its name in every message (round 14, L3). An
    index file is shown home-relative (`~/.sshlg-skills/lessons/index.jsonl`) where it lies
    under the home directory, so the family's and the standalone index stay told apart."""
    try:
        real = path.resolve()
    except OSError:
        real = path
    name = real.name or path.name
    if home_relative:
        try:
            name = "~/" + real.relative_to(pathlib.Path.home().resolve()).as_posix()
        except (ValueError, RuntimeError, OSError):
            pass
    for form in {str(path), str(real), str(path.expanduser())}:
        if os.path.isabs(form) and name:
            _SHOWN[form] = name


def project_key(root: pathlib.Path) -> str:
    """`p-` + 12 hex of the repository's root commit: stable across clones, names nothing.

    The REPOSITORY's root, not the checked-out branch's (round 12): the first-parent root of the
    default branch — `origin/HEAD`, else `main`, else `master`; without any of them the MAIN
    worktree's HEAD, read in the common directory (round 13: one answer for every worktree, so a
    linked worktree on an orphan branch is not a second project), else `init.defaultBranch`,
    else this checkout's HEAD. A worktree on a branch that merged an unrelated history, or a
    checkout sitting on an orphan `gh-pages`, is still its repository's project. Computed once
    per `git rev-parse --git-common-dir`, so every worktree of one repository shares it."""
    common = _git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    key = common or str(root)
    if key in _KEYS:
        return _KEYS[key]
    refs: list[tuple[tuple[str, ...], str]] = []
    head = _git(root, "symbolic-ref", "-q", "refs/remotes/origin/HEAD")
    if head:
        refs.append(((), head))
    refs += [((), "refs/heads/main"), ((), "refs/heads/master")]
    if common:
        refs.append((("--git-dir", common), "HEAD"))  # the main worktree's HEAD
    default = _git(root, "config", "--get", "init.defaultBranch")
    if default:
        refs.append(((), "refs/heads/" + default))
    refs.append(((), "HEAD"))
    for extra, ref in refs:
        if _git(root, *extra, "rev-parse", "-q", "--verify", ref + "^{commit}") is None:
            continue
        roots = _git(root, *extra, "rev-list", "--max-parents=0", "--first-parent", ref)
        if roots:
            _KEYS[key] = "p-" + roots.split()[-1][:12]
            return _KEYS[key]
    raise Refused(f"the repository {root.name} has no commit — a project key needs one")


_RESOLVES: dict[tuple[str, str], bool] = {}


def commit_resolves(root: pathlib.Path, sha: str) -> bool:
    """Does `sha` name a commit in this checkout? Asked of git once per (checkout, sha) in a
    run (round 14, L2): a rebuild asks it for every carried origin in every checkout of its
    provenance, and 150 origins over 5 checkouts doubled the run. Only an answer is cached; a
    git that does not answer raises, uncached, every time."""
    key = (os.path.realpath(root), sha)
    if key not in _RESOLVES:
        _RESOLVES[key] = _git(root, "cat-file", "-e", f"{sha}^{{commit}}") is not None
    return _RESOLVES[key]


_LEGACY_KEYS: dict[str, str | None] = {}
_ROOTS: dict[tuple[str, str], frozenset] = {}


def _legacy_key(checkout: str) -> str | None:
    """The key v1.95.0 gave this checkout: `p-` + the SMALLEST root commit of HEAD (round 14,
    F1). None when git cannot say. Cached per checkout."""
    if checkout not in _LEGACY_KEYS:
        try:
            roots = _git(pathlib.Path(checkout), "rev-list", "--max-parents=0", "HEAD")
        except Refused:
            roots = None
        _LEGACY_KEYS[checkout] = "p-" + sorted(roots.split())[0][:12] if roots else None
    return _LEGACY_KEYS[checkout]


def _roots_of(checkout: str, sha: str) -> frozenset:
    """The 12-hex prefixes of the root commits `sha` descends from in this checkout; empty when
    git cannot say. Cached per (checkout, sha)."""
    key = (checkout, sha)
    if key not in _ROOTS:
        try:
            roots = _git(pathlib.Path(checkout), "rev-list", "--max-parents=0", sha)
        except Refused:
            roots = None
        _ROOTS[key] = frozenset(r[:12] for r in (roots or "").split())
    return _ROOTS[key]


def slug(text: str) -> str:
    """An entry's anchor: lowercase letters and digits of any script, every run of other
    characters one hyphen — a heading in Cyrillic keeps its words."""
    return re.sub(r"[\W_]+", "-", text.lower()).strip("-")


def lesson_id(class_key: str) -> str:
    return "L-" + hashlib.sha256(class_key.encode()).hexdigest()[:12]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------- lesson/1


def _check_text(name: str, value: object, lo: int, hi: int) -> list[str]:
    if not isinstance(value, str):
        return [f"{name} is not a string"]
    errs = []
    if not lo <= len(value) <= hi:
        errs.append(f"{name} is {len(value)} characters; lesson/1 allows {lo}-{hi}")
    # Every character str.splitlines() breaks on, not only \n and \r (round 12, B): a U+2028 in a
    # title once made every later read of the index call it corrupt.
    if value != "".join(value.splitlines()) or any(ch in value for ch in "\r\n"):
        errs.append(f"{name} carries a line break (\\n, \\r, U+2028, U+2029, U+0085 or "
                    "another separator) — one line each")
    for rx, what in FORBIDDEN:
        if rx.search(value):
            errs.append(f"{name} carries {what}")
    return errs


def validate(lesson: object) -> list[str]:
    """Every reason lesson/1 refuses this object, in one list (empty = valid)."""
    if not isinstance(lesson, dict):
        return ["a lesson is a JSON object"]
    errs = [f"unknown field {k!r} — lesson/1 carries {', '.join(FIELDS)} and nothing else"
            for k in lesson if k not in FIELDS]
    errs += [f"missing field {k!r}" for k in FIELDS if k not in lesson]
    if errs:
        return errs
    if lesson["schema"] != "lesson/1":
        errs.append("schema is not lesson/1")
    ck = lesson["classKey"]
    if not isinstance(ck, str) or not CLASS_KEY.match(ck) or len(ck) > 64:
        errs.append("classKey is not a slug (a-z, 0-9, single hyphens, at most 64)")
    for name, (lo, hi) in TEXT_CAPS.items():
        errs += _check_text(name, lesson[name], lo, hi)
    g = lesson["grade"]
    if not isinstance(g, int) or isinstance(g, bool) or not 1 <= g <= 3:
        errs.append("grade is not an integer 1-3")
    st = lesson["stages"]
    if (not isinstance(st, dict) or set(st) != {"owned", "surfaced"}
            or not all(isinstance(v, (int, str)) and not isinstance(v, bool) and str(v).strip()
                       for v in st.values())):
        errs.append("stages is not {owned, surfaced}")
    else:
        # A stage id that is a string gets the text fields' checks (round 13, P): one line, at
        # most 32 characters, no path, URL or credential shape.
        for k in ("owned", "surfaced"):
            if isinstance(st[k], str):
                errs += _check_text(f"stages.{k}", st[k], 1, 32)
    nouns = lesson["nouns"]
    if (not isinstance(nouns, list) or not 3 <= len(nouns) <= 8
            or len(set(map(str, nouns))) != len(nouns)):
        errs.append("nouns is not 3-8 distinct strings")
    else:
        for n in nouns:
            errs += _check_text("a noun", n, 2, 32)
    o = lesson["origin"]
    if not isinstance(o, dict) or set(o) != {"project", "commit", "retro"}:
        errs.append("origin is not {project, commit, retro}")
    else:
        if not isinstance(o["project"], str) or not PROJECT.match(o["project"]):
            errs.append("origin.project is not a pseudonymous key (p- and 12 hex)")
        if not isinstance(o["commit"], str) or not COMMIT.match(o["commit"]):
            errs.append("origin.commit is not a commit SHA")
        r = o["retro"]
        if (not isinstance(r, str) or not RETRO_REF.match(r) or len(r) > 200
                or ".." in r.split("#")[0].split("/")):
            errs.append("origin.retro is not a repository-relative retro file and #anchor")
    return errs


def complete(lesson: dict, root: pathlib.Path) -> dict:
    """Fill what the repository decides: the schema tag and the pseudonymous project key.

    The key is ALWAYS this repository's. A supplied key that is well-formed and different
    is refused, naming both: an add from one project claiming another's key would make one
    project look like two, and `projects ≥ 2` is what turns a lesson into a candidate.
    A malformed one is left for `validate` to name."""
    out = dict(lesson)
    out.setdefault("schema", "lesson/1")
    if isinstance(out.get("origin"), dict):
        o = dict(out["origin"])
        mine = project_key(root)
        given = o.get("project")
        if isinstance(given, str) and PROJECT.match(given) and given != mine:
            raise Refused(f"{out.get('classKey', '?')}: origin.project is {given}, but this "
                          f"repository's key is {mine} — a lesson is added from the project "
                          "that learned it; nothing was written")
        o.setdefault("project", mine)
        out["origin"] = o
    return out


# ---------------------------------------------------------------------------- retro parsing


def _relative(root: pathlib.Path, path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        raise Refused(f"{path} is outside the repository at {root}")


def parse_retro(path: pathlib.Path, root: pathlib.Path, project: str,
                refused: set[str] | None = None) -> tuple[list[dict], int, list[str]]:
    """Lessons from one retro file: (lessons, entries without a Lesson line, refusals).
    `refused`, when given, collects the `retro#anchor` of every Lesson entry refused here."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise Refused(f"{path} cannot be read ({type(exc).__name__})")
    rel = _relative(root, path)
    entries: list[tuple[str, list[str]]] = []
    for line in text.splitlines():
        h = ENTRY_HEAD.match(line)
        if h:
            entries.append((h.group(1), []))
        elif line.startswith("## ") or line.startswith("# "):
            entries.append(("", []))  # a section boundary ends the entry before it
        elif entries:
            entries[-1][1].append(line)
    lessons, private, problems = [], 0, []
    for head, body in entries:
        if not head:
            continue
        ln = next((LESSON_LINE.match(b) for b in body if LESSON_LINE.match(b)), None)
        if not ln:
            private += 1
            continue
        blob = "\n".join(body)
        check = None
        for i, b in enumerate(body):
            c = CHECK.match(b)
            if c:
                parts = [c.group(1).strip()]
                for cont in body[i + 1:]:  # a bullet wrapped onto indented lines
                    if cont.startswith("  ") and not cont.lstrip().startswith("- "):
                        parts.append(cont.strip())
                    else:
                        break
                check = " ".join(parts)
                break
        sur, own, gr, cm = (SURFACED.search(blob), OWNED.search(blob), GRADE.search(blob),
                            COMMIT_LINE.search(blob))
        anchor = slug(head)
        missing = [n for n, v in (("Surfaced at", sur), ("Owned by", own), ("Fix: grade", gr),
                                  ("The check", check), ("Commit", cm)) if not v]
        if missing:
            problems.append(f"{rel}#{anchor}: the Lesson line needs the entry's "
                            + ", ".join(missing))
            if refused is not None:
                refused.add(f"{rel}#{anchor}")
            continue

        def stage(v: str) -> int | str:
            return int(v) if v.isdigit() else v

        lessons.append({
            "schema": "lesson/1", "classKey": ln.group(1).strip(), "title": ln.group(2).strip(),
            "trigger": ln.group(3).strip(), "check": check, "grade": int(gr.group(1)),
            "stages": {"owned": stage(own.group(1)), "surfaced": stage(sur.group(1))},
            "nouns": [n.strip() for n in ln.group(4).split(",") if n.strip()],
            "origin": {"project": project, "commit": cm.group(1), "retro": f"{rel}#{anchor}"}})
    return lessons, private, problems


# ---------------------------------------------------------------------------- the index


def _origin_key(o: dict) -> tuple:
    return (o["project"], o["retro"])


def derive(origins: list[dict]) -> dict:
    """One index entry as a pure function of its origins (carried ones and their memory ids
    included) — so a complete rebuild with nothing carried equals the incremental index.

    `seen`, `projects` and `status` count re-derived origins and origins carried for a
    temporary unavailability; an origin carried as `checkout holds another project` is kept but
    NOT counted (round 11): a stranger at a path, or one checkout under a new root commit, never
    makes a phantom second project. Applied at load too, so these fields are never trusted from
    disk (round 11, #6)."""
    origins = sorted(origins, key=lambda o: (_origin_key(o), json.dumps(o, sort_keys=True)))
    first = origins[0]["lesson"]
    nouns = sorted({n for o in origins for n in o["lesson"]["nouns"]}, key=str.casefold)
    counted = [o for o in origins if o.get("carried") != CARRY_FOREIGN]
    projects = len({o["project"] for o in counted})
    return {"schema": "lesson-index/1", "id": lesson_id(first["classKey"]),
            "classKey": first["classKey"], "title": first["title"], "trigger": first["trigger"],
            "check": first["check"], "grade": min(o["lesson"]["grade"] for o in origins),
            "stages": first["stages"], "nouns": nouns, "seen": len(counted),
            "projects": projects, "status": "candidate" if projects >= 2 else "local",
            "origins": origins}


def _origin(lesson: dict, memory: str | None = None, checkouts: list[str] | None = None) -> dict:
    o = lesson["origin"]
    body = {k: lesson[k] for k in FIELDS if k not in ("schema", "origin")}
    rec = {"project": o["project"], "commit": o["commit"], "retro": o["retro"], "lesson": body}
    if memory:
        rec["memory"] = memory
    if checkouts:
        rec["checkouts"] = sorted(set(checkouts))
    return rec


def checkout_id(root: pathlib.Path) -> str:
    """A checkout's provenance: its real top-level path. Stays in the local index; never emitted."""
    return str(root.resolve())


def merge(entries: dict[str, dict], lessons: list[dict], checkout: str | None = None) -> int:
    """Merge lessons into {classKey: entry}; returns how many origins changed. `checkout` is the
    checkout the lessons were read from: an origin's provenance is the union of the checkouts
    that held it (round 9) — the only checkouts that may later show it is gone."""
    changed = 0
    for le in lessons:
        ck = le["classKey"]
        origins = list(entries[ck]["origins"]) if ck in entries else []
        key = (le["origin"]["project"], le["origin"]["retro"])
        old = next((o for o in origins if _origin_key(o) == key), None)
        prov = list((old or {}).get("checkouts") or []) + ([checkout] if checkout else [])
        new = _origin(le, old.get("memory") if old else None, prov)
        if old == new:
            continue
        origins = [o for o in origins if _origin_key(o) != key] + [new]
        entries[ck] = derive(origins)
        changed += 1
    return changed


class IndexUnreadable(Refused):
    """The file is there and cannot be READ (permissions, I/O). Its contents may be perfectly
    good — memory ids included — so nothing ever replaces it: refuse, name it, write nothing."""


class IndexCorrupt(Refused):
    """The file was read and does not parse as lesson-index/1. Only this one may be replaced,
    and only after it is kept beside as `.corrupt-<date>`."""


# Lines in a NEWER format, per index path: skipped on read, counted, and written back on save,
# so an older script never destroys what a newer one wrote.
_FUTURE: dict[str, list[str]] = {}
# Per index path: the `.corrupt-<date>` file name and the memory ids only its bad lines held.
_CORRUPT_ONLY: dict[str, tuple[str, set[str]]] = {}


ENTRY_TEXT = ("id", "title", "trigger", "check")
LESSON_KEYS = tuple(k for k in FIELDS if k not in ("schema", "origin"))
MEM_RE = re.compile(r"mem:[^@\s\"\\]+@[1-9][0-9]*")  # revisions start at 1 (round 11, #5)


def mem_base(memory: str) -> str:
    """A memory id without its revision: `mem:x@3` → `mem:x`. Ids compare on this (round 9, L3)."""
    return memory.rsplit("@", 1)[0]


def mem_rev(memory: str) -> int:
    try:
        return int(memory.rsplit("@", 1)[1])
    except (IndexError, ValueError):
        return 0


def _entry_shape(e: object) -> bool:
    """A lesson-index/1 line every verb can use (rounds 8–11, L1/L2/H2): the entry's own fields
    with their types — class key, id, title, trigger, check, nouns (strings), seen, projects —
    and a non-empty list of origins, each with its project, retro, commit and a lesson that
    lesson/1 itself accepts (`validate`, with that origin), of the entry's class. Optional
    fields keep their types: memory `mem:<id>@<rev>` with rev from 1, checkouts non-empty
    strings, carried one of CARRY_REASONS. Anything less is a corrupt line — set aside, its good
    neighbours salvaged — never a TypeError in the middle of a verb. Derived fields (seen,
    projects, status, id…) are recomputed by `_put` anyway."""
    if not isinstance(e, dict) or not isinstance(e.get("classKey"), str):
        return False
    if not all(isinstance(e.get(k), str) for k in ENTRY_TEXT):
        return False
    if not isinstance(e.get("nouns"), list) or not all(isinstance(n, str) for n in e["nouns"]):
        return False
    if not all(isinstance(e.get(k), int) and not isinstance(e.get(k), bool) for k in ("seen", "projects")):
        return False
    origins = e.get("origins")
    if not isinstance(origins, list) or not origins:
        return False
    for o in origins:
        if not (isinstance(o, dict) and all(isinstance(o.get(k), str) for k in ("project", "retro", "commit"))
                and isinstance(o.get("lesson"), dict) and all(k in o["lesson"] for k in LESSON_KEYS)):
            return False
        body = {k: o["lesson"][k] for k in LESSON_KEYS}
        whole = dict(body, schema="lesson/1",
                     origin={"project": o["project"], "commit": o["commit"], "retro": o["retro"]})
        if validate(whole) or body["classKey"] != e["classKey"]:
            return False
        if "memory" in o and not (isinstance(o["memory"], str) and MEM_RE.fullmatch(o["memory"])):
            return False
        if "checkouts" in o and not (isinstance(o["checkouts"], list)
                                     and all(isinstance(c, str) and c for c in o["checkouts"])):
            return False
        if "carried" in o and o["carried"] not in CARRY_REASONS:
            return False
    return True


def _stage_id(v: object) -> object:
    """A stage id lesson/1 accepts today, from one v1.95.0 accepted (round 14, L5): a string
    that fails the text checks (longer than 32 characters, a line break, a path or credential
    shape) is folded to one line and cut to 32 characters, and one that still fails becomes
    `stage`. Anything else is returned as it is, for the shape check to judge."""
    if not isinstance(v, str) or not v.strip() or not _check_text("s", v, 1, 32):
        return v
    folded = " ".join(" ".join(v.splitlines()).split())[:32].strip()
    return folded if folded and not _check_text("s", folded, 1, 32) else "stage"


def _migrate_stages(e: object, notes: list[str] | None) -> None:
    """Normalise, in place, the stage ids of an index line written before lesson/1 checked them
    (`_stage_id`), and say so — so the line is read, never set aside as corrupt, and no memory
    id it holds is lost. The next write stores the normalised ids."""
    if not isinstance(e, dict):
        return
    holders = [e] + [o["lesson"] for o in e.get("origins") or []
                     if isinstance(o, dict) and isinstance(o.get("lesson"), dict)]
    changed = False
    for h in holders:
        st = h.get("stages")
        if isinstance(st, dict):
            for k in ("owned", "surfaced"):
                if k in st and _stage_id(st[k]) != st[k]:
                    st[k] = _stage_id(st[k])
                    changed = True
    if changed and notes is not None:
        notes.append(f"{e.get('classKey', '?')}: a stage id written before lesson/1 checked stage "
                     "ids was normalised (one line, at most 32 characters)")


def _put(out: dict[str, dict], e: dict, notes: list[str] | None) -> None:
    """Every line read is normalised: one origin per (project, retro) — the one with the higher
    memory revision winning (on a tie the lexically smaller id), its provenance the union of both copies' (round 10, G5) — and the
    entry re-derived from its origins, so `seen`, `projects`, `status` and the rest are never
    trusted from disk (round 11, #6). Two lines for one class key (a hand-concatenated index)
    merge their origins, never last-one-wins (round 9, L4/D3), and that is said aloud — naming
    every memory id the merge dropped (round 12: one origin holds one id)."""
    ck = e["classKey"]
    twice = ck in out
    by_key: dict[tuple, dict] = {}
    dropped: list[str] = []
    for o in (out[ck]["origins"] if twice else []) + e["origins"]:
        k = _origin_key(o)
        if k in by_key:
            # The higher revision wins; on equal revisions the lexically smaller id, then the
            # smaller line — never the order the lines happen to be in (round 13, Q).
            keep, other = sorted((o, by_key[k]), key=lambda x: (
                -mem_rev(x.get("memory") or ""), x.get("memory") or "", json.dumps(x, sort_keys=True)))
            if other.get("memory") and mem_base(other["memory"]) != mem_base(keep.get("memory") or ""):
                dropped.append(other["memory"])
            prov = sorted(set(keep.get("checkouts") or []) | set(other.get("checkouts") or []))
            o = dict(keep, **({"checkouts": prov} if prov else {}))
        by_key[k] = o
    out[ck] = derive(list(by_key.values()))
    if notes is not None and (twice or dropped):
        lost = f"dropped {', '.join(dropped)}" if dropped else "none dropped"
        notes.append(f"{'two lines' if twice else 'one line'} for {ck} merged — {len(by_key)} origin"
                     f"{'' if len(by_key) == 1 else 's'} kept, {lost}")


def _salvage(path: pathlib.Path, notes: list[str] | None = None
             ) -> tuple[dict[str, dict], list[str], int, set[str]]:
    """The lines of a corrupt index that still parse: (entries, newer-format lines, bad lines,
    memory ids seen only in bad lines). A corrupt index is set aside whole; what parses is
    carried into the live index, so one bad line never costs every memory id and carried origin
    beside it (round 8, L2), and an id only a bad line held is named (round 9, D2)."""
    out, future, bad, bad_mems = {}, [], 0, set()
    try:
        raw = path.read_bytes()
    except OSError:
        return out, future, 0, bad_mems
    for chunk in raw.split(b"\n"):  # "\n" only, as `dump` writes (round 12, B)
        if not chunk.strip():
            continue
        try:
            line = chunk.decode("utf-8")
            e = json.loads(line)
        except (UnicodeDecodeError, ValueError):
            bad += 1
            bad_mems |= set(MEM_RE.findall(chunk.decode("utf-8", "replace")))
            continue
        if isinstance(e, dict) and e.get("schema", "lesson-index/1") != "lesson-index/1":
            future.append(line)
            continue
        _migrate_stages(e, notes)
        if _entry_shape(e):
            _put(out, e, notes)
        else:
            bad += 1
            bad_mems |= set(MEM_RE.findall(line))
    held = {o["memory"] for e in out.values() for o in e["origins"] if o.get("memory")}
    return out, future, bad, {m for m in bad_mems
                              if mem_base(m) not in {mem_base(h) for h in held}}


def load(path: pathlib.Path, notes: list[str] | None = None) -> dict[str, dict]:
    if not path.exists():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        if isinstance(exc, UnicodeDecodeError):
            raise IndexCorrupt(f"the index {path} is not UTF-8 text — `lessons.py rebuild` "
                               "keeps it as .corrupt-<date> and re-derives it")
        raise IndexUnreadable(f"the index {path} cannot be read ({type(exc).__name__}) — fix "
                              "its permissions; nothing was written")
    out, future = {}, []
    # One index line per "\n", exactly as `dump` writes it — never str.splitlines(), which also
    # breaks on U+2028/U+2029/U+0085 inside a JSON string written with ensure_ascii=False and
    # made every later read call a good index corrupt (round 12, B).
    for i, line in enumerate(text.split("\n"), 1):
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except ValueError:
            raise IndexCorrupt(f"the index {path} does not parse (line {i}) — `lessons.py "
                               "rebuild` keeps it as .corrupt-<date> and re-derives it")
        if isinstance(e, dict) and e.get("schema", "lesson-index/1") != "lesson-index/1":
            future.append(line)
            continue
        _migrate_stages(e, notes)
        if not _entry_shape(e):
            raise IndexCorrupt(f"the index {path} has a line that is not a lesson (line {i}) — "
                               "`lessons.py rebuild` keeps it as .corrupt-<date> and re-derives it")
        _put(out, e, notes)
    _FUTURE[str(path)] = future
    if future:
        print(_say(f"lessons: {len(future)} line{'' if len(future) == 1 else 's'} in a newer format "
                   f"skipped in {path} (kept on write; a newer lessons.py reads them)"), file=sys.stderr)
    return out


def dump(entries: dict[str, dict], future: list[str] | None = None) -> str:
    return ("".join(json.dumps(entries[k], ensure_ascii=False, sort_keys=True) + "\n"
                    for k in sorted(entries))
            + "".join(line + "\n" for line in (future or [])))


class locked:
    """An exclusive lock on an index DIRECTORY (`<dir>/.lock`), around every operation on any
    file in it — the index, its `.migrated` and `.corrupt-*` copies (graph.py's `held`, with a
    timeout: a writer that cannot get the lock refuses rather than waiting forever)."""

    def __init__(self, directory: pathlib.Path):
        self.lock = directory / ".lock"
        self.fh = None

    def __enter__(self):
        _ensure_dir(self.lock.parent)
        try:
            import fcntl
        except ImportError:
            print("note: no file locking on this platform — a concurrent write could lose a "
                  "lesson", file=sys.stderr)
            return self
        try:
            timeout = float(os.environ.get(ENV_LOCK, "10"))
        except ValueError:
            timeout = 10.0
        try:
            fd = os.open(self.lock, os.O_RDWR | os.O_CREAT, 0o600)
        except OSError as exc:
            raise Refused(f"the index lock {self.lock} cannot be opened ({type(exc).__name__}) "
                          "— nothing was written")
        self.fh = os.fdopen(fd, "a+")
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(self.fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except OSError:
                if time.monotonic() >= deadline:
                    self.fh.close()
                    self.fh = None
                    raise Refused(f"the index is locked by another writer ({self.lock}) after "
                                  f"{timeout:g}s — nothing was written; retry")
                time.sleep(0.05)

    def __exit__(self, *exc):
        if self.fh:
            self.fh.close()
        return False


def _ensure_dir(d: pathlib.Path) -> None:
    """Create the index directory 0700 — only the levels this script creates. A directory
    that already exists keeps its mode: it may be shared, and it is not ours to tighten."""
    missing = []
    cur = d
    while not cur.exists():
        missing.append(cur)
        cur = cur.parent
    try:
        for m in reversed(missing):
            try:
                m.mkdir(mode=0o700)
            except FileExistsError:
                # Another first writer made it between our look and our mkdir: theirs,
                # used as it is. Until round 2 this race was a refusal.
                continue
            os.chmod(m, 0o700)
    except OSError as exc:
        raise Refused(f"the index directory {d} cannot be created ({type(exc).__name__}) — "
                      "nothing was written")


def save(path: pathlib.Path, entries: dict[str, dict]) -> None:
    _ensure_dir(path.parent)
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".index-", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(dump(entries, _FUTURE.get(str(path))))
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException as exc:
        if tmp is not None:
            try:
                os.unlink(tmp)
            except OSError:
                pass
        if isinstance(exc, OSError):
            raise Refused(f"the index {path} cannot be written ({type(exc).__name__}) — "
                          "the previous index is intact")
        raise


def _resolve(entries: dict[str, dict], lid: str) -> dict:
    if not LESSON_ID.match(lid):
        raise Refused(f"{lid!r} is not a lesson id (L- and 12 hex)")
    for e in entries.values():
        if e["id"] == lid:
            return e
    raise Refused(f"no lesson {lid} in the index")


# ---------------------------------------------------------------------------- verbs


def refuse_shallow(root: pathlib.Path) -> None:
    """A shallow clone's project key — its root commit — moves whenever its boundary moves, so
    add, emit and record refuse there (round 11): nothing written, the store never sees a key
    that will not last."""
    if _git(root, "rev-parse", "--is-shallow-repository") == "true":
        raise Refused(f"{root.name} is a shallow clone: its project key changes when it is "
                      "deepened — deepen it first (git fetch --unshallow); nothing was written")


def cmd_add(a, idx: pathlib.Path) -> int:
    root = repo_root(pathlib.Path(a.root or "."))
    refuse_shallow(root)
    project = project_key(root)
    private, problems = 0, []
    if a.json is not None:
        try:
            raw = _stdin_utf8() if a.json == "-" else pathlib.Path(a.json).read_text(encoding="utf-8")
            data = json.loads(raw)
        except (OSError, ValueError) as exc:
            print(f"lessons: the lesson JSON cannot be read ({type(exc).__name__})", file=sys.stderr)
            return 2
        lessons = [complete(x, root) for x in (data if isinstance(data, list) else [data])]
    else:
        retro = pathlib.Path(a.retro)
        if not retro.is_absolute():
            retro = pathlib.Path(a.root or ".").resolve() / retro
        found, private, problems = parse_retro(retro, root, project)
        if a.all:
            lessons = found
        else:
            want = {slug(e) for e in a.entry}
            lessons = [x for x in found if x["origin"]["retro"].split("#", 1)[1] in want]
            missing = want - {x["origin"]["retro"].split("#", 1)[1] for x in found}
            if missing:
                raise Refused("no Lesson-bearing entry " + ", ".join(sorted(missing))
                              + f" in {retro.name} — the anchor is the heading's slug")
    errors = []
    for le in lessons:
        errs = validate(le)
        if not errs and not commit_resolves(root, le["origin"]["commit"]):
            errs = [f"origin.commit {le['origin']['commit']} does not resolve in this repository"]
        errors += [f"{le.get('classKey', '?')}: {e}" for e in errs]
    errors += problems
    if errors:
        raise Refused("refused, nothing written:\n  " + "\n  ".join(errors))
    with session(idx, a.default_index) as ss:
        entries = ss.entries
        before = json.loads(json.dumps(entries))  # the index as read: who held each id first
        changed = merge(entries, lessons, checkout_id(root))
        # The same FOREIGN rule at add time (round 12, repro G): an origin of another project key
        # that came from THIS checkout, whose commit no longer resolves here, is this checkout's
        # old identity (a re-init) — kept, marked, not counted, so add never adds a phantom.
        here = checkout_id(root)
        rekeyed: list[str] = []
        # The same live-project rule as rebuild (round 15): never re-key an origin into this
        # project when its key is a project the index already records with provenance.
        known = _known_projects(before)
        for ck in sorted({le["classKey"] for le in lessons}):
            origins = entries[ck]["origins"]
            marked = [dict(o, carried=CARRY_FOREIGN)
                      if o["project"] != project and here in (o.get("checkouts") or [])
                      and not o.get("carried") and not commit_resolves(root, o["commit"]) else o
                      for o in origins]
            # An origin v1.95.0 wrote for this repository — no provenance, keyed on the smallest
            # root — whose commit resolves here is this checkout's origin under its old key
            # (round 13, K): it takes this key and gives its memory id to the origin just added.
            fresh = [o for o in marked if here in (o.get("checkouts") or []) and o["project"] == project]
            for o in list(marked):
                n = None if o["project"] in known else _legacy_twin(o, fresh)
                if n is None or (o.get("memory") and n.get("memory")
                                 and mem_base(o["memory"]) != mem_base(n["memory"])):
                    continue
                memory = _newer_memory(o.get("memory"), n.get("memory"))
                marked = [dict(x, **({"memory": memory} if memory else {}))
                          if _origin_key(x) == _origin_key(n) else x for x in marked if x is not o]
                rekeyed.append(f"{ck} — {o['retro']}: {o['project']} is {project} (written before "
                               "provenance; its commit resolves here)" + (f" · {memory}" if memory else ""))
            if marked != origins:
                entries[ck] = derive(marked)
                changed += 1
        # One memory id stays on one live project at add time too (round 14, F3): an add from
        # an old clone that brings a carried holder back to life must not leave its id on both.
        shared = _one_project_per_memory(entries, before)
        changed += len(shared)
        if changed:
            ss.save()
    n = len(lessons)
    note = (f" · {private} entr{'y carries' if private == 1 else 'ies carry'} no Lesson line "
            "(project-private)") if private else ""
    print(f"lessons: {n} lesson{'' if n == 1 else 's'} · {changed} changed{note}")
    for le in lessons:
        e = entries[le["classKey"]]
        print(f"  {e['id']} {e['classKey']} — {e['status']} (seen {e['seen']}, projects {e['projects']})")
    for n in rekeyed:
        print(f"  re-keyed: {n}")
    for n in shared:
        print(f"  memory: {n}")
    return 0


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"\w+", text.casefold()) if len(w) > 2}


def _hit(q: str, words: set[str]) -> bool:
    # A cheap stem: Russian and English word forms share their first five letters often
    # enough for a noun query; anything finer is a search engine this file will not be.
    return q in words or (len(q) >= 5 and any(len(w) >= 5 and w[:5] == q[:5] for w in words))


def cmd_query(a, idx: pathlib.Path) -> int:
    with session(idx, a.default_index) as ss:
        entries = ss.entries
    if not entries and not idx.exists():
        print(_say(f"lessons: local index absent ({idx}) — nothing to read; the retro and "
                   "learned.md still run"))
        return 0
    query = [part.strip().casefold() for arg in a.nouns for part in arg.split(",") if part.strip()]
    qwords = set(query) | {w for q in query for w in _words(q)}
    scored = []
    for e in entries.values():
        nouns = {n.casefold() for n in e["nouns"]}
        nwords = {w for n in nouns for w in _words(n)} | nouns
        text = _words(" ".join((e["title"], e["trigger"], e["check"])))
        score = 3 * sum(1 for q in qwords if _hit(q, nwords)) + sum(1 for q in qwords if _hit(q, text))
        if score:
            scored.append((-score, -e["projects"], -e["seen"], e["id"], e))
    scored.sort(key=lambda t: t[:4])
    limit = max(1, min(a.limit, 10))
    for *_, e in scored[:limit]:
        print(f"[lesson {e['id']}] {e['title']} — {e['trigger']} — {e['check']} "
              f"(seen {e['seen']}, projects {e['projects']})")
    print(f"lessons: {min(len(scored), limit)} of {len(scored)} match · {len(entries)} in the local index")
    return 0


def _source_stat(path: pathlib.Path):
    """Optional absent source, but never hide a dangling link or an unreadable parent.

    Path.exists/is_file suppress different errors across Python versions. lstat names
    the directory entry; stat follows a present link and must succeed. Ancestor admission
    distinguishes a truly missing default tree from a broken link higher in that tree.
    """
    try:
        info = path.lstat()
    except FileNotFoundError:
        if path.parent != path:
            parent = _source_stat(path.parent)
            if parent is not None and not stat.S_ISDIR(parent.st_mode):
                raise Refused(f"{path.parent}: source parent is not a directory")
        return None
    if stat.S_ISLNK(info.st_mode):
        try:
            return path.stat()
        except OSError as exc:
            raise Refused(f"{path}: source link cannot be read ({type(exc).__name__})")
    return info


Problem = tuple  # (owner checkout path or None, text)


def find_retros(roots: list[str], depth: int) -> tuple[list[tuple[pathlib.Path, pathlib.Path]], list[Problem],
                                                        dict[pathlib.Path, bool]]:
    """Discovery and its unknowns, kept separate from a readable empty scope.

    Returns (retro files, problems, checkouts). Each checkout discovered — keyed by its real
    path — maps to whether its retro sources were discovered in full. Each problem carries its
    OWNER: the checkout it belongs to, or None when no checkout owns it (an unreadable
    directory, a missing root). Ownership is structural, never a path-prefix match (round 9).

    Every git worktree of a checkout found is discovered too (`git worktree list --porcelain`,
    round 8): the walk skips dot-directories, and `.worktrees/` or `.claude/worktrees/` is where
    a feature branch's retro usually lives. A listing git refuses — a non-zero exit or no answer —
    is a problem owned by that checkout (round 9, L1)."""
    found: list[tuple[pathlib.Path, pathlib.Path]] = []
    problems: list[Problem] = []
    repos: dict[pathlib.Path, bool] = {}

    def unread(exc):
        problems.append((None, f"{pathlib.Path(exc.filename or '?').name}: cannot discover "
                               f"({type(exc).__name__})"))

    def visit(here: pathlib.Path) -> None:
        try:
            here = here.resolve()
        except OSError:
            pass
        if here in repos:
            return
        repos[here] = False
        try:
            art = _artifact_root(here)
            archive = art / "retro"
            archive_info = _source_stat(archive)
            if archive_info is not None and not stat.S_ISDIR(archive_info.st_mode):
                raise Refused(f"{archive}: retro archive is not a directory")
            archived = sorted(archive.iterdir()) if archive_info is not None else []
            files = [art / "retro.md"] + [p for p in archived if p.suffix == ".md"]
            for f in files:
                info = _source_stat(f)
                if info is None:
                    continue
                if not stat.S_ISREG(info.st_mode):
                    raise Refused(f"{f}: retro source is not a regular file")
                found.append((here, f))
            repos[here] = True
        except (OSError, Refused) as exc:
            problems.append((here, f"{here.name}: {exc}"))

    for r in roots:
        base = pathlib.Path(r).expanduser()
        try:
            base_info = _source_stat(base)
            if base_info is None or not stat.S_ISDIR(base_info.st_mode):
                raise Refused(f"{base}: root is missing or not a readable directory")
        except (OSError, Refused) as exc:
            problems.append((None, str(exc)))
            continue
        for cur, dirs, _files in os.walk(base, followlinks=True, onerror=unread):
            here = pathlib.Path(cur)
            rel_depth = len(here.relative_to(base).parts)
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
            try:
                is_repo = _source_stat(here / ".git") is not None
            except (OSError, Refused) as exc:
                problems.append((None, f"{here}: {exc}"))
                is_repo = False
            if is_repo:
                visit(here)
            if rel_depth >= depth:
                dirs[:] = []
    for repo in list(repos):
        for wt in _worktrees(repo, problems):
            visit(wt)
    return found, problems, repos


def _worktrees(repo: pathlib.Path, problems: list[Problem]) -> list[pathlib.Path]:
    """The live worktrees git lists for `repo` (bare and prunable ones skipped). A listing that
    cannot be read is a problem owned by `repo`: its siblings are unknown."""
    try:
        listing = _git(repo, "worktree", "list", "--porcelain")
    except Refused as exc:
        listing, why = None, str(exc)
    else:
        why = "git exited non-zero"
    if listing is None:
        problems.append((repo, f"{repo.name}: worktrees cannot be listed ({why})"))
        return []
    out = []
    for block in listing.split("\n\n"):
        lines = block.splitlines()
        head = next((ln[len("worktree "):] for ln in lines if ln.startswith("worktree ")), None)
        if head is None or any(ln == "bare" or ln.startswith("prunable") for ln in lines):
            continue
        path = pathlib.Path(head)
        if path.is_dir():
            out.append(path)
    return out


def _artifact_root(repo: pathlib.Path) -> pathlib.Path:
    """`paths.artifacts` in pipeline.json, else the first known root carrying a register."""
    try:
        config = repo / "pipeline.json"
        info = _source_stat(config)
        if info is not None and not stat.S_ISREG(info.st_mode):
            raise Refused("pipeline.json is not a regular file")
        conf = json.loads(config.read_text(encoding="utf-8")) if info is not None else {}
    except (OSError, ValueError) as exc:
        raise Refused(f"pipeline.json cannot be read ({type(exc).__name__})")
    if not isinstance(conf, dict) or not isinstance(conf.get("paths", {}), dict):
        raise Refused("pipeline.json must contain an object with an object paths field")
    given = conf.get("paths", {}).get("artifacts")
    if given is not None:
        if not isinstance(given, str) or not given or pathlib.Path(given).is_absolute() or ".." in pathlib.Path(given).parts:
            raise Refused("pipeline.json paths.artifacts is not a repository-relative directory")
        art = repo / given
        info = _source_stat(art)
        if info is None or not stat.S_ISDIR(info.st_mode):
            raise Refused(f"{art}: configured artifacts directory is missing or not a directory")
        return art
    # The same rule, names and registers as bin/lib/artifact-root.js and test/artifact_root.py:
    # the first KNOWN name that exists AND carries one of the REGISTERS, else the default.
    for name in ARTIFACT_KNOWN:
        art = repo / name
        info = _source_stat(art)
        if info is not None and not stat.S_ISDIR(info.st_mode):
            raise Refused(f"{art}: default artifacts path is not a directory")
        if any(_source_stat(art / reg) is not None for reg in ARTIFACT_REGISTERS):
            return art
    return repo / ARTIFACT_KNOWN[0]


CARRY_CHECKOUT = "checkout not read"
CARRY_FILE = "retro file not read"
CARRY_LEGACY = "no provenance"
CARRY_FOREIGN = "checkout holds another project"
CARRY_UNRESOLVED = "commit does not resolve"
CARRY_CITES_UNRESOLVED = "retro cites a commit that does not resolve"
CARRY_REFUSED = "lesson refused"
CARRY_GONE = "no checkout read holds it"
CARRY_SOURCE = "source not read"  # the round-7 label, still accepted in an index line
CARRY_REASONS = (CARRY_CHECKOUT, CARRY_FILE, CARRY_LEGACY, CARRY_FOREIGN, CARRY_UNRESOLVED,
                 CARRY_CITES_UNRESOLVED, CARRY_REFUSED, CARRY_GONE, CARRY_SOURCE)
# The reasons `_carry_reason` can produce today — the only ones --prune-carried-reason offers.
PRUNE_REASONS = tuple(r for r in CARRY_REASONS if r != CARRY_SOURCE)


def _redact(text: str, shown: dict[str, str]) -> str:
    """`text` with every known absolute path replaced by its name, longest path first, so a
    checkout inside a root is shown as itself and never as the root plus a tail. Only absolute
    paths with a real name are replaced, and only as whole path components (round 13, N2): a
    root given as `.` once deleted every dot of every message (`repo.v2`, `mem:v1.2.3`)."""
    for path in sorted(shown, key=len, reverse=True):
        name = shown[path]
        if not os.path.isabs(path) or path == "/" or name in ("", ".", ".."):
            continue
        text = re.sub(r"(?<![\w.~/-])" + re.escape(path) + r"(?![\w.~-])", lambda _m: name, text)
    return text


def _say(text: str) -> str:
    """A message as printed: every path `rebuild` knows shown by its name (`_SHOWN`)."""
    return _redact(text, _SHOWN)


def _legacy_twin(o: dict, candidates: list[dict]) -> dict | None:
    """The re-derived origin a provenance-less origin is, or None (round 13, K).

    v1.95.0 keyed a project on the SMALLEST root commit of HEAD and recorded no checkouts; a
    repository that merged an unrelated history whose root sorts lower is keyed differently
    now. Such an origin is the same repository's — re-keyed, never counted twice — only on
    positive evidence: it has no `checkouts`, exactly one candidate of another key holds the
    same `retro#anchor` under the same class key, and in a checkout that candidate was derived
    from (round 14, F1) the origin's own commit resolves AND descends from the root the
    candidate's key names (`_roots_of`: its own history, not a history it merged; a commit that
    does not resolve has no roots, and a git that does not answer is a no), and v1.95.0 would
    have computed exactly the origin's key there (`_legacy_key`). A monorepo that merged another
    repository's history holds that repository's commits too, and under v1.95.0 may even have
    shared its key; the commit's roots tell them apart."""
    if o.get("checkouts"):
        return None

    def same_repository(n: dict, c: str) -> bool:
        return (_legacy_key(c) == o["project"]
                and n["project"][2:] in _roots_of(c, o["commit"]))
    hits = [n for n in candidates if n.get("checkouts") and n["project"] != o["project"]
            and n["retro"] == o["retro"]
            and any(same_repository(n, c) for c in n["checkouts"])]
    return hits[0] if len(hits) == 1 else None


def _newer_memory(a: str | None, b: str | None) -> str | None:
    """Of two ids of ONE record (same base), the higher revision; either when one is absent."""
    if not a or not b:
        return a or b
    return a if mem_rev(a) >= mem_rev(b) else b


def _known_projects(index: dict[str, dict]) -> set[str]:
    """Every project key an index records with provenance — an origin with `checkouts` (round
    15). Only the current key derivation writes provenance, so such a key is a real project of
    this version, never v1.95.0's name for another one. Every verb treats it as live: a project
    absent from THIS run's roots is not thereby another repository's to take."""
    return {o["project"] for e in index.values() for o in e["origins"] if o.get("checkouts")}


def _rekey_legacy(old: dict[str, dict], entries: dict[str, dict],
                  live: set[str] | frozenset = frozenset()) -> list[str]:
    """Re-key, in the previous index, every provenance-less origin `_legacy_twin` proves is
    the same repository as an origin this rebuild re-derived: it takes the new key, so
    `_attach_memory` carries its memory id to the re-derived origin and it is not carried as a
    second project. One that holds a different memory id than the previous index's copy under
    the new key is left as it is — carried, named — since two store records are not one. An
    origin whose own key this run re-derives is never re-keyed: it is that project's — nor is
    one whose PROJECT key any checkout read this run holds (round 14, F2), whatever its anchor:
    that project is here, and its retitled entry is not another repository's. `live` is this
    run's projects plus every project the previous index records with provenance
    (`_known_projects`, round 15): which project owns an id never depends on verb order or on
    which roots a rebuild was given."""
    said: list[str] = []
    for ck in sorted(old):
        if ck not in entries:
            continue
        origins, changed = list(old[ck]["origins"]), False
        for o in list(origins):
            if o["project"] in live:
                continue  # its project is here this run (its own origin re-derived or not): never moved
            n = _legacy_twin(o, entries[ck]["origins"])
            if n is None:
                continue
            twin = next((x for x in origins if _origin_key(x) == _origin_key(n)), None)
            if (twin and twin.get("memory") and o.get("memory")
                    and mem_base(twin["memory"]) != mem_base(o["memory"])):
                said.append(f"{ck} — {o['project']} {o['retro']}: the same repository as "
                            f"{n['project']}, but each holds its own memory id — left carried")
                continue
            moved = {k: v for k, v in o.items() if k != "carried"}
            moved["project"] = n["project"]
            memory = _newer_memory(o.get("memory"), (twin or {}).get("memory"))
            if memory:
                moved["memory"] = memory
            origins = [x for x in origins if x is not o and x is not twin] + [moved]
            said.append(f"{ck} — {o['retro']}: {o['project']} is {n['project']} (written before "
                        "provenance; its commit resolves in the checkout that re-derived it)"
                        + (f" · {memory}" if memory else ""))
            changed = True
        if changed:
            old[ck] = derive(origins)
    return said


def _one_project_per_memory(entries: dict[str, dict], old: dict[str, dict]) -> list[str]:
    """One memory id is one PROJECT's store record (round 13, M/M2), as `_one_class_per_memory`
    makes it one class's. Two projects may hold one id only while one of them is carried as
    `checkout holds another project` (the re-attach `record` allows at the same path). When two
    LIVE projects hold it — that origin's checkout came back — the id stays on the earlier
    holder: the project the previous index carried as `checkout holds another project` with it
    (it held the id before the re-attach), else the smaller project key. The other origin keeps
    its place without the id, and that is named; nothing is duplicated in silence."""
    first: dict[str, set] = {}
    for e in old.values():
        for o in e["origins"]:
            if o.get("memory") and o.get("carried") == CARRY_FOREIGN:
                first.setdefault(mem_base(o["memory"]), set()).add(o["project"])
    said: list[str] = []
    for ck in sorted(entries):
        origins = entries[ck]["origins"]
        live: dict[str, set] = {}
        for o in origins:
            if o.get("memory") and o.get("carried") != CARRY_FOREIGN:
                live.setdefault(mem_base(o["memory"]), set()).add(o["project"])
        changed = False
        for base, projects in sorted(live.items()):
            if len(projects) < 2:
                continue
            keep = (sorted(projects & first.get(base, set())) or sorted(projects))[0]
            out = []
            for o in origins:
                if (o.get("memory") and mem_base(o["memory"]) == base and o["project"] != keep
                        and o.get("carried") != CARRY_FOREIGN):
                    said.append(f"{base} is held by {keep} and {o['project']} for {ck}; one id is "
                                f"one project's store record, so it stays on {keep}, which held it "
                                f"first — {o['project']} {o['retro']} keeps its place without it "
                                "(record that project's own id there)")
                    o = {k: v for k, v in o.items() if k != "memory"}
                    changed = True
                out.append(o)
            origins = out
        if changed:
            entries[ck] = derive(origins)
    return said


def _resolves_in(checkout: str, sha: str) -> bool:
    """Does `sha` resolve in this checkout? A git that does not answer counts as yes: the
    cautious side, which keeps the origin counted rather than calling its checkout a stranger."""
    try:
        return commit_resolves(pathlib.Path(checkout), sha)
    except Refused:
        return True


def _carry_reason(ck: str, o: dict, run: dict) -> str:
    """Why a previous origin this run did not re-derive is carried — every one is (round 11):
    a rebuild never removes or moves anything on its own. The reason is accurate and decides
    one thing only: an origin whose every checkout now holds ANOTHER project is not counted in
    `seen`/`projects`/`status` (`derive`); every other reason is a temporary unavailability.

    Per checkout in the origin's provenance: not discovered, shallow, or owning a problem →
    `checkout not read`; holding another project AND not holding the origin's own commit →
    `checkout holds another project` (round 12: the same repository under another key is not a
    stranger); the
    entry refused there → `lesson refused`; its retro file not read → `retro file not read`;
    read, same project, entry absent → `no checkout read holds it`. The most available
    explanation wins; `checkout holds another project` only when every checkout says so."""
    k = _origin_key(o)
    if k in run["unresolved"]:
        return CARRY_UNRESOLVED if run["unresolved"][k] == o["commit"] else CARRY_CITES_UNRESOLVED
    prov = o.get("checkouts") or []
    if not prov:
        return CARRY_LEGACY
    states = set()
    rel = o["retro"].split("#", 1)[0]
    for c in prov:
        if c not in run["complete"] or c not in run["project"]:
            states.add(CARRY_CHECKOUT)
        elif run["project"][c] != o["project"] and not _resolves_in(c, o["commit"]):
            # Another project only when the origin's own commit is not there (round 12): the
            # same repository under another key — a branch, a lost default branch — still holds it.
            states.add(CARRY_FOREIGN)
        elif o["retro"] in run["refused"].get(c, ()):
            states.add(CARRY_REFUSED)
        elif rel not in run["files"].get(c, ()):
            states.add(CARRY_FILE)
        else:
            states.add(CARRY_GONE)
    for reason in (CARRY_REFUSED, CARRY_CHECKOUT, CARRY_FILE, CARRY_GONE):
        if reason in states:
            return reason
    return CARRY_FOREIGN


def _attach_memory(entries: dict[str, dict], old: dict[str, dict], notes: list[str]) -> None:
    """Memory ids follow the store's own identity, (project, classKey) — never a retro anchor
    (round 8, M1): a rotated archive or a reworded heading keeps its id, a class key changed
    inside one entry never inherits another key's id, and two entries under one heading keep one
    id each. Ids compare on the part before `@`; the highest revision wins (round 9, L3). Within
    (project, classKey) the id goes on the first origin by (project, retro); `emit-observatory`
    and `record` both read the origin of the project that holds the id (`_this_origin`), so the
    three agree. Only when one (project, classKey) held several ids does the exact
    (project, retro) decide, and only where that match is unique."""
    by_pc: dict[tuple, dict[str, set]] = {}
    best: dict[str, str] = {}
    for ck, e in old.items():
        for o in e["origins"]:
            m = o.get("memory")
            if m:
                by_pc.setdefault((o["project"], ck), {}).setdefault(mem_base(m), set()).add(o["retro"])
                if mem_base(m) not in best or mem_rev(m) > mem_rev(best[mem_base(m)]):
                    best[mem_base(m)] = m  # seeded unconditionally (round 11, #5)
    for ck, e in list(entries.items()):
        origins = sorted(e["origins"], key=_origin_key)
        changed = False
        for project in sorted({o["project"] for o in origins}):
            ids = by_pc.get((project, ck), {})
            mine = [o for o in origins if o["project"] == project]
            if len(ids) == 1:
                (base,) = ids
                mine[0]["memory"] = best[base]
                changed = True
            elif len(ids) > 1:
                for o in mine:
                    exact = [b for b, retros in ids.items() if o["retro"] in retros]
                    if len(exact) == 1:
                        o["memory"] = best[exact[0]]
                        changed = True
                if not any(o.get("memory") for o in mine):
                    notes.append(f"{ck} — {project}: several memory ids and none matches a retro "
                                 "anchor uniquely; the previous origins keep them")
        if changed:
            entries[ck] = derive(origins)


def _one_class_per_memory(entries: dict[str, dict], notes: list[str]) -> None:
    """One memory id (compared before `@`) is one store record: it carries its highest revision
    everywhere it appears, and it belongs to one class key. An index that already holds an id on
    two keys (the round-7 defect) keeps it on the first and says so."""
    top: dict[str, str] = {}
    holders: dict[str, list[str]] = {}
    for ck in sorted(entries):
        for o in entries[ck]["origins"]:
            m = o.get("memory")
            if m:
                b = mem_base(m)
                if b not in top or mem_rev(m) > mem_rev(top[b]):
                    top[b] = m  # seeded unconditionally (round 11, #5)
                if ck not in holders.setdefault(b, []):
                    holders[b].append(ck)
    for ck in list(entries):
        origins, changed = [], False
        for o in entries[ck]["origins"]:
            m = o.get("memory")
            if m and holders[mem_base(m)][0] != ck:
                o = {k: v for k, v in o.items() if k != "memory"}
                changed = True
                notes.append(f"memory id {mem_base(m)} was on {holders[mem_base(m)][0]} and {ck}; one id "
                             f"is one store record, so it stays on {holders[mem_base(m)][0]} only")
            elif m and m != top[mem_base(m)]:
                o = dict(o, memory=top[mem_base(m)])
                changed = True
            origins.append(o)
        if changed:
            entries[ck] = derive(origins)
    for ck, e in entries.items():
        for o in e["origins"]:
            if o.get("memory") and holders[mem_base(o["memory"])][0] != ck:
                raise Refused(f"memory id {o['memory']} is on two class keys — nothing was written")


def cmd_rebuild(a, idx: pathlib.Path) -> int:
    """A rebuild never removes or moves anything on its own (rounds 7–11 of release iteration 1;
    round 11 narrowed the contract under the loop guard).

    The index becomes the lessons derived from every readable retro — under the roots, and in
    every git worktree of each checkout found — merged with EVERY origin of the previous index
    this run did not re-derive, CARRIED FORWARD. An origin is one project's copy of a lesson,
    `(project, retro#anchor)` under its class key; it records its provenance, `checkouts`, the
    real paths of the checkouts it was derived from (local; `show` and `emit` omit it).

    No implicit removal: the only way an origin leaves the index is `--prune-carried`, narrowed
    to one reason by `--prune-carried-reason` (which needs `--prune-carried` and offers only the
    reasons below). No supersede, no move: a memory id stays on the origin that holds it;
    `_attach_memory` re-attaches it only to the same (project, classKey).

    The project key is the repository's (round 12): the first-parent root of its default
    branch, computed once per git common dir, so a worktree on a branch that merged an
    unrelated history, or a checkout sitting on an orphan `gh-pages`, is still its project.

    A carried origin keeps everything recorded on it and is marked `carried: <reason>`
    (`_carry_reason`): `checkout not read`, `retro file not read`, `no checkout read holds it`,
    `commit does not resolve`, `retro cites a commit that does not resolve`, `lesson refused`,
    `no provenance` (one this run proves is the same repository under a new key — no
    provenance, one re-derived origin of another key at its `retro#anchor`, its commit resolving
    in that checkout — is re-keyed instead, its memory id following: `_rekey_legacy`) —
    temporary unavailabilities, counted in `seen`/`projects`/`status` — or
    `checkout holds another project`, kept but NOT counted: every checkout in its provenance
    holds another project key AND the origin's own commit does not resolve there (a stranger at
    the path, a re-initialised history), so neither makes a phantom second project. `add`
    applies the same rule to this checkout's own old-key origin.

    A shallow clone (`git rev-parse --is-shallow-repository`) is never a source: a problem owned
    by that checkout, nothing derived under its unstable key, its origins carried as `checkout
    not read`; a shallow check that does not answer is refused the same way (and, having taught
    nothing, does not count as something read). Known limit: a project whose root commit
    changes (re-init, unshallow) starts new store records; the operator re-attaches by
    `record`-ing the old id on the new origin of the same class key — allowed, because the
    origin holding it is carried as `checkout holds another project` from that same checkout.
    The re-key needs the commit to descend from the new key's root and v1.95.0's key for that
    checkout to equal the origin's, and never touches a project read this run (round 14).
    One memory id stays on one live project (`_one_project_per_memory`): the earlier holder keeps
    it, the other is named. Every message — stdout, the session's notes and a refusal on stderr —
    names checkouts and files by name, never by absolute path (`_redact`, `_say`).

    Retro files are stamped when read and stamped again under the lock: a file that changed in
    between — an `add` landing mid-run — leaves its checkout not read for this run. Memory ids
    follow (project, classKey) and compare before `@`; the run refuses to write if a memory id
    of the previous index would vanish other than by `--prune-carried`, and names an id that only
    a corrupt line held.

    Exit 0 whenever anything was read — a retro, or a checkout discovered in full — and for a
    readable root holding no checkout at all (the index is written, every origin carried). Exit 1
    only when nothing could be read because every root was missing or unreadable — before the
    session opens, so no index, lock directory or migration is touched — or on a lock or
    unreadable-index refusal. On the default path the one-time merge of the standalone index,
    and setting a corrupt index aside (its good lines salvaged), run first, as for every verb."""
    found, problems, repos = find_retros(a.roots, a.depth)
    # Messages name checkouts and files, never an absolute path (round 12, E): every root,
    # checkout and the index itself, as given and as resolved, is shown by its name.
    # The index's directory and the standalone index are named too: the session's notes and a
    # refusal go to stderr through the same `_say` (round 13, O).
    shown = _SHOWN
    legacy = LEGACY_INDEX()
    for p in [pathlib.Path(r).expanduser() for r in a.roots] + list(repos):
        _show(p)
    for p in (idx, idx.parent, legacy, legacy.parent):
        _show(p, home_relative=True)
    def redact(text: str) -> str:
        return _redact(text, shown)
    lessons: list[tuple[str, dict]] = []
    private, seen_files = 0, 0
    unresolved: list[str] = []
    keys: dict[pathlib.Path, str] = {}
    stats: dict[tuple, tuple] = {}
    run: dict = {"files": {}, "refused": {}, "unresolved": {}, "complete": set(), "project": {}}
    # A shallow clone is never a source (round 11): its root commit — the project key — moves
    # whenever its boundary does, so nothing is derived from it until it is deepened.
    shallow: set[pathlib.Path] = set()
    unchecked: set[pathlib.Path] = set()
    for repo in repos:
        try:
            if _git(repo, "rev-parse", "--is-shallow-repository") == "true":
                shallow.add(repo)
                problems.append((repo, f"{repo.name}: a shallow clone — never a source; deepen it "
                                       "(git fetch --unshallow) for its lessons to be read"))
        except Refused as exc:
            # A shallow check that does not answer is refused, not trusted (round 12): the
            # checkout is no source this run, and that is a problem it owns. Unlike a clone that
            # answered "shallow", nothing was learned from it: it does not count as read.
            unchecked.add(repo)
            problems.append((repo, f"{repo.name}: the shallow check did not answer ({exc}) — not "
                                   "a source this run"))
    for repo, retro in found:
        if repo in shallow or repo in unchecked:
            continue
        c = checkout_id(repo)
        try:
            if repo not in keys:
                keys[repo] = project_key(repo)
            stats[(repo, retro)] = _stamp(retro)
            refused: set[str] = set()
            got, priv, probs = parse_retro(retro, repo, keys[repo], refused)
            mine, unres = [], []
            for le in got:
                if validate(le):
                    probs.append(f"{le['classKey']}: refused by lesson/1")
                    refused.add(le["origin"]["retro"])
                elif not commit_resolves(repo, le["origin"]["commit"]):
                    unres.append(le)
                else:
                    mine.append(le)
        except Refused as exc:
            problems.append((repo, f"{repo.name}: {exc}"))
            continue
        seen_files += 1
        private += priv
        run["files"].setdefault(c, set()).add(_relative(repo, retro))
        run["refused"].setdefault(c, set()).update(refused)
        for le in unres:
            run["unresolved"][_origin_key(le["origin"])] = le["origin"]["commit"]
        unresolved += [f"{repo.name}: {le['classKey']} (commit {le['origin']['commit']})" for le in unres]
        lessons += [(c, le) for le in mine]
        problems += [(repo, f"{repo.name}: {p}") for p in probs]
    # Which project each checkout holds: a path is not an identity (round 10, F1).
    for repo in repos:
        if repo in shallow or repo in unchecked:
            continue
        try:
            if repo not in keys:
                keys[repo] = project_key(repo)
            run["project"][checkout_id(repo)] = keys[repo]
        except Refused:
            continue
    owners = {owner for owner, _ in problems}
    run["complete"] = {checkout_id(r) for r, whole in repos.items() if whole and r not in owners}
    # A shallow checkout was found and read far enough to know it is shallow: something was read.
    if problems and not seen_files and not run["complete"] and not shallow:
        for _, problem in problems:
            print(f"  not read: {redact(problem)}")
        print("lessons: rebuild refused — nothing could be read; the index, its lock directory "
              "and any migration were not touched", file=sys.stderr)
        return 1
    with session(idx, a.default_index) as ss:
        # A retro that changed after it was read — an `add` landing between discovery and this
        # lock (round 10, H1) — leaves its checkout not read for this run.
        for (repo, retro), stamp in stats.items():
            if _stamp(retro) != stamp:
                problems.append((repo, f"{repo.name}: {_relative(repo, retro)} changed while the "
                                       "rebuild ran — read again next run"))
                run["complete"].discard(checkout_id(repo))
        # The previous index lends its memory ids and its carried origins. `session` already
        # refused an unreadable one (its contents may be good) and set a corrupt one aside, its
        # good lines salvaged; its notes go to stderr as for every verb, and into this report.
        old = ss.entries
        index_notes = list(ss.notes)
        corrupt_name, corrupt_only = _CORRUPT_ONLY.get(str(idx), ("", set()))
        notes: list[str] = []
        entries: dict[str, dict] = {}
        # Worktrees of one project hold the same entries: one origin per (project, anchor), its
        # provenance the checkouts that hold it in this run; where two copies differ the order
        # below decides, the same way every time.
        for c, le in sorted(lessons, key=lambda x: (x[0], json.dumps(x[1], sort_keys=True))):
            merge(entries, [le], c)
        # An origin v1.95.0 wrote — no provenance, keyed on the smallest root — that is the same
        # repository as one re-derived here takes its key first (round 13, K), so its memory id
        # follows and it is never a second project.
        rekeyed = _rekey_legacy(old, entries, set(run["project"].values()) | _known_projects(old))
        _attach_memory(entries, old, notes)
        derived = {(ck, _origin_key(o)) for ck, e in entries.items() for o in e["origins"]}
        carried, pruned = [], []
        for ck, e in sorted(old.items()):
            for o in e["origins"]:
                if (ck, _origin_key(o)) in derived:
                    continue
                rec = dict(o, carried=_carry_reason(ck, o, run))
                if a.prune_carried and a.prune_carried_reason in (None, rec["carried"]):
                    pruned.append((ck, rec))
                else:
                    carried.append((ck, rec))
        for ck, o in carried:
            held = [x for x in entries[ck]["origins"] if _origin_key(x) != _origin_key(o)] if ck in entries else []
            entries[ck] = derive(held + [o])
        _one_class_per_memory(entries, notes)
        shared = _one_project_per_memory(entries, old)
        # A memory id of the previous index vanishes only through --prune-carried (compared
        # before `@`). An id only a corrupt line held is counted and named.
        before = {mem_base(o["memory"]) for e in old.values() for o in e["origins"] if o.get("memory")}
        after = {mem_base(o["memory"]) for e in entries.values() for o in e["origins"] if o.get("memory")}
        gone = before - after - {mem_base(o["memory"]) for _, o in pruned if o.get("memory")}
        if gone:
            raise Refused(f"rebuild would lose {len(gone)} memory id(s) ({sorted(gone)[:3]}) — "
                          "nothing was written; this is a defect, report it")
        lost_to_corrupt = sorted(m for m in corrupt_only if mem_base(m) not in after)
        ss.entries = entries
        ss.save()
    print(f"lessons: rebuilt from {seen_files} retro file{'s' if seen_files != 1 else ''} in "
          f"{len(keys)} repositor{'y' if len(keys) == 1 else 'ies'} · {len(entries)} "
          f"lesson{'' if len(entries) == 1 else 's'} · {private} private entries skipped · "
          f"{len(unresolved)} with a commit that does not resolve · {len(carried)} origin"
          f"{'' if len(carried) == 1 else 's'} carried forward (an origin leaves the index only "
          "by --prune-carried)")
    for ck, o in carried:
        print(f"  carried ({o['carried']}): {ck} — {o['project']} {o['retro']}"
              + (f" · {o['memory']}" if o.get("memory") else ""))
    for ck, o in pruned:
        print(f"  pruned ({o['carried']}): {ck} — {o['project']} {o['retro']}")
    for u in unresolved:
        print(f"  skipped, commit does not resolve: {u}")
    for n in rekeyed:
        print(f"  re-keyed: {redact(n)}")
    for n in shared:
        print(f"  memory: {redact(n)}")
    for n in notes:
        print(f"  memory: {redact(n)}")
    for m in lost_to_corrupt:
        print(f"  memory: {m} is held only by a bad line, kept in {corrupt_name} — not in the live index")
    for n in index_notes:
        print(f"  previous index: {redact(n)}")
    for _, p in problems:
        print(f"  not read: {redact(p)}")
    return 0


def _stamp(path: pathlib.Path) -> tuple:
    """A retro file's (mtime_ns, size, inode) — compared under the lock to see it changed."""
    try:
        st = path.stat()
    except OSError:
        return ()
    return (st.st_mtime_ns, st.st_size, st.st_ino)


def cmd_candidates(a, idx: pathlib.Path) -> int:
    with session(idx, a.default_index) as ss:
        entries = ss.entries
    hits = sorted((e for e in entries.values() if e["projects"] >= a.min_projects),
                  key=lambda e: (-e["projects"], e["classKey"]))
    for e in hits:
        print(f"{e['id']} {e['classKey']} — {e['title']} (projects {e['projects']}, seen {e['seen']})")
    print(f"lessons: {len(hits)} candidate{'' if len(hits) == 1 else 's'} for learned.md "
          f"(projects ≥ {a.min_projects}) · {len(entries)} in the local index")
    return 0


def _this_origin(e: dict, root: pathlib.Path) -> dict:
    project = project_key(root)
    mine = [o for o in e["origins"] if o["project"] == project]
    if not mine:
        raise Refused(f"{e['id']} has no origin in this repository — emit and record from the "
                      "project that learned it")
    # The origin that holds this project's memory id first, then the first by (project, retro):
    # emit revises the record the store already has, and record writes where emit reads (round 9).
    return sorted(mine, key=lambda o: (not o.get("memory"), _origin_key(o)))[0]


def cmd_emit(a, idx: pathlib.Path) -> int:
    """The shared store's arguments for this project's origin.

    Two routes, chosen by the agent from the tools its session lists — this script cannot see
    them offline, so the choice is `--tool`, defaulting to the one every engine has:
    - `observatory_lesson` where the session lists it (the engine's lesson kind): exactly
      `owner, classKey, title, trigger, check, nouns, origin{projectId, commit}`, the engine's
      published inputSchema; idempotent on (classKey, projectId) in the store itself.
    - `observatory_record` otherwise: a note whose statement starts `lesson:`, so a later
      migration finds every one; a recorded lesson is revised (memoryId, expectedRevision).
    Either way the project travels as the same pseudonymous key the index holds, never a
    `project:<slug>` id, and the commit as `commit:` + 12 hex — the store's redactor removes a
    40-hex SHA as a credential shape and keeps exactly that short form."""
    root = repo_root(pathlib.Path(a.root or "."))
    refuse_shallow(root)
    with session(idx, a.default_index) as ss:
        e = _resolve(ss.entries, a.id)
    o = _this_origin(e, root)
    le = o["lesson"]
    if a.tool == "observatory_lesson":
        args = {"owner": OWNER, "classKey": le["classKey"], "title": le["title"],
                "trigger": le["trigger"], "check": le["check"], "nouns": le["nouns"],
                "origin": {"projectId": o["project"], "commit": "commit:" + o["commit"][:12]}}
        print(json.dumps({"tool": "observatory_lesson", "arguments": args}, ensure_ascii=True))
        return 0
    args = {"owner": OWNER, "statement": f"lesson: {le['classKey']} — {le['title']}",
            "why": f"{le['trigger']}; check: {le['check']}",
            "evidence": [{"kind": "commit", "ref": "commit:" + o["commit"][:12]},
                         {"kind": "lesson", "id": e["id"], "classKey": le["classKey"],
                          "project": o["project"], "nouns": le["nouns"]}]}
    mem = re.match(r"^(mem:[^@\s]+)@([0-9]+)$", o.get("memory") or "")
    if mem:
        args["memoryId"], args["expectedRevision"] = mem.group(1), int(mem.group(2))
    # ASCII-escaped JSON: lossless whatever the locale's codec (a '?' in a lesson's title
    # would be stored in the shared store as the lesson).
    print(json.dumps({"tool": "observatory_record", "arguments": args}, ensure_ascii=True))
    return 0


def _stdin_utf8() -> str:
    """stdin as UTF-8, whatever the locale: JSON is UTF-8 by definition, and decoding it in a
    Latin-1 locale stored mojibake in the index (verification round 3)."""
    return sys.stdin.buffer.read().decode("utf-8")


def _ledger_line(ledger: pathlib.Path | None, line: str) -> None:
    if ledger is None:
        return
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def cmd_record(a, idx: pathlib.Path) -> int:
    root = repo_root(pathlib.Path(a.root or "."))
    refuse_shallow(root)
    ledger = pathlib.Path(a.ledger) if a.ledger else (root / DEFAULT_LEDGER)
    ledger = ledger if ledger.exists() or a.ledger else None
    try:
        raw = _stdin_utf8() if a.answer == "-" else pathlib.Path(a.answer).read_text(encoding="utf-8")
        answer = json.loads(raw)
    except (OSError, ValueError) as exc:
        print(f"lessons: the answer cannot be read ({type(exc).__name__})", file=sys.stderr)
        return 2
    if not isinstance(answer, dict):
        print("lessons: the answer is not a JSON object", file=sys.stderr)
        return 2
    with session(idx, a.default_index) as ss:
        entries = ss.entries
        e = _resolve(entries, a.id)
        o = _this_origin(e, root)
        if answer.get("error"):
            code = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(answer["error"]))[:60] or "unknown"
            line = f"event: lessons — store refused — {code} — {e['id']} kept locally — {_now()}"
            _ledger_line(ledger, line)
            print(line)
            return 0
        mid = answer.get("memoryId") or answer.get("memory_id") or answer.get("id")
        # Absent means the store's first revision; a PRESENT 0 is a malformed answer, not 1.
        rev = answer["revision"] if "revision" in answer else (answer.get("record") or {}).get("revision", 1)
        if not isinstance(mid, str) or not mid.startswith("mem:") or re.search(r"[@\s]", mid):
            print("lessons: the answer names no memory id (mem:…)", file=sys.stderr)
            return 2
        if isinstance(rev, bool) or not (
                (isinstance(rev, int) and rev >= 1)
                or (isinstance(rev, str) and re.fullmatch(r"[1-9][0-9]*", rev, re.ASCII))):
            print(f"lessons: the answer's revision {rev!r} is not a whole number from 1",
                  file=sys.stderr)
            return 2
        memory = f"{mid}@{int(rev)}"
        # Only an id the loader itself accepts is written (round 12, H): `mem:`, a quote or a
        # backslash would make the next read set the whole index aside.
        if not MEM_RE.fullmatch(memory):
            print(f"lessons: {mid!r} is not a memory id this index can hold (mem:<id>@<rev>, no "
                  "quote, backslash or space) — nothing written", file=sys.stderr)
            return 2
        # One id is one PROJECT's record (round 12, C): an id another project's origin holds is
        # refused, naming that project — unless that origin is carried as `checkout holds another
        # project` FROM THIS CHECKOUT (round 13, M/M2): a re-init at the same path, the known
        # root-commit limit, where the operator re-attaches the old id on purpose. A stranger
        # elsewhere never takes it.
        here = checkout_id(root)
        holders = sorted({y["project"] for y in e["origins"] if y["project"] != o["project"]
                          and mem_base(y.get("memory") or "") == mid
                          and not (y.get("carried") == CARRY_FOREIGN and here in (y.get("checkouts") or []))})
        if holders:
            print(f"lessons: {mid} is the store record of project {', '.join(holders)} for "
                  f"{e['classKey']} — refused for {o['project']}, nothing written", file=sys.stderr)
            return 1
        # One id is one store record of one class (round 10, G1): an answer naming an id another
        # class key holds is a stale or misplaced answer — refused, nothing written, or `emit`
        # for this class would revise the other class's record.
        others = sorted(ck for ck, x in entries.items() if ck != e["classKey"]
                        and any(mem_base(y.get("memory") or "") == mid for y in x["origins"]))
        if others:
            print(f"lessons: {mid} is the store record of {', '.join(others)} — refused for "
                  f"{e['classKey']}, nothing written", file=sys.stderr)
            return 1
        # A revision never goes back (G1b): a replayed older answer is refused.
        held = max((mem_rev(y["memory"]) for y in e["origins"]
                    if y.get("memory") and mem_base(y["memory"]) == mid), default=0)
        if int(rev) < held:
            print(f"lessons: {mid} is at revision {held}; revision {int(rev)} is older — refused, "
                  "nothing written", file=sys.stderr)
            return 1
        # Replacing the id this origin already holds is a deliberate act (round 11, R5): without
        # --replace the old store record would be orphaned in silence.
        if o.get("memory") and mem_base(o["memory"]) != mid and not a.replace:
            print(f"lessons: this origin holds {o['memory']}; {mid} would replace it — pass "
                  "--replace to do that on purpose; nothing written", file=sys.stderr)
            return 1
        # The same id elsewhere in this entry takes the new revision too: one record, one revision.
        origins = [dict(x, memory=memory) if _origin_key(x) == _origin_key(o)
                   or (x.get("memory") and mem_base(x["memory"]) == mid) else x
                   for x in e["origins"]]
        entries[e["classKey"]] = derive(origins)
        ss.save()
    line = f"event: lessons — recorded {e['id']} as {memory} — {_now()}"
    _ledger_line(ledger, line)
    print(line)
    return 0


def cmd_show(a, idx: pathlib.Path) -> int:
    with session(idx, a.default_index) as ss:
        e = _resolve(ss.entries, a.id)
    # Provenance is local machine state — absolute checkout paths — and stays in the index file:
    # `show` prints the entry without it (round 10, G3), like everything that leaves the index.
    e = dict(e, origins=[{k: v for k, v in o.items() if k not in ("checkouts", "worktreeOf")}
                         for o in e["origins"]])
    print(json.dumps(e, ensure_ascii=True, indent=1, sort_keys=True))
    return 0


def main(argv: list[str]) -> int:
    # Titles and anchors may be in any script, and the messages carry dashes: under a locale
    # that cannot encode them, print() raised and the verb exited 1 for no reason of its own.
    # Human lines degrade to '?' there; what a machine reads (`emit-observatory`, `show`) is
    # ASCII-escaped JSON and stdin is read as UTF-8, so nothing a lesson carries is lost.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--index", help=f"the index file; default ${ENV_INDEX}, else "
                                        "~/.sshlg-skills/lessons/index.jsonl where "
                                        "~/.sshlg-skills exists, else "
                                        "~/.task-pipeline/lessons/index.jsonl")
    p = argparse.ArgumentParser(prog="lessons.py", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    ad = sub.add_parser("add", parents=[common], help="merge lessons into the index")
    src = ad.add_mutually_exclusive_group(required=True)
    src.add_argument("--retro", help="a retro or archive file of this repository")
    src.add_argument("--json", help="a lesson/1 object or list, a file or - for stdin")
    ad.add_argument("--entry", action="append", default=[], help="an entry's anchor; repeatable")
    ad.add_argument("--all", action="store_true", help="every Lesson-bearing entry of --retro")
    ad.add_argument("--root", help="the repository (default: the current directory)")
    q = sub.add_parser("query", parents=[common], help="lessons that fire on the task's nouns")
    q.add_argument("nouns", nargs="+")
    q.add_argument("--limit", type=int, default=5)
    rb = sub.add_parser("rebuild", parents=[common], help="re-derive the index from the retros")
    rb.add_argument("--roots", nargs="+", required=True)
    rb.add_argument("--depth", type=int, default=3, help="directory levels below each root")
    rb.add_argument("--prune-carried", action="store_true",
                    help="remove, on purpose, every origin the rebuild would carry forward — the "
                         "only way an origin leaves the index")
    rb.add_argument("--prune-carried-reason", choices=PRUNE_REASONS, default=None,
                    help="with --prune-carried: prune only the origins carried for this reason")
    c = sub.add_parser("candidates", parents=[common], help="lessons two or more projects hold")
    c.add_argument("--min-projects", type=int, default=2)
    sh = sub.add_parser("show", parents=[common], help="one entry with its origins")
    sh.add_argument("id")
    em = sub.add_parser("emit-observatory", parents=[common], help="the shared store's arguments")
    em.add_argument("id")
    em.add_argument("--tool", default="observatory_record",
                    choices=["observatory_record", "observatory_lesson"],
                    help="observatory_lesson where the session lists it, else observatory_record")
    em.add_argument("--root")
    rc = sub.add_parser("record", parents=[common], help="keep the store's answer")
    rc.add_argument("id")
    rc.add_argument("--answer", required=True, help="the tool's JSON answer, a file or -")
    rc.add_argument("--ledger", help=f"the run ledger (default {DEFAULT_LEDGER} when it exists)")
    rc.add_argument("--root")
    rc.add_argument("--replace", action="store_true",
                    help="replace a different memory id this origin already holds")
    sub.add_parser("path", parents=[common], help="the index this invocation would use")
    a = p.parse_args(argv)
    if a.cmd == "add" and a.retro and not (a.all or a.entry):
        p.error("add --retro needs --entry ANCHOR or --all")
    if a.cmd == "rebuild" and a.depth < 0:
        p.error("rebuild --depth must be non-negative")
    if a.cmd == "rebuild" and a.prune_carried_reason and not a.prune_carried:
        p.error("--prune-carried-reason narrows --prune-carried; it does nothing alone")
    idx = index_path(a.index)
    if a.cmd == "path":
        print(idx)  # the one verb whose answer IS the path
        return 0
    # Every verb's messages name files and directories, never an absolute path (round 14, L3).
    legacy = LEGACY_INDEX()
    for known in (idx, idx.parent, legacy, legacy.parent):
        _show(known, home_relative=True)
    _show(pathlib.Path(getattr(a, "root", None) or "."))
    for given in (getattr(a, "retro", None), getattr(a, "json", None), getattr(a, "answer", None),
                  getattr(a, "ledger", None)):
        if given and given != "-":
            _show(pathlib.Path(given))
    # The default path (no --index, no $TASK_PIPELINE_LESSONS) is the one a standalone index
    # may still need merging into: `session` does it, once, under both directories' locks.
    a.default_index = not a.index and not os.environ.get(ENV_INDEX)
    verbs = {"add": cmd_add, "query": cmd_query, "rebuild": cmd_rebuild, "candidates": cmd_candidates,
             "show": cmd_show, "emit-observatory": cmd_emit, "record": cmd_record}
    try:
        return verbs[a.cmd](a, idx)
    except Refused as exc:
        print(f"lessons: {_say(str(exc))}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
