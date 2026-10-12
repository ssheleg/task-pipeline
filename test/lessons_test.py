#!/usr/bin/env python3
"""The local lesson index (`scripts/lessons.py`, lesson/1) — stdlib only.

MN §3.1, node M-1. A retro entry that carries a `**Lesson:**` line is a lesson; the local
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
    r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, input=stdin, timeout=60,
                       env=env)
    return r.returncode, r.stdout, r.stderr


def git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
    r = subprocess.run(["git", "-c", "commit.gpgsign=false", *args], cwd=repo,
                       capture_output=True, text=True, env=env, timeout=30)
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {r.stderr}")
    return r.stdout.strip()


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
    ok({"kind": "commit", "sha": sha_a} in args["arguments"]["evidence"], "the evidence commit travels")
    ok(args["arguments"]["owner"] == "agent:task-pipeline", "owner is named, never operator")
    rc, out, _ = run("emit-observatory", lid, "--tool", "observatory_lesson",
                     "--project-id", "project:alpha", cwd=a, index=idx)
    la = json.loads(out)["arguments"]
    ok(la["classKey"] == "absence-needs-its-own-check" and la["origin"] == {
        "projectId": "project:alpha", "commit": sha_a}, "observatory_lesson arguments carry classKey and origin")
    ledger = a / ".task-pipeline" / "run.md"
    ledger.parent.mkdir()
    ledger.write_text("# Run ledger\n\nRun: `x`\n\n## Log\n\n", encoding="utf-8")
    rc, out, err = run("record", lid, "--answer", "-", "--ledger", str(ledger), cwd=a,
                       stdin=json.dumps({"memoryId": "mem:abc", "revision": 1}), index=idx)
    ok(rc == 0 and "mem:abc@1" in idx.read_text(encoding="utf-8"), f"record keeps the memory id ({rc} {err})")
    ok("event: lessons — recorded" in ledger.read_text(encoding="utf-8"), "record appends one ledger line")
    rc, out, err = run("record", lid, "--answer", "-", "--ledger", str(ledger), cwd=a,
                       stdin=json.dumps({"error": "bounds", "message": "too long"}), index=idx)
    ok(rc == 0 and "event: lessons — store refused — bounds" in ledger.read_text(encoding="utf-8"),
       f"a refusal is one ledger line, exit 0, the local entry kept ({rc} {err})")

    # --- lock contention: a held lock makes add refuse, nothing written
    try:
        import fcntl
    except ImportError:
        fcntl = None
    if fcntl:
        before = idx.read_bytes()
        fh = open(idx.parent / "index.jsonl.lock", "a+")
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

    # --- the default index lives under HOME, never anywhere else
    rc, out, _ = run("path")
    ok(rc == 0 and out.strip() == str(HOME / ".sshlg-skills" / "lessons" / "index.jsonl"),
       f"the default index path is ~/.sshlg-skills/lessons/index.jsonl ({out!r})")
    print(f"PASS: lessons.py — {CASES} cases")


if __name__ == "__main__":
    main()
