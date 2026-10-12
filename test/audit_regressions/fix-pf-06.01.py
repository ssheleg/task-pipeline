#!/usr/bin/env python3
"""FIX-PF-06.01 — the Fabric taskPipeline adapter refuses what it cannot
honour (sherlock audit, PF-06).

The fix under test:
* pipeline.schema.json gains `must_understand` (a consumer refusing unknown
  entries) and the gate description names the refusal rule;
* fabric's pipelineAdapters/taskPipeline.ts (driven through node when the
  checkout is present, NOT_RUN otherwise): an unknown gate type is refused BY
  NAME, never silently omitted; must_understand outside the adapter's set
  refuses the whole config; profile/skill_lock/graph_version pins validated;
  a supported config round-trips identically, constraints preserved.

Standard library + node only.
"""
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCHEMA = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline",
                      "pipeline.schema.json")
ADAPTER = os.path.join(
    os.environ.get("FABRIC_ROOT", os.path.expanduser("~/DATA/fabric")),
    "apps", "desktop", "src", "main", "pipelineAdapters", "taskPipeline.ts")

failures = []
not_run = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def run_import(cfg):
    js = (
        "import(process.argv[1]).then(m => {"
        "  const r = m.importConfig(JSON.parse(process.argv[2]));"
        "  const rt = r.ok ? JSON.stringify(m.exportConfig(r.pipeline)) : null;"
        "  console.log(JSON.stringify({r, roundtrip: rt}));"
        "});"
    )
    r = subprocess.run(["node", "-e", js, ADAPTER, json.dumps(cfg)],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"node failed: {r.stderr[:300]}"
    return json.loads(r.stdout.strip().splitlines()[-1])


def good_config():
    return {"version": 3, "stages": [
        {"state": "spec", "skills": ["task-pipeline:spec"],
         "gate": {"type": "auto", "check": "npm test"},
         "budget_note": "an extension field that must survive the round-trip"},
        {"state": "build", "skills": ["builder"],
         "gate": {"type": "manual", "check": "operator signs off"}}],
        "must_understand": ["profile", "skill_lock"],
        "profile": {"name": "default"},
        "skill_lock": {"address": "skills.json", "sha256": "c" * 64}}


def t_schema_declares_must_understand():
    d = json.load(open(SCHEMA, encoding="utf-8"))
    assert "must_understand" in d["properties"], "the schema lacks must_understand"
    assert "REFUSES the whole config" in d["properties"]["must_understand"]["description"]
    gate_desc = d["definitions"]["stage"]["properties"]["gate"]["description"]
    assert "never silently omitted" in gate_desc or "silently omitted" in gate_desc, \
        "the gate description does not name the refusal rule"


def _adapter_or_skip():
    if not os.path.isfile(ADAPTER):
        not_run.append("fabric checkout absent — adapter cases NOT_RUN (never PASS)")
        return False
    return True


def t_supported_round_trip():
    if not _adapter_or_skip():
        return
    cfg = good_config()
    out = run_import(cfg)
    assert out["r"]["ok"] is True, f"a supported config was refused: {out['r']}"
    assert json.loads(out["roundtrip"]) == cfg, \
        "the round-trip lost or changed a constraint"


def t_unknown_gate_refused_by_name():
    if not _adapter_or_skip():
        return
    cfg = good_config()
    cfg["stages"][1]["gate"] = {"type": "quorum-vote", "check": "3 of 5"}
    out = run_import(cfg)
    assert out["r"]["ok"] is False
    assert any("quorum-vote" in x for x in out["r"]["reasons"]), \
        "the unknown gate was not refused by name"


def t_unknown_must_understand_refuses_all():
    if not _adapter_or_skip():
        return
    cfg = good_config()
    cfg["must_understand"].append("holographic-consensus")
    out = run_import(cfg)
    assert out["r"]["ok"] is False
    assert any("holographic-consensus" in x for x in out["r"]["reasons"])


def t_pins_validated():
    if not _adapter_or_skip():
        return
    cfg = good_config()
    cfg["skill_lock"] = {"address": "skills.json"}    # no digest
    out = run_import(cfg)
    assert out["r"]["ok"] is False and any("skill_lock" in x for x in out["r"]["reasons"])
    cfg2 = good_config()
    cfg2["graph_version"] = "latest"
    out2 = run_import(cfg2)
    assert out2["r"]["ok"] is False and any("graph_version" in x for x in out2["r"]["reasons"])


FIXTURE = os.path.join(ROOT, "test", "fixtures", "fabric-pipeline-contract.json")
EXAMPLE = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline",
                       "pipeline.example.json")


def _contract():
    return json.load(open(FIXTURE, encoding="utf-8"))


def t_gate_types_match_the_contract():
    """R15 (sshlg-skills waves): runs with NO Fabric checkout, so the seam is never NOT_RUN."""
    d = json.load(open(SCHEMA, encoding="utf-8"))
    ours = sorted(d["definitions"]["stage"]["properties"]["gate"]["properties"]["type"]["enum"])
    assert ours == sorted(_contract()["supported_gates"]), \
        f"gate types {ours} != Fabric adapter's {_contract()['supported_gates']}"


def t_example_config_imports_under_the_contract():
    c = _contract()
    cfg = json.load(open(EXAMPLE, encoding="utf-8"))
    bad = [n for n in cfg.get("must_understand", []) if n not in c["understood_must_understand"]]
    assert not bad, f"pipeline.example.json names must_understand {bad} Fabric would refuse"
    for i, st in enumerate(cfg.get("stages", [])):
        assert st.get("state"), f"stages[{i}].state missing"
        assert isinstance(st.get("skills"), list) and st["skills"], f"stages[{i}].skills empty"
        g = st.get("gate") or {}
        assert g.get("type") in c["supported_gates"], f"stages[{i}].gate.type {g.get('type')!r}"
        assert g.get("check"), f"stages[{i}].gate.check missing"


def t_contract_matches_the_adapter_source():
    """Where a Fabric checkout exists, the fixture is checked against the adapter itself."""
    if not os.path.isfile(ADAPTER):
        not_run.append("fabric checkout absent — fixture-vs-adapter drift check NOT_RUN "
                       "(the contract cases above still ran)")
        return
    import re
    src = open(ADAPTER, encoding="utf-8").read()
    gates = re.search(r"SUPPORTED_GATES = new Set\(\[([^\]]*)\]", src)
    und = re.search(r"UNDERSTOOD = new Set\(\[([^\]]*)\]", src)
    assert gates and und, "the adapter no longer declares SUPPORTED_GATES / UNDERSTOOD as read"
    names = lambda m: sorted(re.findall(r"'([^']+)'", m.group(1)))
    c = _contract()
    assert names(gates) == sorted(c["supported_gates"]), \
        f"adapter gates {names(gates)} != fixture {c['supported_gates']} — re-pin the fixture"
    assert names(und) == sorted(c["understood_must_understand"]), \
        f"adapter understood {names(und)} != fixture — re-pin the fixture"


def main():
    case("gate types match the Fabric contract (no checkout needed)",
         t_gate_types_match_the_contract)
    case("the example config imports under the Fabric contract",
         t_example_config_imports_under_the_contract)
    case("the contract fixture matches the adapter source",
         t_contract_matches_the_adapter_source)
    case("the schema declares must_understand and the gate refusal rule",
         t_schema_declares_must_understand)
    case("a supported config round-trips with constraints preserved",
         t_supported_round_trip)
    case("an unknown gate is refused by name, never omitted",
         t_unknown_gate_refused_by_name)
    case("an ununderstood must_understand refuses the whole config",
         t_unknown_must_understand_refuses_all)
    case("profile/skill_lock/graph_version pins are validated", t_pins_validated)
    for n in not_run:
        print(f"  NOT_RUN  {n}")
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
