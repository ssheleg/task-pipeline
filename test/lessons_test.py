#!/usr/bin/env python3
"""The local lesson index (`scripts/lessons.py`, lesson/1) — stdlib only.

CHANGELOG, Unreleased (lessons across projects). A retro entry that carries a `**Lesson:**` line is a lesson; the local
index projects every such entry from every project's retro into one file, so an agent on
another project reads it at stage 0 without any service. These cases drive the real script
as a process, against git repositories made in temp directories, with `HOME` pointed at a
temp directory too — no case can reach the operator's real index:

  * two projects that learned one class: `query` prints it once, `projects 2`;
  * a lesson that carries an absolute path, a URL or a credential shape is refused, and the
    index is byte-identical after the refusal;
  * `rebuild` from the retros equals the index built by `add`, byte for byte;
  * the index directory is 0700 and the file 0600;
  * a held lock makes `add` refuse after its timeout and write nothing; four concurrent
    writers lose no entry;
  * a repeat from the same project revises, never mints; `candidates` lists only lessons
    two projects hold;
  * `emit-observatory` prints the store's arguments, `record` keeps the memory id and turns
    a refusal into one ledger line;
  * the index path is a parameter, `TASK_PIPELINE_LESSONS` its environment form.

Run bare: prints PASS and exits non-zero on the first failure.
"""
import atexit
import json
import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugins" / "task-pipeline" / "skills" / "task-pipeline" / "scripts" / "lessons.py"
SCHEMA = ROOT / "plugins" / "task-pipeline" / "skills" / "task-pipeline" / "templates" / "lesson.schema.json"
_TREES = []
atexit.register(lambda: [shutil.rmtree(t, ignore_errors=True) for t in _TREES])
CASES = 0


def ok(cond, what):
    global CASES
    CASES += 1
    if not cond:
        print(f"FAIL: {what}")
        sys.exit(1)


def tree(prefix):
    d = pathlib.Path(tempfile.mkdtemp(prefix=prefix))
    _TREES.append(d)
    return d


HOME = tree("tp-lessons-home-")


def run(*args, cwd=None, stdin=None, index=None, env_extra=None):
    env = {k: v for k, v in os.environ.items() if k != "TASK_PIPELINE_LESSONS"}
    env["HOME"] = str(HOME)
    if env_extra:
        env.update(env_extra)
    argv = [sys.executable, str(SCRIPT), *args]
    if index is not None:
        argv += ["--index", str(index)]
    # Decoded as UTF-8 whatever the locale: the harness must not be the locale-dependent part.
    r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", input=stdin, timeout=120, env=env)
    return r.returncode, r.stdout, r.stderr


def git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
    r = subprocess.run(["git", "-c", "commit.gpgsign=false", *args], cwd=repo,
                       capture_output=True, text=True, env=env, timeout=30)
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {r.stderr}")
    return r.stdout.strip()


# The store's own redactor: the public engine's `memory_redact.Redactor`, imported from the
# checkout `OBSERVATORY_ENGINE_DIR` names (its `observatory/engine` directory). No default: a
# path on one machine has no place in a public test. Unset or unimportable, the redactor case
# is SKIPPED and says why; the shape cases around it still run.
ENGINE_DIR = os.environ.get("OBSERVATORY_ENGINE_DIR")
REDACTOR = None
redact = None
if ENGINE_DIR:
    try:
        sys.path.insert(0, ENGINE_DIR)
        import memory_redact as _mr  # noqa: E402
        REDACTOR = f"engine memory_redact from $OBSERVATORY_ENGINE_DIR"

        def redact(value):
            return _mr.Redactor(known_loader=lambda: {}).scrub(value)[0]
    except Exception as exc:  # noqa: BLE001 — named in the skip line below
        REDACTOR = None
        SKIP_WHY = f"OBSERVATORY_ENGINE_DIR is set but memory_redact did not import ({type(exc).__name__})"
else:
    SKIP_WHY = "OBSERVATORY_ENGINE_DIR is unset — the engine's redactor is not on this machine's path"


ENTRY = """### 2026-10-0{n} · `{topic}` · gate 6 reopened twice

- **Symptom:** the export passed its gate with no file written
- **Surfaced at:** stage 6 · **Owned by:** stage 4 (the plan never named the check)
- **Root cause:** the plan's check asserted the success line, not the artefact
- **Fix:** grade 1 (mechanical) — the check reads the artefact
- **The check:** `test/export_test.py` asserts the file exists and is non-empty
- **Lesson:** `absence-needs-its-own-check` — a check that reads a success line passes when the artefact is absent · **When:** a gate verifies an output by its log line · **Nouns:** gate, artefact, success line, absence
- **Commit:** `{sha}`
"""

PRIVATE = """### 2026-10-01 · `{topic}` · the staging host was down

- **Symptom:** deploy failed
- **Surfaced at:** stage 7 · **Owned by:** stage 7
- **Root cause:** a host outage
- **Fix:** grade 3 — retry
- **The check:** none
- **Commit:** `{sha}`
"""


def project(name, n):
    """A git repository whose retro carries one lesson entry and one private entry."""
    repo = tree(f"tp-lessons-{name}-")
    git(repo, "init", "-q")
    (repo / "README.md").write_text(f"# {name}\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "root")
    (repo / "fix.txt").write_text("fixed\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "the fix")
    sha = git(repo, "rev-parse", "HEAD")
    art = repo / "docs" / "evidence"
    art.mkdir(parents=True)
    retro = ("# Pipeline retrospective\n\n## Recent log — narrative entries\n\n"
             + ENTRY.format(n=n, topic=f"{name}-export", sha=sha) + "\n"
             + PRIVATE.format(topic=f"{name}-deploy", sha=sha) + "\n## Run stamps\n")
    (art / "retro.md").write_text(retro, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "retro")
    return repo, sha


COMMIT_RE = re.compile(r"\*\*Commit:\*\*\s*`([0-9a-f]{7,40})`")


def anchor():
    return "2026-10-0{n}-{topic}-gate-6-reopened-twice"


def conservative_rebuild_controls():
    repo, _ = project("rebuild-preservation", 1)
    retro = repo / "docs/evidence/retro.md"
    work = tree("tp-lessons-preservation-")
    idx = work / "index.jsonl"
    rc, _, _ = run("add", "--retro", str(retro), "--all", cwd=repo, index=idx)
    ok(rc == 0, "preservation fixture seeds a real lesson")
    before = idx.read_bytes()
    for root in (repo / "missing-root", retro):
        rc, out, err = run("rebuild", "--roots", str(root), index=idx)
        ok(rc != 0 and idx.read_bytes() == before and "not read" in out + err,
           f"missing/non-directory root refuses without replacing the index ({rc} {out} {err})")
    retro.chmod(0)
    try:
        rc, out, err = run("rebuild", "--roots", str(repo), index=idx)
        ok(rc != 0 and idx.read_bytes() == before and "not read" in out + err,
           "unreadable retro retains every old lesson")
    finally:
        retro.chmod(0o644)
    blocked = repo / "unreadable-child"
    blocked.mkdir()
    blocked.chmod(0)
    try:
        rc, out, err = run("rebuild", "--roots", str(repo), index=idx)
        # Round 6: the readable rest is rebuilt; the lesson it holds is the one the index held,
        # so nothing is dropped and the projection is byte-identical.
        ok(rc == 0 and idx.read_bytes() == before and "not read" in out and str(blocked) in out,
           f"unreadable discovery subtree is named and drops no lesson ({rc} {out!r} {err!r})")
    finally:
        blocked.chmod(0o755)
    conf = repo / "pipeline.json"
    conf.write_text('{"paths":')
    rc, out, err = run("rebuild", "--roots", str(repo), index=idx)
    ok(rc != 0 and idx.read_bytes() == before, "malformed artifact-root configuration refuses rebuild")
    conf.unlink()
    absent = work / "fresh" / "index.jsonl"
    rc, _, _ = run("rebuild", "--roots", str(repo / "missing-root"), index=absent)
    ok(rc != 0 and not absent.parent.exists(), "incomplete first rebuild creates no index or lock directory")
    empty = work / "empty"
    empty.mkdir()
    rc, out, _ = run("rebuild", "--roots", str(empty), index=idx)
    # Round 7: a readable empty scope re-derives nothing and loses nothing — the held lesson is
    # carried; --prune-carried is how it is emptied on purpose.
    ok(rc == 0 and [o.get("carried") for o in lesson_of(idx)["origins"]] == ["checkout not read"],
       f"a readable empty scope carries the held lesson ({rc} {out!r})")
    rc, _, _ = run("rebuild", "--roots", str(empty), "--prune-carried", index=idx)
    ok(rc == 0 and idx.read_bytes() == b"", "--prune-carried over a readable empty scope rebuilds to zero")


def partial_rebuild_controls():
    """Round 6: one bad source never costs the whole rebuild. Squash merges plus branch deletion
    leave dangling evidence commits routinely, and a corrupt index has already been set aside
    when `rebuild --roots` is asked to re-derive it, so an all-or-nothing rebuild left it empty."""
    work = tree("tp-lessons-partial-")
    good, _ = project("partial-good", 1)
    dangling, _ = project("partial-dangling", 2)
    retro = dangling / "docs/evidence/retro.md"
    text = retro.read_text(encoding="utf-8")
    sha = COMMIT_RE.search(text).group(1)
    retro.write_text(text.replace(sha, "deadbeefcafe"), encoding="utf-8")
    roots = tree("tp-lessons-partial-roots-")
    os.symlink(good, roots / "good")
    os.symlink(dangling, roots / "dangling")
    idx = work / "dangling" / "index.jsonl"
    rc, out, err = run("rebuild", "--roots", str(roots), index=idx)
    ok(rc == 0 and "· 1 lesson ·" in out and "1 with a commit that does not resolve" in out
       and "absence-needs-its-own-check" in out and "incomplete rebuild refused" not in err
       and len(idx.read_text(encoding="utf-8").splitlines()) == 1,
       f"rebuild: a dangling evidence commit is counted and named, the rest rebuilt, exit 0 ({rc} {out!r} {err!r})")
    ok("2 retro files in 2 repositories" in out,
       f"rebuild: the retro whose commit dangles was still read ({out!r})")

    blocked = work / "unreadable-root"
    blocked.mkdir()
    (blocked / "inside").mkdir()
    blocked.chmod(0)
    unread_idx = work / "unreadable" / "index.jsonl"
    try:
        rc, out, err = run("rebuild", "--roots", str(roots), str(blocked), index=unread_idx)
    finally:
        blocked.chmod(0o755)
    ok(rc == 0 and "not read" in out and str(blocked) in out and unread_idx.is_file()
       and "absence-needs-its-own-check" in unread_idx.read_text(encoding="utf-8"),
       f"rebuild: an unreadable directory among the roots is named, the other roots still rebuilt ({rc} {out!r} {err!r})")

    # #116's conservation case, under the round-7 design: a lesson the scan does not reach is
    # carried forward, never dropped, and the run still exits 0.
    held = work / "held" / "index.jsonl"
    ok(run("add", "--retro", str(good / "docs/evidence/retro.md"), "--all", cwd=good, index=held)[0] == 0,
       "partial-rebuild fixture seeds a lesson the scan will not reach")
    rc, out, err = run("rebuild", "--roots", str(dangling), index=held)
    kept = entries_of(held).get(KEY)
    ok(rc == 0 and kept is not None and [o.get("carried") for o in kept["origins"]] == ["checkout not read"]
       and "carried" in out,
       f"rebuild: a held lesson outside the readable scan is carried, named, exit 0 ({rc} {out!r} {err!r})")


KEY = "absence-needs-its-own-check"


def entries_of(path):
    return {e["classKey"]: e for e in
            (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())}


def lesson_of(path, class_key=KEY):
    """The entry, or an empty stand-in so a dropped lesson fails its `ok` by name, not by KeyError."""
    return entries_of(path).get(class_key) or {"id": None, "origins": [], "projects": 0, "seen": 0,
                                                 "status": "absent"}


def carry_forward_controls():
    """Round 7 (loop guard): rebuild never loses what it cannot re-derive. An origin whose source
    could not be read, or whose commit no longer resolves, is CARRIED with everything recorded on
    it; status counts it; it is re-derived and un-marked when its source reads again; only
    `--prune-carried` removes it on purpose."""
    work = tree("tp-lessons-carry-")
    f1, _ = project("carry-f1", 1)
    f2, _ = project("carry-f2", 2)
    idx = work / "index.jsonl"
    for repo in (f1, f2):
        ok(run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=repo, index=idx)[0] == 0,
           "carry fixture: both projects add the lesson")
    lid = lesson_of(idx)["id"]
    rc, _, err = run("record", lid, "--answer", "-", cwd=f2, index=idx,
                     stdin=json.dumps({"memoryId": "mem:probe-f2", "revision": 1}))
    ok(rc == 0, f"carry fixture: the store's answer is recorded on f2's origin ({rc} {err!r})")
    f2_key = next(o["project"] for o in lesson_of(idx)["origins"] if o.get("memory"))

    def f2_origin():
        return next((o for o in lesson_of(idx)["origins"] if o["project"] == f2_key), None)

    # N1: f2's root unreadable. Its origin and memory id are carried, the lesson stays a
    # candidate held by two projects, exit 0.
    f2.chmod(0)
    try:
        rc, out, err = run("rebuild", "--roots", str(f1), str(f2), index=idx)
    finally:
        f2.chmod(0o755)
    e, o = lesson_of(idx), f2_origin()
    ok(rc == 0 and o is not None and o.get("memory") == "mem:probe-f2@1"
       and o.get("carried") == "checkout not read",
       f"N1: an unreadable root's origin is carried with its memory id, exit 0 ({rc} {out!r} {err!r} {e})")
    ok(e["projects"] == 2 and e["status"] == "candidate" and e["seen"] == 2,
       f"N1: status, projects and seen count the carried origin ({e['status']} {e['projects']} {e['seen']})")
    ok("carried" in out and f2_key in out, f"N1: the summary names the carried origin ({out!r})")

    # Restored: re-derived from the retro, un-marked, memory id still there.
    rc, out, err = run("rebuild", "--roots", str(f1), str(f2), index=idx)
    o = f2_origin()
    ok(rc == 0 and o is not None and "carried" not in o and o.get("memory") == "mem:probe-f2@1",
       f"a carried origin is re-derived and un-marked once its root reads again ({rc} {o})")

    # Origin granularity: f1 deletes the entry on a READABLE root while f2 is unreadable. f1's
    # origin leaves (its source no longer holds it); f2's is carried. A class-key carry would
    # keep f1's too.
    retro1 = f1 / "docs/evidence/retro.md"
    original1 = retro1.read_text(encoding="utf-8")
    retro1.write_text("\n".join(ln for ln in original1.splitlines() if "**Lesson:**" not in ln) + "\n",
                      encoding="utf-8")
    f2.chmod(0)
    try:
        rc, out, err = run("rebuild", "--roots", str(f1), str(f2), index=idx)
    finally:
        f2.chmod(0o755)
    e = lesson_of(idx)
    ok(rc == 0 and [x["project"] for x in e["origins"]] == [f2_key]
       and e["origins"][0].get("carried") == "checkout not read" and e["projects"] == 1
       and e["status"] == "local" and "removed" in out,
       f"carry is per origin: a readable root's deleted entry leaves, the unreadable one stays ({rc} {out!r} {e})")

    # Identity is (project, retro) under the class key, never the title: f1 retitles the lesson
    # while f2 is carried; one entry, two projects.
    retro1.write_text(original1.replace("a check that reads a success line passes",
                                        "a gate that reads a success line passes"), encoding="utf-8")
    f2.chmod(0)
    try:
        rc, out, err = run("rebuild", "--roots", str(f1), str(f2), index=idx)
    finally:
        f2.chmod(0o755)
    all_entries = entries_of(idx)
    e = all_entries.get(KEY)
    ok(rc == 0 and len(all_entries) == 1 and e is not None and e["projects"] == 2
       and sorted(bool(x.get("carried")) for x in e["origins"]) == [False, True],
       f"a retitled lesson keeps its carried origin under the same class key ({rc} {all_entries})")

    # --prune-carried removes exactly the carried origins, on purpose.
    f2.chmod(0)
    try:
        rc, out, err = run("rebuild", "--roots", str(f1), str(f2), "--prune-carried", index=idx)
    finally:
        f2.chmod(0o755)
    e = lesson_of(idx)
    ok(rc == 0 and [x["project"] for x in e["origins"]] != [] and f2_origin() is None
       and all("carried" not in x for x in e["origins"]) and e["projects"] == 1 and "pruned" in out,
       f"--prune-carried drops exactly the carried origins ({rc} {out!r} {e})")
    retro1.write_text(original1, encoding="utf-8")

    # N2, the routine case: a lesson already indexed, then its commit orphaned and pruned after a
    # squash merge and branch deletion. It is carried (exit 0); another project's new lesson is
    # added in the same run.
    g = tree("tp-lessons-carry-g-")
    git(g, "init", "-q")
    (g / "README.md").write_text("# g\n", encoding="utf-8")
    git(g, "add", "-A")
    git(g, "commit", "-q", "-m", "root")
    main_branch = git(g, "rev-parse", "--abbrev-ref", "HEAD")
    git(g, "checkout", "-q", "-b", "side")
    (g / "fix.txt").write_text("fixed\n", encoding="utf-8")
    git(g, "add", "-A")
    git(g, "commit", "-q", "-m", "the fix")
    orphan = git(g, "rev-parse", "HEAD")
    git(g, "checkout", "-q", main_branch)
    (g / "docs" / "evidence").mkdir(parents=True)
    (g / "docs/evidence/retro.md").write_text(
        "# Pipeline retrospective\n\n## Recent log\n\n"
        + ENTRY.format(n=3, topic="g-export", sha=orphan), encoding="utf-8")
    git(g, "add", "-A")
    git(g, "commit", "-q", "-m", "retro")
    gidx = work / "g" / "index.jsonl"
    ok(run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=g, index=gidx)[0] == 0,
       "N2 fixture: the lesson is indexed while its commit resolves")
    git(g, "branch", "-q", "-D", "side")
    git(g, "reflog", "expire", "--expire=now", "--all")
    git(g, "gc", "-q", "--prune=now")
    gone = subprocess.run(["git", "cat-file", "-e", f"{orphan}^{{commit}}"], cwd=g,
                          capture_output=True).returncode != 0
    ok(gone, "N2 fixture: the squashed branch's commit no longer resolves")
    h, _ = project("carry-h", 4)
    hr = h / "docs/evidence/retro.md"
    hr.write_text(hr.read_text(encoding="utf-8").replace(KEY, "a-new-class-elsewhere"), encoding="utf-8")
    rc, out, err = run("rebuild", "--roots", str(g), str(h), index=gidx)
    es = entries_of(gidx)
    ok(rc == 0 and KEY in es and [x.get("carried") for x in es[KEY]["origins"]] == ["commit does not resolve"]
       and es[KEY]["origins"][0]["commit"] == orphan and "a-new-class-elsewhere" in es,
       f"N2: an indexed lesson whose commit was pruned is carried, exit 0, new lessons added ({rc} {out!r} {err!r})")
    rc, out, err = run("rebuild", "--roots", str(g), str(h), "--prune-carried", index=gidx)
    es = entries_of(gidx)
    ok(rc == 0 and KEY not in es and "a-new-class-elsewhere" in es,
       f"N2: --prune-carried removes the carried lesson and keeps the rest ({rc} {sorted(es)})")

    # Nothing read: exit 1, the index byte-identical.
    before = idx.read_bytes()
    f2.chmod(0)
    try:
        rc, out, err = run("rebuild", "--roots", str(f2), str(work / "absent"), index=idx)
    finally:
        f2.chmod(0o755)
    ok(rc == 1 and idx.read_bytes() == before, f"nothing read: exit 1, index untouched ({rc} {err!r})")


HEADED = """### {head}

- **Symptom:** the export passed its gate with no file written
- **Surfaced at:** stage 6 · **Owned by:** stage 4
- **Fix:** grade 1 (mechanical) — the check reads the artefact
- **The check:** `test/export_test.py` asserts the file exists
- **Lesson:** `{key}` — a check that reads a success line passes when the artefact is absent · **When:** a gate verifies an output by its log line · **Nouns:** gate, artefact, absence
- **Commit:** `{sha}`
"""
K2 = "absence-renamed-class"


def write_retros(repo, entries, sha, keep=False):
    """entries: (file under docs/evidence, heading, class key). Replaces every retro file,
    unless keep: then only the files named are rewritten."""
    art = repo / "docs" / "evidence"
    for f in ([] if keep else list(art.rglob("*.md")) if art.exists() else []):
        f.unlink()
    files = {}
    for f, head, key in entries:
        files.setdefault(f, []).append(HEADED.format(head=head, key=key, sha=sha))
    if not (keep and (art / "retro.md").exists()):
        files.setdefault("retro.md", [])
    for f, bodies in files.items():
        p = art / f
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# Retro\n\n## Log\n\n" + "\n".join(bodies), encoding="utf-8")


def headed_repo(name, entries, parent=None):
    if parent is None:
        repo = tree(f"tp-lessons-{name}-")
    else:
        repo = parent / name
        repo.mkdir(parents=True)
    git(repo, "init", "-q")
    (repo / "README.md").write_text(name, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "root")
    (repo / "fix.txt").write_text("x", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fix")
    sha = git(repo, "rev-parse", "HEAD")
    write_retros(repo, entries, sha)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "retro")
    return repo, sha


def record_mem(idx, cwd, class_key, mem):
    lid = entries_of(idx)[class_key]["id"]
    return run("record", lid, "--answer", "-", cwd=cwd, index=idx,
               stdin=json.dumps({"memoryId": mem, "revision": 1}))[0]


def mems(idx):
    """{memory id: sorted class keys holding it} — one id on two keys is the M1 defect."""
    out = {}
    for ck, e in entries_of(idx).items():
        for o in e["origins"]:
            if o.get("memory"):
                out.setdefault(o["memory"], set()).add(ck)
    return {m: sorted(v) for m, v in out.items()}


def identity_controls():
    """Round 8 (adversarial): identity. A project key names every checkout of a project, so one
    checkout read never decides for another; a memory id belongs to (project, classKey), the
    store's own identity, never to a retro anchor."""
    work = tree("tp-lessons-identity-")

    # Q1 — the routine branch flow, with the worktree under a dot-directory the walk skips:
    # the lesson is added and recorded in the worktree, then a rebuild runs over main only.
    main_repo, sha = headed_repo("q1", [("retro.md", "old entry", "an-older-class")])
    wt = main_repo / ".claude" / "worktrees" / "feature"
    git(main_repo, "worktree", "add", "-q", "-b", "feature", str(wt))
    write_retros(wt, [("retro.md", "old entry", "an-older-class"), ("retro.md", "new entry", KEY)], sha)
    git(wt, "add", "-A")
    git(wt, "commit", "-q", "-m", "retro on branch")
    idx = work / "q1.jsonl"
    ok(run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=wt, index=idx)[0] == 0
       and record_mem(idx, wt, KEY, "mem:q1-branch") == 0, "Q1 fixture: added and recorded in the worktree")
    rc, out, err = run("rebuild", "--roots", str(main_repo), index=idx)
    o = lesson_of(idx)["origins"]
    ok(rc == 0 and len(o) == 1 and o[0].get("memory") == "mem:q1-branch@1" and "carried" not in o[0],
       f"Q1: a worktree under .claude/worktrees is discovered; its lesson keeps its memory id ({rc} {out!r} {o})")
    git(main_repo, "merge", "-q", "feature")
    git(main_repo, "worktree", "remove", "--force", str(wt))
    rc, out, err = run("rebuild", "--roots", str(main_repo), index=idx)
    ok(rc == 0 and mems(idx) == {"mem:q1-branch@1": [KEY]},
       f"Q1: after the merge the lesson keeps its one memory id ({rc} {mems(idx)})")

    # P5 — two clones of one project; only clone A holds an archived, recorded entry. A rebuild
    # over clone B alone does not remove A's origin: it carries it with its memory id.
    a, sha = headed_repo("p5a", [("retro.md", "main entry", KEY)])
    b = work / "p5b"
    git(work, "clone", "-q", str(a), str(b))
    arch = a / "docs/evidence/retro/2026-Q3.md"
    arch.parent.mkdir(parents=True)
    arch.write_text("# Retro\n\n## Log\n\n" + HEADED.format(head="archived entry", key=K2, sha=sha),
                    encoding="utf-8")
    idx = work / "p5.jsonl"
    ok(run("rebuild", "--roots", str(a), str(b), index=idx)[0] == 0
       and record_mem(idx, a, K2, "mem:p5-archive") == 0, "P5 fixture: both clones read, the archive recorded")
    rc, out, err = run("rebuild", "--roots", str(b), index=idx)
    e = entries_of(idx).get(K2)
    ok(rc == 0 and e is not None and e["origins"][0].get("memory") == "mem:p5-archive@1"
       and e["origins"][0].get("carried"),
       f"P5: another clone's recorded origin is carried, never removed, by a narrower rebuild ({rc} {out!r})")

    # P5b — clone A scanned with its archive unreadable, clone B complete: A failed, so the
    # project is not complete and A's files decide nothing.
    idx = work / "p5b.jsonl"
    run("rebuild", "--roots", str(a), str(b), index=idx)
    record_mem(idx, a, K2, "mem:p5b-archive")
    arch.chmod(0)
    try:
        rc, out, err = run("rebuild", "--roots", str(a), str(b), index=idx)
    finally:
        arch.chmod(0o644)
    e = entries_of(idx).get(K2)
    ok(rc == 0 and e is not None and e["origins"][0].get("carried") == "checkout not read"
       and e["origins"][0].get("memory") == "mem:p5b-archive@1" and "2026-Q3.md" in out
       and "removed" not in out,
       f"P5b: an unreadable archive is not read, so its origin is carried, not removed ({rc} {out!r})")

    # P1 — rotation: the entry moves from retro.md into the archive. The id follows the class.
    d, sha = headed_repo("p1", [("retro.md", "2026-10-01 export gate", KEY)])
    idx = work / "p1.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=d, index=idx)
    record_mem(idx, d, KEY, "mem:p1")
    write_retros(d, [("retro/2026-Q4.md", "2026-10-01 export gate", KEY)], sha)
    rc, out, err = run("rebuild", "--roots", str(d), index=idx)
    o = lesson_of(idx)["origins"]
    ok(rc == 0 and len(o) == 1 and o[0]["retro"].startswith("docs/evidence/retro/2026-Q4.md#")
       and o[0].get("memory") == "mem:p1@1" and "carried" not in o[0],
       f"P1: a rotated entry keeps its memory id ({rc} {o})")

    # P2 — the heading is reworded (the anchor changes); the id stays with the class.
    d, sha = headed_repo("p2", [("retro.md", "2026-10-01 export gate", KEY)])
    idx = work / "p2.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=d, index=idx)
    record_mem(idx, d, KEY, "mem:p2")
    write_retros(d, [("retro.md", "2026-10-01 export gate reopened", KEY)], sha)
    rc, out, err = run("rebuild", "--roots", str(d), index=idx)
    o = lesson_of(idx)["origins"]
    ok(rc == 0 and len(o) == 1 and o[0].get("memory") == "mem:p2@1" and "reopened" in o[0]["retro"],
       f"P2: a reworded heading keeps the memory id ({rc} {o})")

    # P3 — the class key changes inside the same entry. k1's id never moves to k2: k2 starts
    # with no id, and k1's recorded origin is carried with its own.
    d, sha = headed_repo("p3", [("retro.md", "2026-10-01 export gate", KEY)])
    idx = work / "p3.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=d, index=idx)
    record_mem(idx, d, KEY, "mem:p3-k1")
    write_retros(d, [("retro.md", "2026-10-01 export gate", K2)], sha)
    rc, out, err = run("rebuild", "--roots", str(d), index=idx)
    es = entries_of(idx)
    ok(rc == 0 and mems(idx) == {"mem:p3-k1@1": [KEY]} and K2 in es
       and not any(x.get("memory") for x in es[K2]["origins"])
       and es[KEY]["origins"][0].get("carried"),
       f"P3: a changed class key does not inherit the old key's memory id ({rc} {mems(idx)})")
    rc, out, _ = run("emit-observatory", es[K2]["id"], cwd=d, index=idx)
    ok(rc == 0 and "memoryId" not in out, f"P3: emit for the new class creates, never revises k1's record ({out!r})")

    # P4 — two entries share one heading (one anchor) with different class keys; one id each.
    d, sha = headed_repo("p4", [("retro.md", "same heading", KEY), ("retro.md", "same heading", K2)])
    idx = work / "p4.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=d, index=idx)
    record_mem(idx, d, KEY, "mem:p4-k1-only")
    rc, out, err = run("rebuild", "--roots", str(d), index=idx)
    ok(rc == 0 and mems(idx) == {"mem:p4-k1-only@1": [KEY]},
       f"P4: one heading, two classes — the id stays on its own class ({rc} {mems(idx)})")
    # An index already carrying one id on two classes (the round-7 defect) is repaired, said aloud.
    lines = [json.loads(x) for x in idx.read_text(encoding="utf-8").splitlines()]
    for line in lines:
        if line["classKey"] == K2:
            line["origins"][0]["memory"] = "mem:p4-k1-only@1"
    idx.write_text("".join(json.dumps(x) + "\n" for x in lines), encoding="utf-8")
    rc, out, err = run("rebuild", "--roots", str(d), index=idx)
    ok(rc == 0 and len(mems(idx)["mem:p4-k1-only@1"]) == 1 and "memory id" in out + err,
       f"one memory id is never attached to two class keys ({rc} {mems(idx)} {out!r} {err!r})")


def low_controls():
    """Round 8 LOW findings: L1 a line without origins, L2 a corrupt line among good ones,
    L4 something read is never 'nothing read', L5 the unresolved label names whose commit."""
    work = tree("tp-lessons-low-")
    d, sha = headed_repo("low", [("retro.md", "x entry", KEY)])
    other, _ = headed_repo("low-other", [("retro.md", "y entry", K2)])

    # L1 — a previous-index line without origins is a corrupt index, never a traceback.
    idx = work / "l1.jsonl"
    idx.write_text(json.dumps({"classKey": "old-shape", "title": "t"}) + "\n", encoding="utf-8")
    rc, out, err = run("rebuild", "--roots", str(d), index=idx)
    ok(rc == 0 and "Traceback" not in err and list(work.glob("l1.jsonl.corrupt-*")) and KEY in entries_of(idx),
       f"L1: a line without origins is set aside as corrupt, the rebuild goes on ({rc} {err[-300:]!r})")

    # L2 — a corrupt line among good ones: the good lines are salvaged (memory ids and carried
    # origins kept), the file is kept whole as .corrupt-<date>, and the notice says so.
    idx = work / "l2.jsonl"
    run("rebuild", "--roots", str(d), str(other), index=idx)
    record_mem(idx, d, KEY, "mem:l2")
    idx.write_text(idx.read_text(encoding="utf-8") + "{not json\n", encoding="utf-8")
    d.chmod(0)
    try:
        rc, out, err = run("rebuild", "--roots", str(d), str(other), index=idx)
    finally:
        d.chmod(0o755)
    o = lesson_of(idx)["origins"]
    ok(rc == 0 and o and o[0].get("memory") == "mem:l2@1" and o[0].get("carried") == "checkout not read"
       and list(work.glob("l2.jsonl.corrupt-*")) and "salvaged" in err,
       f"L2: good lines of a corrupt index are salvaged with their memory ids ({rc} {err!r} {o})")

    # L4 — one repository read in full (no retro) and another's retro unreadable: something was
    # read, so exit 0, the unreadable retro named, its origin carried.
    emp = tree("tp-lessons-low-empty-")
    git(emp, "init", "-q")
    (emp / "a").write_text("a", encoding="utf-8")
    git(emp, "add", "-A")
    git(emp, "commit", "-q", "-m", "r")
    idx = work / "l4.jsonl"
    run("rebuild", "--roots", str(d), index=idx)
    retro = d / "docs/evidence/retro.md"
    retro.chmod(0)
    try:
        rc, out, err = run("rebuild", "--roots", str(emp), str(d), index=idx)
    finally:
        retro.chmod(0o644)
    ok(rc == 0 and "retro.md" in out and lesson_of(idx)["origins"][0].get("carried") == "checkout not read",
       f"L4: a fully read repository counts as read — exit 0, the unreadable retro named ({rc} {out!r} {err!r})")

    # L5 — the retro now cites a commit that does not resolve, while the indexed origin's own
    # commit still does: the label says which side failed, and the origin keeps its commit.
    idx = work / "l5.jsonl"
    run("rebuild", "--roots", str(d), index=idx)
    write_retros(d, [("retro.md", "x entry", KEY)], "deadbeefcafe")
    rc, out, err = run("rebuild", "--roots", str(d), index=idx)
    o = lesson_of(idx)["origins"][0]
    ok(rc == 0 and o.get("carried") == "retro cites a commit that does not resolve" and o["commit"] == sha
       and "deadbeefcafe" in out,
       f"L5: the carried label names the retro's unresolvable commit, the origin keeps its own ({rc} {o} {out!r})")
    write_retros(d, [("retro.md", "x entry", KEY)], sha)


def emit_mem(idx, cwd, class_key):
    """emit-observatory's (memoryId, expectedRevision) for this checkout's origin."""
    rc, out, err = run("emit-observatory", entries_of(idx)[class_key]["id"], cwd=cwd, index=idx)
    if rc:
        return ("refused", err.strip()[-120:])
    args = json.loads(out)["arguments"]
    return (args.get("memoryId"), args.get("expectedRevision"))


def provenance_controls():
    """Round 9 (loop guard, rule simplified): implicit removal needs positive evidence from the
    SAME checkout. An origin records the checkouts it was derived from; a rebuild removes it
    without --prune-carried only when each of them was discovered and read completely, its retro
    file at that path was read, and the file no longer holds the entry. Everything else carries."""
    work = tree("tp-lessons-prov-")
    K_ = KEY

    def kept(idx, what):
        e = entries_of(idx).get(K_)
        ok(e is not None and all(o.get("carried") for o in e["origins"]),
           f"{what}: the lesson is carried, never lost ({e and [o.get('carried') for o in e['origins']]})")

    # A1 — two clones; the lesson only in clone Y's archive. Y outside the roots: carried.
    r1, r2 = work / "a1" / "root1", work / "a1" / "root2"
    r1.mkdir(parents=True)
    r2.mkdir(parents=True)
    x, sha = headed_repo("x", [("retro.md", "old entry", "an-older-class")], parent=r1)
    y = r2 / "y"
    git(work, "clone", "-q", str(x), str(y))
    write_retros(y, [("retro/2026-Q4.md", "export gate", K_)], sha, keep=True)
    idx = work / "a1.jsonl"
    ok(run("rebuild", "--roots", str(r1), str(r2), index=idx)[0] == 0 and K_ in entries_of(idx), "A1 fixture")
    rc, out, _ = run("rebuild", "--roots", str(r1), index=idx)
    ok(rc == 0, f"A1 exit ({rc})")
    kept(idx, "A1 another clone's archive, that clone outside the roots")

    # A2 — the lesson in Y's retro.md; X's retro.md lacks it. X never held it: X decides nothing.
    r1, r2 = work / "a2" / "root1", work / "a2" / "root2"
    r1.mkdir(parents=True)
    r2.mkdir(parents=True)
    x, sha = headed_repo("x", [("retro.md", "old entry", "an-older-class")], parent=r1)
    y = r2 / "y"
    git(work, "clone", "-q", str(x), str(y))
    write_retros(y, [("retro.md", "old entry", "an-older-class"), ("retro.md", "export gate", K_)], sha)
    idx = work / "a2.jsonl"
    run("rebuild", "--roots", str(r1), str(r2), index=idx)
    run("rebuild", "--roots", str(r1), index=idx)
    kept(idx, "A2 the same retro path read in another checkout")

    # A3 — both clones under one root; Y's retro.md unreadable (Y failed), X complete.
    root = work / "a3"
    root.mkdir()
    x, sha = headed_repo("x", [("retro.md", "old entry", "an-older-class")], parent=root)
    y = root / "y"
    git(work, "clone", "-q", str(x), str(y))
    write_retros(y, [("retro.md", "old entry", "an-older-class"), ("retro.md", "export gate", K_)], sha)
    idx = work / "a3.jsonl"
    run("rebuild", "--roots", str(root), index=idx)
    (y / "docs/evidence/retro.md").chmod(0)
    try:
        rc, out, _ = run("rebuild", "--roots", str(root), index=idx)
    finally:
        (y / "docs/evidence/retro.md").chmod(0o644)
    kept(idx, "A3 its own checkout failed")

    # A4 — add --json with a retro outside the artifact root, then rebuild: never read, carried.
    root = work / "a4"
    root.mkdir()
    x, sha = headed_repo("x", [("retro.md", "old entry", "an-older-class")], parent=root)
    lesson = {"classKey": K_, "title": "a check that reads a success line passes",
              "trigger": "a gate verifies an output", "check": "the test reads the file",
              "grade": 1, "stages": {"owned": 4, "surfaced": 6}, "nouns": ["gate", "artefact", "absence"],
              "origin": {"commit": sha, "retro": "notes/retro.md#export-gate"}}
    idx = work / "a4.jsonl"
    ok(run("add", "--json", "-", cwd=x, index=idx, stdin=json.dumps(lesson))[0] == 0, "A4 fixture")
    rc, out, _ = run("rebuild", "--roots", str(root), index=idx)
    kept(idx, "A4 a retro outside the artifact root")
    ok(lesson_of(idx)["origins"][0].get("carried") == "retro file not read",
       f"A4: the reason is accurate ({lesson_of(idx)['origins'][0].get('carried')})")

    # A5 — the artifact root moves; the old retro is no longer read: carried.
    root = work / "a5"
    root.mkdir()
    x, sha = headed_repo("x", [("retro.md", "export gate", K_)], parent=root)
    idx = work / "a5.jsonl"
    run("rebuild", "--roots", str(root), index=idx)
    (x / "docs/new").mkdir(parents=True)
    (x / "docs/new/retro.md").write_text("# Retro\n\n## Log\n\n", encoding="utf-8")
    (x / "pipeline.json").write_text(json.dumps({"paths": {"artifacts": "docs/new"}}), encoding="utf-8")
    run("rebuild", "--roots", str(root), index=idx)
    kept(idx, "A5 the artifact root moved")

    # g1/g2 — an unreadable sibling directory hides a clone that holds the lesson. Its name
    # shares the checkout's prefix in g2 (".../x-old" starts with ".../x"); attribution is by
    # owner, never by prefix. And x itself still decides for its own origins: an entry x deleted
    # leaves even while the sibling is unreadable.
    for tag, other in (("g1", "zz-other"), ("g2", "x-old")):
        root = work / tag
        root.mkdir()
        x, sha = headed_repo("x", [("retro.md", "old entry", "an-older-class")], parent=root)
        hidden = root / other
        hidden.mkdir()
        yy = hidden / "clone"
        git(work, "clone", "-q", str(x), str(yy))
        write_retros(yy, [("retro/2026-Q4.md", "export gate", K_)], sha, keep=True)
        write_retros(x, [("retro.md", "old entry", "an-older-class"), ("retro.md", "x own entry", K2)], sha)
        idx = work / f"{tag}.jsonl"
        run("rebuild", "--roots", str(root), index=idx)
        ok(K_ in entries_of(idx) and K2 in entries_of(idx), f"{tag} fixture")
        write_retros(x, [("retro.md", "old entry", "an-older-class")], sha)
        hidden.chmod(0)
        try:
            rc, out, _ = run("rebuild", "--roots", str(root), index=idx)
        finally:
            hidden.chmod(0o755)
        kept(idx, f"{tag} a clone hidden by an unreadable sibling directory")
        ok(K2 not in entries_of(idx) and "removed" in out,
           f"{tag}: x's own deleted entry leaves — its checkout read completely ({out!r})")

    # C2 — `git worktree list` exits non-zero: a problem owned by that checkout; the hidden
    # worktree's origin is carried.
    root = work / "c2"
    root.mkdir()
    x, sha = headed_repo("x", [("retro.md", "old entry", "an-older-class")], parent=root)
    wt = x / ".worktrees" / "feat"
    git(x, "worktree", "add", "-q", "--detach", str(wt))
    write_retros(wt, [("retro.md", "old entry", "an-older-class"), ("retro.md", "export gate", K_)], sha)
    idx = work / "c2.jsonl"
    run("rebuild", "--roots", str(root), index=idx)
    ok(K_ in entries_of(idx), "C2 fixture: the worktree's lesson is indexed")
    fake = work / "fakebin"
    fake.mkdir()
    real_git = shutil.which("git")
    (fake / "git").write_text(
        "#!/bin/sh\nfor a in \"$@\"; do if [ \"$a\" = worktree ]; then echo 'fatal: simulated' >&2; "
        f"exit 128; fi; done\nexec {real_git} \"$@\"\n", encoding="utf-8")
    (fake / "git").chmod(0o755)
    rc, out, err = run("rebuild", "--roots", str(root), index=idx,
                       env_extra={"PATH": f"{fake}:{os.environ['PATH']}"})
    ok(rc == 0 and "worktrees cannot be listed" in out, f"C2: the failed listing is named ({rc} {out!r})")
    kept(idx, "C2 a worktree git could not list")

    # B4 — a memory id recorded on the archive origin; a retro.md entry of the same class added
    # later sorts first. emit and record keep using the origin that holds the id.
    root = work / "b4"
    root.mkdir()
    x, sha = headed_repo("x", [("retro/2026-Q3.md", "older gate", K_)], parent=root)
    idx = work / "b4.jsonl"
    run("add", "--retro", "docs/evidence/retro/2026-Q3.md", "--all", cwd=x, index=idx)
    record_mem(idx, x, K_, "mem:b4")
    write_retros(x, [("retro.md", "newer gate", K_)], sha, keep=True)
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=x, index=idx)
    ok(emit_mem(idx, x, K_) == ("mem:b4", 1), f"B4: emit after add revises mem:b4 ({emit_mem(idx, x, K_)})")
    run("rebuild", "--roots", str(root), index=idx)
    ok(emit_mem(idx, x, K_) == ("mem:b4", 1), f"B4: emit after rebuild revises mem:b4 ({emit_mem(idx, x, K_)})")

    # B5 — as B4, with retro.md unreadable at the rebuild: the carried memory-less origin sorts
    # first; emit still revises the recorded id.
    root = work / "b5"
    root.mkdir()
    x, sha = headed_repo("x", [("retro/2026-Q3.md", "older gate", K_)], parent=root)
    idx = work / "b5.jsonl"
    run("add", "--retro", "docs/evidence/retro/2026-Q3.md", "--all", cwd=x, index=idx)
    record_mem(idx, x, K_, "mem:b5")
    write_retros(x, [("retro.md", "newer gate", K_)], sha, keep=True)
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=x, index=idx)
    (x / "docs/evidence/retro.md").chmod(0)
    try:
        run("rebuild", "--roots", str(root), index=idx)
    finally:
        (x / "docs/evidence/retro.md").chmod(0o644)
    ok(emit_mem(idx, x, K_) == ("mem:b5", 1), f"B5: emit picks the origin holding the id ({emit_mem(idx, x, K_)})")

    # B6 — one id on a carried and a derived origin; a revision recorded on one. Ids compare on
    # the part before `@`, and the highest revision wins everywhere.
    root = work / "b6"
    root.mkdir()
    x, sha = headed_repo("x", [("retro.md", "export gate", K_)], parent=root)
    idx = work / "b6.jsonl"
    run("rebuild", "--roots", str(root), index=idx)
    record_mem(idx, x, K_, "mem:b6")
    write_retros(x, [("retro/2026-Q4.md", "export gate", K_)], sha)
    (x / "docs/evidence/retro.md").chmod(0)
    try:
        run("rebuild", "--roots", str(root), index=idx)
    finally:
        (x / "docs/evidence/retro.md").chmod(0o644)
    lid = lesson_of(idx)["id"]
    ok(run("record", lid, "--answer", "-", cwd=x, index=idx,
           stdin=json.dumps({"memoryId": "mem:b6", "revision": 2}))[0] == 0, "B6 fixture: revision 2 recorded")
    for _ in range(2):
        rc, out, err = run("rebuild", "--roots", str(root), index=idx)
    ids = {o.get("memory") for o in lesson_of(idx)["origins"] if o.get("memory")}
    ok(rc == 0 and ids == {"mem:b6@2"} and emit_mem(idx, x, K_) == ("mem:b6", 2),
       f"B6: one id, its highest revision, everywhere ({rc} {ids} {emit_mem(idx, x, K_)} {err!r})")


def index_shape_controls():
    """Round 9 LOW: D1 an origin whose lesson is {} is a corrupt line, no traceback; D2 a memory
    id held only by a corrupt line is named in the run; D3 two lines for one class key merge."""
    work = tree("tp-lessons-shape-")
    root = work / "d"
    root.mkdir()
    x, sha = headed_repo("x", [("retro.md", "export gate", KEY)], parent=root)

    idx = work / "d1.jsonl"
    idx.write_text(json.dumps({"schema": "lesson-index/1", "classKey": "ghost-class", "id": "L-000000000000",
                               "origins": [{"project": "p-aaaaaaaaaaaa", "retro": "docs/evidence/retro.md#x",
                                            "commit": "abcdef1", "lesson": {}, "memory": "mem:ghost@1"}]})
                   + "\n", encoding="utf-8")
    rc, out, err = run("rebuild", "--roots", str(root), index=idx)
    ok(rc == 0 and "Traceback" not in err and list(work.glob("d1.jsonl.corrupt-*")) and KEY in entries_of(idx),
       f"D1: an origin whose lesson is {{}} is a corrupt line, set aside, no traceback ({rc} {err[-300:]!r})")
    rc, out, err = run("query", "gate", index=idx)
    ok(rc == 0 and "Traceback" not in err, f"D1: query after it works ({rc} {err[-200:]!r})")

    idx = work / "d2.jsonl"
    run("rebuild", "--roots", str(root), index=idx)
    record_mem(idx, x, KEY, "mem:d2")
    ent = lesson_of(idx)
    bad = dict(ent, origins=[dict(o, commit=None) for o in ent["origins"]])
    idx.write_text(json.dumps(bad) + "\n", encoding="utf-8")
    rc, out, err = run("rebuild", "--roots", str(root), index=idx)
    ok(rc == 0 and "mem:d2@1" in out and ".corrupt-" in out,
       f"D2: a memory id held only by a corrupt line is named, with where it is kept ({rc} {out!r} {err!r})")

    idx = work / "d3.jsonl"
    run("rebuild", "--roots", str(root), index=idx)
    record_mem(idx, x, KEY, "mem:first")
    first = idx.read_text(encoding="utf-8")
    ent = json.loads(first)
    other = dict(ent, origins=[dict(o, project="p-bbbbbbbbbbbb", memory="mem:second@1") for o in ent["origins"]])
    idx.write_text(first + json.dumps(other) + "\n", encoding="utf-8")
    rc, out, err = run("rebuild", "--roots", str(root), index=idx)
    ids = sorted(o.get("memory") for o in lesson_of(idx)["origins"] if o.get("memory"))
    ok(rc == 0 and ids == ["mem:first@1", "mem:second@1"] and "merged" in out + err,
       f"D3: two lines for one class key merge their origins, said aloud ({rc} {ids} {out!r} {err!r})")


def round10_controls():
    """Round 10 (adversarial): provenance is a checkout path AND the project checked out there.
    F1 a different project at the same path decides nothing; J1/J2 a project-key change at one
    path supersedes, never doubles; F2 a removed worktree counts as gone; G1 record never puts
    one id on two classes nor lowers a revision; H1 an add racing a rebuild is kept; H2/G2 a
    type-malformed line is corrupt, never a traceback; G3 show prints no local paths; G5 merged
    lines keep both provenances."""
    work = tree("tp-lessons-r10-")

    # F1 — project A at root/app; A moves out; project B (its own root commit) takes root/app.
    root = work / "f1"
    root.mkdir()
    a, _ = headed_repo("app", [("retro.md", "export gate", KEY)], parent=root)
    idx = work / "f1.jsonl"
    run("rebuild", "--roots", str(root), index=idx)
    a.rename(work / "elsewhere-app")
    # Its own root commit: a repo named alike, made in the same second, would share A's root SHA.
    b, _ = headed_repo("app-b", [("retro.md", "other entry", "an-unrelated-class")], parent=work)
    b.rename(root / "app")
    rc, out, _ = run("rebuild", "--roots", str(root), index=idx)
    o = lesson_of(idx)["origins"]
    ok(rc == 0 and len(o) == 1 and o[0].get("carried") == "checkout holds another project",
       f"F1: a different project at the same path decides nothing for A's origin ({rc} {o} {out!r})")

    # J2 — the repository is re-initialised in place (new root commit), same retro, a memory id
    # recorded: the old-key origin is superseded, its id moves, one project.
    root = work / "j2"
    root.mkdir()
    x, sha = headed_repo("app", [("retro.md", "export gate", KEY)], parent=root)
    idx = work / "j2.jsonl"
    run("rebuild", "--roots", str(root), index=idx)
    record_mem(idx, x, KEY, "mem:j2")
    old_key = lesson_of(idx)["origins"][0]["project"]
    shutil.rmtree(x / ".git")
    git(x, "init", "-q")
    (x / "NEW").write_text("reinit", encoding="utf-8")
    git(x, "add", "-A")
    git(x, "commit", "-q", "-m", "reinit")
    write_retros(x, [("retro.md", "export gate", KEY)], git(x, "rev-parse", "HEAD"))
    rc, out, _ = run("rebuild", "--roots", str(root), index=idx)
    e = lesson_of(idx)
    ok(rc == 0 and e["projects"] == 1 and e["status"] == "local" and len(e["origins"]) == 1
       and e["origins"][0]["project"] != old_key and e["origins"][0].get("memory") == "mem:j2@1"
       and "project key changed" in out,
       f"J2: a re-initialised repository supersedes its old key; the id moves ({rc} {e['projects']} {out!r})")

    # J1 — a shallow clone is a problem owned by its checkout (its key is unstable); once
    # deepened, the old-key origin is superseded, never a phantom second project.
    src, _ = headed_repo("j1-src", [("retro.md", "export gate", KEY)])
    root = work / "j1"
    root.mkdir()
    sh = root / "app"
    git(work, "clone", "-q", "--depth", "2", f"file://{src}", str(sh))
    idx = work / "j1.jsonl"
    rc, out, _ = run("rebuild", "--roots", str(root), index=idx)
    ok(rc == 0 and "shallow" in out and KEY in entries_of(idx), f"J1: a shallow clone is named ({rc} {out!r})")
    git(sh, "fetch", "-q", "--unshallow")
    rc, out, _ = run("rebuild", "--roots", str(root), index=idx)
    e = lesson_of(idx)
    ok(rc == 0 and e["projects"] == 1 and e["status"] == "local" and "project key changed" in out,
       f"J1: --unshallow supersedes the shallow key; one project ({rc} {e['projects']} {out!r})")

    # F2 — a lesson born in a worktree, merged, the worktree removed, then withdrawn from main:
    # the removed worktree counts as gone (its main checkout no longer lists it), so it leaves.
    root = work / "f2"
    root.mkdir()
    m, sha = headed_repo("app", [("retro.md", "old entry", "an-older-class")], parent=root)
    wt = m / ".claude" / "worktrees" / "feat"
    git(m, "worktree", "add", "-q", "-b", "feat", str(wt))
    write_retros(wt, [("retro.md", "old entry", "an-older-class"), ("retro.md", "export gate", KEY)], sha)
    git(wt, "add", "-A")
    git(wt, "commit", "-q", "-m", "lesson")
    idx = work / "f2.jsonl"
    run("rebuild", "--roots", str(root), index=idx)
    git(m, "merge", "-q", "feat")
    run("rebuild", "--roots", str(root), index=idx)
    git(m, "worktree", "remove", "--force", str(wt))
    git(m, "branch", "-q", "-D", "feat")
    run("rebuild", "--roots", str(root), index=idx)
    write_retros(m, [("retro.md", "old entry", "an-older-class")], sha)
    rc, out, _ = run("rebuild", "--roots", str(root), index=idx)
    ok(rc == 0 and KEY not in entries_of(idx) and "removed" in out,
       f"F2: a removed worktree counts as gone; the withdrawn lesson leaves ({rc} {out!r} {entries_of(idx).get(KEY)})")

    # G1/G1b — record refuses an id another class already holds, and a lower revision.
    root = work / "g1"
    root.mkdir()
    x, _ = headed_repo("app", [("retro.md", "export gate", KEY), ("retro.md", "second", K2)], parent=root)
    idx = work / "g1.jsonl"
    run("rebuild", "--roots", str(root), index=idx)
    ok(record_mem(idx, x, KEY, "mem:aaa") == 0, "G1 fixture")
    before = idx.read_bytes()
    rc, out, err = run("record", entries_of(idx)[K2]["id"], "--answer", "-", cwd=x, index=idx,
                       stdin=json.dumps({"memoryId": "mem:aaa", "revision": 1}))
    ok(rc == 1 and idx.read_bytes() == before and KEY in err,
       f"G1: record refuses an id another class key holds, writing nothing ({rc} {err!r})")
    lid = entries_of(idx)[KEY]["id"]
    run("record", lid, "--answer", "-", cwd=x, index=idx, stdin=json.dumps({"memoryId": "mem:aaa", "revision": 5}))
    before = idx.read_bytes()
    rc, out, err = run("record", lid, "--answer", "-", cwd=x, index=idx,
                       stdin=json.dumps({"memoryId": "mem:aaa", "revision": 2}))
    ok(rc == 1 and idx.read_bytes() == before and mems(idx) == {"mem:aaa@5": [KEY]},
       f"G1b: record refuses a revision lower than the one held ({rc} {err!r} {mems(idx)})")

    # G3 — show prints no checkout paths. G5 — merged lines keep both provenances.
    rc, out, _ = run("show", lid, index=idx)
    ok(rc == 0 and "checkouts" not in out and str(root) not in out and str(root.resolve()) not in out,
       f"G3: show prints no local checkout paths ({out[:200]!r})")
    e = json.loads(idx.read_text(encoding="utf-8").splitlines()[0])
    e1 = json.loads(json.dumps(e))
    e1["origins"][0]["checkouts"] = ["/elsewhere/clone-p"]
    e2 = json.loads(json.dumps(e))
    e2["origins"][0]["checkouts"] = ["/elsewhere/clone-q"]
    g5 = work / "g5.jsonl"
    g5.write_text(json.dumps(e2) + "\n" + json.dumps(e1) + "\n", encoding="utf-8")
    empty = work / "g5-empty"
    empty.mkdir()
    run("rebuild", "--roots", str(empty), index=g5)
    prov = json.loads(g5.read_text(encoding="utf-8").splitlines()[0])["origins"][0].get("checkouts")
    ok(prov == ["/elsewhere/clone-p", "/elsewhere/clone-q"], f"G5: merged lines keep both provenances ({prov})")

    # H2/G2 — type-malformed fields are a corrupt line for every verb, never a traceback.
    base = json.loads(idx.read_text(encoding="utf-8").splitlines()[0])
    muts = {
        "noun-int": lambda e: (e["origins"][0]["lesson"].__setitem__("nouns", [1, 2, 3]),
                               e.__setitem__("nouns", [1, 2, 3])),
        "grade-str": lambda e: e["origins"][0]["lesson"].__setitem__("grade", "2"),
        "classkey-int": lambda e: e["origins"][0]["lesson"].__setitem__("classKey", 7),
        "title-list": lambda e: e["origins"][0]["lesson"].__setitem__("title", ["x"]),
        "checkouts-empty": lambda e: e["origins"][0].__setitem__("checkouts", [""]),
        "entry-nouns-int": lambda e: e.__setitem__("nouns", [1]),
    }
    for name, mut in muts.items():
        bad = json.loads(json.dumps(base))
        mut(bad)
        for verb in (["query", "gate"], ["show", base["id"]], ["candidates", "--min-projects", "1"],
                     ["rebuild", "--roots", str(root)], ["emit-observatory", base["id"]]):
            h = work / f"h2-{name}-{verb[0]}.jsonl"
            h.write_text(json.dumps(bad) + "\n", encoding="utf-8")
            rc, out, err = run(*verb, cwd=x, index=h)
            ok("Traceback" not in err, f"H2/G2: {name} under {verb[0]} is a corrupt line, not a traceback ({rc} {err[-200:]!r})")

    # H1 — an add that lands while a rebuild is between reading the retro and writing.
    root = work / "h1"
    root.mkdir()
    x, sha = headed_repo("app", [("retro.md", "export gate", KEY)], parent=root)
    idx = work / "h1.jsonl"
    run("rebuild", "--roots", str(root), index=idx)
    binp = work / "h1-bin"
    binp.mkdir()
    flag = work / "h1-slow"
    (binp / "git").write_text(f"#!/bin/sh\nif [ \"$1\" = cat-file ] && [ -f {flag} ]; then sleep 4; fi\n"
                              f"exec {shutil.which('git')} \"$@\"\n", encoding="utf-8")
    (binp / "git").chmod(0o755)
    flag.write_text("1", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != "TASK_PIPELINE_LESSONS"}
    env.update(HOME=str(HOME), PATH=f"{binp}:{env['PATH']}")
    proc = subprocess.Popen([sys.executable, str(SCRIPT), "rebuild", "--roots", str(root), "--index", str(idx)],
                            env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(1.5)
    flag.unlink()
    write_retros(x, [("retro.md", "export gate", KEY), ("retro.md", "added mid run", K2)], sha)
    rc_add = run("add", "--retro", "docs/evidence/retro.md", "--entry", "added mid run", cwd=x, index=idx)[0]
    out, err = proc.communicate(timeout=120)
    ok(rc_add == 0 and proc.returncode == 0 and K2 in entries_of(idx),
       f"H1: an add racing a rebuild is kept ({rc_add} {proc.returncode} {out!r} {err!r})")


def source_admission_controls():
    repo, _ = project("source-admission", 1)
    retro = repo / "docs/evidence/retro.md"
    work = tree("tp-lessons-source-admission-")
    idx = work / "index.jsonl"
    ok(run("add", "--retro", str(retro), "--all", cwd=repo, index=idx)[0] == 0,
       "source-admission fixture seeds a valid index")
    before = idx.read_bytes()
    conf = repo / "pipeline.json"
    conf.write_text(json.dumps({"paths": {"artifacts": "missing-artifacts"}}))
    rc, out, err = run("rebuild", "--roots", str(repo), index=idx)
    ok(rc != 0 and idx.read_bytes() == before and "not read" in out + err,
       "explicit missing artifact directory is unknown, not empty")
    conf.unlink()
    original = retro.read_bytes()
    retro.unlink()
    retro.symlink_to("missing-retro.md")
    try:
        rc, out, err = run("rebuild", "--roots", str(repo), index=idx)
        ok(rc != 0 and idx.read_bytes() == before, "dangling canonical retro preserves the index")
    finally:
        retro.unlink()
        retro.write_bytes(original)
    archive = retro.parent / "retro"
    archive.mkdir()
    bad = archive / "not-regular.md"
    bad.mkdir()
    try:
        rc, out, _ = run("rebuild", "--roots", str(repo), index=idx)
        # Round 6: the canonical retro was read and holds the index's lesson, so the rebuild
        # goes on — the bad archive entry is named, never silently skipped.
        ok(rc == 0 and idx.read_bytes() == before and "not read" in out and "not-regular.md" in out,
           f"archive md directory is named, not silently skipped ({rc} {out!r})")
    finally:
        bad.rmdir()
        archive.rmdir()
    conf.symlink_to("missing-config.json")
    try:
        rc, _, _ = run("rebuild", "--roots", str(repo), index=idx)
        ok(rc != 0 and idx.read_bytes() == before, "dangling artifact configuration is not absent configuration")
    finally:
        conf.unlink()
    retro.unlink()
    retro.mkdir()
    try:
        rc, _, _ = run("rebuild", "--roots", str(repo), index=idx)
        ok(rc != 0 and idx.read_bytes() == before, "canonical retro directory refuses as nonregular")
    finally:
        retro.rmdir()
        retro.write_bytes(original)
    archive.symlink_to("absent-archive")
    try:
        rc, _, _ = run("rebuild", "--roots", str(repo), index=idx)
        ok(rc != 0 and idx.read_bytes() == before, "dangling archive refuses as unknown")
    finally:
        archive.unlink()
    docs, saved = repo / "docs", repo / "held-docs"
    docs.rename(saved)
    docs.symlink_to("absent-docs")
    try:
        rc, _, _ = run("rebuild", "--roots", str(repo), index=idx)
        ok(rc != 0 and idx.read_bytes() == before, "dangling default ancestor is not a new empty repository")
    finally:
        docs.unlink()
        saved.rename(docs)
    # Explicit source is hidden from generic os.walk; direct stat must expose EACCES.
    private = repo / ".private-artifacts"
    private.mkdir()
    conf.write_text(json.dumps({"paths": {"artifacts": ".private-artifacts"}}))
    private.chmod(0)
    try:
        rc, _, _ = run("rebuild", "--roots", str(repo), index=idx)
        ok(rc != 0 and idx.read_bytes() == before, "unreadable explicit hidden source preserves the index")
    finally:
        private.chmod(0o755)
        private.rmdir()
        conf.unlink()
    # An absent DEFAULT directory is legitimate for a new repository with no lessons.
    newrepo = work / "new-repo"
    newrepo.mkdir()
    git(newrepo, "init", "-q")
    (newrepo / "README.md").write_text("new repository")
    git(newrepo, "add", "README.md")
    git(newrepo, "commit", "-q", "-m", "initial")
    rc, out, _ = run("rebuild", "--roots", str(newrepo), index=idx)
    # Genuinely empty: no refusal, nothing new derived; the held lesson (another project) is carried.
    ok(rc == 0 and list(entries_of(idx)) == [KEY] and "  not read:" not in out,
       f"new repository without default artifacts is genuinely empty, not a refusal ({rc} {out!r})")


def main():
    a, sha_a = project("alpha", 1)
    b, sha_b = project("beta", 2)
    work = tree("tp-lessons-idx-")
    idx = work / "lessons" / "index.jsonl"

    # --- the schema ships and names exactly the fields the script accepts
    ok(SCHEMA.is_file(), "templates/lesson.schema.json ships")
    sch = json.loads(SCHEMA.read_text(encoding="utf-8"))
    ok(sch.get("additionalProperties") is False, "lesson/1 refuses unknown fields")
    ok(set(sch["required"]) == {"schema", "classKey", "title", "trigger", "check", "grade",
                                "stages", "nouns", "origin"}, "lesson/1 required fields")

    # --- absent index: said, not an error
    rc, out, _ = run("query", "gate", index=idx)
    ok(rc == 0 and "absent" in out, f"query on an absent index says so and exits 0 ({rc} {out!r})")

    # --- add from two projects → one lesson, projects 2
    rc, out, err = run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=a, index=idx)
    ok(rc == 0, f"add --all from project alpha ({rc} {err})")
    ok("1 lesson" in out and "1 entry carries no Lesson line" in out,
       f"add reports the lesson and the private entry it skipped ({out!r})")
    rc, out, err = run("add", "--retro", "docs/evidence/retro.md",
                       "--entry", "2026-10-02-beta-export-gate-6-reopened-twice", cwd=b, index=idx)
    ok(rc == 0, f"add --entry from project beta ({rc} {err})")
    rc, out, _ = run("query", "gate", "artefact", "--limit", "5", index=idx)
    lines = [ln for ln in out.splitlines() if ln.startswith("[lesson L-")]
    ok(len(lines) == 1, f"one class seen twice is one lesson ({out!r})")
    ok("projects 2" in lines[0] and "seen 2" in lines[0],
       f"query prints the lesson with projects 2 ({lines[0]!r})")
    ok("alpha" not in out and "beta" not in out and str(a) not in out,
       "query names no project and no path")
    ok(len(lines[0]) < 400, "one line per lesson")

    # --- modes
    ok(stat.S_IMODE(idx.parent.stat().st_mode) == 0o700, "index directory is 0700")
    ok(stat.S_IMODE(idx.stat().st_mode) == 0o600, "index file is 0600")

    # --- a repeat from the same project revises, never mints
    before = idx.read_bytes()
    rc, _, _ = run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=a, index=idx)
    ok(rc == 0 and idx.read_bytes() == before, "re-adding the same entry changes nothing")

    # --- candidates: projects >= 2 only
    single = {"schema": "lesson/1", "classKey": "one-project-only", "title": "a class only one project saw",
              "trigger": "never twice", "check": "test/x.py", "grade": 2,
              "stages": {"owned": 4, "surfaced": 6}, "nouns": ["one", "project", "only"],
              "origin": {"commit": sha_a, "retro": "docs/evidence/retro.md#x"}}
    rc, out, err = run("add", "--json", "-", cwd=a, stdin=json.dumps(single), index=idx)
    ok(rc == 0, f"add --json from stdin ({rc} {err})")
    rc, out, _ = run("candidates", index=idx)
    ok("absence-needs-its-own-check" in out and "one-project-only" not in out,
       f"candidates lists only lessons two projects hold ({out!r})")

    # --- refusals leave the index byte-identical
    before = idx.read_bytes()
    for field, bad, why in (("check", "see /Users/someone/repo/test.py", "an absolute path"),
                            ("trigger", "when ~/work/x breaks", "a home path"),
                            ("title", "read https://intranet.example/x", "a URL"),
                            ("check", "token AKIA" + "A" * 16, "a credential shape"),
                            ("title", "x\ny", "a line break")):
        bad_lesson = dict(single, classKey="refused-one", **{field: bad})
        rc, out, err = run("add", "--json", "-", cwd=a, stdin=json.dumps(bad_lesson), index=idx)
        ok(rc == 1 and idx.read_bytes() == before,
           f"a lesson carrying {why} is refused and nothing is written ({rc} {err!r})")
    extra = dict(single, classKey="refused-two", transcript="...")
    rc, _, err = run("add", "--json", "-", cwd=a, stdin=json.dumps(extra), index=idx)
    ok(rc == 1 and "transcript" in err, "an unknown field is refused by name")
    ghost = dict(single, classKey="refused-three", origin={"commit": "0" * 40, "retro": "docs/evidence/retro.md#x"})
    rc, _, err = run("add", "--json", "-", cwd=a, stdin=json.dumps(ghost), index=idx)
    ok(rc == 1 and "resolve" in err, "a commit that does not resolve in the repository is refused")
    ok(idx.read_bytes() == before, "the index is untouched by every refusal")

    # --- rebuild equals the incremental index (without the --json-only lesson)
    inc = work / "inc" / "index.jsonl"
    for repo in (a, b):
        run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=repo, index=inc)
    reb = work / "reb" / "index.jsonl"
    roots = tree("tp-lessons-roots-")
    os.symlink(a, roots / "alpha")
    os.symlink(b, roots / "beta")
    rc, out, err = run("rebuild", "--roots", str(roots), index=reb)
    ok(rc == 0, f"rebuild ({rc} {err})")
    ok(reb.read_bytes() == inc.read_bytes(), "rebuild from the retros equals the incremental index")
    ok("2 retro" in out, f"rebuild says how many retros it read ({out!r})")

    # --- emit-observatory and record
    rc, out, _ = run("query", "gate", index=idx)
    lid = out.split("[lesson ")[1].split("]")[0]
    rc, out, err = run("emit-observatory", lid, cwd=a, index=idx)
    ok(rc == 0, f"emit-observatory ({rc} {err})")
    args = json.loads(out)
    ok(args["tool"] == "observatory_record" and args["arguments"]["statement"].startswith(
        "lesson: absence-needs-its-own-check — "), "the bridge write is observatory_record with a `lesson:` statement")
    ok({"kind": "commit", "ref": "commit:" + sha_a[:12]} in args["arguments"]["evidence"],
       "the evidence commit travels as commit:<12 hex>, the form the store keeps")
    if redact is not None:
        survived = redact(args["arguments"])
        ok(json.dumps(survived) == json.dumps(args["arguments"]),
           f"the store's redactor ({REDACTOR}) changes nothing in the emitted arguments: the commit survives")
        full = redact({"evidence": [{"kind": "commit", "sha": sha_a}]})
        ok(sha_a not in json.dumps(full),
           "a full 40-hex SHA would not survive the redactor — the reason for the short form")
    else:
        print(f"skipped: the engine-redactor case — {SKIP_WHY}")
    ok(args["arguments"]["owner"] == "agent:task-pipeline", "owner is named, never operator")
    key_a = "p-" + git(a, "rev-list", "--max-parents=0", "HEAD").split()[0][:12]
    ok("projectId" not in args["arguments"] and any(e.get("project") == key_a for e in args["arguments"]["evidence"]),
       "the store gets the pseudonymous key, never a project:<slug> id")
    # observatory_lesson's arguments, pinned to the engine's published inputSchema
    # (project-observatory-dashboard #251: `observatory_lesson` with a LessonOrigin model,
    # extra fields forbidden). The engine's own fixture is pinned to this output in turn.
    rc, out, err = run("emit-observatory", lid, "--tool", "observatory_lesson", cwd=a, index=idx)
    ok(rc == 0, f"--tool observatory_lesson ({rc} {err!r})")
    lo = json.loads(out)
    la = lo["arguments"]
    ok(lo["tool"] == "observatory_lesson"
       and set(la) == {"owner", "classKey", "title", "trigger", "check", "nouns", "origin"}
       and set(la["origin"]) == {"projectId", "commit"},
       f"observatory_lesson carries exactly owner, classKey, title, trigger, check, nouns, origin ({sorted(la)})")
    import re as _re3
    ok(_re3.fullmatch(r"p-[0-9a-f]{12}", la["origin"]["projectId"])
       and la["origin"]["projectId"] == key_a
       and la["origin"]["commit"] == "commit:" + sha_a[:12]
       and _re3.fullmatch(r"(?:commit:)?[0-9a-f]{7,40}", la["origin"]["commit"])
       and _re3.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", la["classKey"])
       and 8 <= len(la["title"]) <= 160 and 3 <= len(la["trigger"]) <= 200 and 3 <= len(la["check"]) <= 200
       and 3 <= len(la["nouns"]) <= 8 and la["owner"] == "agent:task-pipeline",
       f"each field meets the engine's pattern and bounds ({la['origin']})")
    rc, out, _ = run("emit-observatory", lid, cwd=a, index=idx)
    ok(json.loads(out)["tool"] == "observatory_record", "without --tool the route is observatory_record")
    rc, _, _ = run("emit-observatory", lid, "--tool", "observatory_learn", cwd=a, index=idx)
    ok(rc == 2, "no other tool is offered: observatory_learn is not the retro write")
    rc, _, _ = run("emit-observatory", lid, "--project-id", "project:alpha", cwd=a, index=idx)
    ok(rc == 2, "--project-id is gone: a slug never reaches the store")
    ledger = a / ".task-pipeline" / "run.md"
    ledger.parent.mkdir()
    ledger.write_text("# Run ledger\n\nRun: `x`\n\n## Log\n\n", encoding="utf-8")
    rc, out, err = run("record", lid, "--answer", "-", "--ledger", str(ledger), cwd=a,
                       stdin=json.dumps({"memoryId": "mem:abc", "revision": 1}), index=idx)
    ok(rc == 0 and "mem:abc@1" in idx.read_text(encoding="utf-8"), f"record keeps the memory id ({rc} {err})")
    ok("event: lessons — recorded" in ledger.read_text(encoding="utf-8"), "record appends one ledger line")
    rc, _, err = run("record", lid, "--answer", "-", "--ledger", str(ledger), cwd=a,
                     stdin=json.dumps({"memoryId": "mem:abc", "revision": "two"}), index=idx)
    ok(rc == 2 and "revision" in err, f"a non-numeric revision is exit 2, named ({rc} {err!r})")
    rc, out, _ = run("emit-observatory", lid, cwd=a, index=idx)
    again = json.loads(out)["arguments"]
    ok(again.get("memoryId") == "mem:abc" and again.get("expectedRevision") == 1,
       "a recorded lesson is revised, not minted again: memoryId and expectedRevision are emitted")
    rc, out, err = run("record", lid, "--answer", "-", "--ledger", str(ledger), cwd=a,
                       stdin=json.dumps({"error": "bounds", "message": "too long"}), index=idx)
    ok(rc == 0 and "event: lessons — store refused — bounds" in ledger.read_text(encoding="utf-8"),
       f"a refusal is one ledger line, exit 0, the local entry kept ({rc} {err})")

    # --- origin.project is the repository's own key: a supplied other key is refused
    before = idx.read_bytes()
    forged = dict(single, classKey="forged-origin",
                  origin={"project": "p-000000000000", "commit": sha_a, "retro": "docs/evidence/retro.md#x"})
    rc, _, err = run("add", "--json", "-", cwd=a, stdin=json.dumps(forged), index=idx)
    ok(rc == 1 and "p-000000000000" in err and key_a in err and idx.read_bytes() == before,
       f"an add from alpha claiming p-000000000000 is refused, naming both keys ({rc} {err!r})")
    rc, out, _ = run("candidates", index=idx)
    ok("forged-origin" not in out, "candidates lists nothing from a refused origin")
    bad_shape = dict(single, classKey="bad-shape",
                     origin={"project": "alpha", "commit": sha_a, "retro": "docs/evidence/retro.md#x"})
    rc, _, err = run("add", "--json", "-", cwd=a, stdin=json.dumps(bad_shape), index=idx)
    ok(rc == 1 and "origin.project" in err, "an origin.project that is not a pseudonymous key is refused")

    # --- seen counts origins, projects counts distinct projects
    two = idx.parent / "two.jsonl"
    one_proj = [dict(single, classKey="same-project-twice",
                     origin={"commit": sha_a, "retro": f"docs/evidence/retro.md#entry-{i}"}) for i in (1, 2)]
    run("add", "--json", "-", cwd=a, stdin=json.dumps(one_proj), index=two)
    e = json.loads(two.read_text(encoding="utf-8").splitlines()[0])
    ok(e["seen"] == 2 and e["projects"] == 1 and e["status"] == "local",
       f"two entries of one project: seen 2, projects 1, not a candidate ({e['seen']} {e['projects']})")

    # --- the e-mail and hex patterns
    for field, bad, why in (("check", "ask someone@example.org first", "an e-mail address"),
                            ("trigger", "after " + "deadbeef" * 5, "a long hex run")):
        rc, _, err = run("add", "--json", "-", cwd=a, index=idx,
                         stdin=json.dumps(dict(single, classKey="pattern-" + field, **{field: bad})))
        ok(rc == 1 and why in err, f"{why} is refused by name ({rc} {err!r})")

    # --- rebuild keeps the memory ids `record` stored
    rc, _, _ = run("rebuild", "--roots", str(roots), index=idx)
    ok(rc == 0 and "mem:abc@1" in idx.read_text(encoding="utf-8"), "rebuild keeps the recorded memory ids")

    # --- Unicode headings keep their letters in the anchor
    c, sha_c = project("gamma", 3)
    rp = c / "docs" / "evidence" / "retro.md"
    rp.write_text(rp.read_text(encoding="utf-8").replace("gate 6 reopened twice", "ворота открылись дважды"),
                  encoding="utf-8")
    rc, out, err = run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=c, index=idx)
    ok(rc == 0, f"a heading in Cyrillic is a valid anchor ({rc} {err!r})")
    rc, out, _ = run("show", lid, index=idx)
    ok("ворота-открылись-дважды" in json.dumps(json.loads(out), ensure_ascii=False),
       "the anchor keeps its Unicode letters")

    # --- a directory the script did not create keeps its mode
    shared = tree("tp-lessons-shared-")
    os.chmod(shared, 0o755)
    rc, _, _ = run("add", "--json", "-", cwd=a, stdin=json.dumps(single), index=shared / "index.jsonl")
    ok(rc == 0 and stat.S_IMODE(shared.stat().st_mode) == 0o755,
       "a directory the script did not create is not chmod-ed")
    ro = tree("tp-lessons-ro-")
    os.chmod(ro, 0o500)
    rc, _, err = run("add", "--json", "-", cwd=a, stdin=json.dumps(single), index=ro / "sub" / "index.jsonl")
    os.chmod(ro, 0o700)
    ok(rc == 1 and "Traceback" not in err, f"an unwritable index location is a refusal, not a traceback ({rc} {err!r})")

    # --- the two flakes of round 2, made deterministic. (1) A git that does not answer in
    # time used to read as "no commit" / "does not resolve" — under parallel load that turned
    # a busy machine into a refusal about the lesson. Now it is its own refusal, named.
    shim = tree("tp-lessons-slowgit-")
    real_git = shutil.which("git")
    (shim / "git").write_text(f"#!/bin/sh\nsleep 3\nexec {real_git} \"$@\"\n")
    os.chmod(shim / "git", 0o755)
    rc, _, err = run("add", "--json", "-", cwd=a, stdin=json.dumps(dict(single, classKey="slow-git")),
                     index=idx, env_extra={"PATH": f"{shim}:{os.environ['PATH']}",
                                           "TASK_PIPELINE_GIT_TIMEOUT": "1"})
    ok(rc == 1 and "did not answer" in err and "no commit" not in err and "resolve" not in err,
       f"a git that times out is named as such, never as a missing commit ({rc} {err!r})")
    # (2) Two first writers race between "the directory is missing" and mkdir: the loser's
    # FileExistsError used to become a refusal. Simulated in-process: the check says missing,
    # the directory exists.
    sys.path.insert(0, str(SCRIPT.parent))
    import lessons as L  # noqa: E402
    raced = tree("tp-lessons-raced-") / "made-by-the-other-writer"
    raced.mkdir(mode=0o755)
    os.chmod(raced, 0o755)
    real_exists = pathlib.Path.exists
    pathlib.Path.exists = lambda self: False if self == raced else real_exists(self)
    try:
        L._ensure_dir(raced)
        raced_ok = True
    except L.Refused:
        raced_ok = False
    finally:
        pathlib.Path.exists = real_exists
    ok(raced_ok and stat.S_IMODE(raced.stat().st_mode) == 0o755,
       "a directory another writer created first is used as it is, not refused nor chmod-ed")
    # (3) Output under a non-UTF-8 locale: the script printed an em dash and crashed.
    rc, out, _ = run("query", "gate", index=idx, env_extra={"LC_ALL": "en_US.ISO8859-1", "PYTHONUTF8": "0",
                                                          "PYTHONIOENCODING": ""})
    ok(rc == 0, f"query under an ISO-8859-1 locale exits 0 ({rc})")
    # ...and nothing is lost there: what a machine reads (emit, show) is lossless JSON, and
    # what comes in on stdin is read as UTF-8 whatever the locale.
    latin = {"LC_ALL": "en_US.ISO8859-1", "PYTHONUTF8": "0", "PYTHONIOENCODING": ""}
    cyr = dict(single, classKey="cyrillic-title", title="проверка читает артефакт, а не строку успеха")
    rc, _, err = run("add", "--json", "-", cwd=a, stdin=json.dumps(cyr, ensure_ascii=False), index=idx,
                     env_extra=latin)
    ok(rc == 0, f"add --json - under ISO-8859-1 ({rc} {err!r})")
    stored = [json.loads(ln) for ln in idx.read_text(encoding="utf-8").splitlines()
              if json.loads(ln)["classKey"] == "cyrillic-title"]
    ok(stored and stored[0]["title"] == cyr["title"],
       f"a Cyrillic title read from stdin under ISO-8859-1 is stored intact ({stored[0]['title'] if stored else None!r})")
    cid = stored[0]["id"]
    rc_u, out_u, _ = run("emit-observatory", cid, cwd=a, index=idx)
    rc_l, out_l, _ = run("emit-observatory", cid, cwd=a, index=idx, env_extra=latin)
    ok(rc_u == 0 and rc_l == 0 and json.loads(out_l) == json.loads(out_u),
       "emit-observatory under ISO-8859-1 gives the same JSON as under UTF-8: lossless")
    rc_s, out_s, _ = run("show", cid, index=idx, env_extra=latin)
    ok(rc_s == 0 and json.loads(out_s)["title"] == cyr["title"], "show under ISO-8859-1 is lossless too")

    # --- the schema's anchor pattern is the script's, character for character
    ok(sch["properties"]["origin"]["properties"]["retro"]["pattern"] == L.RETRO_REF.pattern,
       "lesson.schema.json's origin.retro pattern equals lessons.py's RETRO_REF")
    # --- a lock that cannot be opened is a refusal, not a traceback
    lockless = tree("tp-lessons-lockless-")
    os.chmod(lockless, 0o500)
    rc, _, err = run("add", "--json", "-", cwd=a, stdin=json.dumps(single), index=lockless / "index.jsonl")
    os.chmod(lockless, 0o700)
    ok(rc == 1 and "lock" in err and "Traceback" not in err, f"an unopenable lock is a refusal ({rc} {err!r})")
    # --- a revision is ASCII digits from 1
    for bad_rev in (0, "0", "\u0661", -1):
        rc, _, err = run("record", lid, "--answer", "-", cwd=a, index=idx,
                         stdin=json.dumps({"memoryId": "mem:abc", "revision": bad_rev}))
        ok(rc == 2 and "revision" in err, f"revision {bad_rev!r} is refused, exit 2 ({rc})")

    # --- the artifact-root rule is the shared one, register for register
    js = (ROOT / "bin" / "lib" / "artifact-root.js").read_text(encoding="utf-8")
    import re as _re2
    js_regs = tuple(_re2.findall(r"'([^']+)'", _re2.search(r"const REGISTERS = \[(.*?)\]", js, _re2.S).group(1)))
    js_known = tuple(_re2.findall(r"'([^']+)'", _re2.search(r"const KNOWN = \[(.*?)\]", js, _re2.S).group(1)))
    ok(L.ARTIFACT_REGISTERS == js_regs and L.ARTIFACT_KNOWN == js_known,
       f"lessons.py reads the artifact root with artifact-root.js's names and registers ({L.ARTIFACT_REGISTERS} vs {js_regs})")

    # --- complete rebuild repairs corrupt projection; an unknown source cannot replace it
    rb2 = work / "rb2" / "index.jsonl"
    rb2.parent.mkdir(parents=True, exist_ok=True)
    rb2.write_text("{not json\n", encoding="utf-8")
    rc, out, err = run("rebuild", "--roots", str(roots), index=rb2)
    ok(rc == 0 and "previous index" in out and "absence-needs-its-own-check" in rb2.read_text(encoding="utf-8"),
       f"rebuild replaces a corrupt index instead of refusing it ({rc} {out!r} {err!r})")
    rc, out, err = run("rebuild", "--roots", str(roots), index=work / "rb3" / "index.jsonl",
                       env_extra={"PATH": f"{shim}:{os.environ['PATH']}", "TASK_PIPELINE_GIT_TIMEOUT": "1"})
    ok(rc == 1 and out.count("not read") >= 2 and "did not answer" in out
       and not (work / "rb3" / "index.jsonl").exists(),
       f"git timeouts report all unknown sources and refuse index replacement ({rc} {out!r})")

    # --- cycle 4: a corrupt old index never blocks; an unreadable index is never replaced
    h3 = tree("tp-lessons-home3-")
    leg3 = h3 / ".task-pipeline" / "lessons" / "index.jsonl"
    leg3.parent.mkdir(parents=True)
    leg3.write_text("not json\n", encoding="utf-8")
    (h3 / ".sshlg-skills").mkdir()
    rc, out, err = run("rebuild", "--roots", str(roots), env_extra={"HOME": str(h3)})
    kept = list(leg3.parent.glob("index.jsonl.corrupt-*"))
    ok(rc == 0 and kept and not leg3.exists() and "corrupt" in err,
       f"a corrupt old index is set aside as .corrupt-<date>, said once, and rebuild works ({rc} {err!r})")
    rc, out, err = run("query", "gate", env_extra={"HOME": str(h3)})
    ok(rc == 0 and "corrupt" not in err, f"query works after, and the notice is not repeated ({rc} {err!r})")

    locked_idx = work / "rb-locked" / "index.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=a, index=locked_idx)
    lk_lid = json.loads(locked_idx.read_text(encoding="utf-8").splitlines()[0])["id"]
    run("record", lk_lid, "--answer", "-", cwd=a, index=locked_idx,
        stdin=json.dumps({"memoryId": "mem:abc", "revision": 3}))
    os.chmod(locked_idx, 0o000)
    rc, out, err = run("rebuild", "--roots", str(roots), index=locked_idx)
    os.chmod(locked_idx, 0o600)
    ok(rc == 1 and str(locked_idx) in err and "mem:abc@3" in locked_idx.read_text(encoding="utf-8"),
       f"an index that cannot be READ is a refusal naming it, and nothing is replaced ({rc} {err!r})")

    corrupt_idx = work / "rb-corrupt" / "index.jsonl"
    corrupt_idx.parent.mkdir(parents=True)
    corrupt_idx.write_text("{broken\n", encoding="utf-8")
    rc, out, err = run("rebuild", "--roots", str(roots), index=corrupt_idx)
    ok(rc == 0 and list(corrupt_idx.parent.glob("index.jsonl.corrupt-*"))
       and "absence-needs-its-own-check" in corrupt_idx.read_text(encoding="utf-8"),
       f"an index that cannot be PARSED is kept as .corrupt-<date>, then replaced ({rc} {err!r})")

    future_idx = work / "rb-future" / "index.jsonl"
    run("add", "--json", "-", cwd=a, stdin=json.dumps(dict(single, classKey="present-day")), index=future_idx)
    fline = json.dumps({"schema": "lesson-index/2", "classKey": "from-the-future", "x": 1})
    with future_idx.open("a", encoding="utf-8") as fh:
        fh.write(fline + "\n")
    rc, out, err = run("add", "--json", "-", cwd=a, stdin=json.dumps(dict(single, classKey="added-later")),
                       index=future_idx)
    body = future_idx.read_text(encoding="utf-8")
    ok(rc == 0 and "1 line" in err and "newer format" in err and fline in body and "added-later" in body,
       f"a line in a newer format is skipped, counted, and kept on write ({rc} {err!r})")

    h4 = tree("tp-lessons-home4-")
    run("add", "--json", "-", cwd=a, stdin=json.dumps(dict(single, classKey="in-the-old-file")),
        env_extra={"HOME": str(h4)})
    (h4 / ".sshlg-skills").mkdir()
    run("add", "--json", "-", cwd=a, stdin=json.dumps(dict(single, classKey="in-the-new-file")),
        index=h4 / ".sshlg-skills" / "lessons" / "index.jsonl")
    rc, out, err = run("candidates", "--min-projects", "1", env_extra={"HOME": str(h4)})
    ok(rc == 0 and "in-the-old-file" in out and "in-the-new-file" in out and "both" in err,
       f"when both index files exist both are read, and that is said ({rc} {out!r} {err!r})")
    rc, out, err = run("candidates", "--min-projects", "1", env_extra={"HOME": str(h4)})
    ok("both" not in err and "in-the-old-file" in out, "said once: the old file is merged and set aside")

    # --- cycle 5: every index-file operation under one lock; corrupt handling the same for both
    # files; a merge never overwrites. Each scenario is run by several processes AT ONCE.
    def parallel(n, args, home, stdin=None):
        env = {k: v for k, v in os.environ.items() if k != "TASK_PIPELINE_LESSONS"}
        env["HOME"] = str(home)
        procs = [subprocess.Popen([sys.executable, str(SCRIPT), *args], cwd=a, env=env,
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                 for _ in range(n)]
        outs = [pr.communicate(input=(stdin or "").encode(), timeout=120) for pr in procs]
        return [(pr.returncode, o.decode("utf-8", "replace"), e.decode("utf-8", "replace"))
                for pr, (o, e) in zip(procs, outs)]

    def legacy_of(h):
        return h / ".task-pipeline" / "lessons" / "index.jsonl"

    def family_of(h):
        return h / ".sshlg-skills" / "lessons" / "index.jsonl"

    def entry_line(class_key, title):
        le = dict(single, classKey=class_key, title=title)
        h0 = tree("tp-lessons-mk-")
        run("add", "--json", "-", cwd=a, stdin=json.dumps(le), index=h0 / "i.jsonl")
        return (h0 / "i.jsonl").read_text(encoding="utf-8").strip()

    # (1) a good old index and a corrupt new one: rebuild and query both exit 0, in parallel
    h5 = tree("tp-lessons-c5a-")
    legacy_of(h5).parent.mkdir(parents=True)
    legacy_of(h5).write_text(entry_line("old-and-good", "an old lesson that is fine") + "\n", encoding="utf-8")
    family_of(h5).parent.mkdir(parents=True)
    family_of(h5).write_text("{corrupt\n", encoding="utf-8")
    res = parallel(3, ["rebuild", "--roots", str(roots)], h5) + parallel(3, ["query", "gate"], h5)
    ok(all(rc == 0 and "Traceback" not in err for rc, _, err in res),
       f"good old + corrupt new: rebuild and query exit 0 ({[(rc, err[-160:]) for rc, _, err in res if rc]})")
    # Round 6: the merge notice says what was read — a family file set aside was not read.
    h5b = tree("tp-lessons-c5a-msg-")
    legacy_of(h5b).parent.mkdir(parents=True)
    legacy_of(h5b).write_text(entry_line("old-and-good", "an old lesson that is fine") + "\n", encoding="utf-8")
    family_of(h5b).parent.mkdir(parents=True)
    family_of(h5b).write_text("{corrupt\n", encoding="utf-8")
    rc, out, err = run("query", "gate", env_extra={"HOME": str(h5b)})
    ok(rc == 0 and "read both" not in err and "corrupt and set aside" in err and "old-and-good" in
       family_of(h5b).read_text(encoding="utf-8"),
       f"a corrupt family index set aside is not reported as 'read both' ({rc} {err!r})")

    # (2) six concurrent queries on a corrupt old index with the family directory present
    bad_runs = []
    for trial in range(30):
        h6 = tree("tp-lessons-c5b-")
        legacy_of(h6).parent.mkdir(parents=True)
        legacy_of(h6).write_text("not json\n", encoding="utf-8")
        (h6 / ".sshlg-skills").mkdir()
        for rc, _, err in parallel(6, ["query", "gate"], h6):
            if rc != 0 or "Traceback" in err:
                bad_runs.append((trial, rc, err[-200:]))
        shutil.rmtree(h6, ignore_errors=True)
    ok(not bad_runs, f"6 concurrent queries x 30 trials on a corrupt old index: no traceback ({bad_runs[:2]})")

    # (3) a stale old title never overwrites a newer family title; (4) a future line survives
    h7 = tree("tp-lessons-c5c-")
    legacy_of(h7).parent.mkdir(parents=True)
    future_line = json.dumps({"schema": "lesson-index/2", "classKey": "next-format", "x": 1})
    legacy_of(h7).write_text(entry_line("shared-class", "the stale old title of it") + "\n"
                             + entry_line("only-in-old", "a lesson only the old file has") + "\n"
                             + future_line + "\n", encoding="utf-8")
    family_of(h7).parent.mkdir(parents=True)
    family_of(h7).write_text(entry_line("shared-class", "the newer family title") + "\n", encoding="utf-8")
    res = parallel(4, ["candidates", "--min-projects", "1"], h7)
    body7 = family_of(h7).read_text(encoding="utf-8")
    titles = {json.loads(ln)["classKey"]: json.loads(ln).get("title") for ln in body7.splitlines()}
    ok(all(rc == 0 for rc, _, _ in res) and titles.get("shared-class") == "the newer family title",
       f"the family copy wins: a stale old title never overwrites it ({titles.get('shared-class')!r})")
    ok("only-in-old" in titles, "a lesson only the old file has is copied across")
    ok(future_line in body7, "a lesson-index/2 line survives the merge verbatim")
    ok(not legacy_of(h7).exists() and len(list(legacy_of(h7).parent.glob("index.jsonl.migrated*"))) == 1,
       "the old file is renamed .migrated, once, by exactly one of the concurrent runs")

    # --- lock contention: a held lock makes add refuse, nothing written
    try:
        import fcntl
    except ImportError:
        fcntl = None
    if fcntl:
        before = idx.read_bytes()
        fh = open(idx.parent / ".lock", "a+")
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        t0 = time.time()
        late = dict(single, classKey="late-writer")
        rc, out, err = run("add", "--json", "-", cwd=a, stdin=json.dumps(late), index=idx,
                           env_extra={"TASK_PIPELINE_LESSONS_LOCK_TIMEOUT": "1"})
        fh.close()
        ok(rc == 1 and "locked" in err and idx.read_bytes() == before and time.time() - t0 < 30,
           f"a held lock refuses after its timeout, nothing written ({rc} {err!r})")
        conc = work / "conc" / "index.jsonl"
        procs = []
        for i in range(4):
            le = dict(single, classKey=f"concurrent-{i}")
            env = {k: v for k, v in os.environ.items() if k != "TASK_PIPELINE_LESSONS"}
            env.update(HOME=str(HOME), TASK_PIPELINE_LESSONS=str(conc))
            procs.append(subprocess.Popen([sys.executable, str(SCRIPT), "add", "--json", "-"],
                                          cwd=a, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, text=True, env=env))
            procs[-1].stdin.write(json.dumps(le))
            procs[-1].stdin.close()
        codes = [p.wait(timeout=60) for p in procs]
        keys = {json.loads(ln)["classKey"] for ln in conc.read_text(encoding="utf-8").splitlines()}
        ok(codes == [0, 0, 0, 0] and keys == {f"concurrent-{i}" for i in range(4)},
           f"four concurrent writers lose nothing; the env var names the index ({codes} {keys})")
    else:
        print("note: no fcntl here — the lock cases were not run")

    # --- the default index never switches silently: once ~/.sshlg-skills appears, the
    # standalone index is moved there once, and the move is said
    h2 = tree("tp-lessons-home2-")
    rc, _, err = run("add", "--json", "-", cwd=a, stdin=json.dumps(dict(single, classKey="before-the-move")),
                     env_extra={"HOME": str(h2)})
    legacy = h2 / ".task-pipeline" / "lessons" / "index.jsonl"
    ok(rc == 0 and legacy.is_file(), f"a standalone add writes ~/.task-pipeline/lessons ({rc} {err!r})")
    (h2 / ".sshlg-skills").mkdir()
    rc, out, err = run("candidates", "--min-projects", "1", env_extra={"HOME": str(h2)})
    moved = h2 / ".sshlg-skills" / "lessons" / "index.jsonl"
    ok(rc == 0 and "before-the-move" in out, f"after ~/.sshlg-skills appears the lessons are still read ({out!r})")
    ok(moved.is_file() and "moved the local index" in err and str(legacy) in err,
       f"the index is moved once, and the move is said ({err!r})")
    ok(not legacy.exists() and legacy.with_name("index.jsonl.migrated").is_file(),
       "the old file is kept beside, renamed .migrated, so nothing reads two indexes")
    rc, _, err = run("candidates", env_extra={"HOME": str(h2)})
    ok("moved the local index" not in err, "the move is said once, not on every run")

    # --- the default index: task-pipeline's own, unless the family's directory already exists
    rc, out, _ = run("path")
    ok(rc == 0 and out.strip() == str(HOME / ".task-pipeline" / "lessons" / "index.jsonl"),
       f"without ~/.sshlg-skills the default is ~/.task-pipeline/lessons/index.jsonl ({out!r})")
    ok(not (HOME / ".sshlg-skills").exists(), "a standalone install never creates the family's directory")
    (HOME / ".sshlg-skills").mkdir()
    rc, out, _ = run("path")
    ok(rc == 0 and out.strip() == str(HOME / ".sshlg-skills" / "lessons" / "index.jsonl"),
       f"with ~/.sshlg-skills present the default is its lessons/index.jsonl ({out!r})")
    conservative_rebuild_controls()
    partial_rebuild_controls()
    carry_forward_controls()
    identity_controls()
    low_controls()
    provenance_controls()
    index_shape_controls()
    round10_controls()
    source_admission_controls()
    print(f"PASS: lessons.py — {CASES} cases")


if __name__ == "__main__":
    main()
