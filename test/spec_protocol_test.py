#!/usr/bin/env python3
"""spec_protocol.py, stages 0-4 as a checked protocol: every verb against planted specs.

Each case plants the defect it looks for, so a protocol that stopped catching it fails
here. The first case is OT-07's acceptance check from the 2026-11-21 system plan: a
spec with five tactical questions and one strategic question sends the owner exactly one.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "plugins/task-pipeline/skills/task-pipeline/scripts/spec_protocol.py")
CASES = []
FAILS = []


def case(fn):
    CASES.append(fn)
    return fn


SPEND_LOG = os.path.join(tempfile.mkdtemp(prefix="specproto-spend-"), "spend.jsonl")


def spend_rows():
    return [json.loads(x) for x in open(SPEND_LOG)] if os.path.exists(SPEND_LOG) else []


def run(*args, env=None):
    r = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True,
                       env=dict(os.environ, TASK_PIPELINE_SPEND_LOG=SPEND_LOG, **(env or {})))
    return r.returncode, r.stdout + r.stderr


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def expect(cond, msg):
    if not cond:
        raise AssertionError(msg)


LEDGER = """| id | question | class | answer | by | basis |
|---|---|---|---|---|---|
| Q1 | Which queue library carries the jobs? | tactics | the stdlib queue | agent | no new dependency (conventions.md) |
| Q2 | What retry timeout for the fetch? | tactics | 30 s, three tries | agent | the provider's documented limit |
| Q3 | Which file layout for the module? | tactics | one package, three files | agent | the project's layout |
| Q4 | Which schema format for the export? | tactics | JSON Schema 2020-12 | agent | the contract repo uses it |
| Q5 | Which test runner? | tactics | the existing pytest suite | agent | package.json test script |
| Q6 | Who is the product for: teams or solo founders? | strategy | solo founders first | pending | the vision names founders; teams change pricing |
"""

S_SPEC = """# Export of reports

Size: S

## Goal
Owners export a report as one file.

## Scope
In: the export. Out: sharing.

## Requirements
REQ-1 export writes one HTML file.

## Design
A function renders the snapshot. covers: REQ-1

## Questions
{ledger}
## Tests
A test opens the file with the network off. covers: REQ-1
"""


def sources(n, primary=2, unread=()):
    out = []
    for i in range(1, n + 1):
        out.append({"id": "S%d" % i, "kind": "docs" if i <= primary else "article",
                    "title": "t%d" % i, "url": "https://example.org/%d" % i,
                    "read": ("S%d" % i) not in unread, "claim": "c%d" % i})
    return out


def dossier(root, tier="M", n=6, validators=(("v1", "other-family", "agree"),),
            author="family-a/deep", cite="[S1]", unread=(), resolution=False):
    d = os.path.join(root, "research", "export")
    rows = "".join("| %s | %s | %s | evidence |\n" % v for v in validators)
    write(root, "research/export/README.md", """# Research: export

Question: how to export
Tier: {tier}
Author: {author}

## Findings
The format embeds data {cite}.

## Options
Two options.

## Recommendation
Embed the snapshot.

## What would refute it
A page that fetches on open.

## Rejected
A live API call on open.

## Validation

| validator | family | verdict | note |
|---|---|---|---|
{rows}{res}""".format(tier=tier, author=author, cite=cite, rows=rows,
                     res="\n## Resolution\nThe validator's evidence is weaker.\n" if resolution else ""))
    write(root, "research/export/sources.json", json.dumps(sources(n, unread=unread)))
    return d


@case
def owner_gets_exactly_the_one_strategic_question(root):
    spec = write(root, "spec.md", S_SPEC.format(ledger=LEDGER))
    code, out = run("questions", spec, "--json")
    data = json.loads(out)
    expect(code == 0, out)
    expect([o["id"] for o in data["owner"]] == ["Q6"], data["owner"])
    expect(data["owner"][0]["default"] == "solo founders first", data["owner"])


@case
def a_tactical_question_never_waits_on_the_owner(root):
    bad = LEDGER.replace("| the stdlib queue | agent |", "| the stdlib queue | pending |")
    code, out = run("questions", write(root, "spec.md", S_SPEC.format(ledger=bad)))
    expect(code == 1 and "Q1" in out and "never waits" in out, out)


@case
def strategy_is_not_decided_by_the_agent(root):
    bad = LEDGER.replace("| solo founders first | pending |", "| solo founders first | agent |")
    code, out = run("questions", write(root, "spec.md", S_SPEC.format(ledger=bad)))
    expect(code == 1 and "strategy is the owner's" in out, out)


@case
def an_owner_question_carries_a_default(root):
    bad = LEDGER.replace("| solo founders first | pending |", "|  | pending |")
    code, out = run("questions", write(root, "spec.md", S_SPEC.format(ledger=bad)))
    expect(code == 1 and "recommended default" in out, out)


@case
def an_unknown_is_researched_before_it_is_asked(root):
    extra = "| Q7 | Will the store accept it? | unknown | assume yes | pending | a guess |\n"
    code, out = run("questions", write(root, "spec.md", S_SPEC.format(ledger=LEDGER + extra)))
    expect(code == 1 and "researched before" in out, out)
    ok = extra.replace("a guess", "research/export: no public rule found [S3]")
    code, out = run("questions", write(root, "spec2.md", S_SPEC.format(ledger=LEDGER + ok)))
    expect(code == 0 and "owner batch: 2" in out, out)


@case
def a_known_domain_answer_cites_its_source(root):
    extra = "| Q8 | Which status code for a missing page? | known-domain | 404 | agent | everyone knows |\n"
    code, out = run("questions", write(root, "spec.md", S_SPEC.format(ledger=LEDGER + extra)))
    expect(code == 1 and "cites its source" in out, out)
    ok = extra.replace("everyone knows", "https://www.rfc-editor.org/rfc/rfc9110")
    code, _ = run("questions", write(root, "spec2.md", S_SPEC.format(ledger=LEDGER + ok)))
    expect(code == 0, "a cited known-domain answer was refused")


@case
def a_mislabelled_question_warns(root):
    bad = LEDGER.replace("Which test runner?", "What price do we charge?")
    code, out = run("questions", write(root, "spec.md", S_SPEC.format(ledger=bad)))
    expect(code == 0 and "reads like strategy" in out, out)


@case
def size_grows_with_the_task(root):
    small = json.loads(run("size", "--reqs", "2", "--files", "3", "--json")[1])
    mid = json.loads(run("size", "--reqs", "5", "--files", "8", "--contract", "--json")[1])
    big = json.loads(run("size", "--reqs", "12", "--files", "30", "--irreversible",
                         "--cross-project", "--json")[1])
    expect((small["tier"], mid["tier"], big["tier"]) == ("S", "M", "L"), (small, mid, big))
    expect(len(small["sections"]) < len(mid["sections"]) < len(big["sections"]), "sections do not grow")
    expect(big["research"]["validators"] == 2 and small["research"]["scouts"] == 0, big)
    desk = json.loads(run("size", "--reqs", "1", "--files", "1", "--new-domain", "--json")[1])
    expect(desk["tier"] == "S" and desk["research"]["scouts"] == 1, "a new domain owes research")


@case
def a_small_spec_is_short_but_complete(root):
    spec = write(root, "spec.md", S_SPEC.format(ledger=LEDGER))
    code, out = run("check", spec)
    expect(code == 0 and "owner batch: 1" in out, out)
    gap = write(root, "gap.md", S_SPEC.format(ledger=LEDGER).replace("## Tests\n", "## Notes\n"))
    code, out = run("check", gap)
    expect(code == 1 and "`Tests` missing" in out, out)


@case
def an_open_decision_in_prose_fails(root):
    spec = write(root, "spec.md", S_SPEC.format(ledger=LEDGER).replace(
        "A function renders", "TBD whether a function renders"))
    code, out = run("check", spec)
    expect(code == 1 and "leaves a decision open" in out, out)


@case
def a_medium_spec_owes_its_research(root):
    m = S_SPEC.format(ledger=LEDGER).replace("Size: S", "Size: M")
    for name in ("Contracts", "Edge cases", "Decisions", "Rollout"):
        m += "\n## %s\nwritten.\n" % name
    code, out = run("check", write(root, "spec.md", m))
    expect(code == 1 and "owes research" in out, out)
    dossier(root)
    code, out = run("check", write(root, "spec2.md", m.replace("Size: M", "Size: M\nResearch: research/export")))
    expect(code == 0 and "Meanings" in out, "an M spec without its meanings is not warned: " + out)
    code, out = run("check", write(root, "spec3.md", m.replace(
        "Size: M", "Size: M\nResearch: research/export\nMeanings: nowhere.md")))
    expect(code == 1 and "names no file" in out, out)
    write(root, "meanings.md", "# Meanings\n")
    code, out = run("check", write(root, "spec4.md", m.replace(
        "Size: M", "Size: M\nResearch: research/export\nMeanings: meanings.md")))
    expect(code == 0 and "Meanings" not in out, out)


@case
def research_counts_only_what_was_read(root):
    d = dossier(root, n=6, unread=("S6",))
    code, out = run("research", "check", d)
    expect(code == 1 and "5 source(s) read" in out, out)


@case
def an_unopened_source_is_not_evidence(root):
    d = dossier(root, n=7, unread=("S1",))
    code, out = run("research", "check", d)
    expect(code == 1 and "[S1] is cited but was not opened" in out, out)


@case
def a_citation_must_resolve(root):
    d = dossier(root, cite="[S9]")
    code, out = run("research", "check", d)
    expect(code == 1 and "[S9] is cited and not in sources.json" in out, out)


@case
def a_model_answer_is_not_a_source(root):
    d = dossier(root, n=6)
    src = os.path.join(d, "sources.json")
    items = json.load(open(src))
    items[5]["kind"] = "model"
    json.dump(items, open(src, "w"))
    code, out = run("research", "check", d)
    expect(code == 1 and "a model's answer is not a source" in out, out)


@case
def validators_come_from_another_family(root):
    d = dossier(root, validators=(("v1", "family-a", "agree"),))
    code, out = run("research", "check", d)
    expect(code == 1 and "another family" in out, out)
    d = dossier(root, tier="L", n=12, validators=(("v1", "family-b", "agree"), ("v2", "family-b", "agree")))
    code, out = run("research", "check", d)
    expect(code == 1 and "two different families" in out, out)


@case
def a_disagreement_needs_a_resolution(root):
    d = dossier(root, validators=(("v1", "family-b", "disagree"),))
    code, out = run("research", "check", d)
    expect(code == 1 and "Resolution" in out, out)
    d = dossier(root, validators=(("v1", "family-b", "disagree"),), resolution=True)
    code, out = run("research", "check", d)
    expect(code == 0, out)


@case
def research_init_writes_the_skeleton_first_and_keeps_it(root):
    d = os.path.join(root, "r")
    code, out = run("research", "init", d, "--tier", "M", "--question", "q", "--author", "fam/deep")
    expect(code == 0 and os.path.isfile(os.path.join(d, "sources.json")), out)
    with open(os.path.join(d, "README.md"), "a") as fh:
        fh.write("kept\n")
    run("research", "init", d, "--tier", "M", "--question", "q", "--author", "fam/deep")
    expect(open(os.path.join(d, "README.md")).read().endswith("kept\n"), "init overwrote work")
    code, out = run("research", "check", d)
    expect(code == 1, "an empty skeleton passed")
    plan = json.loads(run("research", "plan", "--tier", "L", "--json")[1])
    roles = [r["role"] for r in plan["roles"]]
    expect(roles == ["scout", "decider", "validator", "merge"], roles)


@case
def the_order_is_spec_then_board_then_build(root):
    spec = write(root, "2026-11-21-export-design.md", S_SPEC.format(ledger=LEDGER))
    board = write(root, "backlog.md", "| B-1 | export | planned |\n")
    code, out = run("gate", spec, "--board", board)
    expect(code == 1 and "spec, then board, then build" in out, out)
    write(root, "backlog.md", "| B-1 | export, spec 2026-11-21-export-design | planned |\n")
    plan = write(root, "plan.md", "Builds 2026-11-21-export-design.\n")
    code, out = run("gate", spec, "--board", board, "--plan", plan)
    expect(code == 0, out)


class FakeModel:
    """An OpenAI-compatible endpoint on localhost that records what it was sent."""

    def __init__(self, status=200, content=None):
        seen = self.seen = []
        answer = content if content is not None else json.dumps(
            {"verdict": "partial", "evidence": "S1 holds; the refutation test is vague",
             "gaps": ["name the page that would fetch on open"]})

        class H(BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers["Content-Length"])).decode()
                seen.append({"path": self.path, "auth": self.headers.get("Authorization"),
                             "body": body})
                out = json.dumps({"model": "fake/validator", "usage": {"total_tokens": 9},
                                  "choices": [{"message": {"content": answer}}]}).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(out)

            def log_message(self, *a):
                pass

        self.server = HTTPServer(("127.0.0.1", 0), H)
        self.url = "http://127.0.0.1:%d/v1" % self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


KEY = {"SPEC_PROTOCOL_API_KEY": "planted-key-not-a-secret"}


@case
def a_validator_of_another_family_is_called_and_recorded(root):
    d = dossier(root, validators=())
    code, out = run("research", "check", d)
    expect(code == 1 and "validator" in out, "a dossier with no validator passed: " + out)
    fake = FakeModel()
    try:
        code, out = run("research", "validate", d, "--model", "fake/validator",
                        "--family", "family-b", "--endpoint", fake.url, env=KEY)
    finally:
        fake.close()
    expect(code == 0 and "partial" in out, out)
    expect(fake.seen and fake.seen[0]["path"] == "/v1/chat/completions", fake.seen)
    expect(fake.seen[0]["auth"] == "Bearer planted-key-not-a-secret", "the key was not sent as a header")
    expect("planted-key" not in fake.seen[0]["body"] and "planted-key" not in out, "the key leaked")
    text = open(os.path.join(d, "README.md")).read()
    expect("| fake/validator | family-b | partial |" in text, text)
    rec = json.load(open(os.path.join(d, "validation", "family-b-fake-validator.json")))
    expect(rec["gaps"] and rec["usage"] == {"total_tokens": 9}, rec)
    rows = [x for x in spend_rows() if x["route"] == "research.validate" and x["model"] == "fake/validator"]
    expect(rows and rows[-1]["usd"] is None and rows[-1]["source"] == "unknown",
           "the validator's call is not in the spend ledger, or a missing cost became zero: %r" % rows)
    code, out = run("research", "check", d)
    expect(code == 0, "the recorded verdict did not count: " + out)


@case
def the_validator_is_blind_and_the_authors_family_never_counts(root):
    d = dossier(root, validators=(("first-model", "family-c", "disagree"),), resolution=True)
    code, out = run("research", "validate", d, "--model", "m", "--family", "family-b", "--dry-run")
    expect(code == 0 and "Embed the snapshot" in out, out)
    expect("first-model" not in out and "weaker" not in out,
           "the prompt shows another validator's verdict or the Resolution")
    # B-176: the author's family is recorded with a warning and never counts toward the minimum.
    d = dossier(os.path.join(root, "same"), validators=())
    fake = FakeModel()
    try:
        code, out = run("research", "validate", d, "--model", "m", "--family", "Family-A",
                        "--endpoint", fake.url, env=KEY)
    finally:
        fake.close()
    expect(code == 0 and "WARN" in out and "author" in out,
           "the author's family was refused or recorded silently: " + out)
    rec = json.load(open(os.path.join(d, "validation", "family-a-m.json")))
    expect(rec.get("same_family") is True, "the record does not say same family: %r" % rec)
    code, out = run("research", "check", d)
    expect(code == 1 and "validator" in out, "a same-family validator met the minimum: " + out)


@case
def a_failed_call_records_no_verdict(root):
    d = dossier(root, validators=())
    before = open(os.path.join(d, "README.md")).read()
    for status, content in ((500, None), (200, "I think it is fine."),
                            (200, '{"verdict": "looks good"}')):
        fake = FakeModel(status, content)
        try:
            code, out = run("research", "validate", d, "--model", "m", "--family", "family-b",
                            "--endpoint", fake.url, env=KEY)
        finally:
            fake.close()
        expect(code == 1 and "no verdict recorded" in out, out)
    code, out = run("research", "validate", d, "--model", "m", "--family", "family-b",
                    "--endpoint", "http://127.0.0.1:9", env={"SPEC_PROTOCOL_API_KEY": ""})
    expect(code == 1 and "SPEC_PROTOCOL_API_KEY" in out, out)
    expect(open(os.path.join(d, "README.md")).read() == before, "a failed call changed the dossier")
    expect(not os.path.exists(os.path.join(d, "validation")), "a failed call wrote a record")


@case
def the_loop_is_at_hand_in_its_order(root):
    code, out = run("loop", "--json")
    data = json.loads(out)
    names = [s["name"] for s in data["steps"]]
    expect(code == 0 and names == ["analysis", "definition", "research planning", "research",
                                   "verification"], out)
    expect(all(s["who"] and s["takes"] and s["leaves"] and s["stages"] for s in data["steps"]),
           "a step without who, takes, leaves or stages")
    expect("other agents than the author" in data["steps"][3]["who"], "research is not other agents'")
    expect("other families" in data["steps"][4]["who"], "verification names no other family")
    code, out = run("loop")
    expect(code == 0 and out.index("1. analysis") < out.index("5. verification"), out)


@case
def money_by_role_meanings_on_tokens_text_on_the_subscription(root):
    # The owner, 2026-11-23: the thinker decides the meanings by tokens, a writer on the
    # subscription writes the text, validators answer by tokens one call each.
    code, out = run("loop", "--json")
    data = json.loads(out)
    rule = data["author"]
    expect("meanings" in rule and "subscription" in rule and "one call each" in rule, rule)
    expect("meanings.py write" in data["steps"][1]["who"] and "writer" in data["steps"][1]["who"],
           data["steps"][1]["who"])
    code, out = run("research", "plan", "--tier", "M", "--json")
    roles = {r["role"]: r for r in json.loads(out)["roles"]}
    expect(roles["decider"]["tier"] == "thinker", "the decider is not the thinker: %r" % roles["decider"])
    expect(roles["scout"]["route"] == "subscription", roles["scout"])
    expect(roles["validator"]["route"].startswith("tokens, one call"), roles["validator"])
    expect("another agent than the author" in roles["scout"]["does"], roles["scout"]["does"])


def main():
    for fn in CASES:
        root = tempfile.mkdtemp(prefix="specproto-")
        try:
            fn(root)
            print(f"ok   {fn.__name__}")
        except AssertionError as exc:
            FAILS.append(fn.__name__)
            print(f"FAIL {fn.__name__}: {exc}")
        finally:
            shutil.rmtree(root, ignore_errors=True)
    if FAILS:
        print(f"FAIL: spec_protocol.py, {len(FAILS)} of {len(CASES)} cases")
        return 1
    print(f"PASS: spec_protocol.py, {len(CASES)} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
