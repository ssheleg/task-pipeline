#!/usr/bin/env python3
"""DIET-1020 D: the retro floor has a byte budget, and `retro_budget.py` enforces it.

Measured 2026-10-20: the floor stage 0 reads in full (standing instructions plus run
stamps) ran from ~3k to ~76k tokens across ~50 projects, and this repository's own was
27 620 bytes. The doctrine capped rows at ten and never their size.

Every plant below asserts it changed the text it is planted in before the verdict is
read (learned.md rule 4), and each over-budget plant must FAIL with exit 1.
Standard library only.
"""
import os
import pathlib
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
SK = ROOT / "plugins/task-pipeline/skills/task-pipeline"
SCRIPT = SK / "scripts/retro_budget.py"
TEMPLATE = SK / "templates/retro.md"

failures = []


def case(name):
    def wrap(fn):
        try:
            fn()
            print("  ok  " + name)
        except AssertionError as exc:
            failures.append(name)
            print("FAIL  %s: %s" % (name, exc))
        return fn
    return wrap


def run(*args):
    r = subprocess.run([sys.executable, str(SCRIPT)] + list(args),
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def plant(text, old, new):
    assert text.count(old) == 1, "the plant's needle %r is not unique in the seed" % old[:40]
    out = text.replace(old, new)
    assert out != text, "the plant changed nothing"
    return out


def write(d, text, name="retro.md"):
    p = pathlib.Path(d) / name
    p.write_text(text, encoding="utf-8")
    return str(p)


SEED = TEMPLATE.read_text(encoding="utf-8")
ROW_NEEDLE = "| … | … (one line; links the archive entry) |"
STAMP_NEEDLE = "| 1 entry · 7 standing (was 9) · retired 3 · added 1 |"


@case("the shipped template is within budget and prints bytes and bytes/4 tokens")
def _():
    code, out = run("check", "--retro", str(TEMPLATE))
    assert code == 0, out
    assert "bytes · ~" in out and "tokens (bytes/4)" in out, out


@case("an over-long standing row fails, and names the row")
def _():
    with tempfile.TemporaryDirectory() as d:
        bad = plant(SEED, ROW_NEEDLE, "| … | " + "x" * 700 + " |")
        code, out = run("check", "--retro", write(d, bad))
        assert code == 1 and "standing row R-001" in out, out


@case("an over-long run stamp fails, and names its commit")
def _():
    with tempfile.TemporaryDirectory() as d:
        bad = plant(SEED, STAMP_NEEDLE, "| " + "a prune that retired nothing. " * 12 + " |")
        code, out = run("check", "--retro", write(d, bad))
        assert code == 1 and "stamp 2026-05-04" in out, out


@case("a floor over the byte budget fails even when every row is short")
def _():
    with tempfile.TemporaryDirectory() as d:
        bad = plant(SEED, "## Run stamps\n", "## Run stamps\n\n" + ("prune note. " * 60 + "\n\n") * 20)
        code, out = run("check", "--retro", write(d, bad))
        assert code == 1 and "over the budget of 12000" in out, out


@case("a missing floor section is `could not measure` (exit 2), never a pass")
def _():
    with tempfile.TemporaryDirectory() as d:
        bad = plant(SEED, "## Run stamps\n", "## Stamps, renamed\n")
        code, out = run("check", "--retro", write(d, bad))
        assert code == 2 and "could not measure" in out, out
        code, out = run("check", "--retro", os.path.join(d, "absent.md"))
        assert code == 2, out


@case("migrate --write moves narrative verbatim, hash-proved, and brings the floor in budget")
def _():
    with tempfile.TemporaryDirectory() as d:
        long_stamp = "| " + "the release narrative that belongs in the archive. " * 10 + " |"
        bad = plant(SEED, STAMP_NEEDLE, long_stamp)
        long_because = "the whole story of the incident, " * 30
        bad = plant(bad, "… (one line; links the archive entry)", long_because)
        p = write(d, bad)
        code, out = run("migrate", "--retro", p)
        assert code == 0 and "dry run" in out, out
        assert pathlib.Path(p).read_text(encoding="utf-8") == bad, "a dry run wrote the retro"
        arch = os.path.join(d, "retro", "2026-Q4.md")
        code, out = run("migrate", "--retro", p, "--archive", arch, "--write")
        assert code == 0, out
        after = pathlib.Path(p).read_text(encoding="utf-8")
        archived = pathlib.Path(arch).read_text(encoding="utf-8")
        assert long_because.strip() in archived, "the Because cell did not move verbatim"
        moved_rows = [l for l in bad.split("\n") if l.startswith("| 2026-05-04 |")]
        assert moved_rows and moved_rows[0] in archived, "the stamp row did not move verbatim"
        assert "sha256:" in after and long_because.strip() not in after, after[-600:]
        code, out = run("check", "--retro", p)
        assert code == 0, out
        code, out = run("verify", "--retro", p)
        assert code == 0, out
        # tamper with the archived text: the pointer must stop proving it
        tampered = plant(archived, long_because.strip(), long_because.strip() + " edited")
        pathlib.Path(arch).write_text(tampered, encoding="utf-8")
        code, out = run("verify", "--retro", p)
        assert code == 1 and "unproved" in out, out


@case("a stamp whose narrative holds a `|` keeps the table's column count after migrate")
def _():
    with tempfile.TemporaryDirectory() as d:
        bad = plant(SEED, STAMP_NEEDLE, "| a | b | " + "narrative with a pipe | inside. " * 12 + " |")
        p = write(d, bad)
        code, out = run("migrate", "--retro", p, "--write")
        assert code == 0, out
        row = [l for l in pathlib.Path(p).read_text(encoding="utf-8").split("\n")
               if l.startswith("| 2026-05-04 |")][0]
        assert row.count("|") == 6, "the migrated stamp has %d pipes, the table 6: %s" % (row.count("|"), row)


@case("an instruction too long to shorten by moving its story stays a failure after migrate")
def _():
    with tempfile.TemporaryDirectory() as d:
        bad = plant(SEED, "| R-001 | 2026-05-04 · `<topic>` | `<sha>` | … |",
                    "| R-001 | 2026-05-04 · `<topic>` | `<sha>` | " + "do this. " * 80 + " |")
        p = write(d, bad)
        code, out = run("migrate", "--retro", p, "--write")
        assert code == 1 and "still over" in out, out


@case("this repository's own retro floor is within budget and every pointer is proved")
def _():
    retro = ROOT / "docs/evidence/retro.md"
    code, out = run("check", "--retro", str(retro))
    assert code == 0, out
    code, out = run("verify", "--retro", str(retro))
    assert code == 0, out


if failures:
    print("\n%d failure(s)" % len(failures))
    sys.exit(1)
print("\nall green")
