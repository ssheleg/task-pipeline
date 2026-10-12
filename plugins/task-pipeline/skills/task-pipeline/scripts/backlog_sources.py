#!/usr/bin/env python3
"""The declared task sources a wave-0 harvest reads (`references/waves.md`, R13) — stdlib only.

Where a repository carries `docs/backlog-sources.json`, the harvest reads exactly the sources
it lists, with the id, title and status columns each one names, and a source of open work the
manifest does not list is a finding, not a silent addition. This script is the mechanical half
of that sentence: it reads the manifest, refuses one the harvest could not follow, and prints
the list the harvest works from.

    backlog_sources.py [--root DIR] [--found PATH ...]

The rule a user of this skill reads is the shipped schema template,
`templates/backlog-sources.schema.json` (backlog-sources/1), with `references/backlog.md` →
*A declared source list*; this checker enforces it, plus the two rules a schema cannot state
(a regular file reached through no symlink, no duplicate declaration). The Fabric workspace's
`knowledge/backlog.md` (section *Source contract*; read at fabric-workspace d49b6f58,
2026-10-08) is its provenance: the template is compatible with it, with one deliberate
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
  string; `statusColumn`, `defaultStatus`, `excludeIds` and `idPattern` are checked on every
  source, whatever its kind. Where `jsonschema` is installed the shipped schema is applied too.

Output, on success: one JSON object — `repository`, `tasks` (each declaration as given, the
fields the harvest reads), `context` (paths), `undeclared` (each `--found` path the manifest
does not list, as `file:line`-free repository paths).

Exit codes: 0 the manifest is readable and nothing undeclared was found, or there is no
manifest (discovery then, as `references/knowledge-sources.md` describes — printed, not
silent); 1 the manifest is malformed, every reason printed; 3 the manifest is fine and a
`--found` source is not in it — the finding the doctrine asks for.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
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
        if cur.is_symlink():
            return False
    return cur.is_file()


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


def check(root: pathlib.Path, found: list[str]) -> tuple[int, dict | None, list[str]]:
    """(exit code, the harvest list or None, reasons)."""
    mf = root / MANIFEST
    if not mf.exists():
        return 0, None, [f"no {MANIFEST} — the harvest discovers its sources"]
    try:
        doc = json.loads(mf.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return 1, None, [f"{MANIFEST}: not readable JSON ({type(exc).__name__})"]
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
        if "statusColumn" in s and not _nonempty(s.get("statusColumn")):
            errs.append(f"{where}: `statusColumn` is empty")
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


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="backlog_sources.py",
                                description="The declared task sources a wave-0 harvest reads.")
    p.add_argument("--root", default=".", help="the repository root (default: .)")
    p.add_argument("--found", nargs="*", default=[],
                   help="sources of open work discovery found, as repository paths")
    a = p.parse_args(argv)
    code, out, notes = check(pathlib.Path(a.root), a.found)
    for n in notes:
        print(f"backlog-sources: {n}", file=sys.stderr)
    if out is not None:
        print(json.dumps(out, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
