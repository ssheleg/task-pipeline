#!/usr/bin/env python3
"""before.py: the practice before 2026-11-23: the strongest model writes the WHOLE spec by tokens, one call.

    before.py --brief FILE --input FILE ... --out FILE [--model ID] [--task T]

Same thinker, same effort and same inputs as `meanings.py write`, so the two arms differ only in who writes
the text. The call is booked to the spend ledger (route ab.before). Run under use_secret.py run.
"""
import argparse, json, os, pathlib, sys
SKILL = pathlib.Path(__file__).resolve().parents[3] / "plugins/task-pipeline/skills/task-pipeline/scripts"
sys.path.insert(0, str(SKILL))
import consilium, spend  # noqa: E402

SYSTEM = """You are the principal author of an engineering specification. Write the whole spec a zero-context
implementer builds from without a second question: exact, concrete, buildable. Size M owes these sections:
Goal, Scope (in and out), Requirements (ids REQ-1..., each with how it is verified), Design, Contracts (exact
shapes: CLI verbs, flags, JSON fields, exit codes), Edge cases, Decisions (a table: decision, reason, rejected
alternative), Rollout, Questions (a ledger: id, question, class strategy|tactics|known-domain|unknown, answer,
by, basis), Tests. Decide tactical questions yourself; ask the owner only strategy, with a default. Header lines
`Size: M` and `Author: anthropic/thinker`. Write in English. Never use the em dash character."""

ap = argparse.ArgumentParser()
ap.add_argument("--brief", required=True)
ap.add_argument("--input", action="append", default=[])
ap.add_argument("--out", required=True)
ap.add_argument("--model", default="anthropic/claude-fable-5.2")
ap.add_argument("--task", default="model-budget-ab")
a = ap.parse_args()
parts = ["<brief>\n" + pathlib.Path(a.brief).read_text() + "\n</brief>"]
parts += [f"<input path=\"{f}\">\n" + pathlib.Path(f).read_text() + "\n</input>" for f in a.input]
msgs = [{"role": "system", "content": SYSTEM},
        {"role": "user", "content": "\n\n".join(parts) + "\n\nWrite the spec for this brief."}]
res = consilium.call(consilium.DEFAULT_ENDPOINT, os.environ["OPENROUTER_API_KEY"], a.model, msgs, 1500, int(os.environ.get("BEFORE_MAX_TOKENS", "32000")),
                     {"reasoning": {"effort": "medium"}})
spend.record("ab.before", a.model, res.get("cost") if res.get("cost_known", True) else None,
             res.get("cost_source", "unknown"), a.task, res.get("tokens_in"), res.get("tokens_out"), res.get("served_by"))
meta = {k: v for k, v in res.items() if k != "text"}
pathlib.Path(a.out + ".meta.json").write_text(json.dumps(meta, indent=1))
if res.get("text"):
    pathlib.Path(a.out).write_text(res["text"])
print(json.dumps(meta))
