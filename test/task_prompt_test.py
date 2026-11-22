#!/usr/bin/env python3
"""task_prompt.py, the check of a task written for an executor: every question against a
planted prompt, so a check that stopped catching the missing part fails here."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "plugins/task-pipeline/skills/task-pipeline/scripts/task_prompt.py")
CASES, FAILS = [], []

GOOD = """Goal: the export endpoint returns CSV with a header row for every account type.
Fix `src/export/csv.py`; do not change the JSON export.
Done when `pytest tests/export -q` passes and a business account's file opens in a spreadsheet.
Work in waves: after the fix, make a second pass over every caller of `to_csv` for what was
missed, and list what you did not examine.
Report back: the commits, the test output, open concerns."""


def case(fn):
    CASES.append(fn)
    return fn


def run(*args, stdin=None):
    r = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, input=stdin)
    return r.returncode, r.stdout + r.stderr


def expect(cond, msg):
    if not cond:
        raise AssertionError(msg)


def verdict(text, *args):
    code, out = run("check", "-", "--json", *args, stdin=text)
    return code, json.loads(out)


def without(marker):
    return "\n".join(l for l in GOOD.split("\n") if marker not in l)


@case
def a_whole_task_passes(root):
    code, res = verdict(GOOD)
    expect(code == 0 and res["kind"] == "work" and not res["fails"] and not res["warns"], res)


@case
def a_task_without_its_end_result_fails_by_name(root):
    code, res = verdict(without("Goal:"))
    expect(code == 1 and res["fails"] == ["P1"], res)


@case
def a_task_without_a_finish_criterion_fails_by_name(root):
    code, res = verdict(without("Done when"))
    expect(code == 1 and res["fails"] == ["P2"], res)


@case
def a_task_without_a_pass_for_what_was_missed_fails_by_name(root):
    text = "\n".join(l for l in GOOD.split("\n") if "waves" not in l and "missed" not in l)
    code, res = verdict(text)
    expect(code == 1 and res["fails"] == ["P3"], res)


@case
def a_wave_named_as_a_label_is_not_a_sweep(root):
    text = without("waves").replace("missed, and list what you did not examine.", "") + "\nYou build wave 3 of the release. Sound waves render in the chart."
    code, res = verdict(text)
    expect("P3" in res["fails"], res)


@case
def a_stop_for_approval_between_steps_fails_and_is_quoted(root):
    code, res = verdict(GOOD + "\nAfter the fix, wait for my approval before you continue.")
    expect(code == 1 and res["fails"] == ["P4"] and res["gates"], res)
    code, res = verdict(GOOD + "\nПосле шага дождись подтверждения.")
    expect(code == 1 and "P4" in res["fails"], res)


@case
def forbidding_a_stop_is_not_a_gate(root):
    code, res = verdict(GOOD + "\nDo not wait for approval between steps. Не жди подтверждения.")
    expect(code == 0 and not res["gates"], res)


@case
def a_lookup_owes_its_result_and_its_return_only(root):
    code, res = verdict("Find where the retry limit is read.\nI need the file and line of every reader.\nReturn a table: reader, file:line.")
    expect(code == 0 and res["kind"] == "lookup", res)
    code, res = verdict("Look at the retry limit in the config loader and its readers.")
    expect(code == 1 and res["fails"] == ["P1", "P5"], res)


@case
def a_verifier_owes_no_sweep(root):
    code, out = run("check", "-", "--json", "--kind", "verify",
                    stdin="Goal: a verdict on node N-12.\nIt is done when the node's check exits 0.\nReturn the eight-key report.")
    res = json.loads(out)
    expect(code == 0 and res["kind"] == "verify", res)


@case
def a_russian_task_is_read(root):
    text = ("Цель: экспорт отдаёт CSV со строкой заголовков.\nИсправь `src/export/csv.py`.\n"
            "Готово, когда тесты зелёные.\nПосле правки сделай второй проход по всем вызовам: что пропущено, "
            "и перечисли, что не проверено.\nВерни коммиты и вывод тестов.")
    code, res = verdict(text)
    expect(code == 0 and res["kind"] == "work", res)


@case
def a_brief_on_disk_is_read_with_the_task(root):
    brief = os.path.join(root, "task-7-brief.md")
    open(brief, "w", encoding="utf-8").write(GOOD)
    code, res = verdict("Implement task 7. Read and follow the brief: %s" % brief)
    expect(code == 0 and res["followed"], res)


@case
def a_brief_nobody_can_read_is_said_not_guessed(root):
    code, res = verdict("Implement task 7. Read and follow the brief: /nonexistent/dir/task-7-brief.md\nReport the commits.")
    expect(res["not_read"] and set(res["open"]) == {"P1", "P2", "P3"} and not res["fails"], res)


@case
def a_corpus_counts_each_question(root):
    path = os.path.join(root, "c.jsonl")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"prompt": GOOD, "project": "a"}) + "\n")
        fh.write(json.dumps({"prompt": without("Goal:"), "project": "a"}) + "\n")
    code, out = run("corpus", path, "--by", "project", "--json")
    g = json.loads(out)
    expect(code == 0 and g["all"]["n"] == 2 and g["all"]["ok"] == 1 and g["all"]["fails"]["P1"] == 1
           and g["a"]["n"] == 2, out)


def main():
    for fn in CASES:
        root = tempfile.mkdtemp(prefix="taskprompt-")
        try:
            fn(root)
            print(f"ok   {fn.__name__}")
        except AssertionError as exc:
            FAILS.append(fn.__name__)
            print(f"FAIL {fn.__name__}: {exc}")
        finally:
            shutil.rmtree(root, ignore_errors=True)
    if FAILS:
        print(f"FAIL: task_prompt.py, {len(FAILS)} of {len(CASES)} cases")
        return 1
    print(f"PASS: task_prompt.py, {len(CASES)} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
