#!/usr/bin/env python3
"""design_gate.py and resource_guard.py (1.100.0): the design review as a gate, and the
machine it borrows. Every refusal is planted and must fail; every pass is a real fixture.
Standard library only."""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "plugins/task-pipeline/skills/task-pipeline"
DG = SK / "scripts/design_gate.py"
RG = SK / "scripts/resource_guard.py"
count, failures = 0, []


def ok(cond, msg):
    global count
    count += 1
    if not cond:
        failures.append(msg)
        print("FAIL  " + msg)


def run(script, *args):
    r = subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def portrait(n, scenarios="SCR-01, SCR-02", basis="hypothesis", segment=None):
    segment = segment or ("local" if n % 2 else "tourist")
    return f"""## P-{n:02d} Persona {n}

- **basis**: {basis}
- **situation**: on a phone between meetings
- **goals**: finish a task in under a minute
- **features**: search, checkout
- **scenarios**: {scenarios}
- **activation**: sign up, first order; drops at the payment step
- **retention**: {segment}: weekly reminder, reorder, saved cart brings them back
- **needs**: iOS Safari, large text
"""


def panel_text(n=10, **kw):
    return "# Test panel\n\n" + "\n".join(portrait(i, **kw) for i in range(1, n + 1))


CHECKS_OK = {c: "pass" for c in ("frame", "primary_action", "controls", "focus", "states", "text_fit", "outcome")}


def row(scn, persona, kind, **kw):
    r = {"scenario": scn, "step": 1, "persona": persona, "pass": kind, "round": 1,
         "checks": dict(CHECKS_OK), "findings": []}
    if kind == "design":
        r["frame"] = "figma:12:34"
    else:
        r.update(capture="frames/s1.png", engine="webkit", outcome="order created")
    r.update(kw)
    return r


def report(rows, resources=None):
    return {"schema": "design-review/1", "surface": "checkout", "panel_revision": "abc1234",
            "rows": rows, "resources": resources if resources is not None else {"started": [], "live": [], "closed": True}}


def full_rows(kind_set=("design", "build"), scenarios=("SCR-01",)):
    return [row(s, f"P-{i:02d}", k) for s in scenarios for i in range(1, 11) for k in kind_set]


with tempfile.TemporaryDirectory() as d:
    d = pathlib.Path(d)
    panel = d / "test-panel.md"
    panel.write_text(panel_text())
    rc, out, _ = run(DG, "panel", panel)
    ok(rc == 0 and "10 portrait" in out, f"a ten-portrait panel passes ({rc} {out!r})")
    panel9 = d / "nine.md"
    panel9.write_text(panel_text(9))
    rc, out, _ = run(DG, "panel", panel9)
    ok(rc == 1 and "owes 10" in out, f"nine portraits fail ({rc} {out!r})")
    nobasis = d / "nobasis.md"
    nobasis.write_text(panel_text().replace("- **basis**: hypothesis\n", "", 1))
    rc, out, _ = run(DG, "panel", nobasis)
    ok(rc == 1 and "P-01: no **basis** line" in out, f"a portrait without its basis fails ({rc} {out!r})")
    badbasis = d / "badbasis.md"
    badbasis.write_text(panel_text().replace("hypothesis", "a hunch", 1))
    rc, out, _ = run(DG, "panel", badbasis)
    ok(rc == 1 and "basis is" in out, f"a basis that is neither evidence nor hypothesis fails ({rc} {out!r})")
    noscr = d / "noscr.md"
    noscr.write_text(panel_text().replace("SCR-01, SCR-02", "checkout flow", 1))
    rc, out, _ = run(DG, "panel", noscr)
    ok(rc == 1 and "cite no SCR- id" in out, f"composite scenarios without SCR ids fail ({rc} {out!r})")
    # 1.101.0 (M2 R3): at least two locals and two tourists among the portraits.
    one_tourist = d / "one-tourist.md"
    one_tourist.write_text("# Test panel\n\n" + "\n".join(portrait(i, segment="tourist" if i == 1 else "local") for i in range(1, 11)))
    rc, out, _ = run(DG, "panel", one_tourist)
    ok(rc == 1 and "9 locals and 1 tourist" in out, f"a panel with one tourist fails, counted ({rc} {out!r})")
    unmarked = d / "unmarked.md"
    unmarked.write_text(panel_text().replace("local: ", "").replace("tourist: ", ""))
    rc, out, _ = run(DG, "panel", unmarked)
    ok(rc == 1 and "opens with `local` or `tourist`" in out, f"a retention line without its segment fails, named ({rc} {out!r})")
    rc, out, _ = run(DG, "panel", d / "absent.md")
    ok(rc == 3 and "NOT_RUN" in out, f"no panel is NOT_RUN, never PASS ({rc} {out!r})")

    def rep(doc, *extra, cls="product"):
        p = d / "r.json"
        p.write_text(json.dumps(doc))
        return run(DG, "report", p, "--class", cls, "--panel", panel, "--scope", "SCR-01", *extra)

    rc, out, _ = rep(report(full_rows()), "--require", "build")
    ok(rc == 0 and "PASS" in out, f"a full matrix, clean, closed: PASS ({rc} {out!r})")

    # 1.101.0 (M2 G8, R2): a subscription surface owes cancel parity and one clear offer.
    SUB_OK = {"cancel_parity": "pass", "subscribe_steps": 3, "cancel_steps": 2,
              "cancel_path": "Settings > Subscription > Cancel", "single_offer": "pass", "pause": "offered"}

    def subrep(sub, *extra, cls="product"):
        doc = report(full_rows())
        if sub is not None:
            doc["subscription"] = sub
        return rep(doc, "--require", "build", *extra, cls=cls)

    rc, out, _ = subrep(None, "--subscription")
    ok(rc == 1 and "cancel parity" in out, f"a subscription surface without its cancel-parity block fails ({rc} {out!r})")
    rc, out, _ = subrep(dict(SUB_OK), "--subscription")
    ok(rc == 0 and "PASS" in out, f"cancel no harder than subscribe, one offer: PASS ({rc} {out!r})")
    rc, out, _ = subrep(dict(SUB_OK))
    ok(rc == 0, f"a report that carries the block is checked without the flag ({rc} {out!r})")
    rc, out, _ = subrep(dict(SUB_OK, cancel_parity="fail", cancel_steps=6))
    ok(rc == 1 and "6 steps" in out and "3 to subscribe" in out, f"cancelling in more steps than subscribing fails, counted ({rc} {out!r})")
    rc, out, _ = subrep(dict(SUB_OK, cancel_steps=5))
    ok(rc == 1 and "contradicts" in out, f"a `pass` over a longer cancel path is refused ({rc} {out!r})")
    rc, out, _ = subrep(dict(SUB_OK, subscribe_steps=0))
    ok(rc == 1 and "subscribe_steps" in out, f"a step count is a positive integer ({rc} {out!r})")
    rc, out, _ = subrep(dict(SUB_OK, cancel_parity="yes"))
    ok(rc == 1 and "cancel_parity" in out, f"an unknown parity value is refused, never read as pass ({rc} {out!r})")
    rc, out, _ = subrep(dict(SUB_OK, single_offer="fail"))
    ok(rc == 1 and "single clear offer" in out, f"a paywall without one clear offer fails ({rc} {out!r})")
    rc, out, _ = subrep(dict(SUB_OK, cancel_parity="NOT_RUN"))
    ok(rc == 1 and "reason" in out, f"a NOT_RUN parity carries its reason ({rc} {out!r})")
    rc, out, _ = subrep(dict(SUB_OK, cancel_parity="NOT_RUN", reason="no test account can subscribe"))
    ok(rc == 3 and "NOT_RUN" in out, f"parity never walked is NOT_RUN, never PASS ({rc} {out!r})")
    rc, out, _ = subrep(dict(SUB_OK, pause="absent"))
    ok(rc == 0 and "no pause" in out, f"a missing pause is reported, not gated ({rc} {out!r})")
    rc, out, _ = subrep(dict(SUB_OK, pause="maybe"))
    ok(rc == 1 and "pause" in out, f"pause is offered, absent or na ({rc} {out!r})")
    rc, out, _ = subrep(None, "--subscription", cls="internal")
    ok(rc == 0 and "cancel parity" in out, f"an internal class reports the gap without gating ({rc} {out!r})")
    rc, out, _ = subrep("yes")
    ok(rc == 1 and "`subscription` is an object" in out, f"a non-object block is refused ({rc} {out!r})")
    rc, out, _ = rep(report(full_rows(("design",))), "--require", "design")
    ok(rc == 0, f"pass D alone satisfies --require design ({rc} {out!r})")
    rc, out, _ = rep(report(full_rows(("design",))), "--require", "build")
    ok(rc == 1 and "no build pass" in out, f"stage 6 without pass B fails ({rc} {out!r})")
    missing = full_rows()[:-2]
    rc, out, _ = rep(report(missing), "--require", "build")
    ok(rc == 1 and "SCR-01 × P-10" in out, f"a persona missing from the matrix fails, named ({rc} {out!r})")
    rows = full_rows()
    rows[0]["checks"].pop("controls")
    rc, out, _ = rep(report(rows), "--require", "build")
    ok(rc == 1 and "`controls`" in out, f"a step missing a checklist item fails ({rc} {out!r})")
    rows = full_rows()
    rows[1]["checks"]["controls"] = "fail"
    rc, out, _ = rep(report(rows), "--require", "build")
    ok(rc == 1 and "names its finding" in out, f"a failed item with no finding fails ({rc} {out!r})")
    rows = full_rows()
    rows[1]["checks"]["controls"] = "fail"
    rows[1]["findings"] = [{"severity": "breaks", "what": "no back button", "status": "open"}]
    rc, out, _ = rep(report(rows), "--require", "build")
    ok(rc == 1 and "open `breaks`" in out, f"an open breaks finding fails the gate ({rc} {out!r})")
    rows[1]["findings"][0]["status"] = "fixed"
    rows[1]["checks"]["controls"] = "pass"
    rows[1]["findings"] = []
    rc, out, _ = rep(report(rows), "--require", "build")
    ok(rc == 0, f"the fixed finding re-read passes ({rc} {out!r})")
    rows = full_rows()
    rows[0]["findings"] = [{"severity": "breaks", "what": "taste", "status": "open"}]
    rc, out, _ = rep(report(rows), "--require", "build")
    ok(rc == 1 and "names the checklist item" in out, f"breaks with every item passing is refused as taste ({rc} {out!r})")
    rows = full_rows()
    del rows[1]["capture"]
    rc, out, _ = rep(report(rows), "--require", "build")
    ok(rc == 1 and "carries its `capture`" in out, f"a build step without its capture fails ({rc} {out!r})")
    rows = full_rows()
    del rows[0]["frame"]
    rc, out, _ = rep(report(rows), "--require", "build")
    ok(rc == 1 and "`frame`" in out, f"a design step without its frame fails ({rc} {out!r})")
    rows = full_rows()
    rows[1]["checks"]["outcome"] = "NOT_RUN"
    rc, out, _ = rep(report(rows), "--require", "build")
    ok(rc == 1 and "carries its reason" in out, f"NOT_RUN without a reason fails ({rc} {out!r})")
    rc, out, _ = rep(report(full_rows(), {"started": [{"pid": 1}], "live": [4242], "closed": False}), "--require", "build")
    ok(rc == 1 and "still running" in out and "4242" in out, f"a live process in the receipt fails the gate ({rc} {out!r})")
    rc, out, _ = rep({k: v for k, v in report(full_rows()).items() if k != "resources"}, "--require", "build")
    ok(rc == 1 and "no resource receipt" in out, f"a report without its receipt fails ({rc} {out!r})")
    rows = full_rows() + [dict(r, pass_id="second") for r in full_rows(("build",))]
    rc, out, _ = rep(report(rows), "--require", "build")
    ok(rc == 1 and "the budget is 1" in out, f"a second build pass in one round is over budget ({rc} {out!r})")
    rows = full_rows()
    rc, out, _ = run(DG, "report", d / "absent.json", "--class", "product")
    ok(rc == 3 and "NOT_RUN" in out, f"no report on a gated class is NOT_RUN ({rc} {out!r})")
    rc, out, _ = run(DG, "report", d / "absent.json", "--class", "internal")
    ok(rc == 0, f"no report on internal is recommended, not gated ({rc} {out!r})")
    rows = full_rows()
    rows[0]["checks"].pop("focus")
    rc, out, _ = rep(report(rows), "--require", "build", cls="internal")
    ok(rc == 0 and "recommended" in out and "`focus`" in out, f"internal reports problems without gating ({rc} {out!r})")
    p = d / "r.json"
    p.write_text(json.dumps(report(full_rows())))
    rc, out, _ = run(DG, "report", p, "--class", "product", "--panel", panel, "--scope", "SCR-09", "--require", "build")
    ok(rc == 1 and "no panel persona uses it" in out, f"a scope scenario no persona uses fails: the panel does not cover the change ({rc} {out!r})")
    p.write_text("{not json")
    rc, out, err = run(DG, "report", p, "--class", "product")
    ok(rc == 2, f"an unreadable report is usage, exit 2 ({rc} {err!r})")

    cfg = d / "pipeline.json"
    cfg.write_text(json.dumps({"browser": {"primary": "safari", "fallback": ["playwright-webkit"],
                                          "storageState": str(pathlib.Path.home() / ".local/share/x/state.json")}}))
    rc, out, _ = run(DG, "browser", cfg, "--repo", d)
    ok(rc == 0, f"a recorded browser with its state outside the repo passes ({rc} {out!r})")
    cfg.write_text(json.dumps({"browser": {"primary": "safari", "storageState": ".auth/state.json"}}))
    rc, out, _ = run(DG, "browser", cfg, "--repo", d)
    ok(rc == 1 and "inside the repository" in out, f"a state file inside the repo is refused ({rc} {out!r})")
    cfg.write_text(json.dumps({"browser": {"primary": "netscape"}}))
    rc, out, _ = run(DG, "browser", cfg, "--repo", d)
    ok(rc == 1 and "primary is one of" in out, f"an unknown driver is refused ({rc} {out!r})")
    cfg.write_text(json.dumps({"stages": []}))
    rc, out, _ = run(DG, "browser", cfg, "--repo", d)
    ok(rc == 3 and "asks the operator" in out, f"no browser block is NOT_RUN: ask once ({rc} {out!r})")

    # Review fixes (round 1 of the blind reading).
    rows = full_rows() + [row("SCR-01", "P-01", "design")]
    rc, out, _ = rep(report(rows), "--require", "build")
    ok(rc == 1 and "walks a design step 2 times" in out, f"the same step walked twice in a round is over the pass budget, no pass_id needed ({rc} {out!r})")
    rows = full_rows()
    rows[0]["round"] = "1"
    rows.append(dict(row("SCR-01", "P-01", "design"), round=1))
    rc, out, _ = rep(report(rows), "--require", "build")
    ok(rc == 1 and "2 times" in out, f"round written as a string still counts with round 1 ({rc} {out!r})")
    p_ = d / "r.json"
    p_.write_text(json.dumps(report(full_rows())))
    rc, out, _ = run(DG, "report", p_, "--class", "product", "--panel", d / "nope.md", "--scope", "SCR-01", "--require", "build")
    ok(rc == 3 and "test panel" in out, f"a panel path that does not exist is NOT_RUN on a gated class ({rc} {out!r})")
    rc, out, _ = run(DG, "report", p_, "--class", "product", "--panel", panel, "--require", "build")
    ok(rc == 3 and "scope" in out, f"no --scope is NOT_RUN on a gated class ({rc} {out!r})")
    idle = {c: "NOT_RUN" for c in CHECKS_OK}
    rows = full_rows(("design",)) + [dict(row("SCR-01", f"P-{i:02d}", "build"), checks=dict(idle), reason="no browser channel")
                                     for i in range(1, 11)]
    rc, out, _ = rep(report(rows), "--require", "build")
    ok(rc == 3 and "build pass did not run" in out, f"pass B never driven is NOT_RUN even with design rows passing ({rc} {out!r})")
    rows = full_rows()
    rows[3]["checks"] = dict(idle)
    rows[3]["reason"] = "sign-in wall"
    rc, out, _ = rep(report(rows), "--require", "build")
    ok(rc == 0 and "sign-in wall" in out, f"one walled step passes and is listed in notes ({rc} {out!r})")
    alias = d / "alias.md"
    alias.write_text(panel_text().replace("- **basis**: ", "- **Basis:** ").replace("- **activation**: ", "- **activation funnel** – "))
    rc, out, _ = run(DG, "panel", alias)
    ok(rc == 0, f"`**Basis:**` and `activation funnel –` are read ({rc} {out!r})")
    dup = d / "dup.md"
    dup.write_text(panel_text().replace("## P-04 Persona 4", "## P-03 Persona 4"))
    rc, out, _ = run(DG, "panel", dup, "--min", "9")
    ok(rc == 1 and "P-03 appears twice" in out, f"a duplicated portrait id is named ({rc} {out!r})")
    cfg = d / "pipeline.json"
    cfg.write_text(json.dumps({"browser": {"primary": "safari", "storageState": str(d).upper() + "/.auth/s.json"}}))
    rc, out, _ = run(DG, "browser", cfg, "--repo", d)
    ok(rc == 1 or sys.platform != "darwin", f"an upper-case in-repo path is still inside the repo on macOS ({rc} {out!r})")
    cfg.write_text(json.dumps({"browser": {"primary": "safari", "storageState": 42}}))
    rc, out, _ = run(DG, "browser", cfg, "--repo", d)
    ok(rc == 1 and "path string" in out, f"a non-string storageState is refused, not a traceback ({rc} {out!r})")

    # Review fixes (round 2).
    empty = d / "empty.md"
    empty.write_text("# Test panel\n\n### P-01 not a portrait heading\n")
    p_ = d / "r.json"
    p_.write_text(json.dumps(report(full_rows())))
    rc, out, _ = run(DG, "report", p_, "--class", "product", "--panel", empty, "--scope", "SCR-01", "--require", "build")
    ok(rc == 3 and "portraits" in out, f"a panel file with no portraits is NOT_RUN, not PASS ({rc} {out!r})")
    rows = full_rows()
    rows[2]["checks"]["controls"] = "fail"
    rows[2]["findings"] = [{"severity": "breaks", "what": "x", "status": "open"}]
    p_.write_text(json.dumps(report(rows)))
    rc, out, _ = run(DG, "report", p_, "--class", "product", "--panel", empty, "--scope", "SCR-01", "--require", "build")
    ok(rc == 1 and "open `breaks`" in out and "coverage cannot be computed" in out,
       f"with no panel the open breaks finding is still shown ({rc} {out!r})")
    rows = full_rows()
    rows[0]["round"] = "1.0"
    rc, out, _ = rep(report(rows), "--require", "build")
    ok(rc == 1 and "positive integer" in out, f"round '1.0' is refused ({rc} {out!r})")
    rows = full_rows()
    rows[1]["checks"]["frame"] = "na"
    rc, out, _ = rep(report(rows), "--require", "build")
    ok(rc == 1 and "never na" in out, f"`frame` cannot be na ({rc} {out!r})")
    cfg = d / "pipeline.json"
    cfg.write_text(json.dumps({"browser": {"primary": "safari", "fallback": "chrome-dev"}}))
    rc, out, _ = run(DG, "browser", cfg, "--repo", d)
    ok(rc == 1 and out.count("  - ") == 1 and "is a list" in out, f"a string fallback is one problem ({rc} {out!r})")

    # Review fixes (round 3).
    for st in ("OPEN", None, "", "deferred"):
        rows = full_rows()
        rows[1]["checks"]["primary_action"] = "fail"
        rows[1]["findings"] = [{"severity": "breaks", "what": "x", "status": st}]
        rc, out, _ = rep(report(rows), "--require", "build")
        ok(rc == 1, f"a breaks finding with status {st!r} keeps the gate shut ({rc} {out!r})")
    for bad in ({"round": "\u00b2"}, {"checks": ["pass"]}, {"findings": "oops"}):
        rows = full_rows()
        rows[0].update(bad)
        rc, out, err = rep(report(rows), "--require", "build")
        ok(rc == 1 and "Traceback" not in err and "FAIL" in out, f"malformed {bad} is a named FAIL, no traceback ({rc} {err[-200:]!r})")
    rc, out, err = rep(report(["not a row"]), "--require", "build")
    ok(rc == 1 and "Traceback" not in err, f"a row that is not an object is a named FAIL ({rc} {err[-200:]!r})")
    cfg = d / "pipeline.json"
    cfg.write_text(json.dumps({"browser": {"primary": "safari", "fallback": 5}}))
    rc, out, err = run(DG, "browser", cfg, "--repo", d)
    ok(rc == 1 and "Traceback" not in err, f"a numeric fallback is a named FAIL ({rc} {err[-200:]!r})")

    # resource_guard.py, on real processes
    led = d / "ledger.json"
    rc, out, _ = run(RG, "check", "--max-load-ratio", "1000", "--min-free-gb", "0", "--max-memory-pressure", "warn")
    ok(rc == 0 and out.startswith("resource_guard: go"), f"check under generous lines says go ({rc} {out!r})")
    rc, out, _ = run(RG, "check", "--max-load-ratio", "0.00001")
    ok(rc == 4 and "wait" in out, f"check over the load line says wait, exit 4 ({rc} {out!r})")
    a = subprocess.Popen(["sleep", "60"])
    b = subprocess.Popen(["sleep", "61"])
    try:
        rc, out, _ = run(RG, "record", led, a.pid, "browser one", "--max-browsers", "1")
        ok(rc == 0, f"record a live process ({rc} {out!r})")
        rc, _, err = run(RG, "record", led, b.pid, "browser two", "--max-browsers", "1")
        ok(rc == 5 and "cap reached" in err, f"a second browser over the cap of one is refused, exit 5 ({rc} {err!r})")
        rc, out, _ = run(RG, "verify", led)
        ok(rc == 1 and str(a.pid) in out, f"verify names the live recorded process ({rc} {out!r})")
        rc, out, _ = run(RG, "close", led, "--grace", "2")
        a.wait(timeout=10)
        ok(a.returncode is not None, "close ended the recorded process")
        ok(b.poll() is None, "close never touched the process it did not record")
        rc, out, _ = run(RG, "verify", led, "--json")
        doc = json.loads(out)
        ok(rc == 0 and doc["closed"] is True and doc["live"] == [], f"verify is clean after close ({rc} {out!r})")
        rc, _, err = run(RG, "record", led, 999999, "ghost")
        ok(rc == 2 and "not running" in err, f"recording a pid that is not running is refused ({rc} {err!r})")
        # An exec'ing launcher keeps its pid and start time: it is the same process.
        led2 = d / "ledger2.json"
        e = subprocess.Popen(["sh", "-c", "sleep 1; exec sleep 62"])
        rc, out, _ = run(RG, "record", led2, e.pid, "dev server", "--cap-kind", "server", "--max-servers", "1")
        ok(rc == 0, f"record the launcher ({rc} {out!r})")
        time.sleep(2)
        f2 = subprocess.Popen(["sleep", "63"])
        rc, _, err = run(RG, "record", led2, f2.pid, "second server", "--cap-kind", "server", "--max-servers", "1")
        ok(rc == 5, f"after exec the launcher still counts against the server cap ({rc} {err!r})")
        rc, out, _ = run(RG, "verify", led2)
        ok(rc == 1 and str(e.pid) in out, f"verify still sees the exec'd process ({rc} {out!r})")
        run(RG, "close", led2, "--grace", "2")
        e.wait(timeout=10)
        rc, out, _ = run(RG, "verify", led2)
        ok(rc == 0, f"close ended the exec'd process and verify is clean ({rc} {out!r})")
        f2.kill()
        # A parent and its child: close ends the child too.
        led3 = d / "ledger3.json"
        par = subprocess.Popen(["sh", "-c", "sleep 64 & wait"])
        time.sleep(0.5)
        kid = int(subprocess.run(["pgrep", "-P", str(par.pid)], capture_output=True, text=True).stdout.split()[0])
        run(RG, "record", led3, par.pid, "browser")
        rc, out, _ = run(RG, "close", led3, "--grace", "2")
        par.wait(timeout=10)
        time.sleep(0.5)
        ok(subprocess.run(["kill", "-0", str(kid)], capture_output=True).returncode != 0 and "1 descendant" in out,
           f"close ended the recorded process's child ({out!r})")
        # Four agents recording at once all land.
        led4 = d / "ledger4.json"
        sleepers = [subprocess.Popen(["sleep", "65"]) for _ in range(4)]
        procs = [subprocess.Popen([sys.executable, str(RG), "record", str(led4), str(x.pid), f"page {n}", "--cap-kind", "page", "--max-pages", "9"])
                 for n, x in enumerate(sleepers)]
        codes = [pp.wait() for pp in procs]
        n_rec = len(json.loads(led4.read_text())["started"])
        ok(codes == [0, 0, 0, 0] and n_rec == 4, f"four concurrent records all land ({codes} {n_rec})")
        run(RG, "close", led4, "--grace", "2")
        for x in sleepers:
            x.wait(timeout=10)
        # The start time is read in one locale and zone, whatever the caller's.
        h = subprocess.Popen(["sleep", "67"])
        led6 = d / "ledger6.json"
        subprocess.run([sys.executable, str(RG), "record", str(led6), str(h.pid), "browser"],
                       env=dict(os.environ, LC_ALL="C", TZ="UTC"), capture_output=True)
        r = subprocess.run([sys.executable, str(RG), "verify", str(led6)], capture_output=True, text=True,
                           env=dict(os.environ, LC_ALL="ru_RU.UTF-8", LANG="ru_RU.UTF-8", TZ="Asia/Tokyo"))
        ok(r.returncode == 1 and str(h.pid) in r.stdout, f"verify under another locale and zone still sees the process ({r.returncode} {r.stdout!r})")
        subprocess.run([sys.executable, str(RG), "close", str(led6), "--grace", "2"], capture_output=True,
                       env=dict(os.environ, TZ="America/New_York"))
        h.wait(timeout=10)
        ok(h.returncode is not None, "close under another zone ended the process")
        lock = d / "ledger6.json.lock"
        ok(run(RG, "verify", led6)[0] == 0 and (not lock.exists() or lock.stat().st_size == 0),
           "a clean verify leaves at most the empty lock sidecar (never unlinked under another writer)")
        rc, _, err = run(RG, "record", d / "ledger7.json", os.getpid(), "myself")
        ok(rc == 2 and "never recorded" in err, f"recording this process or an ancestor is refused ({rc} {err!r})")
        # A protected pid in a corrupted ledger: close refuses it and its whole subtree.
        import importlib.util
        spec = importlib.util.spec_from_file_location("rg", RG)
        rg = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rg)
        led8 = d / "ledger8.json"
        led8.write_text(json.dumps({"schema": "resource-ledger/1", "started": [
            {"pid": 1, "what": "corrupt", "kind": "browser", "started": rg.started(1)},
            {"pid": os.getppid(), "what": "corrupt", "kind": "browser", "started": rg.started(os.getppid())}]}))
        sent = []
        real_kill = rg.os.kill
        rg.os.kill = lambda pid, sig: sent.append((pid, sig)) if sig != 0 else real_kill(pid, 0)
        try:
            closed, kids, skipped, refused = rg.close(str(led8), 0.2)
        finally:
            rg.os.kill = real_kill
        ok(sent == [] and 1 in refused and kids == [], f"close never signals a protected pid or anything under it ({len(sent)} signals, refused {refused})")
        # Without ps, verify cannot tell: NOT_RUN, never clean.
        g = subprocess.Popen(["sleep", "66"])
        led5 = d / "ledger5.json"
        run(RG, "record", led5, g.pid, "browser")
        r = subprocess.run([sys.executable, str(RG), "verify", str(led5)], capture_output=True, text=True,
                           env={"PATH": "/nonexistent"})
        ok(r.returncode == 2 and "NOT_RUN" in r.stderr, f"verify without ps is NOT_RUN, exit 2 ({r.returncode} {r.stderr!r})")
        g.kill()
    finally:
        for p_ in (a, b):
            if p_.poll() is None:
                p_.kill()

if failures:
    print("FAIL: %d of %d design-review checks" % (len(failures), count))
    sys.exit(1)
print("PASS: design review gate and resource guard — %d cases" % count)
