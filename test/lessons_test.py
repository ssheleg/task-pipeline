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
        ok(rc != 0 and idx.read_bytes() == before and "not read" in out + err,
           "unreadable discovery subtree cannot silently drop lessons")
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
    rc, _, _ = run("rebuild", "--roots", str(empty), index=idx)
    ok(rc == 0 and idx.read_bytes() == b"", "an explicitly readable empty scope can rebuild to zero")


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
    print(f"PASS: lessons.py — {CASES} cases")


if __name__ == "__main__":
    main()
