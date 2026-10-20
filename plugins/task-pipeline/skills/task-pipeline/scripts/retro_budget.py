#!/usr/bin/env python3
"""retro_budget.py: the byte budget of the retro's floor, measured and enforced.

The floor is what stage 0 reads in full: the *Standing instructions* section and the
*Run stamps* section of `<artifacts>/retro.md` (`references/retrospective.md` ->
*The floor has a byte budget*). A cap of ten rows never bounded their SIZE: measured
on 2026-10-20 across ~50 projects the floor ran from ~3k to ~76k tokens, one of them
304 KB. This script is the bound.

    retro_budget.py check   [--retro PATH] [--budget N] [--row N] [--stamp N]
        prints one line: the floor's bytes, bytes/4 tokens, and the largest row of
        each kind. Exit 0 within budget; 1 over budget (every offender listed);
        2 could not measure (no file, or a floor section is missing).
    retro_budget.py migrate [--retro PATH] [--archive PATH] [--write]
        moves narrative out of the floor VERBATIM into the archive, each block
        carrying the sha256 of the text it holds, and leaves a pointer in its place:
        a stamp row over the stamp limit keeps Date, Topic and Commit; a standing row
        over the row limit loses its `Because` cell. Without --write it prints the
        plan and writes nothing. Exit 0 when the floor is then within budget, 1 when a
        row is still over (an instruction too long to shorten by moving its story:
        rewrite it by hand), 2 could not measure.
    retro_budget.py verify  [--retro PATH]
        every `sha256:` pointer in the floor resolves to an archive block whose text
        hashes to it. Exit 0, or 1 naming each pointer that does not.

Standard library only, like every script this skill ships.
"""
import argparse
import datetime
import hashlib
import os
import re
import sys

BUDGET = 12000  # bytes of floor (standing instructions + run stamps)
ROW = 600       # chars per standing-instruction row
STAMP = 300     # chars per run-stamp row
CAP = 10        # rows per table, the existing cap

STANDING = "## Standing instructions"
STAMPS = "## Run stamps"
POINTER = re.compile(r"(retro/[0-9]{4}-Q[1-4]\.md) sha256:([0-9a-f]{12,64})")


class Unmeasurable(Exception):
    pass


def sections(text):
    """{name: (start, end)} line spans of the two floor sections, end exclusive."""
    lines = text.split("\n")
    spans = {}
    for i, line in enumerate(lines):
        for name in (STANDING, STAMPS):
            if line.startswith(name) and name not in spans:
                j = i + 1
                while j < len(lines) and not (lines[j].startswith("## ")
                                              or lines[j].startswith("# ")):
                    j += 1
                spans[name] = (i, j)
    missing = [n for n in (STANDING, STAMPS) if n not in spans]
    if missing:
        raise Unmeasurable("no `%s` section, so the floor cannot be measured"
                           % "` or `".join(missing))
    return lines, spans


def table_rows(lines, span):
    """Indices of the data rows of every table inside a span (header and rule skipped)."""
    out = []
    start, end = span
    i = start
    while i < end:
        if lines[i].startswith("|") and i + 1 < end and re.match(r"^\|\s*:?-{3}", lines[i + 1]):
            i += 2
            while i < end and lines[i].startswith("|"):
                out.append(i)
                i += 1
            continue
        i += 1
    return out


def cells(row):
    parts = row.strip().split("|")
    return [c.strip() for c in parts[1:-1]]


def header_cols(lines, i):
    """Column count of the table holding row i, read from its header (a `|` inside a
    cell's text must not widen the row that replaces it)."""
    k = i
    while k > 0 and lines[k - 1].startswith("|"):
        k -= 1
    return len(cells(lines[k]))


def measure(text, budget=BUDGET, row=ROW, stamp=STAMP):
    lines, spans = sections(text)
    floor = "\n".join(lines[spans[STANDING][0]:spans[STANDING][1]]) + "\n" + \
            "\n".join(lines[spans[STAMPS][0]:spans[STAMPS][1]])
    nbytes = len(floor.encode("utf-8"))
    std = table_rows(lines, spans[STANDING])
    stm = table_rows(lines, spans[STAMPS])
    over = []
    if nbytes > budget:
        over.append("floor is %d bytes, over the budget of %d" % (nbytes, budget))
    for i in std:
        if len(lines[i]) > row:
            over.append("standing row %s is %d chars, over %d"
                        % ((cells(lines[i]) or ["?"])[0], len(lines[i]), row))
    for i in stm:
        if len(lines[i]) > stamp:
            c = cells(lines[i])
            over.append("stamp %s %s is %d chars, over %d"
                        % (c[0] if c else "?", c[2] if len(c) > 2 else "", len(lines[i]), stamp))
    if len(std) > CAP:
        over.append("%d standing rows, over the cap of %d" % (len(std), CAP))
    if len(stm) > CAP:
        over.append("%d run stamps, over the cap of %d" % (len(stm), CAP))
    return {
        "bytes": nbytes, "tokens": nbytes // 4, "budget": budget,
        "standing": len(std), "standing_max": max([len(lines[i]) for i in std] or [0]),
        "stamps": len(stm), "stamps_max": max([len(lines[i]) for i in stm] or [0]),
        "over": over, "lines": lines, "spans": spans, "std": std, "stm": stm,
    }


def summary(m, row=ROW, stamp=STAMP):
    return ("retro floor: %d bytes · ~%d tokens (bytes/4) · budget %d · standing %d/%d rows, "
            "largest %d/%d · stamps %d/%d, largest %d/%d"
            % (m["bytes"], m["tokens"], m["budget"], m["standing"], CAP, m["standing_max"], row,
               m["stamps"], CAP, m["stamps_max"], stamp))


def read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError as exc:
        raise Unmeasurable("cannot read %s (%s)" % (path, exc.strerror or exc))


def default_archive(retro):
    today = datetime.date.today()
    q = (today.month - 1) // 3 + 1
    return os.path.join(os.path.dirname(os.path.abspath(retro)), "retro",
                        "%d-Q%d.md" % (today.year, q))


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def block(kind, label, text):
    h = digest(text)
    return h, ("\n### retro_budget migrate · %s · %s · %s\n\n<!-- sha256:%s -->\n%s\n"
               % (datetime.date.today().isoformat(), kind, label, h, text))


def cmd_check(a):
    m = measure(read(a.retro), a.budget, a.row, a.stamp)
    print(summary(m, a.row, a.stamp))
    if m["over"]:
        for o in m["over"]:
            print("  over: " + o)
        print("  remedy: retro_budget.py migrate --write moves the narrative to the archive "
              "verbatim; an instruction still over the row limit is rewritten by hand")
        return 1
    return 0


def cmd_migrate(a):
    text = read(a.retro)
    m = measure(text, a.budget, a.row, a.stamp)
    lines = m["lines"]
    archive = a.archive or default_archive(a.retro)
    rel = os.path.relpath(os.path.abspath(archive),
                          os.path.dirname(os.path.abspath(a.retro))).replace(os.sep, "/")
    moved = []
    for i in m["stm"]:
        if len(lines[i]) <= a.stamp:
            continue
        c = cells(lines[i])
        if len(c) < 3:
            continue
        h, b = block("stamp", "%s %s" % (c[0], c[2]), lines[i])
        ptr = "moved: %s sha256:%s" % (rel, h[:12])
        # the table keeps its column count: the pointer fills Verdict, `·` the rest
        tail = ["·"] * max(0, header_cols(lines, i) - 4)

        def row_of(topic):
            return "| " + " | ".join([c[0], topic, c[2], ptr] + tail) + " |"

        topic = c[1]
        new = row_of(topic)
        if len(new) > a.stamp:
            keep = max(8, len(topic) - (len(new) - a.stamp) - 1)
            new = row_of(topic[:keep].rstrip() + "…")
        moved.append((i, new, b, "stamp %s %s" % (c[0], c[2])))
    for i in m["std"]:
        if len(lines[i]) <= a.row:
            continue
        c = cells(lines[i])
        if len(c) < 5:
            continue
        h, b = block("standing", c[0], c[4])
        c[4] = "story: %s sha256:%s" % (rel, h[:12])
        moved.append((i, "| " + " | ".join(c) + " |", b, "standing %s Because" % c[0]))
    if not moved:
        print(summary(m, a.row, a.stamp))
        print("migrate: nothing to move")
        return 1 if m["over"] else 0
    for i, new, _, label in moved:
        print("migrate: %s -> %s (%d -> %d chars)" % (label, rel, len(lines[i]), len(new)))
    if not a.write:
        print("migrate: dry run, nothing written (pass --write)")
        return 0
    os.makedirs(os.path.dirname(os.path.abspath(archive)), exist_ok=True)
    if not os.path.exists(archive):
        with open(archive, "w", encoding="utf-8") as fh:
            fh.write("# Retro archive · %s\n\n**Append-only. Queried, never read in full.** "
                     "Blocks moved here by `retro_budget.py migrate` carry the sha256 of the "
                     "text they hold; the floor keeps a pointer to it.\n"
                     % os.path.basename(archive)[:-3])
    with open(archive, "a", encoding="utf-8") as fh:
        for _, _, b, _ in moved:
            fh.write(b)
    for i, new, _, _ in moved:
        lines[i] = new
    tmp = a.retro + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    os.replace(tmp, a.retro)
    after = measure(read(a.retro), a.budget, a.row, a.stamp)
    print(summary(after, a.row, a.stamp))
    bad = verify(a.retro)
    if bad:
        for b in bad:
            print("  unproved: " + b)
        return 1
    for o in after["over"]:
        print("  still over: " + o)
    return 1 if after["over"] else 0


def verify(retro):
    text = read(retro)
    lines, spans = sections(text)
    floor = "\n".join(lines[spans[STANDING][0]:spans[STANDING][1]] +
                      lines[spans[STAMPS][0]:spans[STAMPS][1]])
    base = os.path.dirname(os.path.abspath(retro))
    bad, cache = [], {}
    for rel, short in POINTER.findall(floor):
        path = os.path.join(base, rel)
        if path not in cache:
            try:
                cache[path] = read(path)
            except Unmeasurable:
                cache[path] = None
        arch = cache[path]
        if arch is None:
            bad.append("sha256:%s points at %s, which does not exist" % (short, rel))
            continue
        ok = False
        for m in re.finditer(r"<!-- sha256:([0-9a-f]{64}) -->\n(.*?)\n(?=\n#{2,3} |\Z)", arch, re.S):
            if m.group(1).startswith(short) and digest(m.group(2)) == m.group(1):
                ok = True
                break
        if not ok:
            bad.append("sha256:%s has no block in %s whose text hashes to it" % (short, rel))
    return bad


def cmd_verify(a):
    bad = verify(a.retro)
    for b in bad:
        print("unproved: " + b)
    if not bad:
        print("verify: every archive pointer in the floor resolves and its hash matches")
    return 1 if bad else 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("check", "migrate", "verify"):
        s = sub.add_parser(name)
        s.add_argument("--retro", default="docs/evidence/retro.md")
        s.add_argument("--budget", type=int, default=BUDGET)
        s.add_argument("--row", type=int, default=ROW)
        s.add_argument("--stamp", type=int, default=STAMP)
        if name == "migrate":
            s.add_argument("--archive")
            s.add_argument("--write", action="store_true")
    a = p.parse_args(argv)
    try:
        return {"check": cmd_check, "migrate": cmd_migrate, "verify": cmd_verify}[a.cmd](a)
    except Unmeasurable as exc:
        print("retro_budget: could not measure: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
