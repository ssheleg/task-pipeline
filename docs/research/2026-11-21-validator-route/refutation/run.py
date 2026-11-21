#!/usr/bin/env python3
"""B-175: the refutation test of the validator-route dossier.

Two counts, both named in the dossier's *What would refute it*:

1. Parse failures over validator calls: a reply without a JSON object or with an
   unknown verdict. Refusals, truncation and HTTP errors are counted apart.
2. The family rule: four copies of the dossier, each with one planted wrong claim,
   plus the unplanted control, judged by a validator of the author's family and by
   two of other families, with the same blind prompt `research validate` sends.

A plant counts as caught when the verdict is not `agree` and the validator's
evidence or gaps contain one of the plant's keywords. The keywords are fixed in
this file before the run; the control's replies give the keyword noise floor.

The author-family validator is called here directly, outside `research validate`,
which refuses it by design: the refusal guards what a dossier records, and this is
a measurement of whether that refusal buys anything.

Usage (the key only from the variable, run under the host's secret runner):
  run.py --dry-run
  run.py --endpoint https://openrouter.ai/api/v1 --key-env OPENROUTER_API_KEY
"""
import argparse
import copy
import importlib.util
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(DOSSIER, "..", "..", ".."))
SCRIPT = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline",
                      "scripts", "spec_protocol.py")

VALIDATORS = [  # (model, family); the author is anthropic (README header)
    ("anthropic/claude-sonnet-5.5", "anthropic"),
    ("moonshotai/kimi-k3.1-pro", "moonshotai"),
    ("google/gemini-4-argon", "google"),
]

# Each plant: replacements in README.md, an optional source added to sources.json,
# and keywords that only a reply discussing the plant would carry.
PLANTS = {
    "P1-silent-ignore-reversed": {
        "what": "says OpenRouter rejects an unsupported response_format with an error, "
                "the opposite of [B3], and that option 3 loses only on token cost",
        "replace": [(
            "Option 3 is not\nthe default because its support is per endpoint and sometimes only a hint [B2], and an\n"
            "unsupported `response_format` is ignored without notice [B3], so the local check is needed either\n"
            "way [B1].",
            "Option 3 is not\nthe default only because it costs more tokens: OpenRouter rejects an unsupported\n"
            "`response_format` with an error [B3], so a missing schema never passes unnoticed.")],
        "keywords": ["reject", "more tokens", "token cost", "costs more"],
    },
    "P2-unsupported-gain": {
        "what": "claims [B5] shows a judge of another family removes self-preference entirely, "
                "while the Findings say no source read quantifies that gain",
        "replace": [(
            "Validators come from another family than the author, because self-preference is\n"
            "measured [B6] even though its size is uncertain [B5];",
            "Validators come from another family than the author, because [B5] shows that a judge\n"
            "of another family removes self-preference entirely;")],
        "keywords": ["entirely", "quantif", "removes"],
    },
    "P3-model-source-as-evidence": {
        "what": "rests a fallback route on M2, a source of kind model with read false",
        "replace": [(
            "a direct endpoint stays possible where a provider is native [A4][A5].",
            "a direct endpoint stays possible where a provider is native [A4][A5]; DeepSeek's\n"
            "endpoint enforces strict `json_schema` on every call [M2], so it is the fallback route.")],
        "add_source": {"id": "M2", "kind": "model", "title": "A second model's answer",
                       "url": "", "read": False,
                       "claim": "DeepSeek's endpoint enforces strict json_schema on every call."},
        "keywords": ["m2", "kind: model", "kind model", "read: false", "not evidence", "unread"],
    },
    "P4-rejected-route-chosen": {
        "what": "picks Anthropic's compatibility layer as the route and says its page recommends "
                "it for production, contradicting [A3] and the Rejected section",
        "replace": [(
            "On this host the route is OpenRouter (option 1): one key, and every model the\n"
            "host's model map names for checks is in its catalogue [M1] [A1];",
            "On this host the route is Anthropic's compatibility layer (option 2), which its page\n"
            "recommends for production use [A3];")],
        "keywords": ["production", "test and compare", "primarily intended", "rejected"],
    },
}


def load_protocol():
    spec = importlib.util.spec_from_file_location("spec_protocol", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def base_texts():
    readme = open(os.path.join(DOSSIER, "README.md")).read()
    # The decider's notes name the earlier validators' gaps: not shown to any variant.
    readme = re.sub(r"\n## Changes after validation\n.*\Z", "\n", readme, flags=re.S)
    sources = json.load(open(os.path.join(DOSSIER, "sources.json")))
    return readme, sources


def variants():
    readme, sources = base_texts()
    out = {"C0-control": (readme, sources)}
    for pid, p in PLANTS.items():
        text, src = readme, copy.deepcopy(sources)
        for old, new in p["replace"]:
            if old not in text:
                sys.exit("plant %s: anchor not found in README.md" % pid)
            text = text.replace(old, new, 1)
        if p.get("add_source"):
            src.append(p["add_source"])
        out[pid] = (text, src)
    return out


def prompt_for(sp, text, sources):
    # The same prompt research_validate builds.
    return "%s\n\n--- README.md ---\n%s\n--- sources.json ---\n%s" % (
        sp.VALIDATOR_BRIEF, sp.blind_dossier(text), json.dumps(sources, ensure_ascii=False, indent=1))


def call(endpoint, key, model, prompt, timeout=240):
    body = json.dumps({"model": model, "temperature": 0,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(endpoint.rstrip("/") + "/chat/completions", data=body,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer " + key})
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            reply = json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return {"outcome": "http_error", "detail": "HTTP %d" % e.code,
                "seconds": round(time.time() - started, 1)}
    except (urllib.error.URLError, OSError, ValueError) as e:
        return {"outcome": "transport_error", "detail": type(e).__name__,
                "seconds": round(time.time() - started, 1)}
    res = {"seconds": round(time.time() - started, 1), "usage": reply.get("usage"),
           "answered_by": reply.get("model", model)}
    try:
        choice = reply["choices"][0]
        content = choice["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return dict(res, outcome="no_content", detail="no choices[0].message.content")
    res["finish_reason"] = choice.get("finish_reason")
    res["content"] = content
    if choice.get("finish_reason") == "length":
        return dict(res, outcome="truncated")
    if choice.get("message", {}).get("refusal"):
        return dict(res, outcome="refusal")
    return res


def classify(sp, res):
    if "outcome" in res:
        return res
    verdict, err = sp.parse_verdict(res["content"])
    if err:
        kind = "parse_no_json" if "no JSON" in err else (
            "parse_bad_verdict" if "verdict" in err else "parse_bad_json")
        return dict(res, outcome=kind, detail=err)
    return dict(res, outcome="verdict", **verdict)


def hits(res, keywords):
    blob = (res.get("evidence", "") + " " + " ".join(res.get("gaps", []))).lower()
    return [k for k in keywords if k in blob]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default=os.environ.get("SPEC_PROTOCOL_ENDPOINT", ""))
    ap.add_argument("--key-env", default="SPEC_PROTOCOL_API_KEY")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "results.json"))
    a = ap.parse_args()
    sp = load_protocol()
    vs = variants()
    if a.dry_run:
        for vid, (text, src) in vs.items():
            print("%s: prompt %d chars" % (vid, len(prompt_for(sp, text, src))))
        return 0
    key = os.environ.get(a.key_env, "")
    if not a.endpoint or not key:
        sys.exit("need --endpoint and a non-empty %s" % a.key_env)
    rows = []
    for vid, (text, src) in vs.items():
        prompt = prompt_for(sp, text, src)
        for model, family in VALIDATORS:
            res = classify(sp, call(a.endpoint, key, model, prompt))
            row = {"variant": vid, "model": model, "family": family,
                   "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            row.update({k: v for k, v in res.items() if k != "content"})
            if res.get("outcome") != "verdict":
                row["content_head"] = (res.get("content") or "")[:400]
            if vid == "C0-control":
                row["keyword_noise"] = {pid: hits(res, p["keywords"]) for pid, p in PLANTS.items()}
            else:
                h = hits(res, PLANTS[vid]["keywords"])
                row["keyword_hits"] = h
                row["caught"] = res.get("outcome") == "verdict" and res["verdict"] != "agree" and bool(h)
            rows.append(row)
            print("%-28s %-28s %-16s %s %s" % (vid, model, res.get("outcome"),
                                               res.get("verdict", ""), row.get("keyword_hits", "")),
                  flush=True)
    summary = {"calls": len(rows), "outcomes": {}, "caught_by_family": {}, "cost_usd": 0.0}
    for r in rows:
        summary["outcomes"][r["outcome"]] = summary["outcomes"].get(r["outcome"], 0) + 1
        summary["cost_usd"] += float((r.get("usage") or {}).get("cost") or 0)
        if "caught" in r:
            f = summary["caught_by_family"].setdefault(r["model"], [0, 0])
            f[0] += int(r["caught"])
            f[1] += 1
    summary["cost_usd"] = round(summary["cost_usd"], 4)
    json.dump({"plants": {k: {"what": v["what"], "keywords": v["keywords"]} for k, v in PLANTS.items()},
               "validators": VALIDATORS, "summary": summary, "rows": rows},
              open(a.out, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
