#!/usr/bin/env python3
"""spec_judge.py: a judge of another model family reads a final-state spec cold.

`references/judge-rubric.md` is the doctrine and the prompt; the spec's shape is
`references/spec-template.md`. Standard library only. The judge answers one
question: can this spec be built without a builder asking anything? The council
(`consilium.py`) still answers whether the design is right; the two never replace
each other.

A spec is a directory: `spec.md` (the template's sections), `spec.json`
(`spec/1`: id, size, kind, author_family, status) and `judge/` (one
`judge/<round>.json` per round, `judge/1`, plus the judged text as
`judge/<round>.spec.md` so the next round can read the diff).

    check   SPEC_DIR [--models FILE] [--rubric FILE] [--glossary FILE]
            [--key-env NAME] [--endpoint URL] [--timeout S] [--import FILE]
            [--dry-run] [--task T] [--json]
            One round: round 1 reads the whole spec, round 2 and 3 read the spec,
            the previous round's questions and the diff. A third round runs only
            when exactly one blocking question stayed open after round 2. The
            verdict is computed here from the judge's answer, never taken from it.
            --import FILE brings in a judge/1 answer a subscription agent wrote
            (`prompt` prints what it must read), at no token cost.
    check   SPEC_DIR --verify [--rubric FILE] [--json]
            The gate (hook, CI, board): the latest round's verdict is `pass`,
            bound to the current content hash, and cross-family where the rubric
            or the size demands it.
    hash    SPEC_DIR    SHA-256 of spec.md without its `## Judge record` section.
    prompt  SPEC_DIR    The exact prompt the next round would send, for a
                        subscription judge.
    lint    SPEC_DIR    The mechanical automatic fails (sections, header fields,
                        enums, TBD, an empty section), with no model.
    find    ID [--root DIR]  The spec directory whose spec.json carries this id
                        (docs/specs/*/ and docs/plans/**/), for the CI gate.
    seeds   DIR [--min N]    Every seed spec under DIR is judged (or linted
                        with --lint-only); exit 0 when at least N of them are
                        caught (any verdict but pass). The weekly calibration.

Exit codes (check, check --verify):
  0  judged: `pass` (or `judged-degraded` where the rubric and size allow it)
  1  judged and not passing: pass-with-fixes, fail, degraded where not allowed,
     or the round limit reached (the spec stays draft)
  2  no verdict, or a stale one: spec.md changed after it was judged
  3  cannot run: no spec, a malformed record, no judge model, no key, a call error
"""
import argparse
import datetime
import difflib
import hashlib
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
try:
    import spend  # noqa: E402  (the shared spend ledger, scripts/spend.py)
except Exception:  # pragma: no cover - the ledger is optional for the gate
    spend = None

RUBRIC = SKILL / "references" / "judge-rubric.md"
MODELS = SKILL / "references" / "judge-models.json"
HOST_DIR = pathlib.Path(os.path.expanduser("~/.config/task-pipeline"))
DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1"

SECTIONS = ["Header", "Outcome", "Users", "Final behaviour", "Data and contracts", "Boundaries",
            "Acceptance", "Delivery order", "Waits and gates", "Estimate", "Question ledger",
            "Glossary", "Judge record"]
HEADER_FIELDS = ["id", "owner repositories", "size", "kind", "memory side", "supersedes", "status"]
SIZES = ("S", "M", "L")
KINDS = ("feature", "fix", "research", "release", "docs")
STATUSES = ("draft", "judged", "judged-degraded", "built", "observed", "superseded")
DIMENSIONS = ["clarity", "completeness", "testability", "finality", "consistency"]
MAX_ROUNDS = 3
TBD_RE = re.compile(r"\b(TBD|TODO|to be decided|to be defined|FIXME)\b|\?\?\?", re.I)
JUDGE_RE = re.compile(r"^## Judge record\b.*?(?=^## |\Z)", re.M | re.S)


class Stop(Exception):
    """Exit 3: the tool cannot run."""


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- the content

def strip_judge(text):
    return JUDGE_RE.sub("", text)


def content_hash(text):
    return hashlib.sha256(strip_judge(text).encode("utf-8")).hexdigest()


def load_spec(d):
    d = pathlib.Path(d)
    md, js = d / "spec.md", d / "spec.json"
    if d.is_file() and d.name == "spec.md":
        d, md, js = d.parent, d, d.parent / "spec.json"
    if not md.is_file():
        raise Stop(f"{md}: no spec.md")
    meta = {}
    if js.is_file():
        try:
            meta = json.loads(js.read_text(encoding="utf-8"))
        except ValueError as e:
            raise Stop(f"{js}: not JSON ({e})")
    return d, md.read_text(encoding="utf-8"), meta


def rounds(d):
    out = {}
    jd = pathlib.Path(d) / "judge"
    if jd.is_dir():
        for p in jd.glob("*.json"):
            if p.stem.isdigit():
                try:
                    out[int(p.stem)] = json.loads(p.read_text(encoding="utf-8"))
                except ValueError as e:
                    raise Stop(f"{p}: not JSON ({e})")
    return out


def sections(text):
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^## (.+?)\s*$", line)
        if m:
            cur = m.group(1).strip()
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def header(text):
    sec = sections(text).get("Header", "")
    rows = {}
    for line in sec.splitlines():
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0] and not set(cells[0]) <= set("-: "):
            rows[cells[0].lower()] = cells[1]
    return rows


def lint(text, meta):
    """The automatic fails a script can see. The judge sees the rest."""
    fails = []
    sec = sections(text)
    names = list(sec)
    missing = [s for s in SECTIONS if s not in sec]
    if missing:
        fails.append("missing section: " + ", ".join(missing))
    order = [s for s in names if s in SECTIONS]
    if order != [s for s in SECTIONS if s in order]:
        fails.append("sections out of the template's order")
    for s in SECTIONS:
        if s in sec and s != "Judge record" and not sec[s].strip():
            fails.append(f"empty section: {s} (write \"none\")")
    h = header(text)
    for f in HEADER_FIELDS:
        if not h.get(f):
            fails.append(f"header field missing: {f}")
    size = (h.get("size") or meta.get("size") or "").strip()
    if size and size not in SIZES:
        fails.append(f"size {size!r} is not S, M or L")
    kind = (h.get("kind") or meta.get("kind") or "").strip()
    if kind and kind not in KINDS:
        fails.append(f"kind {kind!r} is not one of {', '.join(KINDS)}")
    status = (h.get("status") or "").strip().strip("`").split()[0] if h.get("status") else ""
    if status and status not in STATUSES:
        fails.append(f"status {status!r} is not one of {', '.join(STATUSES)}")
    facts = re.findall(r"^(\d+)\. ", sec.get("Final behaviour", ""), re.M)
    acc = sec.get("Acceptance", "")
    unchecked = [n for n in facts if not re.search(r"\bFacts? (?:[\d, and]*\b)?%s\b" % n, acc)]
    if unchecked:
        fails.append("fact with no acceptance check: " + ", ".join(unchecked))
    body = strip_judge(text)
    for i, line in enumerate(body.splitlines(), 1):
        if TBD_RE.search(line):
            fails.append(f"open placeholder at line {i}: {line.strip()[:80]}")
            break
    if not meta.get("author_family"):
        fails.append("spec.json has no author_family")
    return fails


# ---------------------------------------------------------------- configuration

def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                v = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
            elif v.lower() in ("true", "false"):
                v = v.lower() == "true"
            else:
                v = v.strip("'\"")
            out[k.strip()] = v
    return out, text[m.end():]


def load_rubric(path=None):
    for p in (path, os.environ.get("TASK_PIPELINE_JUDGE_RUBRIC"), HOST_DIR / "judge-rubric.md", RUBRIC):
        if p and pathlib.Path(p).is_file():
            fm, body = front_matter(pathlib.Path(p).read_text(encoding="utf-8"))
            if fm.get("version") != "judge-rubric/1":
                raise Stop(f"{p}: front matter version is not judge-rubric/1")
            fm["_source"] = str(p)
            fm["_body"] = body
            extra = fm.get("extra_dimensions") or []
            fm["extra_dimensions"] = extra if isinstance(extra, list) else [extra]
            return fm
    raise Stop("no judge rubric found")


def load_models(path=None):
    for source, p in (("--models", path), ("$TASK_PIPELINE_JUDGE_MODELS", os.environ.get("TASK_PIPELINE_JUDGE_MODELS")),
                      ("host", HOST_DIR / "judge-models.json"), ("shipped", MODELS)):
        if p and pathlib.Path(p).is_file():
            cfg = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
            if cfg.get("schema") != "judge-models/1" or not isinstance(cfg.get("models"), list):
                raise Stop(f"{p}: not judge-models/1")
            cfg["_source"] = f"{source}: {p}"
            return cfg
    raise Stop("no judge-models file found")


def pick_judge(models, author_family):
    """The strongest (rank 1 first) entry of another family; else the strongest of the same, degraded."""
    usable = [m for m in models.get("models", [])
              if isinstance(m, dict) and m.get("model") and m.get("family") and "<" not in m["model"]]
    usable.sort(key=lambda m: int(m.get("rank", 99)))
    for m in usable:
        if m["family"] != author_family:
            return m, True
    return (usable[0], False) if usable else (None, False)


def find_glossary(spec_dir, path=None):
    cands = [path, os.environ.get("TASK_PIPELINE_GLOSSARY")]
    d = pathlib.Path(spec_dir).resolve()
    for parent in [d, *d.parents]:
        cands += [parent / "knowledge" / "glossary.md", parent / "docs" / "glossary.md"]
        if (parent / ".git").exists():
            break
    for p in cands:
        if p and pathlib.Path(p).is_file():
            return pathlib.Path(p)
    return None


# ---------------------------------------------------------------- the verdict

def compute_verdict(answer, rubric):
    """pass: no 0, no blocking question, no automatic fail. pass-with-fixes: no 0,
    every blocking question carries a fix, no automatic fail. Otherwise fail."""
    dims = DIMENSIONS + [d for d in rubric.get("extra_dimensions", []) if d]
    scores = answer.get("scores") or {}
    missing = [d for d in dims if not isinstance(scores.get(d), int) or not 0 <= scores[d] <= 2]
    if missing:
        return "fail", [f"score missing or out of 0..2: {', '.join(missing)}"]
    qs = answer.get("questions") or []
    blocking = [q for q in qs if isinstance(q, dict) and q.get("blocking")]
    auto = [a for a in (answer.get("auto_fail") or []) if a]
    if auto or any(scores[d] == 0 for d in dims):
        return "fail", []
    if not blocking:
        return "pass", []
    if all((q.get("fix") or "").strip() for q in blocking):
        return "pass-with-fixes", []
    return "fail", ["a blocking question has no fix"]


def allowed_degraded(rubric, size):
    return not rubric.get("require_cross_family") and size in ("S", "M")


def verify(spec_dir, rubric_path=None):
    """(code, message) for the gate."""
    d, text, meta = load_spec(spec_dir)
    rs = rounds(d)
    if not rs:
        return 2, "no judge verdict: run spec_judge.py check " + str(d)
    last = rs[max(rs)]
    for k in ("verdict", "content_sha256"):
        if k not in last:
            raise Stop(f"judge/{max(rs)}.json has no {k}")
    if last["content_sha256"] != content_hash(text):
        return 2, f"stale: spec.md changed after round {max(rs)} was judged"
    if last["verdict"] != "pass":
        return 1, f"round {max(rs)} verdict is {last['verdict']}"
    if last.get("cross_family") is False:
        rubric = load_rubric(rubric_path)
        size = meta.get("size") or header(text).get("size", "")
        if not allowed_degraded(rubric, size):
            why = "the rubric requires a judge of another family" if rubric.get("require_cross_family") \
                else f"a size {size} spec needs a judge of another family"
            return 1, f"judged-degraded does not satisfy the gate: {why}"
        return 0, f"judged-degraded (round {max(rs)}, one model family)"
    return 0, f"judged (round {max(rs)}, {last.get('model')}, {last.get('family')})"


# ---------------------------------------------------------------- the prompt

ANSWER_SCHEMA = (
    '{"questions": [{"q": "what a builder would have to ask", "blocking": true|false,'
    ' "fix": "the one-line change that answers it", "closes": "id of a previous question or empty"}],'
    ' "scores": {"clarity": 0-2, "completeness": 0-2, "testability": 0-2, "finality": 0-2,'
    ' "consistency": 0-2%s},'
    ' "auto_fail": ["each automatic fail, one line"],'
    ' "previous": [{"q": "a previous question", "closed": true|false}]}'
)


def build_prompt(d, text, meta, rubric, glossary, rs):
    extra = "".join(f', "{x}": 0-2' for x in rubric.get("extra_dimensions", []))
    parts = [rubric["_body"].strip(), "",
             "Answer with ONE JSON object and nothing else, in this shape:",
             ANSWER_SCHEMA % extra, ""]
    if rubric.get("extra_dimensions"):
        parts += ["Also score these dimensions of this organisation: "
                  + ", ".join(rubric["extra_dimensions"]) + ".", ""]
    parts += ["# Glossary", glossary.read_text(encoding="utf-8") if glossary else "none supplied", ""]
    if rs:
        prev_n = max(rs)
        prev = rs[prev_n]
        old = (d / "judge" / f"{prev_n}.spec.md")
        old_text = old.read_text(encoding="utf-8") if old.is_file() else ""
        diff = "".join(difflib.unified_diff(strip_judge(old_text).splitlines(True),
                                            strip_judge(text).splitlines(True),
                                            f"round-{prev_n}/spec.md", "now/spec.md"))
        parts += [f"# Round {prev_n + 1}",
                  "Say for every previous question whether the new spec closes it (field `previous`), "
                  "and whether the diff opened a new question.", "",
                  "## Previous questions",
                  json.dumps(prev.get("questions", []), ensure_ascii=False, indent=1), "",
                  "## Diff since the previous round", diff or "(no change)", ""]
    parts += ["# The spec", strip_judge(text)]
    return "\n".join(parts)


# ---------------------------------------------------------------- one round

def call(endpoint, key, model, prompt, timeout, max_tokens=8000):
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens, "usage": {"include": True}}
    req = urllib.request.Request(endpoint.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                                          "X-Title": "task-pipeline spec judge"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        raise Stop(f"judge call: http {e.code}: {e.read().decode('utf-8', 'replace')[:300]}")
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise Stop(f"judge call: {type(e).__name__}: {e}")
    msg = ((data.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    usage = data.get("usage") or {}
    usd, source = spend.cost_of(usage) if spend else (None, "unknown")
    return msg, {"cost_usd": usd, "cost_source": source, "seconds": round(time.time() - t0, 1),
                 "tokens_in": usage.get("prompt_tokens"), "tokens_out": usage.get("completion_tokens")}


def parse_json(text):
    text = (text or "").strip()
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    if m:
        text = m.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise Stop("the judge did not answer with JSON")
    try:
        return json.loads(text[start:end + 1])
    except ValueError as e:
        raise Stop(f"the judge's JSON does not parse: {e}")


def record_section(rs):
    lines = ["## Judge record", "",
             "| Round | Judge | Verdict | Scores | Questions | Cost |", "|---|---|---|---|---|---|"]
    for n in sorted(rs):
        r = rs[n]
        sc = ", ".join(f"{k} {v}" for k, v in (r.get("scores") or {}).items())
        qs = r.get("questions") or []
        b = sum(1 for q in qs if q.get("blocking"))
        cost = "subscription" if r.get("cost_usd") is None and r.get("route") == "subscription" else \
            ("unknown" if r.get("cost_usd") is None else f"USD {r['cost_usd']:.6f}")
        lines.append(f"| {n} | {r.get('model')} ({r.get('family')}; author family {r.get('author_family')}) "
                     f"| {r.get('verdict')} | {sc} | {b} blocking, {len(qs) - b} other | {cost} |")
    last = rs[max(rs)]
    lines += ["", f"Content SHA-256 without this section: `{last.get('content_sha256')}`. "
                  f"Rubric `{last.get('rubric')}`. Records: `judge/<round>.json`.", ""]
    return "\n".join(lines)


def write_record(md_path, text, rs):
    sec = record_section(rs)
    if JUDGE_RE.search(text):
        new = JUDGE_RE.sub(lambda _m: sec + "\n", text, count=1)
    else:
        new = text.rstrip("\n") + "\n\n" + sec
    md_path.write_text(new, encoding="utf-8")


def check(args):
    d, text, meta = load_spec(args.spec)
    if args.verify:
        code, msg = verify(d, args.rubric)
        out(args, {"code": code, "message": msg, "spec": str(d)})
        return code
    rubric = load_rubric(args.rubric)
    rs = rounds(d)
    n = (max(rs) + 1) if rs else 1
    if rs and rs[max(rs)].get("content_sha256") == content_hash(text) and rs[max(rs)].get("verdict") == "pass":
        out(args, {"code": 0, "message": f"already judged pass in round {max(rs)}; nothing to do"})
        return 0
    if n > MAX_ROUNDS:
        return escalate(args, d, rs, "the round limit (3) is reached")
    if n == 3:
        open_b = [q for q in rs[2].get("questions", []) if q.get("blocking")]
        if len(open_b) != 1:
            return escalate(args, d, rs, f"round 2 left {len(open_b)} blocking questions; "
                                         "a third round runs only for exactly one")
    author = meta.get("author_family") or ""
    mech = lint(text, meta)
    models = load_models(args.models)
    route, cost = "tokens", {}
    if args.import_file:
        answer = json.loads(pathlib.Path(args.import_file).read_text(encoding="utf-8"))
        judge = {"model": answer.get("model"), "family": answer.get("family")}
        if not judge["model"] or not judge["family"]:
            raise Stop("an imported answer must name its model and family")
        cross, route = judge["family"] != author, "subscription"
    else:
        judge, cross = pick_judge(models, author)
        if not judge:
            raise Stop(f"no usable judge model in {models['_source']} (placeholders are never called)")
        glossary = find_glossary(d, args.glossary)
        prompt = build_prompt(d, text, meta, rubric, glossary, rs)
        if args.dry_run:
            out(args, {"code": 0, "round": n, "judge": judge, "cross_family": cross, "prompt_chars": len(prompt),
                       "glossary": str(glossary) if glossary else None, "lint": mech})
            return 0
        key = os.environ.get(args.key_env)
        if not key:
            raise Stop(f"no key in ${args.key_env} (fill it through the host's secret door, never a file)")
        reply, cost = call(args.endpoint, key, judge["model"], prompt, args.timeout)
        answer = parse_json(reply)
        if spend:
            spend.record("tokens", judge["model"], cost.get("cost_usd"), cost.get("cost_source", "unknown"),
                         args.task, cost.get("tokens_in"), cost.get("tokens_out"), note=f"spec judge round {n}")
    answer.setdefault("auto_fail", [])
    answer["auto_fail"] = list(answer["auto_fail"]) + [f"lint: {m}" for m in mech]
    verdict, notes = compute_verdict(answer, rubric)
    size = meta.get("size") or header(text).get("size", "")
    if verdict == "pass":
        status = "judged" if cross else ("judged-degraded" if allowed_degraded(rubric, size) else "draft")
    else:
        status = "draft"
    rec = {"schema": "judge/1", "round": n, "model": judge["model"], "family": judge["family"],
           "author_family": author, "cross_family": cross, "rubric": rubric.get("version"),
           "rubric_source": rubric["_source"], "route": route, "verdict": verdict, "status": status,
           "scores": answer.get("scores"), "questions": answer.get("questions") or [],
           "previous": answer.get("previous") or [], "auto_fail": answer["auto_fail"], "notes": notes,
           "content_sha256": content_hash(text), "cost_usd": cost.get("cost_usd"),
           "cost_source": cost.get("cost_source"), "created": now()}
    jd = d / "judge"
    jd.mkdir(exist_ok=True)
    (jd / f"{n}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (jd / f"{n}.spec.md").write_text(strip_judge(text), encoding="utf-8")
    rs[n] = rec
    write_record(d / "spec.md", text, rs)
    if meta:
        meta["status"] = status
        (d / "spec.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    out(args, {"code": 0 if verdict == "pass" and status != "draft" else 1, "round": n, "verdict": verdict,
               "status": status, "judge": f"{judge['model']} ({judge['family']})", "cross_family": cross})
    if verdict != "pass" and n == MAX_ROUNDS:
        return escalate(args, d, rs, "round 3 did not pass")
    return 0 if verdict == "pass" and status != "draft" else 1


def escalate(args, d, rs, why):
    """The spec stays draft; the open questions go to the owning project's coordinator as a task."""
    last = rs[max(rs)] if rs else {}
    openq = [q for q in last.get("questions", []) if q.get("blocking")]
    body = ["# Спека не прошла судью", "", f"Spec: `{d}`. Why: {why}.", "",
            "Open blocking questions for the owning project's coordinator:", ""]
    body += [f"- {q.get('q')} (fix: {q.get('fix') or 'none given'})" for q in openq] or ["- none recorded"]
    p = d / "judge" / "escalation.md"
    p.parent.mkdir(exist_ok=True)
    p.write_text("\n".join(body) + "\n", encoding="utf-8")
    out(args, {"code": 1, "message": f"stays draft: {why}; file {p} as a task «спека не прошла судью» "
                                     "for the owning project's coordinator"})
    return 1


def out(args, obj):
    if getattr(args, "json", False):
        print(json.dumps(obj, ensure_ascii=False))
    else:
        print("spec_judge: " + "; ".join(f"{k}={v}" for k, v in obj.items() if k != "prompt"))


# ---------------------------------------------------------------- other commands

def find(spec_id, root="."):
    root = pathlib.Path(root)
    pats = ["docs/specs/*/spec.json", "docs/plans/**/spec.json"]
    hits = []
    for pat in pats:
        for p in root.glob(pat):
            try:
                if json.loads(p.read_text(encoding="utf-8")).get("id") == spec_id:
                    hits.append(p.parent)
            except ValueError:
                continue
    return sorted(set(hits))


def seeds(args):
    base = pathlib.Path(args.dir)
    # A seed is a spec with its known defect beside it; the control has none.
    dirs = sorted(p.parent for p in base.glob("*/spec.md") if (p.parent / "defect.json").is_file())
    caught = 0
    for s in dirs:
        _, text, meta = load_spec(s)
        if args.lint_only:
            hit = bool(lint(text, meta))
        else:
            work = pathlib.Path(args.work or (base / ".runs")) / s.name
            work.mkdir(parents=True, exist_ok=True)
            for f in ("spec.md", "spec.json"):
                if (s / f).is_file():
                    (work / f).write_text((s / f).read_text(encoding="utf-8"), encoding="utf-8")
            ns = argparse.Namespace(spec=str(work), verify=False, rubric=args.rubric, models=args.models,
                                    glossary=None, key_env=args.key_env, endpoint=args.endpoint,
                                    timeout=args.timeout, import_file=None, dry_run=False, task="judge-seeds",
                                    json=False)
            hit = check(ns) != 0
        caught += hit
        print(f"{'caught' if hit else 'MISSED'}  {s.name}")
    print(f"seeds: {caught} of {len(dirs)} caught (need {args.min})")
    return 0 if caught >= args.min else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("spec")
    c.add_argument("--verify", action="store_true")
    c.add_argument("--rubric")
    c.add_argument("--models")
    c.add_argument("--glossary")
    c.add_argument("--key-env", default="OPENROUTER_API_KEY")
    c.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    c.add_argument("--timeout", type=float, default=300)
    c.add_argument("--import", dest="import_file")
    c.add_argument("--dry-run", action="store_true")
    c.add_argument("--task")
    c.add_argument("--json", action="store_true")
    for name in ("hash", "prompt", "lint"):
        p = sub.add_parser(name)
        p.add_argument("spec")
        p.add_argument("--rubric")
        p.add_argument("--glossary")
    f = sub.add_parser("find")
    f.add_argument("id")
    f.add_argument("--root", default=".")
    s = sub.add_parser("seeds")
    s.add_argument("dir")
    s.add_argument("--min", type=int, default=9)
    s.add_argument("--lint-only", action="store_true")
    s.add_argument("--work")
    s.add_argument("--rubric")
    s.add_argument("--models")
    s.add_argument("--key-env", default="OPENROUTER_API_KEY")
    s.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    s.add_argument("--timeout", type=float, default=300)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "check":
            return check(a)
        if a.cmd == "hash":
            _, text, _ = load_spec(a.spec)
            print(content_hash(text))
            return 0
        if a.cmd == "prompt":
            d, text, meta = load_spec(a.spec)
            print(build_prompt(d, text, meta, load_rubric(a.rubric), find_glossary(d, a.glossary), rounds(d)))
            return 0
        if a.cmd == "lint":
            _, text, meta = load_spec(a.spec)
            fails = lint(text, meta)
            for x in fails:
                print("auto-fail: " + x)
            print("PASS: lint" if not fails else f"FAIL: {len(fails)} automatic fails")
            return 0 if not fails else 1
        if a.cmd == "find":
            hits = find(a.id, a.root)
            if len(hits) != 1:
                print(f"spec_judge: {len(hits)} spec directories carry id {a.id!r}", file=sys.stderr)
                return 3
            print(hits[0])
            return 0
        if a.cmd == "seeds":
            return seeds(a)
    except Stop as e:
        print(f"spec_judge: cannot run: {e}", file=sys.stderr)
        return 3
    return 3


if __name__ == "__main__":
    sys.exit(main())
