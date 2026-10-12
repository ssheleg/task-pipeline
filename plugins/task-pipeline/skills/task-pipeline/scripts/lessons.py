#!/usr/bin/env python3
"""The local lesson index — every project's retro lessons, readable from any project.

A retro entry is written per project and read by that project's next stage 0. An agent on
another project never sees it, unless a wiki or a shared store happens to be installed. This
script is the floor every install has (`references/iteration.md` → *The learning loop*): a
retro entry that carries a `**Lesson:**` line is a lesson (`templates/lesson.schema.json`,
lesson/1), and the index projects every such entry from every project on this machine into
one file that stage 0 queries by the task's nouns.

**The retro stays canonical; the index is a projection.** It can be lost and rebuilt from
the retros (`rebuild`), and a rebuild equals the incremental index byte for byte, because an
entry is a pure function of its origins.

    lessons.py add --retro FILE (--entry ANCHOR ... | --all) [--root DIR]
    lessons.py add --json FILE|-                              [--root DIR]
        validate lesson/1 and merge it into the index; a second project's copy of one
        classKey makes it a candidate, a repeat from the same project revises, never mints
    lessons.py query NOUN ... [--limit 5]
        at most --limit lines: `[lesson L-<sha12>] title — trigger — check (seen N, projects K)`
    lessons.py rebuild --roots DIR ... [--depth 3]
        re-derive the whole index from every retro found under the roots
    lessons.py candidates [--min-projects 2]
        lessons two or more projects hold: the `retro.publish` queue for learned.md
    lessons.py show L-<sha12>
        one entry, with its origins (pseudonymous project keys, commits, retro anchors)
    lessons.py emit-observatory L-<sha12> [--tool observatory_record|observatory_lesson]
                                          [--project-id project:<slug>] [--root DIR]
        the shared store's arguments for this project's origin, as JSON; the agent calls the tool
    lessons.py record L-<sha12> --answer FILE|- [--ledger PATH] [--root DIR]
        keep the store's memory id beside this project's origin; a refusal becomes one ledger
        line (`event: lessons — store refused — <code>`) and the local entry stays
    lessons.py path
        the index this invocation would use

**Where the index lives.** `--index PATH`, else `$TASK_PIPELINE_LESSONS`, else
`~/.sshlg-skills/lessons/index.jsonl`. The default is a proposal, not yet a contract: the
directory is the family's machine-state home (sshlg-skills `docs/working-rules/state-json.md`),
and listing `lessons/` there as task-pipeline's awaits that family's agreement. Until it is
recorded, the path stays a parameter and the doctrine says so. Directory 0700, file 0600,
written by a unique temp file and `os.replace`, under an exclusive lock
(`index.jsonl.lock`, `flock`; `$TASK_PIPELINE_LESSONS_LOCK_TIMEOUT` seconds, default 10).

**What a lesson may carry.** The fields of lesson/1 and nothing else. The text fields are one
line each and refused when they carry an absolute or home path, a URL, an e-mail address, a
credential shape or a long hex/base64 run: what a pattern can see. A person's or a customer's
name a pattern cannot see; that stays the writer's duty (`references/retrospective.md` →
*What may leave the project*). The project is a pseudonymous key — `p-` and 12 hex digits
of the repository's root commit — never its name, and the evidence commit must resolve in
the repository it came from.

**The retro line it reads**, inside a `### ` entry of the retro or its archive:

    - **Lesson:** `<class-key>` — <the class, one sentence> · **When:** <trigger> · **Nouns:** a, b, c

with the entry's own `**Surfaced at:** stage N · **Owned by:** stage M`, `**Fix:** grade G`,
`**The check:**` and `**Commit:** `<sha>`` lines. An entry with no Lesson line is private to
its project and is skipped, counted aloud.

Exit codes: 0 done (an absent index on `query` is a state, printed); 1 a refusal — a lesson
that fails lesson/1, a commit that does not resolve, a held lock, an unknown id; 2 usage or an
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
RETRO_REF = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_./-]*\.md#[a-z0-9-]+$")
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
    return pathlib.Path.home() / ".sshlg-skills" / "lessons" / "index.jsonl"


def _git(root: pathlib.Path, *args: str) -> str | None:
    try:
        r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
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
    """An entry's anchor: lowercase, every run of other characters one hyphen."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


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
    """Fill what the repository decides: the schema tag and the pseudonymous project key."""
    out = dict(lesson)
    out.setdefault("schema", "lesson/1")
    if isinstance(out.get("origin"), dict):
        o = dict(out["origin"])
        o.setdefault("project", project_key(root))
        out["origin"] = o
    return out


# ---------------------------------------------------------------------------- retro parsing


def _relative(root: pathlib.Path, path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        raise Refused(f"{path} is outside the repository at {root}")


def parse_retro(path: pathlib.Path, root: pathlib.Path, project: str) -> tuple[list[dict], int, list[str]]:
    """Lessons from one retro file: (lessons, entries without a Lesson line, refusals)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
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
    """One index entry as a pure function of its origins — so rebuild equals incremental."""
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


def _origin(lesson: dict, memory: str | None = None) -> dict:
    o = lesson["origin"]
    body = {k: lesson[k] for k in FIELDS if k not in ("schema", "origin")}
    rec = {"project": o["project"], "commit": o["commit"], "retro": o["retro"], "lesson": body}
    if memory:
        rec["memory"] = memory
    return rec


def merge(entries: dict[str, dict], lessons: list[dict]) -> int:
    """Merge lessons into {classKey: entry}; returns how many origins changed."""
    changed = 0
    for le in lessons:
        ck = le["classKey"]
        origins = list(entries[ck]["origins"]) if ck in entries else []
        key = (le["origin"]["project"], le["origin"]["retro"])
        old = next((o for o in origins if _origin_key(o) == key), None)
        new = _origin(le, old.get("memory") if old else None)
        if old == new:
            continue
        origins = [o for o in origins if _origin_key(o) != key] + [new]
        entries[ck] = derive(origins)
        changed += 1
    return changed


def load(path: pathlib.Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    out = {}
    try:
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                e = json.loads(line)
                out[e["classKey"]] = e
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise Refused(f"the index {path} cannot be read ({type(exc).__name__}) — "
                      "`lessons.py rebuild` re-derives it from the retros")
    return out


def dump(entries: dict[str, dict]) -> str:
    return "".join(json.dumps(entries[k], ensure_ascii=False, sort_keys=True) + "\n"
                   for k in sorted(entries))


class locked:
    """An exclusive lock around a whole read-modify-write of the index (graph.py's `held`,
    with a timeout: a writer that cannot get the lock refuses rather than waiting forever)."""

    def __init__(self, path: pathlib.Path):
        self.lock = path.parent / (path.name + ".lock")
        self.fh = None

    def __enter__(self):
        self.lock.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(self.lock.parent, 0o700)
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
        fd = os.open(self.lock, os.O_RDWR | os.O_CREAT, 0o600)
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


def save(path: pathlib.Path, entries: dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".index-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(dump(entries))
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
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
            raw = sys.stdin.read() if a.json == "-" else pathlib.Path(a.json).read_text(encoding="utf-8")
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
    with locked(idx):
        entries = load(idx)
        changed = merge(entries, lessons)
        if changed:
            save(idx, entries)
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
    if not idx.exists():
        print(f"lessons: local index absent ({idx}) — nothing to read; the retro and "
              "learned.md still run")
        return 0
    entries = load(idx)
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


def find_retros(roots: list[str], depth: int) -> list[tuple[pathlib.Path, pathlib.Path]]:
    """(repository root, retro file) for every retro and archive file under the roots."""
    found = []
    for r in roots:
        base = pathlib.Path(r).expanduser()
        for cur, dirs, _files in os.walk(base, followlinks=True):
            here = pathlib.Path(cur)
            rel_depth = len(here.relative_to(base).parts)
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
            if (here / ".git").exists():
                art = _artifact_root(here)
                files = [art / "retro.md"] + sorted((art / "retro").glob("*.md"))
                found += [(here, f) for f in files if f.is_file()]
            if rel_depth >= depth:
                dirs[:] = []
    return found


def _artifact_root(repo: pathlib.Path) -> pathlib.Path:
    """`paths.artifacts` in pipeline.json, else docs/evidence, else docs/superpowers."""
    try:
        conf = json.loads((repo / "pipeline.json").read_text(encoding="utf-8"))
        given = (conf.get("paths") or {}).get("artifacts")
        if isinstance(given, str) and given and not given.startswith("/"):
            return repo / given
    except (OSError, ValueError, AttributeError):
        pass
    for name in ("docs/evidence", "docs/superpowers"):
        if (repo / name / "retro.md").is_file() or (repo / name / "retro").is_dir():
            return repo / name
    return repo / "docs/evidence"


def cmd_rebuild(a, idx: pathlib.Path) -> int:
    found = find_retros(a.roots, a.depth)
    lessons, problems, private, unresolved, seen_files = [], [], 0, 0, 0
    keys: dict[pathlib.Path, str] = {}
    for repo, retro in found:
        try:
            if repo not in keys:
                keys[repo] = project_key(repo)
            got, priv, probs = parse_retro(retro, repo, keys[repo])
        except Refused as exc:
            problems.append(str(exc))
            continue
        seen_files += 1
        private += priv
        problems += [f"{repo.name}: {p}" for p in probs]
        for le in got:
            if validate(le):
                problems.append(f"{repo.name}: {le['classKey']}: refused by lesson/1")
            elif not commit_resolves(repo, le["origin"]["commit"]):
                unresolved += 1
            else:
                lessons.append(le)
    with locked(idx):
        old = load(idx) if idx.exists() else {}
        memory = {(o["project"], o["retro"]): o["memory"]
                  for e in old.values() for o in e["origins"] if o.get("memory")}
        entries: dict[str, dict] = {}
        # Worktrees of one project hold the same entries: one origin per (project, anchor),
        # and where two copies differ the order below decides, the same way every time.
        for le in sorted(lessons, key=lambda x: json.dumps(x, sort_keys=True)):
            merge(entries, [le])
        for e in entries.values():
            origins = [dict(o, memory=memory[_origin_key(o)]) if _origin_key(o) in memory else o
                       for o in e["origins"]]
            entries[e["classKey"]] = derive(origins)
        save(idx, entries)
    print(f"lessons: rebuilt from {seen_files} retro file{'s' if seen_files != 1 else ''} in "
          f"{len(keys)} repositor{'y' if len(keys) == 1 else 'ies'} · {len(entries)} lessons · "
          f"{private} private entries skipped · {unresolved} with a commit that does not resolve")
    for p in problems:
        print(f"  not read: {p}")
    return 0


def cmd_candidates(a, idx: pathlib.Path) -> int:
    entries = load(idx)
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
    return sorted(mine, key=_origin_key)[0]


def cmd_emit(a, idx: pathlib.Path) -> int:
    e = _resolve(load(idx), a.id)
    o = _this_origin(e, repo_root(pathlib.Path(a.root or ".")))
    le = o["lesson"]
    if a.tool == "observatory_lesson":
        args = {"owner": OWNER, "classKey": le["classKey"], "title": le["title"],
                "trigger": le["trigger"], "check": le["check"], "nouns": le["nouns"],
                "origin": {"projectId": a.project_id, "commit": o["commit"]}}
        if not a.project_id:
            del args["origin"]["projectId"]
    else:
        # The bridge until the store has a lesson kind: a note whose statement starts
        # `lesson:`, so a later migration can find every one (MN §3.8 step 1).
        args = {"owner": OWNER, "statement": f"lesson: {le['classKey']} — {le['title']}",
                "why": f"{le['trigger']}; check: {le['check']}",
                "evidence": [{"kind": "commit", "sha": o["commit"]},
                             {"kind": "lesson", "id": e["id"], "classKey": le["classKey"],
                              "nouns": le["nouns"]}]}
        if a.project_id:
            args["projectId"] = a.project_id
    print(json.dumps({"tool": a.tool, "arguments": args}, ensure_ascii=False))
    return 0


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
        raw = sys.stdin.read() if a.answer == "-" else pathlib.Path(a.answer).read_text(encoding="utf-8")
        answer = json.loads(raw)
    except (OSError, ValueError) as exc:
        print(f"lessons: the answer cannot be read ({type(exc).__name__})", file=sys.stderr)
        return 2
    if not isinstance(answer, dict):
        print("lessons: the answer is not a JSON object", file=sys.stderr)
        return 2
    with locked(idx):
        entries = load(idx)
        e = _resolve(entries, a.id)
        o = _this_origin(e, root)
        if answer.get("error"):
            code = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(answer["error"]))[:60] or "unknown"
            line = f"event: lessons — store refused — {code} — {e['id']} kept locally — {_now()}"
            _ledger_line(ledger, line)
            print(line)
            return 0
        mid = answer.get("memoryId") or answer.get("memory_id") or answer.get("id")
        rev = answer.get("revision") or (answer.get("record") or {}).get("revision") or 1
        if not isinstance(mid, str) or not mid.startswith("mem:") or re.search(r"[@\s]", mid):
            print("lessons: the answer names no memory id (mem:…)", file=sys.stderr)
            return 2
        memory = f"{mid}@{int(rev)}"
        origins = [dict(x, memory=memory) if _origin_key(x) == _origin_key(o) else x
                   for x in e["origins"]]
        entries[e["classKey"]] = derive(origins)
        save(idx, entries)
    line = f"event: lessons — recorded {e['id']} as {memory} — {_now()}"
    _ledger_line(ledger, line)
    print(line)
    return 0


def cmd_show(a, idx: pathlib.Path) -> int:
    print(json.dumps(_resolve(load(idx), a.id), ensure_ascii=False, indent=1, sort_keys=True))
    return 0


def main(argv: list[str]) -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--index", help=f"the index file; default ${ENV_INDEX}, else "
                                        "~/.sshlg-skills/lessons/index.jsonl")
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
    c = sub.add_parser("candidates", parents=[common], help="lessons two or more projects hold")
    c.add_argument("--min-projects", type=int, default=2)
    sh = sub.add_parser("show", parents=[common], help="one entry with its origins")
    sh.add_argument("id")
    em = sub.add_parser("emit-observatory", parents=[common], help="the shared store's arguments")
    em.add_argument("id")
    em.add_argument("--tool", default="observatory_record",
                    choices=["observatory_record", "observatory_lesson"])
    em.add_argument("--project-id", help="the store's project id, e.g. project:<slug>")
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
    idx = index_path(a.index)
    if a.cmd == "path":
        print(idx)
        return 0
    verbs = {"add": cmd_add, "query": cmd_query, "rebuild": cmd_rebuild, "candidates": cmd_candidates,
             "show": cmd_show, "emit-observatory": cmd_emit, "record": cmd_record}
    try:
        return verbs[a.cmd](a, idx)
    except Refused as exc:
        print(f"lessons: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
