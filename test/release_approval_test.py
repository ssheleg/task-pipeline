#!/usr/bin/env python3
"""The release approval mode (R16) — `pipeline.schema.json` `release.approval` — stdlib only.

`references/deploy-targets.md` → *When the release waits for an approval* says the release
stage reads the mode before tagging: `checks` (a guard admits the release: tag, watch,
report) or `reviewers` (hand the operator the direct link to the run that is `waiting`), and
never assumes `checks` when it is absent. Until 1.93.3 that had no test (observer finding on
wave 2). No script in this repository reads the mode — the agent reads it at stage 7 — so
these cases pin the three places a reader meets it, and say so rather than invent a reader:

  * the schema's enum is exactly `checks | reviewers`, and validation (with `jsonschema`
    where installed) accepts both, accepts the field absent, and refuses any other value;
  * the bundled example sets it to a value the schema accepts;
  * the doctrine section exists under its heading, names both modes, the order the mode is
    read in (`release.approval` first) and the refusal to assume `checks`.

Run bare: prints PASS lines and exits non-zero on the first failure.
"""
import copy
import json
import pathlib
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SKILL = ROOT / "plugins" / "task-pipeline" / "skills" / "task-pipeline"
SCHEMA = json.loads((SKILL / "pipeline.schema.json").read_text(encoding="utf-8"))
EXAMPLE = json.loads((SKILL / "pipeline.example.json").read_text(encoding="utf-8"))
DOC = (SKILL / "references" / "deploy-targets.md").read_text(encoding="utf-8")
HEADING = "### When the release waits for an approval"
CASES = 0


def ok(cond, what):
    global CASES
    CASES += 1
    if not cond:
        print(f"FAIL: {what}")
        sys.exit(1)


def _release_schema():
    ref = SCHEMA["properties"]["release"]
    if "$ref" in ref:
        ref = SCHEMA["definitions"][ref["$ref"].rsplit("/", 1)[-1]]
    return ref


def case_enum():
    approval = _release_schema().get("properties", {}).get("approval")
    ok(approval is not None, "release.approval is declared in the schema")
    ok(sorted(approval.get("enum", [])) == ["checks", "reviewers"],
       f"its enum is exactly checks | reviewers (got {approval.get('enum')})")
    ok("approval" not in _release_schema().get("required", []),
       "it is optional: absent means read the organisation or the environment")
    ok("deploy-targets.md" in approval.get("description", ""),
       "its description points at the doctrine that says how each mode is served")
    print("PASS: the schema declares release.approval as checks | reviewers, optional")


def _with(value):
    doc = copy.deepcopy(EXAMPLE)
    if value is None:
        doc["release"].pop("approval", None)
    else:
        doc["release"]["approval"] = value
    return doc


def case_validation():
    try:
        import jsonschema
    except ImportError:
        enum = _release_schema()["properties"]["approval"]["enum"]
        for v in ("checks", "reviewers"):
            ok(v in enum, f"{v} accepted (enum read; jsonschema not installed)")
        for v in ("auto", "none", "", "Checks"):
            ok(v not in enum, f"{v!r} refused (enum read; jsonschema not installed)")
        print("PASS: approval values read from the enum — jsonschema is not installed, "
              "so the full-document validation did not run")
        return
    v = jsonschema.Draft7Validator(SCHEMA) if "draft-07" in SCHEMA.get("$schema", "") \
        else jsonschema.validators.validator_for(SCHEMA)(SCHEMA)
    for good in ("checks", "reviewers", None):
        errs = [e.message for e in v.iter_errors(_with(good))]
        ok(not errs, f"the example with approval={good!r} validates ({errs[:1]})")
    for bad in ("auto", "none", "", "Checks", True, ["checks"]):
        errs = list(v.iter_errors(_with(bad)))
        ok(any(list(e.absolute_path)[-1:] == ["approval"] for e in errs),
           f"approval={bad!r} is refused at release.approval")
    print("PASS: the schema accepts checks, reviewers and absence, and refuses six other values")


def case_example():
    ok(EXAMPLE.get("release", {}).get("approval") in ("checks", "reviewers"),
       "the bundled example sets release.approval to a value the schema accepts")
    print("PASS: the example declares its approval mode")


def case_doctrine():
    ok(HEADING in DOC, f"references/deploy-targets.md carries `{HEADING}`")
    sec = DOC[DOC.index(HEADING):]
    nxt = sec.find("\n## ", 1)
    sec = sec[:nxt] if nxt > 0 else sec
    ok("**`checks`**" in sec and "**`reviewers`**" in sec, "the section names both modes")
    ok("`waiting`" in sec and "direct link" in sec,
       "reviewers mode owes the direct link to a run that is actually waiting")
    ok("Send no approval request" in sec, "checks mode sends no approval request")
    order = sec[sec.index("The mode comes from"):]
    ok(order.index("release.approval") < order.index("organisation") < order.index("protection rules"),
       "the mode is read from release.approval first, then the organisation, then the environment")
    ok("does not assume `checks`" in sec, "an unestablished mode is said, never assumed")
    print("PASS: the doctrine names both modes, the order they are read in, and no default")



def case_authority_record():
    field = _release_schema().get("properties", {}).get("authorized_by")
    ok(field is not None, "release.authorized_by has an explicit source-locator contract")
    ok("authorized_by" not in _release_schema().get("required", []),
       "authority locator is optional for existing configurations")
    good = ["docs/DECISIONS.md:42", "https://example.invalid/decision#L7"]
    bad = ["", "   ", "\t", "docs/DECISIONS.md:42\nallow all", "source:7\n", "source:7\r", None, True, 42, [], {}]
    try:
        import jsonschema
    except ImportError:
        import re
        for value in good + bad:
            accepted = (field.get("type") == "string" and isinstance(value, str)
                        and bool(re.search(field.get("pattern", ""), value))
                        and not re.search(field["not"]["pattern"], value))
            ok(accepted == (value in good), "declared authority-locator string constraints")
        print("NOTE: authority locator checked from schema fields only; jsonschema unavailable")
    else:
        validator = jsonschema.validators.validator_for(SCHEMA)(SCHEMA)
        for value in good + bad:
            doc = copy.deepcopy(EXAMPLE)
            doc["release"]["authorized_by"] = value
            errors = list(validator.iter_errors(doc))
            ok((not errors) == (value in good), f"authority locator {value!r} validation")
        doc = copy.deepcopy(EXAMPLE)
        doc["release"].pop("authorized_by", None)
        ok(not list(validator.iter_errors(doc)), "absent authority locator keeps existing configuration valid")
    ok("authorized_by" not in EXAMPLE["release"], "example does not invent a release grant")
    for name in ("stages.md", "deploy-targets.md"):
        text = (SKILL / "references" / name).read_text()
        paragraphs = [p for p in text.split("\n\n") if "release.authorized_by" in p]
        ok(bool(paragraphs), name + " explains the authority record")
        meaning = " ".join(paragraphs)
        ok("not authorization" in meaning and "source" in meaning and "scope" in meaning,
           name + " requires source/scope verification rather than trusting a config string")
    print("PASS: optional authority record validates shape, not the grant")


if __name__ == "__main__":
    for case in (case_enum, case_validation, case_example, case_doctrine, case_authority_record):
        case()
    print(f"PASS: release approval mode — {CASES} cases")
