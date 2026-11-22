#!/usr/bin/env python3
"""task_prompt.py: check a task written for an executor before it is handed over.

An executor is whoever receives the task and works without the author beside it: a
subagent, a wave's node owner, another session, another project's agent. The check reads
the task's text and answers six questions (`references/task-prompts.md`):

    P1 outcome   the end result is stated: what is true when the work is finished
    P2 done      how the executor knows it is finished: a check, a command, a criterion
    P3 sweep     the work goes in waves with a pass that looks for what was missed
    P4 no gates  nothing tells the executor to stop for approval between steps
    P5 return    what comes back, and in which form
    P6 context   where to look, what is ruled out, what must not change

    check  FILE|-  [--kind work|lookup|verify] [--json]
           One task. Exit 0 pass, 1 a failed question, 2 usage.
    corpus FILE.jsonl [--by FIELD] [--json]
           Many tasks, one JSON object a line with `prompt` (and optionally `kind_hint`,
           and the field named by --by). Prints the share that fails each question.

The kind decides what is owed. `work` changes something and owes all of P1 to P4.
`lookup` only finds or reads and owes P1 and P5. `verify` returns a verdict on someone
else's work and owes P1, P2 and P5. P5 and P6 are warnings on `work`.

The reading is by words, in English and Russian, so it proves presence, never quality:
a task that passes may still be a bad task; a task that fails is missing a part by name.
Standard library only.
"""
import argparse
import json
import re
import sys

F = re.I | re.S


def rx(*parts):
    return re.compile("|".join(parts), F)


OUTCOME = rx(
    r"\b(goal|objective|outcome|end[ -]state|end[ -]result|deliverable|expected result)s?\b\s*[:.(]",
    r"\b(the )?(result|output) (is|should be|must be|will be)\b",
    r"\bwhen (you are |this is |it is |the work is )?(done|finished|complete)\b",
    r"\b(so that|what (must|should|will) be true|is true when)\b",
    r"\bwhat i (need|want)\b", r"\bi need (to know|a|an|the)\b",
    r"\b(produce|return|deliver|write|report)\b[^.\n]{0,80}\b(report|table|list|verdict|file|json|summary|diff|patch|inventory|findings|receipt)\b",
    r"\byour (job|task|goal|mission)\b\s*(is|:)",
    r"(цель|итог|результат|что должно получиться|что должно быть|конечн\w+ результат|на выходе)\s*[:.(]",
    r"(должн\w+ (быть|получиться|появиться|работать)|в итоге|чтобы в результате|нужно получить)",
)
DONE = rx(
    r"\b(done when|definition of done|dod\b|acceptance|exit (check|criteri\w+)|finish line|success criteri\w+)",
    r"\b(is|are) (done|finished|complete) (when|only when|once)\b",
    r"\b(passes?|must pass|exit(s)? 0|exit code 0|prints? `?pass|green)\b",
    r"\b(verify|prove|check|confirm) (it |this |that |the \w+ )?(by|with|against)\b",
    r"\b(run|rerun)\b[^.\n]{0,60}(`[^`]+`|\btests?\b|\bsuite\b|\bcheck\b)",
    r"\b(the check|the test|the proof|evidence)\b\s*(is|:)",
    r"(готово,? когда|критери\w+ готовности|критери\w+ приёмки|приёмк\w+|считается (сделан|готов)\w*)",
    r"(провер\w+ (командой|тестом|так)|тесты? (зелён\w+|проход\w+)|доказательств\w+\s*:)",
)
SWEEP = rx(
    r"\b(second|another|final|closing|last) (pass|round|wave|sweep|reading)\b",
    r"\b(sweep|re-?read|re-?check|re-?scan|go (back )?over)\b[^.\n]{0,80}\b(miss\w*|skipp\w*|left|gap\w*|overlook\w*|whole|every|all)\b",
    r"\bwhat (was|is|you|we|i) (have )?(missed|skipped|left out|overlooked)\b",
    r"\b(look|search|hunt|check) for (what|anything|things) (was |is |you |we )?(missed|skipped|left|overlooked)\b",
    r"\b(two|2|three|3) consecutive (verification )?(rounds|passes|waves)\b",
    r"\b(waves?|rounds?|pass(es)?)\b[^.\n]{0,80}\b(miss\w*|skipp\w*|overlook\w*|left out|nothing new|no new)\b",
    r"\b(until|repeat until) (a round|a pass|a wave)?[^.\n]{0,40}\b(finds? nothing|comes back clean|no new)\b",
    r"\b(not examined|did not (look|examine|check|read)|could not (verify|check|open))\b",
    r"(втор\w+ (проход|круг|волн\w+)|ещё раз пройди|повторн\w+ проход|волн\w+[^.\n]{0,60}(пропущ\w+|упущ\w+|пропуск\w*))",
    r"(что (было )?(пропущен\w+|упущен\w+)|пропустил\w*|упустил\w*|не просмотрен\w+|не проверен\w+)",
)
GATE = rx(
    r"\b(wait|pause|stop|halt)\b[^.\n]{0,50}\b(for|until)\b[^.\n]{0,30}\b(my|our|the user'?s?|the operator'?s?|human|explicit)?\s*(approval|confirmation|go-ahead|sign-?off|ok(ay)?|review|answer|reply)\b",
    r"\b(ask|check with|confirm with) (me|us|the user|the operator|the owner)\b[^.\n]{0,40}\b(before|first|prior)\b",
    r"\bbefore (you )?(proceed|continu|mov)\w*[^.\n]{0,40}\b(ask|confirm|get approval|wait)\b",
    r"\b(do not|don't|never) (proceed|continue|move on|start)\b[^.\n]{0,60}\b(until|without)\b[^.\n]{0,40}\b(approv\w+|confirm\w+|i say|told|go-ahead|sign-?off)\b",
    r"\b(report back|check in|stop) after (each|every) (step|stage|phase|file|task)\b",
    r"\b(get|need|requires?) (my |explicit |human )?(approval|sign-?off) (before|at|after) (each|every)\b",
    r"(жди|дожд\w+|останов\w+)[^.\n]{0,40}(подтвержден\w+|одобрен\w+|разрешен\w+|ответа|согласован\w+)",
    r"(спроси|уточни|согласуй)[^.\n]{0,30}(перед|прежде|сначала)",
    r"(не (продолжай|начинай|переходи))[^.\n]{0,60}(пока|без)[^.\n]{0,30}(подтвержд\w+|одобр\w+|разреш\w+|скажу)",
    r"после кажд\w+ (шага|этапа|стадии)[^.\n]{0,40}(отчитайся и жди|жди|спрашивай|останавливайся)",
)
# A sentence that forbids stopping names the same words; it is not a gate.
NOT_GATE = rx(r"\b(do not|don't|never|no need to|without) (wait|pause|stop|ask|check in)\b",
              r"\bnot? (a )?question\b", r"не (жди|спрашивай|останавливайся|уточняй)")
RETURN = rx(
    r"\b(report|return|reply|respond|answer|output|give me|send back|come back with|hand back)\b[^.\n]{0,80}",
    r"\b(format|shape|schema|as a table|as json|under \d+ words|in \d+ (lines|words))\b",
    r"(верни|вернуть|ответ\w*|отчёт\w*|отчет\w*|пришли|в ответе|формат\w*)",
)
CONTEXT = rx(
    r"(`[^`\n]*[/.][^`\n]*`|(?<!\w)[~.]?/[\w.-]+/[\w./-]+|\b[\w-]+\.(md|py|ts|tsx|js|json|sh|swift|go|rs|yml|yaml|toml)\b)",
    r"\b(ruled out|already (checked|tried|know|established)|do not (touch|change|edit|modify)|must not change|out of scope|read-only|scope:)\b",
    r"(не (трогай|меняй|правь)|вне (объёма|рамок)|уже (проверено|исключено|известно)|только чтение)",
)
CHANGE = rx(
    r"\b(implement|fix|write|add|create|build|refactor|edit|change|update|migrate|remove|delete|rename|"
    r"commit|deploy|release|publish|install|apply|patch|rewrite|translate|generate|render|merge)\b",
    r"(реализуй|исправь|почини|добавь|создай|напиши|собери|измени|обнови|удали|переименуй|выпусти|"
    r"задеплой|опубликуй|установи|сделай|переведи|сгенерируй|перепиши|внедри|встрой)",
)
VERDICT = rx(r"\b(verdict|blind|certif\w+|review(er)?|audit(or)?|judge|pass or fail|tier report)\b",
             r"(вердикт|ревью|проверяющ\w+|суди\w*)")

# A task may hand its substance to a brief, a plan or a packet on disk. Then the text that
# is checked is the task plus that file; a file that cannot be read is said, not guessed.
REF = re.compile(r"(?:brief|plan|packet|spec|task card|backlog row|dossier)\b[^\n]{0,160}?((?:~|/)[\w./@+-]+\.(?:md|json|txt))"
                 r"|((?:~|/)[\w./@+-]*(?:brief|plan|packet|spec)[\w./@+-]*\.(?:md|json|txt))", re.I)


def follow(text, limit=200000):
    """The files a task delegates to: (text of those that exist, paths that could not be read)."""
    import os
    read, unread, seen = [], [], set()
    for m in REF.finditer(text):
        path = (m.group(1) or m.group(2)).rstrip(".,;)")
        if path in seen:
            continue
        seen.add(path)
        full = os.path.expanduser(path)
        try:
            if os.path.getsize(full) <= limit:
                read.append(open(full, encoding="utf-8", errors="ignore").read())
                continue
        except OSError:
            pass
        unread.append(path)
    return "\n".join(read), unread


QUESTIONS = {
    "P1": ("outcome", "the end result is not stated: say what is true when the work is finished"),
    "P2": ("done", "no finish criterion: name the check, command or condition that says it is done"),
    "P3": ("sweep", "no wave that looks for what was missed: ask for a closing pass over the whole and a list of what was not examined"),
    "P4": ("no gates", "the task stops for approval between steps: state the end result and the limits instead, and let it run"),
    "P5": ("return", "what comes back is not stated: name the form of the answer and its evidence"),
    "P6": ("context", "no pointer to where to look or what must not change"),
}
OWED = {"work": {"fail": ["P1", "P2", "P3", "P4"], "warn": ["P5", "P6"]},
        "lookup": {"fail": ["P1", "P5"], "warn": ["P6"]},
        "verify": {"fail": ["P1", "P2", "P5"], "warn": ["P4", "P6"]}}


def kind_of(text, hint=""):
    h = (hint or "").lower()
    if "verifier" in h or "tester" in h or "auditor" in h:
        return "verify"
    if h in ("explore", "web-fetch", "plan"):
        return "lookup"
    head = text[:1500]
    if VERDICT.search(head) and not CHANGE.search(text[:600]):
        return "verify"
    return "work" if CHANGE.search(text) else "lookup"


def gates(text):
    hits = []
    for m in GATE.finditer(text):
        start = text.rfind("\n", 0, m.start()) + 1
        sent = text[max(start, m.start() - 80):m.end()]
        if NOT_GATE.search(sent):
            continue
        hits.append(" ".join(text[m.start():m.end()].split())[:120])
    return hits


def check(text, kind=None, hint="", follow_refs=True):
    kind = kind or kind_of(text, hint)
    gate_hits = gates(text)
    extra, unread = follow(text) if follow_refs else ("", [])
    own = text
    text = text + "\n" + extra
    present = {"P1": bool(OUTCOME.search(text)), "P2": bool(DONE.search(text)),
               "P3": bool(SWEEP.search(text)), "P4": not gate_hits,
               "P5": bool(RETURN.search(text)), "P6": bool(CONTEXT.search(text))}
    owed = OWED[kind]
    # What a file nobody could read may hold is not judged: P1 to P3 are left open, by name.
    open_q = [q for q in ("P1", "P2", "P3") if unread and not extra and not present[q] and q in owed["fail"]]
    fails = [q for q in owed["fail"] if not present[q] and q not in open_q]
    warns = [q for q in owed["warn"] if not present[q]]
    return {"kind": kind, "words": len(own.split()), "present": present, "fails": fails,
            "warns": warns, "gates": gate_hits, "ok": not fails, "followed": bool(extra),
            "not_read": unread, "open": open_q}


def corpus(path, by=None):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    groups = {}
    for r in rows:
        res = check(r["prompt"], hint=r.get("kind_hint") or r.get("agent") or "")
        for key in ("all", (r.get(by) or "?") if by else None):
            if key is None:
                continue
            g = groups.setdefault(key, {"n": 0, "ok": 0, "kinds": {}, "fails": {q: 0 for q in QUESTIONS},
                                        "owed": {q: 0 for q in QUESTIONS}})
            g["n"] += 1
            g["ok"] += res["ok"]
            g["kinds"][res["kind"]] = g["kinds"].get(res["kind"], 0) + 1
            g["followed"] = g.get("followed", 0) + res["followed"]
            g["open"] = g.get("open", 0) + bool(res["open"])
            for q in OWED[res["kind"]]["fail"]:
                g["owed"][q] += q not in res["open"]
            for q in res["fails"]:
                g["fails"][q] += 1
    return groups


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("file")
    c.add_argument("--kind", choices=list(OWED))
    c.add_argument("--json", action="store_true")
    k = sub.add_parser("corpus")
    k.add_argument("file")
    k.add_argument("--by")
    k.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    if a.cmd == "check":
        text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
        res = check(text, a.kind)
        if a.json:
            print(json.dumps(res, ensure_ascii=False, indent=1))
        else:
            print("task prompt, kind %s, %d words" % (res["kind"], res["words"]))
            for q in res["fails"]:
                print("FAIL %s %s: %s" % (q, QUESTIONS[q][0], QUESTIONS[q][1]))
            for g in res["gates"]:
                print("     gate: " + g)
            for q in res["warns"]:
                print("warn %s %s: %s" % (q, QUESTIONS[q][0], QUESTIONS[q][1]))
            print("PASS" if res["ok"] else "FAIL: %d question(s)" % len(res["fails"]))
        return 0 if res["ok"] else 1
    groups = corpus(a.file, a.by)
    if a.json:
        print(json.dumps(groups, ensure_ascii=False, indent=1))
        return 0
    for key, g in sorted(groups.items(), key=lambda kv: -kv[1]["n"]):
        parts = ["%s %d/%d" % (q, g["fails"][q], g["owed"][q]) for q in QUESTIONS if g["owed"][q]]
        print("%-30s n=%-5d pass %3d%%  brief read %d, unread %d  fails: %s"
              % (str(key)[:30], g["n"], 100 * g["ok"] // max(g["n"], 1), g.get("followed", 0),
                 g.get("open", 0), ", ".join(parts)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
