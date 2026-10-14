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
    lessons.py rebuild --roots DIR ... [--depth 3] [--prune-carried]
        re-derive the index from every retro found under the roots and their git worktrees.
        Each origin records the checkouts it came from; it is removed only on positive
        evidence from those same checkouts — read completely, holding the origin's project,
        its retro file read, the entry gone. A checkout whose project key changed supersedes
        its old-key origin. Every other origin is carried forward, marked `carried: <reason>`,
        and named. Memory ids follow (project, classKey). Exit 1, touching nothing, only when
        nothing could be read: every root missing or unreadable. A readable empty root exits 0
        and writes the index. --prune-carried removes the carried origins on purpose
    lessons.py candidates [--min-projects 2]
        lessons two or more projects hold: the `retro.publish` queue for learned.md
    lessons.py show L-<sha12>
        one entry, with its origins (pseudonymous project keys, commits, retro anchors)
    lessons.py emit-observatory L-<sha12> [--tool observatory_record|observatory_lesson] [--root DIR]
        the store's arguments for this project's origin, as JSON: `observatory_lesson` where the
        session lists it, else `observatory_record` (the default; memoryId and expectedRevision
        once recorded). The same pseudonymous project key, never a `project:<slug>` id; the
        commit as `commit:` + 12 hex. The agent calls the tool
    lessons.py record L-<sha12> --answer FILE|- [--ledger PATH] [--root DIR]
        keep the store's memory id beside this project's origin; a refusal becomes one ledger
        line (`event: lessons — store refused — <code>`) and the local entry stays
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
of the repository's root commit — never its name, and the evidence commit must resolve in
the repository it came from.

**The retro line it reads**, inside a `### ` entry of the retro or its archive:

    - **Lesson:** `<class-key>` — <the class, one sentence> · **When:** <trigger> · **Nouns:** a, b, c

with the entry's own `**Surfaced at:** stage N · **Owned by:** stage M`, `**Fix:** grade G`,
`**The check:**` and `**Commit:** `<sha>`` lines. An entry with no Lesson line is private to
its project and is skipped, counted aloud.

Exit codes: 0 done (an absent index on `query` is a state, printed; a `rebuild` that named
what it skipped or carried); 1 a refusal — a lesson that fails lesson/1 or whose commit does
not resolve on `add`, a held lock, an unknown id, a `rebuild` whose every root was missing or
unreadable, a `record` naming an id another class holds or an older revision; 2 usage or an
unreadable input. Stdlib only (`references/portability.md`).
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
            print(f"lessons: {n}", file=sys.stderr)
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
    return pathlib.Path(top)


def project_key(root: pathlib.Path) -> str:
    """`p-` + 12 hex of the repository's root commit: stable across clones, names nothing."""
    roots = _git(root, "rev-list", "--max-parents=0", "HEAD")
    if not roots:
        raise Refused(f"the repository at {root} has no commit — a project key needs one")
    return "p-" + sorted(roots.split())[0][:12]


def commit_resolves(root: pathlib.Path, sha: str) -> bool:
    return _git(root, "cat-file", "-e", f"{sha}^{{commit}}") is not None


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
    if "\n" in value or "\r" in value:
        errs.append(f"{name} carries a line break — one line each")
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
    included) — so a complete rebuild with nothing carried equals the incremental index."""
    origins = sorted(origins, key=lambda o: (_origin_key(o), json.dumps(o, sort_keys=True)))
    first = origins[0]["lesson"]
    nouns = sorted({n for o in origins for n in o["lesson"]["nouns"]}, key=str.casefold)
    projects = len({o["project"] for o in origins})
    return {"schema": "lesson-index/1", "id": lesson_id(first["classKey"]),
            "classKey": first["classKey"], "title": first["title"], "trigger": first["trigger"],
            "check": first["check"], "grade": min(o["lesson"]["grade"] for o in origins),
            "stages": first["stages"], "nouns": nouns, "seen": len(origins),
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
MEM_RE = re.compile(r"mem:[^@\s\"\\]+@[0-9]+")


def mem_base(memory: str) -> str:
    """A memory id without its revision: `mem:x@3` → `mem:x`. Ids compare on this (round 9, L3)."""
    return memory.rsplit("@", 1)[0]


def mem_rev(memory: str) -> int:
    try:
        return int(memory.rsplit("@", 1)[1])
    except (IndexError, ValueError):
        return 0


def _entry_shape(e: object) -> bool:
    """A lesson-index/1 line every verb can use (rounds 8–10, L1/L2/H2): the entry's own fields
    with their types — class key, id, title, trigger, check, nouns (strings), seen, projects —
    and a non-empty list of origins, each with its project, retro, commit and a lesson that
    lesson/1 itself accepts (`validate`, with that origin), of the entry's class. Optional
    fields keep their types: memory `mem:<id>@<rev>`, checkouts non-empty strings, worktreeOf
    string to string, carried a string. Anything less is a corrupt line — set aside, its good
    neighbours salvaged — never a TypeError in the middle of a verb."""
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
        if "worktreeOf" in o and not (isinstance(o["worktreeOf"], dict) and all(
                isinstance(k, str) and isinstance(v, str) and k and v for k, v in o["worktreeOf"].items())):
            return False
        if "carried" in o and not isinstance(o["carried"], str):
            return False
    return True


def _put(out: dict[str, dict], e: dict, notes: list[str] | None) -> None:
    """Two lines for one class key (a hand-concatenated index) merge their origins — one origin
    per (project, retro), the one with the higher memory revision winning, its provenance the
    union of both copies' (round 10, G5) — never last-one-wins (round 9, L4/D3). Said aloud."""
    ck = e["classKey"]
    if ck not in out:
        out[ck] = e
        return
    by_key: dict[tuple, dict] = {}
    for o in out[ck]["origins"] + e["origins"]:
        k = _origin_key(o)
        if k in by_key:
            keep, other = ((o, by_key[k]) if mem_rev(o.get("memory") or "")
                           > mem_rev(by_key[k].get("memory") or "") else (by_key[k], o))
            prov = sorted(set(keep.get("checkouts") or []) | set(other.get("checkouts") or []))
            parents = dict(other.get("worktreeOf") or {}, **(keep.get("worktreeOf") or {}))
            o = dict(keep, **({"checkouts": prov} if prov else {}), **({"worktreeOf": parents} if parents else {}))
        by_key[k] = o
    out[ck] = derive(list(by_key.values()))
    if notes is not None:
        notes.append(f"two lines for {ck} merged — {len(by_key)} origin"
                     f"{'' if len(by_key) == 1 else 's'} kept, none dropped")


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
    for chunk in raw.splitlines():
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
        elif _entry_shape(e):
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
    for i, line in enumerate(text.splitlines(), 1):
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
        if not _entry_shape(e):
            raise IndexCorrupt(f"the index {path} has a line that is not a lesson (line {i}) — "
                               "`lessons.py rebuild` keeps it as .corrupt-<date> and re-derives it")
        _put(out, e, notes)
    _FUTURE[str(path)] = future
    if future:
        print(f"lessons: {len(future)} line{'' if len(future) == 1 else 's'} in a newer format "
              f"skipped in {path} (kept on write; a newer lessons.py reads them)", file=sys.stderr)
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


def cmd_add(a, idx: pathlib.Path) -> int:
    root = repo_root(pathlib.Path(a.root or "."))
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
        changed = merge(entries, lessons, checkout_id(root))
        if changed:
            ss.save()
    n = len(lessons)
    note = (f" · {private} entr{'y carries' if private == 1 else 'ies carry'} no Lesson line "
            "(project-private)") if private else ""
    print(f"lessons: {n} lesson{'' if n == 1 else 's'} · {changed} changed{note}")
    for le in lessons:
        e = entries[le["classKey"]]
        print(f"  {e['id']} {e['classKey']} — {e['status']} (seen {e['seen']}, projects {e['projects']})")
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
        print(f"lessons: local index absent ({idx}) — nothing to read; the retro and "
              "learned.md still run")
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
        problems.append((None, f"{exc.filename}: cannot discover ({type(exc).__name__})"))

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
            problems.append((here, f"{here}: {exc}"))

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
        problems.append((repo, f"{repo}: worktrees cannot be listed ({why})"))
        return []
    out, main = [], None
    for n, block in enumerate(listing.split("\n\n")):
        lines = block.splitlines()
        head = next((ln[len("worktree "):] for ln in lines if ln.startswith("worktree ")), None)
        if head is None:
            continue
        if n == 0 and "bare" not in lines:
            main = checkout_id(pathlib.Path(head))  # git lists the main worktree first
        if any(ln == "bare" or ln.startswith("prunable") for ln in lines):
            continue
        path = pathlib.Path(head)
        if path.is_dir():
            out.append(path)
    # Parentage (round 10, F2): which worktrees the main checkout lists right now. A worktree
    # it no longer lists was removed, and an origin's provenance may then count it gone.
    if main is not None:
        _TREES[main] = {checkout_id(p) for p in out}
        for p in out:
            if checkout_id(p) != main:
                _PARENT[checkout_id(p)] = main
    return out


# Per run: main checkout → the worktrees it lists (listing read), and worktree → its main.
_TREES: dict[str, set[str]] = {}
_PARENT: dict[str, str] = {}


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
CARRY_RECORDED = "no checkout read holds it"


def _gone_from(c: str, ck: str, o: dict, run: dict) -> bool:
    """Positive evidence, from checkout `c` itself, that it no longer holds origin `o` of class
    `ck` (round 9): `c` was discovered and read completely with no problem owned by it, it holds
    the origin's PROJECT (round 10, F1 — a path is not an identity), its retro file at the
    origin's path was read, and that file holds no such entry. Or (round 10, F2) `c` was a
    worktree whose main checkout read completely and no longer lists it: it was removed."""
    if c not in run["project"]:
        main = (o.get("worktreeOf") or {}).get(c)
        return bool(main) and main in run["complete"] and main in run["trees"] and c not in run["trees"][main]
    rel = o["retro"].split("#", 1)[0]
    if (c not in run["complete"] or run["project"][c] != o["project"]
            or rel not in run["files"].get(c, ())):
        return False
    return (ck, o["retro"]) not in run["held"].get(c, ()) and o["retro"] not in run["refused"].get(c, ())


def _moved_in(c: str, ck: str, o: dict, run: dict) -> str | None:
    """The new project key when checkout `c` now holds another project key AND the same
    (classKey, retro) — the same checkout after `fetch --unshallow` or a re-init, not a stranger
    (round 10, J1/J2). The old-key origin is then superseded by the one `c` derives."""
    p = run["project"].get(c)
    if (p is None or p == o["project"] or c not in run["complete"]
            or (ck, o["retro"]) not in run["held"].get(c, ())):
        return None
    return p


def _carry_reason(ck: str, o: dict, still: list[str], run: dict) -> str:
    """The accurate reason an origin is carried, given the checkouts that did not show it gone."""
    k = _origin_key(o)
    if k in run["unresolved"]:
        return CARRY_UNRESOLVED if run["unresolved"][k] == o["commit"] else CARRY_CITES_UNRESOLVED
    if any(o["retro"] in run["refused"].get(c, ()) for c in still):
        return CARRY_REFUSED
    if any(c in run["complete"] and run["project"].get(c) not in (None, o["project"]) for c in still):
        return CARRY_FOREIGN
    if any(c not in run["complete"] for c in still):
        return CARRY_CHECKOUT
    return CARRY_FILE


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
                if mem_rev(m) > mem_rev(best.get(mem_base(m), "")):
                    best[mem_base(m)] = m
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
                if mem_rev(m) > mem_rev(top.get(b, "")):
                    top[b] = m
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
    """Rebuild never loses what it cannot re-derive (rounds 7–10 of release iteration 1).

    The index becomes the lessons derived from every readable retro — under the roots, and in
    every git worktree of each checkout found — merged with the previous index's origins that
    could not be re-derived, CARRIED FORWARD. An origin is one project's copy of a lesson,
    `(project, retro#anchor)` under its class key, and it records its PROVENANCE: `checkouts`,
    the real paths of the checkouts it was derived from, and `worktreeOf`, the main checkout of
    each that was a git worktree. Provenance stays in the index file; `show` and `emit` omit it.

    The one rule (round 9): implicit removal needs positive evidence from the same checkout.
    Without `--prune-carried`, an origin leaves only when, for EVERY checkout in its provenance,
    (a) that checkout was discovered in this run and read completely, with no problem owned by
    it, and holds the origin's PROJECT — a path is not an identity (round 10); (b) its retro
    file at the origin's path was read; and (c) that file no longer holds the entry. A worktree
    whose main checkout read completely and no longer lists it was removed: it counts as gone.

    A checkout that now holds ANOTHER project key and the same (classKey, retro) is the same
    checkout after `fetch --unshallow` or a re-init: its old-key origin is superseded by the one
    it derives — the memory id moves, the run says `moved: project key changed`, and `projects`
    does not count it twice (round 10). A shallow clone is a problem owned by its checkout: its
    key is not stable yet.

    Every other case carries the origin, with the reason:
      * `checkout not read` — not discovered, or a problem is owned by it (an unreadable retro,
        a refused `git worktree list`, a shallow clone, a retro that changed during the run);
      * `checkout holds another project` — a different project now sits at that path;
      * `retro file not read` — the checkout read completely, but not that file (outside the
        artifact root, moved, deleted);
      * `no provenance` — an origin written before provenance existed;
      * `commit does not resolve` / `retro cites a commit that does not resolve` /
        `lesson refused` — the entry is there and could not be derived;
      * `no checkout read holds it` — every checkout showed it gone, but it holds a memory id
        the run did not re-attach elsewhere: the store still has that record.
    A carried origin keeps everything recorded on it, the checkouts that did not show it gone,
    and `carried: <reason>`; it counts toward `seen`, `projects` and `status`, and is re-derived
    and un-marked as soon as a checkout holding it reads again.

    Retro files are stamped when read and stamped again under the lock: a file that changed in
    between — an `add` landing mid-run — leaves its checkout incomplete for this run (round 10).

    Memory ids follow (project, classKey) and compare before `@` (`_attach_memory`,
    `_one_class_per_memory`). The run refuses to write if a memory id of the previous index would
    vanish other than by `--prune-carried`; an id that only a corrupt line held is named, with
    the `.corrupt-<date>` file that keeps it.

    Exit 0 whenever anything was read — a retro, or a checkout discovered in full — and for a
    readable root that holds no checkout at all (an empty scope: the index is written, every
    origin carried). Exit 1 only when nothing could be read because every root was missing or
    unreadable — before the session opens, so no index, lock directory or migration is touched —
    or on a lock or unreadable-index refusal. On the default path the one-time merge of the
    standalone index, and setting a corrupt index aside (its good lines salvaged), run first, as
    for every verb."""
    found, problems, repos = find_retros(a.roots, a.depth)
    lessons: list[tuple[str, dict]] = []
    private, seen_files = 0, 0
    unresolved: list[str] = []
    keys: dict[pathlib.Path, str] = {}
    stats: dict[tuple, tuple] = {}
    run: dict = {"files": {}, "held": {}, "refused": {}, "unresolved": {}, "complete": set(),
                 "project": {}, "trees": dict(_TREES)}
    for repo, retro in found:
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
        run["held"].setdefault(c, set()).update((le["classKey"], le["origin"]["retro"]) for le in mine + unres)
        run["refused"].setdefault(c, set()).update(refused)
        for le in unres:
            run["unresolved"][_origin_key(le["origin"])] = le["origin"]["commit"]
        unresolved += [f"{repo.name}: {le['classKey']} (commit {le['origin']['commit']})" for le in unres]
        lessons += [(c, le) for le in mine]
        problems += [(repo, f"{repo.name}: {p}") for p in probs]
    # Which project each checkout holds (round 10, F1: a path is not an identity), and whether its
    # key is stable: a shallow clone's root commit moves when it is deepened (J1).
    for repo in repos:
        try:
            if repo not in keys:
                keys[repo] = project_key(repo)
            run["project"][checkout_id(repo)] = keys[repo]
        except Refused:
            continue
        try:
            shallow = _git(repo, "rev-parse", "--is-shallow-repository") == "true"
        except Refused:
            shallow = False
        if shallow:
            problems.append((repo, f"{repo}: a shallow clone — its project key changes when it is "
                                   "deepened, so it shows nothing gone until then"))
    owners = {owner for owner, _ in problems}
    run["complete"] = {checkout_id(r) for r, whole in repos.items() if whole and r not in owners}
    if problems and not seen_files and not run["complete"]:
        for _, problem in problems:
            print(f"  not read: {problem}")
        print("lessons: rebuild refused — nothing could be read; the index, its lock directory "
              "and any migration were not touched", file=sys.stderr)
        return 1
    with session(idx, a.default_index) as ss:
        # A retro that changed after it was read — an `add` landing between discovery and this
        # lock (round 10, H1) — decides nothing: its checkout is not complete for this run.
        for (repo, retro), stamp in stats.items():
            if _stamp(retro) != stamp:
                problems.append((repo, f"{repo.name}: {_relative(repo, retro)} changed while the "
                                       "rebuild ran — read again next run"))
                run["complete"].discard(checkout_id(repo))
        # The previous index lends its memory ids, its provenance and its carried origins.
        # `session` already refused an unreadable one (its contents may be good) and set a
        # corrupt one aside, its good lines salvaged; its notes go to stderr as for every verb,
        # and into this report.
        old = ss.entries
        index_notes = list(ss.notes)
        corrupt_name, corrupt_only = _CORRUPT_ONLY.get(str(idx), ("", set()))
        notes: list[str] = []
        entries: dict[str, dict] = {}
        # Worktrees of one project hold the same entries: one origin per (project, anchor), its
        # provenance the union of the checkouts that hold it; where two copies differ the order
        # below decides, the same way every time.
        for c, le in sorted(lessons, key=lambda x: (x[0], json.dumps(x[1], sort_keys=True))):
            merge(entries, [le], c)
        # A re-derived origin keeps the previous provenance that did not show it gone, and every
        # worktree in it remembers its main checkout (round 10, F2).
        for ck, e in list(entries.items()):
            prev = {_origin_key(o): o for o in old.get(ck, {}).get("origins", [])}
            origins = []
            for o in e["origins"]:
                was = prev.get(_origin_key(o)) or {}
                extra = [c for c in was.get("checkouts") or []
                         if c not in o["checkouts"] and not _gone_from(c, ck, dict(o, worktreeOf=was.get("worktreeOf") or {}), run)]
                prov = sorted(set(o["checkouts"]) | set(extra))
                parents = {c: m for c, m in (was.get("worktreeOf") or {}).items() if c in prov}
                parents.update({c: _PARENT[c] for c in prov if c in _PARENT})
                o = dict(o, checkouts=prov)
                if parents:
                    o["worktreeOf"] = parents
                origins.append(o)
            entries[ck] = derive(origins)
        _attach_memory(entries, old, notes)
        derived = {(ck, _origin_key(o)) for ck, e in entries.items() for o in e["origins"]}
        carried, pruned, removed, moved, all_gone = [], [], [], [], []
        for ck, e in sorted(old.items()):
            for o in e["origins"]:
                if (ck, _origin_key(o)) in derived:
                    continue
                prov = o.get("checkouts") or []
                newkey = {c: _moved_in(c, ck, o, run) for c in prov}
                still = [c for c in prov if not newkey[c] and not _gone_from(c, ck, o, run)]
                target = next((x for c in prov if newkey[c] for x in entries.get(ck, {}).get("origins", [])
                               if _origin_key(x) == (newkey[c], o["retro"])), None)
                if not prov:
                    reason, keep = CARRY_LEGACY, prov
                elif still or (any(newkey.values()) and target is None):
                    still = still or [c for c in prov if newkey[c]]
                    reason, keep = _carry_reason(ck, o, still, run), still
                elif target is not None:
                    # The same checkout under a new project key (J1/J2): superseded, not doubled.
                    if o.get("memory") and not target.get("memory"):
                        target["memory"] = o["memory"]
                        entries[ck] = derive(entries[ck]["origins"])
                    if not o.get("memory") or mem_base(target["memory"]) == mem_base(o["memory"]):
                        moved.append((ck, o, target["project"]))
                        continue
                    reason, keep = CARRY_RECORDED, prov
                else:
                    all_gone.append((ck, o))
                    continue
                rec = dict(o, carried=reason)
                if keep:
                    rec["checkouts"] = sorted(keep)
                (pruned if a.prune_carried else carried).append((ck, rec))
        attached = {mem_base(o["memory"]) for e in entries.values() for o in e["origins"] if o.get("memory")}
        for ck, o in all_gone:
            if o.get("memory") and mem_base(o["memory"]) not in attached:
                (pruned if a.prune_carried else carried).append((ck, dict(o, carried=CARRY_RECORDED)))
            else:
                removed.append((ck, o))
        for ck, o in carried:
            held = [x for x in entries[ck]["origins"] if _origin_key(x) != _origin_key(o)] if ck in entries else []
            entries[ck] = derive(held + [o])
        _one_class_per_memory(entries, notes)
        # A memory id of the previous index vanishes only through --prune-carried (round 8, L6;
        # compared before `@`, round 9). An id only a corrupt line held is counted and named.
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
          f"{'' if len(carried) == 1 else 's'} carried forward")
    for ck, o in carried:
        print(f"  carried ({o['carried']}): {ck} — {o['project']} {o['retro']}"
              + (f" · {o['memory']}" if o.get("memory") else ""))
    for ck, o in pruned:
        print(f"  pruned ({o['carried']}): {ck} — {o['project']} {o['retro']}")
    for ck, o, new in moved:
        print(f"  moved: project key changed — {ck} {o['retro']}: {o['project']} → {new}"
              + (f" · {o['memory']}" if o.get("memory") else ""))
    for ck, o in removed:
        print(f"  removed (its checkout read it and no longer holds it): {ck} — {o['project']} {o['retro']}")
    for u in unresolved:
        print(f"  skipped, commit does not resolve: {u}")
    for n in notes:
        print(f"  memory: {n}")
    for m in lost_to_corrupt:
        print(f"  memory: {m} is held only by a bad line, kept in {corrupt_name} — not in the live index")
    for n in index_notes:
        print(f"  previous index: {n}")
    for _, p in problems:
        print(f"  not read: {p}")
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
    with session(idx, a.default_index) as ss:
        e = _resolve(ss.entries, a.id)
    o = _this_origin(e, repo_root(pathlib.Path(a.root or ".")))
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
                    help="remove, on purpose, every origin the rebuild would carry forward")
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
    sub.add_parser("path", parents=[common], help="the index this invocation would use")
    a = p.parse_args(argv)
    if a.cmd == "add" and a.retro and not (a.all or a.entry):
        p.error("add --retro needs --entry ANCHOR or --all")
    if a.cmd == "rebuild" and a.depth < 0:
        p.error("rebuild --depth must be non-negative")
    idx = index_path(a.index)
    if a.cmd == "path":
        print(idx)
        return 0
    # The default path (no --index, no $TASK_PIPELINE_LESSONS) is the one a standalone index
    # may still need merging into: `session` does it, once, under both directories' locks.
    a.default_index = not a.index and not os.environ.get(ENV_INDEX)
    verbs = {"add": cmd_add, "query": cmd_query, "rebuild": cmd_rebuild, "candidates": cmd_candidates,
             "show": cmd_show, "emit-observatory": cmd_emit, "record": cmd_record}
    try:
        return verbs[a.cmd](a, idx)
    except Refused as exc:
        print(f"lessons: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
