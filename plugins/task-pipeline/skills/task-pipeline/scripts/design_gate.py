#!/usr/bin/env python3
"""The design-review gate: the test panel and the design-tester's report, as commands
with an exit code. Stdlib only.

    design_gate.py panel  <docs/ux/test-panel.md> [--min 10] [--json]
        the test panel the design-tester walks: ten portraits (or --min), each with its
        basis, situation, goals, features, composite scenarios, activation funnel,
        retention loop and needs. A portrait without a basis line is refused: a panel is a
        hypothesis instrument, and saying so is part of the portrait.
    design_gate.py report <design-review.json> --class <surface_class>
                          [--panel <test-panel.md>] [--scope SCR-01,SCR-02] [--require build]
                          [--max-passes 1] [--subscription] [--json]
        stage 3 (`--require design`) and stage 6 (`--require build`): the report covers
        every scope scenario × every panel persona that uses it, every step carries the
        full checklist, no `breaks` finding is open, each round holds at most --max-passes
        passes of each kind, and the resource receipt shows every process it started closed.
        `--subscription` (or a `subscription` block in the report): the surface sells, renews
        or cancels a subscription, so cancelling takes no more steps than subscribing and the
        paywall makes one clear offer (1.101.0).

    design_gate.py browser <pipeline.json> [--repo DIR] [--json]
        the recorded test browser: `browser.primary` is set (NOT_RUN when the block is
        absent: stage 0 asks the operator once), the fallback names known drivers, and
        `browser.storageState`, a credential, sits outside the repository.

`<surface_class>` is the brief's stage-0 answer: flagship | product | internal | ad. On
flagship, product and ad the review is a GATE; on internal the report is checked for honesty
and its coverage only reported (`references/design-review.md`).

**A check that could not run says NOT_RUN, and NOT_RUN is never PASS.** No report on a gated
class is NOT_RUN; a step whose capture could not be taken is NOT_RUN with its reason.

Exit codes: 0 PASS · 1 FAIL · 2 usage, or an input that cannot be read · 3 NOT_RUN.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

SURFACE_CLASSES = ("flagship", "product", "internal", "ad")
GATED = ("flagship", "product", "ad")
PASSES = ("design", "build")
# The fixed checklist every step is judged on (spec DR-05). A person can read it in a row.
CHECKS = ("frame", "primary_action", "controls", "focus", "states", "text_fit", "outcome")
CHECK_VALUES = ("pass", "fail", "na", "NOT_RUN")
SEVERITIES = ("breaks", "risk", "nit")
STATUSES = ("open", "fixed")  # absent means open; anything else is refused, never read as closed
FIELDS = ("basis", "situation", "goals", "features", "scenarios", "activation", "retention", "needs")
PORTRAIT = re.compile(r"^##\s+(P-\d{2})\b(.*)$")
ALIASES = {"composite scenarios": "scenarios", "activation funnel": "activation",
           "retention loop": "retention"}
FIELD = re.compile(r"^\s*[-*]\s+\*\*(%s)\s*:?\*\*\s*[:—–-]?\s*(.+?)\s*$"
                   % "|".join(sorted(list(FIELDS) + list(ALIASES), key=len, reverse=True)), re.I)
SCR = re.compile(r"\bSCR-\d+\b")


def read_text(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError as exc:
        raise SystemExit(_usage("cannot read %s (%s)" % (path, exc.strerror or exc)))


def _usage(msg):
    print("design_gate: %s" % msg, file=sys.stderr)
    return 2


def parse_panel(text):
    """{persona id: {field: value}} from the panel's `## P-NN` sections. A repeated id is
    kept under `__duplicates__` so the check can name it rather than count it once."""
    panel, cur, dups = {}, None, []
    for line in text.splitlines():
        m = PORTRAIT.match(line)
        if m:
            cur = m.group(1)
            if cur in panel:
                dups.append(cur)
            panel[cur] = {"title": m.group(2).strip(" —-:")}
            continue
        if line.startswith("## "):
            cur = None
            continue
        if cur:
            f = FIELD.match(line)
            if f:
                key = f.group(1).lower()
                panel[cur][ALIASES.get(key, key)] = f.group(2).strip()
    if dups:
        panel["__duplicates__"] = dups
    return panel


def portraits(panel):
    return {k: v for k, v in panel.items() if not k.startswith("__")}


def panel_problems(panel, minimum):
    out = ["%s appears twice; every portrait has its own id" % d for d in panel.get("__duplicates__", [])]
    panel = portraits(panel)
    if len(panel) < minimum:
        out.append("the panel holds %d portrait(s); it owes %d" % (len(panel), minimum))
    for pid, p in sorted(panel.items()):
        for f in FIELDS:
            if not p.get(f):
                out.append("%s: no **%s** line" % (pid, f))
        basis = p.get("basis", "")
        if basis and not re.match(r"^(evidence\s+RE-\d+|hypothesis)\b", basis, re.I):
            out.append("%s: basis is `evidence RE-NN` or `hypothesis`, not %r" % (pid, basis[:40]))
        if p.get("scenarios") and not SCR.search(p["scenarios"]):
            out.append("%s: composite scenarios cite no SCR- id" % pid)
    return out


def personas_using(panel, scenario):
    return sorted(pid for pid, p in portraits(panel).items() if scenario in SCR.findall(p.get("scenarios", "")))


def _posint(v):
    """A round or step as a positive int: 1, "1" and "01" are 1; "1.0", "first", 0 are None."""
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v if v > 0 else None
    if isinstance(v, str) and v.strip().isascii() and v.strip().isdigit() and int(v) > 0:
        return int(v)
    return None


def row_problems(r, i):
    out, rid = [], "row %d (%s %s/%s %s)" % (i, r.get("scenario"), r.get("step"), r.get("persona"), r.get("pass"))
    for k in ("scenario", "step", "persona", "pass", "round"):
        if r.get(k) in (None, ""):
            out.append("%s: no `%s`" % (rid, k))
    if r.get("round") not in (None, "") and _posint(r.get("round")) is None:
        out.append("%s: round is a positive integer, not %r" % (rid, r.get("round")))
    if r.get("pass") not in PASSES:
        out.append("%s: pass is design or build" % rid)
    checks = r.get("checks") or {}
    if not isinstance(checks, dict):
        return out + ["%s: `checks` is an object of the seven checklist items" % rid]
    if not isinstance(r.get("findings") or [], list):
        return out + ["%s: `findings` is a list" % rid]
    for c in CHECKS:
        v = checks.get(c)
        if v not in CHECK_VALUES:
            out.append("%s: checklist item `%s` is %r, not one of %s" % (rid, c, v, "/".join(CHECK_VALUES)))
    for c in ("frame", "outcome"):
        if checks.get(c) == "na":
            out.append("%s: `%s` is never na: every step has a screen and an outcome" % (rid, c))
    if any(v == "NOT_RUN" for v in checks.values()) and not r.get("reason"):
        out.append("%s: a NOT_RUN item carries its reason" % rid)
    if r.get("pass") == "design" and not r.get("frame"):
        out.append("%s: a design step names its Figma node or mockup (`frame`)" % rid)
    if r.get("pass") == "build":
        if not r.get("capture") and checks.get("frame") != "NOT_RUN":
            out.append("%s: a build step carries its `capture`" % rid)
        if not r.get("engine"):
            out.append("%s: a build step names its `engine`" % rid)
    failed = any(checks.get(c) == "fail" for c in CHECKS)
    for f in r.get("findings") or []:
        if not isinstance(f, dict):
            out.append("%s: a finding is an object with severity, what and status" % rid)
            continue
        if f.get("status", "open") not in STATUSES:
            out.append("%s: finding status is open or fixed, not %r" % (rid, f.get("status")))
        if f.get("severity") not in SEVERITIES:
            out.append("%s: finding severity is breaks, risk or nit" % rid)
        elif f.get("severity") == "breaks" and not failed:
            out.append("%s: a `breaks` finding names the checklist item that failed" % rid)
    if any(v == "fail" for v in checks.values()) and not (r.get("findings") or []):
        out.append("%s: a failed checklist item names its finding" % rid)
    return out


PARITY = ("pass", "fail", "NOT_RUN")
PAUSE = ("offered", "absent", "na")


def subscription_problems(sub):
    """M2 G8/R2: cancelling is as easy as subscribing, and the paywall makes one clear offer.
    Returns (problems, notes, not_run)."""
    if sub is None:
        return (["a subscription surface carries its cancel parity check (`subscription` block: "
                 "cancel_parity, subscribe_steps, cancel_steps, single_offer, pause)"], [], False)
    if not isinstance(sub, dict):
        return ["`subscription` is an object, not %r" % (sub,)], [], False
    out, notes = [], []
    for k in ("cancel_parity", "single_offer"):
        if sub.get(k) not in PARITY:
            out.append("subscription.%s is %r, not one of %s" % (k, sub.get(k), "/".join(PARITY)))
    steps = {k: _posint(sub.get(k)) for k in ("subscribe_steps", "cancel_steps")}
    for k, v in steps.items():
        if v is None and sub.get("cancel_parity") != "NOT_RUN":
            out.append("subscription.%s is a positive integer, not %r" % (k, sub.get(k)))
    s, c = steps["subscribe_steps"], steps["cancel_steps"]
    if sub.get("cancel_parity") == "fail":
        out.append("cancelling takes %s steps against %s to subscribe: cancel parity fails" % (c, s))
    elif sub.get("cancel_parity") == "pass" and s and c and c > s:
        out.append("cancel_parity `pass` contradicts %d cancel steps against %d to subscribe" % (c, s))
    if sub.get("single_offer") == "fail":
        out.append("the paywall makes no single clear offer")
    if sub.get("pause") not in PAUSE:
        out.append("subscription.pause is offered, absent or na, not %r" % (sub.get("pause"),))
    elif sub.get("pause") == "absent":
        notes.append("no pause offered on the cancel path (a save offer, not gated)")
    idle = [k for k in ("cancel_parity", "single_offer") if sub.get(k) == "NOT_RUN"]
    if idle and not sub.get("reason"):
        out.append("a NOT_RUN %s carries its reason" % " and ".join(idle))
    return out, notes, bool(idle)


def report_check(doc, surface_class, panel=None, scope=(), require=None, max_passes=1, subscription=False):
    problems, notes = [], []
    if not isinstance(doc, dict) or doc.get("schema") != "design-review/1":
        return "FAIL", ["the report is not design-review/1"], notes
    sub_idle = False
    if subscription or "subscription" in doc:
        sp, sn, sub_idle = subscription_problems(doc.get("subscription"))
        problems += sp
        notes += sn
    rows = doc.get("rows") or []
    if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
        return "FAIL", ["`rows` is a list of objects"], notes
    if not rows:
        return "NOT_RUN", ["the report holds no rows"], notes
    for i, r in enumerate(rows):
        problems += row_problems(r, i)
    open_breaks = [(r.get("scenario"), r.get("step"), r.get("persona")) for r in rows
                   for f in (r.get("findings") if isinstance(r.get("findings"), list) else [])
                   if isinstance(f, dict) and f.get("severity") == "breaks" and f.get("status", "open") != "fixed"]
    for s in open_breaks:
        problems.append("open `breaks` finding at %s step %s for %s" % s)
    # DR-10: one pass of each kind per surface per round. A second pass shows as the same
    # step walked again in the same round; the round is read as a number.
    walks = {}
    for r in rows:
        rnd = _posint(r.get("round"))
        if rnd is None:
            continue
        step = _posint(r.get("step"))
        key = (rnd, r.get("pass"), r.get("scenario"), step if step is not None else str(r.get("step")), r.get("persona"))
        walks[key] = walks.get(key, 0) + 1
    over = {}
    for (rnd, kind, *_), n in walks.items():
        if n > max_passes:
            over[(rnd, kind)] = max(over.get((rnd, kind), 0), n)
    for (rnd, kind), n in sorted(over.items()):
        problems.append("round %d walks a %s step %d times; the budget is %d pass(es) per round" % (rnd, kind, n, max_passes))
    # Coverage: each scope scenario × each persona that uses it, for each required pass.
    kinds = PASSES if require == "build" else ("design",) if require == "design" else ()
    no_panel = panel is None or not portraits(panel)
    coverage_gap = None
    if kinds and surface_class in GATED and (no_panel or not scope):
        missing = ("a test panel with portraits" if no_panel else "") + (" and " if no_panel and not scope else "") + \
                  ("the scope (--scope SCR ids)" if not scope else "")
        coverage_gap = "coverage cannot be computed without %s; the gate does not pass on it" % missing
    if panel and portraits(panel) and scope:
        seen = {(r.get("scenario"), r.get("persona"), r.get("pass")) for r in rows}
        for s in scope:
            users = personas_using(panel, s)
            if not users:
                problems.append("%s: no panel persona uses it; the panel does not cover the change" % s)
            for p in users:
                for k in kinds:
                    if (s, p, k) not in seen:
                        problems.append("%s × %s: no %s pass" % (s, p, k))
    elif kinds:
        notes.append("coverage not computed: --panel and --scope are both needed")
    # DR-08: the resource receipt.
    res = doc.get("resources")
    if not isinstance(res, dict):
        problems.append("no resource receipt (`resources`): what the review started, and that it closed")
    else:
        if res.get("live"):
            problems.append("processes the review started are still running: %s" % ", ".join(map(str, res["live"])))
        if res.get("closed") is not True:
            problems.append("the resource receipt does not say `closed: true`")
    if surface_class not in GATED:
        notes.append("class %s: the review is recommended; problems are reported, not gated" % surface_class)
        return "PASS", problems, notes
    if problems:
        return "FAIL", problems + ([coverage_gap] if coverage_gap else []), notes
    if coverage_gap:
        return "NOT_RUN", [coverage_gap], notes
    # NOT_RUN is judged per required pass: a stage-6 gate whose build steps were never driven
    # is NOT_RUN, whatever the design rows say. Partial NOT_RUN (a sign-in wall) is listed.
    def idle(r):
        return all(v == "NOT_RUN" for v in (r.get("checks") or {}).values())
    for k in kinds or PASSES:
        mine = [r for r in rows if r.get("pass") == k]
        if mine and all(idle(r) for r in mine):
            return "NOT_RUN", ["every %s step is NOT_RUN: the %s pass did not run" % (k, k)], notes
        if k in kinds and not mine:
            return "NOT_RUN", ["no %s step in the report" % k], notes
    if sub_idle:
        return "NOT_RUN", ["the subscription checks were not walked: %s" % doc["subscription"].get("reason")], notes
    partial = ["%s step %s for %s (%s)" % (r.get("scenario"), r.get("step"), r.get("persona"), r.get("reason", "no reason"))
               for r in rows if any(v == "NOT_RUN" for v in (r.get("checks") or {}).values())]
    if partial:
        notes.append("NOT_RUN steps: " + "; ".join(partial))
    return "PASS", problems, notes


DRIVERS = ("safari", "playwright-webkit", "chrome-dev", "playwright-chromium")


def browser_check(cfg, repo):
    b = cfg.get("browser") if isinstance(cfg, dict) else None
    if not isinstance(b, dict):
        return "NOT_RUN", ["no `browser` block: stage 0 asks the operator which browser the tests use, once"], []
    probs = []
    if b.get("primary") not in DRIVERS:
        probs.append("browser.primary is one of %s, not %r" % (", ".join(DRIVERS), b.get("primary")))
    fb = b.get("fallback") or []
    if not isinstance(fb, list):
        probs.append("browser.fallback is a list of drivers, not %r" % (fb,))
        fb = []
    for f in fb:
        if f not in DRIVERS:
            probs.append("browser.fallback names an unknown driver %r" % f)
    st = b.get("storageState")
    if st is not None and not isinstance(st, str):
        probs.append("browser.storageState is a path string")
        st = None
    if st:
        exp = os.path.expanduser(st)
        full = os.path.normcase(os.path.realpath(exp if os.path.isabs(exp) else os.path.join(repo, exp)))
        root = os.path.normcase(os.path.realpath(repo))
        if sys.platform == "darwin":  # APFS is case-insensitive by default; normcase is not
            full, root = full.lower(), root.lower()
        if full == root or full.startswith(root + os.sep):
            probs.append("browser.storageState %s is inside the repository; a signed-in state is a credential" % st)
    notes = ["primary %s, fallback %s" % (b.get("primary"), ", ".join(map(str, fb)) or "none")]
    return ("FAIL" if probs else "PASS"), probs, notes


def emit(verdict, problems, notes, as_json, extra=None):
    if as_json:
        print(json.dumps(dict(verdict=verdict, problems=problems, notes=notes, **(extra or {})), indent=2))
    else:
        print("design_gate: %s" % verdict)
        for p in problems:
            print("  - %s" % p)
        for n in notes:
            print("  note: %s" % n)
    return {"PASS": 0, "FAIL": 1, "NOT_RUN": 3}[verdict]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("panel")
    p1.add_argument("path")
    p1.add_argument("--min", type=int, default=10)
    p1.add_argument("--json", action="store_true")
    p3 = sub.add_parser("browser")
    p3.add_argument("path")
    p3.add_argument("--repo", help="the repository root; default: the git top level of the pipeline.json's folder")
    p3.add_argument("--json", action="store_true")
    p2 = sub.add_parser("report")
    p2.add_argument("path")
    p2.add_argument("--class", dest="cls", required=True, choices=SURFACE_CLASSES)
    p2.add_argument("--panel")
    p2.add_argument("--scope", default="")
    p2.add_argument("--require", choices=PASSES)
    p2.add_argument("--max-passes", type=int, default=1)
    p2.add_argument("--subscription", action="store_true",
                    help="the surface sells, renews or cancels a subscription: cancel parity and one clear offer are owed")
    p2.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "panel":
        if not os.path.exists(a.path):
            return emit("NOT_RUN", ["no test panel at %s: super-ux `ux-foundation` builds it" % a.path], [], a.json)
        panel = parse_panel(read_text(a.path))
        probs = panel_problems(panel, a.min)
        return emit("FAIL" if probs else "PASS", probs, ["%d portrait(s)" % len(portraits(panel))], a.json)
    if a.cmd == "browser":
        try:
            cfg = json.loads(read_text(a.path))
        except ValueError as exc:
            print("design_gate: %s is not JSON (%s)" % (a.path, exc), file=sys.stderr)
            return 2
        repo = a.repo
        if not repo:
            import subprocess
            here = os.path.dirname(os.path.abspath(a.path))
            r = subprocess.run(["git", "-C", here, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
            repo = r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else here
        v, probs, notes = browser_check(cfg, repo)
        return emit(v, probs, notes, a.json)
    if not os.path.exists(a.path):
        v = "NOT_RUN" if a.cls in GATED else "PASS"
        return emit(v, ["no design review at %s" % a.path], [], a.json)
    try:
        doc = json.loads(read_text(a.path))
    except ValueError as exc:
        print("design_gate: %s is not JSON (%s)" % (a.path, exc), file=sys.stderr)
        return 2
    panel = parse_panel(read_text(a.panel)) if a.panel and os.path.exists(a.panel) else None
    scope = [s.strip() for s in a.scope.split(",") if s.strip()]
    verdict, probs, notes = report_check(doc, a.cls, panel, scope, a.require, a.max_passes, a.subscription)
    return emit(verdict, probs, notes, a.json)


if __name__ == "__main__":
    sys.exit(main())
