#!/usr/bin/env python3
"""meanings.py: the spec's meanings are thought on tokens; its text is written on the subscription.

`references/model-tiering.md` (Roles and money) is the doctrine; the owner's rule of
2026-11-23: the strongest model through the API (tokens, no stinting) decides the meaning
and the key features of a spec; a writer agent on the subscription writes the spec's text
from them. Standard library only.

    write        --brief FILE [--input FILE ...] --out FILE [--task T] [--config FILE]
                 [--model ID] [--max-tokens N] [--effort low|medium|high] [--key-env NAME]
                 [--endpoint URL] [--timeout S] [--dry-run]
                 ONE call to the thinker (the consilium config's "thinker", else its judge:
                 the strongest model of the host's map) that returns the meanings in the
                 fixed sections below, written to OUT with a `Thinker:` header. The call
                 goes into the spend ledger (route spec.meanings). Never retried: a failed
                 call writes nothing and exits 1.
    check        FILE [--max-words N] [--json]
                 The meanings are whole and short: every section present and filled, each
                 decision with its reason, no TBD, at most N words (default 2500: meanings,
                 not the spec; the text is the writer's).
    review-brief --brief FILE
                 The brief for the council that reviews the meanings BEFORE the writer
                 starts (size M and L): `consilium.py review --doc meanings.md --brief -`.
                 The A/B test of 2026-11-23 found the thinker's short call can bend an order
                 (a retry where the order said one request); the writer carries such an
                 error into the spec, so the meanings are judged first.
    writer-task  --meanings FILE --brief FILE --spec-out FILE [--size S|M|L]
                 The task for the writer, a subscription agent of the session: write the
                 spec from the meanings, change no meaning, send a gap back as a question.
                 It passes `task_prompt.py check --kind work`.

Sections of the meanings, in order:
    ## Goal and meaning        what the work is for and what is true when it is done
    ## Key features            the features that make it what it is, each one line
    ## Decisions               `- D1: <decision>. Because <reason>.`
    ## Contracts               what each interface promises and the check that proves it
    ## Non-goals               what it will not do
    ## Risks                   what could break it, and what would refute the design
    ## Questions for the owner strategy only, each with a default; or `none`

Exit 0 pass, 1 a failed check or a failed call, 2 usage or no key.
"""
import argparse
import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import consilium  # noqa: E402
import spend  # noqa: E402

SECTIONS = ["Goal and meaning", "Key features", "Decisions", "Contracts", "Non-goals", "Risks",
            "Questions for the owner"]
REASON = re.compile(r"\b(because|since|so that)\b|потому что|так как|чтобы", re.I)

SYSTEM = """You are the thinker of an engineering specification. You decide its meaning, not its prose:
another agent writes the spec's text from what you return, and it may not change a meaning you set.
Decide every tactical choice yourself (formats, names, thresholds, dates counted from today, what a check
compares); the writer may not invent a decision. Ask the owner only a strategy question (who it is for, what it
promises, price, name), always with the default the work goes on with. Where the brief asks for a deliverable
(a reply, a date, a row), decide its concrete value.
Return Markdown with exactly these sections, in this order, and nothing before the first one:
## Goal and meaning
## Key features
## Decisions        (each line: `- D<n>: <decision>. Because <reason>.`)
## Contracts        (what each interface promises, and the check that proves it holds: an equality, a
                     hash, a resolution, never only that a field is present)
## Non-goals
## Risks            (what could break it; what would refute the design)
## Questions for the owner   (strategy only, each with a default; or `none`)
Be dense: at most 2000 words. Write in English. Never use the em dash character."""


def split_sections(text):
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*(\(.*\))?\s*$", line)
        if m:
            cur = m.group(1).strip()
            out.setdefault(cur, [])
        elif cur is not None:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def check(path, max_words=2500):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    secs = split_sections(text)
    errors = []
    for name in SECTIONS:
        body = secs.get(name)
        if body is None:
            errors.append(f"no `## {name}` section")
        elif not body:
            errors.append(f"`## {name}` is empty (write `none` and why, if there is nothing)")
    dec = [x for x in (secs.get("Decisions") or "").splitlines() if re.match(r"^\s*[-*]\s", x)]
    if secs.get("Decisions") is not None and not dec:
        errors.append("`## Decisions` lists no decision")
    for d in dec:
        if not REASON.search(d):
            errors.append("a decision without its reason: " + d.strip()[:100])
    if re.search(r"\b(TBD|TODO|FIXME)\b", text):
        errors.append("TBD/TODO left in the meanings")
    words = len(re.findall(r"\w+", text))
    if words > max_words:
        errors.append(f"{words} words, the meanings owe at most {max_words}: the text is the writer's job")
    return {"file": str(path), "pass": not errors, "errors": errors, "words": words, "decisions": len(dec)}


def thinker_of(cfg, model=None):
    if model:
        return {"model": model, "family": model.split("/")[0], "max_tokens": 32000}
    return dict(cfg.get("thinker") or cfg["judge"])


def write(a):
    cfg = consilium.load_config(a.config)
    t = thinker_of(cfg, a.model)
    if t["model"].startswith("<") and not a.dry_run:
        print("meanings: the configuration names a role, not a model (" + cfg["_source"] + "); write the host file "
              f"{consilium.HOST} from the model map first", file=sys.stderr)
        return 2
    parts = ["<brief>\n" + pathlib.Path(a.brief).read_text(encoding="utf-8") + "\n</brief>"]
    for f in a.input or []:
        parts.append(f"<input path=\"{f}\">\n" + pathlib.Path(f).read_text(encoding="utf-8") + "\n</input>")
    user = "\n\n".join(parts) + "\n\nDecide the meanings of the spec for this brief."
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
    extra = dict(t.get("extra") or {})
    if a.effort:
        extra["reasoning"] = {"effort": a.effort}
    task = a.task or os.environ.get("TASK_PIPELINE_TASK") or pathlib.Path(a.out).parent.name
    if a.dry_run:
        print(json.dumps({"thinker": t["model"], "prompt_chars": len(user) + len(SYSTEM), "task": task}, indent=1))
        return 0
    key = os.environ.get(a.key_env)
    if not key:
        print(f"meanings: ${a.key_env} is empty; run under use_secret.py run", file=sys.stderr)
        return 2
    res = consilium.call(a.endpoint, key, t["model"], msgs, a.timeout, a.max_tokens or t.get("max_tokens", 32000),
                         extra or None)
    spend.record("spec.meanings", t["model"], res.get("cost") if res.get("cost_known", True) else None,
                 res.get("cost_source", "unknown"), task, res.get("tokens_in"), res.get("tokens_out"),
                 res.get("served_by"))
    meta = {k: v for k, v in res.items() if k != "text"}
    if res.get("error") or not (res.get("text") or "").strip():
        print("meanings: no meanings written: " + (res.get("error") or "empty answer"), file=sys.stderr)
        print(json.dumps(meta), file=sys.stderr)
        return 1
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    body = res["text"].strip()
    if not body.startswith("#"):
        body = body[body.find("## "):] if "## " in body else body
    out.write_text(f"# Meanings\n\nThinker: {t['model']}\nTask: {task}\n\n{body}\n", encoding="utf-8")
    pathlib.Path(str(out) + ".meta.json").write_text(json.dumps(dict(meta, model=t["model"], task=task,
                                                                     at=consilium.now()), indent=1), encoding="utf-8")
    r = check(out)
    print(json.dumps({"out": str(out), "cost_usd": res.get("cost"), "cost_source": res.get("cost_source"),
                      "check": r}, indent=1))
    return 0 if r["pass"] else 1


WRITER_TASK = """Your job: write the spec `{spec}` from the meanings in `{meanings}` for the brief in `{brief}`.
You are the writer on the subscription; the meanings were decided by the thinker and are not yours to change.

End result: `{spec}` exists, carries `Size: {size}` and `Meanings: {meanings}` in its header, and turns every
meaning into the sections `references/spec-protocol.md` owes for size {size}: every key feature into a
requirement with an acceptance check, every decision into the Decisions table with its reason, every
contract into its exact shape. Nothing in it contradicts the meanings; nothing in the meanings is missing.

Done when: `python3 <skill>/scripts/spec_protocol.py check {spec}` exits 0, and a closing pass over the
meanings, line by line, finds each one in the spec, and a second pass checks every example and contract
against every rule it falls under.

Work in waves: write the sections, then a closing pass that rereads the whole spec against the meanings and
lists what was missed or left vague; fix it in the same run. A gap the meanings do not settle is not filled
by invention of meaning: decide it as a tactic, record it in `## Questions` with the class `tactics`, `by`
agent and its basis, and go on. Only a strategy question the meanings already list stays `pending`. Every
check verifies the truth of what it guards (an equality, a hash, a resolution), never only that a field is
present. Every example passes the spec's own rules. Where the brief asks for a deliverable (a date, a reply),
the spec gives its concrete value. Be concise: say each thing once. Do not stop between steps for approval;
the limits are the meanings and the brief.

Return: the path of the spec, the output of the check, and the list of open questions with their defaults.
Context: read the brief and the meanings first; the documents the brief names; do not change any other file."""


REVIEW_ADDENDUM = """

## What the council reviews

The artefact is the MEANINGS of the spec (goal, key features, decisions, contracts, non-goals, risks, owner
questions), written by the thinker before a writer turns them into the spec's text. The writer may not change a
meaning, so an error here becomes an error in the spec. Judge: is every item of the order honoured literally (no
exception the order does not make, no retry where it says one request)? Is every decision correct against the
brief's facts, and does each contract say how it is proven? Is any tactical question pushed to the owner?
"""


def review_brief(a):
    print(pathlib.Path(a.brief).read_text(encoding="utf-8").rstrip() + REVIEW_ADDENDUM)
    return 0


def writer_task(a):
    print(WRITER_TASK.format(spec=a.spec_out, meanings=a.meanings, brief=a.brief, size=a.size))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write")
    w.add_argument("--brief", required=True)
    w.add_argument("--input", action="append")
    w.add_argument("--out", required=True)
    w.add_argument("--task")
    w.add_argument("--config")
    w.add_argument("--model", help="override the thinker of the config (the owner's recorded choice only)")
    w.add_argument("--max-tokens", type=int)
    w.add_argument("--effort", choices=["low", "medium", "high"])
    w.add_argument("--key-env", default="OPENROUTER_API_KEY")
    w.add_argument("--endpoint", default=consilium.DEFAULT_ENDPOINT)
    w.add_argument("--timeout", type=int, default=900)
    w.add_argument("--dry-run", action="store_true")
    c = sub.add_parser("check")
    c.add_argument("file")
    c.add_argument("--max-words", type=int, default=2500)
    c.add_argument("--json", action="store_true")
    rb = sub.add_parser("review-brief")
    rb.add_argument("--brief", required=True)
    t = sub.add_parser("writer-task")
    t.add_argument("--meanings", required=True)
    t.add_argument("--brief", required=True)
    t.add_argument("--spec-out", required=True)
    t.add_argument("--size", default="M", choices=["S", "M", "L"])
    a = ap.parse_args(argv)
    if a.cmd == "write":
        return write(a)
    if a.cmd == "writer-task":
        return writer_task(a)
    if a.cmd == "review-brief":
        return review_brief(a)
    r = check(a.file, a.max_words)
    print(json.dumps(r, indent=1) if a.json else ("PASS " if r["pass"] else "FAIL ") + "; ".join(r["errors"]))
    return 0 if r["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
