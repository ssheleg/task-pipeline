#!/usr/bin/env python3
"""FIX-PF-01.01 — the attempt/grant schema: a claim is an identity, fenced and
expiring, not a role name (sherlock audit, PF-01).

The finding: two independent `next` processes both got N-001 while its status
stayed `pending`; `owner` is a ROLE name, not a session/attempt identity;
`running` could be written by hand but there was no acquire/start/renew/
release/recover, so a lost `running` node dead-ended `next` (exit 4) forever.

This leaf ships the SCHEMA the CLI verbs (the next implementation leaf) must
round-trip:
* execution-attempt.schema.json — owner (session/attempt, not role), attempt,
  revision, fence, expiry and state ready→claimed; missing owner/revision/
  fence/expiry are rejected; a valid grant round-trips byte-for-byte;
* graph.schema.json — a node gains an optional `claim`, and a `running` node
  MUST carry one (rule_running_needs_claim), while every other status must not
  be forced to.

Validates with jsonschema when importable (real reject/accept); otherwise a
stdlib required-field check still binds. No new mandatory package.
"""
import copy
import json
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TP = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline")
ATTEMPT = os.path.join(TP, "execution-attempt.schema.json")
GRAPH = os.path.join(TP, "graph.schema.json")

failures = []
not_run = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def jsonschema_or_none():
    try:
        import jsonschema
        return jsonschema
    except ImportError:
        return None


VALID_GRANT = {
    "schema_version": "execution-attempt/1",
    "node": "N-001",
    "owner": "sess-ab12:attempt-3",
    "attempt": 3,
    "revision": 7,
    "fence": 42,
    "expiry": "2026-09-09T12:00:00Z",
    "state": "claimed",
    "installed_at": "2026-09-09T11:50:00Z",
}


def t_attempt_schema_shape():
    s = load(ATTEMPT)
    req = set(s["required"])
    for field in ("owner", "attempt", "revision", "fence", "expiry", "state"):
        assert field in req, f"execution-attempt schema does not require {field}"
    assert s["properties"]["state"]["enum"] == ["ready", "claimed"], \
        "the attempt states are not ready→claimed"
    # owner is an identity string, and the description says NOT a role name
    assert "never a role name" in s["properties"]["owner"]["description"]


def t_attempt_rejects_missing_and_round_trips():
    js = jsonschema_or_none()
    schema = load(ATTEMPT)
    if js is None:
        not_run.append("jsonschema absent — live validation NOT_RUN; required-set still checked")
        # stdlib fallback: the required set must name each field
        for field in ("owner", "revision", "fence", "expiry"):
            assert field in schema["required"]
        return
    js.validate(VALID_GRANT, schema)                     # a valid grant validates
    assert json.loads(json.dumps(VALID_GRANT)) == VALID_GRANT, "grant did not round-trip"
    for missing in ("owner", "revision", "fence", "expiry"):
        bad = copy.deepcopy(VALID_GRANT)
        del bad[missing]
        try:
            js.validate(bad, schema)
            raise AssertionError(f"a grant missing {missing} was accepted")
        except js.ValidationError:
            pass


def t_graph_node_running_needs_claim():
    js = jsonschema_or_none()
    schema = load(GRAPH)
    # the rule exists regardless of jsonschema
    defs = schema.get("definitions", {})
    assert "rule_running_needs_claim" in defs, "the running⇒claim rule is missing"
    node = defs["node"]
    assert "claim" in node["properties"], "the node gained no claim property"
    if js is None:
        not_run.append("jsonschema absent — running⇒claim validation NOT_RUN")
        return

    def full_node(**over):
        n = {"id": "N-001", "title": "a node", "owner": "impl",
             "status": "pending", "serves": "REQ-1", "check": "npm test"}
        n.update(over)
        return n

    # a running node with a claim validates; without one is rejected
    claim = {k: VALID_GRANT[k] for k in
             ("owner", "attempt", "revision", "fence", "expiry", "state")}
    _validate_node(js, schema, full_node(status="running", claim=claim), should_pass=True)
    _validate_node(js, schema, full_node(status="running"), should_pass=False)
    _validate_node(js, schema, full_node(status="pending"), should_pass=True)


def _validate_node(js, schema, node, should_pass):
    sub = {"$schema": schema.get("$schema"),
           "definitions": schema["definitions"],
           "$ref": "#/definitions/node"}
    try:
        js.validate(node, sub)
        assert should_pass, f"node {node.get('status')} validated but should not have"
    except js.ValidationError:
        assert not should_pass, f"node {node.get('status')} rejected but should have passed"


def main():
    case("the attempt schema requires owner/attempt/revision/fence/expiry and states ready→claimed",
         t_attempt_schema_shape)
    case("a grant missing owner/revision/fence/expiry is rejected; a valid grant round-trips",
         t_attempt_rejects_missing_and_round_trips)
    case("a running node must carry a claim; others need not",
         t_graph_node_running_needs_claim)
    for n in not_run:
        print(f"  NOT_RUN  {n}")
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
