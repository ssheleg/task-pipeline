#!/usr/bin/env python3
"""FIX-HK-02 — the commit gate's `if` filter lives on the handler, where Claude Code reads it.

`templates/hooks.example.json` carried `"if": "Bash(git commit *)"` beside `matcher` from
2026-08-03 to v1.86.1. A matcher group is `{matcher, hooks}` and nothing else (read out of
the 2.1.270 binary's zod schema), so the key was ignored — silently until 2.1.270, which
announces it at every session start — and the documentation gate ran on EVERY Bash call of
every project that copied the block.

This regression lives here and not as a workflow step on purpose: `validate.yml` sits at
511,941 of GitHub's 512,000 bytes (ssheleg/task-pipeline#91), and the validator refuses a
workflow past the ceiling. It plants the pre-v1.86.2 shape into a copy of the tree and
requires `test/validate.py` to refuse it by name — the same proof a negative self-test
gives, without the step.

Standard library only.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
REL = os.path.join("plugins", "task-pipeline", "skills", "task-pipeline", "templates",
                   "hooks.example.json")
REF = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline", "references",
                   "hooks.md")
MIRROR = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "evidence-docs",
                      "references", "hooks.md")
GROUP = {"matcher", "hooks"}
HANDLER = {"type", "command", "args", "if", "shell", "timeout", "statusMessage", "once",
           "async", "asyncRewake"}

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def t_shipped_shape():
    d = json.load(open(os.path.join(ROOT, REL), encoding="utf-8"))
    commit_if = 0
    for ev, groups in d["hooks"].items():
        for g in groups:
            assert set(g) <= GROUP, f"{ev}: a group carries {sorted(set(g) - GROUP)} — Claude Code ignores it"
            for h in g["hooks"]:
                assert set(h) <= HANDLER, f"{ev}: a handler carries {sorted(set(h) - HANDLER)}"
                if ev == "PreToolUse" and str(h.get("if", "")).startswith("Bash(git commit"):
                    commit_if += 1
    assert commit_if == 1, "the commit gate must carry exactly one handler-level Bash(git commit *)"


def t_doctrine_says_handler():
    for p in (REF, MIRROR):
        t = " ".join(open(p, encoding="utf-8").read().split())
        assert "inside the handler object" in t, f"{os.path.relpath(p, ROOT)}: no longer says the filter goes inside the handler"
        assert '"if": "Bash(git commit *)" beside "matcher": "Bash"' not in t, \
            f"{os.path.relpath(p, ROOT)}: tells the reader to put `if` beside `matcher` again"


def t_validator_refuses_the_old_shape():
    tmp = tempfile.mkdtemp(prefix="fix-hk-02-")
    try:
        work = os.path.join(tmp, "repo")
        shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(
            ".git", "node_modules", "__pycache__", ".agent-sync", ".task-pipeline"))
        p = os.path.join(work, REL)
        d = json.load(open(p, encoding="utf-8"))
        g = d["hooks"]["PreToolUse"][0]
        assert "if" in g["hooks"][0] and "if" not in g, "PLANT DID NOT LAND: unexpected shipped shape"
        g["if"] = g["hooks"][0].pop("if")
        json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
        r = subprocess.run([sys.executable, os.path.join(work, "test", "validate.py")],
                           capture_output=True, text=True, timeout=900)
        out = r.stdout + r.stderr
        assert r.returncode != 0, "the validator ACCEPTED a filter beside the matcher"
        assert "a matcher group is only matcher+hooks" in out, \
            "the validator failed, but not on the planted key — the refusal is not this check's"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    case("the template carries only keys Claude Code's hook schema knows, if on the handler",
         t_shipped_shape)
    case("hooks.md and its evidence-docs mirror say 'inside the handler object'",
         t_doctrine_says_handler)
    case("plant: the pre-v1.86.2 shape (if beside matcher) is refused by name",
         t_validator_refuses_the_old_shape)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
