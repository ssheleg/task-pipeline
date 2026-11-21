#!/usr/bin/env python3
"""spec_protocol.py: stages 0-4 as a protocol a script checks, not prose a model recalls.

`references/spec-protocol.md` is the doctrine. This file makes four of its rules
mechanical, standard library only, no model, no network:

    size      --reqs N --files N [--surfaces N] [--contract] [--outward]
              [--irreversible] [--cross-project] [--new-domain] [--unknowns N] [--json]
              The spec's size (S, M, L) from the brief's facts: which sections it owes,
              how deep the research goes. Small is shorter, never incomplete.
    questions SPEC [--json]
              The grill's question ledger: every question carries a class (strategy,
              tactics, known-domain, unknown). Tactics and known domains are decided
              by the agent and recorded; only strategy and a researched unknown reach
              the owner, as one batch, each with a recommended default.
    research  init DIR --tier T --question Q --author FAMILY/TIER
              plan --tier T [--json]
              check DIR [--tier T] [--json]
              The research dossier: skeleton first, sources with what was actually
              read, citations that resolve, validators of another model family.
    check     SPEC [--tier T] [--json]
              The spec is complete for its size: sections, ledger, research, no TBD.
    gate      SPEC [--plan PLAN] [--board FILE]
              The order spec -> board -> build: the spec passes, the board rows and
              the plan cite it.

Exit 0 pass, 1 findings, 2 usage.
"""
import argparse
import json
import os
import re
import sys

TIERS = {
    "S": {
        "sections": ["Goal", "Scope", "Requirements", "Design", "Questions", "Tests"],
        "research": {"scouts": 0, "validators": 0, "sources": 0, "primary": 0},
        "note": "short but complete: every section present and filled",
    },
    "M": {
        "sections": ["Goal", "Scope", "Requirements", "Design", "Contracts",
                     "Edge cases", "Questions", "Decisions", "Tests", "Rollout"],
        "research": {"scouts": 2, "validators": 1, "sources": 6, "primary": 1},
        "note": "two scouts in parallel, one decider, one validator of another family",
    },
    "L": {
        "sections": ["Goal", "Scope", "Requirements", "Architecture", "Data",
                     "Contracts", "Edge cases", "Non-functional", "Alternatives",
                     "Risks", "Questions", "Decisions", "Tests", "Rollout"],
        "research": {"scouts": 4, "validators": 2, "sources": 12, "primary": 2},
        "note": "up to four scouts, one decider, two blind validators of two other families",
    },
}
# A new domain owes research even in a small spec: one scout, three sources read.
DESK = {"scouts": 1, "validators": 0, "sources": 3, "primary": 1}

CLASSES = ("strategy", "tactics", "known-domain", "unknown")
BY = ("owner", "agent", "pending")
PRIMARY_KINDS = {"docs", "paper", "code", "standard", "benchmark", "measurement"}
KINDS = PRIMARY_KINDS | {"article", "community", "model"}
VERDICTS = ("agree", "partial", "disagree")
VAGUE = re.compile(r"\b(TBD|TODO|to be decided|decide later|later decide)\b|\?\?\?", re.I)
CITE = re.compile(r"\[(S\d+)\]")
# Words that usually mean a question is the owner's, or the agent's. A mismatch warns.
STRATEGIC = re.compile(r"\b(vision|concept|positioning|price|pricing|audience|brand|"
                       r"promise|business model|who is it for|meaning|naming|name the product)\b", re.I)
TACTICAL = re.compile(r"\b(library|framework|schema|format|port|endpoint|database|index|"
                      r"cache|retry|timeout|refactor|test|lint|file layout|algorithm|queue)\b", re.I)


# ---------------------------------------------------------------- size

def size(reqs, files, surfaces=1, contract=False, outward=False, irreversible=False,
         cross_project=False, new_domain=False, unknowns=0):
    score, why = 0, []
    for cond, pts, text in (
            (reqs > 8, 2, "%d requirements" % reqs), (3 < reqs <= 8, 1, "%d requirements" % reqs),
            (files > 20, 2, "%d files" % files), (5 < files <= 20, 1, "%d files" % files),
            (surfaces > 1, 1, "%d surfaces" % surfaces), (contract, 1, "a contract changes"),
            (outward, 1, "an outward effect"), (irreversible, 2, "hard to reverse"),
            (cross_project, 1, "other projects depend on it"),
            (new_domain, 1, "a domain the project has not worked in"),
            (unknowns > 0, 1, "%d material unknown(s)" % unknowns)):
        if cond:
            score += pts
            why.append(text)
    tier = "S" if score <= 1 else "M" if score <= 4 else "L"
    research = dict(TIERS[tier]["research"])
    if tier == "S" and new_domain:
        research = dict(DESK)
    return {"tier": tier, "score": score, "why": why or ["nothing raises it"],
            "sections": TIERS[tier]["sections"], "research": research,
            "note": TIERS[tier]["note"]}


# ---------------------------------------------------------------- markdown helpers

def sections(text):
    """{heading lowercased: body} for level-2 headings."""
    out, cur, buf = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m and not line.startswith("###"):
            if cur is not None:
                out[cur] = "\n".join(buf)
            cur, buf = m.group(1).strip().lower(), []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out[cur] = "\n".join(buf)
    return out


def find_section(secs, name):
    name = name.lower()
    for h, body in secs.items():
        if h == name or h.startswith(name + " ") or h.startswith(name + ":") or h.startswith(name + " ("):
            return body
    return None


def table(body):
    """Rows of the first Markdown table in body, as dicts keyed by lowercased header."""
    rows, header = [], None
    for line in (body or "").splitlines():
        s = line.strip()
        if not s.startswith("|"):
            if header is not None and rows:
                break
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
        elif all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        else:
            rows.append(dict(zip(header, cells + [""] * (len(header) - len(cells)))))
    return rows


def header_value(text, key):
    m = re.search(r"^\s*(?:\*\*)?%s(?:\*\*)?\s*:\s*(.+?)\s*$" % re.escape(key), text, re.M | re.I)
    return m.group(1).strip().strip("`") if m else None


# ---------------------------------------------------------------- questions

def questions(text):
    """(owner_batch, errors, warnings) for the spec's `## Questions` ledger."""
    body = find_section(sections(text), "questions")
    if body is None:
        return [], ["no `## Questions` section: the grill's ledger is owed even when empty "
                    "(write `none: <why>`)"], []
    rows = table(body)
    if not rows:
        if re.search(r"\bnone\b", body, re.I):
            return [], [], []
        return [], ["`## Questions` has no ledger table and does not say `none`"], []
    need = {"id", "question", "class", "answer", "by", "basis"}
    missing = need - set(rows[0])
    if missing:
        return [], ["ledger columns missing: " + ", ".join(sorted(missing))], []
    owner, errors, warns = [], [], []
    for r in rows:
        qid, q, cls, ans, by, basis = (r[k] for k in ("id", "question", "class", "answer", "by", "basis"))
        cls, by = cls.lower(), by.lower()
        if cls not in CLASSES:
            errors.append("%s: class %r is not one of %s" % (qid, cls, ", ".join(CLASSES)))
            continue
        if by not in BY:
            errors.append("%s: by %r is not one of %s" % (qid, by, ", ".join(BY)))
            continue
        if cls in ("tactics", "known-domain"):
            if by == "pending":
                errors.append("%s: a %s question never waits on the owner: decide it, record "
                              "the answer and its basis" % (qid, cls))
            elif not ans or not basis:
                errors.append("%s: a decided %s question needs its answer and its basis" % (qid, cls))
            elif cls == "known-domain" and not re.search(r"https?://|\[S\d+\]|[\w./-]+\.\w+|#L\d+", basis):
                errors.append("%s: a known-domain answer cites its source (URL, [Sn] or a path)" % qid)
            if cls == "tactics" and STRATEGIC.search(q) and not TACTICAL.search(q):
                warns.append("%s: reads like strategy (%s); is it the owner's?" % (qid, STRATEGIC.search(q).group(0)))
        else:  # strategy, unknown
            if cls == "unknown" and not re.search(r"research|\[S\d+\]|https?://", basis, re.I):
                errors.append("%s: an unknown is researched before it is asked: link the "
                              "research that could not answer it" % qid)
            if by == "pending":
                if not ans:
                    errors.append("%s: a question to the owner carries a recommended default "
                                  "in `answer`; the work goes on with it" % qid)
                owner.append({"id": qid, "class": cls, "question": q, "default": ans})
            elif by == "agent" and cls == "strategy":
                errors.append("%s: strategy is the owner's: mark it `pending` with a default, "
                              "or record the owner's words with `by: owner`" % qid)
            if cls == "strategy" and TACTICAL.search(q) and not STRATEGIC.search(q):
                warns.append("%s: reads like tactics (%s); can the agent decide it?" % (qid, TACTICAL.search(q).group(0)))
    return owner, errors, warns


# ---------------------------------------------------------------- research

SKELETON = """# Research: {question}

Question: {question}
Tier: {tier}
Author: {author}

## Findings

## Options

## Recommendation

## What would refute it

## Rejected

## Validation

| validator | family | verdict | note |
|---|---|---|---|
"""


def research_init(d, tier, question, author):
    os.makedirs(d, exist_ok=True)
    readme, src = os.path.join(d, "README.md"), os.path.join(d, "sources.json")
    if os.path.exists(readme):
        return "kept " + readme
    open(readme, "w").write(SKELETON.format(question=question, tier=tier, author=author))
    if not os.path.exists(src):
        open(src, "w").write("[]\n")
    return "wrote " + readme + " and sources.json"


def research_plan(tier):
    r = TIERS[tier]["research"] if tier in TIERS else DESK
    roles = []
    if r["scouts"]:
        roles.append({"role": "scout", "count": r["scouts"], "tier": "work",
                      "does": "web search and reading; fills Findings, Options and sources.json; "
                              "recommends nothing; what it could not open it did not read"})
        roles.append({"role": "decider", "count": 1, "tier": "deep",
                      "does": "rechecks numbers and citations, writes Recommendation, What would "
                              "refute it and Rejected; sends gaps back to a scout, never fills "
                              "them from memory"})
    if r["validators"]:
        roles.append({"role": "validator", "count": r["validators"], "tier": "deep",
                      "family": "another model family than the author, each blind to the other",
                      "does": "verdict agree, partial or disagree with evidence in Validation"})
        roles.append({"role": "merge", "count": 1, "tier": "fast",
                      "does": "on any disagree: Resolution, whose evidence is stronger and why"})
    return {"tier": tier, "minimums": r, "roles": roles,
            "budget": "the host's per-run spend line; an unknown cost is never counted as zero"}


def research_check(d, tier=None):
    errors, warns = [], []
    readme, src = os.path.join(d, "README.md"), os.path.join(d, "sources.json")
    if not os.path.isfile(readme):
        return ["no README.md in " + d], warns
    text = open(readme).read()
    tier = tier or (header_value(text, "Tier") or "").upper()[:1]
    if tier not in TIERS:
        errors.append("no `Tier: S|M|L` header and no --tier")
        tier = "S"
    mins = TIERS[tier]["research"] if tier != "S" else DESK
    author = (header_value(text, "Author") or "").lower()
    if not author:
        errors.append("no `Author: <family>/<tier>` header")
    fam = author.split("/")[0]
    secs = sections(text)
    for name in ("Findings", "Options", "Recommendation", "What would refute it", "Rejected", "Validation"):
        body = find_section(secs, name)
        if body is None or not body.strip():
            errors.append("section `%s` missing or empty" % name)
    try:
        sources = json.load(open(src)) if os.path.isfile(src) else None
    except ValueError as e:
        sources, _ = None, errors.append("sources.json does not parse: %s" % e)
    if sources is None:
        errors.append("no sources.json")
        sources = []
    by_id = {}
    for s in sources:
        miss = [k for k in ("id", "kind", "title", "url", "read", "claim") if k not in s]
        if miss:
            errors.append("source %s lacks %s" % (s.get("id", "?"), ", ".join(miss)))
            continue
        if s["kind"] not in KINDS:
            errors.append("source %s: kind %r unknown" % (s["id"], s["kind"]))
        by_id[s["id"]] = s
    counted = [s for s in by_id.values() if s.get("read") is True and s.get("kind") != "model"]
    primary = [s for s in counted if s["kind"] in PRIMARY_KINDS]
    if len(counted) < mins["sources"]:
        errors.append("%d source(s) read, tier %s needs %d (a model's answer is not a source)"
                      % (len(counted), tier, mins["sources"]))
    if len(primary) < mins["primary"]:
        errors.append("%d primary source(s), tier %s needs %d" % (len(primary), tier, mins["primary"]))
    for sid in sorted(set(CITE.findall(text))):
        s = by_id.get(sid)
        if s is None:
            errors.append("[%s] is cited and not in sources.json" % sid)
        elif s.get("read") is not True:
            errors.append("[%s] is cited but was not opened: what was not read is not evidence" % sid)
        elif s.get("kind") == "model":
            errors.append("[%s] is a model's answer cited as evidence" % sid)
    rows = table(find_section(secs, "validation") or "")
    other = [r for r in rows if r.get("family", "").lower() and r.get("family", "").lower() != fam]
    fams = {r["family"].lower() for r in other}
    if len(other) < mins["validators"]:
        errors.append("%d validator(s) of another family than %r, tier %s needs %d"
                      % (len(other), fam or "?", tier, mins["validators"]))
    if mins["validators"] >= 2 and len(fams) < 2:
        errors.append("tier %s needs validators of two different families" % tier)
    for r in rows:
        if r.get("verdict", "").lower() not in VERDICTS:
            errors.append("validator %s: verdict %r is not agree, partial or disagree"
                          % (r.get("validator", "?"), r.get("verdict")))
    if any(r.get("verdict", "").lower() == "disagree" for r in rows):
        body = find_section(secs, "resolution")
        if body is None or not body.strip():
            errors.append("a validator disagrees and there is no `## Resolution` "
                          "(whose evidence is stronger and why)")
    return errors, warns


# ---------------------------------------------------------------- spec check and gate

def check(path, tier=None):
    text = open(path).read()
    errors, warns = [], []
    declared = (header_value(text, "Size") or "").upper()[:1]
    tier = (tier or declared or "").upper()[:1]
    if tier not in TIERS:
        return ["no `Size: S|M|L` header and no --tier (run `spec_protocol.py size`)"], warns, []
    if declared and declared != tier:
        errors.append("the spec says Size %s, the check was asked for %s" % (declared, tier))
    secs = sections(text)
    for name in TIERS[tier]["sections"]:
        body = find_section(secs, name)
        if body is None:
            errors.append("section `%s` missing (size %s owes it; a skip says why in one line)" % (name, tier))
        elif not body.strip():
            errors.append("section `%s` is empty" % name)
    for n, line in enumerate(text.splitlines(), 1):
        if VAGUE.search(line) and not line.lstrip().startswith("|"):
            errors.append("line %d leaves a decision open (%s): decide it or put it in "
                          "the Questions ledger" % (n, VAGUE.search(line).group(0)))
    owner, qerr, qwarn = questions(text)
    errors += qerr
    warns += qwarn
    research = header_value(text, "Research")
    if tier in ("M", "L") or research:
        if not research or research.lower().startswith("none"):
            errors.append("size %s owes research: a `Research: <dossier dir>` header" % tier)
        else:
            d = research if os.path.isabs(research) else os.path.join(os.path.dirname(path), research)
            if not os.path.isdir(d):
                d = research if os.path.isdir(research) else d
            rerr, rwarn = research_check(d, tier if tier != "S" else None)
            errors += ["research: " + e for e in rerr]
            warns += ["research: " + w for w in rwarn]
    return errors, warns, owner


def gate(spec, plan=None, board=None):
    errors, _, _ = check(spec)
    slug = os.path.splitext(os.path.basename(spec))[0]
    for label, f in (("board", board), ("plan", plan)):
        if f and slug not in open(f).read():
            errors.append("the %s %s does not cite the spec (%s): spec, then board, then build"
                          % (label, f, slug))
    return errors


# ---------------------------------------------------------------- cli

def emit(obj, as_json, lines):
    if as_json:
        print(json.dumps(obj, ensure_ascii=False, indent=1))
    else:
        for line in lines:
            print(line)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("size")
    s.add_argument("--reqs", type=int, required=True)
    s.add_argument("--files", type=int, required=True)
    s.add_argument("--surfaces", type=int, default=1)
    s.add_argument("--unknowns", type=int, default=0)
    for f in ("contract", "outward", "irreversible", "cross-project", "new-domain"):
        s.add_argument("--" + f, action="store_true")
    s.add_argument("--json", action="store_true")
    q = sub.add_parser("questions")
    q.add_argument("spec")
    q.add_argument("--json", action="store_true")
    r = sub.add_parser("research")
    rs = r.add_subparsers(dest="rcmd", required=True)
    ri = rs.add_parser("init")
    ri.add_argument("dir")
    ri.add_argument("--tier", required=True, choices=list(TIERS))
    ri.add_argument("--question", required=True)
    ri.add_argument("--author", required=True, help="family/tier of the model that writes it")
    rp = rs.add_parser("plan")
    rp.add_argument("--tier", required=True, choices=list(TIERS))
    rp.add_argument("--json", action="store_true")
    rc = rs.add_parser("check")
    rc.add_argument("dir")
    rc.add_argument("--tier", choices=list(TIERS))
    rc.add_argument("--json", action="store_true")
    c = sub.add_parser("check")
    c.add_argument("spec")
    c.add_argument("--tier", choices=list(TIERS))
    c.add_argument("--json", action="store_true")
    g = sub.add_parser("gate")
    g.add_argument("spec")
    g.add_argument("--plan")
    g.add_argument("--board")
    a = p.parse_args(argv)

    if a.cmd == "size":
        out = size(a.reqs, a.files, a.surfaces, a.contract, a.outward, a.irreversible,
                   a.cross_project, a.new_domain, a.unknowns)
        res = out["research"]
        emit(out, a.json, [
            "size %s (score %d): %s" % (out["tier"], out["score"], "; ".join(out["why"])),
            "sections: " + ", ".join(out["sections"]),
            "research: %d scout(s), %d validator(s) of another family, %d sources read, %d primary"
            % (res["scouts"], res["validators"], res["sources"], res["primary"]),
            out["note"]])
        return 0
    if a.cmd == "questions":
        owner, errors, warns = questions(open(a.spec).read())
        emit({"owner": owner, "errors": errors, "warnings": warns}, a.json,
             ["owner batch: %d question(s)" % len(owner)]
             + ["  %s [%s] %s (default: %s)" % (o["id"], o["class"], o["question"], o["default"]) for o in owner]
             + ["FAIL " + e for e in errors] + ["warn " + w for w in warns])
        return 1 if errors else 0
    if a.cmd == "research":
        if a.rcmd == "init":
            print(research_init(a.dir, a.tier, a.question, a.author))
            return 0
        if a.rcmd == "plan":
            out = research_plan(a.tier)
            emit(out, a.json, ["research plan, size %s: minimums %s" % (a.tier, json.dumps(out["minimums"]))]
                 + ["  %d x %s (%s tier%s): %s" % (x["count"], x["role"], x["tier"],
                                                  ", " + x["family"] if "family" in x else "", x["does"])
                    for x in out["roles"]] + ["budget: " + out["budget"]])
            return 0
        errors, warns = research_check(a.dir, a.tier)
        emit({"errors": errors, "warnings": warns}, a.json,
             ["FAIL " + e for e in errors] + ["warn " + w for w in warns]
             + ([] if errors else ["PASS research " + a.dir]))
        return 1 if errors else 0
    if a.cmd == "check":
        errors, warns, owner = check(a.spec, a.tier)
        emit({"errors": errors, "warnings": warns, "owner": owner}, a.json,
             ["FAIL " + e for e in errors] + ["warn " + w for w in warns]
             + ([] if errors else ["PASS spec %s; owner batch: %d question(s)" % (a.spec, len(owner))]))
        return 1 if errors else 0
    if a.cmd == "gate":
        errors = gate(a.spec, a.plan, a.board)
        for e in errors:
            print("FAIL " + e)
        if not errors:
            print("PASS gate: spec complete%s%s; build may start"
                  % (", board cites it" if a.board else "", ", plan cites it" if a.plan else ""))
        return 1 if errors else 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
