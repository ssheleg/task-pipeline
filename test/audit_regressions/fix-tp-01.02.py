#!/usr/bin/env python3
"""FIX-TP-01.02 — the operator's explicit model/effort is inherited verbatim
(sherlock audit, TP-01, second leaf).

The fix under test (SKILL.md + references/model-tiering.md):
* advice and choice separated — the recommendation is advice; an explicit
  operator choice is inherited by plan, stages and subagents unchanged;
* task size is never a basis for switching; only a RECORDED override with a
  basis changes the model mid-run;
* an unsupported capability is surfaced as its own named line, never a
  silent model swap;
* the inheritance rule run as behaviour.

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


def t_advice_vs_choice():
    d = flat("references/model-tiering.md")
    assert "Advice and choice are different things, and the second wins." in d
    assert "inherit it unchanged" in d
    s = flat("SKILL.md")
    assert "the choice — inherited verbatim by plan, stages and subagents" in s


def t_task_size_is_not_a_basis():
    d = flat("references/model-tiering.md")
    assert "Task size is not a basis for switching" in d
    assert "a large task does not upgrade the model, a mechanical stage does not downgrade it" in d
    assert "A switch nobody recorded is a defect, whatever it saved." in d


def t_unsupported_capability_separate():
    d = flat("references/model-tiering.md")
    assert "An unsupported capability is its own line, never a silent swap." in d
    assert "states that limitation by NAME" in d
    assert "the same defect as the silent downgrade" in d


# ---- behaviour


def resolve_model(explicit, recommendation, task_size, override_map=None,
                  stage=None, capability_gap=None):
    """The doctrine's rule as a function."""
    model = explicit or recommendation
    if override_map and stage in override_map:
        entry = override_map[stage]
        if entry.get("basis"):                    # recorded, with a basis
            model = entry["model"]
    notes = []
    if capability_gap:
        notes.append(f"limitation: {capability_gap}")   # named, model unchanged
    return {"model": model, "notes": notes}


def t_plan_and_executor_keep_user_model():
    for size in ("tiny", "huge"):
        r = resolve_model("sonnet-4.5", "opus-top", size)
        assert r["model"] == "sonnet-4.5", \
            f"a {size} task overrode the explicit model"


def t_unrecorded_override_does_not_switch():
    r = resolve_model("opus-top", "opus-top", "huge",
                      override_map={"build": {"model": "cheap"}}, stage="build")
    assert r["model"] == "opus-top", "an override with no basis switched the model"
    r2 = resolve_model("opus-top", "opus-top", "huge",
                       override_map={"build": {"model": "cheap",
                                                "basis": "operator: mechanical stage"}},
                       stage="build")
    assert r2["model"] == "cheap", "a recorded override with a basis was ignored"


def t_capability_gap_is_a_note_not_a_swap():
    r = resolve_model("text-only-model", "opus-top", "big",
                      capability_gap="no vision; screenshots cannot be read")
    assert r["model"] == "text-only-model", "a capability gap silently swapped the model"
    assert any("limitation" in n for n in r["notes"])


def main():
    case("advice and choice are separated; choice inherited verbatim",
         t_advice_vs_choice)
    case("task size is not a basis for switching", t_task_size_is_not_a_basis)
    case("an unsupported capability is its own line", t_unsupported_capability_separate)
    case("fixture: plan and executor keep the user model at any task size",
         t_plan_and_executor_keep_user_model)
    case("fixture: only a recorded override with a basis switches",
         t_unrecorded_override_does_not_switch)
    case("fixture: a capability gap is a named note, never a swap",
         t_capability_gap_is_a_note_not_a_swap)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
