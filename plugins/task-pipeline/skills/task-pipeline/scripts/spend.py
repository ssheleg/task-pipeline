#!/usr/bin/env python3
"""spend.py: every call paid by tokens, written down with its route, model, cost and task.

`references/model-tiering.md` (Roles and money) is the doctrine. Standard library only.
The ledger is one JSON line per paid call, appended to $TASK_PIPELINE_SPEND_LOG or
~/.local/state/task-pipeline/spend.jsonl. consilium.py, meanings.py and
spec_protocol.py write to it themselves; a host script may call `record`.

    record   --route R --model M --usd X [--source S] [--tokens-in N] [--tokens-out N]
             [--task T] [--served-by M] [--note TEXT]
             Append one call by hand (a route the scripts here do not make).
    summary  [--day YYYY-MM-DD] [--month YYYY-MM] [--task T] [--json]
             [--ceiling USD] [--warn-at 0.8] [--estate auto|off|FILE]
             The day and the month of this ledger by route, model and task, and the
             estate's month as Observatory measured it at the providers. Calls whose
             cost is unknown are counted apart, never as zero.
    ceiling  [--ceiling USD] [--warn-at 0.8] [--estate auto|off|FILE] [--json]
             The estate's month against the development-mode ceiling (USD 5,000 by
             default, $TASK_PIPELINE_CEILING_USD). Exit 3 at or above the warning line,
             with the text of the one question the owner gets.

Cost sources: `openrouter` (usage.cost), `byok` (usage.cost plus
cost_details.upstream_inference_cost: OpenRouter answers cost 0 for a call billed to our
own provider key, measured 2026-11-23), `subscription` (no token spend), `unknown`.

Exit 0 ok, 2 usage, 3 the estate is at or above the warning line.
"""
import argparse
import datetime
import json
import os
import pathlib
import shutil
import subprocess
import sys

DEFAULT_LOG = pathlib.Path(os.path.expanduser("~/.local/state/task-pipeline/spend.jsonl"))
DEFAULT_CEILING = 5000.0


def log_path():
    p = os.environ.get("TASK_PIPELINE_SPEND_LOG")
    return pathlib.Path(p) if p else DEFAULT_LOG


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cost_of(usage):
    """(usd or None, source) from an OpenAI-compatible usage object (OpenRouter's shape)."""
    if not isinstance(usage, dict) or ("cost" not in usage and "cost_details" not in usage):
        return None, "unknown"
    try:
        cost = float(usage.get("cost") or 0.0)
    except (TypeError, ValueError):
        return None, "unknown"
    if usage.get("is_byok"):
        up = (usage.get("cost_details") or {}).get("upstream_inference_cost")
        if up is None:
            return None, "unknown"
        return round(cost + float(up), 8), "byok"
    if cost == 0.0 and (usage.get("completion_tokens") or 0) > 0:
        up = (usage.get("cost_details") or {}).get("upstream_inference_cost")
        if up:
            return float(up), "openrouter"
    return cost, "openrouter"


def record(route, model, usd, source, task=None, tokens_in=None, tokens_out=None, served_by=None,
           note=None, at=None):
    """Append one call. A ledger that cannot be written warns and never breaks the caller's call."""
    rec = {"schema": "spend/1", "at": at or now(), "route": route, "model": model,
           "usd": None if usd is None else round(float(usd), 8), "source": source,
           "task": task or os.environ.get("TASK_PIPELINE_TASK") or "", "repo": os.path.basename(os.getcwd())}
    for k, v in (("tokens_in", tokens_in), ("tokens_out", tokens_out), ("served_by", served_by), ("note", note)):
        if v is not None:
            rec[k] = v
    p = log_path()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"spend: the ledger {p} could not be written ({e}); this call is not recorded", file=sys.stderr)
    return rec


def read(path=None):
    p = path or log_path()
    out, bad = [], 0
    if not p.exists():
        return out, bad
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            bad += 1
    return out, bad


def estate_month(mode="auto"):
    """The estate's month as Observatory measured it at the providers, or None with the reason."""
    if mode == "off":
        return None, "estate not read (--estate off)"
    if mode != "auto":
        try:
            return json.loads(pathlib.Path(mode).read_text(encoding="utf-8")), None
        except (OSError, ValueError) as e:
            return None, f"estate file unreadable: {e}"
    exe = shutil.which("project-observatory")
    if not exe:
        return None, "Observatory is not installed here: the estate's month is unknown"
    try:
        base = subprocess.run([exe, "full-path"], capture_output=True, text=True, timeout=30).stdout.strip()
        r = subprocess.run([sys.executable, os.path.join(base, "tools", "spend.py"), "project", "--json"],
                           capture_output=True, text=True, timeout=120)
        return json.loads(r.stdout), None
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        return None, f"Observatory's spend read failed: {type(e).__name__}"


def tally(rows):
    known = sum(r["usd"] for r in rows if r.get("usd") is not None)
    unknown = sum(1 for r in rows if r.get("usd") is None)
    by = {}
    for key in ("route", "model", "task"):
        agg = {}
        for r in rows:
            k = r.get(key) or "-"
            a = agg.setdefault(k, {"usd": 0.0, "calls": 0, "unknown": 0})
            a["calls"] += 1
            if r.get("usd") is None:
                a["unknown"] += 1
            else:
                a["usd"] = round(a["usd"] + r["usd"], 6)
        by[key] = dict(sorted(agg.items(), key=lambda kv: -kv[1]["usd"]))
    return {"usd": round(known, 6), "calls": len(rows), "unknown_cost_calls": unknown, "by": by}


def ceiling_state(estate, ceiling, warn_at):
    if not estate:
        return {"known": False}
    total = estate.get("totalUsd")
    if total is None:
        return {"known": False}
    un = (estate.get("unattributed") or {})
    partial = bool(un.get("partial")) or un.get("monthUsd") is None
    share = total / ceiling if ceiling else 0.0
    st = {"known": True, "month": estate.get("month"), "estate_usd": round(total, 2), "ceiling_usd": ceiling,
          "share": round(share, 4), "warn": share >= warn_at, "lower_bound": partial,
          "fresh": estate.get("fresh"), "scanned_at": estate.get("scannedAt")}
    if st["warn"]:
        st["question"] = (f"Development mode has spent USD {total:,.0f} of USD {ceiling:,.0f} this month "
                          f"({share:.0%}). Double the ceiling to USD {2 * ceiling:,.0f}, or add USD 5,000? "
                          "Default if there is no answer: add USD 5,000 and keep working.")
    return st


def summary(a):
    rows, bad = read()
    today = datetime.datetime.now(datetime.timezone.utc)
    day = a.day or today.strftime("%Y-%m-%d")
    month = a.month or day[:7]
    if a.task:
        rows = [r for r in rows if r.get("task") == a.task]
    d_rows = [r for r in rows if str(r.get("at", "")).startswith(day)]
    m_rows = [r for r in rows if str(r.get("at", "")).startswith(month)]
    estate, why = estate_month(a.estate)
    res = {"ledger": str(log_path()), "unparsable_lines": bad, "day": day, "month": month,
           "task": a.task or None, "day_tally": tally(d_rows), "month_tally": tally(m_rows),
           "estate": ceiling_state(estate, a.ceiling, a.warn_at), "estate_note": why}
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print(render(res))
    return 3 if res["estate"].get("warn") else 0


def render(res):
    L = [f"# Token spend: day {res['day']}, month {res['month']}" + (f", task {res['task']}" if res["task"] else ""), ""]
    for label, t in (("Day", res["day_tally"]), ("Month", res["month_tally"])):
        unk = f", {t['unknown_cost_calls']} with unknown cost (not counted as zero)" if t["unknown_cost_calls"] else ""
        L += [f"## {label}: USD {t['usd']:.2f} over {t['calls']} calls{unk}", "", "| Route | Calls | USD |", "|---|---|---|"]
        L += [f"| {k} | {v['calls']} | {v['usd']:.2f} |" for k, v in t["by"]["route"].items()]
        L += ["", "| Model | Calls | USD |", "|---|---|---|"]
        L += [f"| `{k}` | {v['calls']} | {v['usd']:.2f} |" for k, v in t["by"]["model"].items()]
        L.append("")
    e = res["estate"]
    if e.get("known"):
        lb = " at least" if e["lower_bound"] else ""
        L.append(f"Estate, month {e['month']} (Observatory, measured at the providers):{lb} USD {e['estate_usd']:,.2f} "
                 f"of the ceiling USD {e['ceiling_usd']:,.0f} ({e['share']:.0%}).")
        if e.get("warn"):
            L += ["", "WARNING: at or above the warning line. Ask the owner once (communicator_notify, kind question, "
                      "through the Fabric CEO): " + e["question"]]
    else:
        L.append("Estate month: unknown (" + (res.get("estate_note") or "no reading") + ").")
    if res["unparsable_lines"]:
        L.append(f"{res['unparsable_lines']} unparsable ledger line(s) skipped.")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("--route", required=True)
    r.add_argument("--model", required=True)
    r.add_argument("--usd", type=float)
    r.add_argument("--source", default="openrouter", choices=["openrouter", "byok", "subscription", "unknown"])
    r.add_argument("--tokens-in", type=int)
    r.add_argument("--tokens-out", type=int)
    r.add_argument("--task")
    r.add_argument("--served-by")
    r.add_argument("--note")
    ceiling_default = float(os.environ.get("TASK_PIPELINE_CEILING_USD") or DEFAULT_CEILING)
    for name in ("summary", "ceiling"):
        s = sub.add_parser(name)
        s.add_argument("--ceiling", type=float, default=ceiling_default)
        s.add_argument("--warn-at", type=float, default=0.8)
        s.add_argument("--estate", default="auto")
        s.add_argument("--json", action="store_true")
        if name == "summary":
            s.add_argument("--day")
            s.add_argument("--month")
            s.add_argument("--task")
    a = ap.parse_args(argv)
    if a.cmd == "record":
        usd = a.usd if a.source != "unknown" else None
        if a.source == "subscription":
            usd = 0.0
        print(json.dumps(record(a.route, a.model, usd, a.source, a.task, a.tokens_in, a.tokens_out,
                                a.served_by, a.note), ensure_ascii=False))
        return 0
    if a.cmd == "summary":
        return summary(a)
    estate, why = estate_month(a.estate)
    st = ceiling_state(estate, a.ceiling, a.warn_at)
    if a.json:
        print(json.dumps(dict(st, note=why), ensure_ascii=False, indent=1))
    elif not st.get("known"):
        print("estate month unknown: " + (why or "no reading"))
    else:
        print(f"estate {st['month']}: USD {st['estate_usd']:,.2f} of {st['ceiling_usd']:,.0f} ({st['share']:.0%})"
              + (" WARN: " + st["question"] if st["warn"] else " ok"))
    return 3 if st.get("warn") else 0


if __name__ == "__main__":
    sys.exit(main())
