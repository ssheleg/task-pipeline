#!/usr/bin/env python3
"""USR-015 — the release-iteration evals have fixtures that can fail.

Release iteration 1 (node M-4) added INSTR-09..13, TRIG-12, NOTRIG-09 and the
outcome cases TP-OUT-006/007. The two outcome cases judge an ARTIFACT through a
command over a frozen fixture, so this file proves what an eval cannot prove
about itself:

  * each case's `prompt.files` digests match the fixture bytes in the tree — a
    fixture edited without its case is a different case wearing the old id;
  * each command check passes on the fixture today, and FAILS when the fixture
    is changed so the expected behaviour no longer holds — an inverted wrapper
    that cannot go red is decoration;
  * the eval ids the node promised exist, in the categories it promised.

Standard library only. Fixture copies live in a TemporaryDirectory, never in
the tree.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CASES = os.path.join(ROOT, "evals", "cases", "task-pipeline.json")
SUITE = os.path.join(ROOT, "evals", "task-pipeline.evals.json")
FIX = os.path.join(ROOT, "evals", "fixtures")
SCRIPTS = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline", "scripts")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def outcome_cases():
    with open(CASES, encoding="utf-8") as fh:
        return {c["id"]: c for c in json.load(fh)["cases"]}


def run_wrapper(path, scripts=SCRIPTS):
    env = dict(os.environ, TASK_PIPELINE_SCRIPTS=scripts)
    return subprocess.run(["bash", path], capture_output=True, text=True,
                          env=env, timeout=60)


def copy_fixture(name, dest):
    target = os.path.join(dest, name)
    shutil.copytree(os.path.join(FIX, name), target)
    return target


def t_promised_ids_exist():
    with open(SUITE, encoding="utf-8") as fh:
        evals = {e["id"]: e["category"] for e in json.load(fh)["evals"]}
    want = {"TRIG-12": "should_trigger", "NOTRIG-09": "should_not_trigger"}
    want.update({f"INSTR-{n:02d}": "instruction_following" for n in range(9, 14)})
    for eid, cat in want.items():
        assert evals.get(eid) == cat, f"{eid} is {evals.get(eid)!r}, expected {cat}"
    ids = outcome_cases()
    for prefix in ("TP-OUT-006-", "TP-OUT-007-"):
        assert any(i.startswith(prefix) for i in ids), f"no outcome case {prefix}…"


def t_frozen_files_match():
    for cid, c in outcome_cases().items():
        for f in c["prompt"].get("files") or []:
            p = os.path.join(ROOT, f["path"])
            assert os.path.isfile(p), f"{cid}: frozen file {f['path']} is missing"
            with open(p, "rb") as fh:
                got = hashlib.sha256(fh.read()).hexdigest()
            assert got == f["sha256"], (f"{cid}: {f['path']} changed without its case "
                                        "— re-freeze the digest in the same change")


def t_command_checks_pass_today():
    for cid, c in outcome_cases().items():
        for o in c["checks"]["outcome"]:
            if o["kind"] != "command-exit-0" or "evals/fixtures/" not in o["target"]:
                continue
            path = os.path.join(ROOT, o["target"].split()[-1])
            r = run_wrapper(path)
            assert r.returncode == 0, f"{cid}: {o['target']} exited {r.returncode}: {r.stderr}"


def t_waves_wrapper_goes_red_when_the_item_is_claimed():
    with tempfile.TemporaryDirectory() as tmp:
        d = copy_fixture("waves-unclaimed", tmp)
        plan = os.path.join(d, "plan.json")
        with open(plan, encoding="utf-8") as fh:
            body = json.load(fh)
        body["nodes"].append({"id": "N-002", "wave": 1, "closes": ["B-103"]})
        with open(plan, "w", encoding="utf-8") as fh:
            json.dump(body, fh)
        r = run_wrapper(os.path.join(d, "expect-refusal.sh"))
        assert r.returncode != 0, ("the inverted wrapper passed although every item is "
                                   "now claimed — it cannot tell a refusal from a pass")


def t_waves_wrapper_never_passes_without_the_tool():
    with tempfile.TemporaryDirectory() as tmp:
        d = copy_fixture("waves-unclaimed", tmp)
        r = run_wrapper(os.path.join(d, "expect-refusal.sh"), scripts=tmp)
        assert r.returncode not in (0, 1), \
            f"a missing waves.py exited {r.returncode}; it must be its own non-zero code"


def t_lessons_wrapper_goes_red_without_the_lesson():
    with tempfile.TemporaryDirectory() as tmp:
        d = copy_fixture("lessons", tmp)
        idx = os.path.join(d, "index.jsonl")
        with open(idx, encoding="utf-8") as fh:
            kept = [ln for ln in fh if "L-70cf4d4825df" not in ln]
        with open(idx, "w", encoding="utf-8") as fh:
            fh.writelines(kept)
        r = run_wrapper(os.path.join(d, "expect-match.sh"))
        assert r.returncode != 0, "the wrapper passed with the expected lesson removed"


def t_lessons_wrapper_leaves_no_lock_in_the_tree():
    run_wrapper(os.path.join(FIX, "lessons", "expect-match.sh"))
    stray = sorted(set(os.listdir(os.path.join(FIX, "lessons")))
                   - {"index.jsonl", "expect-match.sh"})
    assert not stray, f"the check wrote into the fixture directory: {stray}"


def main():
    case("the promised eval ids exist in their categories", t_promised_ids_exist)
    case("every frozen fixture matches its case's digest", t_frozen_files_match)
    case("each fixture command check passes today", t_command_checks_pass_today)
    case("the waves wrapper goes red once the item is claimed",
         t_waves_wrapper_goes_red_when_the_item_is_claimed)
    case("the waves wrapper never passes without waves.py",
         t_waves_wrapper_never_passes_without_the_tool)
    case("the lessons wrapper goes red without the lesson",
         t_lessons_wrapper_goes_red_without_the_lesson)
    case("the lessons wrapper leaves nothing in the tree",
         t_lessons_wrapper_leaves_no_lock_in_the_tree)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
