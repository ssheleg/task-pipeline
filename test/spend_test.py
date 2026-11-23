#!/usr/bin/env python3
"""spend.py and meanings.py: every token call booked with its cost; meanings thought once, text written apart.

Runs the real scripts as processes; the model is a local fake OpenAI-compatible endpoint. No network, no key
of value, no read of the host's ledger or Observatory. Every tree goes at exit.
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
SCRIPTS = ROOT / "plugins" / "task-pipeline" / "skills" / "task-pipeline" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import spend  # noqa: E402

TMP = pathlib.Path(tempfile.mkdtemp(prefix="spend-test-"))
atexit.register(lambda: shutil.rmtree(TMP, ignore_errors=True))
LOG = TMP / "spend.jsonl"
CASES = 0
SEEN = []

MEANINGS = """# Meanings

## Goal and meaning
Exports reach the owner as CSV so that the month closes without a person copying rows.

## Key features
- One export per month.

## Decisions
- D1: CSV, not XLSX. Because every reader the owner uses opens CSV.

## Contracts
The export holds every row of the month once.

## Non-goals
No charts.

## Risks
A month with no rows; refuted if the owner needs formulas.

## Questions for the owner
none
"""


def ok(cond, what):
    global CASES
    CASES += 1
    if not cond:
        print("FAIL: " + what)
        sys.exit(1)


def run(script, args, env_extra=None, stdin=None):
    env = dict(os.environ, TASK_PIPELINE_SPEND_LOG=str(LOG), TASK_PIPELINE_TASK="")
    env.update(env_extra or {})
    return subprocess.run([sys.executable, str(SCRIPTS / script)] + args, capture_output=True, text=True, env=env,
                          timeout=60, input=stdin)


class Fake(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        SEEN.append(body)
        text = MEANINGS.split("\n", 2)[2] if body["model"] != "empty/model" else ""
        out = {"model": body["model"], "choices": [{"message": {"content": text}, "finish_reason": "stop"}],
               "usage": {"prompt_tokens": 100, "completion_tokens": 50, "cost": 0.75}}
        data = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    # cost_of: OpenRouter's shapes, measured 2026-11-23.
    ok(spend.cost_of({"cost": 0.5, "is_byok": False}) == (0.5, "openrouter"), "a plain cost")
    ok(spend.cost_of({"cost": 0, "is_byok": True, "cost_details": {"upstream_inference_cost": 0.014}}) == (0.014, "byok"),
       "BYOK: the upstream cost, never 0")
    ok(spend.cost_of({"cost": 0, "is_byok": True}) == (None, "unknown"), "BYOK without its upstream cost is unknown")
    ok(spend.cost_of(None) == (None, "unknown") and spend.cost_of({"total_tokens": 9}) == (None, "unknown"),
       "no usage, or usage without cost, is unknown")

    # record + summary: by route, model and task; unknown cost counted apart, never as zero.
    for args in (["--route", "consilium.review.judge", "--model", "m/judge", "--usd", "2.0", "--task", "T1"],
                 ["--route", "consilium.review.panel", "--model", "m/glm", "--usd", "0.01", "--task", "T1"],
                 ["--route", "research.validate", "--model", "m/x", "--source", "unknown", "--task", "T2"],
                 ["--route", "spec.writer", "--model", "m/opus", "--source", "subscription", "--task", "T1"]):
        r = run("spend.py", ["record"] + args)
        ok(r.returncode == 0, "record: " + r.stderr)
    rows = [json.loads(x) for x in LOG.read_text().splitlines()]
    ok(len(rows) == 4 and rows[2]["usd"] is None and rows[3]["usd"] == 0.0, "unknown is null, subscription is 0")
    r = run("spend.py", ["summary", "--json", "--estate", "off"])
    s = json.loads(r.stdout)
    ok(r.returncode == 0 and abs(s["day_tally"]["usd"] - 2.01) < 1e-9, "the day's known spend: %s" % r.stdout[:300])
    ok(s["day_tally"]["unknown_cost_calls"] == 1, "the unknown call is counted apart")
    ok(list(s["month_tally"]["by"]["route"])[0] == "consilium.review.judge", "routes sorted by spend")
    ok(s["estate"] == {"known": False} and "off" in s["estate_note"], "estate off is said, never zero")
    r = run("spend.py", ["summary", "--json", "--estate", "off", "--task", "T2"])
    ok(json.loads(r.stdout)["day_tally"]["calls"] == 1, "summary filters by task")
    r = run("spend.py", ["summary", "--estate", "off"])
    ok("not counted as zero" in r.stdout and "| consilium.review.judge | 1 | 2.00 |" in r.stdout, r.stdout)

    # The ceiling: the estate's month from an Observatory reading; warn at 80 %, exit 3, the owner's question.
    est = TMP / "estate.json"
    est.write_text(json.dumps({"month": "2026-11", "totalUsd": 4100.0, "fresh": True,
                               "unattributed": {"monthUsd": 10.0, "partial": False}}))
    r = run("spend.py", ["ceiling", "--estate", str(est), "--json"])
    c = json.loads(r.stdout)
    ok(r.returncode == 3 and c["warn"] and "Double the ceiling" in c["question"] and "Default" in c["question"],
       "80 %% of 5000 warns with one question and a default: " + r.stdout)
    est.write_text(json.dumps({"month": "2026-11", "totalUsd": 1075.6, "unattributed": {"monthUsd": None, "partial": True}}))
    r = run("spend.py", ["ceiling", "--estate", str(est), "--json"])
    c = json.loads(r.stdout)
    ok(r.returncode == 0 and not c["warn"] and c["lower_bound"], "below the line passes; a partial reading is a lower bound")
    r = run("spend.py", ["ceiling", "--estate", str(est), "--ceiling", "1000"])
    ok(r.returncode == 3 and "WARN" in r.stdout, "the ceiling is configurable")
    r = run("spend.py", ["summary", "--estate", str(est), "--ceiling", "1000"])
    ok(r.returncode == 3 and "communicator_notify" in r.stdout and "at least" in r.stdout, "the summary carries the warning")

    # An unwritable ledger warns and never breaks the caller.
    bad = TMP / "file-not-dir"
    bad.write_text("x")
    r = run("spend.py", ["record", "--route", "r", "--model", "m", "--usd", "1"],
            {"TASK_PIPELINE_SPEND_LOG": str(bad / "spend.jsonl")})
    ok(r.returncode == 0 and "not recorded" in r.stderr, "an unwritable ledger is said, not raised")

    # meanings.py check.
    mf = TMP / "meanings.md"
    mf.write_text(MEANINGS)
    r = run("meanings.py", ["check", str(mf)])
    ok(r.returncode == 0 and r.stdout.startswith("PASS"), "whole meanings pass: " + r.stdout)
    for broken, what in ((MEANINGS.replace("## Non-goals\nNo charts.\n", ""), "Non-goals"),
                         (MEANINGS.replace(". Because every reader", ", every reader"), "without its reason"),
                         (MEANINGS.replace("No charts.", "TBD"), "TBD"),
                         (MEANINGS.replace("No charts.", "word " * 3000), "words")):
        mf.write_text(broken)
        r = run("meanings.py", ["check", str(mf)])
        ok(r.returncode == 1 and what in r.stdout, f"meanings check catches {what}: " + r.stdout[:200])

    # meanings.py write: ONE call to the thinker, booked to the ledger, the file headed by its thinker.
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Fake)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    endpoint = f"http://127.0.0.1:{srv.server_address[1]}/v1"
    cfg = {"schema": "consilium-config/1", "min_panel": 3,
           "panel": [{"id": "a", "model": "v1/a", "family": "f1"}, {"id": "b", "model": "v2/b", "family": "f2"},
                     {"id": "c", "model": "v3/c", "family": "f3"}],
           "judge": {"model": "strong/judge", "family": "f4"}, "thinker": {"model": "strong/thinker", "family": "f4"}}
    (TMP / "c.json").write_text(json.dumps(cfg))
    brief = TMP / "brief.md"
    brief.write_text("Monthly export for the owner.")
    out = TMP / "run" / "meanings.md"
    before = len(LOG.read_text().splitlines())
    r = run("meanings.py", ["write", "--brief", str(brief), "--out", str(out), "--config", str(TMP / "c.json"),
                            "--endpoint", endpoint, "--key-env", "MEANINGS_TEST_KEY", "--task", "T9"],
            {"MEANINGS_TEST_KEY": "k"})
    ok(r.returncode == 0, "meanings write passes: " + r.stderr + r.stdout)
    ok(len(SEEN) == 1 and SEEN[0]["model"] == "strong/thinker", "one call, to the thinker")
    ok(out.read_text().startswith("# Meanings\n\nThinker: strong/thinker"), "the file names its thinker")
    new = [json.loads(x) for x in LOG.read_text().splitlines()][before:]
    ok(len(new) == 1 and new[0]["route"] == "spec.meanings" and new[0]["usd"] == 0.75 and new[0]["task"] == "T9",
       "the call is in the ledger: %r" % new)
    cfg.pop("thinker")
    (TMP / "c2.json").write_text(json.dumps(cfg))
    r = run("meanings.py", ["write", "--brief", str(brief), "--out", str(TMP / "run2" / "m.md"), "--config",
                            str(TMP / "c2.json"), "--endpoint", endpoint, "--key-env", "MEANINGS_TEST_KEY"],
            {"MEANINGS_TEST_KEY": "k"})
    ok(r.returncode == 0 and SEEN[-1]["model"] == "strong/judge", "no thinker configured: the judge thinks")
    n = len(SEEN)
    r = run("meanings.py", ["write", "--brief", str(brief), "--out", str(TMP / "run3" / "m.md"), "--config",
                            str(TMP / "c2.json"), "--model", "empty/model", "--endpoint", endpoint,
                            "--key-env", "MEANINGS_TEST_KEY"], {"MEANINGS_TEST_KEY": "k"})
    ok(r.returncode == 1 and len(SEEN) == n + 1 and not (TMP / "run3" / "m.md").exists(),
       "an empty answer writes nothing and is not retried")
    example = SCRIPTS.parent / "assets" / "consilium.example.json"
    n = len(SEEN)
    r = run("meanings.py", ["write", "--brief", str(brief), "--out", str(TMP / "run4" / "m.md"), "--config",
                            str(example), "--endpoint", endpoint, "--key-env", "MEANINGS_TEST_KEY"],
            {"MEANINGS_TEST_KEY": "k"})
    ok(r.returncode == 2 and len(SEEN) == n, "a placeholder thinker is never called")
    r = run("meanings.py", ["write", "--brief", str(brief), "--out", str(TMP / "run5" / "m.md"), "--config",
                            str(TMP / "c.json"), "--endpoint", endpoint, "--key-env", "MEANINGS_TEST_KEY"],
            {"MEANINGS_TEST_KEY": ""})
    ok(r.returncode == 2, "no key: exit 2")
    srv.shutdown()

    # writer-task: the subscription writer's task passes the executor check.
    r = run("meanings.py", ["writer-task", "--meanings", "m.md", "--brief", "b.md", "--spec-out", "s.md", "--size", "L"])
    t = subprocess.run([sys.executable, str(SCRIPTS / "task_prompt.py"), "check", "-", "--kind", "work"],
                       input=r.stdout, capture_output=True, text=True)
    ok(t.returncode == 0 and "Meanings: m.md" in r.stdout and "Size: L" in r.stdout, "the writer's task passes: " + t.stdout)

    print(f"spend_test: {CASES} cases passed")


if __name__ == "__main__":
    main()
