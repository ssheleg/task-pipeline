#!/usr/bin/env python3
"""The browser-claims validator (PXS-05.01) — stdlib only.

Validates a filled copy of `templates/browser-claims.json` against the rules
browser.md states in prose: a claim names its REQ/scenario, its STATE and its
KIND (look / suite / library — the existing split); a PASS needs its artifact
present AND captured in the claim's own state; a functional (suite) PASS never
closes a visual (look) claim; a toggle component owes the full cycle; no
browser channel is NOT_RUN with a reason.

Since v1.89.0 the same file is the CONTACT SHEET of the visual look: a look row
carrying `axes` is one frame of the state × axes matrix, with its capture record,
its diff against the Figma frame or the approved baseline, and its rubric items.
The fixtures below plant each way a sheet lies and require the shipped validator
(`scripts/visual_gate.py sheet`) to refuse it.

Run bare, it validates the shipped template (whose rows are honest NOT_RUNs)
and its own fixtures. Import it to validate a real file:
    from browser_claims_test import claim_problems, toggle_cycle_gaps
"""
import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKILL = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline")
TEMPLATE = os.path.join(SKILL, "templates", "browser-claims.json")
VISUAL_GATE = os.path.join(SKILL, "scripts", "visual_gate.py")

# The rules live in the SHIPPED script, so a host project runs the same ones this suite
# tests. They lived here until v1.89.0, in a file that never leaves this repository, while
# browser.md told every host to run it. Re-exported under the old names, which the PXS-05.01
# regression imports.
_spec = importlib.util.spec_from_file_location("visual_gate", VISUAL_GATE)
VG = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(VG)
claim_problems = VG.claim_problems
toggle_cycle_gaps = VG.toggle_cycle_gaps
suite_pass_closes_no_look = VG.suite_pass_closes_no_look
sheet_report = VG.sheet_report


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

    contact_sheet_cases(tpl)

    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


# --- the contact sheet: the visual look over the state × axes matrix ----------

REV = "4dbb96cbba70"


def good_sheet(root):
    """The template's visual rows, captured: every frame PASS, on disk, in its state."""
    with open(TEMPLATE, encoding="utf-8") as fh:
        doc = json.load(fh)
    doc["revision"] = REV
    for c in doc["claims"]:
        if "axes" not in c:
            continue
        c["status"] = "PASS"
        c.pop("reason", None)
        c["capture"] = dict(c["capture"], revision=REV)
        if c.get("figma_frame"):
            c["diff"] = {"against": "figma", "status": "PASS", "ratio": 0.004,
                         "threshold": 0.01}
        c["rubric"] = [{"id": "R1", "type": "G", "status": "PASS"},
                       {"id": "R7", "type": "J", "status": "NOT_ASSESSED"}]
        path = os.path.join(root, c["artifact"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "wb").close()
    return doc


def vrow(doc, cid):
    return next(c for c in doc["claims"] if c["id"] == cid)


def refused(doc, cls, needle, root=None, **kw):
    verdict, problems, _ = sheet_report(doc, cls, root, **kw)
    return verdict == "FAIL" and any(needle in p for p in problems), (verdict, problems)


def contact_sheet_cases(tpl):
    root = tempfile.mkdtemp()
    base = good_sheet(root)

    def fresh():
        return copy.deepcopy(base)

    v, p, n = sheet_report(tpl, "flagship")
    case("the shipped template is an honest contact sheet: NOT_RUN, never PASS",
         v == "NOT_RUN" and p == [], (v, p))
    v, p, n = sheet_report(base, "flagship", root)
    case("a captured, compared, pairwise-covered sheet passes at flagship",
         v == "PASS" and p == [], (v, p, n))

    d = fresh(); del vrow(d, "BC-06")["axes"]["text"]
    ok, why = refused(d, "flagship", "axes.text is missing", root)
    case("a frame whose text axis nobody recorded is refused", ok, why)

    d = fresh(); del vrow(d, "BC-05")["capture"]
    ok, why = refused(d, "product", "capture record", root)
    case("a PASS frame with no capture record is refused", ok, why)

    d = fresh(); vrow(d, "BC-05")["capture"]["revision"] = "0000000older"
    ok, why = refused(d, "product", "stale frame", root)
    case("a frame captured at another revision is refused as stale", ok, why)

    d = fresh(); vrow(d, "BC-05")["diff"] = None
    ok, why = refused(d, "product", "no `diff`", root)
    case("a frame with a Figma reference and no diff is refused", ok, why)

    d = fresh(); vrow(d, "BC-05")["diff"]["status"] = "FAIL"
    ok, why = refused(d, "product", "failing diff", root)
    case("PASS over a failing diff is refused — only a person approves a new baseline",
         ok, why)

    d = fresh(); vrow(d, "BC-05")["rubric"][0].update(
        status="FAIL", triple={"region": "hero", "defect": "contrast 2.9:1",
                               "fix": "use --sem-fg-strong"})
    ok, why = refused(d, "flagship", "never overrides", root)
    case("a PASS frame carrying a gate-item FAIL is refused — the judge is below the floor",
         ok, why)

    d = fresh(); vrow(d, "BC-05")["rubric"][1]["status"] = "PASS"
    ok, why = refused(d, "flagship", "NOT_ASSESSED", root)
    case("a judge item reported PASS with no calibration is refused", ok, why)
    vrow(d, "BC-05")["rubric"][1]["calibration"] = "labelled set L-01, 24 screens, agreement 0.81"
    v, p, _ = sheet_report(d, "flagship", root)
    case("the same judge item with its calibration is accepted", v == "PASS", (v, p))

    d = fresh(); vrow(d, "BC-05")["rubric"].append({"id": "R9", "type": "J", "status": "FAIL",
                                                    "calibration": "L-01"})
    ok, why = refused(d, "flagship", "without its triple", root)
    case("a FAIL with no region → defect → fix triple is refused", ok, why)

    d = fresh()
    for i, cid in enumerate(("BC-05", "BC-06", "BC-07")):
        vrow(d, cid)["rubric"].append({"id": "R%d" % (20 + i), "type": "J", "status": "FAIL",
                                       "calibration": "L-01",
                                       "triple": {"region": "r", "defect": "d", "fix": "f"}})
    ok, why = refused(d, "flagship", "at most two", root)
    case("a flagship sheet with three judge FAILs is over the profile's threshold", ok, why)

    d = fresh(); vrow(d, "BC-05")["rubric"].append({"id": "R2", "type": "H", "status": "PASS"})
    ok, why = refused(d, "flagship", "nobody approved", root)
    case("a human item reported PASS on an unapproved sheet is refused", ok, why)

    d = fresh(); del d["review_rounds"]
    ok, why = refused(d, "product", "review_rounds", root)
    case("a sheet that cannot say how many returns it took is refused", ok, why)

    d = fresh()
    ok, why = refused(d, "flagship", "not approved", root, require_approval=True)
    case("at acceptance an unapproved sheet is refused", ok, why)
    d.update(approved_by="the operator", approved_at="2026-10-07T12:00:00Z")
    v, p, _ = sheet_report(d, "flagship", root, require_approval=True)
    case("the approved sheet passes at acceptance", v == "PASS", (v, p))
    d["approved_at"] = "yesterday"
    ok, why = refused(d, "flagship", "half an approval", root, require_approval=True)
    case("an approval with no parseable time is half an approval", ok, why)

    d = fresh()
    d["claims"] = [c for c in d["claims"] if c["id"] not in ("BC-06", "BC-09")]
    ok, why = refused(d, "product", "dark × large text", root)
    case("dark × large text is a mandatory pair even on a product surface", ok, why)
    v, p, n = sheet_report(d, "internal", root)
    case("on an internal surface the same hole is reported, not gated",
         v == "PASS" and any("dark × large text" in x for x in n), (v, p, n))

    d = fresh(); vrow(d, "BC-06")["axes"]["viewport"] = "1280x800"
    ok, why = refused(d, "product", "RTL × narrow", root)
    case("RTL with no narrow frame misses a mandatory pair", ok, why)

    d = fresh(); vrow(d, "BC-08")["axes"]["locale"] = "en"
    v, p, n = sheet_report(d, "product", root)
    case("a pairwise hole is a note on a product surface",
         v == "PASS" and any(x.startswith("pairwise:") for x in n), (v, p, n))
    ok, why = refused(d, "flagship", "pairwise:", root)
    case("the same pairwise hole fails a flagship surface", ok, why)

    ok, why = refused(fresh(), "flagship", "has no frame", root,
                      states=["SCR-01/default", "SCR-01/offline"])
    case("a state the brief names with no frame is a hole in the matrix", ok, why)

    d = fresh(); d["claims"] = [c for c in d["claims"] if "axes" not in c]
    ok, why = refused(d, "flagship", "did not run", root)
    case("a flagship surface whose sheet has no visual row is refused", ok, why)
    v, _, _ = sheet_report(d, "internal", root)
    case("an internal surface may close on the functional look alone", v == "PASS", v)

    d = fresh(); vrow(d, "BC-07").update(status="NOT_RUN", reason="no browser channel")
    v, p, _ = sheet_report(d, "flagship", root)
    case("one frame that did not run makes the verdict NOT_RUN, never PASS",
         v == "NOT_RUN" and p == [], (v, p))

    # The command a host runs, by its exit code: PASS 0 · FAIL 1 · usage 2 · NOT_RUN 3.
    def run(doc, *args):
        f = os.path.join(root, "sheet.json")
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(doc, fh)
        return subprocess.run([sys.executable, VISUAL_GATE, "sheet", f, *args],
                              capture_output=True, text=True).returncode

    bad = fresh(); vrow(bad, "BC-05")["diff"]["status"] = "FAIL"
    codes = (run(fresh(), "--class", "flagship", "--artifact-root", root),
             run(bad, "--class", "flagship", "--artifact-root", root),
             run(tpl, "--class", "flagship"),
             subprocess.run([sys.executable, VISUAL_GATE, "sheet",
                             os.path.join(root, "absent.json"), "--class", "product"],
                            capture_output=True, text=True).returncode)
    case("the sheet command exits 0 · 1 · 3 · 2 for pass · fail · not run · unreadable",
         codes == (0, 1, 3, 2), codes)


if __name__ == "__main__":
    sys.exit(main())
