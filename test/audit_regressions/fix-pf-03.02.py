#!/usr/bin/env python3
"""FIX-PF-03.02 — an authorized exception is its own disposition, and reviewer
exposure is honest (sherlock audit, PF-03).

After PF-03.01 blocked the direct close over a failed certification, the only
ways past a legitimate exception were a fake PASS tier report or a hand edit —
and a syntax lint could be recorded as a blind-review tier.

The fix under test (graph.py):
* `waive --node --reason --by` records {reason, by, at} as node.exception —
  refusing an empty reason or a missing identity;
* close over a FAILED certification is still refused WITHOUT an exception, and
  with one it closes while stamping the exception (by + reason + the still-
  failing tiers) into the evidence — the node is never marked certified;
* certify refuses a tier report whose exposure is a lint ("a syntax lint is
  not a blind review").

Standard library only (git via subprocess).
"""
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GRAPH = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline",
                     "scripts", "graph.py")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def git(d, *a):
    return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True)


def repo(cert=None):
    d = tempfile.mkdtemp()
    git(d, "init", "-q"); git(d, "config", "user.email", "t@t"); git(d, "config", "user.name", "t")
    open(os.path.join(d, "c.txt"), "w").write("v1\n")
    git(d, "add", "-A"); git(d, "commit", "-qm", "v1")
    head = git(d, "rev-parse", "HEAD").stdout.strip()
    node = {"id": "N-001", "title": "t", "owner": "implementer", "status": "pending",
            "serves": "REQ-001", "check": "true"}
    if cert:
        c = dict(cert)
        if c.get("at") == "<HEAD>":
            c["at"] = head
        node["certification"] = c
    g = {"goal": "ship", "requirements": ["REQ-001"], "nodes": [node], "edges": []}
    gp = os.path.join(d, "graph.json")
    json.dump(g, open(gp, "w"))
    return d, gp, head


def run(d, gp, *argv):
    return subprocess.run([sys.executable, GRAPH, *argv, "--graph", gp],
                          capture_output=True, text=True, cwd=d)


def close(d, gp, head):
    v = {"node": "N-001", "done": ["built"], "not_done": [], "not_verified": [],
         "blockers": [], "replan": {"possible": True, "add": [], "park": [], "why": ""},
         "evidence": ["npm test → PASS"], "tested": {"head": head}}
    vp = os.path.join(d, "verdict.json")
    json.dump(v, open(vp, "w"))
    return subprocess.run([sys.executable, GRAPH, "close", "--graph", gp, "--verdict", vp],
                          capture_output=True, text=True, cwd=d)


FAILED_CERT = {"round": 1, "at": "<HEAD>",
               "tiers": {"unit": "fail", "seam": "pass", "product": "pass"}, "history": []}


def t_waive_records_reason_and_identity():
    d, gp, _ = repo()
    r = run(d, gp, "waive", "--node", "N-001", "--reason", "vendor hotfix window",
            "--by", "operator:sshlg")
    assert r.returncode == 0, r.stderr
    node = json.loads(open(gp).read())["nodes"][0]
    assert node["exception"]["by"] == "operator:sshlg"
    assert node["exception"]["reason"] == "vendor hotfix window"
    bad = run(d, gp, "waive", "--node", "N-001", "--reason", "  ", "--by", "x")
    assert bad.returncode != 0, "an empty reason was accepted"


def t_failed_cert_still_blocks_without_exception():
    d, gp, head = repo(FAILED_CERT)
    r = close(d, gp, head)
    assert r.returncode != 0 and "AUTHORIZED EXCEPTION" in r.stderr, \
        "the refusal no longer names the waive path"


def t_exception_closes_but_never_certifies():
    d, gp, head = repo(FAILED_CERT)
    run(d, gp, "waive", "--node", "N-001", "--reason", "ship the hotfix", "--by", "operator:sshlg")
    r = close(d, gp, head)
    assert r.returncode == 0, f"an authorized exception did not permit the close: {r.stderr}"
    node = json.loads(open(gp).read())["nodes"][0]
    assert node["status"] == "done"
    stamp = " ".join(node["evidence"])
    assert "authorized exception by operator:sshlg" in stamp, "the exception is not in the evidence"
    assert "unit still failing" in stamp or "unit" in stamp, "the failing tier vanished"
    assert node["certification"]["tiers"]["unit"] == "fail", \
        "the failed certification was rewritten — a fake PASS"


def t_lint_exposure_is_not_a_blind_review():
    d, gp, _ = repo()
    tier = {"node": "N-001", "tier": "unit", "verdict": "pass", "scope": ["c.txt"],
            "confirms": ["ok"], "findings": [], "evidence": ["ran x"],
            "not_examined": [], "exposure": "syntax-only lint over the diff"}
    paths = []
    for name in ("unit", "seam", "product"):
        tp = os.path.join(d, f"{name}.json")
        t2 = dict(tier, tier=name)
        json.dump(t2, open(tp, "w"))
        paths.append(tp)
    r = subprocess.run([sys.executable, GRAPH, "certify", "--graph", gp, "--node", "N-001",
                        "--tier", paths[0], "--tier", paths[1], "--tier", paths[2]],
                       capture_output=True, text=True, cwd=d)
    assert r.returncode != 0, "a lint-exposure tier was certified as a blind review"
    assert "syntax lint is not a blind review" in (r.stdout + r.stderr), r.stderr


def main():
    case("waive records reason + identity, refuses empties",
         t_waive_records_reason_and_identity)
    case("a failed certification still blocks without an exception",
         t_failed_cert_still_blocks_without_exception)
    case("an exception closes with the stamp — and never certifies",
         t_exception_closes_but_never_certifies)
    case("a lint exposure is refused as a blind review",
         t_lint_exposure_is_not_a_blind_review)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
