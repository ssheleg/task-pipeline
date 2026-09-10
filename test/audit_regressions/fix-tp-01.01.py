#!/usr/bin/env python3
"""FIX-TP-01.01 — intake builds from existing context; questions only for
material unknowns (sherlock audit, TP-01).

The finding: the doctrine guaranteed an extra human round ("interview
relentlessly", one-question-at-a-time, mandatory) instead of checking whether
a real gap exists — raising stops and cost by instruction.

The fix under test (SKILL.md + references/grill.md):
* phase 2 opens with a GAP CHECK: every branch marked answered / immaterial /
  material-unknown; only the third earns a question;
* a complete brief yields ZERO intake questions; already-decided things are
  recorded, never re-negotiated;
* a material unknown the operator cannot answer now becomes ONE bounded
  decision task, and the run proceeds on independent branches;
* the triage rule run as behaviour on two fixtures.

Standard library only.
"""
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def flat(name):
    with open(os.path.join(SKILL, name), encoding="utf-8") as fh:
        return " ".join(fh.read().split())


def t_gap_check_opens_phase_2():
    g = flat("references/grill.md")
    assert "Phase 2 opens with a verdict, not a question." in g
    for kind in ("**answered**", "**immaterial**", "**material unknown**"):
        assert kind in g, f"the {kind} triage class is missing"
    assert "Only the third kind earns a question." in g


def t_complete_brief_zero_questions():
    g = flat("references/grill.md")
    assert "A complete brief yields zero intake questions" in g
    assert "re-negotiating what is already decided" in g
    s = flat("SKILL.md")
    assert "A complete brief yields ZERO intake questions" in s
    assert "recorded, never re-negotiated" in s


def t_bounded_decision_task():
    g = flat("references/grill.md")
    assert "one bounded decision task" in g
    assert "the latest date it can be decided without rework" in g
    assert "proceeds on the branches that do not depend on it" in g


def t_relentless_default_is_gone():
    g = flat("references/grill.md")
    assert "Interview the operator relentlessly about every aspect" not in g, \
        "the unconditional relentless interview survived"
    s = flat("SKILL.md")
    assert "never enough to finish without a human in the loop" not in s, \
        "the guaranteed-human-round claim survived"
    assert "every MATERIAL question skipped" in s
    assert "confirming what the sources already said" in g


# ---- the triage rule as behaviour


def triage(branches):
    """branches: {name: {answered_by, material}} → (questions, decision_tasks)."""
    questions, tasks = [], []
    for name, b in branches.items():
        if b.get("answered_by"):
            continue                       # recorded, never re-asked
        if not b.get("material"):
            continue                       # decided locally, noted
        if b.get("operator_can_answer_now", True):
            questions.append(name)
        else:
            tasks.append(name)             # one bounded decision task
    return questions, tasks


def t_full_brief_fixture_asks_nothing():
    qs, tasks = triage({
        "auth-model": {"answered_by": "ADR-0007", "material": True},
        "error-copy": {"answered_by": "docs/ux/scenarios.md", "material": True},
        "log-format": {"answered_by": None, "material": False},
    })
    assert qs == [] and tasks == [], \
        f"a complete brief still produced questions: {qs} {tasks}"


def t_missing_material_decision_is_one_task():
    qs, tasks = triage({
        "auth-model": {"answered_by": "ADR-0007", "material": True},
        "pricing-tier": {"answered_by": None, "material": True,
                          "operator_can_answer_now": False},
    })
    assert qs == [] and tasks == ["pricing-tier"], \
        f"the missing material decision did not become one bounded task: {qs} {tasks}"


def main():
    case("phase 2 opens with the answered/immaterial/material triage",
         t_gap_check_opens_phase_2)
    case("a complete brief yields zero intake questions", t_complete_brief_zero_questions)
    case("an unanswerable material unknown becomes one bounded decision task",
         t_bounded_decision_task)
    case("the unconditional relentless-interview default is gone",
         t_relentless_default_is_gone)
    case("fixture: a full brief asks nothing", t_full_brief_fixture_asks_nothing)
    case("fixture: a missing material decision is exactly one task",
         t_missing_material_decision_is_one_task)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
