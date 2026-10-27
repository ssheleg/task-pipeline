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
import re
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
        pipes = len(re.findall(r"(?<!\\)\|", row))   # an escaped `\|` is a cell's text
        assert pipes == 6, "the migrated stamp has %d pipes, the table 6: %s" % (pipes, row)


@case("an instruction too long to shorten by moving its story stays a failure after migrate")
def _():
    with tempfile.TemporaryDirectory() as d:
        bad = plant(SEED, "| R-001 | 2026-05-04 · `<topic>` | `<sha>` | … |",
                    "| R-001 | 2026-05-04 · `<topic>` | `<sha>` | " + "do this. " * 80 + " |")
        p = write(d, bad)
        code, out = run("migrate", "--retro", p, "--write")
        assert code == 1 and "still over" in out, out


# B-244 (sshlg-skills, 2026-10-21): an older retro writes its standing instructions as a
# numbered list and its run stamps as `- **date — title**` narrative items under a table.
# The check read that floor as `standing 0/10` and `migrate` answered `nothing to move`
# on a 103,737-byte floor with 89 stamps.
def legacy(stamps=14, table_first=False, prose=True, long_items=True):
    std = []
    for n in range(1, 4):
        body = ("   the incident, told in full. " * (30 if long_items else 1)).rstrip()
        std.append("%d. **(2026-08-1%d) Rule number %d holds.** %s\n%s *(Retire when rule %d "
                   "is a check, or after five run stamps without firing.)*" % (n, n, n, "why. " * 3, body, n))
    items = ["- **2026-09-%02d — run %d** (base `abc%04d`). %s" % (k + 1, k, k, "narrative. " * 40)
             for k in range(stamps)]
    if not table_first:
        items.reverse()            # newest first, as the sshlg-skills retro is written
    table = ["| Date | Task | Commit | Diverged? |", "|---|---|---|---|",
             "| 2026-08-16 (one) | B-1: a table stamp | `aaa` | no |",
             "| 2026-08-17 (two) | B-2: a table stamp | `bbb` | no |"]
    para = ["", "**Prune, 2026-08-14.** Nine held, and here is why. " * 3] if prose else []
    return "\n".join(["# Retro", "", "## Standing instructions", "", "Hard cap: ten.", ""]
                     + "\n\n".join(std).split("\n")
                     + ["", "## Retired", "", "- 2026-08-13 #3 retired on its cold trigger.", "",
                        "## Run stamps", ""] + "\n\n".join(items).split("\n") + [""] + table
                     + para + ["", "## Recent log", "", "queried, not read.", ""])


@case("B-244: a numbered-list floor counts its standing rows and names the long one")
def _():
    with tempfile.TemporaryDirectory() as d:
        code, out = run("check", "--retro", write(d, legacy()))
        assert code == 1, out
        assert "standing 3/10 rows (numbered list)" in out, out
        assert "standing row #1 is" in out and "16 run stamps, over the cap of 10" in out, out


@case("B-244: migrate keeps the rule and its retire trigger, moves the story verbatim, and is lossless")
def _():
    with tempfile.TemporaryDirectory() as d:
        seed = legacy()
        p = write(d, seed)
        arch = os.path.join(d, "retro", "2026-Q4.md")
        code, out = run("migrate", "--retro", p, "--archive", arch, "--write")
        assert code == 0, out
        after = pathlib.Path(p).read_text(encoding="utf-8")
        archived = pathlib.Path(arch).read_text(encoding="utf-8")
        assert "1. **(2026-08-11) Rule number 1 holds.** *(Retire when rule 1 is a check" in after, after[:900]
        lost = [l for l in seed.split("\n") if l.strip() and l not in after and l not in archived]
        assert not lost, "lines lost by migrate: %r" % lost[:3]
        for name in ("## Retired", "## Recent log", "queried, not read."):
            assert after.count(name) == 1, "%s changed outside the floor" % name
        code, out = run("check", "--retro", p)
        assert code == 0, out
        code, out = run("verify", "--retro", p)
        assert code == 0, out


@case("B-244: the oldest stamps rotate by their date, whichever way round the list is written")
def _():
    for table_first in (False, True):
        with tempfile.TemporaryDirectory() as d:
            p = write(d, legacy(table_first=table_first))
            code, out = run("migrate", "--retro", p, "--write")
            assert code == 0, out
            after = pathlib.Path(p).read_text(encoding="utf-8")
            kept = sorted(int(x) for x in re.findall(r"- \*\*2026-09-(\d\d) — run", after))
            assert kept == list(range(5, 15)), "kept %r, not the ten newest" % kept
            assert "| 2026-08-16 (one)" not in after and "| Date | Task" not in after, \
                "a rotated table left rows or a bare header behind"
            assert re.search(r"Rotated out: 6 oldest run stamps, verbatim in retro/\d{4}-Q\d\.md sha256:", after), after


@case("B-246: repeated rotations into one archive keep one pointer line, losslessly")
def _():
    with tempfile.TemporaryDirectory() as d:
        p = write(d, legacy())
        arch = os.path.join(d, "retro", "2026-Q4.md")
        code, out = run("migrate", "--retro", p, "--archive", arch, "--write")
        assert code == 0, out
        first = pathlib.Path(p).read_text(encoding="utf-8")
        newer = "".join("- **2026-09-%d — run %d** (base `abc%04d`). newer.\n\n" % (k, k, k) for k in (21, 20))
        grown = plant(first, "- **2026-09-14 — run 13**", newer + "- **2026-09-14 — run 13**")
        pathlib.Path(p).write_text(grown, encoding="utf-8")
        code, out = run("migrate", "--retro", p, "--archive", arch, "--write")
        assert code == 0, out
        after = pathlib.Path(p).read_text(encoding="utf-8")
        ptr = re.findall(r"^Rotated out: (\d+) oldest run stamps, verbatim in (\S+) sha256:(\w+)$", after, re.M)
        assert len(ptr) == 1 and ptr[0][0] == "8", "one line naming all 8 rotated stamps, got %r" % ptr
        archived = pathlib.Path(arch).read_text(encoding="utf-8")
        lost = [l for l in grown.split("\n") if l.strip() and not l.startswith("Rotated out: ")
                and l not in after and l not in archived]
        assert not lost, "lines lost by the second rotation: %r" % lost[:3]
        sys.path.insert(0, str(SK / "scripts"))
        import retro_budget as rb
        block = rb.archived_text(arch, ptr[0][2])
        assert block and "run 0**" in block[1] and "run 5**" in block[1] and "(one)" in block[1], \
            "the pointed block does not hold every rotated stamp of the quarter"
        assert len(after) <= len(first) + len(newer) - 2 * len("- **2026-09-0X — run X** (base `abc000X`). ") , \
            "the floor grew by a pointer line"
        code, out = run("verify", "--retro", p)
        assert code == 0, out
        # A pointer into another quarter's archive is that quarter's line: it stays.
        third = plant(after, "- **2026-09-21 — run 21**", "- **2026-09-23 — run 23** (base `abc0023`). q.\n\n- **2026-09-21 — run 21**")
        pathlib.Path(p).write_text(third, encoding="utf-8")
        code, out = run("migrate", "--retro", p, "--archive", os.path.join(d, "retro", "2027-Q1.md"), "--write")
        assert code == 0, out
        lines = re.findall(r"^Rotated out: .*$", pathlib.Path(p).read_text(encoding="utf-8"), re.M)
        assert len(lines) == 2 and any("2026-Q4" in l for l in lines) and any("2027-Q1" in l for l in lines), lines


@case("B-246: a rotation line whose block no longer resolves is not merged away")
def _():
    with tempfile.TemporaryDirectory() as d:
        p = write(d, legacy())
        arch = os.path.join(d, "retro", "2026-Q4.md")
        code, out = run("migrate", "--retro", p, "--archive", arch, "--write")
        assert code == 0, out
        first = pathlib.Path(p).read_text(encoding="utf-8")
        old = re.search(r"^Rotated out: .*$", first, re.M).group(0)
        text = pathlib.Path(arch).read_text(encoding="utf-8")
        pathlib.Path(arch).write_text(plant(text, "run 0** (base", "run 0** (BASE"), encoding="utf-8")
        grown = plant(first, "- **2026-09-14 — run 13**", "- **2026-09-21 — run 21** (base `abc0021`). n.\n\n- **2026-09-14 — run 13**")
        pathlib.Path(p).write_text(grown, encoding="utf-8")
        code, out = run("migrate", "--retro", p, "--archive", arch, "--write")
        assert "does not resolve" in out, out
        after = pathlib.Path(p).read_text(encoding="utf-8")
        assert old in after and len(re.findall(r"^Rotated out: ", after, re.M)) == 2, \
            "an unprovable pointer was dropped instead of kept"


@case("B-244: loose prune prose moves only when the floor is over budget")
def _():
    with tempfile.TemporaryDirectory() as d:
        small = legacy(stamps=3, long_items=False)
        small = small.replace("narrative. " * 40, "short.")
        p = write(d, small)
        code, out = run("check", "--retro", p)
        assert code == 0, out
        code, out = run("migrate", "--retro", p, "--write")
        assert "Prune, 2026-08-14" in pathlib.Path(p).read_text(encoding="utf-8"), \
            "prose moved from a floor that was within budget"
        assert "nothing to move" in out, out
        big = legacy(stamps=30)
        p2 = write(d, big, "big.md")
        code, out = run("check", "--retro", p2)
        assert code == 1 and "over the budget of 12000" in out, "the big fixture is not over budget: " + out
        run("migrate", "--retro", p2, "--write")
        assert "Prune, 2026-08-14" not in pathlib.Path(p2).read_text(encoding="utf-8")


@case("B-244: a second and third migrate change nothing")
def _():
    with tempfile.TemporaryDirectory() as d:
        p = write(d, legacy())
        run("migrate", "--retro", p, "--write")
        once = pathlib.Path(p).read_bytes()
        for _ in range(2):
            code, out = run("migrate", "--retro", p, "--write")
            assert code == 0 and "nothing to move" in out, out
        assert pathlib.Path(p).read_bytes() == once, "a repeated migrate rewrote the retro"


@case("B-244: an undated stamp refuses rotation by name instead of guessing an order")
def _():
    with tempfile.TemporaryDirectory() as d:
        bad = plant(legacy(), "- **2026-09-01 — run 0**", "- **sometime — run 0**")
        p = write(d, bad)
        code, out = run("migrate", "--retro", p)
        assert "rotate the stamps by hand" in out, out


@case("B-149 review: a rule after a date-only bold span survives; a date alone refuses")
def _():
    with tempfile.TemporaryDirectory() as d:
        seed = plant(legacy(), "1. **(2026-08-11) Rule number 1 holds.**", "1. **(2026-08-11)** **Rule number 1 holds.**")
        p = write(d, seed)
        run("migrate", "--retro", p, "--write")
        after = pathlib.Path(p).read_text(encoding="utf-8")
        assert "1. **(2026-08-11)** **Rule number 1 holds.** *(Retire" in after, after[:600]
        seed = plant(legacy(), "1. **(2026-08-11) Rule number 1 holds.**", "1. **(2026-08-11)** Rule number 1 holds.")
        p = write(d, seed, "dateonly.md")
        code, out = run("migrate", "--retro", p, "--write")
        assert "standing #1 opens with no **bold** rule (or only a date)" in out, out
        assert "Rule number 1 holds." in pathlib.Path(p).read_text(encoding="utf-8"), "a date-only item was compressed"


@case("B-149 review: an empty stamps table that was already there is kept, not deleted")
def _():
    with tempfile.TemporaryDirectory() as d:
        seed = plant(SEED, "## Run stamps\n", "## Run stamps\n\n| Date | Task | Commit | Verdict |\n|---|---|---|---|\n")
        seed = plant(seed, "… (one line; links the archive entry)", "the story, " * 80)
        p = write(d, seed)
        arch = os.path.join(d, "retro", "2026-Q4.md")
        code, out = run("migrate", "--retro", p, "--archive", arch, "--write")
        assert code == 0, out
        after = pathlib.Path(p).read_text(encoding="utf-8")
        archived = pathlib.Path(arch).read_text(encoding="utf-8")
        assert after.count("| Date | Task | Commit | Verdict |") == 1, "the empty stamps table was deleted"
        assert ("the story, " * 80).strip() in archived, "the Because cell did not move verbatim"


@case("B-149 review: a heading inside Run stamps prose stays put and every pointer still verifies")
def _():
    with tempfile.TemporaryDirectory() as d:
        seed = legacy(stamps=30).replace("## Recent log", "### Second prune\n\nmore.\n\n## Recent log")
        p = write(d, seed)
        code, out = run("migrate", "--retro", p, "--write")
        assert "### Second prune" in pathlib.Path(p).read_text(encoding="utf-8"), out
        code, out = run("verify", "--retro", p)
        assert code == 0, out


@case("B-149 review: a same-day tie in a newest-first list rotates the older stamp")
def _():
    with tempfile.TemporaryDirectory() as d:
        items = ["- **2026-09-05 — tie %02d** %s" % (k, "x. " * 10) for k in range(11)]
        items.reverse()     # newest (tie 10) first
        seed = SEED.replace("## Run stamps\n", "## Run stamps\n\n" + "\n\n".join(items) + "\n")
        p = write(d, seed)
        run("migrate", "--retro", p, "--write")
        after = pathlib.Path(p).read_text(encoding="utf-8")
        assert "tie 10" in after and "tie 00" not in after, "the newest stamp of the day rotated out"


@case("B-149 review: a retire trigger with nested parentheses is kept whole")
def _():
    with tempfile.TemporaryDirectory() as d:
        seed = plant(legacy(), "*(Retire when rule 1 is a check, or after five run stamps without firing.)*",
                     "*(Retire when `x` (or `y`) is a check.)*")
        p = write(d, seed)
        run("migrate", "--retro", p, "--write")
        assert "*(Retire when `x` (or `y`) is a check.)* story:" in pathlib.Path(p).read_text(encoding="utf-8")


@case("B-149 review: an unindented continuation belongs to its list stamp")
def _():
    with tempfile.TemporaryDirectory() as d:
        seed = SEED.replace("## Run stamps\n", "## Run stamps\n\n- **2026-09-01 — lazy** x\n" + "y" * 500 + "\n")
        code, out = run("check", "--retro", write(d, seed))
        assert "stamp 2026-09-01 (list) is" in out, out


@case("B-149 review 2: a floor still over budget after migrate is left alone by the next run")
def _():
    with tempfile.TemporaryDirectory() as d:
        seed = legacy(stamps=30)
        for n in (1, 2, 3):     # no bold rule: refused by name, so the floor stays over budget
            seed = plant(seed, "%d. **(2026-08-1%d) Rule number %d holds.**" % (n, n, n),
                         "%d. (2026-08-1%d) Rule number %d holds." % (n, n, n))
        seed = seed.replace("Hard cap: ten.", "Hard cap: ten. " + "standing prose that stays. " * 500)
        p = write(d, seed)
        arch = os.path.join(d, "retro", "2026-Q4.md")
        run("migrate", "--retro", p, "--archive", arch, "--write")
        once = (pathlib.Path(p).read_bytes(), pathlib.Path(arch).read_bytes())
        code, out = run("check", "--retro", p)
        assert code == 1, "the fixture did not stay over budget: " + out
        for _ in range(2):
            run("migrate", "--retro", p, "--archive", arch, "--write")
        assert (pathlib.Path(p).read_bytes(), pathlib.Path(arch).read_bytes()) == once, \
            "a repeated migrate on an over-budget floor rewrote the retro or the archive"


@case("B-149 review 2: same-day ties follow each block's own direction")
def _():
    with tempfile.TemporaryDirectory() as d:
        # a newest-first list of newer stamps beside an oldest-first table of same-day rows
        items = ["- **2026-09-%02d — list %d** %s" % (k + 2, k, "x. " * 10) for k in range(9)]
        items.reverse()
        table = ["| Date | Task | Commit | Verdict |", "|---|---|---|---|",
                 "| 2026-08-31 | zero | `a` | ok |"] + \
            ["| 2026-09-01 | %s | `a` | ok |" % w for w in ("first", "second", "third", "fourth")]
        seed = SEED.replace("## Run stamps\n", "## Run stamps\n\n" + "\n\n".join(items) + "\n\n" + "\n".join(table) + "\n")
        seed = seed.replace(STAMP_NEEDLE, "")
        p = write(d, seed)
        run("migrate", "--retro", p, "--write")
        after = pathlib.Path(p).read_text(encoding="utf-8")
        for older in ("| 2026-08-31 | zero |", "| 2026-09-01 | first |", "| 2026-09-01 | second |",
                      "| 2026-09-01 | third |"):
            assert older not in after, "the older table row %s was kept over a newer one" % older
        assert "| 2026-09-01 | fourth |" in after, "the newest table row rotated out"


@case("B-149 review 2: a list marker, a rule or a note under an item is not its continuation")
def _():
    with tempfile.TemporaryDirectory() as d:
        seed = legacy(long_items=False).replace(
            "1. **(2026-08-11) Rule number 1 holds.**",
            "1. **(2026-08-11) Rule number 1 holds.**", 1)
        seed = seed.replace("\n\n2. **(2026-08-12)", "\n*(4 retired)*\n\n2. **(2026-08-12)", 1)
        code, out = run("check", "--retro", write(d, seed))
        assert "standing 3/10 rows" in out, out
        p = write(d, seed, "m.md")
        run("migrate", "--retro", p, "--write")
        assert "*(4 retired)*" in pathlib.Path(p).read_text(encoding="utf-8"), "a vacancy note left the floor"


@case("B-149 review 3: a rule still over the row limit after its story moved is not moved again")
def _():
    for seed in (plant(legacy(), "Rule number 1 holds.**", "Rule number 1 holds " + "and holds " * 55 + ".**"),
                 plant(SEED, "| R-001 | 2026-05-04 · `<topic>` | `<sha>` | … |",
                       "| R-001 | 2026-05-04 · `<topic>` | `<sha>` | " + "do this. " * 80 + " |")):
        with tempfile.TemporaryDirectory() as d:
            p = write(d, seed)
            arch = os.path.join(d, "retro", "2026-Q4.md")
            run("migrate", "--retro", p, "--archive", arch, "--write")
            once = (pathlib.Path(p).read_bytes(), pathlib.Path(arch).read_bytes())
            for _ in range(2):
                code, out = run("migrate", "--retro", p, "--archive", arch, "--write")
                assert code == 1, "an over-long rule stopped being reported: " + out
            assert (pathlib.Path(p).read_bytes(), pathlib.Path(arch).read_bytes()) == once, \
                "a repeated migrate re-archived a rule's own pointer"


@case("B-149 review 3: a `+` bullet, a quote or a `1)` item under an item ends it")
def _():
    with tempfile.TemporaryDirectory() as d:
        seed = legacy(long_items=False)
        seed = seed.replace("\n\n2. **(2026-08-12)", "\n+ plus item\n> a quote\n1) paren item\n\n2. **(2026-08-12)", 1)
        sys.path.insert(0, str(SK / "scripts"))
        import retro_budget as rb
        lines, spans = rb.sections(seed)
        first = rb.list_items(lines, spans[rb.STANDING])[0]
        inside = lines[first[0]:first[1]]
        for line in ("+ plus item", "> a quote", "1) paren item"):
            assert line not in inside, "%r was swallowed into item 1" % line


# B-258 (sshlg-skills, 2026-10-26): migrate assumed every stamp table was
# `Date | Topic | Commit | Verdict | ...`. On `Date | Commit | Task | Diverged?` it cut the
# Commit cell and kept the long Task; on a three-column table it appended a fourth cell.
def split_row(row):
    """Cells of a table row, an escaped `\\|` staying inside its cell."""
    s = row.strip()
    s = s[1:] if s.startswith("|") else s
    s = s[:-1] if s.endswith("|") and not s.endswith("\\|") else s
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def stamp_retro(header, row):
    cols = split_row(header)
    return "\n".join(["# Retro", "", "## Standing instructions", "", "None in force.", "",
                      "## Run stamps", "", header, "|" + "---|" * len(cols), row, "",
                      "## Recent log", "", "queried, not read.", ""])


def migrate_stamp(header, row):
    """Migrate one over-long stamp row; returns (old cells, new cells, new row, archive text)."""
    with tempfile.TemporaryDirectory() as d:
        p = write(d, stamp_retro(header, row))
        arch = os.path.join(d, "retro", "2026-Q4.md")
        code, out = run("check", "--retro", p)
        assert code == 1 and "over 300" in out, "the fixture row is not over the stamp limit: " + out
        code, out = run("migrate", "--retro", p, "--archive", arch, "--write")
        assert code == 0, out
        after = pathlib.Path(p).read_text(encoding="utf-8")
        new = [l for l in after.split("\n") if l.startswith("| 2026-")]
        assert len(new) == 1, "expected one stamp row, got %r" % new
        assert len(new[0]) <= 300, "the shortened row is %d chars" % len(new[0])
        archived = pathlib.Path(arch).read_text(encoding="utf-8")
        assert row in archived, "the original row is not in the archive verbatim"
        code, out = run("verify", "--retro", p)
        assert code == 0, out
        once = (pathlib.Path(p).read_bytes(), pathlib.Path(arch).read_bytes())
        code, out = run("migrate", "--retro", p, "--archive", arch, "--write")
        assert code == 0 and "nothing to move" in out, "a second migrate moved the row again: " + out
        assert (pathlib.Path(p).read_bytes(), pathlib.Path(arch).read_bytes()) == once, \
            "a second migrate rewrote the retro or the archive"
        return split_row(row), split_row(new[0]), new[0], archived


def assert_shape(old, new, keep, shrink):
    """`keep`: indices that must be unchanged; `shrink`: indices that must be capped evenly."""
    assert len(new) == len(old), "the row has %d cells, its table %d: %r" % (len(new), len(old), new)
    last = len(new) - 1
    assert re.search(r"(?:^| )moved: retro/2026-Q4\.md sha256:[0-9a-f]{12}$", new[last]), \
        "the pointer is not at the end of the last cell: %r" % new[last]
    body = [re.sub(r"\s*moved: retro/\S+ sha256:[0-9a-f]{12}$", "", c) if j == last else c
            for j, c in enumerate(new)]
    for j in keep:
        assert body[j] == old[j], "cell %d (%r) was shortened to %r" % (j, old[j], body[j])
    for j in shrink:
        assert body[j].endswith("…") and len(body[j]) < len(old[j]), \
            "cell %d was not shortened: %r" % (j, body[j])
    caps = [len(body[j]) for j in shrink]
    assert max(caps) - min(caps) <= 2, "the long cells were not capped evenly: %r" % caps


@case("B-258: `Date | Topic | Task | Verdict` keeps four cells, the date, and caps the prose evenly")
def _():
    row = "| 2026-10-20 | %s | %s | %s |" % ("topic " * 15, "the task, told at length. " * 9, "verdict words " * 12)
    old, new, _, _ = migrate_stamp("| Date | Topic | Task | Verdict |", row)
    assert_shape(old, new, keep=[0], shrink=[1, 2, 3])


@case("B-258: `Date | Commit | Task | Diverged?` keeps the Commit cell whole, shortens Task")
def _():
    for commit in ("working tree", "`3f9c2ab`"):
        row = "| 2026-10-20 | %s | %s | %s |" % (commit, "the task, told at length. " * 10,
                                                   "yes: the run diverged here. " * 6)
        old, new, _, _ = migrate_stamp("| Date | Commit | Task | Diverged? |", row)
        assert_shape(old, new, keep=[0, 1], shrink=[2, 3])


@case("B-258: a three-column table keeps three cells; the pointer joins the last")
def _():
    row = "| 2026-10-20 | %s | %s |" % ("the task, told at length. " * 10, "no. " * 30)
    old, new, _, _ = migrate_stamp("| Date | Task | Diverged? |", row)
    assert_shape(old, new, keep=[0], shrink=[1, 2])


@case("B-258: a five-column table keeps five cells, its version and commit whole")
def _():
    row = "| 2026-10-20 | v1.102.2 | `ce33d5d` | %s | %s |" % ("the task, told at length. " * 10,
                                                              "14/14 verified, and then some. " * 5)
    old, new, _, _ = migrate_stamp("| Date | Version | Commit | Task | Verdict |", row)
    assert_shape(old, new, keep=[0, 1, 2], shrink=[3, 4])


@case("B-258: an escaped pipe inside a cell is one cell, and a cut never leaves it a delimiter")
def _():
    row = "| 2026-10-20 | %s | %s | ok |" % ("topic", "a \\| b, the escaped pipe inside one cell. " * 9)
    old, new, line, _ = migrate_stamp("| Date | Topic | Task | Verdict |", row)
    assert len(old) == 4, "the fixture's escaped pipe split its cell: %r" % old
    assert_shape(old, new, keep=[0, 1], shrink=[2])
    assert not re.search(r"\\\s*\|", line.replace("\\|", "")), "a cut left a backslash before a delimiter"


# B-246 (sshlg-skills, 2026-10-22): one `Rotated out:` line per archive quarter.
def rotation_lines(text):
    return re.findall(r"^Rotated out: (\d+) oldest run stamps, verbatim in (\S+) sha256:(\w+)$", text, re.M)


@case("B-246: three migrates with rotations leave one Rotated out line, every stamp proved")
def _():
    with tempfile.TemporaryDirectory() as d:
        p = write(d, legacy())
        arch = os.path.join(d, "retro", "2026-Q4.md")
        seen, day = [], 21
        for n, add in enumerate((0, 2, 3)):
            if add:
                cur = pathlib.Path(p).read_text(encoding="utf-8")
                first = re.search(r"^- \*\*2026-09-\d\d — run \d+\*\*", cur, re.M).group(0)
                newer = "".join("- **2026-09-%d — run %d** (base `abc%04d`). newer.\n\n" % (k, k, k)
                                for k in range(day + add - 1, day - 1, -1))
                day += add
                pathlib.Path(p).write_text(plant(cur, first, newer + first), encoding="utf-8")
            seen.append(pathlib.Path(p).read_text(encoding="utf-8"))
            code, out = run("migrate", "--retro", p, "--archive", arch, "--write")
            assert code == 0, "run %d: %s" % (n + 1, out)
            after = pathlib.Path(p).read_text(encoding="utf-8")
            ptr = rotation_lines(after)
            assert len(ptr) == 1, "run %d left %d Rotated out lines: %r" % (n + 1, len(ptr), ptr)
            assert ptr[0][0] == str(6 + sum((0, 2, 3)[:n + 1])), "run %d counts %s" % (n + 1, ptr[0][0])
            code, out = run("verify", "--retro", p)
            assert code == 0, out
        archived = pathlib.Path(arch).read_text(encoding="utf-8")
        lost = [l for t in seen for l in t.split("\n") if l.strip() and not l.startswith("Rotated out: ")
                and l not in after and l not in archived]
        assert not lost, "lines lost across three rotations: %r" % lost[:3]


@case("B-246: a floor already holding several lines for one quarter is merged by the next migrate")
def _():
    sys.path.insert(0, str(SK / "scripts"))
    import retro_budget as rb
    with tempfile.TemporaryDirectory() as d:
        seed = legacy(stamps=4, long_items=False, prose=False).replace("narrative. " * 40, "short.")
        lines, texts = [], {}
        for q, stamps in (("2026-Q4", ("| 2026-07-01 | B-9: q4a | `a1` | no |", "| 2026-07-02 | B-9: q4b | `a2` | no |",
                                        "| 2026-07-03 | B-9: q4c | `a3` | no |")),
                          ("2026-Q3", ("| 2026-06-01 | B-8: q3a | `b1` | no |", "| 2026-06-02 | B-8: q3b | `b2` | no |"))):
            path = pathlib.Path(d, "retro", q + ".md")
            path.parent.mkdir(exist_ok=True)
            body = "# Retro archive · %s\n" % q
            for s in stamps:
                text = "| Date | Task | Commit | Diverged? |\n|---|---|---|---|\n" + s
                h, b = rb.block("stamps", "1 oldest rotated", text)
                body += b
                lines.append("Rotated out: 1 oldest run stamps, verbatim in retro/%s.md sha256:%s" % (q, h[:12]))
                texts.setdefault(q, []).append(s)
            path.write_text(body, encoding="utf-8")
        seed = plant(seed, "## Run stamps\n", "## Run stamps\n\n" + "\n\n".join(lines) + "\n")
        p = write(d, seed)
        code, out = run("verify", "--retro", p)
        assert code == 0, "the planted floor does not verify: " + out
        assert len(rotation_lines(seed)) == 5, "the plant did not seed five lines"
        arch = os.path.join(d, "retro", "2026-Q4.md")
        code, out = run("migrate", "--retro", p, "--archive", arch, "--write")
        assert code == 0, out
        after = pathlib.Path(p).read_text(encoding="utf-8")
        ptr = sorted(rotation_lines(after), key=lambda x: x[1])
        assert [(n, rel) for n, rel, _ in ptr] == [("2", "retro/2026-Q3.md"), ("3", "retro/2026-Q4.md")], ptr
        for n, rel, short in ptr:
            q = rel[len("retro/"):-3]
            block = rb.archived_text(os.path.join(d, rel), short)
            assert block and all(s in block[1] for s in texts[q]), "the %s block lost a stamp" % q
        code, out = run("verify", "--retro", p)
        assert code == 0, out
        once = (pathlib.Path(p).read_bytes(), pathlib.Path(arch).read_bytes())
        code, out = run("migrate", "--retro", p, "--archive", arch, "--write")
        assert code == 0 and "nothing to move" in out, out
        assert (pathlib.Path(p).read_bytes(), pathlib.Path(arch).read_bytes()) == once, "a second merge rewrote"


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
