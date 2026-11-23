#!/usr/bin/env python3
"""brain.py recall: this project's memory in at most ten lines, read-only, nothing from another side.

Two throwaway git repositories (project A and project B) share one lesson index; recall in A must
return A's lesson and never B's. Runs the real scripts as processes. No network. Trees go at exit.
"""
import atexit
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "plugins" / "task-pipeline" / "skills" / "task-pipeline" / "scripts"
TMP = pathlib.Path(tempfile.mkdtemp(prefix="brain-test-"))
atexit.register(lambda: shutil.rmtree(TMP, ignore_errors=True))
CASES = 0
ENV = dict(os.environ, TASK_PIPELINE_LESSONS=str(TMP / "index.jsonl"), TASK_PIPELINE_BRAIN_LOG=str(TMP / "brain.jsonl"),
           GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@e", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@e",
           GIT_AUTHOR_DATE="2026-10-01T12:00:00Z", GIT_COMMITTER_DATE="2026-10-01T12:00:00Z")


def ok(cond, what):
    global CASES
    CASES += 1
    if not cond:
        print("FAIL: " + what)
        sys.exit(1)


def sh(cwd, *args):
    return subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, env=ENV, timeout=60)


def run(script, cwd, *args):
    return sh(cwd, sys.executable, str(SCRIPTS / script), *args)


RETRO = """# Retro

## Standing instructions

1. Every export check compares the row count with the source before release.

## Recent

### 2026-10-01 the export lost rows
- **Surfaced at:** stage 8 · **Owned by:** stage 5
- **Fix:** grade 2
- **The check:** `test/export_test.py` counts rows
- **Lesson:** `{key}`; an export that drops rows silently must count them against the source
  before it ships · **When:** a job writes an export · **Nouns:** export, rows, {noun}
- **Commit:** `{sha}`
"""


def project(name, noun):
    d = TMP / name
    (d / "docs" / "evidence" / "specs").mkdir(parents=True)
    sh(d, "git", "init", "-q", "-b", "main")
    (d / "README.md").write_text(name)
    sh(d, "git", "add", "-A")
    sh(d, "git", "-c", "commit.gpgsign=false", "commit", "-qm", "init")
    sha = sh(d, "git", "rev-parse", "--short", "HEAD").stdout.strip()
    ev = d / "docs" / "evidence"
    (ev / "retro.md").write_text(RETRO.format(key=f"{name}-export-rows", sha=sha, noun=noun))
    (ev / "backlog.md").write_text("| id | What | State |\n|---|---|---|\n"
                                   "| B-001 | **The monthly export has no CSV header check.** | open |\n"
                                   "| B-002 | **An export closed long ago.** | done |\n")
    (ev / "verification.md").write_text("# Verification\n\n## Shipped state: v1.0.0 (the export ships)\n")
    (ev / "specs" / "2026-09-01-monthly-export.md").write_text("# Monthly export to CSV\n\nSize: S\n")
    (d / "docs" / "DECISIONS.md").write_text("# Decisions\n\n## DEC-0001 CSV, not XLSX, for the export\n")
    sh(d, "git", "add", "-A")
    sh(d, "git", "-c", "commit.gpgsign=false", "commit", "-qm", "docs")
    r = run("lessons.py", d, "add", "--retro", "docs/evidence/retro.md", "--all")
    ok(r.returncode == 0, f"lesson of {name} indexed: " + r.stdout + r.stderr)
    return d


def main():
    a = project("alpha", "csv")
    b = project("beta", "secretbeta")
    # Recall in A: A's lesson, standing instruction, open row, decision, episode, recipe; never B's lesson.
    r = run("brain.py", a, "recall", "export", "rows", "csv", "--json")
    ok(r.returncode == 0, "recall runs: " + r.stderr)
    res = json.loads(r.stdout)
    kinds = {u["kind"] for u in res["lines"]}
    ok({"lesson", "open-item", "decision", "episode", "recipe"} <= kinds, "every kind is recalled: %s" % kinds)
    text = json.dumps(res)
    ok("alpha-export-rows" in text and "beta-export-rows" not in text, "only this project's lesson, never another side's")
    ok("B-002" not in text, "a closed backlog row is not an open item")
    ok(all(u["side"] == "this project" for u in res["lines"]), "every line carries its side")
    ok(all(u["id"].startswith("brain:") and ":" in u["source"] for u in res["lines"]), "ids and cited sources")
    # B's own recall sees B's lesson (the filter is by project, not a blanket ban).
    r = run("brain.py", b, "recall", "export", "secretbeta", "--json", "--no-log")
    ok("beta-export-rows" in r.stdout and "alpha-export-rows" not in r.stdout, "each project reads its own")
    # Budget: never more than ten lines; --limit above ten is refused.
    many = "\n".join(f"| B-{i:03d} | **Export task {i}.** | open |" for i in range(3, 40))
    (a / "docs" / "evidence" / "backlog.md").write_text("| id | What | State |\n|---|---|---|\n" + many + "\n")
    r = run("brain.py", a, "recall", "export", "--json", "--no-log")
    ok(len(json.loads(r.stdout)["lines"]) == 10, "at most ten lines")
    ok(run("brain.py", a, "recall", "export", "--limit", "11").returncode == 2, "a budget above ten is refused")
    # Freshness: an open item whose file was last committed long ago is `stale: verify`.
    r = run("brain.py", b, "recall", "header", "--json", "--no-log")
    items = [u for u in json.loads(r.stdout)["lines"] if u["kind"] == "open-item"]
    ok(items and items[0]["fresh"] == "stale: verify", "an old open item is shown stale: %r" % items)
    # Read-only: the repository is unchanged by a recall.
    before = sh(a, "git", "status", "--porcelain").stdout
    run("brain.py", a, "recall", "export")
    ok(sh(a, "git", "status", "--porcelain").stdout == before, "recall writes nothing in the repository")
    # Degraded is named; nothing matched is not "nothing known".
    empty = TMP / "empty"
    empty.mkdir()
    sh(empty, "git", "init", "-q", "-b", "main")
    (empty / "x").write_text("x")
    sh(empty, "git", "add", "-A")
    sh(empty, "git", "-c", "commit.gpgsign=false", "commit", "-qm", "x")
    r = run("brain.py", empty, "recall", "export")
    ok(r.returncode == 0 and "degraded:" in r.stdout and "not \"nothing known\"" in r.stdout, r.stdout)
    # An instruction inside a record is shown as data, with the warning line first.
    ok(r.stdout.startswith("brain recall: pointers, not evidence"), "the header names lines as pointers")
    # The usage log and stats: recalls counted, and a brief citing an id counts as a used hit.
    log = [json.loads(x) for x in (TMP / "brain.jsonl").read_text().splitlines()]
    ok(len(log) == 3 and all("project" in x and "ids" in x for x in log), "each logged recall is one line: %d" % len(log))
    brief = TMP / "brief.md"
    brief.write_text("Recalled and re-derived: " + log[0]["ids"][0])
    r = run("brain.py", a, "stats", "--cite", str(brief), "--json")
    st = json.loads(r.stdout)
    ok(st["recalls"] == 3 and st["cited"] == 1 and st["empty"] == 1, "stats: %r" % st)
    print(f"brain_test: {CASES} cases passed")


if __name__ == "__main__":
    main()
