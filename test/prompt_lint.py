#!/usr/bin/env python3
"""Prompt lint for the plugin's Markdown: Anthropic's prompting practices as checks.

Every Markdown file under plugins/task-pipeline/ is a prompt some agent loads, so
the practices in docs/reports/2026-11-16-anthropic-prompting/README.md apply to it.
This script checks the ones a machine can check.

Hard rules (any hit fails):
  think-instruction     P-02  "think carefully", "think step by step" and kin
  reasoning-extraction  P-03  asking the model to write out its reasoning
  skill-length          P-09  a SKILL.md body over 500 lines
  description           P-11  a skill or agent description that is missing,
                              over 1024 characters, or written in first or
                              second person

Ratchet metrics (may fall, never rise above the committed baseline):
  bold, caps, em_dash, version_history, words   P-08, P-09, P-10
  unwanted_stop   P-04  "ask the operator", "otherwise wait", "escalate to the
                  operator" and kin in a paragraph that names no human gate and
                  no delegation

Text inside fenced code blocks and inline code spans is not checked: quoting a
phrase is not instructing it.

  python3 test/prompt_lint.py              check against the baseline (exit 1 on a breach)
  python3 test/prompt_lint.py measure      print the metrics as JSON
  python3 test/prompt_lint.py rebaseline   lower the baseline to the current numbers
                                           (refuses to raise any metric)
  python3 test/prompt_lint.py selftest     plant each defect and require a rejection
"""
import json, os, re, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "task-pipeline")
BASELINE = os.path.join(ROOT, "test", "prompt_lint_baseline.json")
METRICS = ("bold", "caps", "em_dash", "version_history", "unwanted_stop", "words")

FENCE = re.compile(r"^[ \t]*(```|~~~).*?^[ \t]*\1[^\n]*$", re.M | re.S)
INLINE = re.compile(r"`[^`\n]*`")
NEGATION = re.compile(r"\b(not|never|no|don't|do not|remove|delete|drop|without)\b[^.\n]{0,40}$", re.I)
THINK = re.compile(r"\b(think|reason)(ing)? (carefully|step[- ]by[- ]step|hard(er)?|deeply|thoroughly)\b", re.I)
EXTRACT = re.compile(
    r"\b(show|write( out)?|explain|include|give|output|print|state)\b[^.\n]{0,20}"
    r"\b(your|its|the model's) (full |internal |step[- ]by[- ]step )?"
    r"(reasoning|thinking|thought process|chain[- ]of[- ]thought)\b", re.I)
BOLD = re.compile(r"\*\*[^*\n]+\*\*")
CAPS = re.compile(r"\b[A-Z]{4,}\b")
CAPS_OK = {"REQ", "JSON", "HTML", "TODO", "SKILL", "DOCMAP", "HANDOFF", "README",
           "CHANGELOG", "AGENTS", "CLAUDE", "YAML", "HTTP", "HTTPS", "POST", "UUID",
           "DONE", "PASS", "FAIL", "BLOCKED", "KERNEL", "PROFILE", "NOTICE", "LICENSE",
           "GET", "PUT", "PATCH", "DELETE", "OAUTH", "CI", "API", "URL", "SPEC", "WARN",
           "HOLD", "PARK", "OPEN", "TRUE", "FALSE", "NULL", "NONE", "MCP", "SHA", "UTF",
           "ASCII", "CSV", "XML", "SQL", "HEAD", "ADR", "PARTIAL", "SKIP", "SKIPPED"}
HISTORY = re.compile(r"\b(until|since|added in|from|before|as of) v?\d+\.\d+(\.\d+)?\b", re.I)
STOP = re.compile(r"\b(ask the (operator|user)|let the (operator|user) decide|otherwise wait|"
                  r"escalate to the (operator|user)|wait for the (operator|user)|"
                  r"stop and (ask|report)|the operator decides)\b", re.I)
STOP_OK = re.compile(r"(standing authori[sz]ation|delegat|human gate|sign-in|one-time code|"
                     r"consent|payment|typed secret|spend above|recorded as the operator|"
                     r"`manual`|manual gate|outward|explicit go|\bgo\b)", re.I)
FIRST_SECOND = re.compile(r"^\s*(I|I'm|I'll|My|You|You're|You'll|Your)\b")


def strip_code(text):
    return INLINE.sub("", FENCE.sub("", text))


def md_files(base):
    for d, _, fs in os.walk(base):
        for f in sorted(fs):
            if f.endswith(".md"):
                yield os.path.join(d, f)


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (m.group(1), text[m.end():]) if m else ("", text)


def description(fm):
    m = re.search(r"^description:\s*(.*?)(?=^\w[\w-]*:|\Z)", fm, re.M | re.S)
    if not m:
        return None
    v = " ".join(m.group(1).split())
    if v.startswith(">") or v.startswith("|"):
        v = v[1:].strip()
    return v.strip('"').strip("'")


def lint_file(path, rel):
    raw = open(path, encoding="utf-8").read()
    fm, body = frontmatter(raw)
    text = strip_code(raw)
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        for rule, rx in (("think-instruction", THINK), ("reasoning-extraction", EXTRACT)):
            m = rx.search(line)
            if m and not NEGATION.search(line[:m.start()]):
                hits.append(f"{rel}:{n}: {rule}: {m.group(0)!r}")
    is_skill = os.path.basename(path) == "SKILL.md"
    is_agent = os.sep + "agents" + os.sep in path
    if is_skill and len(body.splitlines()) > 500:
        hits.append(f"{rel}: skill-length: body is {len(body.splitlines())} lines (limit 500)")
    if is_skill or is_agent:
        d = description(fm)
        if not d:
            hits.append(f"{rel}: description: missing")
        else:
            if len(d) > 1024:
                hits.append(f"{rel}: description: {len(d)} characters (limit 1024)")
            if FIRST_SECOND.search(d):
                hits.append(f"{rel}: description: first or second person ({d[:30]!r})")
    unwanted = 0
    for para in re.split(r"\n\s*\n", text):
        for m in STOP.finditer(para):
            if not NEGATION.search(para[:m.start()][-60:]) and not STOP_OK.search(para):
                unwanted += 1
    metrics = {
        "unwanted_stop": unwanted,
        "bold": len(BOLD.findall(text)),
        "caps": sum(1 for w in CAPS.findall(text) if w not in CAPS_OK),
        "em_dash": text.count("—"),
        "version_history": len(HISTORY.findall(text)),
        "words": len(text.split()),
    }
    return hits, metrics


def measure(base=PLUGIN):
    hits, files, total = [], {}, dict.fromkeys(METRICS, 0)
    for p in md_files(base):
        rel = os.path.relpath(p, ROOT)
        h, m = lint_file(p, rel)
        hits += h
        files[rel] = m
        for k in METRICS:
            total[k] += m[k]
    return hits, total, files


def check(base=PLUGIN, baseline_path=BASELINE):
    hits, total, _ = measure(base)
    problems = list(hits)
    if os.path.isfile(baseline_path):
        bl = json.load(open(baseline_path))["total"]
        for k in METRICS:
            if k not in bl:
                problems.append(f"ratchet: {k} has no baseline yet (run rebaseline)")
            elif total[k] > bl[k]:
                problems.append(f"ratchet: {k} rose to {total[k]} (baseline {bl[k]})")
    else:
        problems.append(f"ratchet: no baseline at {os.path.relpath(baseline_path, ROOT)}")
    return problems, total


def rebaseline():
    _, total, files = measure()
    if os.path.isfile(BASELINE):
        old = json.load(open(BASELINE))["total"]
        up = [k for k in METRICS if k in old and total[k] > old[k]]  # a new metric enters at its value
        if up:
            print("refused: rebaseline would raise " + ", ".join(
                f"{k} {old[k]} -> {total[k]}" for k in up))
            return 1
    json.dump({"total": total, "files": files}, open(BASELINE, "w"), indent=1, sort_keys=True)
    print("baseline written: " + json.dumps(total))
    return 0


def selftest():
    cases = {
        "think": ("Think carefully before you answer.\n", "think-instruction"),
        "extract": ("Return the verdict and explain your reasoning in full.\n", "reasoning-extraction"),
        "desc": ("---\nname: x\ndescription: \"You can use me to do things.\"\n---\nbody\n", "description"),
        "long": ("---\nname: x\ndescription: \"Does x. Use when y.\"\n---\n" + "line\n" * 501, "skill-length"),
    }
    stop_cases = (("Unclear? Ask the operator and otherwise wait.\n", 2),
                  ("Unclear? Ask the operator unless a standing authorization covers it.\n", 0))
    clean = ("Do not tell the model to think carefully.\n"
             "Write `think step by step` nowhere.\n"
             "```\nThink carefully.\n```\n")
    failed = 0
    with tempfile.TemporaryDirectory() as td:
        for name, (body, rule) in cases.items():
            d = os.path.join(td, name)
            os.makedirs(d)
            fname = "SKILL.md" if name in ("desc", "long") else "ref.md"
            open(os.path.join(d, fname), "w").write(body)
            hits, _, _ = measure(d)
            ok = any(rule in h for h in hits)
            print(("ok  " if ok else "FAIL") + f"  planted {rule} is rejected")
            failed += not ok
        d = os.path.join(td, "clean")
        os.makedirs(d)
        open(os.path.join(d, "ref.md"), "w").write(clean)
        hits, _, _ = measure(d)
        print(("ok  " if not hits else "FAIL") + "  negated, inline and fenced quotes pass")
        failed += bool(hits)
        for i, (body, want) in enumerate(stop_cases):
            d = os.path.join(td, f"stop{i}")
            os.makedirs(d)
            open(os.path.join(d, "ref.md"), "w").write(body)
            _, total, _ = measure(d)
            ok = total["unwanted_stop"] == want
            print(("ok  " if ok else "FAIL") + f"  unwanted_stop counts {want} for case {i}")
            failed += not ok
        bl = os.path.join(td, "bl.json")
        json.dump({"total": dict.fromkeys(METRICS, 0)}, open(bl, "w"))
        probs, _ = check(os.path.join(td, "think"), bl)
        ok = any(p.startswith("ratchet: words") for p in probs)
        print(("ok  " if ok else "FAIL") + "  a metric above the baseline is rejected")
        failed += not ok
    return failed


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "check"
    if cmd == "measure":
        hits, total, files = measure()
        print(json.dumps({"hits": hits, "total": total, "files": files}, indent=1, sort_keys=True))
        return 0
    if cmd == "rebaseline":
        return rebaseline()
    if cmd == "selftest":
        return 1 if selftest() else 0
    problems, total = check()
    for p in problems:
        print(p)
    if problems:
        print(f"FAIL: prompt lint, {len(problems)} problem(s)")
        return 1
    print("PASS: prompt lint " + json.dumps(total))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
