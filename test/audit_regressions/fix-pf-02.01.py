#!/usr/bin/env python3
"""FIX-PF-02.01 — proof identity: close binds the verdict to the tree it tested
and refuses a stale proof (sherlock audit, PF-02).

The finding: a verdict was created for commit v1; then a code commit v2
replaced node.check; `close` exited 0, kept the v1 PASS and merely stamped
"observed at v2". Stamping the current HEAD never verified the reviewer saw
that HEAD; graph revisions recorded only verb/node/why, no version.

The fix under test (graph.py + graph.schema.json), driven in a real git repo:
* the verdict declares `tested` (the commit/tree it ran against);
* inside a checkout close REQUIRES it and COMPARES it to HEAD — an old proof
  after a code change is REJECTED, a current matching proof is accepted;
* the node records a `proof` identity and the close revision carries a
  `precondition` (the proven HEAD).

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


def repo():
    d = tempfile.mkdtemp()
    git(d, "init", "-q")
    git(d, "config", "user.email", "t@t")
    git(d, "config", "user.name", "t")
    (os.path.join(d, ".task-pipeline"))
    g = {"goal": "ship", "requirements": ["REQ-001"],
         "nodes": [{"id": "N-001", "title": "t", "owner": "implementer",
                    "status": "pending", "serves": "REQ-001", "check": "true"}],
         "edges": []}
    gp = os.path.join(d, "graph.json")
    with open(gp, "w") as fh:
        json.dump(g, fh)
    with open(os.path.join(d, "code.txt"), "w") as fh:
        fh.write("v1\n")
    git(d, "add", "-A")
    git(d, "commit", "-qm", "v1")
    return d, gp


def head(d):
    return git(d, "rev-parse", "HEAD").stdout.strip()


def run_close(d, gp, verdict):
    vp = os.path.join(d, "verdict.json")
    with open(vp, "w") as fh:
        json.dump(verdict, fh)
    return subprocess.run([sys.executable, GRAPH, "close", "--graph", gp, "--verdict", vp],
                          capture_output=True, text=True, cwd=d)


def base_verdict(**over):
    v = {"node": "N-001", "done": ["built"], "not_done": [], "not_verified": [],
         "blockers": [], "replan": {"possible": True, "add": [], "park": [], "why": ""},
         "evidence": ["npm test → PASS"]}
    v.update(over)
    return v


def t_current_matching_proof_is_accepted():
    d, gp = repo()
    v = base_verdict(tested={"head": head(d)})
    r = run_close(d, gp, v)
    assert r.returncode == 0, f"a proof tested at HEAD was refused: {r.stderr}"
    node = json.loads(open(gp).read())["nodes"][0]
    assert node["status"] == "done"
    assert node.get("proof", {}).get("head") == head(d), "the node did not record the proven head"
    assert any("proven at" in e for e in node["evidence"]), "the evidence is not a proof stamp"
    revs = json.loads(open(gp).read()).get("revisions", [])
    close_rev = [x for x in revs if x["verb"] == "close"][-1]
    assert close_rev.get("precondition") == head(d), "the close revision carries no precondition"


def t_stale_proof_after_code_change_is_rejected():
    d, gp = repo()
    v1 = head(d)
    # code moves to v2
    with open(os.path.join(d, "code.txt"), "w") as fh:
        fh.write("v2\n")
    git(d, "commit", "-aqm", "v2")
    assert head(d) != v1
    # a verdict earned at v1 must NOT close a tree now at v2
    r = run_close(d, gp, base_verdict(tested={"head": v1}))
    assert r.returncode != 0, "a stale v1 proof closed a v2 tree — the finding itself"
    assert "moved under the proof" in r.stderr, r.stderr
    node = json.loads(open(gp).read())["nodes"][0]
    assert node["status"] == "pending", "the node was closed despite the stale proof"


def t_missing_tested_in_a_checkout_is_rejected():
    d, gp = repo()
    r = run_close(d, gp, base_verdict())  # no `tested`
    assert r.returncode != 0, "a verdict with no tested identity closed inside a checkout"
    assert "declares no `tested.head`" in r.stderr, r.stderr


def t_tree_mismatch_same_commit_is_rejected():
    d, gp = repo()
    v = base_verdict(tested={"head": head(d), "tree": "deadbeef" * 5})
    r = run_close(d, gp, v)
    assert r.returncode != 0, "a matching commit with a wrong tree was accepted"
    assert "tree" in r.stderr and "moved under the proof" in r.stderr


def main():
    case("a current matching proof is accepted and recorded",
         t_current_matching_proof_is_accepted)
    case("a stale proof after a code change is rejected",
         t_stale_proof_after_code_change_is_rejected)
    case("a verdict with no tested identity is rejected inside a checkout",
         t_missing_tested_in_a_checkout_is_rejected)
    case("a tree mismatch under a matching commit is rejected",
         t_tree_mismatch_same_commit_is_rejected)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
