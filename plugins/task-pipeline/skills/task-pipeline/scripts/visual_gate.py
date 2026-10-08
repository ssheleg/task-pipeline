#!/usr/bin/env python3
"""The visual half of the pipeline's gates, as commands with an exit code. Stdlib only.

    visual_gate.py record   <director-record.md> --class <surface_class>
                            [--validator CMD | --validator none] [--json]
        stage 3: the VISUAL track left a director record, and the record carries the
        fields its surface class owes — not merely "the track ran"
    visual_gate.py sheet    <contact-sheet.json> --class <surface_class>
                            [--artifact-root DIR] [--states a,b,…] [--require-approval] [--json]
        stage 6 (and stage 10 with --require-approval): the contact sheet, a filled copy of
        `templates/browser-claims.json` (browser-claims/1) whose look rows carry the
        state × axes matrix, the capture record, the diff and the rubric
    visual_gate.py lint     <dir> [--linter CMD | --linter none] [--json]
        stages 5–6: the project linter of sheleg-design (`--lint`), run where it exists
    visual_gate.py filekeys --record <foundation.md or brief> --screens <screens.md> [--json]
        stage 3 with Figma on: every frame link's file key is one of the files the project
        recorded — one per surface (App, Web, ASO), never a file nobody recorded
    visual_gate.py tokens   --figma <variables.json> --css <tokens.css> [--json]
        stages 5–6 with Figma on, the token drift probe: every variable name exported from
        the file (`get_variable_defs`, or the REST export) has its CSS custom property in
        the pack's token file and the reverse, and WEB code syntax, where set, names the
        property the file actually declares. No export is NOT_RUN (exit 3), never PASS

`<surface_class>` is the brief's stage-0 answer: flagship | product | internal | ad. It
selects what each check owes (`references/stages.md` → stage 0, *The surface class*).

**A check that could not run says NOT_RUN, and NOT_RUN is never PASS.** The director-record
validator and the project linter belong to sheleg-design; where that package is absent, or
older than the flag, the command says so in words. `record` still checks the required
headings itself — that floor needs nothing installed — and reports the validator NOT_RUN
beside its own verdict, so a reader can tell the floor from the full check.

Exit codes: 0 PASS · 1 FAIL · 2 usage, or an input that cannot be read · 3 NOT_RUN (the check
could not run, or every row it would judge is still NOT_RUN — never a pass).
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime

SURFACE_CLASSES = ("flagship", "product", "internal", "ad")
# Where the visual look is a GATE. `internal` gets the deterministic floor (the linter) and
# a recommended look; a sheet there is checked for honesty, its coverage only reported.
GATED = ("flagship", "product", "ad")

# The director record's fields — `## <Field>` headings — and which class owes which. The
# record's own contract lives with sheleg-design; this is the floor the pipeline can check
# without it. Absent for `internal`: no record is owed there.
FULL_RECORD = ("Brief", "Mode", "Taste", "References", "Cast", "Fork", "Rubric", "Critique",
               "Markers", "Alignment", "Quality", "Signature", "Surfaces", "Haptics", "ADA",
               "Open")
RECORD_FIELDS = {
    "flagship": FULL_RECORD,
    "product": ("Brief", "Mode", "References", "Markers", "Open"),
    "ad": ("Brief", "Mode", "References", "Markers", "ADA", "Open"),
    "internal": (),
}
MODES = ("new", "redesign", "update", "audit", "declined")
# A heading whose body is one of these was never filled in. `n/a` is a valid answer only
# where the contract allows a bare one (Haptics on a surface that is not native); anywhere
# else it owes its reason, and a reason makes the body longer than the bare token.
PLACEHOLDER = re.compile(r"^(?:tbd|tba|todo|\.\.\.|…|-|—|n/?a|none|\?|<[^>]*>)\.?$", re.I)
BARE_NA_OK = ("Haptics",)

DEFAULT_TOOL = "npx --no-install sheleg-design-skill"

AXES = ("viewport", "theme", "text", "locale")
CAPTURE = ("revision", "route", "motion", "captured_at", "source")
RUBRIC_TYPES = ("G", "J", "H")
RUBRIC_STATUS = ("PASS", "FAIL", "NOT_ASSESSED", "uncertain", "unresolved")
DIFF_STATUS = ("PASS", "FAIL", "NOT_RUN")
KINDS = ("look", "suite", "library")
STATUSES = ("PASS", "FAIL", "NOT_RUN", "BLOCKED")
DEFAULT_TEXT = ("default", "base", "normal", "100%", "1x", "m", "medium", "large-off")
RTL = re.compile(r"(?:^|[^a-z])(?:rtl|ar|he|fa|ur|yi)(?:$|[^a-z])", re.I)
NARROW_PX = 400
FIGMA_KEY = re.compile(r"figma\.com/(?:design|file|proto|board|make|slides)/([A-Za-z0-9]{10,})")


# --- browser claims (browser-claims/1) ----------------------------------------
# The rules `references/browser.md` states for every claim, look or not. Kept here so a host
# project can run them; this repository's `test/browser_claims_test.py` imports them.

def claim_problems(claim, artifact_root=None):
    """Every reason this claim must not be believed. Empty list = valid."""
    out = []
    cid = claim.get("id", "?")
    for field in ("id", "req", "scenario", "state", "kind", "status"):
        if not claim.get(field):
            out.append(f"{cid}: {field} missing")
    if claim.get("kind") not in KINDS:
        out.append(f"{cid}: kind {claim.get('kind')!r} is not one of "
                   f"{sorted(KINDS)} — the look/suite/library split is the contract")
    if claim.get("status") not in STATUSES:
        out.append(f"{cid}: status {claim.get('status')!r} unknown")
    if claim.get("status") == "NOT_RUN" and not claim.get("reason"):
        out.append(f"{cid}: NOT_RUN carries its reason, always")
    if claim.get("status") == "PASS" and claim.get("kind") == "look":
        if not claim.get("artifact"):
            out.append(f"{cid}: a visual PASS with no artifact is a functional "
                       "claim wearing a visual verdict")
        else:
            if artifact_root is not None and \
                    not os.path.isfile(os.path.join(artifact_root, claim["artifact"])):
                out.append(f"{cid}: artifact {claim['artifact']} does not exist "
                           "— a named file that is not there proves nothing")
            if claim.get("artifact_state") != claim.get("state"):
                out.append(f"{cid}: artifact captured in state "
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


# --- the contact sheet (the visual look's rows) --------------------------------

def _filled(v):
    return isinstance(v, str) and bool(v.strip())


def _iso(v):
    if not _filled(v):
        return False
    try:
        datetime.fromisoformat(v.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def is_visual_row(c):
    return c.get("kind") == "look" and "axes" in c


def _large_text(v):
    return _filled(v) and v.strip().lower() not in DEFAULT_TEXT


def _narrow(v):
    if not _filled(v):
        return False
    s = v.lower()
    if any(w in s for w in ("narrow", "compact", " se", "iphone se", "small")):
        return True
    m = re.match(r"\s*(\d{2,5})\s*[x×]", s)
    return bool(m) and int(m.group(1)) <= NARROW_PX


def visual_row_problems(c, revision, approved):
    """Everything wrong with one state × axes row, beyond the rules every claim obeys."""
    out = []
    cid = c.get("id", "?")
    axes = c.get("axes")
    if not isinstance(axes, dict):
        return [f"{cid}: `axes` must be an object of {', '.join(AXES)}"]
    for a in AXES:
        if not _filled(axes.get(a)):
            out.append(f"{cid}: axes.{a} is missing — a frame whose {a} nobody recorded "
                       "cannot answer a claim about any one of them")
    for k in ("figma_frame", "baseline"):
        if c.get(k) is not None and not _filled(c.get(k)):
            out.append(f"{cid}: `{k}` is a path or URL, or null")
    diff = c.get("diff")
    if diff is not None:
        if not isinstance(diff, dict):
            out.append(f"{cid}: `diff` is an object or null")
            diff = None
        else:
            if diff.get("against") not in ("figma", "baseline"):
                out.append(f"{cid}: diff.against is {diff.get('against')!r} — it compares "
                           "against `figma` or `baseline`")
            if diff.get("status") not in DIFF_STATUS:
                out.append(f"{cid}: diff.status {diff.get('status')!r} is not one of "
                           f"{', '.join(DIFF_STATUS)}")
            if diff.get("status") == "NOT_RUN" and not _filled(diff.get("reason")):
                out.append(f"{cid}: a diff that did not run carries its reason")
    rubric = c.get("rubric", [])
    if not isinstance(rubric, list):
        out.append(f"{cid}: `rubric` must be a list")
        rubric = []
    g_fail = []
    for i, r in enumerate(rubric):
        if not isinstance(r, dict):
            out.append(f"{cid}: rubric[{i}] is not an object")
            continue
        rid = r.get("id") or f"rubric[{i}]"
        if not _filled(r.get("id")):
            out.append(f"{cid}: rubric[{i}] has no id")
        if r.get("type") not in RUBRIC_TYPES:
            out.append(f"{cid}: {rid}.type {r.get('type')!r} is not G, J or H")
        st = r.get("status")
        if st not in RUBRIC_STATUS:
            out.append(f"{cid}: {rid}.status {st!r} is not one of {', '.join(RUBRIC_STATUS)}")
        if st in ("FAIL", "unresolved"):
            t = r.get("triple")
            if not (isinstance(t, dict) and all(_filled(t.get(k))
                                                 for k in ("region", "defect", "fix"))):
                out.append(f"{cid}: {rid} is {st} without its triple — region, defect, fix. "
                           "A finding nobody can locate and act on is an impression")
        if r.get("type") == "J" and st in ("PASS", "FAIL") and not _filled(r.get("calibration")):
            out.append(f"{cid}: {rid} is a judge item reported {st} with no `calibration` — "
                       "until a labelled set exists and the judge's agreement with it is "
                       "measured, a J item is NOT_ASSESSED, not a verdict")
        if r.get("type") == "H" and st == "PASS" and not approved:
            out.append(f"{cid}: {rid} is a human item reported PASS on a sheet nobody "
                       "approved — only the person who reviewed the sheet can pass it")
        if r.get("type") == "G" and st == "FAIL":
            g_fail.append(rid)
    if c.get("status") == "PASS":
        cap = c.get("capture")
        if not isinstance(cap, dict):
            out.append(f"{cid}: a PASS frame carries its capture record "
                       f"({', '.join(CAPTURE)}) — a screenshot with no record is an image, "
                       "not evidence")
        else:
            for k in CAPTURE:
                if not _filled(cap.get(k)):
                    out.append(f"{cid}: capture.{k} is missing")
            if _filled(cap.get("captured_at")) and not _iso(cap["captured_at"]):
                out.append(f"{cid}: capture.captured_at {cap['captured_at']!r} is not "
                           "ISO-8601, so its staleness cannot be computed")
            if _filled(revision) and _filled(cap.get("revision")) and \
                    cap["revision"] != revision:
                out.append(f"{cid}: captured at {cap['revision']!r} while the sheet is for "
                           f"{revision!r} — a stale frame proves the revision before")
        if (c.get("figma_frame") or c.get("baseline")) and diff is None:
            out.append(f"{cid}: a frame with a reference ({'figma_frame' if c.get('figma_frame') else 'baseline'}) "
                       "and no `diff` — the comparison is the point of having the reference")
        if diff is not None and diff.get("status") == "FAIL":
            out.append(f"{cid}: PASS over a failing diff against {diff.get('against')} — "
                       "either the frame drifted, or a person approves a new baseline; "
                       "neither is a PASS written by the run")
        if g_fail:
            out.append(f"{cid}: PASS while gate item(s) {', '.join(g_fail)} FAIL — a "
                       "deterministic gate item is a floor the judge never overrides")
    return out


def coverage_gaps(rows, states):
    """Holes in the state × axes matrix. Pairwise over the axes, plus the mandatory pairs."""
    gaps = []
    seen_states = {c.get("state") for c in rows}
    for s in states:
        if s not in seen_states:
            gaps.append(f"state {s!r} has no frame — a hole in the matrix")
    ax = [c.get("axes") for c in rows if isinstance(c.get("axes"), dict)]
    if not ax:
        return gaps + ["no state × axes row at all"]
    if not any(_large_text(a.get("text")) for a in ax):
        gaps.append("the text axis never leaves its default — large text (200% / AX5) is a "
                    "mandatory column")
    darks = [a for a in ax if "dark" in str(a.get("theme", "")).lower()]
    if darks and any(_large_text(a.get("text")) for a in ax) and \
            not any(_large_text(a.get("text")) for a in darks):
        gaps.append("no frame is dark × large text — a mandatory pair")
    rtls = [a for a in ax if RTL.search(str(a.get("locale", "")))]
    if rtls and not any(_narrow(a.get("viewport")) for a in rtls):
        gaps.append("no frame is RTL × narrow — a mandatory pair")
    # Pairwise coverage: every value of one axis meets every value of every other axis in
    # SOME frame. The full cross product is what makes a sheet unreadable; pairs are the
    # smallest set that still catches a defect that appears only where one axis meets another.
    values = {k: sorted({str(a.get(k)) for a in ax if _filled(a.get(k))}) for k in AXES}
    for x, y in itertools.combinations(AXES, 2):
        have = {(str(a.get(x)), str(a.get(y))) for a in ax}
        for vx in values[x]:
            for vy in values[y]:
                if (vx, vy) not in have:
                    gaps.append(f"pairwise: no frame is {x}={vx} × {y}={vy}")
    return gaps


def sheet_report(doc, surface_class, artifact_root=None, states=(), require_approval=False):
    """(verdict, problems, notes) for a contact sheet at one surface class."""
    problems, notes = [], []
    if not isinstance(doc, dict) or doc.get("schema_version") != "browser-claims/1":
        return "FAIL", ["not a browser-claims/1 document — the contact sheet extends that "
                        "file, there is no second schema"], notes
    claims = doc.get("claims")
    if not isinstance(claims, list):
        return "FAIL", ["`claims` must be a list"], notes
    for c in claims:
        problems += claim_problems(c, artifact_root)
    for cid in suite_pass_closes_no_look(claims):
        problems.append(f"{cid}: a suite PASS cannot close a look claim with no artifact")
    rows = [c for c in claims if is_visual_row(c)]
    approved = _filled(doc.get("approved_by")) or _filled(doc.get("approved_at"))
    if rows or surface_class in GATED:
        for k in ("surface", "revision"):
            if not _filled(doc.get(k)):
                problems.append(f"the sheet names no `{k}` — a contact sheet is for one "
                                "surface at one revision")
        rr = doc.get("review_rounds")
        if not isinstance(rr, int) or isinstance(rr, bool) or rr < 0:
            problems.append("`review_rounds` must be a whole number — it is how passes are "
                            "measured, and a sheet that cannot say how many returns it took "
                            "cannot show the count falling")
    if approved and not (_filled(doc.get("approved_by")) and _iso(doc.get("approved_at"))):
        problems.append("an approval names who (`approved_by`) and when (`approved_at`, "
                        "ISO-8601) — half an approval is not one")
    if require_approval and not approved:
        problems.append("the sheet is not approved — at acceptance the contact sheet is the "
                        "human's one pass, and an unapproved sheet is a pass that did not "
                        "happen")
    if surface_class in GATED and not rows:
        problems.append(f"a {surface_class} surface with no state × axes row — the visual "
                        "look did not run, and on this class it is a gate")
    j_fail = set()
    pending = []
    for c in rows:
        problems += visual_row_problems(c, doc.get("revision"), approved)
        for r in c.get("rubric") or []:
            if isinstance(r, dict):
                if r.get("type") == "J" and r.get("status") == "FAIL":
                    j_fail.add(r.get("id"))
                if r.get("status") in ("uncertain", "unresolved"):
                    pending.append(f"{c.get('id')}:{r.get('id')} {r.get('status')}")
        if c.get("status") in ("NOT_RUN", "BLOCKED"):
            pending.append(f"{c.get('id')} {c.get('status')}")
    if surface_class == "flagship" and len(j_fail) > 2:
        problems.append(f"{len(j_fail)} judge items FAIL ({', '.join(sorted(map(str, j_fail)))}) "
                        "— the flagship profile admits at most two, each with its triple")
    if rows:
        gaps = coverage_gaps(rows, states)
        if surface_class == "flagship":
            problems += gaps
        elif surface_class in ("product", "ad"):
            hard = [g for g in gaps if not g.startswith("pairwise:")]
            problems += hard
            notes += [g for g in gaps if g.startswith("pairwise:")]
        else:
            notes += gaps
    if isinstance(doc.get("review_rounds"), int) and doc["review_rounds"] > 2 and not approved:
        notes.append(f"review_rounds is {doc['review_rounds']}: past the budget of two — the "
                     "open items go to the person as `unresolved`, not into another round")
    if pending:
        notes.append("for the person on the sheet: " + "; ".join(pending))
    if problems:
        return "FAIL", problems, notes
    # Honest on every class: a frame that did not run is NOT_RUN in the verdict as well as
    # in its row. Whether that blocks the stage is the class's business — on `internal`
    # the look is recommended, so the stage reads NOT_RUN and goes on, saying so.
    if any(c.get("status") in ("NOT_RUN", "BLOCKED") for c in rows):
        return "NOT_RUN", problems, notes
    return "PASS", problems, notes


# --- the director record --------------------------------------------------------

def _sections(text):
    """`## Heading` -> body, keyed by the heading's first word."""
    out = {}
    parts = re.split(r"^##[ \t]+(.+?)[ \t]*$", text, flags=re.M)
    for i in range(1, len(parts), 2):
        m = re.match(r"([A-Za-z]+)", parts[i].strip())
        if m:
            body = re.sub(r"<!--.*?-->", "", parts[i + 1], flags=re.S).strip()
            out.setdefault(m.group(1).lower(), body)
    return out


def _declared_class(text):
    head = text.split("\n## ", 1)[0]
    m = re.search(r"surface_class\**\s*:\s*`?\s*([a-z]+)", head, re.I)
    return m.group(1).lower() if m else None


def record_floor(text, surface_class):
    """(problems, declined) — the headings the class owes, present and filled."""
    problems = []
    sec = _sections(text)
    declared = _declared_class(text)
    if declared is None:
        problems.append("the record declares no `surface_class:` in its header")
    elif declared not in SURFACE_CLASSES:
        problems.append(f"the record's surface_class {declared!r} is not one of "
                        f"{', '.join(SURFACE_CLASSES)}")
    elif declared != surface_class:
        problems.append(f"the record says surface_class {declared!r} and the brief says "
                        f"{surface_class!r} — one of them is stale, and the gate profile "
                        "depends on which")
    mode_body = sec.get("mode", "")
    mode = (re.match(r"[`*_\s]*([A-Za-z]+)", mode_body) or [None, ""])[1].lower()
    if "mode" not in sec or not mode:
        problems.append("## Mode is missing or empty")
        return problems, False
    if mode not in MODES:
        problems.append(f"## Mode is {mode!r} — one of {', '.join(MODES)}")
    if mode == "declined":
        reason = re.sub(r"^[`*_\s]*declined[`*_\s:—-]*", "", mode_body, flags=re.I).strip()
        if len(reason.split()) < 3:
            problems.append("## Mode: declined carries no reason — a refusal passes the gate "
                            "only when it says why, in words a reader can disagree with")
        return problems, True
    for field in RECORD_FIELDS[surface_class]:
        body = sec.get(field.lower())
        if body is None:
            problems.append(f"## {field} is missing — the {surface_class} profile owes it")
        elif not body or (PLACEHOLDER.match(body) and
                          not (field in BARE_NA_OK and re.match(r"^n/?a\.?$", body, re.I))):
            problems.append(f"## {field} is empty ({body!r}) — a heading with nothing under "
                            "it is the fact of the track, not its trace")
    return problems, False


def _run_tool(cmd, flag, args, timeout=180):
    """("PASS"|"FAIL"|"NOT_RUN", detail). The tool is sheleg-design's CLI."""
    if cmd.strip().lower() == "none":
        return "NOT_RUN", "disabled with `none`"
    argv = shlex.split(cmd)
    try:
        h = subprocess.run(argv + ["--help"], capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return "NOT_RUN", f"`{argv[0]}` is not installed"
    except (OSError, subprocess.SubprocessError) as e:
        return "NOT_RUN", f"`{cmd} --help` could not run ({type(e).__name__})"
    if flag not in (h.stdout + h.stderr):
        return "NOT_RUN", (f"`{cmd}` does not offer {flag} — sheleg-design is not installed, "
                           "or older than that flag")
    try:
        r = subprocess.run(argv + [flag] + args, capture_output=True, text=True,
                           timeout=timeout)
    except (OSError, subprocess.SubprocessError) as e:
        return "NOT_RUN", f"`{cmd} {flag}` could not run ({type(e).__name__})"
    tail = (r.stdout + r.stderr).strip()[-1500:]
    if r.returncode == 0:
        return "PASS", tail
    if r.returncode == 1:
        return "FAIL", tail
    return "NOT_RUN", f"`{cmd} {flag}` exited {r.returncode}: {tail[-300:]}"


def cmd_record(a):
    if a.surface_class == "internal":
        return _emit(a, "record", "PASS", [], ["no director record is owed by an internal "
                                               "surface; the floor there is the linter"])
    try:
        text = open(a.path, encoding="utf-8").read()
    except OSError:
        return _emit(a, "record", "FAIL", [f"{a.path} does not exist — the VISUAL track "
                                           "leaves a director record, or a recorded refusal"],
                     [])
    problems, declined = record_floor(text, a.surface_class)
    status, detail = _run_tool(a.validator, "--check-record", [a.path])
    notes = [f"validator: {status}" + (f" — {detail}" if status != "PASS" else "")]
    if declined and not problems:
        notes.insert(0, "the visual track was declined, with its reason — a recorded "
                        "refusal passes")
    floor = "FAIL" if problems else "PASS"
    if status == "FAIL":
        problems.append("the record validator refused it: " + detail)
    verdict = "FAIL" if problems else "PASS"
    return _emit(a, "record", verdict, problems, notes,
                 extra={"floor": floor, "validator": status})


def cmd_sheet(a):
    try:
        doc = json.load(open(a.path, encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"visual_gate: cannot read {a.path} ({type(e).__name__})", file=sys.stderr)
        return 2
    states = [s for s in (a.states or "").split(",") if s.strip()]
    verdict, problems, notes = sheet_report(doc, a.surface_class, a.artifact_root, states,
                                            a.require_approval)
    return _emit(a, "sheet", verdict, problems, notes)


def cmd_lint(a):
    status, detail = _run_tool(a.linter, "--lint", [a.dir, "--json"])
    if status == "NOT_RUN":
        return _emit(a, "lint", "NOT_RUN", [], [detail])
    counts = {}
    try:
        for f in json.loads(detail[detail.index("["):]):
            counts[f.get("severity", "?")] = counts.get(f.get("severity", "?"), 0) + 1
    except (ValueError, AttributeError, TypeError):
        pass
    summary = ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "no findings parsed"
    if status == "FAIL":
        return _emit(a, "lint", "FAIL", [f"the project linter exited 1 ({summary})"], [])
    return _emit(a, "lint", "PASS", [], [f"findings by severity: {summary}"])


def _section(text, title):
    m = re.search(r"^(#{1,6})[ \t]+[^\n]*" + re.escape(title) + r"[^\n]*$", text, re.M | re.I)
    if not m:
        return None
    level = len(m.group(1))
    rest = text[m.end():]
    nxt = re.search(r"^#{1,%d}[ \t]" % level, rest, re.M)
    return rest[:nxt.start()] if nxt else rest


def cmd_filekeys(a):
    try:
        rec = open(a.record, encoding="utf-8").read()
        scr = open(a.screens, encoding="utf-8").read()
    except OSError as e:
        print(f"visual_gate: cannot read an input ({e.filename})", file=sys.stderr)
        return 2
    body = _section(rec, "Design tooling")
    recorded = sorted(set(FIGMA_KEY.findall(body if body is not None else rec)))
    used = sorted(set(FIGMA_KEY.findall(scr)))
    problems = []
    if used and not recorded:
        problems.append("frames link to Figma and the record names no file — the "
                        "destination was never decided, or was decided somewhere else")
    for k in used:
        if recorded and k not in recorded:
            problems.append(f"frame file key {k} is not a recorded file — a second file "
                            "nobody will open, holding real work")
    notes = [f"recorded: {', '.join(recorded) or 'none'}",
             f"linked from screens: {', '.join(used) or 'none'}"]
    return _emit(a, "filekeys", "FAIL" if problems else "PASS", problems, notes)


# --- token-name drift: Figma variables against the pack's CSS custom properties ---
# A token that has one name in the file and another in code has quietly split in two, and
# nothing downstream notices: `get_design_context` hands the agent the Figma name, the agent
# writes a raw value because no property answers to it, and the screen still looks right.

CSS_DECL = re.compile(r"(?<![\w-])(--[A-Za-z0-9_-]+)\s*:")
CS_PROP = re.compile(r"\s*(?:var\(\s*)?(--[A-Za-z0-9_-]+)\s*(?:,[^)]*)?\)?\s*")
# Keys a variable's own record can carry. A dict value with none of them is a token GROUP
# (a nested design-token tree), not a variable, and reading its key as a name would compare
# the code against the group names.
VAR_KEYS = ("codeSyntax", "value", "$value", "resolvedType", "type", "valuesByMode")


def css_property(name):
    """The CSS custom property a Figma variable name maps to when it carries no code syntax:
    `Color/Text Muted` → `--color-text-muted`, `fontSize/bodyLarge` → `--font-size-body-large`.
    A convention, not a law — WEB code syntax, where the file sets it, overrides it."""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
    return "--" + re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()


def figma_variables(doc):
    """[(name, web_code_syntax or None)] from a variable export. Accepts the map
    `get_variable_defs` returns (name → value), the REST export (`meta.variables`, id →
    variable) and a `variables` list. Raises ValueError on any other shape."""
    if isinstance(doc, dict) and isinstance(doc.get("meta"), dict) and "variables" in doc["meta"]:
        doc = doc["meta"]["variables"]
    elif isinstance(doc, dict) and isinstance(doc.get("variables"), (list, dict)):
        doc = doc["variables"]

    def one(v):
        cs = v.get("codeSyntax")
        return v["name"], (cs.get("WEB") if isinstance(cs, dict) else None)

    if isinstance(doc, list):
        if not all(isinstance(v, dict) and isinstance(v.get("name"), str) for v in doc):
            raise ValueError("a `variables` list whose items are not {name, …} objects")
        return [one(v) for v in doc]
    if not isinstance(doc, dict):
        raise ValueError(f"a {type(doc).__name__}, not a variable map")
    if doc and all(isinstance(v, dict) and isinstance(v.get("name"), str) for v in doc.values()):
        return [one(v) for v in doc.values()]
    out = []
    for k, v in doc.items():
        if isinstance(v, dict):
            if not any(key in v for key in VAR_KEYS):
                raise ValueError(f"{k!r} holds a group, not a variable — a nested token tree")
            cs = v.get("codeSyntax")
            out.append((k, cs.get("WEB") if isinstance(cs, dict) else None))
        elif isinstance(v, list):
            raise ValueError(f"{k!r} holds a list, not a variable's value")
        else:
            out.append((k, None))
    return out


def css_properties(text):
    """Every custom property the token file DECLARES. Comments are stripped first, and a
    `var(--x)` use is not a declaration."""
    return set(CSS_DECL.findall(re.sub(r"/\*.*?\*/", "", text, flags=re.S)))


def token_drift(variables, props):
    """(problems, report) — names in one side and not the other, and code syntax that
    disagrees with the property the token file actually has."""
    problems, figma_only, syntax, used, owner = [], [], [], set(), {}
    for name, cs in variables:
        derived = css_property(name)
        target = derived
        if cs is not None:
            m = CS_PROP.fullmatch(cs)
            if not m:
                syntax.append(f"{name}: WEB code syntax {cs!r} is not a CSS custom property")
                continue
            target = m.group(1)
        if target in owner:
            problems.append(f"{owner[target]!r} and {name!r} both map to {target} — one "
                            "property cannot hold both")
            continue
        owner[target] = name
        if target in props:
            used.add(target)
        elif cs is not None and derived in props:
            used.add(derived)
            syntax.append(f"{name}: code syntax names {target}, and the token file calls it "
                          f"{derived}")
        else:
            figma_only.append(f"{name} → {target}")
    css_only = sorted(props - used)
    problems += [f"in Figma, not in the token file: {x}" for x in figma_only]
    problems += [f"in the token file, not in Figma: {x}" for x in css_only]
    problems += [f"code syntax: {x}" for x in syntax]
    return problems, {"figma_only": figma_only, "css_only": css_only, "code_syntax": syntax,
                      "matched": len(used)}


def cmd_tokens(a):
    try:
        css = open(a.css, encoding="utf-8").read()
    except OSError as e:
        print(f"visual_gate: cannot read the token file {a.css} ({type(e).__name__})",
              file=sys.stderr)
        return 2
    if not os.path.isfile(a.figma):
        return _emit(a, "tokens", "NOT_RUN", [], [
            f"no Figma variable export at {a.figma} — export it (`get_variable_defs`, or the "
            "REST variables endpoint) and run again; until then the drift is unmeasured"])
    try:
        doc = json.load(open(a.figma, encoding="utf-8"))
    except (OSError, ValueError) as e:  # JSONDecodeError and UnicodeDecodeError included
        print(f"visual_gate: cannot read {a.figma} ({type(e).__name__})", file=sys.stderr)
        return 2
    try:
        variables = figma_variables(doc)
    except ValueError as e:
        print(f"visual_gate: {a.figma} is not a variable export — {e}", file=sys.stderr)
        return 2
    if not variables:
        return _emit(a, "tokens", "NOT_RUN", [], [
            f"{a.figma} holds no variables — there is nothing to compare, and nothing "
            "compared is not a pass"])
    props = css_properties(css)
    problems, rep = token_drift(variables, props)
    notes = [f"{len(variables)} Figma variable(s), {len(props)} CSS custom propert"
             f"{'y' if len(props) == 1 else 'ies'}, {rep['matched']} matched"]
    return _emit(a, "tokens", "FAIL" if problems else "PASS", problems, notes, extra=rep)


EXIT = {"PASS": 0, "FAIL": 1, "NOT_RUN": 3}


def _emit(a, check, verdict, problems, notes, extra=None):
    if getattr(a, "json", False):
        out = {"check": check, "verdict": verdict, "problems": problems, "notes": notes}
        out.update(extra or {})
        print(json.dumps(out, ensure_ascii=False))
    else:
        cls = getattr(a, "surface_class", None)
        print(f"{check}: {verdict}" + (f" — class {cls}" if cls else ""))
        for p in problems:
            print(f"  ✗ {p}")
        for n in notes:
            print(f"  · {n}")
    return EXIT[verdict]


def main(argv):
    p = argparse.ArgumentParser(prog="visual_gate.py",
                                description="The visual half of the gates; NOT_RUN is never PASS.")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record", help="stage 3: the director record carries its fields")
    r.add_argument("path")
    r.add_argument("--class", dest="surface_class", required=True, choices=SURFACE_CLASSES)
    r.add_argument("--validator", default=DEFAULT_TOOL,
                   help=f"the record validator's command (default `{DEFAULT_TOOL}`), or none")
    r.add_argument("--json", action="store_true")
    s = sub.add_parser("sheet", help="stages 6 and 10: the contact sheet")
    s.add_argument("path")
    s.add_argument("--class", dest="surface_class", required=True, choices=SURFACE_CLASSES)
    s.add_argument("--artifact-root", help="where the frames live, so a named file is checked")
    s.add_argument("--states", help="comma-separated SCR states the matrix must cover")
    s.add_argument("--require-approval", action="store_true",
                   help="stage 10: the sheet carries the person's approval")
    s.add_argument("--json", action="store_true")
    li = sub.add_parser("lint", help="stages 5–6: sheleg-design's project linter")
    li.add_argument("dir")
    li.add_argument("--linter", default=DEFAULT_TOOL)
    li.add_argument("--json", action="store_true")
    f = sub.add_parser("filekeys", help="stage 3: frame links stay in the recorded files")
    f.add_argument("--record", required=True)
    f.add_argument("--screens", required=True)
    f.add_argument("--json", action="store_true")
    t = sub.add_parser("tokens", help="stages 5–6: Figma variable names against the CSS "
                                      "custom properties of the pack's token file")
    t.add_argument("--figma", required=True,
                   help="the variable export (get_variable_defs JSON, or the REST export)")
    t.add_argument("--css", required=True, help="the pack's token file")
    t.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    return {"record": cmd_record, "sheet": cmd_sheet, "lint": cmd_lint,
            "filekeys": cmd_filekeys, "tokens": cmd_tokens}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
