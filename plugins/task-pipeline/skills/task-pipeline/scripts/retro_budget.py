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
        over the row limit loses its `Because` cell; a standing instruction written as
        a numbered list item keeps its bold rule and its `*(Retire ...)*` trigger; the
        oldest run stamps past the cap of ten rotate out whole. Without --write it prints the
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


ITEM = re.compile(r"^(\d+)\.\s")
BULLET = re.compile(r"^[-*]\s")
DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def list_items(lines, span, marker=ITEM):
    """(start, end) line spans of numbered list items inside a span, end exclusive.

    An older retro writes its standing instructions as `N. **rule** ...` paragraphs, not
    the template's table. An item runs until the next item, or the first non-indented,
    non-blank line (a vacancy note, a heading's prose); trailing blank lines are not part
    of it. Reading such a floor as zero rows was B-244 in sshlg-skills."""
    out = []
    start, end = span
    i = start
    while i < end:
        if not marker.match(lines[i]):
            i += 1
            continue
        j = i + 1
        while j < end and not marker.match(lines[j]) and (
                not lines[j].strip() or lines[j].startswith((" ", "\t"))
                # a lazy continuation: unindented text directly under the item's last line,
                # unless it opens something of its own (a list, a rule, a note, a table)
                or (lines[j - 1].strip() and not lines[j].startswith(("|", "#", "*("))
                    and not ITEM.match(lines[j]) and not BULLET.match(lines[j])
                    and not re.match(r"^(?:[+]\s|>|\d+\)\s)", lines[j])
                    and not re.match(r"^(?:-{3,}|\*{3,}|_{3,})\s*$", lines[j]))):
            j += 1
        k = j
        while k > i + 1 and not lines[k - 1].strip():
            k -= 1
        out.append((i, k))
        i = j
    return out


def stamp_date(lines, sp):
    """The date a run stamp was written: a table row's Date cell, or the first date in a
    list stamp's opening line. None when it has none (the stamp cannot be ordered)."""
    if lines[sp[0]].startswith("|"):
        c = cells(lines[sp[0]])
        m = re.match(r"\s*(\d{4}-\d{2}-\d{2})", c[0]) if c else None
    else:
        m = DATE.search(lines[sp[0]])
    return m.group(1) if m else None


LEAD = re.compile(r"^(?:[-*]|\d+\.)\s+((?:\*\*.+?\*\*\s*)+)")
ONLY_DATE = re.compile(r"^(?:\*\*\s*\(?\d{4}-\d{2}-\d{2}\)?\s*\*\*\s*)+$")
RETIRE = re.compile(r"\*\((Retire.*?)\)\*")


def lead_of(lines, sp):
    """The item's leading bold spans, verbatim (`**(date)** **rule.**` keeps both), or None
    when there are none or they hold only a date: the rule must survive in the floor."""
    m = LEAD.match(" ".join(l.strip() for l in lines[sp[0]:sp[1]]))
    if not m or ONLY_DATE.match(m.group(1).strip()):
        return None
    return m.group(1).strip()


def loose_prose(lines, span, taken):
    """Paragraphs of a section that are neither table lines nor list stamps: [(start, end)]."""
    out, start, end = [], span[0] + 1, span[1]
    i = start
    while i < end:
        if i in taken or not lines[i].strip() or lines[i].startswith("|"):
            i += 1
            continue
        j = i
        while j < end and j not in taken and lines[j].strip() and not lines[j].startswith("|"):
            j += 1
        # This script's own pointer notes are not prose: moving them again on the next
        # run would make migrate rewrite an over-budget floor forever.
        if not any(POINTER.search(l) for l in lines[i:j]):
            out.append((i, j))
        i = j
    return out


def measure(text, budget=BUDGET, row=ROW, stamp=STAMP):
    lines, spans = sections(text)
    floor = "\n".join(lines[spans[STANDING][0]:spans[STANDING][1]]) + "\n" + \
            "\n".join(lines[spans[STAMPS][0]:spans[STAMPS][1]])
    nbytes = len(floor.encode("utf-8"))
    std = [(i, i + 1) for i in table_rows(lines, spans[STANDING])]
    form = "table"
    if not std:
        std = list_items(lines, spans[STANDING])
        form = "numbered list" if std else "table"
    # A run stamp is a table row or, in an older retro, a `- **date — title** ...` item.
    stm = [(i, i + 1) for i in table_rows(lines, spans[STAMPS])] + \
        list_items(lines, spans[STAMPS], BULLET)
    stm.sort()
    width = lambda sp: len("\n".join(lines[sp[0]:sp[1]]))
    over = []
    if nbytes > budget:
        over.append("floor is %d bytes, over the budget of %d" % (nbytes, budget))
    for sp in std:
        if width(sp) > row:
            label = (cells(lines[sp[0]]) or ["?"])[0] if form == "table" \
                else "#" + ITEM.match(lines[sp[0]]).group(1)
            over.append("standing row %s is %d chars, over %d" % (label, width(sp), row))
    for sp in stm:
        if width(sp) > stamp:
            c = cells(lines[sp[0]]) if lines[sp[0]].startswith("|") else []
            label = "%s %s" % (c[0], c[2] if len(c) > 2 else "") if c \
                else "%s (list)" % (stamp_date(lines, sp) or "undated")
            over.append("stamp %s is %d chars, over %d" % (label.strip(), width(sp), stamp))
    if len(std) > CAP:
        over.append("%d standing rows, over the cap of %d" % (len(std), CAP))
    if len(stm) > CAP:
        over.append("%d run stamps, over the cap of %d" % (len(stm), CAP))
    return {
        "bytes": nbytes, "tokens": nbytes // 4, "budget": budget,
        "standing": len(std), "standing_max": max([width(sp) for sp in std] or [0]), "form": form,
        "stamps": len(stm), "stamps_max": max([width(sp) for sp in stm] or [0]),
        "over": over, "lines": lines, "spans": spans, "std": std, "stm": stm,
    }


def summary(m, row=ROW, stamp=STAMP):
    return ("retro floor: %d bytes · ~%d tokens (bytes/4) · budget %d · standing %d/%d rows%s, "
            "largest %d/%d · stamps %d/%d, largest %d/%d"
            % (m["bytes"], m["tokens"], m["budget"], m["standing"], CAP,
               " (numbered list)" if m.get("form") == "numbered list" else "", m["standing_max"], row,
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


ROTATED = re.compile(r"^Rotated out: ([0-9]+) oldest run stamps, verbatim in (\S+) sha256:([0-9a-f]{12,64})$")
ARCHIVED = re.compile(r"<!-- sha256:([0-9a-f]{64}) -->\n(.*?)\n(?=\n#{2,3} |\Z)", re.S)


def rotation_lines(lines, span, rel):
    """(line index, stamp count, short sha) of each rotation pointer into `rel`."""
    out = []
    for k in range(span[0], span[1]):
        r = ROTATED.match(lines[k])
        if r and r.group(2) == rel:
            out.append((k, int(r.group(1)), r.group(3)))
    return out


def archived_text(path, short):
    """(offset, text) of the archive block whose text hashes to `short`, or None."""
    try:
        arch = read(path)
    except Unmeasurable:
        return None
    for m in ARCHIVED.finditer(arch):
        if m.group(1).startswith(short) and digest(m.group(2)) == m.group(1):
            return m.start(), m.group(2)
    return None


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
    moved = []      # (first line, last line exclusive, replacement lines, block, label)
    head = m["spans"][STAMPS][0]
    notes = []      # pointer lines inserted under the Run stamps heading
    rotated = set()
    if len(m["stm"]) > CAP:
        # The cap rotates the OLDEST stamps out whole (references/retrospective.md, *The
        # stamp table is capped at ten*). Oldest is read from the date, never from the
        # position: tables and lists are written both ways round.
        # A same-day tie is broken by position, the way its own block is written: a list
        # written newest-first and a table written oldest-first can sit side by side.
        def block_of(sp):
            if not lines[sp[0]].startswith("|"):
                return "list"
            k = sp[0]
            while k > 0 and lines[k - 1].startswith("|"):
                k -= 1
            return k
        blocks = {}
        for n, sp in enumerate(m["stm"]):
            blocks.setdefault(block_of(sp), []).append((n, stamp_date(lines, sp)))
        newest_first, votes = {}, []
        for key, seq in blocks.items():
            ds = [d for _, d in seq]
            down = sum(1 for x, y in zip(ds, ds[1:]) if x and y and x > y)
            up = sum(1 for x, y in zip(ds, ds[1:]) if x and y and x < y)
            newest_first[key] = None if down == up else down > up
            if newest_first[key] is not None:
                votes.append(newest_first[key])
        # A block whose dates show no direction takes the section's; with no evidence
        # anywhere, newest first, the template's order.
        fallback = sum(votes) * 2 >= len(votes) if votes else True
        for key in newest_first:
            if newest_first[key] is None:
                newest_first[key] = fallback
        dated = [(stamp_date(lines, sp), -n if newest_first[block_of(sp)] else n, sp)
                 for n, sp in enumerate(m["stm"])]
        if any(d is None for d, _, _ in dated):
            print("migrate: a run stamp carries no YYYY-MM-DD date; rotate the stamps by hand")
        else:
            rotated = set(sp for _, _, sp in sorted(dated)[:len(dated) - CAP])
            # A rotated table row travels under its table's header, so the archive keeps
            # a table and the header of a table emptied by the rotation is not lost.
            parts, headed = [], set()
            for sp in m["stm"]:
                if sp not in rotated:
                    continue
                if lines[sp[0]].startswith("|"):
                    k = sp[0]
                    while k > 0 and lines[k - 1].startswith("|"):
                        k -= 1
                    if k not in headed:
                        headed.add(k)
                        parts.append("\n".join(lines[k:k + 2]))
                parts.append("\n".join(lines[sp[0]:sp[1]]))
            text = "\n".join(parts)
            for k in headed:
                j = k + 2
                while j < len(lines) and lines[j].startswith("|"):
                    j += 1
                if all((r, r + 1) in rotated for r in range(k + 2, j)):
                    moved.append((k, k + 2, [], None, None))   # archived above, with its rows
            # B-246: one pointer line per archive, not one per rotation. Earlier rotations
            # into the same archive are re-archived with this one as a single block, and
            # their lines give way to one line naming it. The archive stays append-only:
            # the earlier blocks remain, only the floor stops pointing at them.
            count, earlier = len(rotated), []
            for k, n, short in rotation_lines(lines, m["spans"][STAMPS], rel):
                prior = archived_text(archive, short)
                if prior is None:
                    print("migrate: the rotation line sha256:%s does not resolve in %s; "
                          "it stays as its own line" % (short, rel))
                    continue
                earlier.append((prior[0], k, prior[1]))
                count += n
            for _, k, _ in earlier:
                moved.append((k, k + 1, [], None, None))
            if earlier:
                text = "\n".join([t for _, _, t in sorted(earlier)] + [text])
            h, b = block("stamps", "%d oldest rotated" % count, text)
            for sp in rotated:
                moved.append((sp[0], sp[1], [], None, None))
            notes.append(("Rotated out: %d oldest run stamps, verbatim in %s sha256:%s"
                          % (count, rel, h[:12]), b, "%d oldest run stamps rotated" % len(rotated)))
    for sp in m["stm"]:
        i = sp[0]
        if sp in rotated or len("\n".join(lines[sp[0]:sp[1]])) <= a.stamp:
            continue
        if not lines[i].startswith("|"):
            # A list stamp keeps its bold title; the narrative moves.
            item = "\n".join(lines[sp[0]:sp[1]])
            title = lead_of(lines, sp)
            if not title:
                print("migrate: the %s stamp has no **bold** title to keep; shorten it by hand"
                      % (stamp_date(lines, sp) or "undated"))
                continue
            h, b = block("stamp", stamp_date(lines, sp) or "undated", item)
            ptr = " moved: %s sha256:%s" % (rel, h[:12])
            t = title
            if len("- %s%s" % (t, ptr)) > a.stamp:
                inner = re.sub(r"\*\*", "", t)
                t = "**%s…**" % inner[:max(8, a.stamp - len("- ****…") - len(ptr))].rstrip()
            moved.append((sp[0], sp[1], ["- %s%s" % (t, ptr)], b,
                          "stamp %s (list)" % (stamp_date(lines, sp) or "undated")))
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
        moved.append((i, i + 1, [new], b, "stamp %s %s" % (c[0], c[2])))
    if m["bytes"] > a.budget:
        # Prune paragraphs between the stamps were a measured share of the floor
        # (*A prune that retires nothing writes its count into the stamp row*): over
        # budget, every loose paragraph of the Run stamps section moves, verbatim.
        taken = set(k for s0, s1 in m["stm"] for k in range(s0, s1))
        prose = loose_prose(lines, m["spans"][STAMPS], taken)
        # verify ends an archive block at a blank line before a heading, so a paragraph
        # holding a heading stays in the floor rather than moving unprovable.
        held = [pp for pp in prose if any(re.match(r"^#{1,6} ", l) for l in lines[pp[0]:pp[1]])]
        for p0, _ in held:
            print("migrate: a heading inside Run stamps stays in the floor: %s" % lines[p0][:60])
        prose = [pp for pp in prose if pp not in held]
        if prose:
            text = "\n\n".join("\n".join(lines[p0:p1]) for p0, p1 in prose)
            h, b = block("stamps prose", "%d paragraphs" % len(prose), text)
            for p0, p1 in prose:
                moved.append((p0, p1, [], None, None))
            notes.append(("Moved out: %d loose paragraphs, verbatim in %s sha256:%s"
                          % (len(prose), rel, h[:12]), b, "%d prose paragraphs" % len(prose)))
    if notes:
        moved.append((head + 1, head + 1, sum([["", n] for n, _, _ in notes], []), None, None))
        for n, b, label in notes:
            moved.append((head + 1, head + 1, [], b, label))
    for s0, s1 in m["std"]:
        item = "\n".join(lines[s0:s1])
        if len(item) <= a.row:
            continue
        # Already migrated and still too long: its story is gone, the rule itself is the
        # length. Moving the pointer again would rewrite the floor on every run.
        if POINTER.search(item):
            continue
        if m["form"] == "numbered list":
            # Keep the rule (its bold lead) and its retire-when trigger; the story moves.
            flat = " ".join(l.strip() for l in lines[s0:s1])
            num = ITEM.match(lines[s0]).group(1)
            lead = lead_of(lines, (s0, s1))
            retire = RETIRE.findall(flat)
            if not lead:
                print("migrate: standing #%s opens with no **bold** rule (or only a date); "
                      "rewrite it by hand" % num)
                continue
            h, b = block("standing", "#" + num, item)
            new = "%s. %s%s story: %s sha256:%s" % (
                num, lead, (" *(%s)*" % retire[-1]) if retire else "", rel, h[:12])
            if not retire:
                print("migrate: standing #%s carries no *(Retire ...)* trigger; add one by hand" % num)
            moved.append((s0, s1, [new], b, "standing #%s story" % num))
            continue
        c = cells(lines[s0])
        if len(c) < 5:
            continue
        h, b = block("standing", c[0], c[4])
        c[4] = "story: %s sha256:%s" % (rel, h[:12])
        moved.append((s0, s1, ["| " + " | ".join(c) + " |"], b, "standing %s Because" % c[0]))
    if not moved:
        print(summary(m, a.row, a.stamp))
        print("migrate: nothing to move")
        return 1 if m["over"] else 0
    for s0, s1, new, _, label in moved:
        if label:
            print("migrate: %s -> %s%s" % (label, rel, "" if s0 == s1 else " (%d -> %d chars)" % (
                len("\n".join(lines[s0:s1])), len("\n".join(new)))))
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
        for _, _, _, b, _ in moved:
            if b:
                fh.write(b)
    # Rebuild from the bottom so earlier spans keep their indices.
    for s0, s1, new, _, _ in sorted(moved, key=lambda x: (x[0], x[1]), reverse=True):
        lines[s0:s1] = new
    # Removed stamps leave their blank separators behind: within Run stamps, one blank
    # line between blocks is enough. Only a run that removed something tidies, so a
    # table retro that only had a row shortened keeps its bytes (1.99.0 behaviour).
    removed = any(s0 != s1 and not new for s0, s1, new, _, _ in moved)
    _, sp2 = sections("\n".join(lines))
    a0, a1 = sp2[STAMPS]
    seg = lines[a0:a1]
    kept = []
    for k, line in enumerate(seg):
        if removed and not line.strip() and kept and not kept[-1].strip():
            continue
        kept.append(line)
    lines[a0:a1] = kept
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
        for m in ARCHIVED.finditer(arch):
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
