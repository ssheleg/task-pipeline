#!/usr/bin/env python3
"""FIX-PA-03.01 — the optional HTML page is not in the fixed exit criterion
(sherlock audit, PA-03).

The finding: the body writes HTML only with --report, but the exit criterion
demanded the page and its opening on EVERY run; and "read-only" was read as
"nothing written" though the sidecar lands in docs/audit.

The fix under test (project-audit SKILL.md):
* the exit criterion is CONDITIONAL — sidecar always; page + safe links +
  inspect/render status only on --report; a run without --report is complete;
* three modes stdout/json/html, and only --report needs a browser;
* read-only is about the TARGET (source/data), with an allowed output dir;
* the DoD rule run as behaviour.

Standard library only.
"""
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DOC = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "project-audit",
                   "SKILL.md")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def flat():
    with open(DOC, encoding="utf-8") as fh:
        return " ".join(fh.read().split())


def t_exit_criterion_conditional():
    d = flat()
    assert "the criterion is CONDITIONAL on the deliverables requested" in d
    assert "WITHOUT `--report` no page is created and the run is still complete" in d
    assert "the page and the sidecar are written and the page has been opened;" not in d, \
        "the unconditional page-and-open criterion survived"


def t_report_requires_page_and_status():
    d = flat()
    assert "On `--report`, and only then**, the HTML page also exists" in d
    assert "internal links are safe and resolve" in d
    assert "inspect/render status is recorded" in d


def t_three_modes_one_browser():
    d = flat()
    for mode in ("**stdout**", "**json**", "**html**"):
        assert mode in d, f"mode {mode} missing"
    assert "never opens a browser and never requires one" in d
    assert "the browser is a concern of `--report` alone" in d


def t_read_only_is_the_target():
    d = flat()
    assert '"Read-only" is about the TARGET, not the disk.' in d
    assert "Writing the sidecar there is not a violation of read-only" in d
    assert "`--out-dir` to relocate" in d


# ---- the DoD as behaviour


def audit_complete(flags, produced):
    """flags: set of CLI flags; produced: set of artefacts written."""
    missing = []
    if "sidecar" not in produced:
        missing.append("sidecar")
    if "--report" in flags:
        if "page" not in produced:
            missing.append("page")
        if "links-verified" not in produced:
            missing.append("links-verified")
        if "render-status" not in produced:
            missing.append("render-status")
    return {"complete": not missing, "missing": missing}


def t_json_only_run_is_complete():
    r = audit_complete(set(), {"sidecar"})
    assert r["complete"] is True, f"a json-only run was judged incomplete: {r}"


def t_report_run_needs_the_page():
    r = audit_complete({"--report"}, {"sidecar"})
    assert r["complete"] is False and "page" in r["missing"]
    ok = audit_complete({"--report"},
                        {"sidecar", "page", "links-verified", "render-status"})
    assert ok["complete"] is True


def main():
    case("the exit criterion is conditional on requested deliverables",
         t_exit_criterion_conditional)
    case("--report requires an existing page, safe links, render status",
         t_report_requires_page_and_status)
    case("three modes, only --report needs a browser", t_three_modes_one_browser)
    case("read-only is about the target, with an allowed output dir",
         t_read_only_is_the_target)
    case("fixture: a json-only run is complete without a page",
         t_json_only_run_is_complete)
    case("fixture: a --report run is incomplete until the page + status exist",
         t_report_run_needs_the_page)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
