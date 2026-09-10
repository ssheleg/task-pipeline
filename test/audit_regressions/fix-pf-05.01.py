#!/usr/bin/env python3
"""FIX-PF-05.01 — the immutable dispatch packet carries every required
constraint and no ephemeral secret (sherlock audit, PF-05).

The finding: build.md required brief/report files, REQ citations and
interfaces, but the graph schema linked a node to none of it (brief, packet,
base revision, output schema), and the workspace + graph are git-ignored and
cleaned up — so the durable, content-addressed context a build ran under did
not exist.

The fix under test (context_packets.py compile_dispatch_packet + schema):
* a fresh packet assembles REQ refs, constraints, interfaces, artifact
  digests, base, scope, budget, profile and skill lock — every ref bound;
* a missing required key OR an unbound ref is REJECTED;
* no ephemeral secret compiles into the packet (a key that names one is
  refused, at any depth);
* the node schema links to the packet by address + digest.

Standard library only.
"""
import importlib.util
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline")
CP = os.path.join(SKILL, "scripts", "context_packets.py")
SCHEMA = os.path.join(SKILL, "graph.schema.json")

_spec = importlib.util.spec_from_file_location("context_packets", CP)
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


REF = {"id": "REQ-1", "address": "docs/spec.md", "sha256": "a" * 64}
ART = {"address": "api/schema.json", "sha256": "b" * 64}


def full_context(**over):
    c = {"requirements": [REF], "constraints": [REF], "interfaces": [REF],
         "artifacts": [ART], "base": {"head": "h1"}, "scope": {"edit_targets": []},
         "budget": {"context_bytes": 1000}, "profile": {"name": "default"},
         "skill_lock": {"address": "skills.json", "sha256": "c" * 64}}
    c.update(over)
    return c


def t_fresh_packet_carries_every_constraint():
    pkt, problems = M.compile_dispatch_packet({"id": "L-1"}, full_context())
    assert not problems, f"a full context did not compile: {problems}"
    for key in ("requirements", "constraints", "interfaces", "artifacts",
                "base", "scope", "budget", "profile", "skill_lock"):
        assert key in pkt, f"the packet dropped {key}"
    assert pkt["schema_version"] == "dispatch-packet/1"
    assert pkt["leaf_id"] == "L-1"


def t_missing_required_ref_rejects():
    for missing in ("requirements", "interfaces", "base", "skill_lock"):
        ctx = full_context()
        del ctx[missing]
        pkt, problems = M.compile_dispatch_packet({"id": "L-1"}, ctx)
        assert pkt is None and any(missing in p for p in problems), \
            f"a context missing {missing} still compiled"


def t_unbound_ref_rejects():
    ctx = full_context(interfaces=[{"address": "x"}])   # no digest
    pkt, problems = M.compile_dispatch_packet({"id": "L-1"}, ctx)
    assert pkt is None and any("interfaces[0]" in p for p in problems), \
        "an unbound interface ref compiled"


def t_no_ephemeral_secret():
    for leak in ({"profile": {"name": "x", "api_key": "sk-123"}},
                 {"scope": {"edit_targets": [], "auth_token": "t"}},
                 {"base": {"head": "h1", "session_cookie": "c"}}):
        ctx = full_context(**leak)
        pkt, problems = M.compile_dispatch_packet({"id": "L-1"}, ctx)
        assert pkt is None and any("no ephemeral secret" in p for p in problems), \
            f"a secret rode into the packet: {leak}"


def t_cli_verb_and_schema():
    # the named CLI verb runs
    import tempfile
    d = tempfile.mkdtemp()
    lp = os.path.join(d, "leaf.json"); cp = os.path.join(d, "ctx.json")
    json.dump({"id": "L-1"}, open(lp, "w"))
    json.dump(full_context(), open(cp, "w"))
    r = subprocess.run([sys.executable, CP, "compile-dispatch", lp, cp],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"compile-dispatch failed: {r.stderr}"
    assert json.loads(r.stdout)["schema_version"] == "dispatch-packet/1"
    # the schema links a node to the packet
    schema = json.loads(open(SCHEMA, encoding="utf-8").read())
    assert "dispatch_packet" in schema["definitions"]["node"]["properties"], \
        "the node schema does not link to the dispatch packet"


def main():
    case("a fresh packet carries every required constraint",
         t_fresh_packet_carries_every_constraint)
    case("a missing required ref is rejected", t_missing_required_ref_rejects)
    case("an unbound ref is rejected", t_unbound_ref_rejects)
    case("no ephemeral secret compiles in, at any depth", t_no_ephemeral_secret)
    case("the compile-dispatch CLI verb runs; the schema links the packet",
         t_cli_verb_and_schema)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
