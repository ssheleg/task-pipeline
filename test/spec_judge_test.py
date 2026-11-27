#!/usr/bin/env python3
"""spec_judge.py and the spec gate: the S0 acceptance facts 1-9 and 12, offline.

The judge model is a local stub that answers what each case needs and records every
request, so the prompt (round 2's diff and questions) is checked as sent. No network.
"""
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline")
TOOL = os.path.join(SKILL, "scripts", "spec_judge.py")
PROTO = os.path.join(SKILL, "scripts", "spec_protocol.py")
HOOK = os.path.join(ROOT, "plugins", "task-pipeline", "hooks", "build-gate.sh")
FIX = os.path.join(ROOT, "test", "fixtures", "spec-judge")
SEEDS = os.path.join(SKILL, "tests", "judge-seeds")
sys.path.insert(0, os.path.join(SKILL, "scripts"))
import spec_judge  # noqa: E402

FAILS = []


CASES = 0


def it(name, fn):
    global CASES
    CASES += 1
    try:
        fn()
        print("ok   " + name)
    except AssertionError as e:
        FAILS.append(name)
        print("FAIL " + name + ": " + str(e))


# ---------------------------------------------------------------- the stub judge

class Stub:
    def __init__(self):
        self.replies, self.requests = [], []
        stub = self

        class H(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                n = int(self.headers.get("Content-Length") or 0)
                stub.requests.append(json.loads(self.rfile.read(n)))
                reply = stub.replies.pop(0) if stub.replies else verdict()
                if reply == "truncate":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", "5000")
                    self.end_headers()
                    self.wfile.write(b'{"id": "gen-cut", "choices": [')
                    return
                body = json.dumps({"id": "gen-%d" % len(stub.requests), "model": "stub/judge",
                                   "choices": [{"message": {"content": json.dumps(reply)},
                                                "finish_reason": "stop"}],
                                   "usage": {"prompt_tokens": 100, "completion_tokens": 50,
                                             "cost": 0.0123}}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a):
                pass

        self.server = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = "http://127.0.0.1:%d" % self.server.server_port


def verdict(scores=2, questions=(), auto=(), previous=(), **over):
    s = {d: scores for d in spec_judge.CORE}
    s.update(over)
    return {"questions": list(questions), "scores": s, "auto_fail": list(auto),
            "previous": list(previous), "summary": "stub"}


STUB = Stub()
TMP = tempfile.mkdtemp(prefix="spec-judge-test-")
HOME = os.path.join(TMP, "home")
os.makedirs(HOME)


def models(*entries):
    p = os.path.join(TMP, "models-%d.json" % len(os.listdir(TMP)))
    json.dump({"schema": "judge-models/1", "endpoint": STUB.url,
               "models": [{"model": m, "family": f, "rank": r} for m, f, r in entries]}, open(p, "w"))
    return p


CROSS = models(("other/judge", "other", 100), ("author/judge", "author", 50))
SAME = models(("author/judge", "author", 100))


def env():
    return dict(os.environ, HOME=HOME, OPENROUTER_API_KEY="test-key", TASK_PIPELINE_SPEND_LOG=
                os.path.join(TMP, "spend.jsonl"), TASK_PIPELINE_JUDGE_MODELS="",
                TASK_PIPELINE_JUDGE_RUBRIC="")


def run(*args, models_file=CROSS):
    a = [sys.executable, TOOL] + list(args)
    if args and args[0] in ("check", "calibrate") and "--verify" not in args and models_file:
        a += ["--models", models_file]
    r = subprocess.run(a, capture_output=True, text=True, env=env(), cwd=TMP)
    return r.returncode, r.stdout + r.stderr


def new_spec(name, size="S", seed="01-phase-one-only", author="author"):
    d = os.path.join(TMP, name)
    shutil.copytree(os.path.join(SEEDS, seed), d)
    meta = json.load(open(os.path.join(d, "spec.json")))
    meta.update(size=size, author_family=author)
    json.dump(meta, open(os.path.join(d, "spec.json"), "w"))
    os.remove(os.path.join(d, "expect.json"))
    return d


def revise(path, line):
    """An edit before `## Judge record`: an edit inside it is not an edit of the spec."""
    t = open(path).read()
    open(path, "w").write(t.replace("## Boundaries\n", "## Boundaries\n\n%s\n" % line, 1))


def round_file(d, n):
    return json.load(open(os.path.join(d, "judge", "round-%d.json" % n)))


# ---------------------------------------------------------------- fact 1: the template

MENTION = os.path.join(FIX, "mentions-judge-record.md")


def first_occurrence_cut(text):
    """The defect that cut a real spec at its fact 7: a search for the FIRST `## Judge record`."""
    i = text.find("## Judge record")
    return text[:i] + "## Judge record\n\n| Round | Judge |\n|---|---|\n| 1 | x |\n"


def proto(path):
    r = subprocess.run([sys.executable, PROTO, "check", path], capture_output=True, text=True)
    return r.returncode, r.stdout


def fact1_template_check():
    code, out = proto(MENTION)
    assert code == 0, "a whole spec in the template must pass: " + out
    cut = os.path.join(TMP, "cut.md")
    open(cut, "w").write(first_occurrence_cut(open(MENTION).read()))
    code, out = proto(cut)
    assert code == 1 and "section `Acceptance` missing" in out, \
        "the copy cut at its prose mention must fail on its lost sections: " + out
    text = open(MENTION).read()
    for sec in ("## Boundaries\n", "## Glossary\n"):
        p = os.path.join(TMP, "missing.md")
        open(p, "w").write(text.replace(sec, "## Renamed\n"))
        code, out = proto(p)
        assert code == 1 and sec.strip("#\n ") in out, "a missing %s passed" % sec


def fact1_header_values():
    text = open(MENTION).read()
    p = os.path.join(TMP, "badsize.md")
    open(p, "w").write(text.replace("| size | S |", "| size | XL |"))
    code, out = proto(p)
    assert code == 1 and "header `size`" in out, out


def an_edit_inside_the_judge_record_is_not_an_edit():
    text = open(MENTION).read()
    assert spec_judge.content_hash(text + "\nnotes the tool wrote\n") == spec_judge.content_hash(text)


# ---------------------------------------------------------------- fact 7: the hash

def fact7_hash():
    text = open(MENTION).read()
    h = spec_judge.content_hash(text)
    kept = spec_judge.strip_judge_record(text)
    assert "The record of a judgement" in kept and "## Acceptance" in kept, \
        "the prose mention of `## Judge record` cut the spec (the first-occurrence defect)"
    appended = text.rstrip() + "\n\n| Round | Judge |\n|---|---|\n| 1 | x |\n"
    assert spec_judge.content_hash(appended) == h, "appending the judge record changed the hash"
    edited = text.replace("newest first", "newest first!", 1)
    assert edited != text and spec_judge.content_hash(edited) != h, "editing one character kept the hash"
    fenced = text.replace("## Glossary\n", "```\n## Judge record\n```\n\n## Glossary\n", 1)
    assert "## Glossary" in spec_judge.strip_judge_record(fenced), "a fenced heading cut the spec"


# ---------------------------------------------------------------- facts 3, 12: one round on file

def fact3_round_written():
    d = new_spec("f3")
    STUB.replies = [verdict(questions=[{"id": "Q1", "text": "which order?", "blocking": False,
                                        "fix": "say it"}])]
    code, out = run("check", d)
    assert code == 0, out
    r = round_file(d, 1)
    assert set(r["scores"]) == set(spec_judge.CORE), r["scores"]
    assert r["verdict"] == "pass" and r["questions"][0]["id"] == "Q1"
    assert r["family"] == "other" and r["author_family"] == "author" and r["cross_family"] is True
    assert r["cost_usd"] == 0.0123 and r["generation_id"].startswith("gen-"), "fact 12: cost or id missing"
    assert r["spec_sha256"] == spec_judge.content_hash(open(os.path.join(d, "spec.md")).read())
    meta = json.load(open(os.path.join(d, "spec.json")))
    assert meta["status"] == "judged" and meta["judge"][0]["model"] == "other/judge", meta
    assert "## Judge record" in open(os.path.join(d, "spec.md")).read()
    booked = [json.loads(x) for x in open(os.path.join(TMP, "spend.jsonl"))]
    assert any(b["route"] == "spec.judge" and b["usd"] == 0.0123 for b in booked), "fact 12: not booked"
    code, out = run("check", d, "--verify")
    assert code == 0 and "judged" in out, out
    before = len(STUB.requests)
    code, out = run("check", d)
    assert code == 0 and len(STUB.requests) == before, "a content already judged pass was judged again"


def the_verdict_is_computed_not_taken():
    d = new_spec("computed")
    reply = verdict(finality=0)
    reply["verdict"] = "pass"
    STUB.replies = [reply]
    code, out = run("check", d)
    assert code == 1 and round_file(d, 1)["verdict"] == "fail", "a 0 score passed on the judge's word"
    d2 = new_spec("computed2")
    STUB.replies = [verdict(auto=[{"kind": "tbd", "text": "TBD in fact 3"}])]
    code, _ = run("check", d2)
    assert code == 1 and round_file(d2, 1)["verdict"] == "fail", "an automatic fail passed"
    d3 = new_spec("computed3")
    STUB.replies = [verdict(questions=[{"id": "Q1", "text": "x?", "blocking": True, "fix": "y"}])]
    code, _ = run("check", d3)
    assert code == 1 and round_file(d3, 1)["verdict"] == "pass-with-fixes"


# ---------------------------------------------------------------- fact 2: phase one only

def fact2_phase_one_fails():
    d = new_spec("f2", seed="01-phase-one-only")
    STUB.replies = [verdict(finality=0, questions=[{"id": "Q1", "text": "what is the finished export?",
                                                    "blocking": True, "fix": "describe it"}])]
    code, _ = run("check", d)
    r = round_file(d, 1)
    assert code == 1 and r["scores"]["finality"] == 0 and r["verdict"] == "fail"


# ---------------------------------------------------------------- fact 4: rounds and escalation

def fact4_rounds_and_escalation():
    d = new_spec("f4")
    block = lambda i: {"id": "Q%d" % i, "text": "question %d?" % i, "blocking": True, "fix": "fix %d" % i}
    STUB.replies = [verdict(questions=[block(1), block(2)])]
    assert run("check", d)[0] == 1
    p = os.path.join(d, "spec.md")
    revise(p, "A revision line.")
    n = len(STUB.requests)
    STUB.replies = [verdict(questions=[block(3)], previous=[{"id": "Q1", "state": "closed"},
                                                             {"id": "Q2", "state": "closed"}])]
    assert run("check", d)[0] == 1
    sent = STUB.requests[n]["messages"][0]["content"]
    assert "PREVIOUS ROUND QUESTIONS" in sent and "question 1?" in sent, "round 2 lacks the questions"
    assert "+A revision line." in sent, "round 2 lacks the diff"
    assert not os.path.exists(os.path.join(d, "judge", "escalation.json")), "escalated with one open"
    revise(p, "A second revision.")
    STUB.replies = [verdict(questions=[block(4)], previous=[{"id": "Q3", "state": "open"}])]
    code, out = run("check", d)
    assert code == 1 and round_file(d, 3)["cycle_round"] == 3
    esc = json.load(open(os.path.join(d, "judge", "escalation.json")))
    assert esc["title"].startswith("спека не прошла судью") and esc["open_questions"], esc
    assert json.load(open(os.path.join(d, "spec.json")))["status"] == "draft"
    n = len(STUB.requests)
    code, out = run("check", d)
    assert code == 1 and len(STUB.requests) == n, "a fourth round was called"
    code, out = run("check", d, "--new-cycle")
    assert code == 2, "--new-cycle without --reason was accepted"


def round3_only_for_one_blocker():
    d = new_spec("r3")
    block = lambda i: {"id": "Q%d" % i, "text": "q%d?" % i, "blocking": True, "fix": "f"}
    STUB.replies = [verdict(questions=[block(1)])]
    run("check", d)
    revise(os.path.join(d, "spec.md"), "rev")
    STUB.replies = [verdict(questions=[block(2), block(3)])]
    code, out = run("check", d)
    assert code == 1 and os.path.exists(os.path.join(d, "judge", "escalation.json")), \
        "round 2 with two blockers must not get a third round"


# ---------------------------------------------------------------- fact 5: who judges

def fact5_family():
    d = new_spec("f5")
    STUB.replies = [verdict()]
    run("check", d)
    assert round_file(d, 1)["family"] != json.load(open(os.path.join(d, "spec.json")))["author_family"]
    d2 = new_spec("f5deg")
    STUB.replies = [verdict()]
    code, out = run("check", d2, models_file=SAME)
    assert code == 0 and "judged-degraded" in out, "one provider, size S: " + out
    assert json.load(open(os.path.join(d2, "spec.json")))["status"] == "judged-degraded"
    code, out = run("check", d2, "--verify", "--require-cross-family")
    assert code == 1, "the estate flag let a same-family verdict through"
    d3 = new_spec("f5L", size="L")
    code, out = run("check", d3, models_file=SAME)
    assert code == 3, "size L with one provider must name the missing judge: " + out
    rub = os.path.join(TMP, "estate-rubric.md")
    open(rub, "w").write(open(os.path.join(SKILL, "references", "judge-rubric.md")).read()
                         .replace("require_cross_family: false", "require_cross_family: true"))
    code, _ = run("check", d2, "--verify", "--rubric", rub)
    assert code == 1, "the estate rubric's flag was ignored"


def a_reply_cut_mid_body_is_a_failed_call():
    d = new_spec("cut")
    STUB.replies = ["truncate"]
    code, out = run("check", d)
    assert code == 1 and "IncompleteRead" in out and "Traceback" not in out, out
    assert not os.path.isdir(os.path.join(d, "judge")), "a cut reply left a round on file"


def placeholders_are_never_called():
    d = new_spec("ph")
    shipped = os.path.join(SKILL, "references", "judge-models.json")
    code, out = run("check", d, models_file=shipped)
    assert code == 3 and "no judge model available" in out, out


def a_rubric_without_a_core_dimension_is_refused():
    d = new_spec("rub")
    rub = os.path.join(TMP, "org-rubric.md")
    open(rub, "w").write(open(os.path.join(SKILL, "references", "judge-rubric.md")).read()
                         .replace("dimensions: [clarity, completeness, testability, finality, consistency]",
                                  "dimensions: [clarity, completeness, testability, finality]"))
    code, out = run("check", d, "--rubric", rub)
    assert code == 2 and "consistency" in out, out
    rub2 = os.path.join(TMP, "org-rubric2.md")
    open(rub2, "w").write(open(os.path.join(SKILL, "references", "judge-rubric.md")).read()
                          .replace("extra_dimensions: []", "extra_dimensions: [privacy]"))
    STUB.replies = [verdict(privacy=2)]
    code, out = run("check", d, "--rubric", rub2)
    assert code == 0 and "privacy" in round_file(d, 1)["scores"], out


# ---------------------------------------------------------------- fact 6: design review by size

def fact6_design_review():
    d = new_spec("f6", size="M")
    STUB.replies = [verdict()]
    code, out = run("check", d)
    assert code == 1 and "validator" in out, "an M spec reached judged without its design review"
    vd = os.path.join(d, "review", "validators")
    os.makedirs(vd)
    json.dump({"family": "author", "verdict": "agree"}, open(os.path.join(vd, "same.json"), "w"))
    assert run("check", d, "--verify")[0] == 1, "an author-family validator was counted"
    json.dump({"family": "third", "verdict": "agree"}, open(os.path.join(vd, "third.json"), "w"))
    code, out = run("check", d, "--verify")
    assert code == 1 and "council" in out, out
    os.makedirs(os.path.join(d, "review", "council"))
    json.dump({"ruling": {"verdict": "pass"}}, open(os.path.join(d, "review", "council", "judge.json"), "w"))
    code, out = run("check", d, "--verify")
    assert code == 0, out
    meta = json.load(open(os.path.join(d, "spec.json")))
    meta["size"] = "L"
    json.dump(meta, open(os.path.join(d, "spec.json"), "w"))
    code, out = run("check", d, "--verify")
    assert code == 1 and "two families" in out, "size L passed with one validator family"


# ---------------------------------------------------------------- fact 7 end to end

def fact7_edit_voids():
    d = new_spec("f7")
    STUB.replies = [verdict()]
    assert run("check", d)[0] == 0
    assert run("check", d, "--verify")[0] == 0
    p = os.path.join(d, "spec.md")
    revise(p, "One more sentence.")
    code, out = run("check", d, "--verify")
    assert code == 1 and "draft" in out, "an edited spec still verified"


# ---------------------------------------------------------------- fact 8: CI and the hook

def git(repo, *a):
    return subprocess.run(["git", "-C", repo] + list(a), capture_output=True, text=True,
                          env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t"))


def fact8_spec_gate():
    repo = os.path.join(TMP, "repo")
    os.makedirs(os.path.join(repo, "docs", "specs"))
    git(repo, "init", "-q")
    d = new_spec(os.path.join("repo", "docs", "specs", "2026-11-28-export"))
    STUB.replies = [verdict()]
    assert run("check", d)[0] == 0
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "spec")
    sha = git(repo, "rev-parse", "HEAD").stdout.strip()
    sid = json.load(open(os.path.join(d, "spec.json")))["id"]
    body = os.path.join(TMP, "body.md")
    open(body, "w").write("Adds the export.\n\nSpec: %s@%s\n" % (sid, sha))
    code, out = run("gate", "--pr-body", body, "--repo", repo)
    assert code == 0, out
    open(body, "w").write("Adds the export, no trailer.\n")
    code, out = run("gate", "--pr-body", body, "--repo", repo)
    assert code == 1 and "trailer" in out, "a pull request without the trailer passed"
    open(body, "w").write("Spec: no-such-spec@%s\n" % sha)
    assert run("gate", "--pr-body", body, "--repo", repo)[0] == 1


def hook(project, path, ledger):
    os.makedirs(os.path.join(project, ".task-pipeline"), exist_ok=True)
    open(os.path.join(project, ".task-pipeline", "run.md"), "w").write(ledger)
    r = subprocess.run(["bash", HOOK], input=json.dumps({
        "hook_event_name": "PreToolUse", "tool_name": "Write",
        "tool_input": {"file_path": os.path.join(project, path)}}),
        env=dict(env(), CLAUDE_PROJECT_DIR=project), capture_output=True, text=True)
    out = (r.stdout or "").strip()
    return json.loads(out)["hookSpecificOutput"] if out else None


NEW_RUN = "Run: `export` · started `2026-11-28` · module map: none\n\nstage: 3 spec\n"
BUILD = "stage: 5 build — gate auto\n"


def fact8_hook_denies():
    p = os.path.join(TMP, "proj8")
    os.makedirs(p)
    json.dump({"stages": [{"id": 5, "state": "build"}]}, open(os.path.join(p, "pipeline.json"), "w"))
    res = hook(p, "src/export.py", NEW_RUN)
    assert res and res["permissionDecision"] == "deny", "a post-S0 run with no spec was not denied"
    for ok in ("docs/specs/x/spec.md", ".task-pipeline/run.md", "README.md", "NOTES.md"):
        assert hook(p, ok, NEW_RUN) is None, "%s is the pipeline's own artefact" % ok
    d = new_spec(os.path.join("proj8", "docs", "specs", "s"))
    res = hook(p, "src/export.py", NEW_RUN + "spec: docs/specs/s\n" + BUILD)
    assert res and res["permissionDecision"] == "deny" and "does not verify" in res["permissionDecisionReason"]
    STUB.replies = [verdict()]
    assert run("check", d)[0] == 0
    assert hook(p, "src/export.py", NEW_RUN + "spec: docs/specs/s\n" + BUILD) is None, \
        "a verified spec in the build stage was still refused"
    res = hook(p, "src/export.py", NEW_RUN + "spec: docs/specs/s\n")
    assert res and res["permissionDecision"] == "ask", "judged but before build: the old question"


def a_legacy_run_keeps_the_question():
    p = os.path.join(TMP, "legacy")
    os.makedirs(p)
    led = "Run: `old` · started `2026-11-20`\n\nstage: 3 spec\n"
    json.dump({"stages": [{"id": 5, "state": "build"}]}, open(os.path.join(p, "pipeline.json"), "w"))
    res = hook(p, "src/a.py", led)
    assert res and res["permissionDecision"] == "ask", "a run in flight before S0 was stranded"


def fact9_incident_needs_an_s_spec():
    p = os.path.join(TMP, "incident")
    os.makedirs(p)
    led = ("Run: `hotfix` · started `2026-12-01` · kind incident\n\nstage: 5 build\n")
    res = hook(p, "src/fix.py", led)
    assert res and res["permissionDecision"] == "deny" and "S spec" in res["permissionDecisionReason"], \
        "an incident started building without an S spec"


def a_malformed_payload_is_silent():
    p = os.path.join(TMP, "malformed")
    os.makedirs(os.path.join(p, ".task-pipeline"))
    open(os.path.join(p, ".task-pipeline", "run.md"), "w").write(NEW_RUN)
    r = subprocess.run(["bash", HOOK], input="not json", env=dict(env(), CLAUDE_PROJECT_DIR=p),
                       capture_output=True, text=True)
    assert r.returncode == 0 and not r.stdout.strip()


# ---------------------------------------------------------------- fact 12: calibration

def fact12_calibration():
    out = os.path.join(TMP, "calib.json")
    STUB.replies = [verdict(finality=0)] + [verdict(scores=1, auto=[{"kind": "tbd", "text": "x"}])] * 9
    code, text = run("calibrate", "--out", out)
    rec = json.load(open(out))
    assert code == 0 and rec["caught"] == 10 and rec["seeds"] == 10, text
    assert all(r["generation_id"] for r in rec["results"])
    STUB.replies = [verdict()] * 10
    code, text = run("calibrate", "--out", out)
    assert code == 1 and json.load(open(out))["caught"] == 0, "a judge that passes everything calibrated"


def the_shipped_files():
    rub = spec_judge.load_rubric(os.path.join(SKILL, "references", "judge-rubric.md"))
    assert rub["dimensions"] == list(spec_judge.CORE) and rub["require_cross_family"] is False
    ms, _ = spec_judge.load_models(os.path.join(SKILL, "references", "judge-models.json"))
    assert ms == [], "the shipped judge list must name roles only"
    seeds = [x for x in os.listdir(SEEDS) if os.path.isfile(os.path.join(SEEDS, x, "expect.json"))]
    assert len(seeds) == 10, "ten seeded specs, found %d" % len(seeds)


def init_writes_a_template_spec():
    d = os.path.join(TMP, "init", "docs", "specs", "2026-11-28-x")
    code, out = run("init", d, "--id", "x", "--author-family", "author")
    assert code == 0, out
    r = subprocess.run([sys.executable, PROTO, "check", os.path.join(d, "spec.md")], capture_output=True, text=True)
    assert r.returncode == 1 and "placeholder" in r.stdout, "an unfilled template passed the check"


it("fact 1: the template check passes S0 and fails a missing section", fact1_template_check)
it("fact 1: header values come from the template's lists", fact1_header_values)
it("fact 7: the hash leaves out the judge record, and only it", fact7_hash)
it("an edit inside the judge record is not an edit of the spec", an_edit_inside_the_judge_record_is_not_an_edit)
it("fact 3 and 12: a round writes scores, questions, verdict, cost and id", fact3_round_written)
it("the verdict is computed from what the judge listed", the_verdict_is_computed_not_taken)
it("fact 2: a phase-one spec gets finality 0 and fail", fact2_phase_one_fails)
it("fact 4: rounds carry the diff; a third failure escalates and stays draft", fact4_rounds_and_escalation)
it("a third round only for one open blocker", round3_only_for_one_blocker)
it("fact 5: another family judges; one provider gives judged-degraded", fact5_family)
it("a reply cut mid-body is a failed call, never a traceback", a_reply_cut_mid_body_is_a_failed_call)
it("placeholders are never called", placeholders_are_never_called)
it("a rubric without a core dimension is refused", a_rubric_without_a_core_dimension_is_refused)
it("fact 6: M and L owe validators of other families and a council ruling", fact6_design_review)
it("fact 7: an edit voids the verdict", fact7_edit_voids)
it("fact 8: spec-gate needs the trailer and a verified spec at that commit", fact8_spec_gate)
it("fact 8: the build gate denies a product edit without a verified spec", fact8_hook_denies)
it("a run in flight before S0 keeps the old question", a_legacy_run_keeps_the_question)
it("fact 9: an incident cannot build without an S spec", fact9_incident_needs_an_s_spec)
it("a malformed payload is silent", a_malformed_payload_is_silent)
it("fact 12: calibration counts the seeds caught", fact12_calibration)
it("the shipped rubric, judge list and seeds", the_shipped_files)
it("init writes the template; the check refuses it unfilled", init_writes_a_template_spec)

shutil.rmtree(TMP, ignore_errors=True)
if FAILS:
    print("FAIL: spec_judge.py, %d case(s): %s" % (len(FAILS), ", ".join(FAILS)))
    sys.exit(1)
print("PASS: spec_judge.py, %d cases" % CASES)
