#!/usr/bin/env python3
"""consilium.py: a blind panel, the judge rules last, the gate counts families and money.

Runs the real script as a process against a local fake OpenAI-compatible endpoint. No network,
no key of value. Every tree goes at exit.
"""
import atexit
import http.server
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import threading

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugins" / "task-pipeline" / "skills" / "task-pipeline" / "scripts" / "consilium.py"
_TREES = []
atexit.register(lambda: [shutil.rmtree(t, ignore_errors=True) for t in _TREES])
CASES = 0
SEEN = []


def ok(cond, what):
    global CASES
    CASES += 1
    if not cond:
        print(f"FAIL: {what}")
        sys.exit(1)


class Fake(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        SEEN.append(body)
        model = body["model"]
        user = body["messages"][-1]["content"]
        if model == "fail/model":
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"error":"boom"}')
            return
        if "<council>" in user:
            text = 'Ruling:\n```json\n{"verdict": "revise", "score": 6, "summary": "s", "accepted": [{"finding": "A:f1", "severity": "major", "why": "w", "change": "c"}], "rejected": [], "own": [], "dissent": "none"}\n```'
        elif model == "prose/model":
            text = "I think it is fine overall."
        else:
            text = '{"verdict": "revise", "score": 5, "summary": "s", "findings": [{"id": "f1", "severity": "major", "where": "2", "issue": "i", "fix": "x"}]}'
        out = {"model": model, "choices": [{"message": {"content": text}, "finish_reason": "stop"}],
               "usage": {"prompt_tokens": 10, "completion_tokens": 5, "cost": 0.5}}
        data = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run(args, env_extra=None):
    env = dict(os.environ, **(env_extra or {}))
    return subprocess.run([sys.executable, str(SCRIPT)] + args, capture_output=True, text=True, env=env, timeout=60)


def main():
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Fake)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    endpoint = f"http://127.0.0.1:{srv.server_address[1]}/v1"
    tmp = pathlib.Path(tempfile.mkdtemp())
    _TREES.append(tmp)
    doc = tmp / "spec.md"
    doc.write_text("# Spec\n\n## 2. Design\nDo the thing.\n")
    brief = tmp / "brief.md"
    brief.write_text("Build the thing safely.")
    cfg = {"schema": "consilium-config/1", "min_panel": 3, "max_usd_per_round": 10,
           "panel": [{"id": "a", "model": "v1/a", "family": "f1"}, {"id": "b", "model": "v2/b", "family": "f2"},
                     {"id": "c", "model": "v3/c", "family": "f3"}, {"id": "d", "model": "fail/model", "family": "f4"},
                     {"id": "e", "model": "prose/model", "family": "f5"}],
           "judge": {"model": "strong/judge", "family": "f6"}}
    cfg_path = tmp / "c.json"
    cfg_path.write_text(json.dumps(cfg))

    # The example config resolves and validates.
    r = run(["panel"], {"TASK_PIPELINE_CONSILIUM": ""})
    ok(r.returncode == 0 and "judge" in r.stdout, "the example config resolves: " + r.stderr)

    # No key: exit 2 before any call.
    n = len(SEEN)
    r = run(["review", "--doc", str(doc), "--brief", str(brief), "--out", str(tmp / "out"), "--config", str(cfg_path),
             "--endpoint", endpoint, "--key-env", "CONSILIUM_TEST_KEY"], {"CONSILIUM_TEST_KEY": ""})
    ok(r.returncode == 2 and len(SEEN) == n, "no key: exit 2 and no call")

    # A round: the panel is blind, failures and prose are recorded, the judge sees the council.
    r = run(["review", "--doc", str(doc), "--brief", str(brief), "--out", str(tmp / "out"), "--config", str(cfg_path),
             "--endpoint", endpoint, "--key-env", "CONSILIUM_TEST_KEY"], {"CONSILIUM_TEST_KEY": "k"})
    ok(r.returncode == 1, "a revise ruling exits 1: " + r.stderr)
    rd = tmp / "out" / "round-1"
    panel_calls = [b for b in SEEN[n:] if "<council>" not in b["messages"][-1]["content"]]
    judge_calls = [b for b in SEEN[n:] if "<council>" in b["messages"][-1]["content"]]
    ok(len(panel_calls) == 5 and len(judge_calls) == 1, "five panel calls and one judge call")
    ok(all('"findings"' not in b["messages"][-1]["content"].split("</artefact>")[0] for b in panel_calls),
       "no panelist sees another's verdict")
    ok(judge_calls[0]["model"] == "strong/judge", "the judge is the configured strongest model")
    ok("v1/a" not in judge_calls[0]["messages"][-1]["content"], "the judge sees panelists anonymised, not by model id")
    ledger = json.loads((rd / "ledger.json").read_text())
    ok(abs(ledger["spent_usd"] - 2.5) < 1e-9, "spend is the sum of the calls that answered: %s" % ledger["spent_usd"])
    d = json.loads((rd / "d.json").read_text())
    ok(d["verdict"] is None and "http 500" in d["meta"]["error"], "a failing panelist is recorded with its error")
    e = json.loads((rd / "e.json").read_text())
    ok(e["verdict"] is None and e["meta"]["parsed"] is False, "prose without JSON is no verdict")
    j = json.loads((rd / "judge.json").read_text())
    ok(j["ruling"]["verdict"] == "revise", "the fenced ruling is parsed")
    ok("Accepted" in (rd / "summary.md").read_text(), "the summary lists the accepted findings")

    # The gate: three verdicts of three families and a ruling pass; a stricter gate fails.
    r = run(["check", str(tmp / "out"), "--round", "1"])
    ok(r.returncode == 0 and r.stdout.startswith("PASS"), "check passes: " + r.stdout)
    r = run(["check", str(tmp / "out"), "--round", "1", "--min-panel", "4"])
    ok(r.returncode == 1, "check fails with fewer verdicts than required")

    # The cap: a round whose panel spends the cap skips the judge and fails the check.
    n = len(SEEN)
    r = run(["review", "--doc", str(doc), "--brief", str(brief), "--out", str(tmp / "out"), "--round", "2",
             "--config", str(cfg_path), "--endpoint", endpoint, "--key-env", "CONSILIUM_TEST_KEY", "--max-usd", "1"],
            {"CONSILIUM_TEST_KEY": "k"})
    ok(not any("<council>" in b["messages"][-1]["content"] for b in SEEN[n:]), "no judge call over the cap")
    ok("judge_skipped" in json.loads((tmp / "out" / "round-2" / "ledger.json").read_text()), "the skip is recorded")
    r = run(["check", str(tmp / "out"), "--round", "2"])
    ok(r.returncode == 1, "check fails without a ruling")

    # --judge-only reruns the judge over the saved verdicts and calls no panelist again.
    n = len(SEEN)
    r = run(["review", "--doc", str(doc), "--brief", str(brief), "--out", str(tmp / "out"), "--round", "1", "--judge-only",
             "--config", str(cfg_path), "--endpoint", endpoint, "--key-env", "CONSILIUM_TEST_KEY"], {"CONSILIUM_TEST_KEY": "k"})
    new = SEEN[n:]
    ok(len(new) == 1 and "<council>" in new[0]["messages"][-1]["content"], "judge-only makes exactly one call, the judge's")
    led = json.loads((rd / "ledger.json").read_text())
    ok(all(c.get("reused") for c in led["calls"] if c["id"] != "judge"), "the reused verdicts are marked and cost nothing")

    # The shipped example names roles, not models: a run on it refuses before any call.
    example = ROOT / "plugins" / "task-pipeline" / "skills" / "task-pipeline" / "assets" / "consilium.example.json"
    n = len(SEEN)
    r = run(["review", "--doc", str(doc), "--brief", str(brief), "--out", str(tmp / "out"), "--round", "3",
             "--config", str(example), "--endpoint", endpoint, "--key-env", "CONSILIUM_TEST_KEY"], {"CONSILIUM_TEST_KEY": "k"})
    ok(r.returncode == 2 and len(SEEN) == n and "roles, not models" in r.stderr, "placeholders are never called")

    # A config with two families is refused.
    bad = dict(cfg, panel=[{"id": "a", "model": "x", "family": "f1"}, {"id": "b", "model": "y", "family": "f1"},
                           {"id": "c", "model": "z", "family": "f2"}])
    (tmp / "bad.json").write_text(json.dumps(bad))
    r = run(["panel", "--config", str(tmp / "bad.json")])
    ok(r.returncode != 0 and "families" in (r.stderr + r.stdout), "fewer than three families is refused")

    srv.shutdown()
    print(f"consilium_test: {CASES} cases passed")


if __name__ == "__main__":
    main()
