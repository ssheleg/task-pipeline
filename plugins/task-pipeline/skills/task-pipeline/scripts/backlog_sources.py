#!/usr/bin/env python3
"""The declared task sources a wave-0 harvest reads (`references/waves.md`, R13) — stdlib only.

Where a repository carries `docs/backlog-sources.json`, the harvest reads exactly the sources
it lists, with the id, title and status columns each one names, and a source of open work the
manifest does not list is a finding, not a silent addition. This script is the mechanical half
of that sentence: it reads the manifest, refuses one the harvest could not follow, and prints
the list the harvest works from.

    backlog_sources.py [--root DIR] [--found PATH ...]
    backlog_sources.py [--root DIR] --discover [--artifacts DIR]

The rule a user of this skill reads is the shipped schema template,
`templates/backlog-sources.schema.json` (backlog-sources/1), with `references/backlog.md` →
*A declared source list*; this checker enforces it, plus the two rules a schema cannot state
(a regular file reached through no symlink, no duplicate declaration). Fabric's
`knowledge/backlog.md` (its *Source contract* section, read on 2026-10-08) is its provenance: the template is compatible with it, with one deliberate
widening — `repository` may be any `https://github.com/<owner>/<repo>`, because this skill runs
outside one organisation.

- `schema` is 1; `repository` is a canonical GitHub URL; `sources` holds 1–100 entries.
- Each `path` is relative, inside the repository, with no hidden, `.` or `..` segment and no
  symlink on the way; it exists as a regular file — `.md`, or `.json` for `json-tasks`.
- `goal` is one of the five anchors; `kind` is `tasks` (the default) or `context`.
- A `tasks` source is `table`, `checklist` or `json-tasks`. A table names non-empty
  `idColumn` and `titleColumn` and exactly one of `statusColumn` or `defaultStatus: "open"`.
- `excludeIds` is a unique list of strings; `idPattern` is a literal prefix, optionally with
  `[0-9]+` or `\\d+`, anchored at both ends. Two identical declarations are refused.
- A key the schema does not name is refused, at the top and on a source; `heading` is a
  string; `idColumn`, `titleColumn`, `statusColumn`, `defaultStatus`, `excludeIds` and
  `idPattern` are checked on every
  source, whatever its kind. Where `jsonschema` is installed the shipped schema is applied too.

Output, on success: one JSON object — `repository`, `tasks` (each declaration as given, the
fields the harvest reads), `context` (paths), `undeclared` (each `--found` path the manifest
does not list, as `file:line`-free repository paths).

`--discover` answers the question stage 0 asks before it files anything: **where does this
project already keep its open work** (`references/intake-split.md` → *Find the board first*).
It collects candidates from four places, the instruction files' tracker rules beside them:

1. the manifest above, its `tasks` sources (a malformed manifest exits 1, as above);
2. a board file the instruction files (`CLAUDE.md`, `AGENTS.md`) name, when it exists in
   the repository; a file a filing rule negates ("do not file in docs/TODO.md", "no longer
   in", "docs/TODO.md is retired") is listed in `negated` and is no candidate from any pass,
   unless another line states it, the manifest declares it or agent-sync names it;
3. a board file `.claude/agent-sync.json` names in `idRegisters` or `claimTags`; an `outline`
   or `notion` backend is marked `remote`, because the local file is then a mirror;
4. the known paths, in `KNOWN` order.

A board file is one whose name, split on `-`, `_` and `.`, holds a word of `STRONG_WORDS`, or
whose stem is a board name (`TASKS.md`, `BUILD_ORDER.md`); a generic word (`build`, `tasks`,
`queue`) counts only on a line about tracking. `docs/specs/cloud-board.md`, `docs/build.md`
and `docs/onboarding.md` are not boards. The home is, strongest
first: the manifest's first source; a file an instruction clause about where work is tracked
names, a board before a roadmap; a tracker such a clause names and does not negate (Linear, Jira, GitHub issues, the
Fabric board: the file is then its funnel or mirror); the first file named `backlog`; the
first candidate. A roadmap or workstreams page stays a candidate (a queue), not the board.
A tracker mentioned on any other line is reported in `trackers` and never the home.

Plan folders and handoff pages are `weak` signals: input to the harvest, never the board.
Two board-named files with no manifest set `ambiguous` and print the finding that a manifest
should choose. A board whose own header says frozen or not canonical is `negated`. No home
but `signals` (a negated board, a tracked file named as a board elsewhere, an instruction line
about where work lives, a tracker named in any words, and always the instruction files
themselves, `READ_FIRST` plus the README in any case, a probed directory that could not be read,
an agent-sync config that could not be read, a manifest that could not be looked at, and a board
path the walk refuses: `too-deep`, `unwalked`, `agent-sync-register`): exit 5, `seed` null. A
manifest that could not be looked at, or such a board path, also stops a fallback home (a known
path or a candidate) being picked; a home the manifest, a stated rule or a stated tracker names
still stands, with a note on stderr. A tree with none of
those files and none of the above: `home` is null, `seed` is `<artifacts>/backlog.md`, exit 4.
`<artifacts>/backlog.md` itself is probed first among the known paths, wherever the root was
moved; anything at that path that is not walked as a board (a link out of the repository,
another letter case, a dangling link) is a `seed-path-taken` signal, never seeded over, and it
stops a fallback home unless it is the same file, under another letter case or a hard link, as
a board already found (a symbolic link to that board still stops it).
A path that leaves the repository or passes through a symlink is never a candidate.

Exit codes: 0 the manifest is readable and nothing undeclared was found, or there is no
manifest (discovery then, as `references/knowledge-sources.md` describes — printed, not
silent); 1 the manifest is malformed or cannot be looked at, every reason printed; 3 the manifest is fine and a
`--found` source is not in it — the finding the doctrine asks for; 4 (`--discover` only) the
project keeps no board, so the run seeds the printed `seed` path; 5 (`--discover` only) no home,
but `signals` to read before seeding (every kind is listed above, the instruction files always
among them); seed only when they name no live board.
"""
from __future__ import annotations

import argparse
import errno
import json
import os
import pathlib
import re
import subprocess
import sys

MANIFEST = "docs/backlog-sources.json"
SCHEMA = pathlib.Path(__file__).resolve().parents[1] / "templates" / "backlog-sources.schema.json"
TOP_KEYS = ("schema", "repository", "sources")
SOURCE_KEYS = ("path", "goal", "kind", "format", "heading", "idColumn", "titleColumn",
               "statusColumn", "defaultStatus", "idPattern", "excludeIds")
GOALS = ("agent-workplace", "workflow-control", "interoperability", "reliable-work", "shared-context")
FORMATS = ("table", "checklist", "json-tasks")
REPOSITORY = re.compile(r"^https://github\.com/[A-Za-z0-9][A-Za-z0-9-]{0,38}/\.?[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
ID_PATTERN = re.compile(r"^\^[A-Za-z0-9._/-]+(?:\[0-9\]\+|\\d\+)?\$$")
UNSAFE = re.compile(r"[\\\x00-\x1f\x7f?#%:]")


def _safe(path: object) -> bool:
    if not isinstance(path, str) or not path or len(path) > 700 or UNSAFE.search(path):
        return False
    if path.startswith("/"):
        return False
    return all(seg and seg not in (".", "..") and not seg.startswith(".") for seg in path.split("/"))


def _regular(root: pathlib.Path, path: str) -> bool:
    """The file exists and nothing on the way to it is a symlink."""
    cur = root
    for seg in path.split("/"):
        cur = cur / seg
        if os.path.islink(cur):
            return False
    return os.path.isfile(cur)


MAX_DEPTH = 64


def _too_deep(doc: object) -> bool:
    """Nesting deeper than MAX_DEPTH, measured without recursion: repr, jsonschema and json.dumps
    recurse, so a parsed document they would choke on is refused first."""
    stack = [(doc, 0)]
    while stack:
        v, depth = stack.pop()
        if isinstance(v, (dict, list)):
            depth += 1  # containers only: 64 nested lists holding a value are 64 levels
            if depth > MAX_DEPTH:
                return True
            stack += [(x, depth) for x in (v.values() if isinstance(v, dict) else v)]
    return False


def _nonempty(v: object) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _schema_errors(doc: dict) -> list[str]:
    """The shipped schema, applied when `jsonschema` is installed — the authority this
    checker hand-implements. Without the library the hand checks above stand alone, and
    they cover every rule the schema states."""
    try:
        import jsonschema
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    except (ImportError, OSError, ValueError):
        return []
    out = []
    for e in sorted(jsonschema.Draft202012Validator(schema).iter_errors(doc), key=lambda e: list(e.path)):
        where = "/".join(str(p) for p in e.path) or "(top)"
        out.append(f"{MANIFEST}: schema: {where}: {e.message[:200]}")
    return out


def _manifest(root: pathlib.Path) -> str | None:
    """The one presence test both modes use: None when there is no manifest (absent, a link
    loop or a dangling link: the errors pathlib's exists() swallowed, as 1.102.4 read them), ""
    when it is there, the error's name when something may be there that cannot be looked at (a
    docs/ without search permission, a path past the platform's limit)."""
    try:
        os.stat(root / MANIFEST)
        return ""
    except ValueError:
        return None
    except OSError as exc:
        if exc.errno in (errno.ENOENT, errno.ENOTDIR, errno.ELOOP, errno.EBADF):
            return None
        return type(exc).__name__


def check(root: pathlib.Path, found: list[str]) -> tuple[int, dict | None, list[str]]:
    """(exit code, the harvest list or None, reasons)."""
    mf = root / MANIFEST
    state = _manifest(root)
    if state is None:
        return 0, None, [f"no {MANIFEST} — the harvest discovers its sources"]
    if state:  # a manifest that cannot be looked at is not an absent one
        return 1, None, [f"{MANIFEST}: not readable ({state})"]
    try:
        doc = json.loads(mf.read_text(encoding="utf-8"))
    except (OSError, ValueError, RecursionError) as exc:
        return 1, None, [f"{MANIFEST}: not readable JSON ({type(exc).__name__})"]
    if _too_deep(doc):
        return 1, None, [f"{MANIFEST}: nested deeper than {MAX_DEPTH} levels"]
    if not isinstance(doc, dict):
        return 1, None, [f"{MANIFEST}: not an object"]
    errs: list[str] = []
    errs += [f"{MANIFEST}: unknown key `{k}` — backlog-sources/1 names {', '.join(TOP_KEYS)}"
             for k in doc if k not in TOP_KEYS]
    if doc.get("schema") != 1:
        errs.append(f"{MANIFEST}: `schema` is {doc.get('schema')!r}, not 1")
    if not REPOSITORY.match(str(doc.get("repository") or "")):
        errs.append(f"{MANIFEST}: `repository` {doc.get('repository')!r} is not a canonical "
                    "https://github.com/<owner>/<repo> URL")
    sources = doc.get("sources")
    if not isinstance(sources, list) or not 1 <= len(sources) <= 100:
        errs.append(f"{MANIFEST}: `sources` must list 1–100 entries — a context-only "
                    "repository still declares one")
        sources = sources if isinstance(sources, list) else []
    tasks, context, seen = [], [], set()
    for i, s in enumerate(sources):
        where = f"{MANIFEST}: sources[{i}]"
        if not isinstance(s, dict):
            errs.append(f"{where}: not an object")
            continue
        path, kind, fmt = s.get("path"), s.get("kind", "tasks"), s.get("format")
        where = f"{where} ({path})"
        errs += [f"{where}: unknown key `{k}` — a source names only {', '.join(SOURCE_KEYS)}"
                 for k in s if k not in SOURCE_KEYS]
        if "heading" in s and not isinstance(s["heading"], str):
            errs.append(f"{where}: `heading` is not a string")
        # These hold on EVERY source, whatever its kind or format: the schema says so, and
        # a rule checked only on a task table is a rule a context source can break.
        for col in ("idColumn", "titleColumn", "statusColumn"):
            if col in s and not _nonempty(s.get(col)):
                errs.append(f"{where}: `{col}` is empty")
        if "defaultStatus" in s and s.get("defaultStatus") != "open":
            errs.append(f"{where}: `defaultStatus` may only be \"open\"")
        ex = s.get("excludeIds")
        if ex is not None and (not isinstance(ex, list) or not all(_nonempty(x) for x in ex)
                               or len(set(ex)) != len(ex)):
            errs.append(f"{where}: `excludeIds` is a unique list of stable ids")
        if "idPattern" in s and not ID_PATTERN.match(str(s.get("idPattern"))):
            errs.append(f"{where}: `idPattern` {s.get('idPattern')!r} is not a literal "
                        "prefix with an optional [0-9]+, anchored at both ends")
        if kind not in ("tasks", "context"):
            errs.append(f"{where}: `kind` {kind!r} is neither tasks nor context")
        if s.get("goal") not in GOALS:
            errs.append(f"{where}: `goal` {s.get('goal')!r} is not one of {', '.join(GOALS)}")
        ext = ".json" if (kind == "tasks" and fmt == "json-tasks") else ".md"
        if not _safe(path) or not str(path).endswith(ext):
            errs.append(f"{where}: `path` must be a relative {ext} path with no hidden, `.` "
                        "or `..` segment")
        elif not _regular(root, path):
            errs.append(f"{where}: the declared source is missing, or reached through a symlink")
        if kind == "tasks":
            if fmt not in FORMATS:
                errs.append(f"{where}: `format` {fmt!r} is not one of {', '.join(FORMATS)} — "
                            "an unsupported source is migrated or declared as context")
            if fmt == "table":
                has_status, has_default = "statusColumn" in s, "defaultStatus" in s
                if not (_nonempty(s.get("idColumn")) and _nonempty(s.get("titleColumn"))):
                    errs.append(f"{where}: a table names non-empty `idColumn` and `titleColumn`")
                if has_status == has_default or (has_status and not _nonempty(s.get("statusColumn"))) \
                        or (has_default and s.get("defaultStatus") != "open"):
                    errs.append(f"{where}: a table names exactly one of a non-empty "
                                "`statusColumn` or `defaultStatus: \"open\"`")
        key = json.dumps([path, s.get("heading", ""), s.get("idPattern", ""), fmt or "",
                          s.get("idColumn", ""), s.get("titleColumn", ""),
                          s.get("statusColumn", ""), s.get("excludeIds", [])])
        if key in seen:
            errs.append(f"{where}: a duplicate declaration")
        seen.add(key)
        if kind == "tasks":
            tasks.append({k: s[k] for k in ("path", "format", "heading", "idColumn", "titleColumn",
                                             "statusColumn", "defaultStatus", "idPattern",
                                             "excludeIds") if k in s})
        elif isinstance(path, str):
            context.append(path)
    errs += _schema_errors(doc)
    if errs:
        return 1, None, list(dict.fromkeys(errs))
    declared = {t["path"] for t in tasks} | set(context)
    undeclared = sorted({f.strip().lstrip("./") for f in found if f.strip()} - declared)
    out = {"repository": doc["repository"], "tasks": tasks, "context": context,
           "undeclared": undeclared}
    return (3 if undeclared else 0), out, [f"finding: {u} holds open work and is not declared "
                                           f"in {MANIFEST}" for u in undeclared]


# Board-named files: two of these with no manifest is an ambiguity. The rest are queues a
# project keeps beside its board (a roadmap, workstreams, a remediation queue).
BOARDS = ("docs/evidence/backlog.md", "docs/backlog.md", "docs/superpowers/backlog.md",
          "BACKLOG.md", "docs/BACKLOG.md", "TODO.md", "docs/TASKS.md")
QUEUES = ("docs/WORKSTREAMS.md", "docs/BUILD_ORDER.md", "docs/ROADMAP.md", "docs/roadmap.md",
          "ROADMAP.md")
KNOWN = BOARDS + QUEUES
WEAK = ("docs/plans", "docs/superpowers/plans", "docs/OPEN_QUESTIONS.md", "docs/HANDOFF.md")
INSTRUCTIONS = ("CLAUDE.md", "AGENTS.md")
# A file is a board by its name: a strong word anywhere in it, or a whole stem a board is
# called. The generic words (`docs/build.md`, `celery-tasks.md`, `architecture/queue.md`) make a
# board only when the instruction line says that is where work is tracked.
STRONG_WORDS = ("backlog", "roadmap", "workstreams", "todo")
BOARD_STEMS = ("tasks", "build_order", "backlog", "roadmap", "workstreams", "todo")
WEAK_WORDS = ("tasks", "queue", "build", "order")
PATH_IN_TEXT = re.compile(r"(?<![\w/.-])((?:\./)?(?:\.\./|[\w-]+/)*[\w.-]+\.md)\b")
I = re.IGNORECASE
TRACKERS = (("Linear", re.compile(r"(?-i:\bLinear\b)|linear\.app|\b(?:in|on|to|via|into)\s+linear\b"
                                  r"(?!\s+(?:time|history|order|scan|algebra|search|regression))", I)),
            ("Jira", re.compile(r"\bJira\b", I)),
            ("GitHub issues", re.compile(r"\bGitHub issues?\b|\bgh issue\b|github\.com/[\w.-]+/[\w.-]+/issues|"
                                         r"\bissues\b[^.;|]{0,30}\bon GitHub\b", I)),
            ("Trello", re.compile(r"\bTrello\b", I)), ("Notion", re.compile(r"\bNotion\b", I)),
            ("YouTrack", re.compile(r"\bYouTrack\b", I)), ("Asana", re.compile(r"\bAsana\b", I)),
            ("ClickUp", re.compile(r"\bClickUp\b", I)), ("GitLab issues", re.compile(r"\bGitLab issues?\b|gitlab\.com/\S+/issues|\bglab issue\b|"
                                                       r"\bissues\b[^.;|]{0,30}\bon GitLab\b", I)),
            ("Redmine", re.compile(r"\bRedmine\b", I)), ("Azure DevOps", re.compile(r"\bAzure Boards\b|\bAzure DevOps work items?\b|"
                                                     r"\bwork items?\b[^.;|]{0,30}\bAzure DevOps\b", I)),
            ("Shortcut", re.compile(r"\bShortcut\b(?= (?:story|stories|ticket|board|issue))|app\.shortcut\.com", I)),
            ("Monday", re.compile(r"\bmonday\.com\b", I)), ("Basecamp", re.compile(r"\b(?:to-?dos?|tasks?)\b[^.;|]{0,30}\bBasecamp\b|\bBasecamp to-?dos?\b", I)),
            ("Fabric board", re.compile(r"\bFabric board\b|\bfabric_task|\bcom\.submit\b")))
# "not Linear", "do not use Linear", "не в Linear", "do not file in docs/TODO.md" negate;
# "does not replace Linear" does not: only these few words may sit between.
NEGATION = re.compile(r"(?:\bnot|n't|\bno|\bnever|\bwithout|\bне|\bбез|\bбольше не)\W+"
                      r"(?:(?:use|using|file|keep|track|longer|in|into|via|on|through|в|во|через)"
                      r"\W+){0,3}$", re.IGNORECASE)
# A path is negated only by a filing rule, never by prose that happens to hold "no":
# "not in X", "do not file in X", "don't file in X", "no longer in X", "не в X", "больше не в X"
# before it; "X is retired", "X was deprecated", "X (deprecated)" after it. "If there is no X",
# "without X", "X: archived rows are struck through" negate nothing. A rule with a qualifier
# after the path ("X directly", "X without a claim", "X by hand") says HOW to file there.
PATH_NEGATION = re.compile(r"(?:\bnot|n't|\bnever|\bno longer|\bне|\bбольше не)\W+"
                           r"(?:(?:file|track|keep|use|write|put|add|записывай|пиши|веди)\W+)?"
                           r"(?:in|into|to|в|во)\W*$", re.IGNORECASE)
RETIRED = re.compile(r"^[`\])\"']*(?:\s+(?:is|was)\s+(?:now\s+)?(?:retired|deprecated|obsolete)\b|"
                     r"\s+(?:is|was)\s+no longer\s+(?:tracked|used|maintained|kept)\b|"
                     r"\s+(?:is|was|has been)\s+(?:replaced|superseded)\b|"
                     r"\s*\((?:retired|deprecated|obsolete|устарел)\)|\s+устарел|"
                     r"\s+больше не (?:используется|ведётся|ведется))", re.IGNORECASE)
QUALIFIED = re.compile(r"^[`\])\"']*\s+(?:directly|without|by hand|manually|напрямую|вручную|без)\b",
                       re.IGNORECASE)
REMOTE_BACKENDS = ("outline", "notion")
# Words that say where work is tracked. They count only in the path's or the tracker's own
# clause (cut at `;`, `|`, a sentence end) and within NEAR characters, every path blanked: a
# line that mentions `tasks` in one clause and a roadmap in another states nothing about either.
TRACKING = re.compile(r"backlog|бэклог|реестр\w* (?:\w+ )?задач|task register|task status|\btrack(?:s|ed|ing|er)?\b|трекер|source of truth|"
                      r"open work|open rows|\bfiled\b|where work|записыва|занос|воронк|"
                      r"очередь задач|задачи вед|задачи живут", re.IGNORECASE)
NEAR = 80
# A tracking word is unsaid only where a negation governs it: "no longer tracked in X", "don't
# track work in X", "stopped tracking in X", "больше не записываем в X", "moved from X", and the
# object of an active replacement ("which replaced X"). A "not" elsewhere in the clause ("not
# finished today is tracked in X", "don't block a release are tracked in X") says nothing.
UNSAID_BEFORE = re.compile(r"(?:\bnot|n't|\bnever|\bno longer|\bstopped|\bбольше не|\bне)\W+"
                           r"(?:\w+\W+){0,2}?(?:track\w*|file[ds]?|filing|keep|kept|записыва\w*|"
                           r"вед[её]\w*)\b|\bfrom\W*$|\b(?:replaced|superseded)\W+(?:the\s+)?"
                           r"(?:old\s+)?\W*$", re.IGNORECASE)
# After the path, only the passive retires it: "X was replaced", "X is no longer used",
# "X (the old backlog)". "X, which replaced Y" retires Y, not X.
UNSAID_AFTER = re.compile(r"^[`\])\"']*\s*(?:is|was|are|were|has been|have been)\s+(?:now\s+)?"
                          r"(?:no longer|replaced|superseded|retired|deprecated|obsolete)\b|"
                          r"^[`\])\"']*\s+(?:больше не|устарел|заменён|заменен)|"
                          r"^[`\])\"']*\s*\(\s*(?:the\s+)?(?:old|former|previous|legacy|прежний|старый)\b",
                          re.IGNORECASE)
CLAUSE = re.compile(r"[;|]|(?<!\be\.g)(?<!\bi\.e)(?<!\betc)[.!?](?:\s|\*|$)")


def _blank(line: str) -> str:
    """Every path blanked: `BACKLOG.md` beside `ROADMAP.md` names a file, it does not say the
    roadmap is where work is tracked. Computed once per line, not once per mention."""
    return PATH_IN_TEXT.sub(lambda m: " " * len(m.group(0)), line)


def _stated(line: str, start: int, end: int, bare: str | None = None) -> bool:
    bare = _blank(line) if bare is None else bare
    before = CLAUSE.split(bare[max(0, start - NEAR):start])[-1]
    after = CLAUSE.split(bare[end:end + NEAR])[0]
    # "no longer tracked in X", "stopped tracking in X", "moved from X to", "X was replaced":
    # a tracking word in a negated clause states the opposite.
    if UNSAID_BEFORE.search(before) or UNSAID_AFTER.search(after):
        return False
    return bool(TRACKING.search(before + " \n " + after))


def _board_file(path: str, stated: bool = False) -> bool:
    stem = path.rsplit("/", 1)[-1].lower().removesuffix(".md")
    words = re.split(r"[-_.]", stem)
    if stem in BOARD_STEMS or any(w in STRONG_WORDS for w in words):
        return True
    if "remediation" in words and "queue" in words:
        return True
    return stated and any(w in WEAK_WORDS for w in words)


def _queue(path: str) -> bool:
    """A roadmap, workstreams or build-order page: a queue beside the board, not the board."""
    words = re.split(r"[-_.]", path.rsplit("/", 1)[-1].lower().removesuffix(".md"))
    return any(w in ("roadmap", "workstreams", "build", "order") for w in words)


_LISTING: dict[str, frozenset] = {}  # one listing per directory per run (blind reading, round 22)
_LINK: dict[str, bool] = {}  # one lstat per prefix per run (blind reading, round 23)
# A path of more segments than this (MAX_SEGMENTS slashes or more) is not walked: the deepest home among the operator's 156
# repositories sits 3 directories down, and each segment costs a listing and an lstat (blind reading, round 23).
MAX_SEGMENTS = 16


def _names(d) -> frozenset:
    key = os.fspath(d)
    if key not in _LISTING:
        try:
            _LISTING[key] = frozenset(os.listdir(key))
        except OSError:
            _LISTING[key] = frozenset()
    return _LISTING[key]


def _link(key: str) -> bool:
    if key not in _LINK:
        _LINK[key] = os.path.islink(key)
    return _LINK[key]


def _present(root: pathlib.Path, path: str) -> bool:
    """A regular file under its exact name, nothing on the way a symlink. On a case-insensitive
    disk (macOS, Windows) `docs/BACKLOG.md` opens `docs/backlog.md`, and one board would read
    as two. Each prefix is listed and checked once per run, so shared prefixes cost nothing, and
    a path of more than MAX_SEGMENTS segments is never walked, wherever it was named."""
    if path.count("/") >= MAX_SEGMENTS:
        return False
    cur = os.fspath(root)
    for seg in path.split("/"):
        if seg not in _names(cur):
            return False
        cur = os.path.join(cur, seg)
        if _link(cur):
            return False
    return os.path.isfile(cur)


def _unwalkable(root: pathlib.Path, path: object) -> bool:
    """A path inside the repository by its spelling that this script will not walk although
    something may be there: too deep (never looked at), or on disk but hidden, over 700
    characters or reached through a symlink. Such a board is a signal, never silently dropped."""
    if not isinstance(path, str) or not path or path.startswith("/") or "\x00" in path \
            or any(seg == ".." for seg in path.split("/")):
        return False
    if path.count("/") >= MAX_SEGMENTS:
        return True
    cur = os.fspath(root)
    for seg in path.split("/"):  # by exact name: on a case-insensitive disk BACKLOG.md is not backlog.md
        if seg not in _names(cur):
            return False
        cur = os.path.join(cur, seg)
    return _inside(root, path)  # a link out of the repository is not this project's board


def _has_md(d: pathlib.Path) -> bool:
    try:
        return os.path.isdir(d) and any(n.endswith(".md") for n in os.listdir(d))
    except OSError:
        return False


def _no_link(root: pathlib.Path, path: str) -> bool:
    """No segment on the way to `path` is a symlink (a directory too, unlike `_regular`)."""
    cur = root
    for seg in path.split("/"):
        cur = cur / seg
        if os.path.islink(cur):
            return False
    return True


def _remediation(root: pathlib.Path) -> list[str]:
    audits = root / "docs" / "audits"
    if not _no_link(root, "docs/audits") or not os.path.isdir(audits):
        return []
    try:
        names = os.listdir(audits)
    except OSError:
        return []
    return sorted(f"docs/audits/{n}" for n in names if n.endswith("-remediation-queue.md")
                  and _present(root, f"docs/audits/{n}"))


# The longest instruction line on the operator's machine is about 8 KB and the largest file far
# under 1 MB; a bound keeps a pathological file from costing minutes (blind reading, round 21).
MAX_INSTRUCTION_BYTES = 1_000_000
READ_FIRST = ("CLAUDE.md", "AGENTS.md", ".claude/CLAUDE.md", ".github/copilot-instructions.md")


def _inside(root: pathlib.Path, path: str) -> bool:
    """`path` resolves to a regular file inside the repository. os.path.realpath never raises on
    a symlink loop (pathlib's resolve() does, on Python 3.9-3.12)."""
    real_root = os.path.realpath(root)
    target = os.path.realpath(root / path)
    return (target == real_root or target.startswith(real_root + os.sep)) and os.path.isfile(target)


def _instruction_files(root: pathlib.Path) -> list[str]:
    """The files a run reads before seeding, under their real names: every READ_FIRST entry that
    exists at all (a symlink out of the repository, dangling or looping included, since the agent
    host still loads it as the project's instructions; only listed, never read here) and the
    README in any case."""
    out = []
    try:
        top = {n.lower(): n for n in os.listdir(root)}
    except OSError:
        top = {}
    for name in READ_FIRST:
        if "/" in name:
            parent, leaf = name.rsplit("/", 1)
            try:
                found = [n for n in os.listdir(root / parent) if n.lower() == leaf.lower()]
            except OSError:
                found = [leaf] if os.path.lexists(root / name) else []
            out += [f"{parent}/{n}" for n in found]
        elif name.lower() in top:
            out.append(top[name.lower()])
    out += sorted(n for low, n in top.items()
                  if low == "readme" or low.startswith(("readme.", "readme-", "readme_")))
    return out


def _instruction_lines(root: pathlib.Path, notes: list[str]) -> list[tuple[str, int, str]]:
    out = []
    for name in INSTRUCTIONS:
        if not os.path.lexists(root / name):
            continue
        if not (_regular(root, name) or _inside(root, name)):
            notes.append(f"{name}: not a regular file inside the repository, its rules were not read")
            continue
        try:
            with open(root / name, "rb") as fh:
                raw = fh.read(MAX_INSTRUCTION_BYTES + 1)
        except OSError as exc:
            notes.append(f"{name}: not readable ({type(exc).__name__}), its rules were not read")
            continue
        if len(raw) > MAX_INSTRUCTION_BYTES:
            notes.append(f"{name}: larger than {MAX_INSTRUCTION_BYTES} bytes, only the first part was read")
            raw = raw[:MAX_INSTRUCTION_BYTES]
        lines = raw.decode("utf-8", errors="replace").splitlines()
        out += [(name, n, line) for n, line in enumerate(lines[:4000], 1)]
    return out


def _agent_sync(root: pathlib.Path, notes: list[str]) -> dict | None:
    rel = ".claude/agent-sync.json"
    cfg = root / rel
    if not os.path.lexists(cfg):
        return None
    if os.path.islink(cfg) or os.path.islink(root / ".claude") or not os.path.isfile(cfg):
        notes.append(f"{rel}: not a regular file, skipped")
        return None
    try:
        doc = json.loads(cfg.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            raise ValueError("not an object")
        if _too_deep(doc):
            raise ValueError("nested too deeply")
    except (OSError, ValueError, RecursionError) as exc:
        notes.append(f"{rel}: not readable ({type(exc).__name__}), skipped")
        return None
    named = []
    for key in ("idRegisters", "claimTags"):
        if key in doc and not isinstance(doc[key], dict):
            notes.append(f"{rel}: `{key}` is not an object, skipped")
    regs = doc.get("idRegisters") if isinstance(doc.get("idRegisters"), dict) else {}
    named += [r.get("file") for r in regs.values() if isinstance(r, dict)]
    tags = doc.get("claimTags") if isinstance(doc.get("claimTags"), dict) else {}
    named += list(tags)
    files, deep = [], []
    for f in named:
        if not (isinstance(f, str) and _board_file(f)) or f in files or f in deep:
            continue
        if _safe(f) and _present(root, f):
            files.append(f)
        elif len(deep) < 20 and not f.startswith("/") and ".." not in f.split("/") and "\x00" not in f:
            deep.append(f)  # declared here and not walkable or absent: a signal, never a silent seed
    backend = doc.get("backend") if isinstance(doc.get("backend"), str) else None
    return {"backend": backend, "remote": backend in REMOTE_BACKENDS, "files": files, "deep": deep}


# A board whose own header says it is frozen or not canonical is not the home: its first lines
# are the project's word on it (project-observatory's docs/BACKLOG.md, 2026-11-06).
FROZEN_HEAD = re.compile(r"non-canonical|not canonical|неканонич|не канонич|"
                         r"(?:frozen|заморожен\w*)\W+(?:as of\W+|since\W+|on\W+|с\W+)?\d{4}-\d\d-\d\d",
                         re.IGNORECASE)
BOARD_NOUN = re.compile(r"backlog|бэклог|\bboard\b|доск|реестр|register", re.IGNORECASE)
# A clause that says where WORK is kept (not decisions, not "the source of truth" for a spec).
# A work noun in the path's own clause: "Open defects live in X", "Tasks live in X", "the task
# list is X". A verb alone ("Build steps live in docs/build.md") names no place of work.
WORK_CLAUSE = re.compile(r"open work|\btasks?\b|task list|work items?|open (?:defects|issues|items|bugs)|"
                         r"\bgoes to\b|\badd (?:it|them) to\b|\bfile (?:it|them) in\b|deferred|future work|"
                         r"remaining work|next steps|следующие шаги|\bbacklog|бэклог|задач|\bregister\b|реестр",
                         re.IGNORECASE)
# Only phrases that redefine the work noun itself veto it ("user jobs" is UX, not open work).
NOT_WORK = re.compile(r"задачи пользовател|user jobs|jobs to be done", re.IGNORECASE)
# Where the work goes, said with a placement verb or a pointer elsewhere: "goes to X", "add it to
# X", "kept in the data folder", "deferred", "не здесь, а в ssheleg/underline".
# Work nouns beside a place: tickets, issues, bugs, to-dos, known issues, planned or pending work,
# an issue-key template ("ESM-<number>", "NCG-XXXXX"). A ranking aid for the reader; exit 5 does
# not depend on it (see discover()).
WORK_NOUN = re.compile(r"\btasks? (?:live|lives|are kept|are in|go)\b|\btickets?\b|тикет|\bissues?\b|\bbugs?\b|\bto-?dos?\b|known issues|"
                       r"(?:planned|pending|deferred|next) (?:work|items)|work items?|планы работ|"
                       r"(?-i:\b(?!(?:UTF|SHA|ISO|RFC|AES|TLS|SSL|HTTP|CVE|IPV|MD|ES|PEP|CWE|OWASP)-)[A-Z]{2,10}-(?:\d{3,}|<number>|<n>|NNN+|X{3,}|\\d\+))", re.IGNORECASE)
FILING = re.compile(r"\bgoes to\b|\badd (?:it|them) to\b|\bfile (?:it|them) in\b|\bkept in\b|deferred|"
                    r"future work|отложенн|хран\w+ в|складыва", re.IGNORECASE)
ELSEWHERE = re.compile(r"\bnot here\b|не здесь|\bin the [\w./-]+ repo(?:sitory)?\b|в репозитории|"
                       r"\bsibling (?:repo|folder|repository)\b|instance folder|data folder|папк\w+ данных",
                       re.IGNORECASE)
# Instruction and handoff pages are read anyway; naming one is never a board signal.
NOT_BOARD_FILES = ("claude.md", "agents.md", "readme.md", "handoff.md")
REPORT_HEAD = re.compile(r"^type:\s*report\b", re.IGNORECASE | re.MULTILINE)


def _head(root: pathlib.Path, path: str) -> list[str]:
    """The header: up to 15 lines, stopping at the first table row. A row is a task ("mark the
    page non-canonical"), not the board speaking about itself."""
    out = []
    try:
        with (root / path).open(encoding="utf-8", errors="replace") as fh:
            for _ in range(15):
                line = fh.readline()
                if not line or line.lstrip().startswith("|"):
                    break
                out.append(line)
    except OSError:
        return []
    return out


def _frozen(root: pathlib.Path, path: str) -> bool:
    # The freeze belongs to this file unless another path stands before it in the same clause
    # ("Replaces docs/TODO.md, frozen on 2026-09-01"). "Frozen 2026-09-01: open work moved to
    # ../x/backlog.md" and "docs/backlog.md is frozen since ..." freeze this file. When unsure,
    # frozen: a wrong exit 5 is cheap, a wrong exit 0 files into a dead board.
    me = path.rsplit("/", 1)[-1]
    for h in _head(root, path):
        f = FROZEN_HEAD.search(h)
        if not f:
            continue
        owner = None
        for m in PATH_IN_TEXT.finditer(h[:f.start()]):
            if not CLAUSE.search(h[m.end():f.start()]):
                owner = m.group(1)
        if owner is None or owner.rsplit("/", 1)[-1] == me:
            return True
    return False


def _tracked_backlogs(root: pathlib.Path, notes: list[str]) -> list[str]:
    """Tracked `.md` files named as a board (backlog, todo, tasks, roadmap...) anywhere in the tree: not a home (a report may be
    called that), but a reason not to seed blindly (usa-immigration, cmo-creative-agent)."""
    try:
        r = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--", "*.md"],
                           capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        notes.append(f"git ls-files did not answer ({type(exc).__name__}): tracked backlog files not listed")
        return []
    if r.returncode != 0:
        why = r.stderr.decode("utf-8", "replace").strip().splitlines()[:1]
        if why and "not a git repository" not in why[0]:
            notes.append(f"git ls-files failed ({why[0][:160]}): tracked backlog files not listed")
        return []
    named = sorted({f for f in r.stdout.decode("utf-8", "replace").split("\0")
                   if f and ("backlog" in f.rsplit("/", 1)[-1].lower() or _board_file(f))
                   and "{report}" not in f.rsplit("/", 1)[-1].lower()})  # a conflict lists one file per stage
    out = []
    walked = 0
    for f in named:  # cheap name filter first, the file checks only until 20 are kept
        if len(out) == 20:
            break
        if not _safe(f) or f.count("/") >= MAX_SEGMENTS:
            out.append(f)  # git tracks it; hidden, long or too deep to walk: a signal unread
            continue
        walked += 1
        if walked > 200:  # past the budget a name is a signal unread, never a reason to seed
            out.append(f)
            continue
        if not _present(root, f):
            if _unwalkable(root, f):
                out.append(f)  # a tracked link: a signal unread
            continue
        if REPORT_HEAD.search("".join(_head(root, f))):
            continue  # a closed report that happens to say backlog in its title
        out.append(f)
    return out


def discover(root: pathlib.Path, artifacts: str) -> tuple[int, dict | None, list[str]]:
    """(exit code, where the project keeps its open work, notes)."""
    _LISTING.clear()
    _LINK.clear()
    notes: list[str] = []
    candidates: list[dict] = []

    stated: set[str] = set()
    negated: list[str] = []
    negset: set[str] = set()  # membership in O(1); the list keeps the output order
    seen_paths: set[str] = set()

    def negate(path: str) -> None:
        if path not in negset:
            negset.add(path)
            negated.append(path)

    def add(path: str, via: str, evidence: str) -> None:
        if path in negset or path in seen_paths:
            return
        if via != "manifest" and _frozen(root, path):
            negate(path)
            notes.append(f"{path}: its header says frozen or not canonical; not the home")
            return
        candidates.append({"path": path, "via": via, "evidence": evidence})
        seen_paths.add(path)

    unread_manifest = _manifest(root)
    if unread_manifest:  # declared sources this run cannot read: no home is guessed past them
        notes.append(f"{MANIFEST}: not readable ({unread_manifest}); its declared sources are unknown")
    if unread_manifest == "":
        code, harvest, reasons = check(root, [])
        if code == 1:
            return 1, None, reasons
        for t in (harvest or {}).get("tasks", []):
            add(t["path"], "manifest", MANIFEST)
    lines = _instruction_lines(root, notes)
    sync = _agent_sync(root, notes)
    # One pass reads every mention: negated here, or stated here. A path some line states
    # positively, the manifest declares or agent-sync names is never negated by another line;
    # a negated board with nothing else is a signal (exit 5), never a silent seed.
    mentions = []
    for name, n, line in lines:
        bare = None
        for m in PATH_IN_TEXT.finditer(line):
            bare = _blank(line) if bare is None else bare
            path = m.group(1).removeprefix("./")
            tail = line[m.end():m.end() + 60]
            head = line[max(0, m.start() - NEAR):m.start()].rstrip("`[(\"'")
            neg = bool(PATH_NEGATION.search(head) or RETIRED.search(tail)) and not QUALIFIED.search(tail)
            clause = CLAUSE.split(bare[max(0, m.start() - NEAR):m.start()])[-1] + " " \
                + CLAUSE.split(bare[m.end():m.end() + NEAR])[0]
            work = bool(WORK_CLAUSE.search(clause)) and not NOT_WORK.search(clause)
            mentions.append((name, n, path, neg, not neg and _stated(line, m.start(), m.end(), bare), work))
    kept = {c["path"] for c in candidates} | set((sync or {}).get("files", [])) \
        | {path for _, _, path, neg, said, _ in mentions if said}
    for _, _, path, neg, _, _ in mentions:
        if neg and path not in kept:
            negate(path)
    stated_files = []
    stated_seen: set[str] = set()
    present: dict[str, bool] = {}

    def here(path: str) -> bool:
        if path not in present:
            present[path] = _safe(path) and _present(root, path)
        return present[path]

    # A board a line or agent-sync names past MAX_SEGMENTS: not walked, never outranked by a guess.
    deep = [{"kind": "too-deep" if f.count("/") >= MAX_SEGMENTS else "agent-sync-register", "path": f,
             "where": ".claude/agent-sync.json"}
            for f in (sync or {}).pop("deep", [])]  # the printed agentSync keeps its shape
    deep_seen = {d["path"] for d in deep}
    for name, n, path, neg, said, work in mentions:
        if not neg and path not in negset and len(deep) < 40 and _board_file(path, said) \
                and path not in deep_seen and not here(path) and _unwalkable(root, path):
            deep_seen.add(path)
            deep.append({"kind": "too-deep" if path.count("/") >= MAX_SEGMENTS else "unwalked",
                         "path": path, "where": f"{name}:{n}"})
        # A file the path's own clause calls the place of work ("Open defects live in X",
        # "Tasks live in X", "the task list is X") is a signal even with no tracking word.
        if work and not neg and path not in negset and path not in stated_seen \
                and path.rsplit("/", 1)[-1].lower() not in NOT_BOARD_FILES \
                and not _board_file(path, said) and here(path):
            stated_files.append({"kind": "stated-file", "path": path, "where": f"{name}:{n}"})
            stated_seen.add(path)
        if neg or path in negset or not (_board_file(path, said) and here(path)):
            continue
        add(path, "instruction", f"{name}:{n}")
        if said:
            stated.add(path)
    for f in (sync or {}).get("files", []):
        add(f, "agent-sync", ".claude/agent-sync.json")
    # The run's own board first: `<artifacts>/backlog.md` is where earlier runs of this pipeline
    # kept it, wherever `paths.artifacts` put the root (`.pipeline`, `docs/runs`), as 1.102.4
    # read it. Exact name, nothing on the way a link; a hidden root is allowed here.
    own = f"{artifacts}/backlog.md"
    own_full = os.path.join(os.fspath(root), artifacts, "backlog.md")
    try:
        own_there = os.path.lexists(own_full)
    except (OSError, ValueError):
        own_there = False
    for path in [own] + list(KNOWN) + _remediation(root):
        if path == own and path.count("/") >= MAX_SEGMENTS and not own_there:
            continue  # a deep root with nothing there is where the seed goes, not a signal
        if _present(root, path):
            add(path, "known-path", path)
        elif path not in deep_seen and path not in negset and _unwalkable(root, path):
            deep_seen.add(path)
            deep.append({"kind": "seed-path-taken" if path == own else "unwalked",
                         "path": path, "where": "known path"})  # a link, say
    # Something sits at the run's own board path that is neither walked nor a link inside the
    # repository: a link out (a board kept in a sibling data repository) or another letter case
    # on a case-insensitive disk. 1.102.4 read it; here it is a signal that stops a fallback home,
    # unless it is the same file as a board already found.
    if own_there and own not in seen_paths and own not in deep_seen:  # a frozen own board too: read it
        same = False
        for c in candidates:
            try:
                same = same or os.path.samefile(own_full, os.path.join(os.fspath(root), c["path"]))
            except (OSError, ValueError):
                pass
        if not same:
            deep_seen.add(own)
            deep.append({"kind": "seed-path-taken", "path": own, "where": "known path"})
    trackers = []
    unresolved = []
    named_lines = {(name, n) for name, n, path, neg, said, _ in mentions if path in seen_paths}
    for name, n, line in lines:
        bare = None
        # Wide on purpose (exit 5 is cheap, a blind seed is not): any line about where work is
        # tracked, a board noun, a placement verb or a pointer to another repository or folder.
        if (name, n) not in named_lines and not any(rx.search(line) for _, rx in TRACKERS) \
                and (TRACKING.search(line) or BOARD_NOUN.search(line) or FILING.search(line)
                     or ELSEWHERE.search(line) or WORK_NOUN.search(line)) and len(unresolved) < 20:
            unresolved.append(f"{name}:{n}")
        for tracker, rx in TRACKERS:
            hits = list(rx.finditer(line))
            if hits:
                # "not Linear" negates; "does not replace Linear" does not. A line that both
                # names and negates a tracker counts as naming it.
                # Negation is read in a bounded window before each hit (the first 200 per line),
                # and the line is blanked once, so a long line stays linear.
                bare = _blank(line) if bare is None else bare
                live = [h for h in hits[:200]
                        if not NEGATION.search(line[max(0, h.start() - NEAR):h.start()])]
                all_neg = not live
                said = any(_stated(line, h.start(), h.end(), bare) for h in live)
                trackers.append({"name": tracker, "negated": all_neg, "where": f"{name}:{n}",
                                 "stated": said})
    weak = [w for w in WEAK if _no_link(root, w)
            and (_has_md(root / w) or _present(root, w))]
    boards = [c["path"] for c in candidates if c["path"] in BOARDS]
    manifest = any(c["via"] == "manifest" for c in candidates)
    ambiguous = len(boards) > 1 and not manifest
    if ambiguous:
        notes.append(f"finding: {len(boards)} boards ({', '.join(boards)}) and no {MANIFEST}; "
                     "declare the sources in a manifest so the next run reads, not guesses")
    # The home, strongest first: the manifest; a file an instruction clause about tracking
    # names (a board before a queue); a tracker such a clause names; a file named backlog; any
    # candidate. A roadmap or workstreams page found earlier stays a candidate (a queue).
    by_manifest = [c for c in candidates if c["via"] == "manifest"]
    by_rule = sorted((c for c in candidates if c["path"] in stated), key=lambda c: _queue(c["path"]))
    named = [c for c in candidates if "backlog" in c["path"].rsplit("/", 1)[-1].lower()]
    tracker = next((t for t in trackers if t["stated"]), None)
    by_tracker = [{"path": None, "via": "tracker", "tracker": tracker["name"],
                   "evidence": tracker["where"]}] if tracker else []
    pick = by_manifest or by_rule or by_tracker or named or candidates
    if (deep or unread_manifest) and not (by_manifest or by_rule or by_tracker):
        pick = []  # a board the instructions name, too deep to walk, outranks any file found here
    if pick is candidates and all(_queue(c["path"]) for c in candidates) \
            and any(p in BOARDS or "backlog" in p.lower() for p in negated):
        pick = []  # the board is frozen; a roadmap beside it is no home by default
    home: dict | None = dict(pick[0]) if pick else None
    # No home is not yet "no board". A frozen or negated board, a tracked file named as a board
    # elsewhere in the tree, or an instruction line about the board that names no file here
    # (a board in a sibling data folder) is a signal: exit 5, read them before seeding.
    signals = []
    if home is None:
        signals += [{"kind": "negated", "path": p} for p in negated]
        if unread_manifest:
            signals.append({"kind": "unreadable", "path": MANIFEST})
        signals += deep
        signals += [{"kind": "tracked-file", "path": p} for p in _tracked_backlogs(root, notes)
                    if p not in negset]
        if sync is None and os.path.lexists(root / ".claude/agent-sync.json"):
            signals.append({"kind": "unreadable", "path": ".claude/agent-sync.json"})
        for dname in dict.fromkeys(("docs", ".claude", "docs/evidence", "docs/superpowers", "docs/audits", artifacts)):
            dpath = root / dname
            if os.path.isdir(dpath) and not os.access(dpath, os.R_OK | os.X_OK):
                notes.append(f"{dname}/: not readable, a board inside it could not be looked for")
                signals.append({"kind": "unreadable", "path": dname})
        cited = {sf["where"] for sf in stated_files}
        signals += [{"kind": "instruction-line", "where": w} for w in unresolved if w not in cited]
        signals += stated_files[:20]
        # A tracker named without a tracking word ("Tasks live in Linear", "Use GitHub issues
        # for bugs") is still where work may live. The Fabric board counts only when stated:
        # its com.submit lines are asks to other projects, not this project's board.
        seen = set()
        for t in trackers:
            if not t["negated"] and t["name"] not in seen and (t["name"] != "Fabric board" or t["stated"]):
                seen.add(t["name"])
                signals.append({"kind": "tracker", "name": t["name"], "where": t["where"]})
        # The rule, not the lists above, is what keeps a board from being seeded twice: a
        # project that wrote instructions is read before anything is seeded. The lines above
        # rank what to read first; a vocabulary can never be complete (ten blind readings
        # kept finding phrasings it missed), the project's own words always are.
        for name in _instruction_files(root):
            signals.append({"kind": "instructions", "path": name})
    taken = {"kind": "seed-path-taken", "path": own, "where": "known path"}
    if not home and own_there and taken not in signals:  # whichever pass saw the path first
        # The run's own board was found but something else stopped it being the home: the
        # seed path is taken all the same, and never written over.
        signals.append(taken)
    seed = None if home or signals else f"{artifacts}/backlog.md"
    if seed:
        notes.append(f"no board found: seed {seed} from templates/backlog.md")
    elif signals:
        notes.append(f"no home, {len(signals)} signal(s): read them before seeding anything")
    out = {"home": home, "candidates": candidates, "trackers": trackers, "agentSync": sync,
           "weak": weak, "ambiguous": ambiguous, "seed": seed, "negated": negated,
           "signals": signals}
    return (0 if home else 5 if signals else 4), out, notes


def _tolerant_streams() -> None:
    """A file name that is not UTF-8 (a Latin-1 name in a Linux checkout) reaches the notes as a
    lone surrogate; a strict stderr would crash on it. The JSON on stdout is ASCII-escaped."""
    for stream in (sys.stdout, sys.stderr):
        # Only a strict stream: a surrogateescape one (LC_ALL=C, C.UTF-8) already writes the raw
        # bytes, and changing it would change the plain CLI's output.
        try:
            if getattr(stream, "errors", None) == "strict":
                stream.reconfigure(errors="backslashreplace")
        except (AttributeError, ValueError):
            pass


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="backlog_sources.py",
                                description="The declared task sources a wave-0 harvest reads.")
    p.add_argument("--root", default=".", help="the repository root (default: .)")
    p.add_argument("--found", nargs="*", default=[],
                   help="sources of open work discovery found, as repository paths")
    p.add_argument("--discover", action="store_true",
                   help="find where the project already keeps its open work")
    p.add_argument("--artifacts", default="docs/evidence",
                   help="the artifact root, for the seed path (default: docs/evidence)")
    a = p.parse_args(argv)
    if a.discover:
        art = a.artifacts.removeprefix("./").rstrip("/")
        if not art or art.startswith(("/", "~")) or "\\" in art or re.search(r"\s", art) \
                or any(seg in ("", ".", "..") for seg in art.split("/")):
            p.error("--artifacts must be a relative path inside the repository")
        if a.found:
            p.error("--found is for a manifest check; --discover takes no --found")
        if not os.path.isdir(a.root) or not os.access(a.root, os.R_OK | os.X_OK):
            p.error(f"--root {a.root} is not a readable directory")
        code, out, notes = discover(pathlib.Path(a.root), art)
    else:
        code, out, notes = check(pathlib.Path(a.root), a.found)
    for n in notes:
        print(f"backlog-sources: {n}", file=sys.stderr)
    if out is not None:
        # --discover output is ASCII-escaped: valid JSON on any stdout, and a name that is not
        # UTF-8 round-trips through json.loads as the same lone surrogate.
        print(json.dumps(out, ensure_ascii=a.discover))
    return code


if __name__ == "__main__":
    _tolerant_streams()
    sys.exit(main(sys.argv[1:]))
