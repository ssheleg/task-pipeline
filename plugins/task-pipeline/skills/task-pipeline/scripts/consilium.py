#!/usr/bin/env python3
"""consilium.py: a council of models judges an artefact, the strongest model rules last.

`references/consilium.md` is the doctrine. Standard library only. Every model is
called through one OpenAI-compatible endpoint (OpenRouter by default); the key is
read from an environment variable the caller fills (for example through
`use_secret.py run`), never from a file and never printed.

Money (`references/model-tiering.md`, Roles and money): every panelist on tokens
answers in ONE call per round (one retry only for a lost reply); a panelist marked
`"route": "subscription"` is never called here: a subscription agent of the session
writes its verdict/1 JSON and `--import ID=FILE` brings it in at no token cost. Every
paid call is appended to the spend ledger (`spend.py`) with its route, model, cost
and `--task`; a BYOK call's cost is read from its upstream cost, never taken as 0.

    panel     [--config FILE] [--json]
              The panel and the final judge this host resolves to, and where each
              came from (the --config file, $TASK_PIPELINE_CONSILIUM, the host file
              ~/.config/task-pipeline/consilium.json, or the example in assets/).
    review    --doc FILE [--doc FILE ...] --brief FILE --out DIR [--round N]
              [--config FILE] [--max-usd X] [--only ID,ID] [--key-env NAME]
              [--endpoint URL] [--timeout S] [--dry-run] [--task T] [--import ID=FILE]
              One round. Every panelist reads the artefact and the brief BLIND (no
              other verdict) and returns a verdict/1 JSON: verdict, score, findings.
              Then the judge reads the artefact, the brief and the anonymised panel
              verdicts and returns the ruling/1 JSON: each finding accepted or
              rejected with its reason, the verdict, what must change. Files:
              DIR/round-N/<panelist>.json, judge.json, summary.md, ledger.json.
    decide    --options FILE --brief FILE --out DIR [same flags]
              The same council over a choice: the panelists rank the options blind,
              the judge picks one with reasons. The pick is the judge's.
    check     DIR [--round N] [--json]
              The gate: the round has a verdict from every panelist that answered,
              at least --min-panel of them (default 3) of at least --min-families
              families (default 3), a judge ruling, and spend within the ledger's cap.

A host may run its own council in place of this one: the path of its script in
$TASK_PIPELINE_CONSILIUM_OVERRIDE, else in ~/.config/task-pipeline/consilium.override
(`off` turns it off). That script gets the same arguments and keeps the same files
and gate; a path that does not exist is reported and the shipped council runs.

Exit 0 pass, 1 findings or a failed check, 2 usage or no key.
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import http.client
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spend  # noqa: E402  (the shared spend ledger, scripts/spend.py)
EXAMPLE = HERE.parent / "assets" / "consilium.example.json"
HOST = pathlib.Path(os.path.expanduser("~/.config/task-pipeline/consilium.json"))
DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1"

VERDICT_SCHEMA = (
    '{"verdict": "pass" | "revise" | "block", "score": 0-10, "summary": "two sentences",'
    ' "findings": [{"id": "short-id", "severity": "blocker" | "major" | "minor",'
    ' "where": "section or line", "issue": "what is wrong", "fix": "the exact change"}]}'
)
RULING_SCHEMA = (
    '{"verdict": "pass" | "revise" | "block", "score": 0-10, "summary": "three sentences",'
    ' "accepted": [{"finding": "panelist:id", "severity": "blocker" | "major" | "minor",'
    ' "why": "reason", "change": "the exact change to make"}],'
    ' "rejected": [{"finding": "panelist:id", "why": "reason"}],'
    ' "own": [{"severity": "blocker" | "major" | "minor", "issue": "what every panelist missed", "change": "fix"}],'
    ' "dissent": "where the panel disagreed and why the ruling went the way it did"}'
)
PICK_SCHEMA = (
    '{"ranking": ["option-id", ...], "pick": "option-id", "why": "reasons tied to the brief",'
    ' "risks": ["..."], "score": {"option-id": 0-10}}'
)


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_config(path=None):
    """Resolve the panel: --config, $TASK_PIPELINE_CONSILIUM, the host file, the example."""
    for source, p in (("--config", path), ("$TASK_PIPELINE_CONSILIUM", os.environ.get("TASK_PIPELINE_CONSILIUM")),
                      ("host", str(HOST) if HOST.exists() else None), ("example", str(EXAMPLE))):
        if p:
            cfg = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
            problems = validate_config(cfg)
            if problems:
                raise SystemExit(f"consilium: {p}: " + "; ".join(problems))
            cfg["_source"] = f"{source}: {p}"
            return cfg
    raise SystemExit("consilium: no configuration found")


def validate_config(cfg):
    out = []
    panel = cfg.get("panel")
    if not isinstance(panel, list) or len(panel) < 3:
        out.append("panel needs at least three members")
        panel = panel if isinstance(panel, list) else []
    fams = set()
    for m in panel:
        if not isinstance(m, dict) or not m.get("id") or not m.get("model") or not m.get("family"):
            out.append("every panelist needs id, model and family")
            continue
        fams.add(m["family"])
        if m.get("route", "tokens") not in ("tokens", "subscription"):
            out.append(f"panelist {m['id']}: route is tokens or subscription")
    if panel and len(fams) < 3:
        out.append("the panel needs at least three model families")
    judge = cfg.get("judge")
    if not isinstance(judge, dict) or not judge.get("model") or not judge.get("family"):
        out.append("judge needs model and family (the strongest model of the host's model map)")
    return out


TRANSIENT_HTTP = {429, 502, 503, 504}


def call(endpoint, key, model, messages, timeout, max_tokens, extra=None):
    """One call, and ONE retry after a pause when the transport failed (a cut or undecodable
    body, a reset, a timeout, 429/502/503/504): a verdict is never asked twice, a lost
    reply is (board request fb909e59: one IncompleteRead took a whole round down)."""
    res = _call_once(endpoint, key, model, messages, timeout, max_tokens, extra)
    if res.get("transient"):
        time.sleep(float(os.environ.get("CONSILIUM_RETRY_PAUSE", "5")))
        first = res.get("error")
        res = _call_once(endpoint, key, model, messages, timeout, max_tokens, extra)
        res["retried"] = first
    if res.get("error"):
        res["status"] = "failed"
    res.pop("transient", None)
    return res


def _call_once(endpoint, key, model, messages, timeout, max_tokens, extra=None):
    body = {"model": model, "messages": messages, "max_tokens": max_tokens,
            "usage": {"include": True}}
    if extra:
        body.update(extra)
    req = urllib.request.Request(endpoint.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                                          "X-Title": "task-pipeline consilium"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", "replace")[:400]
        except (http.client.HTTPException, OSError):
            detail = ""
        return {"error": f"http {e.code}: {detail}", "seconds": round(time.time() - t0, 1),
                "transient": e.code in TRANSIENT_HTTP}
    except (urllib.error.URLError, http.client.HTTPException, OSError, ValueError) as e:
        # http.client.IncompleteRead is an HTTPException, not an OSError (fb909e59).
        return {"error": f"{type(e).__name__}: {e}", "seconds": round(time.time() - t0, 1), "transient": True}
    choice = (data.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    usage = data.get("usage") or {}
    usd, source = spend.cost_of(usage)
    paid = {"cost": usd or 0.0, "cost_source": source, "cost_known": usd is not None}
    if not (msg.get("content") or "").strip() and choice.get("finish_reason") == "length":
        # A reasoning model can spend the whole budget thinking and answer nothing (Fable 5.2, 2026-11-23):
        # cap reasoning in the panelist's "extra" ({"reasoning": {"max_tokens": N}}) or raise max_tokens.
        return {"error": "no text: the token budget ran out (reasoning ate it); cap reasoning or raise max_tokens",
                **paid, "tokens_in": usage.get("prompt_tokens"), "tokens_out": usage.get("completion_tokens"),
                "seconds": round(time.time() - t0, 1), "finish": "length"}
    return {"text": msg.get("content") or "", "finish": choice.get("finish_reason"),
            **paid, "tokens_in": usage.get("prompt_tokens"),
            "tokens_out": usage.get("completion_tokens"), "seconds": round(time.time() - t0, 1),
            "served_by": data.get("model")}


def _top_level_objects(text):
    """Every balanced top-level {...} in text, braces inside JSON strings ignored."""
    out, depth, start, in_str, esc = [], 0, None, False, False
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"' and depth > 0:
            in_str = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth > 0:
            depth -= 1
            if depth == 0:
                out.append(text[start:i + 1])
    return out


def parse_json(text):
    """The last top-level JSON object in a reply (models wrap it in prose or a fence).

    Read by balanced braces, never by a fence regex: a non-greedy fence match took the
    INNER object when a reply carried a stray closing fence (handoff 2026-11-23)."""
    if not text:
        return None
    for cand in reversed(_top_level_objects(text)):
        try:
            data = json.loads(cand)
        except ValueError:
            continue
        if isinstance(data, dict):
            return data
    return None


def read_docs(paths):
    parts = []
    for p in paths:
        t = pathlib.Path(p).read_text(encoding="utf-8")
        parts.append(f"<artefact path=\"{p}\" sha256=\"{hashlib.sha256(t.encode()).hexdigest()[:16]}\">\n{t}\n</artefact>")
    return "\n\n".join(parts)


def panel_prompt(kind, brief, artefact, lens):
    if kind == "decide":
        task = ("Rank the options against the brief. Judge each on its own merits and on the brief's criteria, "
                f"then pick one. Answer with ONE JSON object only, this shape: {PICK_SCHEMA}")
    else:
        task = ("Review the artefact against the brief as an independent expert. Find what is wrong, missing, "
                "contradictory, unsafe, unbuildable or unverifiable; say exactly what to change. Do not praise. "
                "A finding without a concrete fix is not a finding. "
                f"Answer with ONE JSON object only, this shape: {VERDICT_SCHEMA}")
    sys_msg = ("You are one member of a council of models from different vendors. You do not see the others' "
               "answers. Be specific, cite sections, and keep to what the artefact says." + (f" Your lens: {lens}" if lens else ""))
    user = f"<brief>\n{brief}\n</brief>\n\n{artefact}\n\n{task}"
    return [{"role": "system", "content": sys_msg}, {"role": "user", "content": user}]


def judge_prompt(kind, brief, artefact, verdicts):
    anon = json.dumps(verdicts, ensure_ascii=False, indent=1)
    if kind == "decide":
        task = ("You are the final judge. Read the options, the brief and the council's blind rankings. Pick the "
                "option that best serves the brief; a majority does not bind you, a reason does. "
                f"Answer with ONE JSON object only, this shape: {PICK_SCHEMA}")
    else:
        task = ("You are the final judge of the council and the strongest model in it. Rule on every panel finding: "
                "accept it (with the exact change) or reject it (with the reason). Add what every panelist missed. "
                "A majority does not bind you, a reason does. Then give the verdict: pass only when no accepted "
                "blocker or major finding remains. "
                f"Answer with ONE JSON object only, this shape: {RULING_SCHEMA}")
    user = f"<brief>\n{brief}\n</brief>\n\n{artefact}\n\n<council>\n{anon}\n</council>\n\n{task}"
    return [{"role": "system", "content": "You rule last. Be exact and fair; quote the artefact where it decides."},
            {"role": "user", "content": user}]


def run_round(args, kind):
    cfg = load_config(args.config)
    key = os.environ.get(args.key_env)
    if not key and not args.dry_run:
        print(f"consilium: ${args.key_env} is empty; run under use_secret.py run", file=sys.stderr)
        return 2
    brief = pathlib.Path(args.brief).read_text(encoding="utf-8")
    artefact = read_docs(args.doc if kind == "review" else [args.options])
    out = pathlib.Path(args.out) / f"round-{args.round}"
    out.mkdir(parents=True, exist_ok=True)
    panel = cfg["panel"]
    if args.only:
        keep = set(args.only.split(","))
        panel = [m for m in panel if m["id"] in keep]
    task = args.task or os.environ.get("TASK_PIPELINE_TASK") or pathlib.Path(args.out).name
    imports = {}
    for spec in args.imports or []:
        pid, _, f = spec.partition("=")
        if not f:
            print(f"consilium: --import takes ID=FILE, got {spec!r}", file=sys.stderr)
            return 2
        imports[pid] = f
    unknown = set(imports) - {m["id"] for m in panel}
    if unknown:
        print("consilium: --import names no panelist: " + ", ".join(sorted(unknown)), file=sys.stderr)
        return 2
    sub = [m for m in panel if m.get("route") == "subscription" or m["id"] in imports]
    panel = [m for m in panel if m not in sub]
    placeholders = [m["model"] for m in panel + [cfg["judge"]] if m["model"].startswith("<")]
    if placeholders and not args.dry_run:
        print("consilium: the configuration names roles, not models (" + cfg["_source"] + "); write the host file "
              f"{HOST} from the model map first", file=sys.stderr)
        return 2
    cap = float(args.max_usd if args.max_usd is not None else cfg.get("max_usd_per_round", 10))
    ledger = {"schema": "consilium-ledger/1", "round": args.round, "kind": kind, "started": now(),
              "config": cfg["_source"], "cap_usd": cap, "calls": []}
    if args.dry_run:
        print(json.dumps({"panel": [m["model"] for m in panel], "subscription": [m["id"] for m in sub],
                          "judge": cfg["judge"]["model"], "prompt_chars": len(artefact) + len(brief),
                          "cap_usd": cap, "task": task}, indent=1))
        return 0

    def one(m):
        try:
            res = call(args.endpoint, key, m["model"], panel_prompt(kind, brief, artefact, m.get("lens")),
                       args.timeout, m.get("max_tokens", 12000), m.get("extra"))
        except Exception as e:  # one panelist never takes the round down (fb909e59)
            res = {"error": f"{type(e).__name__}: {e}", "status": "failed"}
        parsed = parse_json(res.get("text"))
        rec = {"id": m["id"], "model": m["model"], "family": m["family"], "at": now(), "route": "tokens",
               **{k: v for k, v in res.items() if k != "text"}, "parsed": parsed is not None}
        log_spend(rec, f"consilium.{kind}.panel", task)
        (out / f"{m['id']}.json").write_text(json.dumps({"meta": rec, "verdict": parsed, "raw": res.get("text", "")},
                                                          ensure_ascii=False, indent=1), encoding="utf-8")
        return m, rec, parsed

    verdicts = {}
    for m in sub:
        # A subscription panelist: its verdict was written by an agent of the session, never called here.
        f = imports.get(m["id"])
        parsed, err = None, None
        if not f:
            err = "subscription panelist: run it as an agent of the session and pass --import ID=FILE"
        else:
            try:
                raw = pathlib.Path(f).read_text(encoding="utf-8")
                parsed = parse_json(raw)
                err = None if parsed is not None else "the imported file holds no JSON verdict"
            except OSError as e:
                err = f"import unreadable: {e}"
        rec = {"id": m["id"], "model": m["model"], "family": m["family"], "at": now(), "route": "subscription",
               "cost": 0.0, "cost_source": "subscription", "cost_known": True, "parsed": parsed is not None,
               **({"error": err} if err else {}), **({"imported": f} if f else {})}
        ledger["calls"].append(rec)
        if parsed is not None:
            verdicts[m["id"]] = parsed
            (out / f"{m['id']}.json").write_text(json.dumps({"meta": rec, "verdict": parsed}, ensure_ascii=False,
                                                              indent=1), encoding="utf-8")
        print(f"  {m['id']:<10} {m['model']:<34} {'imported' if parsed else 'NO VERDICT':<10} subscription "
              f"{err or ''}", file=sys.stderr)
    if args.judge_only:
        # Rerun only the judge over the verdicts this round already holds (a judge that failed is not
        # a reason to pay the panel again).
        for m in panel:
            f = out / f"{m['id']}.json"
            if f.exists():
                rec = json.loads(f.read_text(encoding="utf-8"))
                # The panel's spend stays in the round's total (it was paid); the spend ledger
                # already holds it, so nothing is logged again.
                ledger["calls"].append(dict(rec["meta"], reused=True))
                if rec.get("verdict") is not None:
                    verdicts[m["id"]] = rec["verdict"]
        panel_iter = []
    else:
        panel_iter = panel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(panel_iter))) as ex:
        for m, rec, parsed in ex.map(one, panel_iter):
            ledger["calls"].append(rec)
            if parsed is not None:
                verdicts[m["id"]] = parsed
            print(f"  {m['id']:<10} {m['model']:<34} {'ok' if parsed else 'NO VERDICT':<10} "
                  f"${rec.get('cost', 0):.3f} {rec.get('seconds')}s {rec.get('error', '')[:120]}", file=sys.stderr)
    spent = sum(c.get("cost", 0) for c in ledger["calls"])
    ruling = None
    if spent >= cap:
        ledger["judge_skipped"] = f"spend {spent:.2f} reached the cap {cap:.2f} before the judge"
    elif len(verdicts) < int(cfg.get("min_panel", 3)):
        ledger["judge_skipped"] = f"only {len(verdicts)} verdicts; the council needs {cfg.get('min_panel', 3)}"
    else:
        # Anonymise: the judge sees panelists by letter and family, never by vendor rank.
        letters = {pid: chr(65 + i) for i, pid in enumerate(sorted(verdicts))}
        anon = {f"{letters[p]} ({next(m['family'] for m in panel + sub if m['id'] == p)})": v for p, v in verdicts.items()}
        j = cfg["judge"]
        res = call(args.endpoint, key, j["model"], judge_prompt(kind, brief, artefact, anon), args.timeout,
                   j.get("max_tokens", 16000), j.get("extra"))
        ruling = parse_json(res.get("text"))
        rec = {"id": "judge", "model": j["model"], "family": j["family"], "at": now(), "route": "tokens",
               **{k: v for k, v in res.items() if k != "text"}, "parsed": ruling is not None, "letters": letters}
        log_spend(rec, f"consilium.{kind}.judge", task)
        ledger["calls"].append(rec)
        (out / "judge.json").write_text(json.dumps({"meta": rec, "ruling": ruling, "raw": res.get("text", "")},
                                                    ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  {'judge':<10} {j['model']:<34} {'ok' if ruling else 'NO RULING':<10} ${rec.get('cost', 0):.3f} "
              f"{rec.get('seconds')}s {rec.get('error', '')[:120]}", file=sys.stderr)
    ledger["spent_usd"] = round(sum(c.get("cost", 0) for c in ledger["calls"]), 4)
    ledger["unknown_cost_calls"] = sum(1 for c in ledger["calls"] if c.get("cost_known") is False)
    ledger["task"] = task
    ledger["finished"] = now()
    (out / "ledger.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "summary.md").write_text(summary_md(ledger, verdicts, ruling, kind), encoding="utf-8")
    print(str(out / "summary.md"))
    return 0 if ruling and (kind == "decide" or ruling.get("verdict") == "pass") else 1


def log_spend(rec, route, task):
    spend.record(route, rec["model"], rec.get("cost") if rec.get("cost_known", True) else None,
                 rec.get("cost_source", "unknown"), task, rec.get("tokens_in"), rec.get("tokens_out"),
                 rec.get("served_by"))


def summary_md(ledger, verdicts, ruling, kind):
    L = [f"# Consilium round {ledger['round']} ({kind})", "",
         f"Config: {ledger['config']}. Spent USD {ledger['spent_usd']:.2f} of the cap {ledger['cap_usd']:.2f}.", "",
         "| Panelist | Model | Verdict | Score | Findings | Cost |", "|---|---|---|---|---|---|"]
    for c in ledger["calls"]:
        if c["id"] == "judge":
            continue
        v = verdicts.get(c["id"]) or {}
        L.append(f"| {c['id']} | `{c['model']}` | {v.get('verdict', v.get('pick', c.get('error', 'no verdict'))) if v else c.get('error', 'no verdict')[:60]} "
                 f"| {v.get('score', '') if not isinstance(v.get('score'), dict) else ''} | {len(v.get('findings', []) or [])} | {c.get('cost', 0):.3f} |")
    L.append("")
    if ruling:
        j = next(c for c in ledger["calls"] if c["id"] == "judge")
        if kind == "decide":
            L += [f"## Ruling by `{j['model']}`: pick **{ruling.get('pick')}**", "", ruling.get("why", ""), ""]
        else:
            L += [f"## Ruling by `{j['model']}`: **{ruling.get('verdict')}** ({ruling.get('score')}/10)", "",
                  ruling.get("summary", ""), "", "### Accepted", ""]
            for a in ruling.get("accepted", []) or []:
                L.append(f"- [{a.get('severity')}] {a.get('finding')}: {a.get('change')} ({a.get('why')})")
            L += ["", "### Judge's own", ""]
            for a in ruling.get("own", []) or []:
                L.append(f"- [{a.get('severity')}] {a.get('issue')}: {a.get('change')}")
            L += ["", "### Rejected", ""]
            for a in ruling.get("rejected", []) or []:
                L.append(f"- {a.get('finding')}: {a.get('why')}")
            L += ["", f"Dissent: {ruling.get('dissent', '')}"]
    else:
        L.append(f"No ruling: {ledger.get('judge_skipped', 'the judge gave no parsable answer')}.")
    return "\n".join(L) + "\n"


def check(args):
    d = pathlib.Path(args.dir) / f"round-{args.round}"
    problems = []
    try:
        ledger = json.loads((d / "ledger.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        problems.append(f"{d}/ledger.json missing or unreadable")
        ledger = {"calls": []}
    panel = [c for c in ledger["calls"] if c.get("id") != "judge" and c.get("parsed")]
    fams = {c.get("family") for c in panel}
    if len(panel) < args.min_panel:
        problems.append(f"{len(panel)} panel verdicts, {args.min_panel} needed")
    if len(fams) < args.min_families:
        problems.append(f"{len(fams)} model families, {args.min_families} needed")
    judge = next((c for c in ledger["calls"] if c.get("id") == "judge"), None)
    if not judge or not judge.get("parsed"):
        problems.append("no parsable judge ruling")
    if ledger.get("spent_usd", 0) > ledger.get("cap_usd", 0) + 1e-9:
        problems.append("spend above the round's cap")
    res = {"dir": str(d), "pass": not problems, "problems": problems, "panel": len(panel), "families": sorted(fams),
           "judge": judge.get("model") if judge else None, "spent_usd": ledger.get("spent_usd")}
    print(json.dumps(res, indent=1) if args.json else ("PASS " if res["pass"] else "FAIL ") + "; ".join(problems))
    return 0 if res["pass"] else 1


OVERRIDE_ENV = "TASK_PIPELINE_CONSILIUM_OVERRIDE"
OVERRIDE_FILE = pathlib.Path("~/.config/task-pipeline/consilium.override")
OVERRIDE_ACTIVE = "TASK_PIPELINE_CONSILIUM_OVERRIDDEN"


def host_override():
    """The host's own council script, or None: none named, `off`, missing, or already inside it."""
    if os.environ.get(OVERRIDE_ACTIVE):
        return None
    raw = os.environ.get(OVERRIDE_ENV)
    if raw is None:
        f = OVERRIDE_FILE.expanduser()
        raw = f.read_text(encoding="utf-8").strip() if f.is_file() else ""
    if not raw or raw.strip().lower() == "off":
        return None
    path = pathlib.Path(raw.strip()).expanduser()
    if not path.is_file():
        print(f"consilium.py: the host's council {path} does not exist; the shipped council runs", file=sys.stderr)
        return None
    if path.resolve() == pathlib.Path(__file__).resolve():
        return None
    return path


def main(argv=None):
    override = host_override()
    if override is not None:
        args = sys.argv[1:] if argv is None else list(argv)
        env = dict(os.environ, **{OVERRIDE_ACTIVE: "1"})
        return subprocess.call([sys.executable, str(override)] + args, env=env)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("panel")
    p.add_argument("--config")
    p.add_argument("--json", action="store_true")
    for name in ("review", "decide"):
        r = sub.add_parser(name)
        if name == "review":
            r.add_argument("--doc", action="append", required=True)
        else:
            r.add_argument("--options", required=True)
        r.add_argument("--brief", required=True)
        r.add_argument("--out", required=True)
        r.add_argument("--round", type=int, default=1)
        r.add_argument("--config")
        r.add_argument("--max-usd", type=float)
        r.add_argument("--only")
        r.add_argument("--key-env", default="OPENROUTER_API_KEY")
        r.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
        r.add_argument("--timeout", type=int, default=600)
        r.add_argument("--dry-run", action="store_true")
        r.add_argument("--judge-only", action="store_true",
                       help="rerun only the judge over this round's saved verdicts")
        r.add_argument("--task", help="the task the spend is booked to (default $TASK_PIPELINE_TASK, else --out's name)")
        r.add_argument("--import", dest="imports", action="append", metavar="ID=FILE",
                       help="a verdict a subscription agent wrote for panelist ID; never a token call")
    c = sub.add_parser("check")
    c.add_argument("dir")
    c.add_argument("--round", type=int, default=1)
    c.add_argument("--min-panel", type=int, default=3)
    c.add_argument("--min-families", type=int, default=3)
    c.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "panel":
        cfg = load_config(a.config)
        if a.json:
            print(json.dumps(cfg, indent=1))
        else:
            print(f"source: {cfg['_source']}")
            for m in cfg["panel"]:
                print(f"  panel  {m['id']:<10} {m['model']:<36} {m['family']:<10} {m.get('route', 'tokens')}")
            print(f"  judge  {'':<10} {cfg['judge']['model']:<36} {cfg['judge']['family']}")
        return 0
    if a.cmd == "check":
        return check(a)
    return run_round(a, a.cmd)


if __name__ == "__main__":
    sys.exit(main())
