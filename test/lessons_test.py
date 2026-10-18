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
import hashlib
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
        ok(rc == 0 and idx.read_bytes() == before and "not read" in out and blocked.name in out
           and str(blocked) not in out,
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
    ok(rc == 0 and "not read" in out and blocked.name in out and unread_idx.is_file()
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
    reasons = {x["project"]: x.get("carried") for x in e["origins"]}
    # Round 11 (narrowed): nothing leaves on its own. f1's withdrawn entry is carried as
    # `no checkout read holds it`, f2's as `checkout not read` — per origin, each its own reason.
    ok(rc == 0 and reasons.get(f2_key) == "checkout not read" and len(reasons) == 2
       and sorted(reasons.values()) == ["checkout not read", "no checkout read holds it"]
       and "removed" not in out,
       f"carry is per origin: a withdrawn entry and an unreadable root each carried with their reason ({rc} {out!r} {e})")

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
        # Atomically (round 16): a rebuild racing this write (H1) reads the old file or the new
        # one, never half of either.
        tmp = p.with_name(p.name + ".tmp")
        tmp.write_text("# Retro\n\n## Log\n\n" + "\n".join(bodies), encoding="utf-8")
        os.replace(tmp, p)


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


def high_root_repo(name, entries, parent):
    """headed_repo whose root commit sorts in the upper half (round 16): a later root that must
    sort BELOW it is then a few tries away, never a fixture flake."""
    for attempt in range(60):
        stage = parent.parent / f".stage-{parent.name}-{name}-{attempt}"
        repo, sha = headed_repo(name, entries, parent=stage)
        if git(repo, "rev-list", "--max-parents=0", "HEAD")[0] in "89abcdef":
            parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(repo), str(parent / name))
            shutil.rmtree(stage)
            return parent / name, sha
        shutil.rmtree(stage)  # a failed attempt leaves no repository behind
    raise SystemExit(f"fixture {name}: no upper-half root in 60 tries")

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
    e = lesson_of(idx)
    new = [x for x in e["origins"] if "carried" not in x]
    old = [x for x in e["origins"] if x.get("carried")]
    # Round 11: the old anchor is carried (`no checkout read holds it`), never removed; the id
    # follows the class onto the re-derived origin, and one project is counted.
    ok(rc == 0 and len(new) == 1 and new[0]["retro"].startswith("docs/evidence/retro/2026-Q4.md#")
       and new[0].get("memory") == "mem:p1@1" and [x["carried"] for x in old] == ["no checkout read holds it"]
       and e["projects"] == 1,
       f"P1: a rotated entry keeps its memory id; the old anchor is carried ({rc} {e['origins']})")

    # P2 — the heading is reworded (the anchor changes); the id stays with the class.
    d, sha = headed_repo("p2", [("retro.md", "2026-10-01 export gate", KEY)])
    idx = work / "p2.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=d, index=idx)
    record_mem(idx, d, KEY, "mem:p2")
    write_retros(d, [("retro.md", "2026-10-01 export gate reopened", KEY)], sha)
    rc, out, err = run("rebuild", "--roots", str(d), index=idx)
    new = [x for x in lesson_of(idx)["origins"] if "carried" not in x]
    ok(rc == 0 and len(new) == 1 and new[0].get("memory") == "mem:p2@1" and "reopened" in new[0]["retro"],
       f"P2: a reworded heading keeps the memory id on the re-derived origin ({rc} {lesson_of(idx)['origins']})")

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
        # Round 11: x read completely and no longer holds it — carried with exactly that reason
        # (attribution by owner, never by prefix: an `x-old` problem does not make x unread).
        k2 = entries_of(idx).get(K2)
        ok(k2 is not None and [o.get("carried") for o in k2["origins"]] == ["no checkout read holds it"]
           and "removed" not in out,
           f"{tag}: x's own withdrawn entry is carried as read-and-gone, not as unread ({out!r} {k2})")

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
    """Rounds 10–11: provenance is a checkout path AND the project checked out there, and (round
    11, narrowed) a rebuild never removes or moves anything on its own. F1 a different project at
    the same path: carried, not counted; J1/J2 a project-key change: the old-key origin carried
    with its id, not counted, nothing moved; F2 a removed worktree: carried until
    --prune-carried; G1 record never puts one id on two classes nor lowers a revision; H1 an add
    racing a rebuild is kept; H2/G2 a type-malformed line is corrupt, never a traceback; G3 show
    prints no local paths; G5 merged lines keep both provenances."""
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
    e = lesson_of(idx)
    o = e["origins"]
    ok(rc == 0 and len(o) == 1 and o[0].get("carried") == "checkout holds another project"
       and e["projects"] == 0 and e["seen"] == 0,
       f"F1: a different project at the same path decides nothing; A's origin carried, not counted ({rc} {e} {out!r})")

    # J2 — the repository is re-initialised in place (new root commit), same retro, a memory id
    # recorded. Round 11: nothing moves — the old-key origin is carried with its id as
    # `checkout holds another project` and not counted; the new origin starts without an id.
    # Known limit: re-attach by recording the old id on the new origin (same class key).
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
    olds = [y for y in e["origins"] if y["project"] == old_key]
    news = [y for y in e["origins"] if y["project"] != old_key]
    ok(rc == 0 and e["projects"] == 1 and e["status"] == "local"
       and [y.get("carried") for y in olds] == ["checkout holds another project"]
       and olds[0].get("memory") == "mem:j2@1" and len(news) == 1 and "memory" not in news[0]
       and "moved" not in out,
       f"J2: a re-init carries the old key with its id, counts one project, moves nothing ({rc} {e} {out!r})")
    ok(emit_mem(idx, x, KEY) == (None, None), f"J2: emit from the new history opens a new record ({emit_mem(idx, x, KEY)})")
    rc, _, err = run("record", e["id"], "--answer", "-", cwd=x, index=idx,
                     stdin=json.dumps({"memoryId": "mem:j2", "revision": 1}))
    ok(rc == 0 and emit_mem(idx, x, KEY) == ("mem:j2", 1),
       f"J2 known limit: the operator re-attaches the old id on the new origin ({rc} {err!r})")

    # J1 — a shallow clone is never a source: a problem owned by its checkout, nothing derived
    # under its unstable key. Once deepened it is read; one project.
    src, _ = headed_repo("j1-src", [("retro.md", "export gate", KEY)])
    root = work / "j1"
    root.mkdir()
    sh = root / "app"
    git(work, "clone", "-q", "--depth", "2", f"file://{src}", str(sh))
    idx = work / "j1.jsonl"
    rc, out, _ = run("rebuild", "--roots", str(root), index=idx)
    ok(rc == 0 and "shallow" in out and KEY not in entries_of(idx) and str(sh) not in out,
       f"J1: a shallow clone is named by its name and nothing is derived from it ({rc} {out!r})")
    git(sh, "fetch", "-q", "--unshallow")
    rc, out, _ = run("rebuild", "--roots", str(root), index=idx)
    e = lesson_of(idx)
    ok(rc == 0 and e["projects"] == 1 and e["status"] == "local" and len(e["origins"]) == 1,
       f"J1: once deepened it is read; one project ({rc} {e} {out!r})")

    # F2 — a lesson born in a worktree, merged, the worktree removed, then withdrawn from main.
    # Round 11: carried (`no checkout read holds it`), counted, until --prune-carried.
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
    e = entries_of(idx).get(KEY)
    ok(rc == 0 and e is not None and all(y.get("carried") for y in e["origins"]) and "removed" not in out,
       f"F2: a withdrawn lesson is carried, never removed on its own ({rc} {out!r} {e})")
    rc, out, _ = run("rebuild", "--roots", str(root), "--prune-carried", index=idx)
    ok(rc == 0 and KEY not in entries_of(idx) and "pruned" in out,
       f"F2: --prune-carried is the way out ({rc} {out!r})")

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


def round11_controls():
    """Round 11 (loop guard, contract narrowed): a rebuild never removes or moves anything on
    its own. R1 a stranger at the same path; R2/R6 shallow clones; R3/R3b a locked or prunable
    worktree; R4 a worktree whose main path is now a stranger; R5 record over an existing id;
    #5 `mem:…@0`; #6/R7 lines missing derived fields; --prune-carried-reason."""
    work = tree("tp-lessons-r11-")

    # R1 — A records an id and moves out of the roots; an unrelated B, holding the same class at
    # the same anchor, takes A's path. A's origin keeps its id (carried, not counted); emit from
    # B opens B's own record; reading A again re-derives A's origin with its id.
    root = work / "r1"
    root.mkdir()
    a, _ = headed_repo("app", [("retro.md", "export gate", KEY)], parent=root)
    idx = work / "r1.jsonl"
    run("rebuild", "--roots", str(root), index=idx)
    record_mem(idx, a, KEY, "mem:store-record-of-a")
    proj_a = lesson_of(idx)["origins"][0]["project"]
    a.rename(work / "elsewhere-app")
    b, _ = headed_repo("b-src", [("retro.md", "export gate", KEY)], parent=work)
    b.rename(root / "app")
    b = root / "app"
    rc, out, _ = run("rebuild", "--roots", str(root), index=idx)
    e = lesson_of(idx)
    mine = [o for o in e["origins"] if o["project"] == proj_a]
    ok(rc == 0 and [o.get("carried") for o in mine] == ["checkout holds another project"]
       and mine[0].get("memory") == "mem:store-record-of-a@1" and e["projects"] == 1,
       f"R1: A's origin is carried with its id, not counted; B counts once ({rc} {e} {out!r})")
    ok(emit_mem(idx, b, KEY) == (None, None), f"R1: emit from B never revises A's record ({emit_mem(idx, b, KEY)})")
    run("rebuild", "--roots", str(root), str(work / "elsewhere-app"), "--depth", "0", index=idx)
    ok(emit_mem(idx, work / "elsewhere-app", KEY) == ("mem:store-record-of-a", 1),
       f"R1: A read again keeps its own record ({emit_mem(idx, work / 'elsewhere-app', KEY)})")

    # R2/R6 — a shallow clone whose boundary moves while it stays shallow: never a source, so
    # never a second project; add/emit/record refuse there, saying to deepen it.
    src, _ = headed_repo("r2-src", [("retro.md", "export gate", KEY)])
    for n in ("a", "b"):
        (src / f"{n}.txt").write_text(n, encoding="utf-8")
        git(src, "add", "-A")
        git(src, "commit", "-q", "-m", n)
    root = work / "r2"
    root.mkdir()
    sh = root / "app"
    git(work, "clone", "-q", "--depth", "3", f"file://{src}", str(sh))
    idx = work / "r2.jsonl"
    rc, out, _ = run("rebuild", "--roots", str(root), index=idx)
    git(sh, "fetch", "-q", "--deepen=1")
    rc2, out2, _ = run("rebuild", "--roots", str(root), index=idx)
    ok(rc == 0 and rc2 == 0 and KEY not in entries_of(idx) and "shallow" in out2,
       f"R2: a shallow clone, deepened but still shallow, is never a source ({rc} {rc2} {out2!r})")
    before = idx.read_bytes()
    lid = "L-" + hashlib.sha256(KEY.encode()).hexdigest()[:12]
    for verb in (["add", "--retro", "docs/evidence/retro.md", "--all"], ["emit-observatory", lid],
                 ["record", lid, "--answer", "-"]):
        rc, out, err = run(*verb, cwd=sh, index=idx, stdin=json.dumps({"memoryId": "mem:one", "revision": 1}))
        ok(rc == 1 and "shallow" in err and "deepen" in err and idx.read_bytes() == before,
           f"R6: {verb[0]} refuses in a shallow clone, writing nothing ({rc} {err!r})")

    # R3/R3b — a worktree (locked, or merely absent and prunable) whose directory is gone for now;
    # R4 — a worktree outside the roots whose main checkout's path now holds a stranger.
    for tag in ("r3", "r3b", "r4"):
        root = work / tag / "root"
        root.mkdir(parents=True)
        m, sha = headed_repo("app", [("retro.md", "old entry", "an-older-class")], parent=root)
        wt = work / tag / "wt-feat"
        git(m, "worktree", "add", "-q", "-b", "feat", str(wt))
        write_retros(wt, [("retro.md", "old entry", "an-older-class"), ("retro.md", "export gate", KEY)], sha)
        idx = work / tag / "i.jsonl"
        run("rebuild", "--roots", str(root), index=idx)
        ok(KEY in entries_of(idx), f"{tag} fixture: the worktree's lesson is indexed")
        if tag == "r3":
            git(m, "worktree", "lock", "--reason", "on a removable drive", str(wt))
        if tag in ("r3", "r3b"):
            wt.rename(work / tag / "unmounted")
        else:
            m.rename(work / tag / "elsewhere-app")
            stranger, _ = headed_repo("b-src", [("retro.md", "other", "an-unrelated-class")], parent=work / tag)
            stranger.rename(root / "app")
        rc, out, _ = run("rebuild", "--roots", str(root), index=idx)
        o = entries_of(idx).get(KEY, {"origins": []})["origins"]
        ok(rc == 0 and [x.get("carried") for x in o] == ["checkout not read"] and "removed" not in out,
           f"{tag}: the worktree's origin is carried as not read, never removed ({rc} {o} {out!r})")

    # R5 — record over an existing, different id needs --replace.
    root = work / "r5"
    root.mkdir()
    a, _ = headed_repo("app", [("retro.md", "export gate", KEY)], parent=root)
    idx = work / "r5.jsonl"
    run("rebuild", "--roots", str(root), index=idx)
    lid = lesson_of(idx)["id"]
    run("record", lid, "--answer", "-", cwd=a, index=idx, stdin=json.dumps({"memoryId": "mem:first", "revision": 2}))
    before = idx.read_bytes()
    rc, _, err = run("record", lid, "--answer", "-", cwd=a, index=idx,
                     stdin=json.dumps({"memoryId": "mem:second", "revision": 1}))
    ok(rc == 1 and idx.read_bytes() == before and "--replace" in err,
       f"R5: record over a different id refuses without --replace ({rc} {err!r})")
    rc, _, err = run("record", lid, "--answer", "-", "--replace", cwd=a, index=idx,
                     stdin=json.dumps({"memoryId": "mem:second", "revision": 1}))
    ok(rc == 0 and mems(idx) == {"mem:second@1": [KEY]}, f"R5: --replace replaces on purpose ({rc} {err!r} {mems(idx)})")

    # --prune-carried-reason narrows the prune to one reason.
    root = work / "pr"
    root.mkdir()
    x, sha = headed_repo("app", [("retro.md", "one", KEY), ("retro.md", "two", K2)], parent=root)
    idx = work / "pr.jsonl"
    run("rebuild", "--roots", str(root), index=idx)
    write_retros(x, [("retro.md", "one", KEY)], sha)
    other = work / "pr-other"
    other.mkdir()
    rc, out, _ = run("rebuild", "--roots", str(other), "--prune-carried", "--prune-carried-reason",
                     "no checkout read holds it", index=idx)
    ok(rc == 0 and KEY in entries_of(idx) and K2 in entries_of(idx),
       f"--prune-carried-reason prunes only that reason ({rc} {out!r} {sorted(entries_of(idx))})")
    rc, out, _ = run("rebuild", "--roots", str(root), "--prune-carried", "--prune-carried-reason",
                     "no checkout read holds it", index=idx)
    ok(rc == 0 and KEY in entries_of(idx) and K2 not in entries_of(idx) and "pruned" in out,
       f"--prune-carried-reason removes exactly the origins carried for that reason ({rc} {out!r})")

    # #5/#6/R7 — lines that pass the shape check but used to crash a verb.
    d, _ = headed_repo("r7", [("retro.md", "export gate", KEY)])
    base_idx = work / "r7-base.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=d, index=base_idx)
    base = json.loads(base_idx.read_text(encoding="utf-8"))
    muts = {
        "no status": lambda e: e.pop("status"),
        "no stages/grade": lambda e: (e.pop("stages"), e.pop("grade")),
        "id of another class": lambda e: e.__setitem__("id", "L-000000000000"),
        "carried not in the enum": lambda e: e["origins"][0].__setitem__("carried", "whatever"),
        "memory @0": lambda e: e["origins"][0].__setitem__("memory", "mem:z@0"),
        "duplicate origin": lambda e: e["origins"].append(dict(e["origins"][0])),
        "status lies": lambda e: (e.__setitem__("status", "candidate"), e.__setitem__("projects", 7)),
    }
    for name, mut in muts.items():
        bad = json.loads(json.dumps(base))
        mut(bad)
        for verb in (["query", "gate"], ["candidates", "--min-projects", "1"], ["show", base["id"]],
                     ["emit-observatory", base["id"]], ["add", "--retro", "docs/evidence/retro.md", "--all"],
                     ["rebuild", "--roots", str(d), "--depth", "0"]):
            h = work / f"r7-{len(name)}-{verb[0]}.jsonl"
            h.write_text(json.dumps(bad) + "\n", encoding="utf-8")
            rc, out, err = run(*verb, cwd=d, index=h)
            ok("Traceback" not in err, f"R7 {name}: {verb[0]} never crashes ({rc} {err[-200:]!r})")
            if name == "status lies" and verb[0] == "query":
                ok("projects 1" in out and "candidate" not in out,
                   f"#6: derived fields are recomputed at load, never trusted from disk ({out!r})")
            if name == "duplicate origin" and verb[0] == "query":
                ok("seen 1" in out, f"R7: a duplicated origin is one origin ({out!r})")


def round12_controls():
    """Round 12 (adversarial): A/F a project key is the repository's, not the checked-out
    branch's; C/H record never puts an id on another project's origin nor one the loader would
    refuse; B a line separator never corrupts the index; E rebuild prints no absolute path; and
    the LOW items: load-side rejection of `mem:…@0` and an unknown `carried`, the prune-reason
    usage, duplicate lines naming the dropped id, add after a re-init, a shallow check that
    times out."""
    work = tree("tp-lessons-r12-")

    def main_branch(repo):
        return git(repo, "rev-parse", "--abbrev-ref", "HEAD")

    # A — one repository, two worktrees; the feature branch merged an unrelated history (a
    # subtree-style --allow-unrelated-histories merge). One project, read once per repository.
    root = work / "a"
    repo, _ = headed_repo("repo", [("retro.md", "export gate", KEY)], parent=root)
    other = tree("tp-lessons-r12-other-")
    git(other, "init", "-q")
    (other / "o.txt").write_text("o", encoding="utf-8")
    git(other, "add", "-A")
    git(other, "commit", "-q", "-m", "an unrelated root")
    base = main_branch(repo)
    git(repo, "checkout", "-q", "-b", "feature")
    git(repo, "fetch", "-q", str(other), "HEAD:otherhist")
    git(repo, "merge", "-q", "--allow-unrelated-histories", "-m", "subtree", "otherhist")
    git(repo, "checkout", "-q", base)
    git(repo, "worktree", "add", "-q", str(repo / ".worktrees" / "feat"), "feature")
    idx = work / "a.jsonl"
    rc, out, _ = run("rebuild", "--roots", str(root), index=idx)
    e = entries_of(idx).get(KEY, {"origins": [], "projects": None})
    ok(rc == 0 and e["projects"] == 1 and len({o["project"] for o in e["origins"]}) == 1,
       f"A: worktrees of one repository are one project whatever branch they hold ({rc} {e} {out!r})")

    # F — a checkout temporarily on an orphan gh-pages branch is still its project; with its
    # default branch gone its key changes, but the origin's commit still resolves there, so it
    # is never `checkout holds another project`. Two projects stay a candidate.
    for variant in ("pages", "pages-no-main"):
        root = work / f"f-{variant}"
        r1, _ = headed_repo("r1", [("retro.md", "export gate", KEY)], parent=root)
        r2, _ = headed_repo("r2-" + variant, [("retro.md", "gate export", KEY)], parent=root)
        idx = work / f"f-{variant}.jsonl"
        run("rebuild", "--roots", str(root), index=idx)
        ok(lesson_of(idx)["projects"] == 2, f"F fixture {variant}: two projects")
        base = main_branch(r2)
        git(r2, "checkout", "-q", "--orphan", "gh-pages")
        git(r2, "rm", "-rqf", ".")
        (r2 / "index.html").write_text("x", encoding="utf-8")
        git(r2, "add", "-A")
        git(r2, "commit", "-q", "-m", "pages")
        if variant == "pages-no-main":
            git(r2, "branch", "-q", "-D", base)
        rc, out, _ = run("rebuild", "--roots", str(root), index=idx)
        e = lesson_of(idx)
        reasons = sorted(o.get("carried") or "derived" for o in e["origins"])
        ok(rc == 0 and e["projects"] == 2 and e["status"] == "candidate"
           and "checkout holds another project" not in reasons,
           f"F {variant}: a checkout on another branch is not a stranger ({rc} {reasons} {e['projects']} {out!r})")
        if variant == "pages":
            # The project key is the default branch's root, not HEAD's: on gh-pages, r2 is still
            # its project, so emit finds its origin (a HEAD-rooted key would refuse here).
            rc, out, err = run("emit-observatory", e["id"], cwd=r2, index=idx)
            ok(rc == 0 and '"tool"' in out, f"F: emit from a checkout on an orphan branch finds its origin ({rc} {err!r})")

    # C — record an id another PROJECT's origin of the same class holds: refused, named.
    root = work / "c"
    r1, _ = headed_repo("r1", [("retro.md", "export gate", KEY)], parent=root)
    r2, _ = headed_repo("r2-c", [("retro.md", "gate export", KEY)], parent=root)
    idx = work / "c.jsonl"
    for r in (r1, r2):
        run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=r, index=idx)
    lid = lesson_of(idx)["id"]
    ok(record_mem(idx, r2, KEY, "mem:abc") == 0, "C fixture: r2 records mem:abc")
    p2 = next(o["project"] for o in lesson_of(idx)["origins"] if o.get("memory"))
    before = idx.read_bytes()
    rc, _, err = run("record", lid, "--answer", "-", cwd=r1, index=idx,
                     stdin=json.dumps({"memoryId": "mem:abc", "revision": 2}))
    ok(rc == 1 and idx.read_bytes() == before and p2 in err,
       f"C: record refuses an id another project's origin holds, naming it ({rc} {err!r})")

    # H — ids the loader would refuse are refused by record (exit 2), and nothing is lost.
    for n, bad in enumerate(("mem:", 'mem:a"b', "mem:a\\b")):
        before = idx.read_bytes()
        rc, _, err = run("record", lid, "--answer", "-", cwd=r1, index=idx,
                         stdin=json.dumps({"memoryId": bad, "revision": 1}))
        rcq, _, errq = run("query", "gate", index=idx)
        ok(rc == 2 and idx.read_bytes() == before and rcq == 0 and "could not be parsed" not in errq
           and any(o.get("memory") == "mem:abc@1" for o in lesson_of(idx)["origins"]),
           f"H: record refuses {bad!r} with exit 2; the other project's id survives ({rc} {err!r} {errq!r})")

    # B — a line separator in a title is refused by lesson/1; a separator in a field lesson/1
    # does not check (a checkout path) never makes the index corrupt.
    root = work / "b"
    x, sha = headed_repo("x", [("retro.md", "export gate", KEY)], parent=root)
    idx = work / "b.jsonl"
    for sep in (" ", " ", "\x85"):
        lesson = {"classKey": "ls-sep", "title": f"a title with a{sep}separator in it",
                  "trigger": "when it fires", "check": "the check runs", "grade": 1,
                  "stages": {"owned": 4, "surfaced": 6}, "nouns": ["gate", "artefact", "absence"],
                  "origin": {"commit": sha, "retro": "docs/evidence/retro.md#x"}}
        rc, _, err = run("add", "--json", "-", cwd=x, index=idx, stdin=json.dumps(lesson))
        ok(rc == 1 and not idx.exists() and "line break" in err,
           f"B: a title carrying {sep!r} is refused, nothing written ({rc} {err!r})")
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=x, index=idx)
    line = json.loads(idx.read_text(encoding="utf-8"))
    line["origins"][0]["checkouts"] = [line["origins"][0]["checkouts"][0] + " odd"]
    idx.write_text(json.dumps(line, ensure_ascii=False) + "\n", encoding="utf-8")
    for _ in range(3):
        rc, out, err = run("query", "gate", index=idx)
        ok(rc == 0 and "could not be parsed" not in err, f"B: a separator inside a value is not a line ({err!r})")
    ok(not list(work.glob("b.jsonl.corrupt-*")), "B: three reads leave no .corrupt file")

    # E — three failing checkouts under one scratch root: no absolute path in any message.
    root = work / "e"
    repo, _ = headed_repo("repo", [("retro.md", "export gate", KEY)], parent=root)
    (repo / "docs/evidence/retro").write_text("not a dir", encoding="utf-8")
    repo2, _ = headed_repo("repo2", [("retro.md", "export gate", KEY)], parent=root)
    (repo2 / "pipeline.json").write_text('{"paths": {"artifacts": "nope"}}', encoding="utf-8")
    repo3, _ = headed_repo("repo3", [("retro.md", "export gate", KEY)], parent=root)
    (repo3 / "docs/evidence/retro.md").chmod(0)
    try:
        rc, out, err = run("rebuild", "--roots", str(root), str(work / "e-missing"), index=work / "e.jsonl")
    finally:
        (repo3 / "docs/evidence/retro.md").chmod(0o644)
    ok(out.count("not read") >= 4 and str(work) not in out + err and str(work.resolve()) not in out + err,
       f"E: rebuild names checkouts and files, never an absolute path ({rc} {out!r} {err!r})")

    # LOW — the loader rejects `mem:…@0` and an unknown `carried` (each line set aside).
    d, _ = headed_repo("low12", [("retro.md", "export gate", KEY)])
    base_idx = work / "low-base.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=d, index=base_idx)
    for name, field, value in (("mem0", "memory", "mem:x@0"), ("carried", "carried", "whatever")):
        bad = json.loads(base_idx.read_text(encoding="utf-8"))
        bad["origins"][0][field] = value
        h = work / f"low-{name}.jsonl"
        h.write_text(json.dumps(bad) + "\n", encoding="utf-8")
        rc, _, err = run("query", "gate", index=h)
        ok(rc == 0 and "could not be parsed" in err and list(work.glob(f"low-{name}.jsonl.corrupt-*")),
           f"LOW: a line with {field}={value!r} is rejected by the loader ({rc} {err!r})")

    # LOW — --prune-carried-reason: needs --prune-carried; only reasons that can occur.
    empty = work / "empty-root"
    empty.mkdir()
    for args, what in ((["--prune-carried-reason", "no checkout read holds it"], "without --prune-carried"),
                       (["--prune-carried", "--prune-carried-reason", "bogus"], "an unknown reason"),
                       (["--prune-carried", "--prune-carried-reason", "source not read"], "a reason that cannot occur")):
        rc, _, err = run("rebuild", "--roots", str(empty), *args, index=base_idx)
        ok(rc == 2, f"LOW: --prune-carried-reason {what} is a usage error ({rc} {err[-160:]!r})")

    # LOW — two lines for one class with different ids for the same origin: the higher revision
    # is kept and the dropped id is named (probe3).
    lesson_body = {"classKey": "dup-ids", "title": "a title long enough", "trigger": "when it fires",
                   "check": "the check runs", "grade": 1, "stages": {"owned": 4, "surfaced": 6},
                   "nouns": ["gate", "artefact", "absence"]}

    def dup_line(mem):
        o = {"project": "p-0123456789ab", "commit": "0123456", "retro": "docs/evidence/retro.md#x",
             "lesson": lesson_body, "memory": mem}
        return json.dumps({"schema": "lesson-index/1", "id": "L-000000000000", "classKey": "dup-ids",
                           "title": lesson_body["title"], "trigger": lesson_body["trigger"],
                           "check": lesson_body["check"], "grade": 1, "stages": lesson_body["stages"],
                           "nouns": lesson_body["nouns"], "seen": 1, "projects": 1, "status": "local",
                           "origins": [o]})
    dup = work / "dup.jsonl"
    dup.write_text(dup_line("mem:aaa@1") + "\n" + dup_line("mem:bbb@2") + "\n", encoding="utf-8")
    rc, out, err = run("rebuild", "--roots", str(empty), index=dup)
    mem_now = [o.get("memory") for o in entries_of(dup)["dup-ids"]["origins"]]
    ok(rc == 0 and mem_now == ["mem:bbb@2"] and "dropped mem:aaa@1" in out + err and "none dropped" not in out + err,
       f"LOW: merged duplicate lines keep the higher revision and name the dropped id ({mem_now} {out!r} {err!r})")

    # LOW — add after a re-init at the same path: the old-key origin is `checkout holds another
    # project` at once, so add never counts a phantom project (repro G).
    root = work / "g"
    g, _ = headed_repo("repo", [("retro.md", "export gate", KEY)], parent=root)
    idx = work / "g.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=g, index=idx)
    shutil.rmtree(g / ".git")
    git(g, "init", "-q")
    (g / "NEW").write_text("reinit", encoding="utf-8")
    git(g, "add", "-A")
    git(g, "commit", "-q", "-m", "reinit")
    write_retros(g, [("retro.md", "export gate", KEY)], git(g, "rev-parse", "HEAD"))
    rc, out, _ = run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=g, index=idx)
    e = lesson_of(idx)
    ok(rc == 0 and e["projects"] == 1 and e["status"] == "local"
       and sorted(o.get("carried") or "derived" for o in e["origins"]) == ["checkout holds another project", "derived"],
       f"LOW: add after a re-init counts one project ({rc} {e} {out!r})")

    # LOW — a shallow check that does not answer counts as refused: not a source, named.
    root = work / "sh-timeout"
    s, _ = headed_repo("repo", [("retro.md", "export gate", KEY)], parent=root)
    binp = work / "slow-shallow-bin"
    binp.mkdir()
    (binp / "git").write_text(
        # `exec sleep`: the timeout kills the sleeper itself, leaving no orphan in the group.
        "#!/bin/sh\nfor a in \"$@\"; do if [ \"$a\" = --is-shallow-repository ]; then exec sleep 3; fi; done\n"
        f"exec {shutil.which('git')} \"$@\"\n", encoding="utf-8")
    (binp / "git").chmod(0o755)
    idx = work / "sh.jsonl"
    rc, out, _ = run("rebuild", "--roots", str(root), index=idx,
                     env_extra={"PATH": f"{binp}:{os.environ['PATH']}", "TASK_PIPELINE_GIT_TIMEOUT": "1"})
    ok(KEY not in entries_of(idx) if idx.exists() else True, "LOW: an unanswered shallow check derives nothing")
    # Nothing was learned from that checkout, so nothing was read: exit 1, nothing written.
    ok(rc == 1 and "shallow" in out and "did not answer" in out and not idx.exists(),
       f"LOW: an unanswered shallow check is a problem owned by the checkout ({rc} {out!r})")


def round13_controls():
    """Round 13 (adversarial): K an index written by v1.95.0 (smallest-root key, no provenance)
    is re-keyed to its repository, never a second project, its memory id kept; M/M2 one memory
    id is one project's record — record's re-attach exception holds only at the same checkout,
    and a rebuild never leaves one id on two live projects; and the LOW items: L a repository
    with no origin/HEAD, main or master keys on its main worktree's HEAD, then
    init.defaultBranch; N2 redaction replaces whole path components only; O stderr names no
    absolute path; P string stage ids get the text checks; Q a same-revision tie is
    deterministic."""
    work = tree("tp-lessons-r13-")

    # K — a repository that merged an unrelated history whose root sorts LOWER than its own:
    # v1.95.0 keyed it on that smaller root; the key now is the default branch's first-parent root.
    def merged_repo(root, name):
        for attempt in range(40):
            repo, sha = headed_repo(name, [("retro.md", "export gate", KEY)], parent=root / str(attempt))
            other = tree("tp-lessons-r13-other-")
            git(other, "init", "-q")
            (other / "o.txt").write_text(f"o{attempt}", encoding="utf-8")
            git(other, "add", "-A")
            git(other, "commit", "-q", "-m", f"an unrelated root {attempt}")
            own = git(repo, "rev-list", "--max-parents=0", "HEAD")
            theirs = git(other, "rev-parse", "HEAD")
            if theirs < own:
                git(repo, "fetch", "-q", str(other), "HEAD:otherhist")
                git(repo, "merge", "-q", "--allow-unrelated-histories", "-m", "subtree", "otherhist")
                return repo, sha, "p-" + own[:12], "p-" + theirs[:12]
            shutil.rmtree(root / str(attempt))
        raise SystemExit("K fixture: no unrelated root sorted lower in 40 tries")

    def as_v195(idx, old_key, memory, commit=None):
        """Rewrite the index's one line as v1.95.0 wrote it: the smallest-root key, no
        `checkouts`, a recorded memory id."""
        line = json.loads(idx.read_text(encoding="utf-8").splitlines()[0])
        o = line["origins"][0]
        o.pop("checkouts", None)
        o.pop("carried", None)
        o["project"] = old_key
        o["memory"] = memory
        if commit:
            o["commit"] = commit
        idx.write_text(json.dumps(line, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    root = work / "k"
    repo, sha, new_key, old_key = merged_repo(root, "repo")
    idx = work / "k.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=repo, index=idx)
    ok({o["project"] for o in lesson_of(idx)["origins"]} == {new_key}, "K fixture: the key is the default branch's root")
    as_v195(idx, old_key, "mem:v195@1")
    rc, out, err = run("rebuild", "--roots", str(root), index=idx)
    e = lesson_of(idx)
    ok(rc == 0 and e["projects"] == 1 and e["status"] == "local" and len(e["origins"]) == 1
       and e["origins"][0]["project"] == new_key and e["origins"][0].get("memory") == "mem:v195@1"
       and not e["origins"][0].get("carried") and "re-keyed" in out,
       f"K: a v1.95.0 origin of the same repository is re-keyed, its id kept, one project ({rc} {e} {out!r} {err!r})")
    rc, out, err = run("emit-observatory", e["id"], cwd=repo, index=idx)
    args = json.loads(out)["arguments"] if rc == 0 else {}
    ok(args.get("memoryId") == "mem:v195" and args.get("expectedRevision") == 1,
       f"K: emit carries the re-keyed memory id ({rc} {out!r} {err!r})")
    rc, _, err = run("record", e["id"], "--answer", "-", cwd=repo, index=idx,
                     stdin=json.dumps({"memoryId": "mem:v195", "revision": 2}))
    ok(rc == 0 and lesson_of(idx)["origins"][0].get("memory") == "mem:v195@2",
       f"K: record of the old id is accepted after the upgrade ({rc} {err!r})")

    # K, add — the same upgrade without a rebuild: add re-keys it at once.
    idx = work / "k-add.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=repo, index=idx)
    as_v195(idx, old_key, "mem:v195@1")
    rc, out, err = run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=repo, index=idx)
    e = lesson_of(idx)
    ok(rc == 0 and e["projects"] == 1 and len(e["origins"]) == 1
       and e["origins"][0]["project"] == new_key and e["origins"][0].get("memory") == "mem:v195@1"
       and "re-keyed" in out,
       f"K: add re-keys a v1.95.0 origin of this repository and keeps its id ({rc} {e} {out!r} {err!r})")

    # K, control — a provenance-less origin whose commit does NOT resolve in the checkout is no
    # evidence of one repository: it stays carried, and its id stays with it.
    idx = work / "k-ctl.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=repo, index=idx)
    as_v195(idx, old_key, "mem:v195@1", commit="0" * 40)
    rc, out, _ = run("rebuild", "--roots", str(root), index=idx)
    e = lesson_of(idx)
    legacy = [o for o in e["origins"] if o["project"] == old_key]
    ok(rc == 0 and len(legacy) == 1 and legacy[0].get("carried") == "no provenance"
       and legacy[0].get("memory") == "mem:v195@1" and "re-keyed" not in out,
       f"K: without its commit in the checkout an old-key origin is not re-keyed ({rc} {e} {out!r})")

    def append_legacy(idx, project, memory, commit=None):
        """Add, beside the line's first origin, a v1.95.0-style origin: no checkouts."""
        line = json.loads(idx.read_text(encoding="utf-8").splitlines()[0])
        o = {k: v for k, v in line["origins"][0].items() if k not in ("checkouts", "carried", "memory")}
        o.update(project=project, memory=memory, **({"commit": commit} if commit else {}))
        line["origins"].append(o)
        idx.write_text(json.dumps(line, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    # K, refusals of the re-key — each one a move the contract forbids.
    # (d) the old copy under the new key holds ANOTHER memory id: two records stay two, named.
    for verb in ("rebuild", "add"):
        idx = work / f"k-two-{verb}.jsonl"
        run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=repo, index=idx)
        ok(record_mem(idx, repo, KEY, "mem:b") == 0, f"K {verb} fixture: mem:b recorded")
        append_legacy(idx, old_key, "mem:a@1")
        if verb == "rebuild":
            rc, out, err = run("rebuild", "--roots", str(root), index=idx)
        else:
            rc, out, err = run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=repo, index=idx)
        ok(rc == 0 and sorted(mems(idx)) == ["mem:a@1", "mem:b@1"]
           and (verb == "add" or "left carried" in out),
           f"K {verb}: an old-key origin holding another id is not merged into the new one ({rc} {mems(idx)} {out!r} {err!r})")

    # A monorepo B that merged A's history under its own root: A's commit resolves in B.
    kc = work / "kc"
    a_repo, a_sha = headed_repo("a", [("retro.md", "export gate", KEY)], parent=kc / "ra")
    b_repo = kc / "rb" / "b"
    b_repo.mkdir(parents=True)
    git(b_repo, "init", "-q")
    (b_repo / "B.md").write_text("the monorepo", encoding="utf-8")
    git(b_repo, "add", "-A")
    git(b_repo, "commit", "-q", "-m", "monorepo root")
    git(b_repo, "fetch", "-q", str(a_repo), "HEAD:ahist")
    git(b_repo, "merge", "-q", "--allow-unrelated-histories", "-m", "mono", "ahist")

    def ab_index(name):
        idx = work / f"{name}.jsonl"
        for r in (a_repo, b_repo):
            run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=r, index=idx)
        return idx
    # (a) an origin WITH provenance is never re-keyed: A not read stays A's, carried.
    idx = ab_index("kc-a")
    ka = next(o["project"] for o in lesson_of(idx)["origins"] if str(a_repo.resolve()) in (o.get("checkouts") or []))
    rc, out, _ = run("rebuild", "--roots", str(kc / "rb"), index=idx)
    e = lesson_of(idx)
    a_now = [o for o in e["origins"] if o["project"] == ka]
    ok(rc == 0 and e["projects"] == 2 and len(a_now) == 1 and a_now[0].get("carried") == "checkout not read"
       and "re-keyed" not in out,
       f"K: an origin with provenance is carried, never re-keyed into another project ({rc} {e} {out!r})")
    # (b) a provenance-less origin whose OWN key this run re-derives stays that project's.
    idx = ab_index("kc-b")
    line = json.loads(idx.read_text(encoding="utf-8").splitlines()[0])
    for o in line["origins"]:
        if o["project"] == ka:
            o.pop("checkouts", None)
            o["memory"] = "mem:ka@1"
    idx.write_text(json.dumps(line, sort_keys=True) + "\n", encoding="utf-8")
    rc, out, _ = run("rebuild", "--roots", str(kc), index=idx)
    e = lesson_of(idx)
    ok(rc == 0 and e["projects"] == 2 and "re-keyed" not in out
       and [o["project"] for o in e["origins"] if o.get("memory")] == [ka],
       f"K: an old origin whose own key is re-derived keeps its id there ({rc} {e} {out!r})")
    # (c) two candidates hold its commit: no evidence which one it is — not re-keyed.
    idx = ab_index("kc-c")
    append_legacy(idx, "p-000000000000", "mem:z@1", commit=a_sha)
    rc, out, _ = run("rebuild", "--roots", str(kc), index=idx)
    e = lesson_of(idx)
    z = [o for o in e["origins"] if o["project"] == "p-000000000000"]
    ok(rc == 0 and len(z) == 1 and z[0].get("carried") == "no provenance" and z[0].get("memory") == "mem:z@1"
       and "re-keyed" not in out,
       f"K: an old origin two projects could be is not re-keyed ({rc} {e} {out!r})")

    def move(src, dst):
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

    # M — P1 records mem:x; a stranger takes P1's path; an unrelated P3 elsewhere records
    # mem:x: refused, P1's id is not P3's to take.
    root = work / "m"
    p1, _ = high_root_repo("p1", [("retro.md", "export gate", KEY)], parent=root / "here")
    p3, _ = headed_repo("p3", [("retro.md", "gate export", KEY)], parent=root / "p3home")
    idx = work / "m.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=p1, index=idx)
    ok(record_mem(idx, p1, KEY, "mem:x") == 0, "M fixture: P1 records mem:x")
    k1 = lesson_of(idx)["origins"][0]["project"]
    move(p1, root / "away" / "p1")
    # The stranger: its own content, so its commits never coincide with P1's within one second,
    # and a root that sorts BELOW P1's (round 14, L1): "the smaller key" would then pick the
    # stranger, so only the earlier-holder rule keeps the id on P1 — every run, not 3 in 4.
    for attempt in range(60):
        # Its own content per attempt (round 16): an identical commit in the same second is the
        # same root, and no retry would ever change the order.
        s0, _ = headed_repo(f"stranger-{attempt}", [("retro.md", "export gate", KEY)], parent=root / "tmp" / str(attempt))
        if "p-" + git(s0, "rev-list", "--max-parents=0", "HEAD")[:12] < k1:
            break
    else:
        raise SystemExit("M fixture: no stranger root sorted below P1's in 60 tries")
    move(s0, root / "here" / "p1")
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=p3, index=idx)
    run("rebuild", "--roots", str(root / "here"), str(root / "p3home"), index=idx)
    before = idx.read_bytes()
    rc, _, err = run("record", lesson_of(idx)["id"], "--answer", "-", cwd=p3, index=idx,
                     stdin=json.dumps({"memoryId": "mem:x", "revision": 2}))
    ok(rc == 1 and idx.read_bytes() == before and k1 in err,
       f"M: a project at another checkout never takes an id a carried origin holds ({rc} {err!r})")

    # M, rebuild — the stranger at P1's path records mem:x (allowed: the same checkout), then P1
    # reappears elsewhere: two live projects would hold one id. It stays on P1, which held it
    # first; the stranger's origin keeps its place without it, and that is named.
    stranger = root / "here" / "p1"
    rc = run("record", lesson_of(idx)["id"], "--answer", "-", cwd=stranger, index=idx,
             stdin=json.dumps({"memoryId": "mem:x", "revision": 2}))[0]
    ok(rc == 0, f"M fixture: the re-attach at the same checkout is allowed ({rc})")
    ks = git(stranger, "rev-list", "--max-parents=0", "HEAD")[:12]
    rc, out, err = run("rebuild", "--roots", str(root), index=idx)
    holders = sorted(o["project"] for o in lesson_of(idx)["origins"] if o.get("memory"))
    ok(rc == 0 and holders == [k1] and "mem:x is held by" in out and "p-" + ks in out,
       f"M: one id never stays on two live projects; the earlier holder keeps it ({rc} {holders} {out!r} {err!r})")
    rc, _, err = run("record", lesson_of(idx)["id"], "--answer", "-", cwd=root / "away" / "p1", index=idx,
                     stdin=json.dumps({"memoryId": "mem:x", "revision": 3}))
    ok(rc == 0, f"M: P1's own record of its id is accepted ({rc} {err!r})")

    # M2 — the documented re-attach after a re-init at the same path, then an old clone of the
    # pre-re-init history under the roots: the id stays on the project that held it first.
    root = work / "m2"
    r, _ = high_root_repo("repo", [("retro.md", "export gate", KEY)], parent=root / "roots")
    idx = work / "m2.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=r, index=idx)
    ok(record_mem(idx, r, KEY, "mem:y") == 0, "M2 fixture: the project records mem:y")
    k_old = lesson_of(idx)["origins"][0]["project"]
    git(root, "clone", "-q", str(r), str(root / "attic" / "old"))
    # The re-initialised root sorts BELOW the old one (round 14, L1), so "the smaller key" would
    # pick the later holder: only the earlier-holder rule passes, every run.
    for attempt in range(60):
        shutil.rmtree(r / ".git")
        git(r, "init", "-q")
        (r / "NEW").write_text(f"reinit {attempt}", encoding="utf-8")
        git(r, "add", "-A")
        git(r, "commit", "-q", "-m", f"reinit {attempt}")
        if "p-" + git(r, "rev-parse", "HEAD")[:12] < k_old:
            break
    else:
        raise SystemExit("M2 fixture: no re-init root sorted below the old one in 60 tries")
    write_retros(r, [("retro.md", "export gate", KEY)], git(r, "rev-parse", "HEAD"))
    git(r, "add", "-A")
    git(r, "commit", "-q", "-m", "retro")
    run("rebuild", "--roots", str(root / "roots"), index=idx)
    rc, _, err = run("record", lesson_of(idx)["id"], "--answer", "-", cwd=r, index=idx,
                     stdin=json.dumps({"memoryId": "mem:y", "revision": 2}))
    ok(rc == 0, f"M2: the documented re-attach at the same path is accepted ({rc} {err!r})")
    k_new = next(o["project"] for o in lesson_of(idx)["origins"] if not o.get("carried"))
    move(root / "attic" / "old", root / "roots" / "old")
    rc, out, err = run("rebuild", "--roots", str(root / "roots"), index=idx)
    e = lesson_of(idx)
    holders = sorted(o["project"] for o in e["origins"] if o.get("memory"))
    ok(rc == 0 and holders == [k_old] and k_new in out and "mem:y is held by" in out,
       f"M2: after an old clone returns, one id is on one live project, the earlier ({rc} {holders} {out!r} {err!r})")
    rc, out, _ = run("rebuild", "--roots", str(root / "roots"), index=idx)
    ok(rc == 0 and "mem:y is held by" not in out
       and sorted(o["project"] for o in lesson_of(idx)["origins"] if o.get("memory")) == [k_old],
       f"M2: the next rebuild is stable ({out!r})")

    # L — default branch `trunk`, no remote, a linked worktree on an orphan `pages` that carries
    # the same retro entry: one project (the main worktree's HEAD), one origin read twice.
    root = work / "l"
    lr = root / "repo"
    lr.mkdir(parents=True)
    git(lr, "init", "-q", "-b", "trunk")
    (lr / "README.md").write_text("l", encoding="utf-8")
    git(lr, "add", "-A")
    git(lr, "commit", "-q", "-m", "root")
    sha = git(lr, "rev-parse", "HEAD")
    write_retros(lr, [("retro.md", "export gate", KEY)], sha)
    git(lr, "add", "-A")
    git(lr, "commit", "-q", "-m", "retro")
    pages = root / "pages-wt"
    git(lr, "worktree", "add", "-q", "--detach", str(pages))
    git(pages, "checkout", "-q", "--orphan", "pages")
    git(pages, "rm", "-rqf", ".")
    (pages / "index.html").write_text("p", encoding="utf-8")
    git(pages, "add", "-A")
    git(pages, "commit", "-q", "-m", "pages")
    write_retros(pages, [("retro.md", "export gate", KEY)], sha)
    git(pages, "add", "-A")
    git(pages, "commit", "-q", "-m", "pages retro")
    # Each `add` is its own process: the per-common-dir cache cannot hide a key that follows
    # the branch a worktree holds.
    def add_both(idx):
        return [run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=c, index=idx)
                for c in (lr, pages)]
    got = add_both(work / "l.jsonl")
    e = lesson_of(work / "l.jsonl")
    ok(all(g[0] == 0 for g in got) and e["projects"] == 1 and len(e["origins"]) == 1
       and len(e["origins"][0].get("checkouts") or []) == 2,
       f"L: without origin/HEAD, main or master, every worktree keys on the main worktree's HEAD ({got} {e})")
    # …and with that HEAD unborn, init.defaultBranch decides.
    git(lr, "config", "init.defaultBranch", "trunk")
    git(lr, "checkout", "-q", "--orphan", "unborn")
    got = add_both(work / "l2.jsonl")
    e = lesson_of(work / "l2.jsonl") if (work / "l2.jsonl").exists() else {}
    ok(all(g[0] == 0 for g in got) and e.get("projects") == 1 and len(e.get("origins", [])) == 1
       and len(e["origins"][0].get("checkouts") or []) == 2,
       f"L: with the main worktree's HEAD unborn, init.defaultBranch keys the repository ({got} {e})")

    # N2 — `--roots .`: names with dots survive (`repo.v2`, `docs/x.y`, `mem:v1.2.3`).
    root = work / "n2"
    headed_repo("good", [("retro.md", "export gate", KEY)], parent=root)
    bad, _ = headed_repo("repo.v2", [("retro.md", "export gate", KEY)], parent=root)
    (bad / "pipeline.json").write_text('{"paths": {"artifacts": "docs/x.y"}}', encoding="utf-8")
    body = {"classKey": "dot-ids", "title": "a title long enough", "trigger": "when it fires",
            "check": "the check runs", "grade": 1, "stages": {"owned": 4, "surfaced": 6},
            "nouns": ["gate", "artefact", "absence"]}

    def line(mem):
        o = {"project": "p-0123456789ab", "commit": "0123456", "retro": "docs/evidence/retro.md#x",
             "lesson": body, "memory": mem}
        return json.dumps({"schema": "lesson-index/1", "id": "L-000000000000", "classKey": "dot-ids",
                           "title": body["title"], "trigger": body["trigger"], "check": body["check"],
                           "grade": 1, "stages": body["stages"], "nouns": body["nouns"], "seen": 1,
                           "projects": 1, "status": "local", "origins": [o]})
    idx = work / "n2.jsonl"
    idx.write_text(line("mem:v1.2.3@1") + "\n" + line("mem:w4.5@2") + "\n", encoding="utf-8")
    rc, out, err = run("rebuild", "--roots", ".", cwd=root, index=idx)
    ok(rc == 0 and "repo.v2" in out and "docs/x.y" in out and "mem:v1.2.3@1" in out + err
       and str(work) not in out + err and str(work.resolve()) not in out + err,
       f"N2: a root given as . deletes no dot ({rc} {out!r} {err!r})")
    unit = subprocess.run([sys.executable, "-B", "-c",
                           "import sys; sys.path.insert(0, sys.argv[1]); import lessons; "
                           "print(lessons._redact(sys.argv[2], {'/a/b/repo': 'repo', '.': '', 'docs': 'D'}))",
                           str(SCRIPT.parent), "/a/b/repo.v2 /a/b/repo/x.y /a/b/repo: c/a/b/repo ./run docs/x"],
                          capture_output=True, text=True, timeout=60)
    ok(unit.stdout.strip() == "/a/b/repo.v2 repo/x.y repo: c/a/b/repo ./run docs/x",
       f"N2: only whole path components are replaced ({unit.stdout!r} {unit.stderr[-200:]!r})")

    # O — the newer-format notice, the corrupt set-aside notice and a refusal go to stderr
    # without the index's absolute path.
    root = work / "o"
    headed_repo("good", [("retro.md", "export gate", KEY)], parent=root)
    for name, extra in (("newer", '{"schema": "lesson-index/9"}'), ("corrupt", "{not json")):
        idx = work / "o-dir" / f"{name}.jsonl"
        idx.parent.mkdir(exist_ok=True)
        idx.write_text(line("mem:o@1") + "\n" + extra + "\n", encoding="utf-8")
        rc, out, err = run("rebuild", "--roots", str(root), index=idx)
        ok(rc == 0 and f"{name}.jsonl" in err and str(work) not in out + err
           and str(work.resolve()) not in out + err,
           f"O: the {name} index notice names the file, never its absolute path ({rc} {err!r})")

    # P — a string stage id gets the text checks: one line, a short id, no path.
    x, sha = headed_repo("p", [("retro.md", "export gate", KEY)], parent=work / "p")
    idx = work / "p.jsonl"
    for bad_stage, why in (("4\u2028x", "line break"), ("4\nx", "line break"),
                           ("/home/someone/plan", "absolute path"), ("s" * 40, "characters")):
        lesson = {"classKey": "stage-text", "title": "a title long enough", "trigger": "when it fires",
                  "check": "the check runs", "grade": 1, "stages": {"owned": bad_stage, "surfaced": 6},
                  "nouns": ["gate", "artefact", "absence"],
                  "origin": {"commit": sha, "retro": "docs/evidence/retro.md#x"}}
        rc, _, err = run("add", "--json", "-", cwd=x, index=idx, stdin=json.dumps(lesson))
        ok(rc == 1 and not idx.exists() and "stages.owned" in err and why in err,
           f"P: a stage id {bad_stage[:12]!r} is refused ({rc} {err!r})")
    lesson["stages"] = {"owned": "plan", "surfaced": 6}
    rc, _, err = run("add", "--json", "-", cwd=x, index=idx, stdin=json.dumps(lesson))
    ok(rc == 0, f"P: an ordinary string stage id is accepted ({rc} {err!r})")

    # Q — two lines with one origin at the SAME revision: the kept id does not depend on the
    # order of the lines.
    kept = []
    empty = work / "q-empty"
    empty.mkdir()
    for order in (("mem:bbb@2", "mem:aaa@2"), ("mem:aaa@2", "mem:bbb@2")):
        q = work / f"q-{order[0][4:7]}.jsonl"
        q.write_text("".join(line(m) + "\n" for m in order), encoding="utf-8")
        rc, out, err = run("rebuild", "--roots", str(empty), index=q)
        kept.append([o.get("memory") for o in entries_of(q)["dot-ids"]["origins"]])
        ok(rc == 0 and "dropped mem:bbb@2" in out + err, f"Q: the dropped id is named ({order} {out!r} {err!r})")
    ok(kept == [["mem:aaa@2"], ["mem:aaa@2"]], f"Q: a same-revision tie keeps the smaller id either way ({kept})")


def round14_controls():
    """Round 14 (adversarial): F1 a monorepo that merged another repository's history never
    takes that repository's v1.95.0 origin (the commit's roots and the key v1.95.0 would have
    computed decide); F2 an origin whose project is read this run is never re-keyed; F3 `add`
    keeps one memory id on one live project; and the LOW items: L2 one git question per
    (checkout, commit); L3 no absolute path in `add` or `query` messages; L5 a stage id v1.95.0
    accepted is normalised on read, never set aside with its memory id; L6 the schema's stage
    ids are not blank."""
    work = tree("tp-lessons-r14-")

    def root_of(repo):
        return git(repo, "rev-list", "--max-parents=0", "--first-parent", "HEAD").split()[-1]

    def legacy(idx, memory, project=None):
        """Rewrite every origin of the one line as v1.95.0 wrote it: no checkouts, a memory id,
        optionally another project key."""
        line = json.loads(idx.read_text(encoding="utf-8").splitlines()[0])
        for o in line["origins"]:
            o.pop("checkouts", None)
            o.pop("carried", None)
            o["memory"] = memory
            if project:
                o["project"] = project
        idx.write_text(json.dumps(line, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    def init_root(repo, text, want):
        """A fresh repository whose root commit satisfies want(root), retried."""
        for attempt in range(200):
            if (repo / ".git").exists():
                shutil.rmtree(repo / ".git")
            repo.mkdir(parents=True, exist_ok=True)
            git(repo, "init", "-q")
            (repo / f"ROOT-{text.replace(' ', '-')}.md").write_text(f"{text} {attempt}", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", f"{text} {attempt}")
            if want(git(repo, "rev-parse", "HEAD")):
                return
        raise SystemExit(f"fixture {text}: no root satisfied the order in 200 tries")

    # F1 — monorepo B merged A's whole history (retro included) at its root. A's v1.95.0
    # origin holds mem:a. Neither a rebuild over B alone nor an add in B moves it, whichever
    # root sorts lower (when A's sorts lower, v1.95.0 would even have keyed B as A).
    for order in ("a-lower", "a-higher"):
        for verb in ("rebuild", "add"):
            base = work / f"f1-{order}-{verb}"
            # A's root in the middle of the range, so either order is a few tries away.
            for attempt in range(60):
                a_repo, _ = headed_repo("a", [("retro.md", "export gate", KEY)], parent=base / "ra" / str(attempt))
                ra = root_of(a_repo)
                if ra[0] in "56789a":
                    break
            b_repo = base / "rb" / "b"
            init_root(b_repo, "monorepo", (lambda r: ra < r) if order == "a-lower" else (lambda r: ra > r))
            git(b_repo, "fetch", "-q", str(a_repo), "HEAD:ahist")
            git(b_repo, "merge", "-q", "--allow-unrelated-histories", "-m", "mono", "ahist")
            idx = base / "index.jsonl"
            run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=a_repo, index=idx)
            ka = lesson_of(idx)["origins"][0]["project"]
            legacy(idx, "mem:a@1")
            if verb == "rebuild":
                rc, out, err = run("rebuild", "--roots", str(base / "rb"), index=idx)
            else:
                rc, out, err = run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=b_repo, index=idx)
            e = lesson_of(idx)
            held = [(o["project"], o.get("memory")) for o in e["origins"] if o.get("memory")]
            ok(rc == 0 and held == [(ka, "mem:a@1")] and "re-keyed" not in out,
               f"F1 {order} {verb}: a monorepo never takes the merged repository's id ({rc} {held} {out!r} {err!r})")
            rc, _, err = run("record", e["id"], "--answer", "-", cwd=a_repo, index=idx,
                             stdin=json.dumps({"memoryId": "mem:a", "revision": 2}))
            ok(rc == 0, f"F1 {order} {verb}: A still records its own id ({rc} {err!r})")

    # F1b — the commit is this checkout's own, but v1.95.0 would never have given this checkout
    # the origin's key: no evidence it is this repository's, so it is not re-keyed.
    base = work / "f1b"
    x, _ = headed_repo("x", [("retro.md", "export gate", KEY)], parent=base / "roots")
    idx = base / "index.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=x, index=idx)
    legacy(idx, "mem:b@1", project="p-000000000000")
    rc, out, _ = run("rebuild", "--roots", str(base / "roots"), index=idx)
    held = [(o["project"], o.get("memory")) for o in lesson_of(idx)["origins"] if o.get("memory")]
    ok(rc == 0 and held == [("p-000000000000", "mem:b@1")] and "re-keyed" not in out,
       f"F1b: a key v1.95.0 would not have computed here is not re-keyed ({held} {out!r})")

    # F1c — every other condition holds (X's own commit, X merged a history whose root sorts
    # lower, so v1.95.0 keyed X under that root), but the old-key origin HAS provenance: it was
    # not written by v1.95.0, so nothing proves it is X's under an old key. Never re-keyed.
    base = work / "f1c"
    x, _ = headed_repo("x", [("retro.md", "export gate", KEY)], parent=base / "roots")
    rx = root_of(x)
    o_repo = base / "other"
    init_root(o_repo, "other", lambda r: r < rx)
    git(x, "fetch", "-q", str(o_repo), "HEAD:ohist")
    git(x, "merge", "-q", "--allow-unrelated-histories", "-m", "other in", "ohist")
    idx = base / "index.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=x, index=idx)
    line = json.loads(idx.read_text(encoding="utf-8"))
    ro = "p-" + root_of(o_repo)[:12]
    line["origins"][0].update(project=ro, memory="mem:c@1")  # checkouts kept
    idx.write_text(json.dumps(line, sort_keys=True) + "\n", encoding="utf-8")
    rc, out, _ = run("rebuild", "--roots", str(base / "roots"), index=idx)
    held = [(o["project"], o.get("memory")) for o in lesson_of(idx)["origins"] if o.get("memory")]
    ok(rc == 0 and held == [(ro, "mem:c@1")] and "re-keyed" not in out,
       f"F1c: an origin with provenance is never re-keyed ({rc} {held} {out!r})")

    # F1d — two repositories each qualify on every other condition: one history H with roots
    # R0 < R1, R2 (first-parent R1) and a second checkout whose first-parent root is R2 holding
    # the same commit and retro. A v1.95.0 origin keyed R0 could be either: never re-keyed.
    base = work / "f1d"
    h = base / "roots" / "h"
    h.mkdir(parents=True)
    git(h, "init", "-q")

    def orphan_root(branch, name, want):
        for attempt in range(200):
            if branch != "main" or attempt:
                git(h, "checkout", "-q", "--orphan", f"{branch}-{attempt}")
                git(h, "rm", "-rqf", "--ignore-unmatch", ".")
            (h / name).write_text(f"{name} {attempt}", encoding="utf-8")
            git(h, "add", "-A")
            git(h, "commit", "-q", "-m", f"{name} {attempt}")
            sha = git(h, "rev-parse", "HEAD")
            if want(sha):
                git(h, "branch", "-q", "-f", branch, sha)
                return sha
        raise SystemExit(f"F1d fixture: no {name} root in 200 tries")
    # R1 and R2 sort in the upper half, so a lower R0 is a few tries away, never a flake.
    r1 = orphan_root("main", "r1.md", lambda s: s[0] in "89abcdef")
    r2 = orphan_root("r2", "r2.md", lambda s: s[0] in "89abcdef")
    r0 = orphan_root("r0", "r0.md", lambda s: s < r1 and s < r2)
    git(h, "checkout", "-q", "main")
    for other in ("r0", "r2"):
        git(h, "merge", "-q", "--allow-unrelated-histories", "-m", f"{other} in", other)
    (h / "fix.txt").write_text("fix", encoding="utf-8")
    git(h, "add", "-A")
    git(h, "commit", "-q", "-m", "fix")
    c = git(h, "rev-parse", "HEAD")
    write_retros(h, [("retro.md", "export gate", KEY)], c)
    git(h, "add", "-A")
    git(h, "commit", "-q", "-m", "retro")
    for b in git(h, "branch", "--format=%(refname:short)").split():
        if b not in ("main", "r2"):
            git(h, "branch", "-q", "-D", b)
    h2 = base / "roots" / "h2"
    git(base, "clone", "-q", str(h), str(h2))
    git(h2, "checkout", "-q", "-b", "trunk", "origin/r2")
    git(h2, "merge", "-q", "--no-ff", "-m", "H in", "origin/main")
    git(h2, "remote", "remove", "origin")
    git(h2, "branch", "-q", "-D", "main")
    idx = base / "index.jsonl"
    for repo in (h, h2):
        run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=repo, index=idx)
    ok(sorted({o["project"] for o in lesson_of(idx)["origins"]}) == sorted({"p-" + r1[:12], "p-" + r2[:12]}),
       f"F1d fixture: two repositories, keyed R1 and R2 ({lesson_of(idx)['origins']})")
    line = json.loads(idx.read_text(encoding="utf-8"))
    ghost = {k: v for k, v in line["origins"][0].items() if k not in ("checkouts", "carried")}
    ghost.update(project="p-" + r0[:12], memory="mem:d@1")
    line["origins"].append(ghost)
    idx.write_text(json.dumps(line, sort_keys=True) + "\n", encoding="utf-8")
    rc, out, _ = run("rebuild", "--roots", str(base / "roots"), index=idx)
    held = [(o["project"], o.get("memory")) for o in lesson_of(idx)["origins"] if o.get("memory")]
    ok(rc == 0 and held == [("p-" + r0[:12], "mem:d@1")] and "re-keyed" not in out,
       f"F1d: an origin two repositories could each be is never re-keyed ({rc} {held} {out!r})")

    # F2 — X merged Y's root (Y's sorts lower: v1.95.0 keyed X as Y). X's origin, written by
    # v1.95.0 under Y's key, sits at X's anchor; Y itself is read this run with its entry
    # retitled. Y's project is here, so nothing is moved into X.
    base = work / "f2"
    y = base / "ry" / "y"
    x = base / "rx" / "x"
    init_root(y, "y root", lambda r: r[0] in "01234567")  # lower half: X's root above it is quick
    ry = root_of(y)
    init_root(x, "x root", lambda r: ry < r)
    git(x, "fetch", "-q", str(y), "HEAD:yhist")
    git(x, "merge", "-q", "--allow-unrelated-histories", "-m", "y in", "yhist")
    (x / "fix.txt").write_text("x", encoding="utf-8")
    git(x, "add", "-A")
    git(x, "commit", "-q", "-m", "fix")
    write_retros(x, [("retro.md", "export gate", KEY)], git(x, "rev-parse", "HEAD"))
    git(x, "add", "-A")
    git(x, "commit", "-q", "-m", "retro")
    (y / "fix.txt").write_text("y", encoding="utf-8")
    git(y, "add", "-A")
    git(y, "commit", "-q", "-m", "fix")
    write_retros(y, [("retro.md", "retitled gate", KEY)], git(y, "rev-parse", "HEAD"))
    git(y, "add", "-A")
    git(y, "commit", "-q", "-m", "retro")
    idx = base / "index.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=x, index=idx)
    legacy(idx, "mem:f2@1", project="p-" + ry[:12])
    rc, out, err = run("rebuild", "--roots", str(base), index=idx)
    held = [(o["project"], o.get("memory")) for o in lesson_of(idx)["origins"] if o.get("memory")]
    # The id stays with Y's project — on the carried origin and, following (project, classKey),
    # on Y's retitled entry — and never reaches X's.
    ok(rc == 0 and held and {h[0] for h in held} == {"p-" + ry[:12]} and "re-keyed" not in out,
       f"F2: an origin whose project is read this run is never re-keyed ({rc} {held} {out!r} {err!r})")

    # F2 across verbs (round 15) — the same fixture after an `add` in Y, so the index records
    # Y with provenance. Then an `add` in X, or a rebuild of X's root alone: Y is not read, but
    # it is a known project, so nothing moves into X; a later full rebuild agrees, and Y still
    # records its own id. Who owns the id never depends on verb order or on the roots given.
    def f2_fixture(name):
        b = work / name
        y2, x2 = b / "ry" / "y", b / "rx" / "x"
        init_root(y2, "y root", lambda r: r[0] in "01234567")
        r_y = root_of(y2)
        init_root(x2, "x root", lambda r: r_y < r)
        git(x2, "fetch", "-q", str(y2), "HEAD:yhist")
        git(x2, "merge", "-q", "--allow-unrelated-histories", "-m", "y in", "yhist")
        for repo, head in ((x2, "export gate"), (y2, "retitled gate")):
            (repo / "fix.txt").write_text(name, encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "fix")
            write_retros(repo, [("retro.md", head, KEY)], git(repo, "rev-parse", "HEAD"))
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "retro")
        ix = b / "index.jsonl"
        run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=x2, index=ix)
        legacy(ix, "mem:f2@1", project="p-" + r_y[:12])
        run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=y2, index=ix)
        return b, x2, y2, "p-" + r_y[:12], ix
    for verb in ("add in X", "rebuild of X alone"):
        b, x2, y2, ky, ix = f2_fixture("f2-" + verb.split()[0])
        if verb == "add in X":
            rc, out, err = run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=x2, index=ix)
        else:
            rc, out, err = run("rebuild", "--roots", str(b / "rx"), index=ix)
        held = {o["project"] for o in lesson_of(ix)["origins"] if o.get("memory")}
        ok(rc == 0 and held == {ky} and "re-keyed" not in out,
           f"F2 {verb}: a known project's origin is never re-keyed ({rc} {held} {out!r} {err!r})")
        rc, out, _ = run("rebuild", "--roots", str(b), index=ix)
        held = {o["project"] for o in lesson_of(ix)["origins"] if o.get("memory")}
        rc2, _, err2 = run("record", lesson_of(ix)["id"], "--answer", "-", cwd=y2, index=ix,
                           stdin=json.dumps({"memoryId": "mem:f2", "revision": 2}))
        ok(rc == 0 and held == {ky} and rc2 == 0,
           f"F2 {verb}: a later full rebuild agrees and Y records its own id ({held} {rc2} {err2!r})")

    # m10 (round 15) — re-init, rebuild, the documented re-attach, rebuild again: the carried
    # FOREIGN holder is not live, so the id stays on the new origin and is never stripped.
    base = work / "m10"
    r, _ = headed_repo("repo", [("retro.md", "export gate", KEY)], parent=base / "roots")
    idx = base / "index.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=r, index=idx)
    ok(record_mem(idx, r, KEY, "mem:z") == 0, "m10 fixture: mem:z recorded")
    init_root(r, "reinit", lambda s: True)
    write_retros(r, [("retro.md", "export gate", KEY)], git(r, "rev-parse", "HEAD"))
    git(r, "add", "-A")
    git(r, "commit", "-q", "-m", "retro")
    run("rebuild", "--roots", str(base / "roots"), index=idx)
    rc = run("record", lesson_of(idx)["id"], "--answer", "-", cwd=r, index=idx,
             stdin=json.dumps({"memoryId": "mem:z", "revision": 2}))[0]
    ok(rc == 0, f"m10 fixture: the re-attach at the same checkout is accepted ({rc})")
    rc, out, _ = run("rebuild", "--roots", str(base / "roots"), index=idx)
    live_mem = [o.get("memory") for o in lesson_of(idx)["origins"] if not o.get("carried")]
    ok(rc == 0 and live_mem == ["mem:z@2"] and "is held by" not in out,
       f"m10: after the re-attach a rebuild keeps the id on the new origin ({live_mem} {out!r})")

    # F3 — the M2 sequence, then `add` in the old clone instead of a rebuild: the id stays on
    # the project that held it first, and the add says so.
    base = work / "f3"
    r, _ = high_root_repo("repo", [("retro.md", "export gate", KEY)], parent=base / "roots")
    idx = base / "index.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=r, index=idx)
    ok(record_mem(idx, r, KEY, "mem:y") == 0, "F3 fixture: the project records mem:y")
    k_old = lesson_of(idx)["origins"][0]["project"]
    git(base, "clone", "-q", str(r), str(base / "attic" / "old"))
    init_root(r, "reinit", lambda s: "p-" + s[:12] < k_old)
    write_retros(r, [("retro.md", "export gate", KEY)], git(r, "rev-parse", "HEAD"))
    git(r, "add", "-A")
    git(r, "commit", "-q", "-m", "retro")
    run("rebuild", "--roots", str(base / "roots"), index=idx)
    rc = run("record", lesson_of(idx)["id"], "--answer", "-", cwd=r, index=idx,
             stdin=json.dumps({"memoryId": "mem:y", "revision": 2}))[0]
    ok(rc == 0, f"F3 fixture: the re-attach at the same path is accepted ({rc})")
    rc, out, err = run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=base / "attic" / "old", index=idx)
    holders = sorted(o["project"] for o in lesson_of(idx)["origins"] if o.get("memory"))
    ok(rc == 0 and holders == [k_old] and "mem:y is held by" in out,
       f"F3: add leaves one id on one live project, the earlier holder ({rc} {holders} {out!r} {err!r})")
    rc, out, _ = run("rebuild", "--roots", str(base / "roots"), str(base / "attic"), index=idx)
    ok(rc == 0 and sorted(o["project"] for o in lesson_of(idx)["origins"] if o.get("memory")) == [k_old],
       f"F3: the next rebuild agrees ({out!r})")

    # L2 — one `cat-file` per (checkout, commit) in a run, however many origins ask.
    base = work / "l2"
    keys3 = (KEY, K2, "third-class-key")
    r, _ = headed_repo("repo", [("retro.md", f"gate {i}", k) for i, k in enumerate(keys3)], parent=base / "roots")
    idx = base / "index.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=r, index=idx)
    init_root(r, "reinit", lambda s: True)
    write_retros(r, [("retro.md", f"gate {i}", k) for i, k in enumerate(keys3)], git(r, "rev-parse", "HEAD"))
    git(r, "add", "-A")
    git(r, "commit", "-q", "-m", "retro")
    log = base / "cat-file.log"
    binp = base / "bin"
    binp.mkdir()
    (binp / "git").write_text(
        f"#!/bin/sh\nif [ \"$1\" = cat-file ]; then echo \"$(pwd -P) $*\" >> {log}; fi\n"
        f"exec {shutil.which('git')} \"$@\"\n", encoding="utf-8")
    (binp / "git").chmod(0o755)
    rc, out, _ = run("rebuild", "--roots", str(base / "roots"), index=idx,
                     env_extra={"PATH": f"{binp}:{os.environ['PATH']}"})
    asked = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    ok(rc == 0 and asked and len(asked) == len(set(asked)),
       f"L2: git is asked once per (checkout, commit) ({len(asked)} asked, {len(set(asked))} distinct)")

    # L3 — add and query messages name files, never an absolute path.
    base = work / "l3"
    base.mkdir()
    plain = base / "plain"
    plain.mkdir()
    (base / "a-file").write_text("x", encoding="utf-8")
    x, _ = headed_repo("x", [("retro.md", "export gate", KEY)], parent=base / "repos")
    outside = base / "elsewhere" / "retro.md"
    outside.parent.mkdir()
    outside.write_text("# r\n", encoding="utf-8")
    cases = (("query absent", ["query", "gate"], None, base / "absent" / "index.jsonl", "absent"),
             ("add outside git", ["add", "--retro", "r.md", "--all", "--root", str(plain)], None,
              base / "i1.jsonl", "not inside a git repository"),
             ("add unwritable index", ["add", "--retro", "docs/evidence/retro.md", "--all"], x,
              base / "a-file" / "sub" / "index.jsonl", "cannot be"),
             ("add outside retro", ["add", "--retro", str(outside), "--all"], x,
              base / "i2.jsonl", "outside the repository"),
             # From a subdirectory, with the index in no ancestor of the repository: the
             # repository's top is neither the directory given nor under a named one, and is
             # still named, not printed.
             ("add from a subdirectory", ["add", "--retro", str(outside), "--all"], x / "docs",
              work / "l3-index" / "i3.jsonl", "outside the repository"))
    for what, args, cwd, index, says in cases:
        rc, out, err = run(*args, cwd=cwd, index=index)
        ok(says in out + err and str(work) not in out + err and str(work.resolve()) not in out + err,
           f"L3 {what}: the message names files, not absolute paths ({rc} {out!r} {err!r})")

    # L5 — stage ids v1.95.0 accepted (long, a line separator, a path) are normalised on read;
    # the line and its memory id are kept, never set aside as corrupt.
    base = work / "l5"
    x, _ = headed_repo("x", [("retro.md", "export gate", KEY)], parent=base / "roots")
    idx = base / "index.jsonl"
    run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=x, index=idx)
    line = json.loads(idx.read_text(encoding="utf-8"))
    old_stages = {"owned": "a stage identifier far longer than thirty-two characters",
                  "surfaced": "4 x"}
    for holder in [line] + [o["lesson"] for o in line["origins"]]:
        holder["stages"] = dict(old_stages)
    line["origins"][0]["memory"] = "mem:l5@1"
    idx.write_text(json.dumps(line, ensure_ascii=False) + "\n", encoding="utf-8")
    rc, out, err = run("query", "gate", index=idx)
    ok(rc == 0 and "could not be parsed" not in err and "normalised" in err
       and not list(base.glob("index.jsonl.corrupt-*")),
       f"L5: a v1.95.0 stage id is normalised on read, not set aside ({rc} {err!r})")
    (base / "empty").mkdir()
    rc, out, err = run("rebuild", "--roots", str(base / "empty"), index=idx)  # carried: body kept
    e = lesson_of(idx)
    st = e["origins"][0]["lesson"]["stages"]
    ok(rc == 0 and e["origins"][0].get("memory") == "mem:l5@1"
       and st == {"owned": "a stage identifier far longer th", "surfaced": "4 x"}
       and e["stages"] == st and "normalised" not in run("query", "gate", index=idx)[2],
       f"L5: the memory id survives and the next write stores the normalised ids ({rc} {e} {out!r})")
    sys.path.insert(0, str(SCRIPT.parent))
    import lessons as L  # noqa: E402
    ok([L._stage_id(v) for v in (old_stages["owned"], old_stages["surfaced"], "/home/someone/plan", 6, "plan")]
       == ["a stage identifier far longer th", "4 x", "stage", 6, "plan"],
       "L5: _stage_id folds, cuts, and replaces what it cannot keep")

    # L6 — the schema's string stage ids: at most 32 characters and never blank.
    sch = json.loads(SCHEMA.read_text(encoding="utf-8"))
    for k in ("owned", "surfaced"):
        spec = sch["properties"]["stages"]["properties"][k]
        ok(spec.get("maxLength") == 32 and spec.get("minLength") == 1 and spec.get("pattern") == "\\S",
           f"L6: stages.{k} in the schema is 1-32 characters and not blank ({spec})")


def round16_controls():
    """Round 16 (adversarial): ownership is recoverable, not predicted. X merged Y's history; a
    v1.95.0 origin keyed under Y's root holds mem:f2. When X is read before Y ever was (an `add`
    in X, or a rebuild of X's root alone), the re-key moves the id into X and records
    `rekeyedFrom: <Y>`; the first time Y is read (add or rebuild), or Y records the id, it takes
    it back. Whichever verb runs first, the final owner is Y. P4: a known Y is never re-keyed at
    all. And when Y already holds its own id, nothing moves."""
    work = tree("tp-lessons-r16-")

    def root_of(repo):
        return git(repo, "rev-list", "--max-parents=0", "--first-parent", "HEAD").split()[-1]

    def init_root(repo, text, want):
        for attempt in range(200):
            if (repo / ".git").exists():
                shutil.rmtree(repo / ".git")
            repo.mkdir(parents=True, exist_ok=True)
            git(repo, "init", "-q")
            (repo / f"ROOT-{text.replace(' ', '-')}.md").write_text(f"{text} {attempt}", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", f"{text} {attempt}")
            if want(git(repo, "rev-parse", "HEAD")):
                return
        raise SystemExit(f"r16 fixture {text}: no root satisfied the order in 200 tries")

    def fixture(name):
        """X merged Y (Y's root in the lower half, below X's); X's entry and Y's retitled one
        share the class key; the index holds only the v1.95.0 origin, keyed under Y's root."""
        b = work / name
        y, x = b / "ry" / "y", b / "rx" / "x"
        init_root(y, "y root", lambda r: r[0] in "01234567")
        ry = root_of(y)
        init_root(x, "x root", lambda r: ry < r)
        git(x, "fetch", "-q", str(y), "HEAD:yhist")
        git(x, "merge", "-q", "--allow-unrelated-histories", "-m", "y in", "yhist")
        for repo, head in ((x, "export gate"), (y, "retitled gate")):
            (repo / "fix.txt").write_text(name, encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "fix")
            write_retros(repo, [("retro.md", head, KEY)], git(repo, "rev-parse", "HEAD"))
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "retro")
        ix = b / "index.jsonl"
        run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=x, index=ix)
        kx = lesson_of(ix)["origins"][0]["project"]
        line = json.loads(ix.read_text(encoding="utf-8").splitlines()[0])
        for o in line["origins"]:
            o.pop("checkouts", None)
            o.update(project="p-" + ry[:12], memory="mem:f2@1")
        ix.write_text(json.dumps(line, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        return b, x, y, kx, "p-" + ry[:12], ix

    def holders(ix):
        return sorted((o["project"], o.get("memory"), o.get("rekeyedFrom"))
                      for o in lesson_of(ix)["origins"] if o.get("memory"))

    def x_first(verb, b, x, ix):
        if verb == "add in X":
            return run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=x, index=ix)
        return run("rebuild", "--roots", str(b / "rx"), index=ix)

    def add_y(y, ix):
        return run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=y, index=ix)

    for verb in ("add in X", "rebuild of X alone"):
        # Then: add Y, a full rebuild, and Y records its own id.
        b, x, y, kx, ky, ix = fixture("a-" + verb.split()[0])
        rc, out, err = x_first(verb, b, x, ix)
        ok(rc == 0 and holders(ix) == [(kx, "mem:f2@1", ky)] and "re-keyed" in out,
           f"r16 {verb}: X read first re-keys the id and records its source ({rc} {holders(ix)} {out!r} {err!r})")
        # A repeated add in X keeps the source with the id.
        run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=x, index=ix)
        ok(holders(ix) == [(kx, "mem:f2@1", ky)], f"r16 {verb}: a repeated add in X keeps rekeyedFrom ({holders(ix)})")
        rc, out, err = add_y(y, ix)
        ok(rc == 0 and holders(ix) == [(ky, "mem:f2@1", None)] and "reclaimed" in out and "goes back to " + ky in out,
           f"r16 {verb}: the first add in Y reclaims its id, said aloud ({rc} {holders(ix)} {out!r} {err!r})")
        rc, out, _ = run("rebuild", "--roots", str(b), index=ix)
        ok(rc == 0 and holders(ix) == [(ky, "mem:f2@1", None)],
           f"r16 {verb}: a full rebuild after the reclaim agrees ({holders(ix)} {out!r})")
        rc, _, err = run("record", lesson_of(ix)["id"], "--answer", "-", cwd=y, index=ix,
                         stdin=json.dumps({"memoryId": "mem:f2", "revision": 2}))
        ok(rc == 0 and holders(ix) == [(ky, "mem:f2@2", None)],
           f"r16 {verb}: Y records its own id ({rc} {err!r} {holders(ix)})")

        # Or: the full rebuild reclaims it by itself.
        b, x, y, kx, ky, ix = fixture("b-" + verb.split()[0])
        x_first(verb, b, x, ix)
        rc, out, _ = run("rebuild", "--roots", str(b), index=ix)
        ok(rc == 0 and holders(ix) == [(ky, "mem:f2@1", None)] and "reclaimed" in out,
           f"r16 {verb}: a full rebuild reclaims the id for Y ({holders(ix)} {out!r})")


    # record alone reclaims: X holds the re-keyed id and Y has an origin that holds nothing
    # (written by hand, as an index from before round 16 could hold it).
    b, x, y, kx, ky, ix = fixture("record")
    x_first("add in X", b, x, ix)
    yi = b / "y-only.jsonl"
    add_y(y, yi)
    line = json.loads(ix.read_text(encoding="utf-8"))
    line["origins"] += [o for o in json.loads(yi.read_text(encoding="utf-8"))["origins"]]
    ix.write_text(json.dumps(line, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    ok(holders(ix) == [(kx, "mem:f2@1", ky)], f"r16 record fixture: X holds the id, Y holds none ({holders(ix)})")
    rc, out, err = run("record", lesson_of(ix)["id"], "--answer", "-", cwd=y, index=ix,
                       stdin=json.dumps({"memoryId": "mem:f2", "revision": 2}))
    ok(rc == 0 and holders(ix) == [(ky, "mem:f2@2", None)] and "reclaimed" in out,
       f"r16: Y's record reclaims the id from X ({rc} {holders(ix)} {out!r} {err!r})")

    # Y already holds its own id: two store records stay two, and that is said.
    b, x, y, kx, ky, ix = fixture("own")
    x_first("add in X", b, x, ix)
    line = json.loads(ix.read_text(encoding="utf-8"))
    add_y(y, b / "y2.jsonl")
    yo = json.loads((b / "y2.jsonl").read_text(encoding="utf-8"))["origins"][0]
    line["origins"].append(dict(yo, memory="mem:own@1"))
    ix.write_text(json.dumps(line, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    rc, out, _ = run("rebuild", "--roots", str(b), index=ix)
    ok(rc == 0 and holders(ix) == sorted([(kx, "mem:f2@1", ky), (ky, "mem:own@1", None)])
       and "nothing moved" in out,
       f"r16: Y holding its own id keeps it and X keeps the re-keyed one ({holders(ix)} {out!r})")

    # The loader accepts `rekeyedFrom` only as a project key beside a memory id.
    good = json.loads(ix.read_text(encoding="utf-8"))
    for name, value, mem in (("not-a-key", "Y", "mem:q@1"), ("no-memory", "p-0123456789ab", None)):
        bad = json.loads(json.dumps(good))
        o = bad["origins"][0]
        o["rekeyedFrom"] = value
        if mem is None:
            o.pop("memory", None)
        else:
            o["memory"] = mem
        h = work / f"shape-{name}.jsonl"
        h.write_text(json.dumps(bad) + "\n", encoding="utf-8")
        rc, _, err = run("query", "gate", index=h)
        ok(rc == 0 and "could not be parsed" in err, f"r16: a line with rekeyedFrom {name} is set aside ({rc} {err!r})")

    # P4 — Y known first (add Y), then a rebuild of X alone, then an add in X: never re-keyed.
    b, x, y, kx, ky, ix = fixture("p4")
    add_y(y, ix)
    run("rebuild", "--roots", str(b / "rx"), index=ix)
    rc, out, _ = run("add", "--retro", "docs/evidence/retro.md", "--all", cwd=x, index=ix)
    ok(rc == 0 and {h[0] for h in holders(ix)} == {ky} and "re-keyed" not in out,
       f"r16 P4: a known Y keeps its id through any order ({holders(ix)} {out!r})")


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
    # `exec sleep`, never `sleep; exec git`: the timeout kills the shim's own process, so no
    # orphaned sleeper outlives it in the process group. One that did made a negative whose
    # first failure landed within three seconds of this case refuse its plant on a loaded CI
    # runner ("plant left a live process group", round 13). The real git is never needed here.
    (shim / "git").write_text("#!/bin/sh\nexec sleep 3\n")
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
    # Named by its file name, never its absolute path: a rebuild's refusal goes through the same
    # redaction as its report (round 13, O).
    ok(rc == 1 and "index index.jsonl cannot be read" in err and str(work) not in err
       and str(work.resolve()) not in err and "mem:abc@3" in locked_idx.read_text(encoding="utf-8"),
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
    # Named home-relative, never absolute (round 14, L3): both files are `index.jsonl`.
    ok(moved.is_file() and "moved the local index" in err
       and "~/.task-pipeline/lessons/index.jsonl" in err and str(h2) not in err,
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
    round11_controls()
    round12_controls()
    round13_controls()
    round14_controls()
    round16_controls()
    source_admission_controls()
    print(f"PASS: lessons.py — {CASES} cases")


if __name__ == "__main__":
    main()
