#!/usr/bin/env python3
"""FIX-PF-05.03 — the result stores typed outputs, the packet digest and
freshness; credentials ride in neither direction (sherlock audit, PF-05).

The fix under test (execution-result.schema.json + scripts/packet.py +
references/build.md):
* `outputs` are typed (name/kind/address/sha256) and a credential-named
  output is refused by validate-result;
* `packet_digest` ties the answer to the immutable dispatch packet;
* `consumed` pins the predecessor outputs read, and consumed_stale() names
  every result whose input digests moved — a changed predecessor output
  rebuilds the revision;
* the schema declares all three; build.md documents the rule.

Standard library only.
"""
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline")
PK = os.path.join(SKILL, "scripts", "packet.py")
SCHEMA = os.path.join(SKILL, "execution-result.schema.json")
BUILD = os.path.join(SKILL, "references", "build.md")

_spec = importlib.util.spec_from_file_location("packet", PK)
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


def base_env(**over):
    env = {"schema_version": "execution-result/1", "packet_id": "P-1",
           "grant": {"grant_id": "g", "packet_id": "P-1", "holder": "h",
                      "revision": 1, "fence": 1},
           "built_against_revision": 1, "candidate": {"changed": []},
           "checks": [], "evidence": [], "status": "completed"}
    env.update(over)
    return env


def t_typed_outputs_valid():
    env = base_env(outputs=[{"name": "report", "kind": "report",
                              "address": "out/report.md", "sha256": "a" * 64}],
                   packet_digest="b" * 64,
                   consumed=[{"name": "spec", "sha256": "c" * 64}])
    assert M.result_problems(env) == [], "a fully-typed result was refused"


def t_credential_output_refused():
    for name in ("api_token", "client_secret", "SESSION_COOKIE", "db-password"):
        env = base_env(outputs=[{"name": name, "kind": "artifact",
                                  "address": "x", "sha256": "a" * 64}])
        probs = M.result_problems(env)
        assert any("names a credential" in p for p in probs), \
            f"{name!r} rode into the result"


def t_untyped_output_refused():
    env = base_env(outputs=[{"name": "report", "kind": "blob",
                              "address": "x", "sha256": "a" * 64}])
    assert any("kind" in p for p in M.result_problems(env)), \
        "an unknown output kind passed"
    env2 = base_env(outputs=[{"name": "report", "kind": "report", "address": "x",
                               "sha256": "nope"}])
    assert any("sha256" in p for p in M.result_problems(env2))


def t_changed_predecessor_output_is_stale():
    env = base_env(consumed=[{"name": "spec", "sha256": "c" * 64},
                              {"name": "tokens", "sha256": "d" * 64}])
    stale = M.consumed_stale(env, {"spec": "e" * 64, "tokens": "d" * 64})
    assert stale == ["spec"], f"the moved predecessor output was not named: {stale}"
    assert M.consumed_stale(env, {"spec": "c" * 64, "tokens": "d" * 64}) == []
    # a vanished input is stale too
    assert M.consumed_stale(env, {"tokens": "d" * 64}) == ["spec"]


def t_malformed_digest_and_consumed_refused():
    assert any("packet_digest" in p
               for p in M.result_problems(base_env(packet_digest="short")))
    assert any("consumed[0]" in p
               for p in M.result_problems(base_env(consumed=[{"name": "x"}])))


def t_schema_and_doc():
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    props = schema["properties"]
    for key in ("outputs", "packet_digest", "consumed"):
        assert key in props, f"the schema does not declare {key}"
    assert props["outputs"]["items"]["required"] == ["name", "kind", "address", "sha256"]
    with open(BUILD, encoding="utf-8") as fh:
        d = " ".join(fh.read().split())
    assert "The result is typed, tied and comparable." in d
    assert "no credential rides in a result" in d
    assert "rebuild at a new revision" in d


def main():
    case("a fully-typed result validates", t_typed_outputs_valid)
    case("a credential-named output is refused", t_credential_output_refused)
    case("an untyped or unpinned output is refused", t_untyped_output_refused)
    case("a changed (or vanished) predecessor output is stale — rebuild",
         t_changed_predecessor_output_is_stale)
    case("malformed packet_digest / consumed rows are refused",
         t_malformed_digest_and_consumed_refused)
    case("the schema declares the fields; build.md documents the rule",
         t_schema_and_doc)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
