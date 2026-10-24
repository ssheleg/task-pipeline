#!/usr/bin/env python3
"""The release impact card: who a release touches, how it is watched, and the way back, as a
command with an exit code. Stdlib only.

    release_impact.py check <card.md> [--users external|internal|none]
                          [--pipeline pipeline.json] [--outcome] [--json]
        stage 7, before any outward act: the card (`release-impact/1`) answers its four
        sections (who is affected and how, tracking, alerting, rollback or hotfix), each
        answered or `n/a: <reason>`. Tracking names its watch window, alerting says whether it
        was ever seen firing, and rollback states its decision trigger; none of the three is
        `n/a` on a release with users. `--outcome` is stage 8: the card also carries its
        `## Outcome` with a `Result:` of held, rolled back, hotfixed or watching.

Who has users: `--users`, else `pipeline.json` → `release.users`, else the card's own `users:`
line. Absent everywhere means unknown, treated as `external` and said so. On `none` the card
is not owed; a card that exists is still checked.

**A check that could not run says NOT_RUN, and NOT_RUN is never PASS.** No card where one is
owed is NOT_RUN.

Exit codes: 0 PASS · 1 FAIL · 2 usage, or an input that cannot be read · 3 NOT_RUN.
The doctrine is `references/release-impact.md`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

SCHEMA = "release-impact/1"
USERS = ("external", "internal", "none")
RESULTS = ("held", "rolled back", "hotfixed", "watching")
# The four sections, in order, by the words their heading opens with (after an optional number).
SECTIONS = (
    ("who", "who is affected"),
    ("tracking", "tracking"),
    ("alerting", "alerting"),
    ("rollback", "rollback"),
)
TITLES = {"who": "1. Who is affected and how", "tracking": "2. Tracking",
          "alerting": "3. Alerting", "rollback": "4. Rollback or hotfix"}
# Sections the operator's rule never lets be n/a on a release with users.
NEVER_NA = ("tracking", "alerting", "rollback")
COMMENT = re.compile(r"<!--.*?-->", re.S)
HEADING = re.compile(r"^##\s+(.+?)\s*$")
HEADER = re.compile(r"^(schema|release|users|date)\s*:\s*(.*?)\s*$", re.I)
# A field line: `- **Label:** value`, `**Label**: value` or `Label: value`.
FIELD = re.compile(r"^\s*(?:[-*]\s+)?(?:\*\*([^*:]+?)\s*:?\s*\*\*\s*:?|([A-Za-z][A-Za-z /]*?)\s*:)\s*(.*?)\s*$")
NA = re.compile(r"^n/?a\b\.?\s*[:;,(-]?\s*(.*?)\)?\s*$", re.I)


def _usage(msg):
    print("release_impact: %s" % msg, file=sys.stderr)
    return 2


def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _is_na(value):
    """(True, reason) when the value is an n/a answer; (False, None) otherwise. A reason is a
    word of three letters or more, so `n/a`, `n/a:` and `n/a: -` carry none."""
    m = NA.match(value.strip())
    if not m:
        return False, None
    reason = m.group(1).strip()
    return True, (reason if re.search(r"[^\W\d_]{3,}", reason) else "")


def _section_key(title):
    t = re.sub(r"^\d+[.)]?\s*", "", title.strip()).lower()
    for key, opener in SECTIONS:
        if t.startswith(opener):
            return key
    if t.startswith("outcome"):
        return "outcome"
    return None


def parse(text):
    """{'header': {...}, 'sections': {key: [body lines]}, 'duplicates': [...], 'todo': [...]}.
    HTML comments are removed first: guidance in a comment is never an answer."""
    text = COMMENT.sub("", text)
    header, sections, dups, todo = {}, {}, [], []
    cur, infence = None, False
    for n, line in enumerate(text.splitlines(), 1):
        if re.match(r"^\s*(```|~~~)", line):
            infence = not infence
        if "TODO" in line:
            todo.append(n)
        m = None if infence else HEADING.match(line)
        if m:
            cur = _section_key(m.group(1))
            if cur is not None:
                if cur in sections:
                    dups.append(cur)
                sections[cur] = []
            continue
        if cur is None:
            h = HEADER.match(line)
            if h and h.group(1).lower() not in header:
                header[h.group(1).lower()] = h.group(2)
            continue
        sections[cur].append(line)
    return {"header": header, "sections": sections, "duplicates": dups, "todo": todo}


def fields(lines):
    """[(label lowercased, value)] for every field-shaped line of a section body."""
    out = []
    for line in lines:
        m = FIELD.match(line)
        if m:
            out.append(((m.group(1) or m.group(2)).strip().lower(), m.group(3).strip()))
    return out


def field(lines, label):
    for k, v in fields(lines):
        if k == label:
            return v
    return None


def section_state(lines):
    """'empty', ('na', reason) or 'answered'."""
    body = [l.strip() for l in lines if l.strip()]
    if not body:
        return "empty", None
    na, reason = _is_na(re.sub(r"^[-*]\s+", "", body[0]))
    if na and len(body) == 1:
        return "na", reason
    return "answered", None


def check(text, users=None, outcome=False):
    """(verdict, problems, notes, states, users). `users` is the project's value, or None."""
    doc = parse(text)
    problems, notes = [], []
    head = doc["header"]
    if head.get("schema", "").strip() != SCHEMA:
        problems.append("the card is not %s: its header has no `schema: %s` line" % (SCHEMA, SCHEMA))
    card_users = head.get("users", "").strip().lower() or None
    if card_users and card_users not in USERS:
        problems.append("users is one of %s, not %r" % (", ".join(USERS), card_users))
        card_users = None
    if users and card_users and users != card_users:
        problems.append("the card says users: %s and the project says %s; one of them is wrong"
                        % (card_users, users))
    if not users:
        users = card_users
    if not users:
        users = "external"
        notes.append("who has users is unknown (no --users, no release.users, no users: line): "
                     "treated as external; record the answer in pipeline.json")
    for d in sorted(set(doc["duplicates"])):
        problems.append("section %r appears twice; the card holds one of each" % TITLES.get(d, d))
    if doc["todo"]:
        problems.append("TODO left on line(s) %s: every placeholder is replaced"
                        % ", ".join(map(str, doc["todo"][:10])))
    states = {}
    secs = doc["sections"]
    for key, _ in SECTIONS:
        title = TITLES[key]
        if key not in secs:
            states[key] = "missing"
            problems.append("no section %r" % title)
            continue
        st, reason = section_state(secs[key])
        states[key] = st
        if st == "empty":
            problems.append("section %r is empty: answer it, or `n/a: <reason>`" % title)
        elif st == "na":
            if not reason:
                problems.append("section %r is n/a with no reason: `n/a: <reason>`" % title)
            elif key in NEVER_NA and users != "none":
                problems.append("section %r cannot be n/a on a release with users: there is always "
                                "tracking, an alert and a way back" % title)
            else:
                notes.append("%s: n/a: %s" % (title, reason))
        # n/a on any field line carries its reason too.
        for label, value in fields(secs[key]):
            na, why = _is_na(value) if value else (False, None)
            if na and not why:
                problems.append("%s: `%s` is n/a with no reason: `n/a: <reason>`" % (title, label))
    if states.get("tracking") == "answered":
        w = field(secs["tracking"], "watch window")
        if not w or _is_na(w)[0]:
            problems.append("section %r names no watch window (`Watch window: <how long>`)"
                            % TITLES["tracking"])
    if states.get("alerting") == "answered":
        s = field(secs["alerting"], "seen firing")
        if not s:
            problems.append("section %r does not say whether the alert was ever seen firing "
                            "(`Seen firing: yes (when)` or `never`)" % TITLES["alerting"])
        elif re.match(r"^never\b", s, re.I):
            notes.append("the alert has never been seen firing: it is untested")
    if states.get("rollback") == "answered":
        t = field(secs["rollback"], "decision trigger")
        if not t or _is_na(t)[0] or not re.search(r"\b(if|when|если|когда)\b", t, re.I):
            problems.append("section %r states no decision trigger (`Decision trigger: roll back "
                            "if <X> within <Y>`)" % TITLES["rollback"])
    if outcome:
        if "outcome" not in secs:
            problems.append("stage 8: no `## Outcome` section recording what the watch read")
        else:
            r = (field(secs["outcome"], "result") or "").strip().lower()
            if not any(r.startswith(x) for x in RESULTS):
                problems.append("stage 8: `Result:` is one of %s, not %r" % (", ".join(RESULTS), r))
            elif r.startswith("watching"):
                notes.append("the watch window is still open: %s" % r)
    return ("FAIL" if problems else "PASS"), problems, notes, states, users


def pipeline_users(path):
    """release.users from pipeline.json; None when absent. Raises ValueError on bad input."""
    cfg = json.loads(read_text(path))
    rel = cfg.get("release") if isinstance(cfg, dict) else None
    u = rel.get("users") if isinstance(rel, dict) else None
    if u is not None and u not in USERS:
        raise ValueError("release.users is one of %s, not %r" % (", ".join(USERS), u))
    return u


def emit(verdict, problems, notes, as_json, extra=None):
    if as_json:
        print(json.dumps(dict(verdict=verdict, problems=problems, notes=notes, **(extra or {})), indent=2))
    else:
        print("release_impact: %s" % verdict)
        for p in problems:
            print("  - %s" % p)
        for n in notes:
            print("  note: %s" % n)
    return {"PASS": 0, "FAIL": 1, "NOT_RUN": 3}[verdict]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check")
    p.add_argument("path")
    p.add_argument("--users", choices=USERS)
    p.add_argument("--pipeline", help="read release.users from this pipeline.json (--users wins)")
    p.add_argument("--outcome", action="store_true", help="stage 8: the card carries its Outcome")
    p.add_argument("--json", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code else 0
    users = a.users
    if not users and a.pipeline:
        try:
            users = pipeline_users(a.pipeline)
        except OSError as exc:
            return _usage("cannot read %s (%s)" % (a.pipeline, exc.strerror or exc))
        except ValueError as exc:
            return _usage("%s: %s" % (a.pipeline, exc))
    if not os.path.exists(a.path):
        if users == "none":
            return emit("PASS", [], ["users: none: the card is not owed; write `users: none` "
                                     "beside the stage 7 verdict"], a.json, {"users": "none"})
        why = "" if users else " (who has users is unknown: treated as external)"
        return emit("NOT_RUN", ["no release impact card at %s; one is owed before the outward "
                                "act%s" % (a.path, why)], [], a.json, {"users": users or "external"})
    try:
        text = read_text(a.path)
    except (OSError, UnicodeDecodeError) as exc:
        return _usage("cannot read %s (%s)" % (a.path, getattr(exc, "strerror", None) or exc))
    verdict, probs, notes, states, resolved = check(text, users, a.outcome)
    return emit(verdict, probs, notes, a.json, {"users": resolved, "sections": states})


if __name__ == "__main__":
    sys.exit(main())
