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
  * the doctrine and the script name each other, so neither drifts alone;
  * `--discover` finds the board a project already keeps, in the declared order (manifest,
    instruction file, agent-sync, known paths), reads a tracker rule and its negation, marks
    a remote agent-sync backend, and seeds only when nothing exists (exit 4).

Run bare: prints PASS lines and exits non-zero on the first failure.
"""
import copy
import json
import os
import pathlib
import subprocess
import sys
import shutil
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


def sig(doc):
    """The signals other than the standing "read the instruction files" ones."""
    return [x for x in doc["signals"] if x["kind"] != "instructions"]


def no_board(doc, path=None):
    """Not the home and not a candidate. With the wide signal net (exit 5 is conservative by
    design) the line may still be an instruction-line signal; it is never a file signal."""
    files = {sg.get("path") for sg in doc["signals"] if sg["kind"] in ("stated-file", "tracked-file")}
    return doc["home"] is None and doc["candidates"] == [] and (path is None or path not in files)


def discover(d, *extra):
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(d), "--discover", *extra],
                       capture_output=True, text=True, timeout=60)
    return r.returncode, (json.loads(r.stdout) if r.stdout.strip() else None), r.stderr


def tree(tmp, files):
    d = pathlib.Path(tmp)
    for f, text in files.items():
        (d / f).parent.mkdir(parents=True, exist_ok=True)
        (d / f).write_text(text, encoding="utf-8")
    return d


def case_discover_nothing_seeds():
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        code, doc, _ = discover(tree(t, {"src/main.py": "x\n"}))
        ok(code == 4 and doc["home"] is None and doc["seed"] == "docs/evidence/backlog.md",
           f"nothing found → exit 4 and the seed path under the artifacts root ({code}, {doc})")
        code, doc, _ = discover(tree(t, {"src/main.py": "x\n"}), "--artifacts", "docs/superpowers")
        ok(doc["seed"] == "docs/superpowers/backlog.md", "the seed follows --artifacts")
    print("PASS: --discover seeds only when the project keeps no board")


def case_discover_existing_plain_board():
    """The 21-repository case: `docs/backlog.md` and no manifest. Seeding a second board
    beside it is the duplicate the discovery exists to prevent."""
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        code, doc, _ = discover(tree(t, {"docs/backlog.md": "| ID |\n", "docs/ROADMAP.md": "x\n",
                                         "docs/plans/2026-11-01-x.md": "x\n"}))
        ok(code == 0 and doc["home"]["path"] == "docs/backlog.md" and doc["seed"] is None,
           f"an existing docs/backlog.md is the home, nothing is seeded ({doc})")
        ok(doc["home"]["via"] == "known-path" and not doc["ambiguous"],
           "a roadmap beside one board is a queue, not a second board")
        ok("docs/ROADMAP.md" in [c["path"] for c in doc["candidates"]]
           and "docs/plans" in doc["weak"], "roadmap listed as a candidate, plans as a weak signal")
    print("PASS: --discover picks up docs/backlog.md instead of seeding a duplicate")


def case_discover_order_and_ambiguity():
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"docs/evidence/backlog.md": "x\n", "BACKLOG.md": "x\n"})
        code, doc, err = discover(d)
        ok(code == 0 and doc["home"]["path"] == "docs/evidence/backlog.md" and doc["ambiguous"]
           and "backlog-sources.json" in err,
           f"two boards: the first known path wins, the ambiguity is a finding ({doc}, {err})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"docs/evidence/backlog.md": "x\n", "docs/roadmap.md": "x\n",
                     "docs/backlog.md": "x\n", "docs/HANDOFF.md": "x\n"})
        (d / "docs" / "backlog-sources.json").write_text(json.dumps({
            "schema": 1, "repository": "https://github.com/example-org/example-tool",
            "sources": [{"path": "docs/roadmap.md", "goal": "workflow-control", "format": "checklist"},
                        {"path": "docs/HANDOFF.md", "goal": "shared-context", "kind": "context"}]}),
            encoding="utf-8")
        code, doc, _ = discover(d)
        ok(code == 0 and doc["home"] == {"path": "docs/roadmap.md", "via": "manifest",
                                         "evidence": "docs/backlog-sources.json"}
           and not doc["ambiguous"], f"a manifest outranks every known path ({doc})")
        (d / "docs" / "backlog-sources.json").write_text("{", encoding="utf-8")
        code, doc, err = discover(d)
        ok(code == 1 and "not readable JSON" in err, "a broken manifest is refused, not bypassed")
    print("PASS: --discover keeps the declared order and reports two boards")


def case_discover_instruction_rules():
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"CLAUDE.md": "# rules\nOpen work lives in `docs/ops/queue-backlog.md`.\n"
                                  "Tasks are tracked in Linear (team OPS).\n",
                     "docs/ops/queue-backlog.md": "x\n", "docs/backlog.md": "x\n"})
        code, doc, _ = discover(d)
        ok(code == 0 and doc["home"] == {"path": "docs/ops/queue-backlog.md", "via": "instruction",
                                         "evidence": "CLAUDE.md:2"},
           f"a path the instruction file names outranks a known path ({doc})")
        ok({"name": "Linear", "negated": False, "where": "CLAUDE.md:3", "stated": True} in doc["trackers"],
           f"the tracker rule is read with its line ({doc['trackers']})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"AGENTS.md": "Backlog: docs/audits/2026-remediation-queue.md (not Linear).\n",
                     "docs/audits/2026-remediation-queue.md": "x\n"})
        code, doc, _ = discover(d)
        ok(doc["trackers"] == [{"name": "Linear", "negated": True, "where": "AGENTS.md:1", "stated": False}],
           f"a negative rule is read as one ({doc['trackers']})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"CLAUDE.md": "Linear is our tracker for all tasks; see the Fabric board for asks.\n"})
        code, doc, _ = discover(d)
        ok(code == 0 and doc["home"]["via"] == "tracker" and doc["home"]["tracker"] == "Linear"
           and doc["seed"] is None,
           f"a named tracker with no file is the home, nothing seeded ({doc})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"CLAUDE.md": "Read ROADMAP.md for scope.\nLinear is the only tracker; a "
                                  "session list does not replace Linear.\n",
                     "ROADMAP.md": "x\n", "docs/evidence/backlog.md": "x\n"})
        code, doc, _ = discover(d)
        ok(doc["home"]["via"] == "tracker" and doc["home"]["tracker"] == "Linear"
           and doc["candidates"][0]["path"] == "ROADMAP.md",
           f"a roadmap named first is a queue; the stated tracker is the home ({doc})")
        ok(doc["trackers"] == [{"name": "Linear", "negated": False, "where": "CLAUDE.md:2", "stated": True}],
           f"'does not replace Linear' is not a negative rule ({doc['trackers']})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"CLAUDE.md": "- **Task tracking is the remediation ledger, not Linear.** "
                                  "`docs/audits/2026-08-03-remediation-queue.md` is where work is filed.\n",
                     "docs/audits/2026-08-03-remediation-queue.md": "x\n",
                     "docs/superpowers/backlog.md": "x\n"})
        code, doc, _ = discover(d)
        ok(doc["home"]["path"] == "docs/audits/2026-08-03-remediation-queue.md"
           and doc["trackers"][0]["negated"],
           f"a stated tracking rule outranks a file merely named backlog ({doc})")
    print("PASS: --discover reads the instruction file's path, tracker and negation")


def case_discover_agent_sync():
    cfg = {"backend": "outline", "idRegisters": {"B": {"file": "docs/superpowers/backlog.md"},
                                                 "DEC": {"file": "docs/DECISIONS.md"}},
           "claimTags": {"docs/WORKSTREAMS.md": {"mode": "cell"}}}
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {".claude/agent-sync.json": json.dumps(cfg),
                     "docs/superpowers/backlog.md": "x\n", "docs/WORKSTREAMS.md": "x\n",
                     "docs/DECISIONS.md": "x\n", "docs/evidence/backlog.md": "x\n"})
        code, doc, _ = discover(d)
        ok(code == 0 and doc["home"]["path"] == "docs/superpowers/backlog.md"
           and doc["home"]["via"] == "agent-sync", f"the agent-sync register outranks known paths ({doc})")
        ok(doc["agentSync"] == {"backend": "outline", "remote": True,
                                "files": ["docs/superpowers/backlog.md", "docs/WORKSTREAMS.md"]},
           f"a remote backend is marked; DECISIONS is not a board ({doc['agentSync']})")
        (d / ".claude" / "agent-sync.json").write_text("{nope", encoding="utf-8")
        code, doc, err = discover(d)
        ok(code == 0 and doc["agentSync"] is None and "agent-sync.json" in err
           and doc["home"]["path"] == "docs/evidence/backlog.md" and doc["ambiguous"],
           f"an unreadable agent-sync config is said aloud and skipped; the known order rules ({doc})")
    print("PASS: --discover follows agent-sync registers and marks a remote backend")


def case_discover_refuses_escape():
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t, \
            tempfile.TemporaryDirectory(prefix="tp-bdisc-out-") as out:
        pathlib.Path(out, "backlog.md").write_text("x\n", encoding="utf-8")
        d = tree(t, {"CLAUDE.md": f"Backlog: ../{pathlib.Path(out).name}/backlog.md\n"})
        (d / "docs").mkdir()
        os.symlink(out, d / "docs" / "evidence")
        code, doc, _ = discover(d)
        ok(code == 5 and doc["home"] is None and doc["seed"] is None
           and {"kind": "instruction-line", "where": "CLAUDE.md:1"} in sig(doc)
           and all(sg.get("kind") in ("instruction-line", "seed-path-taken") for sg in sig(doc)),
           f"a path outside the repository is never the home; its line is a signal, not a seed ({doc})")
    print("PASS: --discover refuses a path that leaves the repository")


def case_discover_review_round():
    """The blind reader's fixtures (2026-11-06): each was a wrong home before the fix."""
    def home(files, *extra):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            code, doc, err = discover(tree(t, files), *extra)
            return code, doc, err
    code, doc, _ = home({"CLAUDE.md": "Read docs/onboarding.md before starting.\n",
                         "docs/onboarding.md": "x\n"})
    ok(no_board(doc, "docs/onboarding.md") and sig(doc) == [], f"onboarding.md is not a board ({doc})")
    code, doc, _ = home({"CLAUDE.md": "The board idea lives in docs/specs/cloud-board.md.\n",
                         "docs/specs/cloud-board.md": "x\n", "docs/dashboard.md": "x\n"})
    ok(no_board(doc, "docs/specs/cloud-board.md"), f"a spec named cloud-board is not a board ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Open work is tracked in ./docs/work/backlog.md\n",
                         "docs/work/backlog.md": "x\n"})
    ok(code == 0 and doc["home"]["path"] == "docs/work/backlog.md",
       f"a ./-prefixed path is read ({doc})")
    for line in ("The skills ship a Jira MCP bridge.\n", "We do not use Linear for this repo.\n",
                 "Задачи ведём не в Linear.\n"):
        code, doc, _ = home({"CLAUDE.md": line})
        mention = "Jira MCP" in line
        ok(doc["home"] is None and code == 5
           and (sig(doc) == [{"kind": "tracker", "name": "Jira", "where": "CLAUDE.md:1"}]
                if mention else sig(doc) == []),
           f"a mention is a signal, a negated tracker nothing; neither is the home: {line.strip()} ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Do not file in docs/TODO.md (retired); open work is "
                                      "tracked in docs/backlog.md.\n",
                         "docs/TODO.md": "x\n", "docs/backlog.md": "x\n"})
    ok(doc["home"]["path"] == "docs/backlog.md", f"a negated path is not stated ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Task tracking lives in Linear, not in docs/ROADMAP.md.\n",
                         "docs/ROADMAP.md": "x\n"})
    ok(doc["home"]["via"] == "tracker" and doc["home"]["tracker"] == "Linear",
       f"the stated tracker wins over the file the line negates ({doc})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t, \
            tempfile.TemporaryDirectory(prefix="tp-bdisc-out-") as out:
        pathlib.Path(out, "plans").mkdir()
        pathlib.Path(out, "plans", "a.md").write_text("x\n", encoding="utf-8")
        d = pathlib.Path(t)
        os.symlink(out, d / "docs")
        code, doc, _ = discover(d)
        ok(doc["weak"] == [], f"a weak signal behind a symlinked docs/ is not listed ({doc})")
    code, doc, _ = home({"src/main.py": "x\n"}, "--artifacts", "./docs/runs/")
    ok(doc["seed"] == "docs/runs/backlog.md", f"--artifacts is normalised ({doc})")
    code, doc, _ = home({"src/main.py": "x\n"}, "--artifacts", ".pipeline")
    ok(doc["seed"] == ".pipeline/backlog.md", "a hidden artifact root is legal (artifacts.md)")
    for bad in (("--artifacts", "/etc"), ("--artifacts", "../x"), ("--found", "docs/x.md")):
        code, doc, err = home({"src/main.py": "x\n"}, *bad)
        ok(code == 2, f"{bad} is refused, not reinterpreted ({code}, {err.strip()})")
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", "/nonexistent-tp-root", "--discover"],
                       capture_output=True, text=True, timeout=60)
    ok(r.returncode == 2, f"a missing --root is an error, not a seed ({r.returncode})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"docs/backlog.md": "x\n"})
        (d / ".claude").mkdir()
        os.symlink(d / "nowhere.json", d / ".claude" / "agent-sync.json")
        code, doc, err = discover(d)
        ok("agent-sync.json" in err and doc["agentSync"] is None,
           f"a dangling agent-sync symlink is said aloud ({err.strip()})")
        (d / ".claude" / "agent-sync.json").unlink()
        (d / ".claude" / "agent-sync.json").write_text(json.dumps({"idRegisters": ["B"]}),
                                                        encoding="utf-8")
        code, doc, err = discover(d)
        ok("idRegisters" in err, f"a list-shaped idRegisters is said aloud ({err.strip()})")
    code, doc, _ = home({"AGENTS.md": "| `@task` | `NBA-###` | a row of that service's "
                                      "`docs/ROADMAP.md`; " + "x" * 120 + " tasks\n",
                         "docs/ROADMAP.md": "x\n", "docs/superpowers/backlog.md": "x\n"})
    ok(doc["home"]["path"] == "docs/superpowers/backlog.md",
       f"a tracking word far from the path states nothing (nicegram-business AGENTS.md:393) ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Skills for Jira, Confluence and " + "y" * 120 +
                                      " tracking of 300 tasks.\n"})
    ok(code == 5 and doc["home"] is None and sig(doc)[0]["kind"] == "tracker",
       f"a tracker named far from any tracking word is a signal, not the home (claude-skills) ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Prefix commits with the Jira ticket `[NCG-1]`.\n"})
    ok(code == 5 and doc["home"] is None and sig(doc) == [{"kind": "tracker", "name": "Jira", "where": "CLAUDE.md:1"}],
       f"a commit-prefix rule is no home, but Jira is a signal to read (nicegram-api) ({doc})")
    code, doc, _ = home({"CLAUDE.md": "| Active priorities (product, sprint history) | "
                                      "`BACKLOG.md`, `ROADMAP.md` |\n",
                         "BACKLOG.md": "x\n", "ROADMAP.md": "x\n"})
    ok(doc["home"]["path"] == "BACKLOG.md",
       f"a neighbouring path's name is not a tracking word (checkmydata-ai CLAUDE.md:1146) ({doc})")
    print("PASS: --discover holds on the blind reader's fixtures")


def case_discover_second_round():
    """The second blind reading (2026-11-06): generic names, negation that came back through
    the known-path pass, a retirement written after the path, a reading list."""
    def home(files):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            return discover(tree(t, files))
    for f, line in (("docs/build.md", "Build steps live in docs/build.md; run them before a release."),
                    ("docs/build-notes.md", "See docs/build-notes.md"),
                    ("docs/order-flow.md", "The checkout is described in docs/order-flow.md."),
                    ("docs/architecture/queue.md", "Workers: docs/architecture/queue.md."),
                    ("docs/celery-tasks.md", "Celery: docs/celery-tasks.md.")):
        code, doc, _ = home({"CLAUDE.md": line + "\n", f: "x\n"})
        ok(no_board(doc, f), f"{f} named as reading is not a board ({doc})")
    code, doc, _ = home({"AGENTS.md": "Очередь задач: `docs/queue.md`\n", "docs/queue.md": "x\n"})
    ok(code == 0 and doc["home"]["path"] == "docs/queue.md",
       f"a generic name on a tracking line is the board ({doc})")
    code, doc, _ = home({"AGENTS.md": "Build order: docs/BUILD_ORDER.md\n", "docs/BUILD_ORDER.md": "x\n"})
    ok(code == 0 and doc["home"]["path"] == "docs/BUILD_ORDER.md", f"BUILD_ORDER is a board name ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Do not file in TODO.md, it is a scratch list.\n", "TODO.md": "x\n"})
    ok(code == 5 and doc["home"] is None and doc["negated"] == ["TODO.md"]
       and {"kind": "negated", "path": "TODO.md"} in doc["signals"],
       f"a negated file does not come back as a known path; it is a signal to read ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Задачи записывай не в TODO.md, а в docs/backlog.md.\n",
                         "TODO.md": "x\n", "docs/backlog.md": "x\n"})
    ok(doc["home"]["path"] == "docs/backlog.md" and not doc["ambiguous"],
       f"a board the rule settled is no ambiguity ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Open work is no longer in docs/TODO.md; it is tracked in "
                                      "docs/backlog.md.\n", "docs/TODO.md": "x\n",
                         "docs/backlog.md": "x\n"})
    ok(doc["home"]["path"] == "docs/backlog.md", f"'no longer in' negates ({doc})")
    code, doc, _ = home({"CLAUDE.md": "docs/backlog.md is retired, do not file there; open work is "
                                      "tracked in Linear.\n", "docs/backlog.md": "x\n"})
    ok(doc["home"]["via"] == "tracker" and doc["home"]["tracker"] == "Linear",
       f"a retirement after the path negates it ({doc})")
    for line in ("Read docs/ROADMAP.md, docs/ARCHITECTURE.md and docs/backlog.md (open work) before starting.",
                 "| docs/ROADMAP.md | phases | docs/backlog.md | open work |"):
        code, doc, _ = home({"CLAUDE.md": line + "\n", "docs/ROADMAP.md": "x\n",
                             "docs/ARCHITECTURE.md": "x\n", "docs/backlog.md": "x\n"})
        ok(doc["home"]["path"] == "docs/backlog.md", f"the backlog outranks a roadmap: {line} ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Task status lives in the board ([`docs/ROADMAP.md`](./docs/ROADMAP.md)), "
                                      "tracked per row.\n", "docs/ROADMAP.md": "x\n"})
    ok(doc["home"]["path"] == "docs/ROADMAP.md", f"a roadmap stated alone stays the home ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Linear tracks every task.\n"})
    ok(doc["home"] and doc["home"]["via"] == "tracker", f"'tracks' is a tracking word ({doc})")
    print("PASS: --discover holds on the second reader's fixtures")


def case_discover_third_round():
    """The third blind reading (2026-11-06): a negation may demote a board, never erase the
    only one; the output keeps its types; a board outranks a roadmap whatever its name."""
    def home(files):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            return discover(tree(t, files))
    code, doc, _ = home({"CLAUDE.md": "Do not file in docs/TODO.md.\nWe use Linear for releases.\n",
                         "docs/TODO.md": "x\n", "docs/backlog.md": "x\n"})
    ok(doc["negated"] == ["docs/TODO.md"], f"`negated` stays a list beside a tracker line ({doc['negated']!r})")
    for line in ("docs/backlog.md (archived rows live in docs/archive.md)",
                 "docs/backlog.md: archived rows are struck through",
                 "Board: docs/backlog.md - frozen items move to the bottom",
                 "Open work: docs/backlog.md. Frozen deps are listed in package-lock.",
                 "If there is no docs/backlog.md, seed one from the template.",
                 "Without docs/backlog.md the harvest has nothing to read.",
                 "Do not file in docs/backlog.md directly; run scripts/row.sh.",
                 "Open work is tracked in docs/backlog.md.\nNever file in docs/backlog.md without a claim.",
                 "Separate tracker? No - use docs/backlog.md"):
        code, doc, _ = home({"CLAUDE.md": line + "\n", "docs/backlog.md": "x\n"})
        ok(code == 0 and doc["home"]["path"] == "docs/backlog.md",
           f"prose is not a filing rule, the board stays: {line!r} ({doc})")
    for line, gone in (("docs/backlog.md is retired; open work is tracked in Linear.", "docs/backlog.md"),
                       ("TODO.md (deprecated). Open work: docs/backlog.md", "TODO.md"),
                       ("Don't file in TODO.md; it is a scratch list.", "TODO.md")):
        code, doc, _ = home({"CLAUDE.md": line + "\n", "TODO.md": "x\n", "docs/backlog.md": "x\n"})
        ok(gone in doc["negated"] and not doc["ambiguous"], f"a filing rule still negates: {line!r} ({doc})")
    for board in ("TASKS.md", "docs/todo.md", "docs/work/queue.md"):
        code, doc, _ = home({"CLAUDE.md": "Roadmap, tracked by quarter: ROADMAP.md\n"
                                          f"Open work is tracked in {board}.\n",
                             "ROADMAP.md": "x\n", board: "x\n"})
        ok(doc["home"]["path"] == board, f"{board} is a board, the roadmap a queue ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Open work is tracked (e.g. bugs, ideas) in docs/work/queue.md\n",
                         "docs/work/queue.md": "x\n"})
    ok(code == 0 and doc["home"]["path"] == "docs/work/queue.md", f"'e.g.' does not end the clause ({doc})")
    print("PASS: --discover holds on the third reader's fixtures")


def case_discover_fourth_round():
    """The fourth blind reading (2026-11-06): a tracking word inside a negated clause states
    the opposite, for a file and for a tracker."""
    def home(files):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            return discover(tree(t, files))
    for line in ("Open work is no longer tracked in TODO.md; use docs/backlog.md.",
                 "Don't track work in TODO.md. Open work lives in docs/backlog.md.",
                 "Open work moved from TODO.md to docs/backlog.md.",
                 "We stopped tracking tasks in TODO.md; see docs/backlog.md.",
                 "Never track open work in TODO.md.\nOpen work is tracked in docs/backlog.md.",
                 "Задачи больше не записываем в TODO.md; бэклог: docs/backlog.md.",
                 "TODO.md (the old backlog) was replaced by docs/backlog.md.",
                 "TODO.md is superseded by docs/backlog.md for tracking open work.",
                 "TODO.md is no longer tracked.\nDo not file in TODO.md."):
        code, doc, _ = home({"CLAUDE.md": line + "\n", "TODO.md": "x\n", "docs/backlog.md": "x\n"})
        ok(doc["home"]["path"] == "docs/backlog.md", f"a negated tracking clause states nothing: {line!r} ({doc})")
    code, doc, _ = home({"CLAUDE.md": "TODO.md is no longer tracked.\n", "TODO.md": "x\n",
                         "docs/backlog.md": "x\n"})
    ok("TODO.md" in doc["negated"], f"'is no longer tracked' negates the file ({doc})")
    for line, want in (("We don't track work in Linear anymore; open work is in GitHub issues.", "GitHub issues"),
                       ("Tasks are no longer tracked in Jira. Open work: GitHub issues.", "GitHub issues")):
        code, doc, _ = home({"CLAUDE.md": line + "\n"})
        ok(doc["home"] and doc["home"].get("tracker") == want, f"{line!r} → {want} ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Open work is tracked in docs/backlog.md.\n", "docs/backlog.md": "x\n"})
    ok(doc["home"]["path"] == "docs/backlog.md" and doc["home"]["via"] == "instruction",
       "a plain positive rule still states the board")
    print("PASS: --discover holds on the fourth reader's fixtures")


def case_discover_fifth_round():
    """The fifth blind reading (2026-11-06): a negation counts only where it governs the
    tracking word, and only the passive retires the path it follows."""
    def home(files):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            return discover(tree(t, files))
    R = {"docs/BACKLOG.md": "x\n", "docs/ROADMAP.md": "x\n"}
    for text in ("Open work is tracked in docs/BACKLOG.md, which replaced the old TODO.md.\n",
                 "Open work is tracked in docs/BACKLOG.md (it replaced TODO.md).\n",
                 "Open work is tracked in docs/BACKLOG.md, which replaced the roadmap.\n"
                 "Milestones are tracked in docs/ROADMAP.md.\n",
                 "Milestones are tracked in docs/ROADMAP.md.\n"
                 "Bugs that don't block a release are tracked in docs/BACKLOG.md.\n",
                 "Never commit secrets, and track open work in docs/BACKLOG.md.\n"
                 "Phases are tracked in docs/ROADMAP.md.\n",
                 "Вехи ведём в docs/ROADMAP.md.\nЗадачи, которые не влезли в спринт, записываем в docs/BACKLOG.md.\n",
                 "Open work, formerly kept in chat, is tracked in docs/BACKLOG.md.\n"
                 "Milestones are tracked in docs/ROADMAP.md.\n"):
        code, doc, _ = home({"CLAUDE.md": text, "TODO.md": "x\n", **R})
        ok(doc["home"]["path"] == "docs/BACKLOG.md", f"{text!r} → docs/BACKLOG.md ({doc})")
    for text, board in (("Anything not finished today is tracked in docs/work/queue.md.\n", "docs/work/queue.md"),
                        ("Work we can't do now is tracked in docs/open-tasks.md.\n", "docs/open-tasks.md")):
        code, doc, _ = home({"CLAUDE.md": text, board: "x\n"})
        ok(code == 0 and doc["home"]["path"] == board, f"a stray 'not' keeps the board: {text!r} ({doc})")
    for text in ("Don't open PRs without a ticket, all open work is tracked in Linear.\n",
                 "Open work is tracked in Linear, which replaced Jira.\n"):
        code, doc, _ = home({"CLAUDE.md": text})
        ok(doc["home"] and doc["home"].get("tracker") == "Linear", f"{text!r} → Linear ({doc})")
    print("PASS: --discover holds on the fifth reader's fixtures")


def case_discover_sixth_round():
    """The sixth blind reading (2026-11-06), on real repositories: a frozen board is not the
    home, and no home with a board elsewhere is exit 5 (read the signals), never a blind seed."""
    import time
    def home(files, git=False, *extra):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            d = tree(t, files)
            if git:
                subprocess.run(["git", "init", "-q", str(d)], check=True, timeout=60)
                subprocess.run(["git", "-C", str(d), "add", "-A"], check=True, timeout=60)
            return discover(d, *extra)
    code, doc, err = home({"AGENTS.md": "The copies here: `docs/BACKLOG.md` and `docs/PLAN.md`.\n",
                           "docs/BACKLOG.md": "# Backlog\n\n> **Не канонический с 2026-09-29; "
                                              "заморожен 2026-10-04.** The board is elsewhere.\n"})
    ok(code == 5 and doc["home"] is None and "docs/BACKLOG.md" in doc["negated"]
       and {"kind": "negated", "path": "docs/BACKLOG.md"} in doc["signals"] and "frozen" in err,
       f"a board whose header says frozen is no home (project-observatory) ({doc})")
    code, doc, _ = home({"docs/BACKLOG.md": "# Backlog\nFrozen rows sink to the bottom.\n"})
    ok(code == 0 and doc["home"]["path"] == "docs/BACKLOG.md", f"a row-level 'frozen' is no freeze ({doc})")
    code, doc, _ = home({"AGENTS.md": "`case-management/case.json` is the only register of current "
                                      "tasks (реестр текущих задач).\n",
                         "case-management/SYSTEM-BACKLOG.md": "x\n"}, True)
    ok(code == 5 and {"kind": "tracked-file", "path": "case-management/SYSTEM-BACKLOG.md"} in doc["signals"]
       and {"kind": "instruction-line", "where": "AGENTS.md:1"} in doc["signals"] and doc["seed"] is None,
       f"a tracked backlog file and a register line are signals (usa-immigration) ({doc})")
    code, doc, _ = home({"CLAUDE.md": "The plan, the reports and the backlog are in the instance folder "
                                      "beside it, ~/DATA/x-data.\n"})
    ok(code == 5 and sig(doc) == [{"kind": "instruction-line", "where": "CLAUDE.md:1"}],
       f"a board in a sibling folder is a signal, not a seed (sshlg-brand-agent) ({doc})")
    code, doc, _ = home({"src/main.py": "x\n"}, True)
    ok(code == 4 and sig(doc) == [] and doc["seed"] == "docs/evidence/backlog.md",
       "nothing at all still seeds")
    line = " ".join(f"docs/f{i}.md" for i in range(4000))
    t0 = time.monotonic()
    code, doc, _ = home({"CLAUDE.md": line + "\n"})
    ok(time.monotonic() - t0 < 10, f"a 4000-path line reads in seconds, not minutes ({time.monotonic() - t0:.1f}s)")
    for bad in ("~", "docs\\evidence", "docs/ev idence"):
        code, doc, err = home({"src/main.py": "x\n"}, False, "--artifacts", bad)
        ok(code == 2, f"--artifacts {bad!r} is refused ({code})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t, \
            tempfile.TemporaryDirectory(prefix="tp-bdisc-out-") as out:
        pathlib.Path(out, "CLAUDE.md").write_text("Open work is tracked in docs/backlog.md\n", encoding="utf-8")
        d = pathlib.Path(t)
        os.symlink(pathlib.Path(out, "CLAUDE.md"), d / "CLAUDE.md")
        code, doc, err = discover(d)
        ok("CLAUDE.md: not a regular file" in err, f"a symlinked instruction file is said aloud ({err.strip()})")
    print("PASS: --discover holds on the sixth reader's fixtures")


def case_discover_seventh_round():
    """The seventh blind reading (2026-11-06): a skill named tracker is no board line, a
    closed report named backlog is no board, a tracker named in any words is a signal."""
    def home(files, git=False):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            d = tree(t, files)
            if git:
                subprocess.run(["git", "init", "-q", str(d)], check=True, timeout=60)
                subprocess.run(["git", "-C", str(d), "add", "-A"], check=True, timeout=60)
            return discover(d)
    code, doc, _ = home({"CLAUDE.md": "Install the tc-tracker skill for session notes.\n"})
    ok(no_board(doc), f"a skill called tracker is no board (claude-skills) ({doc})")
    code, doc, _ = home({"docs/wiki/{hub-api} {report} composer advisory backlog.md": "x\n",
                         "docs/wiki/advisory-backlog-notes.md": "---\ntype: report\nstatus: final\n---\n"}, True)
    ok(code == 4, f"a closed report named backlog is no signal (hub-api) ({doc})")
    code, doc, _ = home({"case-management/SYSTEM-BACKLOG.md": "x\n"}, True)
    ok(code == 5 and sig(doc) == [{"kind": "tracked-file", "path": "case-management/SYSTEM-BACKLOG.md"}],
       f"a live tracked backlog file stays a signal ({doc})")
    for line, name in (("Tasks live in Linear.", "Linear"), ("File bugs in Jira (project NCG).", "Jira"),
                       ("All work items are in Jira.", "Jira"), ("Use GitHub issues for bugs and features.", "GitHub issues"),
                       ("Create a Jira ticket for every change.", "Jira"),
                       ("Every task has a Linear issue; link it in the PR.", "Linear")):
        code, doc, _ = home({"CLAUDE.md": line + "\n"})
        ok(code == 5 and {"kind": "tracker", "name": name, "where": "CLAUDE.md:1"} in doc["signals"],
           f"{line!r} is a {name} signal, not a blind seed ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Requests to other projects go through com.submit.\n"})
    ok(no_board(doc) and sig(doc) == [], f"a cross-project com.submit line is not this project's board ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Track open work in docs/status.md.\n", "docs/status.md": "x\n"})
    ok(code == 5 and {"kind": "stated-file", "path": "docs/status.md", "where": "CLAUDE.md:1"} in doc["signals"],
       f"a file a work clause names is a signal ({doc})")
    code, doc, _ = home({"CLAUDE.md": "docs/ux/scenarios.md is the source of truth for behaviour.\n",
                         "docs/ux/scenarios.md": "x\n"})
    ok(no_board(doc, "docs/ux/scenarios.md"), f"a 'source of truth' spec is no board and no file signal ({doc})")
    code, doc, _ = home({"docs/backlog.md": "# Backlog\nReplaces docs/TODO.md, frozen on 2026-09-01.\n"})
    ok(code == 0 and doc["home"]["path"] == "docs/backlog.md",
       f"a header line about another file does not freeze this one ({doc})")
    print("PASS: --discover holds on the seventh reader's fixtures")


def case_discover_eighth_round():
    """The eighth blind reading (2026-11-06): a file the path's own clause calls the place of
    work is a signal without a tracking word, and the freeze belongs to the file it is said of."""
    def home(files):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            return discover(tree(t, files))
    for line, f in (("Open defects live in `docs/known-issues.md`; when you fix an entry, remove it.", "docs/known-issues.md"),
                    ("Open work is tracked in docs/status.md; decisions go in docs/DECISIONS.md.", "docs/status.md"),
                    ("Track open work in docs/status.md. The spec is the source of truth.", "docs/status.md"),
                    ("Tasks live in docs/STATUS.md.", "docs/STATUS.md"),
                    ("Открытые задачи лежат в docs/status.md.", "docs/status.md"),
                    ("Keep the task list in docs/work.md up to date.", "docs/work.md"),
                    ("Remaining work is listed in docs/open-items.md.", "docs/open-items.md"),
                    ("Next steps are in NEXT.md.", "NEXT.md")):
        code, doc, _ = home({"CLAUDE.md": line + "\n", f: "x\n", "docs/DECISIONS.md": "x\n"})
        ok(code == 5 and any(sg.get("path") == f and sg["kind"] == "stated-file" for sg in doc["signals"]),
           f"{line!r} makes {f} a signal (nicegram-desktop) ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Build steps live in docs/build.md.\n", "docs/build.md": "x\n"})
    ok(no_board(doc, "docs/build.md"), f"a verb with no work noun names no place of work ({doc})")
    for head in ("Frozen 2026-09-01: open work moved to ../proj-data/backlog.md",
                 "docs/backlog.md is frozen since 2026-09-01",
                 "Не канонический с 2026-09-29; заморожен 2026-10-04. Каноническая доска: "
                 "[board](../../org-index/docs/observatory/BACKLOG.md)"):
        code, doc, _ = home({"docs/backlog.md": "# Backlog\n\n> " + head + "\n"})
        ok(code == 5 and doc["negated"] == ["docs/backlog.md"], f"the header freezes this board: {head!r} ({doc})")
    for line, f in (("Основа (персоны, задачи пользователя, истории): [docs/ux/foundation.md](docs/ux/foundation.md).",
                     "docs/ux/foundation.md"),
                    ("After work: update `HANDOFF.md` (objective, done, open, exact next task).", "HANDOFF.md"),
                    ("Read CLAUDE.md before any task.", "CLAUDE.md")):
        code, doc, _ = home({"AGENTS.md": line + "\n", f: "x\n"})
        ok(no_board(doc, f), f"a UX foundation, a handoff or an instruction file is no board signal: {line!r} ({doc})")
    print("PASS: --discover holds on the eighth reader's fixtures")


def case_discover_ninth_round():
    """The ninth blind reading (2026-11-06): a wide signal net. Any line about where work is
    tracked, a tracker in any case, a filing verb or a pointer to another repository is a
    signal; exit 4 is left for instructions that say nothing about where work lives."""
    def home(files):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            return discover(tree(t, files))
    for line in ("`docs/status.md` is the source of truth for open work.",
                 "Open tasks are tracked in docs/status.md, the single source of truth.",
                 "Log decisions in docs/DECISIONS.md and open tasks in docs/status.md.",
                 "Pick the next task from docs/status.md, top row first."):
        code, doc, _ = home({"CLAUDE.md": line + "\n", "docs/status.md": "x\n", "docs/DECISIONS.md": "x\n"})
        ok(code == 5 and any(sg.get("path") == "docs/status.md" for sg in doc["signals"]),
           f"a decisions or source-of-truth clause does not veto the work noun: {line!r} ({doc})")
    for line in ("All tasks are tracked in JIRA (project ABC).", "Tasks are tracked in jira.",
                 "Tasks are tracked in Trello.", "Open work is tracked in Notion (Tasks database).",
                 "Bugs are tracked in YouTrack.", "Track open work in linear.",
                 "Open work: https://github.com/acme/app/issues", "Issues are tracked on GitHub.",
                 "Open tasks are kept in the data folder ~/DATA/x-data."):
        code, doc, _ = home({"CLAUDE.md": line + "\n"})
        ok(code == 5 and doc["home"] is None or (doc["home"] or {}).get("via") == "tracker",
           f"{line!r} is a signal or a stated tracker, never a blind seed ({code}, {doc})")
    code, doc, _ = home({"CLAUDE.md": "Anything larger than a line goes to docs/future-work.md instead.\n",
                         "docs/future-work.md": "x\n"})
    ok(code == 5 and any(sg.get("path") == "docs/future-work.md" for sg in doc["signals"]),
       f"a filing verb names the place of deferred work (blog-cms) ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Спецификация, решения и сценарии живут не здесь, а в ssheleg/underline.\n"})
    ok(code == 5 and sig(doc)[0]["kind"] == "instruction-line",
       f"a pointer to the sibling repository is a signal (underline-node) ({doc})")
    code, doc, _ = home({"docs/backlog.md": "# Backlog\n\n| ID | Task |\n|---|---|\n| B-1 | mark the page non-canonical |\n"
                                            "| B-2 | frozen on 2026-11-10 |\n"})
    ok(code == 0 and doc["home"]["path"] == "docs/backlog.md", f"a table row is no header freeze ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Keep a linear history; rebase before merging.\n"})
    ok(doc["trackers"] == [] and not any(x["kind"] == "tracker" for x in doc["signals"]),
       f"'linear history' is no tracker ({doc})")
    print("PASS: --discover holds on the ninth reader's fixtures")


def case_discover_tenth_round():
    """The tenth blind reading (2026-11-06): a project that wrote instructions is read before
    anything is seeded. Exit 4 is left for a tree with no instruction file and nothing else."""
    def home(files):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            return discover(tree(t, files))
    for line in ("`ESM-<number>_<type>/<short-description>`: one branch per ticket, PR into `main`.",
                 "Tickets live in GitLab.", "Bugs go into GitLab issues.", "File bugs in Redmine.",
                 "Work items are in Azure DevOps.", "Our tasks are in monday.com.", "To-dos live in Basecamp.",
                 "Open a ticket for every bug you find.", "Where an area's tasks live: docs/MANAGER-GUIDE.md",
                 "Known issues are listed in docs/KNOWN_ISSUES.md.", "Planned work lives in PLAN.md.",
                 "Планы работ: в docs/plan.md."):
        code, doc, _ = home({"AGENTS.md": line + "\n"})
        ok(code == 5 and doc["seed"] is None and {"kind": "instructions", "path": "AGENTS.md"} in doc["signals"]
           and len(sig(doc)) >= 1, f"{line!r}: read before seeding, the line ranked first ({doc})")
    code, doc, _ = home({"README.md": "Issues are tracked in Linear.\n"})
    ok(code == 5 and {"kind": "instructions", "path": "README.md"} in doc["signals"],
       f"a README-only project is read too ({doc})")
    code, doc, _ = home({"src/main.py": "x\n"})
    ok(code == 4 and doc["signals"] == [] and doc["seed"] == "docs/evidence/backlog.md",
       f"no instruction file and nothing else: seed ({doc})")
    code, doc, _ = home({"docs/backlog.md": "# Backlog\n\n> Migrated from Notion; frozen since 2026-09-01.\n",
                         "docs/ROADMAP.md": "x\n"})
    ok(code == 5 and doc["home"] is None, f"a frozen only board does not hand the home to a roadmap ({doc})")
    print("PASS: --discover holds on the tenth reader's fixtures")


def case_discover_eleventh_round():
    """The eleventh blind reading (2026-11-06)."""
    def home(files, links=()):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            d = tree(t, files)
            for src, dst in links:
                os.symlink(d / dst, d / src)
            return discover(d)
    code, doc, _ = home({"CLAUDE.md": "Merge requests are tracked on GitLab.\n", "docs/backlog.md": "x\n"})
    ok(code == 0 and doc["home"]["path"] == "docs/backlog.md", f"GitLab merge requests are no tracker home ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Bugs are tracked in GitLab issues.\n"})
    ok(code == 0 and doc["home"].get("tracker") == "GitLab issues", f"GitLab issues stated is the home ({doc})")
    code, doc, _ = home({"CLAUDE.md": "docs/backlog.md is retired.\nOpen work is tracked in TODO.md.\n",
                         "docs/backlog.md": "x\n", "TODO.md": "x\n"})
    ok(code == 0 and doc["home"]["path"] == "TODO.md", f"a live board beside a retired one stays the home ({doc})")
    code, doc, _ = home({"docs/AI.md": "Rules.\n"}, (("CLAUDE.md", "docs/AI.md"),))
    ok(code == 5 and {"kind": "instructions", "path": "CLAUDE.md"} in doc["signals"],
       f"a CLAUDE.md symlinked inside the repository is read ({doc})")
    for f in (".claude/CLAUDE.md", ".github/copilot-instructions.md"):
        code, doc, _ = home({f: "Rules.\n"})
        ok(code == 5 and {"kind": "instructions", "path": f} in doc["signals"], f"{f} is read before seeding ({doc})")
    code, doc, _ = home({"readme.md": "About.\n"})
    ok(code == 5 and {"kind": "instructions", "path": "readme.md"} in doc["signals"],
       f"a README in another case is read under its real name ({doc})")
    code, doc, _ = home({"CLAUDE.md": "Files are UTF-8; hashes are SHA-256.\n"})
    ok(sig(doc) == [], f"UTF-8 and SHA-256 are no issue keys ({doc})")
    print("PASS: --discover holds on the eleventh reader's fixtures")


def case_discover_twelfth_round():
    """The twelfth blind reading (2026-11-06): instruction files that are symlinks (a loop,
    a target outside the repository, a linked .claude directory) are listed, never a crash."""
    def run_tree(files, links):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t, \
                tempfile.TemporaryDirectory(prefix="tp-bdisc-out-") as out:
            d = tree(t, files)
            pathlib.Path(out, "rules.md").write_text("Open work is tracked in Linear.\n", encoding="utf-8")
            for src, dst in links:
                (d / src).parent.mkdir(parents=True, exist_ok=True)
                os.symlink(dst.replace("<out>", out) if dst.startswith("<out>") else d / dst, d / src)
            return discover(d)
    for links, want in (((("CLAUDE.md", "CLAUDE.md"),), "CLAUDE.md"),
                        ((("CLAUDE.md", "AGENTS.md"), ("AGENTS.md", "CLAUDE.md")), "AGENTS.md"),
                        (((".github/copilot-instructions.md", ".github/copilot-instructions.md"),),
                         ".github/copilot-instructions.md"),
                        ((("CLAUDE.md", "<out>/rules.md"),), "CLAUDE.md"),
                        ((("AGENTS.md", "<out>/rules.md"),), "AGENTS.md")):
        code, doc, err = run_tree({"src/main.py": "x\n"}, links)
        ok(code == 5 and "Traceback" not in err and {"kind": "instructions", "path": want} in doc["signals"],
           f"{links}: listed for reading, no crash ({code}, {err.strip()[:200]}, {doc})")
    code, doc, _ = run_tree({"config/claude/CLAUDE.md": "Open work is tracked in Linear.\n"}, ((".claude", "config/claude"),))
    ok(code == 5 and {"kind": "instructions", "path": ".claude/CLAUDE.md"} in doc["signals"],
       f"a .claude directory linked inside the repository is listed for reading ({doc})")
    code, doc, _ = run_tree({"docs/ai/rules.md": "Open work is tracked in Linear.\n"}, (("CLAUDE.md", "docs/ai/rules.md"),))
    ok(code == 0 and doc["home"].get("tracker") == "Linear", f"an in-repository symlinked CLAUDE.md is parsed ({doc})")
    code, doc, _ = run_tree({"claude.md": "Rules.\n"}, ())
    ok(code == 5 and {"kind": "instructions", "path": "claude.md"} in doc["signals"],
       f"a lowercase claude.md is listed under its real name ({doc})")
    print("PASS: --discover holds on the twelfth reader's fixtures")


def case_discover_thirteenth_round():
    """The thirteenth blind reading (2026-11-06): an unreadable directory is no crash on any
    Python, and a README of any extension is read before seeding."""
    for dname in ("docs", ".claude", "docs/evidence", "docs/superpowers"):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            d = tree(t, {"CLAUDE.md": "Rules.\n", f"{dname}/x.md": "x\n"})
            os.chmod(d / dname, 0)
            try:
                code, doc, err = discover(d)
            finally:
                os.chmod(d / dname, 0o755)
            ok(code == 5 and "Traceback" not in err, f"unreadable {dname}/ is no crash ({code}, {err.strip()[:200]})")
    for name in ("README.markdown", "README.adoc", "README.txt", "README.ru.md"):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            code, doc, _ = discover(tree(t, {name: "Issues are tracked in Jira.\n"}))
            ok(code == 5 and {"kind": "instructions", "path": name} in doc["signals"],
               f"{name} is read before seeding ({doc})")
    print("PASS: --discover holds on the thirteenth reader's fixtures")


def case_discover_fourteenth_round():
    """The fourteenth blind reading (2026-11-06): a name that is not UTF-8 is no crash on a
    strict stdout; an unreadable docs/ alone is a signal; a lowercase .claude/claude.md is found."""
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = pathlib.Path(t)
        bad = os.fsencode(str(d)) + b"/README.fran\xe7ais"
        try:
            with open(bad, "wb") as fh:
                fh.write(b"x\n")
            made = True
        except OSError:
            made = False  # APFS refuses a name that is not UTF-8; the encoding path is still run below
        env = dict(os.environ, PYTHONIOENCODING="utf-8:strict")
        r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(d), "--discover"],
                           capture_output=True, text=True, timeout=60, env=env, errors="replace")
        ok("Traceback" not in r.stderr and r.returncode in (4, 5) and json.loads(r.stdout),
           f"a strict stdout does not crash (name made: {made}; {r.returncode}, {r.stderr.strip()[:200]})")
    import importlib.util
    import io
    spec = importlib.util.spec_from_file_location("bs_probe", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        real_listdir = os.listdir
        def listdir(path="."):
            names = real_listdir(path)
            return names + ["README.fran\udce7ais"] if os.path.samefile(path, t) else names
        out = io.TextIOWrapper(io.BytesIO(), encoding="utf-8", errors="strict")
        err = io.TextIOWrapper(io.BytesIO(), encoding="utf-8", errors="strict")
        saved = (mod.os.listdir, mod.sys.stdout, mod.sys.stderr)
        try:
            mod.os.listdir, mod.sys.stdout, mod.sys.stderr = listdir, out, err
            code = mod.main(["--root", t, "--discover"])
            out.flush()
        finally:
            mod.os.listdir, mod.sys.stdout, mod.sys.stderr = saved
        text = out.buffer.getvalue().decode("utf-8")
        ok(code == 5 and "README.fran" in text and json.loads(text)["signals"],
           f"main() on a strict stdout writes a name that is not UTF-8 as valid JSON ({code}, {text[:200]})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"docs/backlog.md": "x\n"})
        os.chmod(d / "docs", 0)
        try:
            code, doc, err = discover(d)
        finally:
            os.chmod(d / "docs", 0o755)
        if os.geteuid() != 0:
            ok(code == 5 and {"kind": "unreadable", "path": "docs"} in doc["signals"],
               f"an unreadable docs/ alone is a signal, not a seed ({code}, {doc})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        code, doc, _ = discover(tree(t, {".claude/claude.md": "Rules.\n"}))
        ok(code == 5 and {"kind": "instructions", "path": ".claude/claude.md"} in doc["signals"],
           f"a lowercase .claude/claude.md is found under its real name ({doc})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        code, doc, _ = discover(tree(t, {"readme-ru.md": "О проекте.\n"}))
        ok(code == 5, f"readme-ru.md is a README ({doc})")
    print("PASS: --discover holds on the fourteenth reader's fixtures")


def case_discover_fifteenth_round():
    """The fifteenth blind reading (2026-11-06): hostile nesting is a refusal, not a crash; the
    output is valid JSON on any stdout."""
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"CLAUDE.md": "Rules.\n",
                     ".claude/agent-sync.json": '{"idRegisters":' + "[" * 100000 + "]" * 100000 + "}"})
        code, doc, err = discover(d)
        ok("Traceback" not in err and code == 5 and "agent-sync.json" in err,
           f"a deeply nested agent-sync config is skipped aloud ({code}, {err.strip()[:160]})")
        (d / "docs").mkdir()
        (d / "docs" / "backlog-sources.json").write_text("[" * 200000 + "]" * 200000, encoding="utf-8")
        code, doc, err = discover(d)
        ok(code == 1 and "Traceback" not in err and "not readable JSON" in err,
           f"a deeply nested manifest is refused, not a crash ({code}, {err.strip()[:160]})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"README.français.md": "x\n", "docs/audits/q-remediation-queue.md": "x\n"})
        env = dict(os.environ, PYTHONIOENCODING="ascii:strict")
        r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(d), "--discover"],
                           capture_output=True, text=True, timeout=60, env=env, errors="replace")
        doc = json.loads(r.stdout)
        ok("Traceback" not in r.stderr and {"kind": "instructions", "path": "README.français.md"} in doc["signals"]
           or doc["home"], f"an ASCII stdout still gets valid JSON with the real name ({r.returncode}, {r.stdout[:200]})")
        os.chmod(d / "docs" / "audits", 0)
        try:
            code, doc, err = discover(d)
        finally:
            os.chmod(d / "docs" / "audits", 0o755)
        if os.geteuid() != 0:
            ok({"kind": "unreadable", "path": "docs/audits"} in doc["signals"], f"an unreadable docs/audits is a signal ({doc})")
    print("PASS: --discover holds on the fifteenth reader's fixtures")


def case_discover_sixteenth_round():
    """The sixteenth blind reading (2026-11-06): a manifest that parses but nests deeper than
    64 levels is refused before repr or jsonschema recurse; the plain CLI keeps its bytes on a
    surrogateescape stdout; tracker negation is linear."""
    import time
    for depth, field in ((990, "path"), (70000, "schema"), (100000, "schema")):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            g = copy.deepcopy(GOOD)
            deep = "[" * depth + "]" * depth
            text = json.dumps(g)
            text = text.replace('"schema": 1', '"schema": ' + deep) if field == "schema" else \
                text.replace('"path": "docs/backlog.md"', '"path": ' + deep, 1)
            d = repo(t, text)
            for extra in ((), ("--discover",)):
                r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(d), *extra],
                                   capture_output=True, text=True, timeout=120)
                ok(r.returncode == 1 and "Traceback" not in r.stderr,
                   f"{field} nested {depth} deep is refused, not a crash ({extra}, {r.returncode}, {r.stderr.strip()[:160]})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = repo(t, GOOD)
        env = dict(os.environ, PYTHONIOENCODING="utf-8:surrogateescape")
        r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(d), "--found", os.fsdecode(b"docs/caf\xe9.md")],
                           capture_output=True, timeout=60, env=env)
        ok(r.returncode == 3 and b"caf\xe9.md" in r.stdout and b"udce9" not in r.stdout,
           f"the plain CLI keeps raw bytes on a surrogateescape stdout ({r.returncode}, {r.stdout[-60:]!r})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"CLAUDE.md": "Linear " * 20000 + "\n"})
        t0 = time.monotonic()
        code, doc, _ = discover(d)
        ok(time.monotonic() - t0 < 10, f"20000 tracker mentions on one line read in seconds ({time.monotonic() - t0:.1f}s)")
    for depth, want in ((64, 0), (65, 1)):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            g = copy.deepcopy(GOOD)
            g["sources"][0]["excludeIds"] = ["B-001"]
            text = json.dumps(g).replace('"excludeIds": ["B-001"]', '"heading": "x"', 1)
            doc_ = json.loads(text)
            doc_["sources"][0]["excludeIds"] = json.loads("[" * (depth - 3) + '"B-001"' + "]" * (depth - 3))
            r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(repo(t, json.dumps(doc_)))],
                               capture_output=True, text=True, timeout=60)
            deep = "nested deeper than 64" in r.stderr
            ok(deep == bool(want), f"{depth} levels of containers: refused={deep}, want {bool(want)} ({r.stderr.strip()[:120]})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"CLAUDE.md": "not Linear " * 60 + "; open work is tracked in Linear.\n"})
        code, doc, _ = discover(d)
        ok(code == 0 and doc["home"].get("tracker") == "Linear", f"a stated tracker after 60 negated mentions is the home ({doc})")
    print("PASS: --discover holds on the sixteenth reader's fixtures")


def case_discover_twentyfirst_round():
    """The twenty-first blind reading (2026-11-06): many distinct negated paths are linear, and an
    instruction file is read up to 1 MB."""
    import time
    for n, note in ((30000, False), (160000, True)):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            text = "".join(f"do not file in docs/n{i}.md; " for i in range(n)) + "\n"
            d = tree(t, {"CLAUDE.md": text})
            r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(d), "--discover"],
                               capture_output=True, text=True, timeout=120)
            ok(r.returncode == 5 and "Traceback" not in r.stderr
               and (("only the first part was read" in r.stderr) == note),
               f"{n} negated paths ({len(text)} bytes): exit 5, cap note={note} ({r.returncode}, {r.stderr.strip()[-160:]})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        text = "".join(f"do not file in docs/n{i}.md; " for i in range(30000)) + "\n"
        d = tree(t, {"CLAUDE.md": text})
        t0 = time.monotonic()
        subprocess.run([sys.executable, str(SCRIPT), "--root", str(d), "--discover"],
                       capture_output=True, timeout=120)
        ok(time.monotonic() - t0 < 30, f"30000 negated paths read in seconds ({time.monotonic() - t0:.1f}s)")
    import resource
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = pathlib.Path(t)
        (d / "docs").mkdir()
        for i in range(8000):
            (d / "docs" / f"backlog-{i}.md").write_text("x\n", encoding="utf-8")
        (d / "CLAUDE.md").write_text("".join("Open work: " + ", ".join(f"docs/backlog-{i}.md" for i in range(k, k + 10)) + "\n"
                                             for k in range(0, 8000, 10))
                                     + "Open work is tracked in docs/backlog-0.md. " * 2000 + "\n", encoding="utf-8")
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(d), "--discover"],
                           capture_output=True, text=True, timeout=120)
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
        ok(r.returncode == 0 and json.loads(r.stdout)["home"]["path"] == "docs/backlog-0.md" and cpu < 20,
           f"8000 files in one folder, 10000 mentions: directories are listed once ({cpu:.1f}s CPU, {r.returncode})")
    print("PASS: --discover holds on the twenty-first reader's fixtures")


def case_discover_twentythird_round():
    """The twenty-third blind reading (2026-11-06): a path 340 directories deep cost one lstat and
    one listing per prefix, each walking the prefix again; a mention is a board path only up to
    16 segments, and each prefix is checked once per run."""
    import resource
    for depth, home in ((15, True), (16, False)):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            path = "/".join(["s"] * depth) + "/backlog.md"
            d = tree(t, {path: "| ID |\n", "CLAUDE.md": f"Open work is tracked in {path}.\n"})
            code, doc, _ = discover(d)
            ok((code == 0 and doc["home"]["path"] == path) if home else code == 5,
               f"a board {depth} directories down: home={home} ({code}, {doc.get('home')})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = pathlib.Path(t)
        spine = "/".join(["s"] * 300)
        (d / spine).mkdir(parents=True)
        for i in range(1500):
            (d / spine / f"backlog-{i}.md").write_text("x\n", encoding="utf-8")
        (d / "CLAUDE.md").write_text("".join(f"Open work: {spine}/backlog-{i}.md\n" for i in range(1500)),
                                     encoding="utf-8")
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(d), "--discover"],
                           capture_output=True, text=True, timeout=120)
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
        ok(r.returncode == 5 and "Traceback" not in r.stderr and cpu < 10,
           f"1500 boards 300 directories down: not homes, read in seconds ({cpu:.1f}s CPU, {r.returncode})")
    print("PASS: --discover holds on the twenty-third reader's fixtures")


def _module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("backlog_sources_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def case_discover_twentyfourth_round():
    """The twenty-fourth blind reading (2026-11-06): the depth bound held only for paths named in
    text, so agent-sync and tracked files still walked 340-deep chains; a stated board past the
    bound was dropped and a roadmap became the home; the lstat memo, the listing reset and the
    tracked-file dedupe had no test."""
    deep = "/".join(["s"] * 20) + "/backlog.md"
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {deep: "| ID |\n", "docs/ROADMAP.md": "- [ ] x\n",
                     "CLAUDE.md": f"Open work is tracked in {deep}.\n"})
        code, doc, _ = discover(d)
        ok(code == 5 and doc["home"] is None
           and any(sg["kind"] == "too-deep" and sg["path"] == deep for sg in doc["signals"]),
           f"a stated board past the bound is a signal, and a roadmap beside it is not the home ({code}, {doc})")
    mod = _module()
    real_listdir, real_islink = os.listdir, os.path.islink
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {deep: "| ID |\n", ".claude/agent-sync.json": json.dumps(
            {"idRegisters": {"b": {"file": deep}}, "claimTags": {deep: "x"}})})
        subprocess.run(["git", "-C", str(d), "init", "-q"], check=True)
        tracked = "t/" + "/".join(["u"] * 20) + "/backlog.md"
        (d / tracked).parent.mkdir(parents=True)
        (d / tracked).write_text("type: report\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(d), "add", "-A"], check=True)
        calls = []
        try:
            os.listdir = lambda p=".": calls.append(os.fspath(p)) or real_listdir(p)
            os.path.islink = lambda p: calls.append(os.fspath(p)) or real_islink(p)
            code, doc, _ = mod.discover(d, "docs/evidence")
        finally:
            os.listdir, os.path.islink = real_listdir, real_islink
        walked = [c for c in calls if c.count("/s/") + c.count("/u/") >= 15]
        ok(walked == [] and doc["agentSync"]["files"] == [] and code == 5
           and any(sg.get("path") == tracked for sg in doc["signals"])
           and {"kind": "too-deep", "path": deep, "where": ".claude/agent-sync.json"} in doc["signals"],
           f"agent-sync and tracked paths past the bound are not walked ({len(walked)} deep calls, {doc['signals']})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {".claude/agent-sync.json": json.dumps({"idRegisters": {"b": {"file": deep}}})})
        code, doc, _ = discover(d)
        ok(code == 5 and "deep" not in doc["agentSync"],
           f"agent-sync naming only a board too deep to walk: exit 5, not a seed ({code}, {doc['agentSync']})")
        g = ["git", "-C", str(d)]
        subprocess.run(g + ["init", "-q"], check=True)
        for i in range(210):
            tree(t, {f"r{i}/backlog.md": "type: report\n"})
        os.remove(d / ".claude/agent-sync.json")
        subprocess.run(g + ["add", "-A"], check=True)
        code, doc, _ = discover(d)
        ok(code == 5 and sum(sg["kind"] == "tracked-file" for sg in doc["signals"]) == 10,
           f"past 200 tracked files checked, the rest are signals unread, not a seed ({code})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        spine = "/".join(["s"] * 14)
        d = tree(t, {f"{spine}/backlog-{i}.md": "x\n" for i in range(200)})
        (d / "CLAUDE.md").write_text("".join(f"Open work: {spine}/backlog-{i}.md\n" for i in range(200)),
                                     encoding="utf-8")
        links = []
        try:
            os.path.islink = lambda p: links.append(os.fspath(p)) or real_islink(p)
            code, doc, _ = mod.discover(d, "docs/evidence")
        finally:
            os.path.islink = real_islink
        ok(code == 0 and len(links) < 400,
           f"200 boards 14 directories down: each prefix checked once ({len(links)} lstat calls, {code})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = pathlib.Path(t)
        first = mod.discover(d, "docs/evidence")
        tree(t, {"docs/backlog.md": "| ID |\n"})
        second = mod.discover(d, "docs/evidence")
        ok(first[0] == 4 and second[0] == 0 and second[1]["home"]["path"] == "docs/backlog.md",
           f"a second run in one process sees a board made after the first ({first[0]}, {second[0]})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = pathlib.Path(t)
        g = ["git", "-C", str(d), "-c", "user.email=t@t", "-c", "user.name=t"]
        subprocess.run(g + ["init", "-q", "-b", "main"], check=True)
        tree(t, {"n/backlog.md": "a\n"})
        subprocess.run(g + ["add", "-A"], check=True)
        subprocess.run(g + ["commit", "-qm", "a"], check=True)
        subprocess.run(g + ["checkout", "-qb", "other"], check=True)
        tree(t, {"n/backlog.md": "b\n"})
        subprocess.run(g + ["commit", "-qam", "b"], check=True)
        subprocess.run(g + ["checkout", "-q", "main"], check=True)
        tree(t, {"n/backlog.md": "c\n"})
        subprocess.run(g + ["commit", "-qam", "c"], check=True)
        subprocess.run(g + ["merge", "-q", "other"], capture_output=True)
        code, doc, _ = discover(d)
        hits = [sg for sg in doc["signals"] if sg.get("path") == "n/backlog.md"]
        ok(code == 5 and len(hits) == 1, f"a conflicted backlog file is one signal, not one per stage ({hits})")
    print("PASS: --discover holds on the twenty-fourth reader's fixtures")


def case_discover_twentyfifth_round():
    """The twenty-fifth blind reading (2026-11-06): a board path the walk refuses (hidden, over
    700 characters, a symlink) or an agent-sync register that is absent vanished, so a roadmap
    became the home or the run seeded; an unreadable docs/ read as "no manifest"."""
    long = "/".join([f"d{i:02d}" + "x" * 72 for i in range(10)]) + "/backlog.md"
    cases = {
        "long board stated": ({long: "| ID |\n", "docs/ROADMAP.md": "- [ ] x\n",
                               "CLAUDE.md": f"Open work is tracked in {long}.\n"}, None),
        "absent register": ({".claude/agent-sync.json": json.dumps({"idRegisters": {"b": {"file": "docs/backlog.md"}}})}, None),
        "hidden register": ({".planning/backlog.md": "| ID |\n", "docs/ROADMAP.md": "- [ ] x\n",
                             ".claude/agent-sync.json": json.dumps({"idRegisters": {"b": {"file": ".planning/backlog.md"}}})}, None),
        "linked known board": ({"work/rows.md": "| ID |\n"}, ("work/rows.md", "docs/backlog.md")),
    }
    for what, (files, link) in cases.items():
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            d = tree(t, files)
            if link:
                (d / link[1]).parent.mkdir(parents=True, exist_ok=True)
                os.symlink(d / link[0], d / link[1])
            code, doc, _ = discover(d)
            kinds = {sg["kind"] for sg in doc["signals"]}
            ok(code == 5 and doc["home"] is None and kinds & {"unwalked", "agent-sync-register", "too-deep"},
               f"{what}: a signal, not a seed and not a roadmap home ({code}, {doc['home']}, {doc['signals']})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {".planning/BACKLOG.md": "| ID |\n"})
        subprocess.run(["git", "-C", str(d), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(d), "add", "-A"], check=True)
        code, doc, _ = discover(d)
        ok(code == 5 and {"kind": "tracked-file", "path": ".planning/BACKLOG.md"} in doc["signals"],
           f"a tracked hidden backlog is a signal unread ({code}, {doc['signals']})")
    deep = "/".join(["s"] * 20) + "/backlog.md"
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {deep: "| ID |\n", "docs/tasks-board.md": "| ID |\n",
                     "CLAUDE.md": f"Open work is tracked in {deep}. Open work is tracked in docs/tasks-board.md.\n"})
        code, doc, _ = discover(d)
        ok(code == 0 and doc["home"]["path"] == "docs/tasks-board.md",
           f"a shallow stated board still wins over a deep one ({code}, {doc['home']})")
        (d / "CLAUDE.md").write_text(f"Open work is tracked in {deep}.\nOpen work is tracked in Linear.\n",
                                     encoding="utf-8")
        code, doc, _ = discover(d)
        ok(code == 0 and doc["home"].get("tracker") == "Linear",
           f"a stated tracker still wins over a deep board ({code}, {doc['home']})")
    if os.name == "posix" and os.geteuid() != 0:
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            d = tree(t, {"docs/backlog-sources.json": "{}"})
            os.chmod(d / "docs", 0)
            try:
                r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(d)], capture_output=True, text=True, timeout=60)
            finally:
                os.chmod(d / "docs", 0o755)
            ok(r.returncode == 1 and "not readable (PermissionError)" in r.stdout + r.stderr and "Traceback" not in r.stderr,
               f"a manifest behind an unreadable docs/ is not read as absent ({r.returncode}, {(r.stdout + r.stderr).strip()[:160]})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"work/rows.md": "| ID |\n", "docs/TODO.md": "- [ ] x\n"})
        os.symlink(d / "work" / "rows.md", d / "work" / "backlog.md")
        subprocess.run(["git", "-C", str(d), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(d), "add", "-A"], check=True)
        os.remove(d / "docs" / "TODO.md")
        tree(t, {"docs/TODO.md": "- [ ] x\n"})
        code, doc, _ = discover(d)
        paths = {sg.get("path") for sg in doc["signals"] if sg["kind"] == "tracked-file"}
        ok(code == 5 and {"work/backlog.md", "docs/TODO.md"} <= paths,
           f"a tracked link named backlog and a tracked board-named file are signals, not a seed ({code}, {doc['signals']})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"src/main.py": "x\n"})
        (d / "docs").mkdir()
        os.symlink("backlog-sources.json", d / "docs" / "backlog-sources.json")
        r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(d)], capture_output=True, text=True, timeout=60)
        code, doc, _ = discover(d)
        ok(r.returncode == 0 and "no docs/backlog-sources.json" in r.stdout + r.stderr and code == 4,
           f"a manifest link that loops reads as absent in both modes, as in 1.102.4 ({r.returncode}, {code})")
    print("PASS: --discover holds on the twenty-fifth reader's fixtures")


def case_discover_twentyeighth_round():
    """The twenty-eighth blind reading (2026-11-07): a manifest path past the platform's limit
    read as "no manifest" (exit 0) where 1.102.4 exited 1; and with a home elsewhere, --discover
    passed over a manifest it could not look at."""
    if os.name != "posix":
        return
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        limit = os.pathconf(t, "PC_PATH_MAX")
        root = pathlib.Path(t)
        while len(str(root)) < limit - 12:  # the root fits; root/docs/backlog-sources.json does not
            root = root / ("r" * max(1, min(100, limit - 12 - len(str(root)) - 1)))
        os.makedirs(root)
        cwd = os.getcwd()
        os.chdir(root)
        try:
            os.makedirs("docs")
            pathlib.Path("docs/backlog-sources.json").write_text('{"schema": 2}', encoding="utf-8")
            pathlib.Path("docs/backlog.md").write_text("| ID |\n", encoding="utf-8")
        finally:
            os.chdir(cwd)
        r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root)], capture_output=True, text=True, timeout=60)
        out = r.stdout + r.stderr
        ok(r.returncode == 1 and "not readable" in out and "Traceback" not in out,
           f"a manifest past the path limit is not read as absent ({r.returncode}, {out.strip()[:160]})")
        code, doc, err = discover(root)
        ok(code == 5 and doc["home"] is None and {"kind": "unreadable", "path": "docs/backlog-sources.json"} in doc["signals"],
           f"--discover guesses no home past a manifest it cannot read ({code}, {doc and doc['home']})")
    if os.geteuid() != 0:
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            d = tree(t, {"docs/backlog-sources.json": "{}", "BACKLOG.md": "| ID |\n"})
            os.chmod(d / "docs", 0o600)
            try:
                code, doc, _ = discover(d)
            finally:
                os.chmod(d / "docs", 0o755)
            ok(code == 5 and doc["home"] is None,
               f"an unsearchable docs/ holding a manifest stops a root BACKLOG.md becoming the home ({code}, {doc and doc['home']})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"docs": "a file, not a folder\n", "src/main.py": "x\n"})
        r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(d)], capture_output=True, text=True, timeout=60)
        code, doc, err = discover(d)
        ok(r.returncode == 0 and "no docs/backlog-sources.json" in r.stdout + r.stderr and code == 4,
           f"docs as a regular file is no manifest, as in 1.102.4 ({r.returncode}, {code})")
    if os.geteuid() != 0:
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            d = tree(t, {"docs/backlog-sources.json": "{}", "BACKLOG.md": "| ID |\n",
                         "CLAUDE.md": "Open work is tracked in BACKLOG.md.\n"})
            os.chmod(d / "docs", 0o600)
            try:
                code, doc, err = discover(d)
            finally:
                os.chmod(d / "docs", 0o755)
            ok(code == 0 and doc["home"]["path"] == "BACKLOG.md" and "docs/backlog-sources.json: not readable" in err,
               f"a stated home stands past an unreadable manifest, with the note on stderr ({code}, {err.strip()[-160:]})")
    print("PASS: --discover holds on the twenty-eighth reader's fixtures")


def case_discover_thirtieth_round():
    """The thirtieth blind reading (2026-11-07): a project that moved its artifacts root
    (`paths.artifacts`) keeps its board at `<root>/backlog.md`; 1.102.4 read it there, and
    --discover probed only the fixed list, so it reported no board and printed that same file
    as the path to seed."""
    for art in ("docs/runs", ".pipeline"):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            d = tree(t, {f"{art}/backlog.md": "| ID | Status |\n|---|---|\n| B-1 | open |\n", "src/main.py": "x\n"})
            code, doc, _ = discover(d, "--artifacts", art)
            ok(code == 0 and doc["home"]["path"] == f"{art}/backlog.md" and doc["seed"] is None,
               f"the board under a moved artifacts root ({art}) is the home, never a seed ({code}, {doc['home']}, {doc['seed']})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"docs/superpowers/backlog.md": "| ID |\n", "docs/backlog.md": "| ID |\n", "README.md": "x\n"})
        code, doc, _ = discover(d, "--artifacts", "docs/superpowers")
        ok(code == 0 and doc["home"]["path"] == "docs/superpowers/backlog.md",
           f"the run's own board outranks an older docs/backlog.md beside it ({code}, {doc['home']})")
        code, doc, _ = discover(d)
        ok(code == 0 and doc["home"]["path"] == "docs/backlog.md",
           f"with the default root the fixed order stands ({code}, {doc['home']})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"src/main.py": "x\n", "elsewhere.md": "| ID |\n"})
        (d / "docs" / "runs").mkdir(parents=True)
        os.symlink(d / "elsewhere.md", d / "docs" / "runs" / "backlog.md")
        code, doc, _ = discover(d, "--artifacts", "docs/runs")
        ok(code == 5 and doc["seed"] is None and any(sg.get("path") == "docs/runs/backlog.md"
                                                     and sg["kind"] in ("unwalked", "seed-path-taken") for sg in doc["signals"]),
           f"a seed path already taken is a signal, never seeded over ({code}, {doc['signals']})")
    for art in ("docs/runs", ".pipeline"):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            d = tree(t, {"board.md": "| ID |\n", "docs/backlog.md": "| ID |\n", "README.md": "x\n"})
            (d / art).mkdir(parents=True, exist_ok=True)
            os.symlink(d / "board.md", d / art / "backlog.md")
            code, doc, _ = discover(d, "--artifacts", art)
            ok(code == 5 and doc["home"] is None
               and {"kind": "seed-path-taken", "path": f"{art}/backlog.md", "where": "known path"} in doc["signals"],
               f"the run's own board as a link under {art} is a signal and stops a fallback home ({code}, {doc['home']})")
    for target in ("nowhere.md", "backlog.md"):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            d = tree(t, {"src/main.py": "x\n"})
            (d / "docs" / "runs").mkdir(parents=True)
            os.symlink(target, d / "docs" / "runs" / "backlog.md")  # dangling, or a loop onto itself
            code, doc, _ = discover(d, "--artifacts", "docs/runs")
            ok(code == 5 and doc["seed"] is None and any(sg["kind"] == "seed-path-taken" and sg.get("path") == "docs/runs/backlog.md"
                                                         for sg in doc["signals"]),
               f"a dangling or looping link at the seed path is taken, never seeded through ({target}: {code}, {doc['signals']})")
    # Round 32: an own board behind a link out of the repository, or under another letter case.
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t, tempfile.TemporaryDirectory(prefix="tp-bdisc-out-") as out:
        pathlib.Path(out, "backlog.md").write_text("| ID |\n", encoding="utf-8")
        for beside in (True, False):
            d = pathlib.Path(t) / ("a" if beside else "b")
            files = {"README.md": "x\n"}
            if beside:
                files["docs/backlog.md"] = "| ID |\n"
            tree(str(d), files)
            (d / "docs" / "evidence").mkdir(parents=True, exist_ok=True)
            os.symlink(pathlib.Path(out, "backlog.md"), d / "docs" / "evidence" / "backlog.md")
            code, doc, _ = discover(d)
            ok(code == 5 and doc["home"] is None and doc["seed"] is None
               and {"kind": "seed-path-taken", "path": "docs/evidence/backlog.md", "where": "known path"} in doc["signals"],
               f"an own board linked out of the repository is a signal (docs/backlog.md beside: {beside}; {code}, {doc['home']})")
    probe = tempfile.mkdtemp(prefix="tp-bdisc-case-")
    pathlib.Path(probe, "x").write_text("x", encoding="utf-8")
    insensitive = os.path.exists(os.path.join(probe, "X"))
    shutil.rmtree(probe)
    if insensitive:
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            d = tree(t, {"docs/Evidence/backlog.md": "| ID |\n", "docs/backlog.md": "| ID |\n", "README.md": "x\n"})
            code, doc, _ = discover(d)
            ok(code == 5 and doc["home"] is None
               and {"kind": "seed-path-taken", "path": "docs/evidence/backlog.md", "where": "known path"} in doc["signals"],
               f"an own board under another letter case is a signal, not lost to docs/backlog.md ({code}, {doc['home']})")
            code, doc, _ = discover(d, "--artifacts", "Docs")
            ok(code == 0 and doc["home"]["path"] == "docs/backlog.md",
               f"an own path that is the found board under another case is not a signal ({code}, {doc['home']})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"rows.md": "| ID |\n", "src/main.py": "x\n"})
        (d / "docs").mkdir()
        os.symlink("../rows.md", d / "docs" / "backlog.md")
        code, doc, _ = discover(d, "--artifacts", "docs")
        hits = [sg for sg in doc["signals"] if sg.get("path") == "docs/backlog.md"]
        ok(code == 5 and len(hits) == 1, f"an own path that is also a known path is one signal, not two ({hits})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"src/main.py": "x\n"})
        deep = "/".join(["a"] * 20)
        code, doc, _ = discover(d, "--artifacts", deep)
        ok(code == 4 and doc["seed"] == f"{deep}/backlog.md", f"a deep root with nothing there is still where the seed goes ({code})")
    # Round 33: a frozen own board that points elsewhere is read, not lost to docs/backlog.md.
    for pointer in ("open work moved to ../proj-data/backlog.md", "open work moved to Linear (team PRJ)"):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            d = tree(t, {"docs/evidence/backlog.md": f"# Backlog\n\nFrozen 2026-09-01: {pointer}.\n\n| ID |\n",
                         "docs/backlog.md": "| ID |\n", "README.md": "x\n"})
            code, doc, _ = discover(d)
            ok(code == 5 and doc["home"] is None
               and [sg for sg in doc["signals"] if sg["kind"] == "seed-path-taken"] == [
                   {"kind": "seed-path-taken", "path": "docs/evidence/backlog.md", "where": "known path"}],
               f"a frozen own board stops a fallback home and is named once ({pointer}: {code}, {doc['home']}, {doc['signals']})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t, tempfile.TemporaryDirectory(prefix="tp-bdisc-out-") as out:
        pathlib.Path(out, "backlog.md").write_text("| ID |\n", encoding="utf-8")
        d = tree(t, {"README.md": "x\n"})
        (d / "docs" / "evidence").mkdir(parents=True)
        os.symlink(pathlib.Path(out, "backlog.md"), d / "docs" / "evidence" / "backlog.md")
        code, doc, _ = discover(d)
        ok(len([sg for sg in doc["signals"] if sg["kind"] == "seed-path-taken"]) == 1,
           f"a link out at the seed path is named once, not twice ({doc['signals']})")
    # Round 35: the own board is a live candidate, something else empties the home.
    for name, extra in (("roadmap link", None), ("absent register", {".claude/agent-sync.json": json.dumps(
            {"idRegisters": {"d": {"file": "docs/decisions-backlog.md"}}})})):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            files = {"docs/evidence/backlog.md": "| ID | Status |\n|---|---|\n| B-1 | open |\n", "README.md": "x\n",
                     "shared/roadmap.md": "- [ ] x\n"}
            files.update(extra or {})
            d = tree(t, files)
            if extra is None:
                os.symlink("../shared/roadmap.md", d / "docs" / "ROADMAP.md")
            code, doc, _ = discover(d)
            ok(code == 5 and doc["seed"] is None and [sg for sg in doc["signals"] if sg["kind"] == "seed-path-taken"] == [
                {"kind": "seed-path-taken", "path": "docs/evidence/backlog.md", "where": "known path"}],
               f"a live own board without a home is still a taken seed path, named once ({name}: {code}, {doc['signals']})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"old/board.md": "| ID |\n", "README.md": "x\n"})
        (d / "docs" / "evidence").mkdir(parents=True)
        os.symlink("../../old/board.md", d / "docs" / "evidence" / "backlog.md")
        code, doc, _ = discover(d)
        ok({"kind": "seed-path-taken", "path": "docs/evidence/backlog.md", "where": "known path"} in doc["signals"],
           f"an in-repo link at the seed path is named seed-path-taken, the kind the doctrine protects ({doc['signals']})")
    # Round 36: the seed path named first by an instruction line or agent-sync is still taken.
    for name, extra in (("instruction line", {"CLAUDE.md": "Open work is tracked in docs/evidence/backlog.md.\n"}),
                        ("agent-sync register", {".claude/agent-sync.json": json.dumps(
                            {"idRegisters": {"b": {"file": "docs/evidence/backlog.md"}}})})):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            files = {"old/board.md": "# Board\n\nFrozen 2026-09-01: superseded.\n\n| ID |\n", "README.md": "x\n"}
            files.update(extra)
            d = tree(t, files)
            (d / "docs" / "evidence").mkdir(parents=True)
            os.symlink("../../old/board.md", d / "docs" / "evidence" / "backlog.md")
            code, doc, _ = discover(d)
            ok(code == 5 and doc["seed"] is None and [sg for sg in doc["signals"] if sg["kind"] == "seed-path-taken"] == [
                {"kind": "seed-path-taken", "path": "docs/evidence/backlog.md", "where": "known path"}],
               f"an occupied seed path that {name} named first is still taken, once ({code}, {doc['signals']})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"docs/evidence/backlog.md": "| ID |\n", "README.md": "x\n"})
        code, doc, _ = discover(d)
        ok(code == 0 and doc["home"]["path"] == "docs/evidence/backlog.md" and doc["signals"] == [],
           f"the own board as the home carries no signal ({code}, {doc['signals']})")
    probe = tempfile.mkdtemp(prefix="tp-bdisc-case-")
    pathlib.Path(probe, "x").write_text("x", encoding="utf-8")
    insensitive = os.path.exists(os.path.join(probe, "X"))
    shutil.rmtree(probe)
    if insensitive:
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            d = tree(t, {"docs/evidence/backlog.md": "| ID |\n", "README.md": "x\n", "shared/roadmap.md": "- [ ] x\n"})
            os.symlink("../shared/roadmap.md", d / "docs" / "ROADMAP.md")
            code, doc, _ = discover(d, "--artifacts", "docs/Evidence")
            ok(code == 5 and {"kind": "seed-path-taken", "path": "docs/Evidence/backlog.md", "where": "known path"} in doc["signals"],
               f"the own path spelt in another case over a found board is still taken when no home stands ({code}, {doc['signals']})")
    if os.geteuid() != 0:
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            d = tree(t, {".pipeline/backlog.md": "| ID |\n"})
            os.chmod(d / ".pipeline", 0)
            try:
                code, doc, _ = discover(d, "--artifacts", ".pipeline")
            finally:
                os.chmod(d / ".pipeline", 0o755)
            ok(code == 5 and doc["seed"] is None and {"kind": "unreadable", "path": ".pipeline"} in doc["signals"],
               f"an unreadable artifacts root is a signal, never a blind seed ({code}, {doc['signals']})")
    # Round 37: a directory that can be entered but not listed (0o311) is unreadable too.
    if os.geteuid() != 0:
        for dname, art in (("docs", None), (".pipeline", ".pipeline")):
            with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
                d = tree(t, {f"{dname}/backlog.md": "| ID |\n|---|\n| B-1 | open |\n"})
                os.chmod(d / dname, 0o311)
                try:
                    code, doc, _ = discover(d, *(("--artifacts", art) if art else ()))
                finally:
                    os.chmod(d / dname, 0o755)
                ok(code == 5 and doc["seed"] is None and {"kind": "unreadable", "path": dname} in doc["signals"],
                   f"{dname}/ that can be entered but not listed is unreadable, never a blind seed ({code}, {doc['signals']})")
    # Round 38: a long board header is read in one pass; a long link chain is a signal, not a crash.
    import resource
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {"docs/evidence/backlog.md": "# Backlog " + "a.md " * 32000 + "frozen 2026-09-01\n\n| ID |\n",
                     "README.md": "x\n"})
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        code, doc, err = discover(d)
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
        # The marker belongs to the last path before it ("a.md ... frozen"), as before; only the cost changed.
        ok(code == 0 and doc["home"]["path"] == "docs/evidence/backlog.md" and cpu < 10,
           f"a 160 KB header naming another file as frozen is read in one pass ({cpu:.1f}s CPU, {code})")
        (d / "docs" / "evidence" / "backlog.md").write_text("# Backlog " + "a.md; " * 32000 + "this board is frozen 2026-09-01\n\n| ID |\n",
                                                          encoding="utf-8")
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        code, doc, err = discover(d)
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
        ok(code == 5 and "docs/evidence/backlog.md" in doc["negated"] and cpu < 10,
           f"a 160 KB header freezing this board is read in one pass ({cpu:.1f}s CPU, {code})")
    for head in ("docs/backlog.md", "CLAUDE.md"):
        with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
            d = tree(t, {"l/real.md": "| ID |\n", "README.md": "x\n"})
            prev = "real.md"
            for i in range(1500):
                os.symlink(prev, d / "l" / f"h{i}.md")
                prev = f"h{i}.md"
            (d / head).parent.mkdir(parents=True, exist_ok=True)
            os.symlink(os.path.relpath(d / "l" / prev, (d / head).parent), d / head)
            r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(d), "--discover"],
                               capture_output=True, text=True, timeout=120)
            ok(r.returncode == 5 and "Traceback" not in r.stderr and json.loads(r.stdout)["seed"] is None,
               f"a 1,500-link chain at {head} is a signal, not a traceback ({r.returncode}, {r.stderr.strip()[-160:]})")
    with tempfile.TemporaryDirectory(prefix="tp-bdisc-") as t:
        d = tree(t, {".claude/agent-sync.json": "{nope"})
        code, doc, _ = discover(d)
        ok(code == 5 and {"kind": "unreadable", "path": ".claude/agent-sync.json"} in doc["signals"],
           f"an agent-sync config that cannot be read is a signal on its own, never a seed ({code}, {doc['signals']})")
    print("PASS: --discover holds on the thirtieth reader's fixtures")


if __name__ == "__main__":
    for case in (case_no_manifest, case_good_manifest, case_malformed, case_symlinked_source,
                 case_undeclared_finding, case_doctrine_names_script,
                 case_hand_rules_without_jsonschema, case_discover_nothing_seeds,
                 case_discover_existing_plain_board, case_discover_order_and_ambiguity,
                 case_discover_instruction_rules, case_discover_agent_sync,
                 case_discover_refuses_escape, case_discover_review_round,
                 case_discover_second_round, case_discover_third_round,
                 case_discover_fourth_round, case_discover_fifth_round,
                 case_discover_sixth_round, case_discover_seventh_round,
                 case_discover_eighth_round, case_discover_ninth_round,
                 case_discover_tenth_round, case_discover_eleventh_round,
                 case_discover_twelfth_round, case_discover_thirteenth_round,
                 case_discover_fourteenth_round, case_discover_fifteenth_round,
                 case_discover_sixteenth_round, case_discover_twentyfirst_round,
                 case_discover_twentythird_round, case_discover_twentyfourth_round,
                 case_discover_twentyfifth_round, case_discover_twentyeighth_round,
                 case_discover_thirtieth_round):
        case()
    print(f"PASS: backlog_sources.py — {CASES} cases")
