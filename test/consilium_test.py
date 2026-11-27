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
        if model in ("cut/model", "cutalways/model"):
            CUTS[model] = CUTS.get(model, 0) + 1
            if model == "cutalways/model" or CUTS[model] == 1:
                # A reply cut mid-body: http.client.IncompleteRead in the reader (fb909e59).
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", "5000")
                self.end_headers()
                self.wfile.write(b'{"model": "x", "choices": [')
                return
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
        usage = {"prompt_tokens": 10, "completion_tokens": 5, "cost": 0.5}
        if model == "byok/model":  # OpenRouter's shape for a call billed to our own key (measured 2026-11-23)
            usage = {"prompt_tokens": 10, "completion_tokens": 5, "cost": 0, "is_byok": True,
                     "cost_details": {"upstream_inference_cost": 0.25}}
        out = {"model": model, "choices": [{"message": {"content": text}, "finish_reason": "stop"}]}
        if model != "nousage/model":
            out["usage"] = usage
        data = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


CUTS = {}
SPEND_LOG = pathlib.Path(tempfile.mkdtemp()) / "spend.jsonl"
_TREES.append(SPEND_LOG.parent)


def spend_rows():
    return [json.loads(x) for x in SPEND_LOG.read_text().splitlines()] if SPEND_LOG.exists() else []


def run(args, env_extra=None):
    env = dict(os.environ, TASK_PIPELINE_SPEND_LOG=str(SPEND_LOG), TASK_PIPELINE_TASK="", CONSILIUM_RETRY_PAUSE="0",
               TASK_PIPELINE_CONSILIUM_OVERRIDE="off")
    env.update(env_extra or {})
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
    ok(all(c.get("reused") for c in led["calls"] if c["id"] != "judge"), "the reused verdicts are marked")
    ok(abs(led["spent_usd"] - 2.5) < 1e-9, "judge-only keeps the panel's paid spend in the round: %s" % led["spent_usd"])

    # Money: one token call per panelist, BYOK read from its upstream cost, an unknown cost never zero,
    # a subscription panelist never called, every paid call in the spend ledger with its task.
    money = dict(cfg, panel=[{"id": "a", "model": "v1/a", "family": "f1"},
                             {"id": "byok", "model": "byok/model", "family": "f2"},
                             {"id": "nu", "model": "nousage/model", "family": "f3"},
                             {"id": "sub", "model": "session/opus", "family": "f4", "route": "subscription"}])
    (tmp / "money.json").write_text(json.dumps(money))
    imp = tmp / "sub-verdict.json"
    imp.write_text('{"verdict": "pass", "score": 8, "summary": "s", "findings": []}')
    before, n = len(spend_rows()), len(SEEN)
    r = run(["review", "--doc", str(doc), "--brief", str(brief), "--out", str(tmp / "money"), "--config",
             str(tmp / "money.json"), "--endpoint", endpoint, "--key-env", "CONSILIUM_TEST_KEY", "--task", "T-42",
             "--import", "sub=" + str(imp)], {"CONSILIUM_TEST_KEY": "k"})
    ok(r.returncode in (0, 1), "the money round runs: " + r.stderr[-400:])
    called = [b["model"] for b in SEEN[n:]]
    ok("session/opus" not in called, "a subscription panelist is never called by tokens")
    ok(all(called.count(m) == 1 for m in ("v1/a", "byok/model", "nousage/model")), "one token call per validator: %s" % called)
    ml = json.loads((tmp / "money" / "round-1" / "ledger.json").read_text())
    by = {c["id"]: c for c in ml["calls"]}
    ok(abs(by["byok"]["cost"] - 0.25) < 1e-9 and by["byok"]["cost_source"] == "byok", "BYOK cost is the upstream cost")
    ok(by["nu"]["cost_known"] is False and ml["unknown_cost_calls"] == 1, "a call without usage is unknown, not zero")
    ok(by["sub"]["parsed"] and by["sub"]["cost_source"] == "subscription", "the imported verdict counts, at no token cost")
    rows = spend_rows()[before:]
    ok(len(rows) == 4 and all(x["task"] == "T-42" for x in rows), "three panel calls and the judge in the ledger, booked to the task")
    ok({x["route"] for x in rows} == {"consilium.review.panel", "consilium.review.judge"}, "routes named")
    ok([x["usd"] for x in rows if x["model"] == "nousage/model"] == [None], "the ledger keeps the unknown cost unknown")
    r = run(["review", "--doc", str(doc), "--brief", str(brief), "--out", str(tmp / "money2"), "--config",
             str(tmp / "money.json"), "--endpoint", endpoint, "--key-env", "CONSILIUM_TEST_KEY"], {"CONSILIUM_TEST_KEY": "k"})
    sl = json.loads((tmp / "money2" / "round-1" / "ledger.json").read_text())
    ok(any(c["id"] == "sub" and "--import" in c.get("error", "") for c in sl["calls"]),
       "a subscription panelist without its verdict is named, never called")
    r = run(["review", "--doc", str(doc), "--brief", str(brief), "--out", str(tmp / "money3"), "--config",
             str(tmp / "money.json"), "--endpoint", endpoint, "--key-env", "CONSILIUM_TEST_KEY", "--import", "zz=" + str(imp)],
            {"CONSILIUM_TEST_KEY": "k"})
    ok(r.returncode == 2, "an import naming no panelist is refused")

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

    # fb909e59: a reply cut mid-body (IncompleteRead) is retried once; cut twice it is one
    # failed panelist, and the round still reaches the judge with the others.
    cut_cfg = dict(cfg, panel=[{"id": "a", "model": "v1/a", "family": "f1"},
                               {"id": "b", "model": "v2/b", "family": "f2"},
                               {"id": "c", "model": "cut/model", "family": "f3"},
                               {"id": "d", "model": "cutalways/model", "family": "f4"},
                               {"id": "e", "model": "v5/e", "family": "f5"}])
    (tmp / "cut.json").write_text(json.dumps(cut_cfg))
    n = len(SEEN)
    r = run(["review", "--doc", str(doc), "--brief", str(brief), "--out", str(tmp / "cutout"), "--config",
             str(tmp / "cut.json"), "--endpoint", endpoint, "--key-env", "CONSILIUM_TEST_KEY"], {"CONSILIUM_TEST_KEY": "k"})
    ok("Traceback" not in r.stderr, "a cut reply never raises: " + r.stderr[-400:])
    rd = tmp / "cutout" / "round-1"
    ok((rd / "summary.md").exists() and (rd / "judge.json").exists(), "the round reaches the judge and its summary")
    c = json.loads((rd / "c.json").read_text())
    ok(c["verdict"] is not None and "IncompleteRead" in c["meta"].get("retried", ""), "one cut reply is retried once")
    d = json.loads((rd / "d.json").read_text())
    ok(d["verdict"] is None and d["meta"].get("status") == "failed" and "IncompleteRead" in d["meta"]["error"],
       "a reply cut twice is one failed panelist")
    ok(sum(1 for b in SEEN[n:] if b["model"] == "cutalways/model") == 2, "a failed transport is retried once, not more")
    ok(sum(1 for b in SEEN[n:] if b["model"] == "fail/model") == 0 and
       len([b for b in SEEN[n:] if "<council>" in b["messages"][-1]["content"]]) == 1, "one judge call")

    # parse_json reads balanced braces: a stray closing fence or a brace inside a string does
    # not hand back an inner object (handoff 2026-11-23).
    sys.path.insert(0, str(SCRIPT.parent))
    import consilium as cs
    outer = {"verdict": "pass", "findings": [{"id": "f1", "fix": "use {x} here"}]}
    stray = "Verdict:\n```json\n" + json.dumps(outer) + "\n```\n```\n"
    ok(cs.parse_json(stray) == outer, "a stray closing fence keeps the outer object")
    inner_first = "```json\n" + json.dumps(outer, indent=1) + "\n```"
    ok(cs.parse_json(inner_first) == outer, "a nested, indented object is read whole")
    edits = {"edits": [{"new": "an empty config: ``` {} ```"}], "verdict": "pass"}
    ok(cs.parse_json(json.dumps(edits) + "\n```") == edits,
       "a fence inside a string and a stray closing fence keep the outer object (the old regex returned {})")
    ok(cs.parse_json("no json here") is None, "prose is no object")

    # The host's own council (1.116.0): a named script runs in place of the shipped one, with
    # the same arguments and its exit code; `off`, a missing path or a run already inside it
    # keep the shipped council. The host file is read from $HOME, which these runs point at tmp.
    probe = tmp / "host-council.py"
    probe.write_text("import json, os, sys\n"
                     "open(os.environ['PROBE_OUT'], 'w').write(json.dumps({'argv': sys.argv[1:], "
                     "'inside': os.environ.get('TASK_PIPELINE_CONSILIUM_OVERRIDDEN')}))\n"
                     "sys.exit(7)\n")
    out = tmp / "probe.json"
    r = run(["panel", "--json"], {"TASK_PIPELINE_CONSILIUM_OVERRIDE": str(probe), "PROBE_OUT": str(out)})
    seen = json.loads(out.read_text()) if out.exists() else {}
    ok(r.returncode == 7 and seen.get("argv") == ["panel", "--json"], "the host's council gets the arguments and its exit code")
    ok(seen.get("inside") == "1", "the host's council runs marked, so a copy of this script does not call itself")
    home = tmp / "home"
    (home / ".config" / "task-pipeline").mkdir(parents=True)
    (home / ".config" / "task-pipeline" / "consilium.override").write_text(str(probe) + "\n")
    out.unlink()
    env = {k: v for k, v in os.environ.items() if k != "TASK_PIPELINE_CONSILIUM_OVERRIDE"}
    env.update(HOME=str(home), PROBE_OUT=str(out), TASK_PIPELINE_SPEND_LOG=str(SPEND_LOG))
    r = subprocess.run([sys.executable, str(SCRIPT), "panel"], capture_output=True, text=True, env=env, timeout=60)
    ok(r.returncode == 7 and out.exists(), "the host file names the host's council when the variable is unset")
    r = run(["panel"], {"TASK_PIPELINE_CONSILIUM_OVERRIDE": str(tmp / "absent.py"), "PROBE_OUT": str(out)})
    ok(r.returncode != 7 and "does not exist" in r.stderr, "a missing host council is reported and the shipped one runs")
    r = run(["panel"], {"TASK_PIPELINE_CONSILIUM_OVERRIDE": str(probe), "TASK_PIPELINE_CONSILIUM_OVERRIDDEN": "1"})
    ok(r.returncode != 7, "inside the host's council the shipped code never delegates again")
    r = run(["panel"], {"TASK_PIPELINE_CONSILIUM_OVERRIDE": str(SCRIPT)})
    ok(r.returncode != 7 and "does not exist" not in r.stderr, "an override naming this very script is the shipped council")

    srv.shutdown()
    print(f"consilium_test: {CASES} cases passed")


if __name__ == "__main__":
    main()
