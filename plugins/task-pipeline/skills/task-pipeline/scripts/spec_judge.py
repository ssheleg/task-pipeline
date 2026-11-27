#!/usr/bin/env python3
"""spec_judge.py: a spec is judged cold by a model of another family before anything is built.

The doctrine is `references/spec-protocol.md` -> *The clarity judge*; the template is
`references/spec-template.md`, the prompt and the dimensions `references/judge-rubric.md`
(`judge-rubric/1`), the judges `references/judge-models.json` (`judge-models/1`).
Standard library only. One verb calls a model per round; every other verb is offline.

    init      SPEC_DIR --id ID --author-family F [--size S|M|L] [--kind K] [--owner O] [--side S]
              A new spec directory: spec.md from the template, spec.json (`spec/1`).
    check     SPEC_DIR [--verify] [--models FILE] [--rubric FILE] [--glossary FILE]
              [--endpoint URL] [--key-env NAME] [--timeout S] [--new-cycle --reason TEXT]
              [--require-cross-family] [--dry-run] [--json]
              Judge the spec: one round, one call, never retried. Round 1 reads the whole
              spec; round 2 and 3 also get the previous round's questions and the diff.
              A content already judged `pass` is not judged again (no call, no cost).
              With --verify nothing is called: the verdict on file must match the content.
    validate  SPEC_DIR --model ID --family F [--endpoint URL] [--key-env NAME]
              One design validator of another family (size M owes one, L two of two
              families), recorded in review/validators/. The council is consilium.py
              with `--out SPEC_DIR/review/council`.
    hash      SPEC_DIR    The content hash: SHA-256 of spec.md without `## Judge record`.
    gate      --pr-body FILE [--repo DIR] [--require-cross-family]
              CI: the `Spec: <spec id>@<commit>` trailer, that spec at that commit, verified.
    calibrate [--seeds DIR] [--min N] [--out FILE] [model flags]
              The seeded bad specs (`tests/judge-seeds/`): how many the judge catches.

Exit codes (every verb): 0 pass (or `judged-degraded` where allowed), 1 not passed,
2 unreadable spec or rubric, or a usage error, 3 no judge model available.
"""
import argparse
import datetime
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import spend  # noqa: E402  (the shared spend ledger)

PASS, NOT_PASSED, UNREADABLE, NO_MODEL = 0, 1, 2, 3
CORE = ("clarity", "completeness", "testability", "finality", "consistency")
SIZES = ("S", "M", "L")
KINDS = ("feature", "fix", "research", "release", "docs")
STATUSES = ("draft", "judged", "judged-degraded", "built", "observed", "superseded")
VERDICTS = ("pass", "pass-with-fixes", "fail")
AUTO_FAILS = ("undefined-term", "tbd", "open-decision", "fact-without-check",
              "missing-user-kind", "missing-memory-side", "unnamed-owner")
MAX_ROUNDS = 3
JUDGE_HEADING = "judge record"
DEFAULT_ENDPOINT = os.environ.get("SPEC_JUDGE_ENDPOINT", "https://openrouter.ai/api/v1")
TRAILER = re.compile(r"^\s*Spec:\s*([A-Za-z0-9][A-Za-z0-9._:-]*)@([0-9a-fA-F]{7,40})\s*$", re.M)
PLACEHOLDER = re.compile(r"^<.*>$")


class Refusal(Exception):
    """A refusal with its exit code; the message names the remedy."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- content hash

def _fence_mask(lines):
    """True for each line inside a fenced code block (``` or ~~~)."""
    inside, marker, out = False, None, []
    for line in lines:
        m = re.match(r"^\s*(`{3,}|~{3,})", line)
        if m and (not inside or m.group(1)[0] == marker):
            out.append(True)
            inside, marker = (not inside), m.group(1)[0]
            continue
        out.append(inside)
    return out


def _heading(line):
    m = re.match(r"^##\s+(.+?)\s*#*\s*$", line)
    return m.group(1).strip().lower() if m and not line.startswith("###") else None


def strip_judge_record(text):
    """spec.md without its `## Judge record` section.

    The heading counts only at the start of a line and outside a code fence: a spec that
    MENTIONS `## Judge record` in its prose (S0's fact 7 does) must not lose everything
    after the mention, which is what a first-occurrence search does."""
    lines = text.splitlines()
    fenced = _fence_mask(lines)
    keep, skipping = [], False
    for line, inside in zip(lines, fenced):
        h = None if inside else _heading(line)
        if h is not None:
            skipping = h == JUDGE_HEADING or h.startswith(JUDGE_HEADING + " ")
        if not skipping:
            keep.append(line)
    return "\n".join(keep).rstrip() + "\n"


def content_hash(text):
    return hashlib.sha256(strip_judge_record(text).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- the spec directory

def load_spec(spec_dir):
    if os.path.isfile(spec_dir) and os.path.basename(spec_dir) == "spec.md":
        spec_dir = os.path.dirname(spec_dir) or "."
    md, js = os.path.join(spec_dir, "spec.md"), os.path.join(spec_dir, "spec.json")
    if not os.path.isfile(md):
        raise Refusal(UNREADABLE, "no spec.md in %s: start one with `spec_judge.py init`" % spec_dir)
    if not os.path.isfile(js):
        raise Refusal(UNREADABLE, "no spec.json (spec/1) in %s: it names the author's family" % spec_dir)
    try:
        text = open(md, encoding="utf-8").read()
        meta = json.load(open(js, encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise Refusal(UNREADABLE, "the spec cannot be read (%s)" % e)
    if not isinstance(meta, dict) or not str(meta.get("author_family") or "").strip():
        raise Refusal(UNREADABLE, "spec.json has no `author_family`: the judge's family cannot be chosen")
    size = str(meta.get("size") or header_field(text, "size") or "").upper()[:1]
    if size not in SIZES:
        raise Refusal(UNREADABLE, "the spec names no size S, M or L (spec.json `size` or the header)")
    meta["size"] = size
    return spec_dir, text, meta


def header_field(text, name):
    """A value from the `## Header` table (`| field | value |`)."""
    body = section(text, "header")
    for line in (body or "").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0].strip("`*").lower() == name.lower():
            return cells[1].strip()
    return None


def section(text, name):
    lines = text.splitlines()
    fenced = _fence_mask(lines)
    cur, buf, out = None, [], {}
    for line, inside in zip(lines, fenced):
        h = None if inside else _heading(line)
        if h is not None:
            if cur is not None:
                out.setdefault(cur, "\n".join(buf))
            cur, buf = h, []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out.setdefault(cur, "\n".join(buf))
    return out.get(name.lower())


def rounds(spec_dir):
    d = os.path.join(spec_dir, "judge")
    out = []
    if not os.path.isdir(d):
        return out
    for fn in os.listdir(d):
        m = re.match(r"^round-(\d+)\.json$", fn)
        if not m:
            continue
        try:
            rec = json.load(open(os.path.join(d, fn), encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(rec, dict):
            rec["round"] = int(m.group(1))
            out.append(rec)
    return sorted(out, key=lambda r: r["round"])


def cycle(all_rounds):
    """The rounds since the last pass or the last `--new-cycle`: what the limit of three counts."""
    cur = []
    for r in all_rounds:
        if r.get("new_cycle"):
            cur = []
        cur.append(r)
        if r.get("verdict") == "pass":
            cur = []
    return cur


# ---------------------------------------------------------------- rubric and judges

def _front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return None, text
    data, key = {}, None
    for raw in m.group(1).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        item = re.match(r"^\s+-\s+(.*)$", raw)
        if item and key:
            if not isinstance(data.get(key), list):
                data[key] = []
            data[key].append(_scalar(item.group(1)))
            continue
        kv = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", raw)
        if not kv:
            return None, text
        key, val = kv.group(1), kv.group(2).strip()
        if val.startswith("[") and val.endswith("]"):
            data[key] = [_scalar(v) for v in val[1:-1].split(",") if v.strip()]
        else:
            data[key] = _scalar(val) if val else []
    return data, m.group(2)


def _scalar(v):
    v = v.strip().strip('"').strip("'")
    return {"true": True, "false": False}.get(v.lower(), v)


def rubric_path(cli, project):
    for p in (cli, os.environ.get("TASK_PIPELINE_JUDGE_RUBRIC"),
              os.path.join(project, ".task-pipeline", "judge-rubric.md") if project else None,
              os.path.expanduser("~/.config/task-pipeline/judge-rubric.md"),
              os.path.join(SKILL, "references", "judge-rubric.md")):
        if p and os.path.isfile(p):
            return p
    raise Refusal(UNREADABLE, "no judge rubric found (the shipped references/judge-rubric.md is missing)")


def load_rubric(path):
    try:
        data, body = _front_matter(open(path, encoding="utf-8").read())
    except OSError as e:
        raise Refusal(UNREADABLE, "the rubric %s cannot be read (%s)" % (path, e))
    if data is None or data.get("schema") != "judge-rubric/1":
        raise Refusal(UNREADABLE, "the rubric %s has no `schema: judge-rubric/1` front matter" % path)
    dims = [str(d) for d in (data.get("dimensions") or [])]
    missing = [d for d in CORE if d not in dims]
    if missing:
        raise Refusal(UNREADABLE, "the rubric %s removes core dimension(s) %s: an organisation adds "
                      "dimensions under `extra_dimensions`, it never removes the core five"
                      % (path, ", ".join(missing)))
    extra = [str(d) for d in (data.get("extra_dimensions") or []) if str(d) not in CORE]
    return {"path": path, "version": str(data.get("version") or "judge-rubric/1"),
            "dimensions": list(CORE) + extra, "extra": extra,
            "require_cross_family": data.get("require_cross_family") is True,
            "prompt": body.strip()}


def models_path(cli):
    for p in (cli, os.environ.get("TASK_PIPELINE_JUDGE_MODELS"),
              os.path.expanduser("~/.config/task-pipeline/judge-models.json"),
              os.path.join(SKILL, "references", "judge-models.json")):
        if p and os.path.isfile(p):
            return p
    return None


def load_models(path):
    if not path:
        return [], None
    try:
        data = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise Refusal(UNREADABLE, "the judge list %s cannot be read (%s)" % (path, e))
    if not isinstance(data, dict) or data.get("schema") != "judge-models/1":
        raise Refusal(UNREADABLE, "the judge list %s is not `judge-models/1`" % path)
    out = []
    for m in data.get("models") or []:
        if not isinstance(m, dict) or not m.get("model") or not m.get("family"):
            continue
        if PLACEHOLDER.match(str(m["model"]).strip()):
            continue  # a role, not a model: the shipped file names roles only
        try:
            rank = float(m.get("rank", 0))
        except (TypeError, ValueError):
            rank = 0.0
        out.append({"model": str(m["model"]), "family": str(m["family"]).lower(), "rank": rank,
                    "endpoint": m.get("endpoint"), "key_env": m.get("key_env"),
                    "max_tokens": int(m.get("max_tokens") or 8000)})
    return sorted(out, key=lambda m: -m["rank"]), data.get("endpoint")


def pick_judge(models, author_family):
    """(judge, cross_family). The highest-ranked of another family; else the author's own."""
    author = author_family.lower()
    other = [m for m in models if m["family"] != author]
    if other:
        return other[0], True
    if models:
        return models[0], False
    return None, False


def degraded_allowed(size, rubric, require_cross_family):
    return size in ("S", "M") and not (rubric["require_cross_family"] or require_cross_family)


# ---------------------------------------------------------------- the prompt and the verdict

OUTPUT_SHAPE = """Answer with ONE JSON object and nothing else:
{"questions": [{"id": "Q1", "text": "the question a builder would have to ask", "blocking": true,
                "fix": "one line that closes it"}],
 "previous": [{"id": "Q1", "state": "closed"}],
 "scores": {%s},
 "auto_fail": [{"kind": "one of %s", "where": "section or line", "text": "what is wrong"}],
 "summary": "one sentence"}
Scores are integers 0, 1 or 2. `previous` answers every question of the previous round
(closed or open); leave it empty in round 1."""


def build_prompt(rubric, spec_text, glossary, prev=None, diff=None):
    scores = ", ".join('"%s": 0' % d for d in rubric["dimensions"])
    parts = [rubric["prompt"], "", OUTPUT_SHAPE % (scores, ", ".join(AUTO_FAILS))]
    if glossary:
        parts += ["", "=== CANON GLOSSARY ===", glossary.strip()]
    if prev is not None:
        parts += ["", "=== PREVIOUS ROUND QUESTIONS ===",
                  json.dumps(prev.get("questions") or [], ensure_ascii=False, indent=1),
                  "", "=== DIFF SINCE THE PREVIOUS ROUND ===", diff or "(no textual change)"]
    parts += ["", "=== SPEC ===", strip_judge_record(spec_text)]
    return "\n".join(parts)


def parse_reply(text):
    if not isinstance(text, str):
        return None
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    start, end = t.find("{"), t.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        data = json.loads(t[start:end + 1])
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def decide(reply, dimensions, prev=None):
    """The verdict is computed here from what the judge listed, never taken from its words."""
    scores, problems = {}, []
    raw = reply.get("scores") if isinstance(reply.get("scores"), dict) else {}
    for d in dimensions:
        v = raw.get(d)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or int(v) != v or not 0 <= v <= 2:
            problems.append("score `%s` missing or not 0, 1 or 2" % d)
            v = 0
        scores[d] = int(v)
    questions = [q for q in reply.get("questions") or [] if isinstance(q, dict) and q.get("text")]
    auto = [a for a in reply.get("auto_fail") or [] if isinstance(a, dict) and a.get("kind")]
    reopened = []
    if prev:
        state = {str(p.get("id")): str(p.get("state", "")).lower()
                 for p in reply.get("previous") or [] if isinstance(p, dict)}
        for q in prev.get("questions") or []:
            if q.get("blocking") and state.get(str(q.get("id"))) != "closed":
                reopened.append(dict(q, still_open=True))
    blocking = [q for q in questions if q.get("blocking")] + reopened
    if problems or any(v == 0 for v in scores.values()) or auto:
        verdict = "fail"
    elif blocking:
        verdict = "pass-with-fixes" if all(str(q.get("fix") or "").strip() for q in blocking) else "fail"
    else:
        verdict = "pass"
    return {"verdict": verdict, "scores": scores, "questions": questions, "still_open": reopened,
            "auto_fail": auto, "blocking": len(blocking), "problems": problems,
            "summary": str(reply.get("summary") or "")[:400]}


def call_model(endpoint, key, model, prompt, timeout, max_tokens):
    body = {"model": model, "temperature": 0, "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}], "usage": {"include": True}}
    req = urllib.request.Request(endpoint.rstrip("/") + "/chat/completions",
                                 data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer " + key,
                                          "X-Title": "task-pipeline spec judge"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return {"error": "the endpoint answered HTTP %d" % e.code, "seconds": round(time.time() - t0, 1)}
    except (urllib.error.URLError, OSError, ValueError) as e:
        return {"error": "the endpoint failed (%s)" % type(e).__name__, "seconds": round(time.time() - t0, 1)}
    choice = (data.get("choices") or [{}])[0] if isinstance(data, dict) else {}
    usage = data.get("usage") if isinstance(data, dict) else None
    usd, source = spend.cost_of(usage)
    return {"text": ((choice or {}).get("message") or {}).get("content"),
            "finish_reason": (choice or {}).get("finish_reason"),
            "generation_id": data.get("id") if isinstance(data, dict) else None,
            "served_by": data.get("model") if isinstance(data, dict) else None,
            "usage": usage, "cost_usd": usd, "cost_source": source,
            "seconds": round(time.time() - t0, 1)}


# ---------------------------------------------------------------- design review on file (fact 6)

def design_review(spec_dir, size, author_family):
    """[] when the size's design review is on file, else what is owed."""
    if size == "S":
        return []
    author = author_family.lower()
    fams = set()
    vd = os.path.join(spec_dir, "review", "validators")
    for fn in sorted(os.listdir(vd)) if os.path.isdir(vd) else []:
        if not fn.endswith(".json"):
            continue
        try:
            rec = json.load(open(os.path.join(vd, fn), encoding="utf-8"))
        except (OSError, ValueError):
            continue
        fam = str((rec or {}).get("family") or "").lower()
        if fam and fam != author and (rec or {}).get("verdict") in ("agree", "partial", "disagree"):
            fams.add(fam)
    owed = []
    need = 1 if size == "M" else 2
    if len(fams) < need:
        owed.append("size %s owes %d design validator verdict(s) of %s other than the author's (%s); "
                    "on file: %d. Run `spec_judge.py validate`"
                    % (size, need, "a family" if need == 1 else "two families", author, len(fams)))
    council = os.path.join(spec_dir, "review", "council", "judge.json")
    ruling = None
    try:
        ruling = (json.load(open(council, encoding="utf-8")) or {}).get("ruling")
    except (OSError, ValueError):
        pass
    if not ruling:
        owed.append("size %s owes a council ruling on file (review/council/judge.json): "
                    "`consilium.py review --out %s`" % (size, os.path.join(spec_dir, "review", "council")))
    return owed


# ---------------------------------------------------------------- verify

def verify(spec_dir, rubric, require_cross_family=False):
    """(code, status, reasons). Reads files only."""
    spec_dir, text, meta = load_spec(spec_dir)
    h = content_hash(text)
    matching = [r for r in rounds(spec_dir) if r.get("spec_sha256") == h and r.get("verdict") == "pass"]
    if not matching:
        last = (rounds(spec_dir) or [None])[-1]
        why = "no judge round on file" if last is None else (
            "the content changed since round %d (its hash differs): the spec is `draft` again"
            % last["round"] if last.get("spec_sha256") != h else
            "round %d gave `%s`" % (last["round"], last.get("verdict")))
        return NOT_PASSED, "draft", [why + "; run `spec_judge.py check %s`" % spec_dir]
    best = matching[-1]
    if best.get("cross_family") is False:
        if not degraded_allowed(meta["size"], rubric, require_cross_family):
            reason = ("size L needs a judge of another family (a second provider)" if meta["size"] == "L"
                      else "this estate requires a judge of another family (`require_cross_family`)")
            return NOT_PASSED, "draft", ["round %d was judged by the author's own family: %s"
                                         % (best["round"], reason)]
        status = "judged-degraded"
    else:
        status = "judged"
    owed = design_review(spec_dir, meta["size"], meta["author_family"])
    if owed:
        return NOT_PASSED, "draft", owed
    return PASS, status, ["round %d: %s by %s (%s), content %s" % (
        best["round"], status, best.get("model"), best.get("family"), h[:12])]


def write_status(spec_dir, text, meta, status, all_rounds):
    meta = dict(meta)
    meta["schema"] = meta.get("schema") or "spec/1"
    meta["content_sha256"] = content_hash(text)
    meta["status"] = status
    meta["judge"] = [{k: r.get(k) for k in ("round", "model", "family", "rubric", "verdict", "scores",
                                            "questions", "cost_usd", "generation_id", "at")}
                     for r in all_rounds]
    with open(os.path.join(spec_dir, "spec.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def append_record(spec_dir, text, all_rounds, model_note):
    """Rewrite `## Judge record` from the rounds on file. The hash never sees this section."""
    rows = ["| Round | Judge | Verdict | Scores | Questions | Cost |", "|---|---|---|---|---|---|"]
    for r in all_rounds:
        sc = ", ".join("%s %s" % (k, v) for k, v in (r.get("scores") or {}).items())
        qs = r.get("questions") or []
        b = sum(1 for q in qs if q.get("blocking"))
        cost = "USD %.6f" % r["cost_usd"] if isinstance(r.get("cost_usd"), (int, float)) else "unknown"
        rows.append("| %d | %s (%s; author family %s) | %s | %s | %d blocking, %d other | %s |" % (
            r["round"], r.get("model"), r.get("family"), r.get("author_family"), r.get("verdict"),
            sc, b, len(qs) - b, cost))
    body = strip_judge_record(text).rstrip() + "\n\n## Judge record\n\n" + "\n".join(rows) + "\n\n" + \
        "Content SHA-256 without this section: `%s`. Records: %s. %s\n" % (
            content_hash(text), ", ".join("[round %d](judge/round-%d.json)" % (r["round"], r["round"])
                                         for r in all_rounds), model_note)
    with open(os.path.join(spec_dir, "spec.md"), "w", encoding="utf-8") as fh:
        fh.write(body)
    return body


# ---------------------------------------------------------------- check

def check(a):
    project = a.project or os.getcwd()
    rubric = load_rubric(rubric_path(a.rubric, project))
    if a.verify:
        return verify(a.spec_dir, rubric, a.require_cross_family)
    spec_dir, text, meta = load_spec(a.spec_dir)
    h = content_hash(text)
    all_rounds = rounds(spec_dir)
    if any(r.get("spec_sha256") == h and r.get("verdict") == "pass" for r in all_rounds):
        code, status, reasons = verify(spec_dir, rubric, a.require_cross_family)
        write_status(spec_dir, text, meta, status, all_rounds)
        return code, status, ["already judged `pass` for this content: no call"] + reasons
    cur = cycle(all_rounds)
    escalation = os.path.join(spec_dir, "judge", "escalation.json")
    if a.new_cycle:
        if not (a.reason or "").strip():
            raise Refusal(UNREADABLE, "--new-cycle needs --reason: who decided to judge again, and why")
        cur = []
    elif os.path.isfile(escalation) and cur:
        return NOT_PASSED, "draft", ["the judge's rounds are spent (%s): the coordinator decides; "
                                     "judge again only with --new-cycle --reason" % escalation]
    n_in_cycle = len(cur) + 1
    prev = cur[-1] if cur else None
    if n_in_cycle == MAX_ROUNDS and prev and prev.get("blocking", 0) != 1:
        return _escalate(spec_dir, meta, cur, "round 2 left %d blocking question(s); a third round is "
                         "only for one" % prev.get("blocking", 0))
    models, file_endpoint = load_models(models_path(a.models))
    judge, cross = pick_judge(models, meta["author_family"])
    if judge is None:
        raise Refusal(NO_MODEL, "no judge model available: write ~/.config/task-pipeline/judge-models.json "
                      "(`judge-models/1`, the shipped references/judge-models.json names the roles) "
                      "or pass --models")
    if not cross and not degraded_allowed(meta["size"], rubric, a.require_cross_family):
        raise Refusal(NO_MODEL, "every judge on the list is of the author's family (%s), and %s: add a "
                      "model of another family" % (meta["author_family"],
                                                   "size L needs one" if meta["size"] == "L"
                                                   else "this estate requires one"))
    glossary = ""
    gpath = a.glossary or os.environ.get("TASK_PIPELINE_GLOSSARY")
    if gpath:
        try:
            glossary = open(gpath, encoding="utf-8").read()
        except OSError as e:
            raise Refusal(UNREADABLE, "the glossary %s cannot be read (%s)" % (gpath, e))
    diff = None
    if prev is not None:
        snap = os.path.join(spec_dir, "judge", "round-%d.md" % prev["round"])
        old = open(snap, encoding="utf-8").read() if os.path.isfile(snap) else ""
        diff = "".join(difflib.unified_diff(old.splitlines(True), strip_judge_record(text).splitlines(True),
                                            "round-%d" % prev["round"], "now"))
    prompt = build_prompt(rubric, text, glossary, prev, diff)
    if a.dry_run:
        print(prompt)
        return PASS, meta.get("status") or "draft", ["dry run: judge %s (%s), nothing called"
                                                     % (judge["model"], judge["family"])]
    endpoint = a.endpoint or judge.get("endpoint") or file_endpoint or DEFAULT_ENDPOINT
    key_env = a.key_env or judge.get("key_env") or "OPENROUTER_API_KEY"
    key = os.environ.get(key_env, "")
    if not key:
        raise Refusal(NO_MODEL, "the key variable %s is empty: run under the host's secret runner "
                      "(Observatory: use_secret.py run)" % key_env)
    res = call_model(endpoint, key, judge["model"], prompt, a.timeout, judge["max_tokens"])
    spend.record("spec.judge", judge["model"], res.get("cost_usd"), res.get("cost_source", "unknown"),
                 meta.get("id"), (res.get("usage") or {}).get("prompt_tokens"),
                 (res.get("usage") or {}).get("completion_tokens"), res.get("served_by"),
                 note=res.get("generation_id"))
    if res.get("error"):
        return NOT_PASSED, "draft", ["the judge call failed (%s): no verdict recorded, never retried"
                                     % res["error"]]
    reply = parse_reply(res.get("text"))
    if reply is None:
        return NOT_PASSED, "draft", ["the judge answered no JSON object (finish: %s): no verdict recorded"
                                     % res.get("finish_reason")]
    d = decide(reply, rubric["dimensions"], prev)
    number = (all_rounds[-1]["round"] if all_rounds else 0) + 1
    rec = {"schema": "judge-round/1", "round": number, "cycle_round": n_in_cycle,
           "model": judge["model"], "family": judge["family"], "author_family": meta["author_family"],
           "cross_family": cross, "rubric": rubric["version"], "rubric_sha256":
           hashlib.sha256(open(rubric["path"], "rb").read()).hexdigest(),
           "verdict": d["verdict"], "scores": d["scores"], "questions": d["questions"],
           "still_open": d["still_open"], "auto_fail": d["auto_fail"], "blocking": d["blocking"],
           "problems": d["problems"], "summary": d["summary"], "cost_usd": res.get("cost_usd"),
           "cost_source": res.get("cost_source"), "generation_id": res.get("generation_id"),
           "served_by": res.get("served_by"), "spec_sha256": h,
           "glossary_sha256": hashlib.sha256(glossary.encode()).hexdigest() if glossary else None,
           "seconds": res.get("seconds"), "at": now()}
    if a.new_cycle:
        rec["new_cycle"] = {"reason": a.reason.strip(), "at": now()}
    jd = os.path.join(spec_dir, "judge")
    os.makedirs(jd, exist_ok=True)
    with open(os.path.join(jd, "round-%d.json" % number), "w", encoding="utf-8") as fh:
        json.dump(rec, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    with open(os.path.join(jd, "round-%d.md" % number), "w", encoding="utf-8") as fh:
        fh.write(strip_judge_record(text))
    all_rounds = rounds(spec_dir)
    note = "Rubric `%s`; judge chosen from %s." % (rubric["version"], models_path(a.models) or "the list")
    text = append_record(spec_dir, text, all_rounds, note)
    if d["verdict"] == "pass":
        if os.path.isfile(escalation):
            os.remove(escalation)
        code, status, reasons = verify(spec_dir, rubric, a.require_cross_family)
        write_status(spec_dir, text, meta, status, all_rounds)
        return code, status, ["round %d: pass" % number] + reasons
    write_status(spec_dir, text, meta, "draft", all_rounds)
    lines = ["round %d: %s (%d blocking)" % (number, d["verdict"], d["blocking"])] + [
        "  %s %s%s" % (q.get("id", "?"), "[blocking] " if q.get("blocking") else "", q.get("text"))
        for q in d["questions"] + d["still_open"]] + [
        "  auto-fail %s: %s" % (x.get("kind"), x.get("text", "")) for x in d["auto_fail"]]
    if n_in_cycle >= MAX_ROUNDS or (n_in_cycle == 2 and d["blocking"] != 1):
        code, status, more = _escalate(spec_dir, meta, cycle(all_rounds),
                                       "round %d did not pass" % n_in_cycle)
        return code, status, lines + more
    return NOT_PASSED, "draft", lines + ["revise the spec, then run check again (round %d of at most %d)"
                                         % (n_in_cycle + 1, MAX_ROUNDS)]


def _escalate(spec_dir, meta, cur, why):
    open_q = []
    for r in cur[-1:]:
        open_q = [q for q in (r.get("questions") or []) + (r.get("still_open") or []) if q.get("blocking")]
    task = {"schema": "judge-escalation/1", "at": now(), "spec": meta.get("id"), "path": spec_dir,
            "owner": meta.get("owner"), "title": "спека не прошла судью: %s" % (meta.get("id") or spec_dir),
            "why": why, "open_questions": open_q, "rounds": [r["round"] for r in cur],
            "file_with": "fabric_task_create (title and open_questions) for the coordinator of the "
                         "owning project; nothing is built until it passes"}
    os.makedirs(os.path.join(spec_dir, "judge"), exist_ok=True)
    with open(os.path.join(spec_dir, "judge", "escalation.json"), "w", encoding="utf-8") as fh:
        json.dump(task, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    return NOT_PASSED, "draft", ["%s: the spec stays `draft`; file the task in judge/escalation.json "
                                 "with the coordinator of %s" % (why, meta.get("owner") or "the owning project")]


# ---------------------------------------------------------------- validate (design review, fact 6)

VALIDATOR_PROMPT = """You are a design validator of another model family. Read the spec below cold
and judge whether its DESIGN is right (not whether it is clear: a separate judge did that).
Answer with ONE JSON object: {"verdict": "agree" | "partial" | "disagree",
"gaps": ["a design gap, one line each"], "evidence": "why, citing sections"}"""


def validate(a):
    spec_dir, text, meta = load_spec(a.spec_dir)
    if a.family.lower() == meta["author_family"].lower():
        raise Refusal(NOT_PASSED, "the validator's family is the author's (%s): it is never counted" % a.family)
    key = os.environ.get(a.key_env or "OPENROUTER_API_KEY", "")
    if not key:
        raise Refusal(NO_MODEL, "the key variable %s is empty" % (a.key_env or "OPENROUTER_API_KEY"))
    res = call_model(a.endpoint or DEFAULT_ENDPOINT, key, a.model,
                     VALIDATOR_PROMPT + "\n\n=== SPEC ===\n" + strip_judge_record(text), a.timeout, 8000)
    spend.record("spec.validate", a.model, res.get("cost_usd"), res.get("cost_source", "unknown"),
                 meta.get("id"), None, None, res.get("served_by"), note=res.get("generation_id"))
    reply = parse_reply(res.get("text")) if not res.get("error") else None
    if not reply or reply.get("verdict") not in ("agree", "partial", "disagree"):
        return NOT_PASSED, meta.get("status") or "draft", ["no verdict recorded (%s)" % (res.get("error") or "no JSON")]
    rec = {"schema": "spec-validator/1", "model": a.model, "family": a.family.lower(),
           "verdict": reply["verdict"], "gaps": reply.get("gaps") or [], "evidence": reply.get("evidence"),
           "spec_sha256": content_hash(text), "cost_usd": res.get("cost_usd"),
           "generation_id": res.get("generation_id"), "at": now()}
    vd = os.path.join(spec_dir, "review", "validators")
    os.makedirs(vd, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", (a.family + "-" + a.model).lower()).strip("-")
    with open(os.path.join(vd, slug + ".json"), "w", encoding="utf-8") as fh:
        json.dump(rec, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    return PASS, meta.get("status") or "draft", ["%s (%s): %s, recorded in review/validators/%s.json"
                                                 % (a.model, a.family, reply["verdict"], slug)]


# ---------------------------------------------------------------- gate (CI)

def find_spec_at(repo, spec_id, commit):
    """The directory, at that commit, whose spec.json carries that id."""
    def git(*args):
        return subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True)
    if git("cat-file", "-e", commit + "^{commit}").returncode != 0:
        raise Refusal(NOT_PASSED, "commit %s is not in this checkout (fetch it, fetch-depth 0)" % commit)
    files = git("ls-tree", "-r", "--name-only", commit).stdout.splitlines()
    for f in files:
        if not f.endswith("/spec.json") or not (f.startswith("docs/specs/") or f.startswith("docs/plans/")):
            continue
        try:
            meta = json.loads(git("show", "%s:%s" % (commit, f)).stdout)
        except ValueError:
            continue
        if isinstance(meta, dict) and meta.get("id") == spec_id:
            return os.path.dirname(f)
    raise Refusal(NOT_PASSED, "no spec.json with id %s under docs/specs/ or docs/plans/ at %s" % (spec_id, commit))


def gate(a):
    try:
        body = open(a.pr_body, encoding="utf-8").read()
    except OSError as e:
        raise Refusal(UNREADABLE, "the pull request body %s cannot be read (%s)" % (a.pr_body, e))
    m = TRAILER.search(body)
    if not m:
        return NOT_PASSED, "draft", ["the pull request body carries no `Spec: <spec id>@<commit>` trailer: "
                                     "no build merges without a judged spec"]
    spec_id, commit = m.group(1), m.group(2)
    rel = find_spec_at(a.repo, spec_id, commit)
    tmp = tempfile.mkdtemp(prefix="spec-gate-")
    try:
        arch = subprocess.run(["git", "-C", a.repo, "archive", "--format=tar", commit, rel],
                              capture_output=True)
        if arch.returncode != 0:
            raise Refusal(NOT_PASSED, "git archive of %s at %s failed" % (rel, commit))
        subprocess.run(["tar", "-x", "-C", tmp], input=arch.stdout, check=True)
        rubric = load_rubric(rubric_path(a.rubric, a.repo))
        code, status, reasons = verify(os.path.join(tmp, rel), rubric, a.require_cross_family)
        return code, status, ["spec %s at %s (%s)" % (spec_id, commit[:12], rel)] + reasons
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- calibrate (fact 12)

def calibrate(a):
    seeds = a.seeds or os.path.join(SKILL, "tests", "judge-seeds")
    dirs = sorted(d for d in os.listdir(seeds) if os.path.isfile(os.path.join(seeds, d, "expect.json")))
    if not dirs:
        raise Refusal(UNREADABLE, "no seeds (dirs with expect.json) in %s" % seeds)
    results, caught, cost = [], 0, 0.0
    for d in dirs:
        tmp = tempfile.mkdtemp(prefix="judge-seed-")
        try:
            shutil.copytree(os.path.join(seeds, d), os.path.join(tmp, d))
            expect = json.load(open(os.path.join(tmp, d, "expect.json"), encoding="utf-8"))
            sub = argparse.Namespace(**dict(vars(a), spec_dir=os.path.join(tmp, d), verify=False,
                                            new_cycle=False, reason=None, dry_run=False))
            try:
                code, status, reasons = check(sub)
            except Refusal as e:
                if e.code == NO_MODEL:
                    raise
                code, status, reasons = e.code, "draft", [str(e)]
            rs = rounds(os.path.join(tmp, d))
            r = rs[-1] if rs else {}
            zero_ok = all((r.get("scores") or {}).get(dim) == 0 for dim in expect.get("zero") or [])
            hit = bool(r) and r.get("verdict") != "pass" and zero_ok
            caught += hit
            cost += r.get("cost_usd") or 0.0
            results.append({"seed": d, "defect": expect.get("defect"), "verdict": r.get("verdict"),
                            "scores": r.get("scores"), "caught": hit,
                            "generation_id": r.get("generation_id"), "cost_usd": r.get("cost_usd")})
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    rec = {"schema": "judge-calibration/1", "at": now(), "seeds": len(dirs), "caught": caught,
           "min": a.min, "cost_usd": round(cost, 6), "results": results}
    out = a.out or os.path.expanduser("~/.local/state/task-pipeline/judge-calibration/%s.json"
                                      % datetime.date.today().isoformat())
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    lines = ["%s %-28s %s" % ("caught" if x["caught"] else "MISSED", x["seed"], x["verdict"]) for x in results]
    lines.append("calibration: %d of %d seeds caught (minimum %d), USD %.4f, recorded in %s"
                 % (caught, len(dirs), a.min, cost, out))
    return (PASS if caught >= a.min else NOT_PASSED), "calibration", lines


# ---------------------------------------------------------------- init

def init(a):
    d = a.spec_dir
    if os.path.exists(os.path.join(d, "spec.md")):
        raise Refusal(UNREADABLE, "%s already holds a spec.md" % d)
    os.makedirs(d, exist_ok=True)
    tpl = open(os.path.join(SKILL, "references", "spec-template.md"), encoding="utf-8").read()
    body = tpl.split("<!-- spec starts -->", 1)[-1].lstrip("\n")
    for k, v in (("<id>", a.id), ("<size>", a.size), ("<kind>", a.kind)):
        body = body.replace(k, v)
    with open(os.path.join(d, "spec.md"), "w", encoding="utf-8") as fh:
        fh.write(body)
    meta = {"schema": "spec/1", "id": a.id, "owner": a.owner or "", "side": a.side or "",
            "size": a.size, "kind": a.kind, "user_kinds": [], "supersedes": [], "path": d,
            "commit": None, "content_sha256": content_hash(body), "status": "draft",
            "author_family": a.author_family.lower(), "judge": [], "acceptance": [],
            "estimate": {"kind": a.kind, "p50_h": None, "p85_h": None, "slot": None}, "waits": []}
    with open(os.path.join(d, "spec.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    return PASS, "draft", ["%s: spec.md and spec.json written; fill every section, then "
                           "`spec_protocol.py check` and `spec_judge.py check`" % d]


# ---------------------------------------------------------------- cli

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    def model_flags(x):
        x.add_argument("--models", help="a judge-models/1 file (default: $TASK_PIPELINE_JUDGE_MODELS, "
                       "~/.config/task-pipeline/judge-models.json, the shipped roles)")
        x.add_argument("--rubric", help="a judge-rubric/1 file (default: $TASK_PIPELINE_JUDGE_RUBRIC, "
                       ".task-pipeline/judge-rubric.md, ~/.config/task-pipeline/judge-rubric.md, the shipped one)")
        x.add_argument("--glossary", help="the canon glossary sent with the spec")
        x.add_argument("--endpoint", help="an OpenAI-compatible base URL")
        x.add_argument("--key-env", help="the variable holding the key (default OPENROUTER_API_KEY)")
        x.add_argument("--timeout", type=int, default=240)
        x.add_argument("--require-cross-family", action="store_true",
                       help="a same-family judge never satisfies the gate (the PassionCode estate)")
        x.add_argument("--project", help="the repository whose .task-pipeline/judge-rubric.md applies")
        x.add_argument("--json", action="store_true")

    i = sub.add_parser("init")
    i.add_argument("spec_dir")
    i.add_argument("--id", required=True)
    i.add_argument("--author-family", required=True)
    i.add_argument("--size", choices=SIZES, default="S")
    i.add_argument("--kind", choices=KINDS, default="feature")
    i.add_argument("--owner")
    i.add_argument("--side")
    i.add_argument("--json", action="store_true")
    c = sub.add_parser("check")
    c.add_argument("spec_dir")
    c.add_argument("--verify", action="store_true", help="call nothing: the verdict on file must match")
    c.add_argument("--new-cycle", action="store_true", help="judge again after the rounds were spent")
    c.add_argument("--reason")
    c.add_argument("--dry-run", action="store_true", help="print the prompt, call nothing")
    model_flags(c)
    v = sub.add_parser("validate")
    v.add_argument("spec_dir")
    v.add_argument("--model", required=True)
    v.add_argument("--family", required=True)
    v.add_argument("--endpoint")
    v.add_argument("--key-env")
    v.add_argument("--timeout", type=int, default=240)
    v.add_argument("--json", action="store_true")
    hh = sub.add_parser("hash")
    hh.add_argument("spec_dir")
    hh.add_argument("--json", action="store_true")
    g = sub.add_parser("gate")
    g.add_argument("--pr-body", required=True)
    g.add_argument("--repo", default=".")
    g.add_argument("--rubric")
    g.add_argument("--require-cross-family", action="store_true")
    g.add_argument("--json", action="store_true")
    k = sub.add_parser("calibrate")
    k.add_argument("--seeds")
    k.add_argument("--min", type=int, default=9)
    k.add_argument("--out")
    model_flags(k)
    try:
        a = p.parse_args(argv)
    except SystemExit as e:
        return UNREADABLE if e.code else PASS
    try:
        if a.cmd == "hash":
            _, text, _ = load_spec(a.spec_dir)
            code, status, lines = PASS, None, [content_hash(text)]
        else:
            code, status, lines = {"init": init, "check": check, "validate": validate,
                                   "gate": gate, "calibrate": calibrate}[a.cmd](a)
    except Refusal as e:
        code, status, lines = e.code, "draft", [str(e)]
    if getattr(a, "json", False):
        print(json.dumps({"code": code, "status": status, "lines": lines}, ensure_ascii=False, indent=1))
    else:
        tag = {PASS: "PASS", NOT_PASSED: "FAIL", UNREADABLE: "UNREADABLE", NO_MODEL: "NO JUDGE"}[code]
        for n, line in enumerate(lines):
            print(("%s %s" % (tag, line)) if n == 0 and a.cmd != "hash" else line)
        if status and a.cmd in ("check", "gate"):
            print("status: %s" % status)
    return code


if __name__ == "__main__":
    sys.exit(main())
