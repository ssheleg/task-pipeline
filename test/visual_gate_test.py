#!/usr/bin/env python3
"""Fixtures for `scripts/visual_gate.py` record / lint / filekeys — stdlib only.

The contact sheet's fixtures live in `test/browser_claims_test.py`, beside the file it
extends. This one covers the other three verbs, and each fixture plants the way the
check could be fooled:

- `record` — stage 3's VISUAL track leaves a director record, and the gate reads its
  FIELDS for the brief's surface class, not the fact that the track ran. A recorded
  refusal passes. Where sheleg-design's own validator is absent or too old, the floor
  still runs and the validator reads NOT_RUN — never PASS.
- `lint` — sheleg-design's project linter, NOT_RUN (exit 3) where it cannot run.
- `filekeys` — every frame link stays inside the files the project recorded, one per
  surface (App / Web / ASO), never a second file nobody opens.

The validator and linter are faked by a script that answers `--help` the way the real
CLI would, so the fixtures pin the contract (flag present? exit 0 / 1?) and not a
network install.
"""
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKILL = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline")
VG = os.path.join(SKILL, "scripts", "visual_gate.py")

failures = []


def case(name, ok, detail=""):
    if ok:
        print(f"  ok  {name}")
    else:
        failures.append(name)
        print(f"FAIL  {name}: {detail}")


TMP = tempfile.mkdtemp(prefix="visual-gate-")


def write(name, text):
    p = os.path.join(TMP, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


def run(*args):
    r = subprocess.run([sys.executable, VG, *args], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


FIELDS = {
    "Brief": "Landing for the scheduling app. Job: book a first call in under a minute. "
             "Constraint: one screen above the fold. Falsifier: a visitor cannot find the "
             "price without scrolling. Scenario SCN-007.",
    "Mode": "new",
    "Taste": "Take the editorial grid and quiet type of a print schedule; forbid gradients "
             "and glass cards.",
    "References": "1. https://linear.app — density\n2. https://cal.com — booking flow\n"
                  "3. https://stripe.com — price table\n4. https://vercel.com — hero rhythm\n"
                  "5. https://arc.net — motion restraint",
    "Cast": "sheleg-design → visual; copywriting → strings; break-ui → worst-case data",
    "Fork": "yes — rubric written first; A editorial, B instrument, C calm. A won; took B's "
            "meter.",
    "Rubric": "R1 contrast ≥ 4.5:1 on every text token; R7 the theme traces to the brief.",
    "Critique": "hero → headline wraps to four lines at 375 → shorten to six words",
    "Markers": "npx sheleg-design-skill --lint src --json at 4dbb96c: S1 0, S2 1, S3 3",
    "Alignment": "falsifier checked on the 375 frame: price visible above the fold — holds",
    "Quality": "| check | value |\n|---|---|\n| LCP | 1.9 s |",
    "Signature": "the calendar grid assembles from the hero's rule lines on first load",
    "Surfaces": "a widget for the next booking — deferred, web only this release",
    "Haptics": "n/a",
    "ADA": "Delight and Fun; R1–R25 graded on the contact sheet, J items NOT_ASSESSED",
    "Open": "whether the price table shows annual billing first — the operator's call",
}


def record(cls="flagship", drop=(), override=None, header=True):
    body = {**FIELDS, **(override or {})}
    parts = [f"surface_class: {cls}\n" if header else "", "# Director record — landing\n"]
    for k, v in body.items():
        if k in drop:
            continue
        parts.append(f"\n## {k}\n\n{v}\n")
    return "".join(parts)


FAKE = write("fake_tool.py", '''import os, sys
mode = os.environ.get("FAKE_MODE", "ok")
if "--help" in sys.argv:
    print("usage: sheleg-design-skill " + ("" if mode == "old" else "--check-record <file> --lint <dir>"))
    sys.exit(0)
if "--check-record" in sys.argv:
    sys.exit(1 if mode == "refuse" else 0)
if "--lint" in sys.argv:
    if mode == "refuse":
        print(__import__("json").dumps([{"id": "V001", "rule": "lint:purple-gradient", "severity": "S1",
                                          "file": "a.css", "line": 3, "snippet": "x"}]))
        sys.exit(1)
    print("[]"); sys.exit(0)
''')
TOOL = f"{sys.executable} {FAKE}"


def with_mode(mode, *args):
    env = dict(os.environ, FAKE_MODE=mode)
    r = subprocess.run([sys.executable, VG, *args], capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr


def main():
    # --- record: the floor, by class -------------------------------------------------
    full = write("full.md", record())
    code, out = run("record", full, "--class", "flagship", "--validator", "none")
    case("a full flagship record passes the floor, and the absent validator says NOT_RUN",
         code == 0 and "validator: NOT_RUN" in out and "validator: PASS" not in out, out)

    no_rubric = write("no-rubric.md", record(drop=("Rubric",)))
    code, out = run("record", no_rubric, "--class", "flagship", "--validator", "none")
    case("a flagship record without Rubric fails the gate, and the field is named",
         code == 1 and "## Rubric is missing" in out, out)

    empty_rubric = write("empty-rubric.md", record(override={"Rubric": "TBD"}))
    code, out = run("record", empty_rubric, "--class", "flagship", "--validator", "none")
    case("a heading with a placeholder under it is empty, not filled",
         code == 1 and "## Rubric is empty" in out, out)

    product = write("product.md", record("product", drop=("Rubric", "Taste", "Cast", "Fork",
                                                          "Critique", "Signature")))
    code, out = run("record", product, "--class", "product", "--validator", "none")
    case("the product profile owes the short set: no Rubric is not a failure there",
         code == 0, out)
    no_markers = write("product-no-markers.md", record("product", drop=("Markers",)))
    code, out = run("record", no_markers, "--class", "product", "--validator", "none")
    case("the product profile still owes Markers", code == 1 and "## Markers" in out, out)

    ad = write("ad.md", record("ad", drop=("ADA",)))
    code, out = run("record", ad, "--class", "ad", "--validator", "none")
    case("the ad profile owes the ADA field (its rubric profile and safe zones)",
         code == 1 and "## ADA" in out, out)

    mismatch = write("mismatch.md", record("product"))
    code, out = run("record", mismatch, "--class", "flagship", "--validator", "none")
    case("a record whose class disagrees with the brief is refused",
         code == 1 and "one of them is stale" in out, out)

    headless = write("headless.md", record(header=False))
    code, out = run("record", headless, "--class", "flagship", "--validator", "none")
    case("a record that declares no surface_class is refused",
         code == 1 and "declares no `surface_class:`" in out, out)

    bad_mode = write("bad-mode.md", record(override={"Mode": "vibes"}))
    code, out = run("record", bad_mode, "--class", "flagship", "--validator", "none")
    case("a Mode outside new / redesign / update / audit / declined is refused",
         code == 1 and "## Mode is 'vibes'" in out, out)

    declined = write("declined.md", "surface_class: flagship\n\n## Mode\n\ndeclined — the "
                     "operator said «без дизайна»: this release ships the existing pack "
                     "unchanged\n")
    code, out = run("record", declined, "--class", "flagship", "--validator", "none")
    case("a recorded refusal (Mode: declined + reason) still passes", code == 0, out)
    bare = write("declined-bare.md", "surface_class: flagship\n\n## Mode\n\ndeclined\n")
    code, out = run("record", bare, "--class", "flagship", "--validator", "none")
    case("a refusal with no reason is a silence, and is refused",
         code == 1 and "carries no reason" in out, out)

    code, out = run("record", os.path.join(TMP, "absent.md"), "--class", "product",
                    "--validator", "none")
    case("no record at all fails a product surface", code == 1 and "does not exist" in out, out)
    code, out = run("record", os.path.join(TMP, "absent.md"), "--class", "internal",
                    "--validator", "none")
    case("an internal surface owes no record", code == 0, out)

    # --- record: the validator, where it exists -------------------------------------
    code, out = with_mode("ok", "record", full, "--class", "flagship", "--validator", TOOL)
    case("an installed validator that accepts the record reads PASS",
         code == 0 and "validator: PASS" in out, out)
    code, out = with_mode("refuse", "record", full, "--class", "flagship", "--validator", TOOL)
    case("an installed validator that refuses the record fails the gate",
         code == 1 and "validator refused" in out, out)
    code, out = with_mode("old", "record", full, "--class", "flagship", "--validator", TOOL)
    case("a validator older than --check-record is NOT_RUN, never PASS",
         code == 0 and "validator: NOT_RUN" in out and "older than" in out, out)
    code, out = run("record", full, "--class", "flagship", "--validator",
                    os.path.join(TMP, "no-such-binary"))
    case("a missing validator binary is NOT_RUN with the reason",
         code == 0 and "validator: NOT_RUN" in out and "not installed" in out, out)
    code, out = run("record", full, "--class", "flagship", "--validator", "none", "--json")
    rep = json.loads(out)
    case("--json separates the floor from the validator",
         rep["floor"] == "PASS" and rep["validator"] == "NOT_RUN", rep)

    # --- lint ------------------------------------------------------------------------
    code, out = with_mode("ok", "lint", TMP, "--linter", TOOL)
    case("the project linter that finds no S1 reads PASS", code == 0, out)
    code, out = with_mode("refuse", "lint", TMP, "--linter", TOOL)
    case("the project linter that exits 1 fails, with its severity count",
         code == 1 and "S1 1" in out, out)
    code, out = with_mode("old", "lint", TMP, "--linter", TOOL)
    case("a linter that does not offer --lint is NOT_RUN — exit 3, never 0",
         code == 3 and "NOT_RUN" in out, out)

    # --- filekeys: one file per surface, all recorded --------------------------------
    rec = write("foundation.md", "# Foundation\n\n## Design tooling\n\nFigma: on\n\n"
                "- App: https://www.figma.com/design/AAAAAAAAAAAAAAAAAAAAAA/App\n"
                "- Web: https://www.figma.com/design/BBBBBBBBBBBBBBBBBBBBBB/Web\n"
                "- ASO: https://www.figma.com/design/CCCCCCCCCCCCCCCCCCCCCC/ASO\n\n"
                "## Personas\n\nSee https://www.figma.com/design/ZZZZZZZZZZZZZZZZZZZZZZ/old\n")
    ok_scr = write("screens-ok.md",
                   "SCR-01 https://www.figma.com/design/AAAAAAAAAAAAAAAAAAAAAA/App?node-id=1-2\n"
                   "SCR-02 https://www.figma.com/design/BBBBBBBBBBBBBBBBBBBBBB/Web?node-id=3-4\n")
    code, out = run("filekeys", "--record", rec, "--screens", ok_scr)
    case("frames in two of the recorded surface files pass — a set, not one key",
         code == 0, out)
    stray = write("screens-stray.md", open(ok_scr).read() +
                  "SCR-03 https://www.figma.com/design/ZZZZZZZZZZZZZZZZZZZZZZ/old?node-id=9\n")
    code, out = run("filekeys", "--record", rec, "--screens", stray)
    case("a frame in a file outside the recorded set is refused, even one the doc mentions "
         "outside Design tooling", code == 1 and "ZZZZZZZZZZ" in out, out)
    norec = write("foundation-none.md", "# Foundation\n\n## Design tooling\n\nFigma: on\n")
    code, out = run("filekeys", "--record", norec, "--screens", ok_scr)
    case("frames with no recorded file at all are refused",
         code == 1 and "names no file" in out, out)

    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        import shutil
        shutil.rmtree(TMP, ignore_errors=True)
