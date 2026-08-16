#!/usr/bin/env python3
"""Fixtures for templates/exposure.sh — the measurement that must never become a score.

The script turns `verification.md` into one line and a check-list. Every case below is a
way that line could lie, and most of them lie in the *reassuring* direction, which is why
they are asserted separately rather than folded into "the output looks right":

- `0 days` where nobody has ever confirmed anything reads as *checked today*.
- an empty check-list under a non-zero count reads as *nothing to look at*.
- a percentage reads as a probability, which these inputs cannot support.
- a lexical sort hands the operator v1.10.0 before v1.9.0 — the wrong end of the list.

Each case builds a real repository in a temp directory and runs the real script. There is
no unit under test here: the script IS bash, and a python re-implementation of its logic
would be a second thing to keep true.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline",
                      "templates", "exposure.sh")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


HEADER = "| REQ | What | Run | Shipped in | Auto | Human | Note |\n|---|---|---|---|---|---|---|\n"


def project(rows, tags=(), board=None, ledger=True):
    """A real git repository with a real ledger, because the script reads both."""
    d = tempfile.mkdtemp()
    run = lambda *a: subprocess.run(["git", "-C", d, *a], capture_output=True, text=True)
    run("init", "-q")
    run("config", "user.email", "t@t")
    run("config", "user.name", "t")
    os.makedirs(os.path.join(d, "docs", "evidence"), exist_ok=True)
    if ledger:
        with open(os.path.join(d, "docs/evidence/verification.md"), "w", encoding="utf-8") as fh:
            fh.write("# Verification ledger\n\n" + HEADER + "".join(rows))
    if board is not None:
        with open(os.path.join(d, "docs/evidence/backlog.md"), "w", encoding="utf-8") as fh:
            fh.write(board)
    with open(os.path.join(d, "seed"), "w") as fh:
        fh.write("x")
    run("add", "-A")
    run("commit", "-qm", "seed")
    for t in tags:
        run("tag", t)
    return d


def exposure(d, **env):
    e = dict(os.environ)
    e.update({k: str(v) for k, v in env.items()})
    p = subprocess.run(["bash", SCRIPT], cwd=d, capture_output=True, text=True, env=e)
    shutil.rmtree(d, ignore_errors=True)
    return p


def row(req, what="something", shipped="v1.0.0", human="never"):
    return f"| {req} | {what} | run | {shipped} | pass | {human} | — |\n"


# --- the components -----------------------------------------------------------------

def counts_only_rows_whose_human_is_never():
    p = exposure(project([row("REQ-001"), row("REQ-002", human="2026-08-01"),
                          row("REQ-003")]))
    assert p.returncode == 0, p.stderr
    assert "2 unverified" in p.stdout, p.stdout


def no_confirmation_ever_prints_the_words_not_a_zero():
    """`0 days` would read as *checked today*, which is the opposite of the truth."""
    p = exposure(project([row("REQ-001")]))
    assert "never checked" in p.stdout, p.stdout
    assert "0 days" not in p.stdout, "a zero here inverts the meaning: " + p.stdout


def a_confirmation_prints_days_since_the_newest():
    import datetime
    d90 = (datetime.date.today() - datetime.timedelta(days=90)).isoformat()
    d10 = (datetime.date.today() - datetime.timedelta(days=10)).isoformat()
    p = exposure(project([row("REQ-001", human=d90), row("REQ-002", human=d10),
                          row("REQ-003")]))
    assert "10 days since the last human confirmation" in p.stdout, p.stdout
    assert "90 days" not in p.stdout, "it used the oldest date, not the newest: " + p.stdout


def releases_are_counted_over_all_tags_when_nothing_was_ever_confirmed():
    p = exposure(project([row("REQ-001")], tags=("v1.0.0", "v1.1.0", "v2.0.0")))
    assert "3 releases carry one" in p.stdout, p.stdout


def outside_a_checkout_the_release_count_is_unknown_not_zero():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "docs", "evidence"))
    with open(os.path.join(d, "docs/evidence/verification.md"), "w", encoding="utf-8") as fh:
        fh.write("# L\n\n" + HEADER + row("REQ-001"))
    p = exposure(d)
    assert "? releases" in p.stdout, "zero would claim nothing shipped: " + p.stdout


# --- the refusals -------------------------------------------------------------------

def a_percentage_is_refused():
    """The guard the doctrine names. A later hand adds `(N%)` and it looks helpful."""
    src = open(SCRIPT, encoding="utf-8").read()
    assert 'case "$LINE" in' in src and "*%*" in src, \
        "the percentage guard is gone from the script"
    d = project([row("REQ-001")])
    p = subprocess.run(["bash", "-c",
                        f'sed \'s/^LINE=.*/LINE="exposure: 12% likely broken"/\' {SCRIPT!r} > g.sh && bash g.sh'],
                       cwd=d, capture_output=True, text=True)
    shutil.rmtree(d, ignore_errors=True)
    assert p.returncode == 1, f"a percentage was allowed through: {p.stdout}{p.stderr}"
    assert "no percentage, ever" in p.stdout, p.stdout


def an_unparseable_date_fails_rather_than_guessing():
    p = exposure(project([row("REQ-001", human="last tuesday")]))
    # `last tuesday` is not a date and not `never`, so it is neither counted as
    # unverified nor usable as a confirmation. The row is simply not a date — the script
    # must not silently treat the ledger as unconfirmed either.
    assert p.returncode == 0, p.stderr
    assert "never checked" in p.stdout, \
        "a malformed date must not become a confirmation: " + p.stdout


# --- the check-list ------------------------------------------------------------------

def the_list_is_ordered_oldest_first_by_version_not_lexically():
    p = exposure(project([row("REQ-A", shipped="v1.10.0"), row("REQ-B", shipped="v1.9.0"),
                          row("REQ-C", shipped="v1.2.0")]))
    order = [m for m in re.findall(r"REQ-[ABC]", p.stdout)]
    assert order == ["REQ-C", "REQ-B", "REQ-A"], \
        f"lexical sort would put v1.10.0 before v1.9.0; got {order}"


def a_non_empty_count_never_prints_an_empty_list():
    """The failure that made this fixture worth writing: BSD sort died on UTF-8, the
    list came out empty, and the number above it still said there was work."""
    p = exposure(project([row("REQ-001", what="`references/adoption.md` — доктрина и разбор"),
                          row("REQ-002", what="Второй ряд — тоже с тире")]))
    assert "2 unverified" in p.stdout, p.stdout
    assert "REQ-001" in p.stdout and "REQ-002" in p.stdout, \
        "a non-empty count with an empty list: " + p.stdout + p.stderr
    assert "Illegal byte sequence" not in p.stderr, p.stderr


def blast_is_read_by_header_across_both_board_shapes():
    """`$5` is `Blast` in an eight-column board and `Size` in the ten-column one this
    repository SEEDS. Reading by index printed `[blast L]` — the size of the work labelled
    as who it hurts — in every host project, for a full release, two lines from where the
    same lesson had just been applied to the status column."""
    ten = ("| id | What | Source | Size | Sev | Blast | Age | Prio | State | Home |\n"
           "|---|---|---|---|---|---|---|---|---|---|\n"
           "| REQ-001 | a thing | run | L | 1 | 3 | 0 | 3 | open | — |\n")
    p = exposure(project([row("REQ-001")], board=ten))
    assert "[blast 3]" in p.stdout, "the ten-column shape read the wrong cell: " + p.stdout
    assert "[blast L]" not in p.stdout, p.stdout

    eight = ("| id | What | Source | Blast | Age | Effort | P | Status |\n"
             "|---|---|---|---|---|---|---|---|\n"
             "| REQ-001 | a thing | run | 2 | 0 | 1 | 2.0 | open |\n")
    p = exposure(project([row("REQ-001")], board=eight))
    assert "[blast 2]" in p.stdout, "the eight-column shape regressed: " + p.stdout


def a_board_with_no_blast_column_prints_no_blast():
    """Absent is absent — a missing column must not become a default weight."""
    none = ("| id | What | Status |\n|---|---|---|\n| REQ-001 | a thing | open |\n")
    p = exposure(project([row("REQ-001")], board=none))
    assert "REQ-001" in p.stdout, p.stdout
    assert "[blast" not in p.stdout, "it invented a weight from a column that is not there: " + p.stdout


def a_ledger_with_no_status_column_is_dormant_never_clean():
    """THE SILENT GREEN. A four-column ledger has no Human column at all; the first draft
    keyed on position, found four rows out of 298 whose inline code happened to contain a
    `|`, and printed *0 unverified · every shipped row carries a human confirmation*."""
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "docs", "evidence"))
    with open(os.path.join(d, "docs/evidence/verification.md"), "w", encoding="utf-8") as fh:
        fh.write("# L\n\n| REQ | What | Evidence | Note |\n|---|---|---|---|\n"
                 "| R-1 | a thing | `npm test` | — |\n"
                 "| R-2 | with a `|` inside code | see `| open |` | — |\n")
    p = exposure(d)
    assert p.returncode == 0, p.stderr
    assert p.stdout.startswith("dormant:"), \
        "a shape with no status column must be dormant, not clean: " + p.stdout
    assert "0 unverified" not in p.stdout, "it reported a number it could not compute"
    assert "no column named" in p.stdout, p.stdout


def the_status_column_is_found_by_name_not_position():
    """`Last verified` sits where `Run` sits in the canonical shape. Position would read
    the wrong cell; the name cannot. `Watched` and `Verified by` are deliberately NOT
    status names — five members hold shell commands under those headers."""
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "docs", "evidence"))
    with open(os.path.join(d, "docs/evidence/verification.md"), "w", encoding="utf-8") as fh:
        fh.write("# L\n\n| REQ | What ships | Last verified |\n|---|---|---|\n"
                 "| R-1 | a thing | **never** |\n| R-2 | another | 2026-08-01 |\n")
    p = exposure(d)
    assert "1 unverified" in p.stdout, p.stdout


def only_a_human_column_licenses_the_word_human():
    """The umbrella's own ledger defines `verified` as *a person **or a command***, so a
    clean bill drawn from a `Status` column may not claim a person looked."""
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "docs", "evidence"))
    with open(os.path.join(d, "docs/evidence/verification.md"), "w", encoding="utf-8") as fh:
        fh.write("# L\n\n| REQ | What shipped | Status |\n|---|---|---|\n"
                 "| R-1 | a thing | verified |\n")
    p = exposure(d)
    assert "0 unverified" in p.stdout, p.stdout
    assert "human confirmation" not in p.stdout, \
        "a Status column cannot licence the word human: " + p.stdout
    assert "`status` column" in p.stdout, p.stdout


def a_shrug_never_gets_a_clean_bill():
    """A status that is neither a date nor a known word is unreadable, and unreadable is
    not confirmed."""
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "docs", "evidence"))
    with open(os.path.join(d, "docs/evidence/verification.md"), "w", encoding="utf-8") as fh:
        fh.write("# L\n\n| REQ | What | Run | Shipped in | Auto | Human | Note |\n"
                 "|---|---|---|---|---|---|---|\n"
                 "| R-1 | a thing | run | v1.0.0 | pass | ask Ben | - |\n")
    p = exposure(d)
    assert "cannot read" in p.stdout, p.stdout
    assert "every shipped row" not in p.stdout, "a shrug got a clean bill: " + p.stdout


def everything_confirmed_says_so_plainly():
    p = exposure(project([row("REQ-001", human="2026-08-01")]))
    assert "0 unverified" in p.stdout, p.stdout
    assert "every shipped row carries a human confirmation" in p.stdout, p.stdout


def the_list_is_capped_and_says_what_it_dropped():
    rows = [row(f"REQ-{i:03d}", shipped=f"v1.{i}.0") for i in range(1, 13)]
    p = exposure(project(rows), LIST_MAX=3)
    assert "… and 9 more" in p.stdout, "a silent truncation reads as full coverage: " + p.stdout


def blast_radius_comes_from_the_board_and_absence_is_not_a_default():
    board = "| id | What | Source | Blast | Age | Effort | P | Status |\n|---|---|---|---|---|---|---|---|\n| REQ-001 | x | y | 3 | 0 | 1 | 3.0 | open |\n"
    p = exposure(project([row("REQ-001"), row("REQ-002")], board=board))
    assert "[blast 3]" in p.stdout, p.stdout
    assert p.stdout.count("[blast") == 1, \
        "the row with no board entry invented a weight: " + p.stdout


# --- dormancy ------------------------------------------------------------------------

def no_ledger_is_dormant_and_green():
    p = exposure(project([], ledger=False))
    assert p.returncode == 0, p.stderr
    assert p.stdout.startswith("dormant:"), p.stdout


def a_ledger_with_only_a_header_is_dormant():
    p = exposure(project([]))
    assert p.returncode == 0, p.stderr
    assert "no REQ rows yet" in p.stdout, p.stdout


for n, f in [
    ("counts only rows whose Human is never", counts_only_rows_whose_human_is_never),
    ("no confirmation ever prints words, not a zero", no_confirmation_ever_prints_the_words_not_a_zero),
    ("a confirmation prints days since the NEWEST", a_confirmation_prints_days_since_the_newest),
    ("releases count all tags when nothing was confirmed", releases_are_counted_over_all_tags_when_nothing_was_ever_confirmed),
    ("outside a checkout releases is `?`, not 0", outside_a_checkout_the_release_count_is_unknown_not_zero),
    ("a percentage is refused", a_percentage_is_refused),
    ("a malformed date does not become a confirmation", an_unparseable_date_fails_rather_than_guessing),
    ("the list is version-ordered, oldest first", the_list_is_ordered_oldest_first_by_version_not_lexically),
    ("a non-empty count never prints an empty list", a_non_empty_count_never_prints_an_empty_list),
    ("everything confirmed says so plainly", everything_confirmed_says_so_plainly),
    ("blast is read by header across both board shapes", blast_is_read_by_header_across_both_board_shapes),
    ("a board with no blast column prints no blast", a_board_with_no_blast_column_prints_no_blast),
    ("a ledger with no status column is dormant, never clean", a_ledger_with_no_status_column_is_dormant_never_clean),
    ("the status column is found by name, not position", the_status_column_is_found_by_name_not_position),
    ("only a Human column licenses the word human", only_a_human_column_licenses_the_word_human),
    ("a shrug never gets a clean bill", a_shrug_never_gets_a_clean_bill),
    ("the cap says what it dropped", the_list_is_capped_and_says_what_it_dropped),
    ("blast comes from the board; absence is absent", blast_radius_comes_from_the_board_and_absence_is_not_a_default),
    ("no ledger is dormant and green", no_ledger_is_dormant_and_green),
    ("a header-only ledger is dormant", a_ledger_with_only_a_header_is_dormant),
]:
    case(n, f)

if failures:
    print(f"\nFAIL: {len(failures)} of 20")
    sys.exit(1)
print("\nPASS: exposure.sh — 20 cases")
