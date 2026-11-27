#!/usr/bin/env python3
"""spec_judge.py: the judge gate of spec S0 (template, rubric, rounds, hash, verify).

No model is called: answers come in through --import, the route a subscription
judge uses. Every case names the behaviour it proves.
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SJ = ROOT / "plugins/task-pipeline/skills/task-pipeline/scripts/spec_judge.py"
SEEDS = ROOT / "test/judge-seeds"
cases = 0
failed = []


def run(*a, env=None):
    e = dict(os.environ, HOME=tmp, TASK_PIPELINE_SPEND_LOG=os.path.join(tmp, "spend.jsonl"))
    e.pop("TASK_PIPELINE_JUDGE_RUBRIC", None)
    e.pop("TASK_PIPELINE_JUDGE_MODELS", None)
    e.update(env or {})
    return subprocess.run([sys.executable, str(SJ), *map(str, a)], capture_output=True, text=True, env=e, cwd=tmp)


def case(name, cond, detail=""):
    global cases
    cases += 1
    if not cond:
        failed.append(f"{name}: {detail}")


def answer(path, family="vendor-b", blocking=0, zero=False, auto=None, model="judge-x"):
    qs = [{"q": f"question {i}", "blocking": True, "fix": f"fix {i}"} for i in range(blocking)]
    sc = {k: 2 for k in ("clarity", "completeness", "testability", "finality", "consistency")}
    if zero:
        sc["finality"] = 0
    path.write_text(json.dumps({"model": model, "family": family, "questions": qs, "scores": sc,
                                "auto_fail": auto or []}))
    return path


def fresh(name, size="S"):
    d = pathlib.Path(tmp) / name
    shutil.copytree(SEEDS / "control", d)
    meta = json.loads((d / "spec.json").read_text())
    meta["size"] = size
    (d / "spec.json").write_text(json.dumps(meta))
    if size != "S":
        t = (d / "spec.md").read_text().replace("| size | S |", f"| size | {size} |")
        (d / "spec.md").write_text(t)
    return d


tmp = tempfile.mkdtemp()
try:
    # Fact 7: the hash excludes the Judge record section.
    d = fresh("hash")
    h1 = run("hash", d).stdout.strip()
    t = (d / "spec.md").read_text()
    (d / "spec.md").write_text(t.replace("none yet", "| 1 | x | pass |"))
    case("hash ignores the judge record", run("hash", d).stdout.strip() == h1)
    (d / "spec.md").write_text(t.replace("two measured", "three measured").replace("Two measured", "Three measured"))
    case("hash moves with the content", run("hash", d).stdout.strip() != h1)

    # Fact 1: the template's sections; the control passes lint, every lint seed fails it.
    case("control spec lints clean", run("lint", SEEDS / "control").returncode == 0)
    for s in sorted(SEEDS.glob("*/defect.json")):
        if json.loads(s.read_text())["caught_by"] == "lint":
            case(f"lint catches {s.parent.name}", run("lint", s.parent).returncode == 1)
    r = run("seeds", SEEDS, "--lint-only", "--min", "6")
    case("seeds: lint alone catches the six mechanical seeds", r.returncode == 0, r.stdout)
    case("seeds: ten seeds", "of 10 caught" in r.stdout, r.stdout)

    # No verdict: exit 2.
    d = fresh("none")
    case("no verdict exits 2", run("check", d, "--verify").returncode == 2)

    # Fact 3 and 7: pass from another family -> judged, verify 0; an edit -> stale 2.
    d = fresh("pass")
    r = run("check", d, "--import", answer(pathlib.Path(tmp) / "a1.json"))
    case("cross-family pass exits 0", r.returncode == 0, r.stdout + r.stderr)
    rec = json.loads((d / "judge/1.json").read_text())
    case("record names model, family, rubric", rec["model"] == "judge-x" and rec["family"] == "vendor-b"
         and rec["rubric"] == "judge-rubric/1" and rec["status"] == "judged", rec)
    case("spec.json status is judged", json.loads((d / "spec.json").read_text())["status"] == "judged")
    case("judge record written into spec.md", "## Judge record\n\n| Round |" in (d / "spec.md").read_text())
    case("verify passes after the record is written", run("check", d, "--verify").returncode == 0)
    (d / "spec.md").write_text((d / "spec.md").read_text().replace("Two measured", "Four measured"))
    case("an edit after judging is stale (2)", run("check", d, "--verify").returncode == 2)

    # Fact 3: verdicts computed by the tool.
    d = fresh("fixes")
    r = run("check", d, "--import", answer(pathlib.Path(tmp) / "a2.json", blocking=2))
    case("blocking questions with fixes: pass-with-fixes, exit 1",
         r.returncode == 1 and json.loads((d / "judge/1.json").read_text())["verdict"] == "pass-with-fixes")
    case("pass-with-fixes does not satisfy the gate", run("check", d, "--verify").returncode == 1)
    d = fresh("zero")
    run("check", d, "--import", answer(pathlib.Path(tmp) / "a3.json", zero=True))
    case("a score of 0 fails", json.loads((d / "judge/1.json").read_text())["verdict"] == "fail")
    d = fresh("auto")
    run("check", d, "--import", answer(pathlib.Path(tmp) / "a4.json", auto=["undefined term Tier-Q"]))
    case("an automatic fail fails", json.loads((d / "judge/1.json").read_text())["verdict"] == "fail")
    d = pathlib.Path(tmp) / "lintfail"
    shutil.copytree(SEEDS / "02-placeholder", d)
    run("check", d, "--import", answer(pathlib.Path(tmp) / "a5.json"))
    case("a mechanical fail overrides a model's pass", json.loads((d / "judge/1.json").read_text())["verdict"] == "fail")

    # Fact 4: rounds 2 and 3 read the previous questions and the diff; round 3 only for one blocking.
    d = fresh("rounds")
    run("check", d, "--import", answer(pathlib.Path(tmp) / "r1.json", blocking=2))
    (d / "spec.md").write_text((d / "spec.md").read_text().replace("Two measured", "Five measured"))
    p = run("prompt", d).stdout
    case("round 2 prompt carries the previous questions", "question 1" in p and "## Previous questions" in p)
    case("round 2 prompt carries the diff", "+Five measured" in p and "-Two measured" in p, p[-600:])
    run("check", d, "--import", answer(pathlib.Path(tmp) / "r2.json", blocking=2))
    r = run("check", d, "--import", answer(pathlib.Path(tmp) / "r3.json"))
    case("no third round when two blocking questions stay open", r.returncode == 1
         and not (d / "judge/3.json").exists() and (d / "judge/escalation.md").exists(), r.stdout)
    d = fresh("round3")
    run("check", d, "--import", answer(pathlib.Path(tmp) / "s1.json", blocking=2))
    (d / "spec.md").write_text((d / "spec.md").read_text().replace("Two measured", "Six measured"))
    run("check", d, "--import", answer(pathlib.Path(tmp) / "s2.json", blocking=1))
    (d / "spec.md").write_text((d / "spec.md").read_text().replace("Six measured", "Seven measured"))
    r = run("check", d, "--import", answer(pathlib.Path(tmp) / "s3.json"))
    case("a third round runs for exactly one blocking question", r.returncode == 0
         and (d / "judge/3.json").exists(), r.stdout + r.stderr)
    r = run("check", d, "--import", answer(pathlib.Path(tmp) / "s4.json"))
    case("a judged spec is not judged again", r.returncode == 0 and not (d / "judge/4.json").exists())

    # Fact 5 and Users: degraded judging.
    d = fresh("degS")
    r = run("check", d, "--import", answer(pathlib.Path(tmp) / "g1.json", family="vendor-a"))
    case("same-family pass on S is judged-degraded and passes", r.returncode == 0
         and json.loads((d / "judge/1.json").read_text())["status"] == "judged-degraded")
    case("judged-degraded S satisfies verify", run("check", d, "--verify").returncode == 0)
    estate = pathlib.Path(tmp) / "estate-rubric.md"
    rub = (ROOT / "plugins/task-pipeline/skills/task-pipeline/references/judge-rubric.md").read_text()
    estate.write_text(rub.replace("require_cross_family: false", "require_cross_family: true"))
    case("estate rubric refuses judged-degraded",
         run("check", d, "--verify", env={"TASK_PIPELINE_JUDGE_RUBRIC": str(estate)}).returncode == 1)
    d = fresh("degL", size="L")
    r = run("check", d, "--import", answer(pathlib.Path(tmp) / "g2.json", family="vendor-a"))
    case("same-family pass on L stays draft", r.returncode == 1
         and json.loads((d / "judge/1.json").read_text())["status"] == "draft")

    # Fact 5: judge choice from judge-models/1; placeholders are never called.
    d = fresh("pick")
    r = run("check", d, "--dry-run", "--json")
    case("shipped placeholders cannot run (3)", r.returncode == 3, r.stdout + r.stderr)
    m = pathlib.Path(tmp) / "models.json"
    m.write_text(json.dumps({"schema": "judge-models/1", "models": [
        {"model": "same-top", "family": "vendor-a", "rank": 1},
        {"model": "other-top", "family": "vendor-b", "rank": 2},
        {"model": "other-low", "family": "vendor-c", "rank": 3}]}))
    r = run("check", d, "--dry-run", "--json", "--models", m)
    out = json.loads(r.stdout)
    case("the strongest model of another family is picked", out["judge"]["model"] == "other-top"
         and out["cross_family"] is True, r.stdout)
    r = run("check", d, "--json", "--models", m, env={"OPENROUTER_API_KEY": ""})
    case("no key cannot run (3)", r.returncode == 3, r.stderr)

    # Fact 8: the CI gate finds a spec by its id.
    repo = pathlib.Path(tmp) / "repo"
    shutil.copytree(SEEDS / "control", repo / "docs/specs/2026-11-27-export")
    shutil.copytree(SEEDS / "01-missing-section", repo / "docs/plans/p/s1")
    r = run("find", "seed-control", "--root", repo)
    case("find resolves an id under docs/specs", r.returncode == 0 and r.stdout.strip().endswith("2026-11-27-export"))
    r = run("find", "seed-01", "--root", repo)
    case("find resolves an id under docs/plans", r.returncode == 0 and r.stdout.strip().endswith("s1"))
    case("an unknown id cannot run (3)", run("find", "nope", "--root", repo).returncode == 3)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

if failed:
    print("FAIL: spec_judge.py")
    for f in failed:
        print("  " + f)
    sys.exit(1)
print(f"PASS: spec_judge.py — {cases} cases")
