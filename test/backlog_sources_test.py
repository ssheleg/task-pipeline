#!/usr/bin/env python3
"""The declared task sources (`scripts/backlog_sources.py`, R13) — stdlib only.

`references/waves.md` says a wave-0 harvest reads exactly the sources a repository declares in
`docs/backlog-sources.json`, and reports a source of open work the manifest does not list as a
finding. Until 1.93.3 that sentence was doctrine with no mechanism and no test (observer
finding on wave 2). These cases build fixture repositories and pin the mechanical half:

  * no manifest → discovery, said on stderr, exit 0, nothing printed as a harvest list;
  * a well-formed manifest (table, checklist, json-tasks, context) → the harvest list, exit 0;
  * every rule of the contract that a harvest depends on refuses its own malformed fixture,
    exit 1, with the reason named;
  * a `--found` source the manifest does not list → exit 3, the finding named;
  * the doctrine and the script name each other, so neither drifts alone.

Run bare: prints PASS lines and exits non-zero on the first failure.
"""
import copy
import json
import os
import pathlib
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SKILL = ROOT / "plugins" / "task-pipeline" / "skills" / "task-pipeline"
SCRIPT = SKILL / "scripts" / "backlog_sources.py"
CASES = 0

GOOD = {
    "schema": 1,
    "repository": "https://github.com/example-org/example-tool",
    "sources": [
        {"path": "docs/backlog.md", "goal": "reliable-work", "kind": "tasks", "format": "table",
         "idColumn": "ID", "titleColumn": "Item", "statusColumn": "Status",
         "excludeIds": ["B-001"]},
        {"path": "docs/roadmap.md", "goal": "workflow-control", "kind": "tasks",
         "format": "checklist"},
        {"path": "docs/queue.json", "goal": "interoperability", "kind": "tasks",
         "format": "json-tasks"},
        {"path": "docs/HANDOFF.md", "goal": "shared-context", "kind": "context"},
    ],
}


def ok(cond, what):
    global CASES
    CASES += 1
    if not cond:
        print(f"FAIL: {what}")
        sys.exit(1)


def repo(tmp, manifest, files=("docs/backlog.md", "docs/roadmap.md", "docs/queue.json",
                               "docs/HANDOFF.md")):
    d = pathlib.Path(tmp)
    for f in files:
        (d / f).parent.mkdir(parents=True, exist_ok=True)
        (d / f).write_text("x\n", encoding="utf-8")
    if manifest is not None:
        (d / "docs").mkdir(exist_ok=True)
        text = manifest if isinstance(manifest, str) else json.dumps(manifest)
        (d / "docs" / "backlog-sources.json").write_text(text, encoding="utf-8")
    return d


def run(d, *extra):
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(d), *extra],
                       capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout, r.stderr


def case_no_manifest():
    with tempfile.TemporaryDirectory(prefix="tp-bsrc-") as t:
        code, out, err = run(repo(t, None))
        ok(code == 0 and out == "" and "discovers its sources" in err,
           "no manifest is discovery, said aloud, not a harvest list")
    print("PASS: no manifest → discovery, disclosed")


def case_good_manifest():
    with tempfile.TemporaryDirectory(prefix="tp-bsrc-") as t:
        code, out, err = run(repo(t, GOOD))
        ok(code == 0, f"a well-formed manifest is read ({err.strip()})")
        doc = json.loads(out)
        ok([s["path"] for s in doc["tasks"]] == ["docs/backlog.md", "docs/roadmap.md",
                                                  "docs/queue.json"],
           "the harvest reads exactly the declared task sources, in order")
        ok(doc["tasks"][0]["idColumn"] == "ID" and doc["tasks"][0]["statusColumn"] == "Status"
           and doc["tasks"][0]["excludeIds"] == ["B-001"],
           "with the id, title and status columns each one names")
        ok(doc["context"] == ["docs/HANDOFF.md"] and doc["undeclared"] == [],
           "context sources are links, never tasks")
        g = copy.deepcopy(GOOD)
        g["sources"][0].pop("statusColumn")
        g["sources"][0]["defaultStatus"] = "open"
        code, out, _ = run(repo(t, g))
        ok(code == 0 and json.loads(out)["tasks"][0]["defaultStatus"] == "open",
           "an open-only table declares defaultStatus instead of a status column")
    print("PASS: a well-formed manifest becomes the harvest list")


def _mut(fn):
    g = copy.deepcopy(GOOD)
    fn(g)
    return g


MALFORMED = [
    ("not JSON", "{", "not readable JSON"),
    ("schema 2", _mut(lambda g: g.update(schema=2)), "`schema`"),
    ("repository not canonical", _mut(lambda g: g.update(repository="git@github.com:a/b.git")),
     "`repository`"),
    ("no sources", _mut(lambda g: g.update(sources=[])), "1–100 entries"),
    ("absolute path", _mut(lambda g: g["sources"][0].update(path="/etc/backlog.md")), "`path`"),
    ("traversal", _mut(lambda g: g["sources"][0].update(path="docs/../../x.md")), "`path`"),
    ("hidden segment", _mut(lambda g: g["sources"][0].update(path=".task-pipeline/run.md")),
     "`path`"),
    ("missing file", _mut(lambda g: g["sources"][0].update(path="docs/gone.md")), "missing"),
    ("goal outside the anchors", _mut(lambda g: g["sources"][0].update(goal="speed")), "`goal`"),
    ("unknown kind", _mut(lambda g: g["sources"][0].update(kind="ideas")), "`kind`"),
    ("unsupported format", _mut(lambda g: g["sources"][0].update(format="yaml")), "`format`"),
    ("table without idColumn", _mut(lambda g: g["sources"][0].pop("idColumn")), "`idColumn`"),
    ("both status and default", _mut(lambda g: g["sources"][0].update(defaultStatus="open")),
     "exactly one"),
    ("neither status nor default", _mut(lambda g: g["sources"][0].pop("statusColumn")),
     "exactly one"),
    ("default other than open", _mut(lambda g: (g["sources"][0].pop("statusColumn"),
                                                g["sources"][0].update(defaultStatus="done"))),
     "exactly one"),
    ("duplicate excludeIds", _mut(lambda g: g["sources"][0].update(excludeIds=["A1", "A1"])),
     "`excludeIds`"),
    ("free-form idPattern", _mut(lambda g: g["sources"][0].update(idPattern="(a|b)*")),
     "`idPattern`"),
    ("json-tasks on a .md path", _mut(lambda g: g["sources"][2].update(path="docs/backlog.md")),
     "`path`"),
    ("duplicate declaration", _mut(lambda g: g["sources"].append(dict(g["sources"][0]))),
     "duplicate declaration"),
    # What the docstring claims and the checker did not enforce (round 2 of the iteration's
    # verification): every source, not only a task table, and no key the schema lacks.
    ("unknown source key", _mut(lambda g: g["sources"][0].update(owner="someone")), "unknown key `owner`"),
    ("unknown top-level key", _mut(lambda g: g.update(extra=1)), "unknown key `extra`"),
    ("heading not a string", _mut(lambda g: g["sources"][0].update(heading=3)), "`heading`"),
    ("free-form idPattern on a context source", _mut(lambda g: g["sources"][3].update(idPattern="(a)")),
     "`idPattern`"),
    ("duplicate excludeIds on a context source", _mut(lambda g: g["sources"][3].update(excludeIds=["X", "X"])),
     "`excludeIds`"),
    ("defaultStatus other than open on a checklist", _mut(lambda g: g["sources"][1].update(defaultStatus="done")),
     "`defaultStatus`"),
    ("empty statusColumn on a json-tasks source", _mut(lambda g: g["sources"][2].update(statusColumn=" ")),
     "`statusColumn`"),
]


def case_malformed():
    for name, manifest, needle in MALFORMED:
        with tempfile.TemporaryDirectory(prefix="tp-bsrc-") as t:
            code, out, err = run(repo(t, manifest))
            ok(code == 1 and out == "" and needle in err,
               f"{name}: refused with exit 1 naming {needle!r} (got {code}: {err.strip()})")
    print(f"PASS: {len(MALFORMED)} malformed manifests each refused with its reason")


def case_symlinked_source():
    with tempfile.TemporaryDirectory(prefix="tp-bsrc-") as t:
        d = repo(t, GOOD, files=("docs/roadmap.md", "docs/queue.json", "docs/HANDOFF.md",
                                 "elsewhere.md"))
        os.symlink(d / "elsewhere.md", d / "docs" / "backlog.md")
        code, _, err = run(d)
        ok(code == 1 and "symlink" in err, "a source reached through a symlink is refused")
    print("PASS: a symlinked source is refused")


def case_undeclared_finding():
    with tempfile.TemporaryDirectory(prefix="tp-bsrc-") as t:
        d = repo(t, GOOD)
        code, out, err = run(d, "--found", "docs/backlog.md", "./TODO.md", "docs/HANDOFF.md")
        ok(code == 3, "an undeclared source of open work is a finding, exit 3")
        ok(json.loads(out)["undeclared"] == ["TODO.md"] and "finding: TODO.md" in err,
           "the finding names the source, and only that one")
        code, _, _ = run(d, "--found", "docs/backlog.md", "docs/roadmap.md")
        ok(code == 0, "declared sources found by discovery are not findings")
    print("PASS: an undeclared source is reported, not silently added")


def case_doctrine_names_script():
    waves = (SKILL / "references" / "waves.md").read_text(encoding="utf-8")
    ok("docs/backlog-sources.json" in waves and "scripts/backlog_sources.py" in waves,
       "references/waves.md names the manifest and the script that reads it")
    ok("knowledge/backlog.md" in SCRIPT.read_text(encoding="utf-8"),
       "the script names the contract's owner")
    print("PASS: the doctrine and the script name each other")


def case_hand_rules_without_jsonschema():
    """The hand rules alone — `jsonschema` made unimportable — refuse what the schema refuses:
    a blank idColumn or titleColumn on ANY source, not only on a table."""
    with tempfile.TemporaryDirectory(prefix="tp-bsrc-nojs-") as stub:
        pkg = pathlib.Path(stub) / "jsonschema"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("raise ImportError('hidden for this case')\n")
        env = dict(os.environ, PYTHONPATH=stub)
        for name, fn in (("blank idColumn on a checklist", lambda g: g["sources"][1].update(idColumn=" ")),
                         ("blank titleColumn on a context source", lambda g: g["sources"][3].update(titleColumn=""))):
            with tempfile.TemporaryDirectory(prefix="tp-bsrc-") as t:
                d = repo(t, _mut(fn))
                r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(d)], capture_output=True,
                                   text=True, timeout=60, env=env)
                ok(r.returncode == 1 and ("idColumn" in r.stderr or "titleColumn" in r.stderr)
                   and "schema:" not in r.stderr,
                   f"{name}: refused by the hand rules alone ({r.returncode}: {r.stderr.strip()})")
    print("PASS: without jsonschema the hand rules refuse a blank column name on any source")


if __name__ == "__main__":
    for case in (case_no_manifest, case_good_manifest, case_malformed, case_symlinked_source,
                 case_undeclared_finding, case_doctrine_names_script,
                 case_hand_rules_without_jsonschema):
        case()
    print(f"PASS: backlog_sources.py — {CASES} cases")
