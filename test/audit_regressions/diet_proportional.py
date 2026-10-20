#!/usr/bin/env python3
"""DIET-1020 A, B, C: the proportional run, the reading diet and the anti-loop numbers.

A. `scripts/short_path.py` DECIDES the short path from stage 0's five answers; every
   answer outside *small* takes the full flow and is named.
B. The always-read surfaces stay small: the command is a pointer, SKILL.md keeps its
   headroom, each description stays short and moved its triggers into `## Triggers`.
C. The numbers the doctrine states are the numbers the scripts enforce: the short-path
   thresholds, the rounds owed by risk class, the tier count on R1, the ceiling.

Each check computes both sides; none restates an expected value from memory.
Standard library only.
"""
import importlib.util
import pathlib
import re
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
SK = ROOT / "plugins/task-pipeline/skills/task-pipeline"
SKILLS = ROOT / "plugins/task-pipeline/skills"
failures = []


def case(name):
    def wrap(fn):
        try:
            fn()
            print("  ok  " + name)
        except AssertionError as exc:
            failures.append(name)
            print("FAIL  %s: %s" % (name, exc))
        return fn
    return wrap


def load(rel):
    spec = importlib.util.spec_from_file_location(rel.stem, rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SP = SK / "scripts/short_path.py"
sp = load(SP)
SMALL = dict(files=["a.py", "b.md"], contract=False, user_facing=False, deploy=False, risk="R1")


def run(*args):
    r = subprocess.run([sys.executable, str(SP)] + list(args), capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


@case("a small change takes the short path, and the line says why (exit 0)")
def _():
    code, out = run("--files", "a.py", "b.md", "--contract", "no", "--user-facing", "no",
                    "--deploy", "no", "--risk", "R1")
    assert code == 0 and out.startswith("short path: R1 · 2 files · no contract"), out


@case("every answer outside small takes the full flow and is named (exit 3)")
def _():
    flips = {"contract": (True, "public contract"), "user_facing": (True, "user-observable"),
             "deploy": (True, "deploy target"), "risk": ("R2", "risk R2"),
             "files": (["f%d" % i for i in range(sp.MAX_FILES + 1)], "files, over"),
             "unknowns": (1, "material unknown")}
    for key, (val, needle) in flips.items():
        args = dict(SMALL, unknowns=0)
        args[key] = val
        short, line = sp.decide(**args)
        assert not short and line.startswith("full flow:") and needle in line, (key, line)
    code, out = run("--files", "a.py", "--contract", "no", "--user-facing", "yes",
                    "--deploy", "no", "--risk", "R1")
    assert code == 3 and "user-observable" in out, out
    code, out = run("--contract", "no", "--user-facing", "no", "--deploy", "no", "--risk", "R1")
    assert code == 3 and "not bounded" in out, "an unbounded change took the short path: " + out


@case("the doctrine states the thresholds the script enforces")
def _():
    st0 = (SK / "references/stage-00-intake.md").read_text(encoding="utf-8")
    assert "N ≤ %d" % sp.MAX_FILES in st0 and "risk **%s**" % sp.SMALL_RISK in st0, \
        "stage-00-intake.md and short_path.py disagree on the thresholds"
    assert "scripts/short_path.py" in st0, "the doctrine does not name its decider"
    words = {5: "five"}
    skill = re.sub(r"\s+", " ", (SK / "SKILL.md").read_text(encoding="utf-8"))
    assert "at most %s files" % words.get(sp.MAX_FILES, sp.MAX_FILES) in skill and \
        "%s risk" % sp.SMALL_RISK in skill, "SKILL.md states other thresholds"


@case("the command is a pointer, and SKILL.md keeps its headroom")
def _():
    cmd = (ROOT / "plugins/task-pipeline/commands/task-pipeline.md").read_bytes()
    assert len(cmd) <= 2500, "the command grew back into a copy: %d bytes" % len(cmd)
    skill = (SK / "SKILL.md").read_bytes()
    # 5000 tokens is the cap (make-skill); 10% headroom at ~3.7 bytes per token here
    assert len(skill) <= 16650, "SKILL.md is %d bytes, past the headroom bound" % len(skill)


@case("each description is short and its triggers moved verbatim into ## Triggers")
def _():
    for name in ("task-pipeline", "project-audit", "evidence-docs"):
        t = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
        d = re.search(r'^description: "(.*)"$', t, re.M).group(1)
        assert len(d) <= 400, "%s description is %d chars" % (name, len(d))
        trig = re.search(r"(?ms)^## Triggers\n(.*?)(?=^## |\Z)", t)
        assert trig and "Use when" in trig.group(1), "%s has no ## Triggers with the old list" % name


@case("the rounds and tiers the doctrine states are the ones graph.py enforces")
def _():
    g = load(SK / "scripts/graph.py")
    words = {1: "one", 2: "two", 3: "three"}
    cert = re.sub(r"\s+", " ", (SK / "references/certification.md").read_text(encoding="utf-8"))
    want = "R1 one (with one blind tier), R2 %s, R3 %s" % (words[g.ROUNDS_OWED["R2"]],
                                                      words[g.ROUNDS_OWED["R3"]])
    assert words[g.ROUNDS_OWED["R1"]] == "one" and want in cert, \
        "certification.md does not state %r" % want
    assert g.ONE_TIER_RISK == ("R1",), g.ONE_TIER_RISK
    it = (SK / "references/iteration.md").read_text(encoding="utf-8")
    for cls, n in g.ROUNDS_OWED.items():
        row = re.search(r"(?m)^\| %s \|[^\n]*\| (one|three) \| (\d)" % cls, it)
        assert row and int(row.group(2)) == n, "iteration.md's %s row disagrees with %d" % (cls, n)
    guard = (SK / "references/loop-guard.md").read_text(encoding="utf-8")
    assert "**3 failing\ncertification rounds** per node" in guard or \
        "**3 failing certification rounds** per node" in re.sub(r"\s+", " ", guard), \
        "loop-guard.md does not state the certification ceiling"


if failures:
    print("\n%d failure(s)" % len(failures))
    sys.exit(1)
print("\nall green")
