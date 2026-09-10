#!/usr/bin/env python3
"""The browser-claims validator (PXS-05.01) — stdlib only.

Validates a filled copy of `templates/browser-claims.json` against the rules
browser.md states in prose: a claim names its REQ/scenario, its STATE and its
KIND (look / suite / library — the existing split); a PASS needs its artifact
present AND captured in the claim's own state; a functional (suite) PASS never
closes a visual (look) claim; a toggle component owes the full cycle; no
browser channel is NOT_RUN with a reason.

Run bare, it validates the shipped template (whose rows are honest NOT_RUNs)
and its own fixtures. Import it to validate a real file:
    from browser_claims_test import claim_problems, toggle_cycle_gaps
"""
import json
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEMPLATE = os.path.join(ROOT, "plugins", "task-pipeline", "skills",
                        "task-pipeline", "templates", "browser-claims.json")

KINDS = {"look", "suite", "library"}
STATUSES = {"PASS", "FAIL", "NOT_RUN", "BLOCKED"}


def claim_problems(claim, artifact_root=None):
    """Every reason this claim must not be believed. Empty list = valid."""
    out = []
    for field in ("id", "req", "scenario", "state", "kind", "status"):
        if not claim.get(field):
            out.append(f"{claim.get('id', '?')}: {field} missing")
    if claim.get("kind") not in KINDS:
        out.append(f"{claim.get('id', '?')}: kind {claim.get('kind')!r} is not one of "
                   f"{sorted(KINDS)} — the look/suite/library split is the contract")
    if claim.get("status") not in STATUSES:
        out.append(f"{claim.get('id', '?')}: status {claim.get('status')!r} unknown")
    if claim.get("status") == "NOT_RUN" and not claim.get("reason"):
        out.append(f"{claim.get('id', '?')}: NOT_RUN carries its reason, always")
    if claim.get("status") == "PASS" and claim.get("kind") == "look":
        if not claim.get("artifact"):
            out.append(f"{claim['id']}: a visual PASS with no artifact is a functional "
                       "claim wearing a visual verdict")
        else:
            if artifact_root is not None and \
                    not os.path.isfile(os.path.join(artifact_root, claim["artifact"])):
                out.append(f"{claim['id']}: artifact {claim['artifact']} does not exist "
                           "— a named file that is not there proves nothing")
            if claim.get("artifact_state") != claim.get("state"):
                out.append(f"{claim['id']}: artifact captured in state "
                           f"{claim.get('artifact_state')!r} cannot close a claim about "
                           f"{claim.get('state')!r} — the initial screenshot does not "
                           "close an opened/error state")
    return out


def toggle_cycle_gaps(claims, component):
    """Which of the full cycle's states the component's PASSing look claims miss."""
    need = {"initial", "opened", "closed-again"}
    have = {c["state"] for c in claims
            if c.get("component") == component and c.get("kind") == "look"
            and c.get("status") == "PASS"}
    return sorted(need - have)


def suite_pass_closes_no_look(claims):
    """Look claims that would be wrongly closed by a suite PASS: none may be."""
    suite_green = any(c.get("kind") == "suite" and c.get("status") == "PASS"
                      for c in claims)
    if not suite_green:
        return []
    return [c["id"] for c in claims
            if c.get("kind") == "look" and c.get("status") == "PASS"
            and not c.get("artifact")]


failures = []


def case(name, ok, detail=""):
    if ok:
        print(f"  ok  {name}")
    else:
        failures.append(name)
        print(f"FAIL  {name}: {detail}")


def main():
    with open(TEMPLATE, encoding="utf-8") as fh:
        tpl = json.load(fh)
    probs = [p for c in tpl["claims"] for p in claim_problems(c)]
    case("the shipped template validates (honest NOT_RUNs)", probs == [], str(probs))

    # fixtures — the three failure shapes the packet names
    missing = dict(tpl["claims"][1], status="PASS", artifact=None)
    case("a visual PASS with no artifact is refused",
         any("wearing a visual verdict" in p for p in claim_problems(missing)))

    wrong_state = dict(tpl["claims"][1], status="PASS",
                       artifact="shots/nav-menu-initial.png",
                       artifact_state="initial")
    case("an initial-state screenshot cannot close the opened claim",
         any("cannot close a claim" in p for p in claim_problems(wrong_state)))

    import tempfile
    d = tempfile.mkdtemp()
    ghost = dict(tpl["claims"][1], status="PASS")
    case("a named-but-absent artifact is refused",
         any("does not exist" in p for p in claim_problems(ghost, artifact_root=d)))

    cycle = [dict(c, status="PASS") for c in tpl["claims"][:2]]   # initial+opened only
    case("an incomplete toggle cycle names the missing state",
         toggle_cycle_gaps(cycle, "nav-menu") == ["closed-again"])

    full = [dict(c, status="PASS") for c in tpl["claims"][:3]]
    case("the full cycle passes", toggle_cycle_gaps(full, "nav-menu") == [])

    leak = [{"id": "S", "kind": "suite", "status": "PASS"},
            {"id": "V", "kind": "look", "status": "PASS", "artifact": None}]
    case("a suite PASS does not close an artifactless look claim",
         suite_pass_closes_no_look(leak) == ["V"])

    no_channel = {"id": "BC-9", "req": "R", "scenario": "S", "state": "opened",
                  "kind": "look", "status": "NOT_RUN"}
    case("NOT_RUN without a reason is refused",
         any("its reason" in p for p in claim_problems(no_channel)))

    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
