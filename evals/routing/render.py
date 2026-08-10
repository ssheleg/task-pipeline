#!/usr/bin/env python3
"""Render the routing-measurement prompt for one query.

The measurement asks a fresh agent, holding nothing but competing skill
descriptions and one user sentence, which skill it would use. Run before a
description change and after it; the only thing that may differ between the two
runs is the text of the descriptions themselves — this file renders everything
else identically, which is the whole reason it is a file and not a paste.

    python3 evals/routing/render.py <query-id>      # prompt to stdout
    python3 evals/routing/render.py --list          # the queries and expectations

Honest limits, stated here because a reader of the results will not see them:
  * this measures the DESCRIPTIONS' discriminating power, not Claude Code's own
    selection machinery, which sees more than a description;
  * a subagent carries its host's system prompt, so it is fresh in CONTEXT, not
    in disposition — this is not the blind multi-model run board row B-002 asks
    for, and no result here may be quoted as one.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# task-pipeline's description is read from the WORKING TREE, so the after-run
# picks up the edit; the competitors are read from the installed plugins, so an
# unrelated release of theirs cannot silently move the baseline between runs.
SELF = os.path.join(ROOT, "plugins/task-pipeline/skills/task-pipeline/SKILL.md")
MARKETPLACES = os.path.expanduser("~/.claude/plugins/marketplaces")
COMPETITORS = ["super-ux", "sheleg-design", "make-skill", "agent-sync", "seo-aeo-audit"]

QUERIES = [
    # id,           the sentence,                                            what should win, why it is here
    ("AUD-01", "сделай аудит модуля оплат", "task-pipeline",
     "findings on code — audit.md:350 says an audit may be the whole task"),
    ("BUG-01", "проверь, нет ли ошибок в обработчике вебхуков", "task-pipeline",
     "bug hunt — findings that land in the repo"),
    ("PRD-01", "проверь, всё ли живо в проде после вчерашнего релиза", "task-pipeline",
     "production check"),
    ("PRR-01", "посмотри PR #24 и скажи, что там не так", "task-pipeline",
     "PR review — review.md owns the reader contract"),
    ("FEA-01", "добавь экспорт в CSV на страницу отчётов", "task-pipeline",
     "CONTROL+ — build work already routes; must not regress"),
    ("QST-01", "объясни, как наш auth middleware решает, какие роуты публичные", "none",
     "CONTROL− — a question; the exclusion must survive the rewording"),
    ("TYP-01", "поправь опечатку в заголовке README", "none",
     "CONTROL− — a one-line edit; the exclusion must survive"),
    ("SEO-01", "сделай аудит лендинга — почему упал трафик из поиска", "seo-aeo-audit",
     "FALSE-POSITIVE test — 'аудит' must not be stolen from its owner"),
    ("UXA-01", "проверь, что код соответствует UX-сценариям", "ux-audit",
     "FALSE-POSITIVE test — the scenario audit has an owner"),
    ("SKL-01", "проверь, соответствует ли этот скил стандарту", "make-skill",
     "FALSE-POSITIVE test — skill-shaped audit has an owner"),
]


def _desc(path):
    """The description as the platform reads it: the frontmatter field, unwrapped."""
    t = open(path, encoding="utf-8").read()
    n = re.search(r"^name:\s*(.+)$", t, re.M)
    d = re.search(r"^description:\s*(.+?)(?=^[a-z_-]+:\s|^---)", t, re.M | re.S)
    if not (n and d):
        return None
    return n.group(1).strip(), " ".join(d.group(1).split()).strip("\"' ")


def choices():
    out = []
    s = _desc(SELF)
    if s:
        out.append(s)
    for m in COMPETITORS:
        base = os.path.join(MARKETPLACES, m)
        if not os.path.isdir(base):
            continue
        found = subprocess.run(["find", base, "-name", "SKILL.md"],
                               capture_output=True, text=True).stdout.split()
        for f in sorted(found):
            got = _desc(f)
            if got and got[0] not in {o[0] for o in out}:
                out.append(got)
    return out


PROMPT = """You are choosing which skill, if any, to invoke for one user request.

Below are the skills available, each with the description its author wrote. You have
nothing else — no repository, no history, no knowledge of these tools beyond what is
written here.

{catalogue}

The user says:

    {query}

Answer with exactly two lines and nothing else:

SKILL: <the skill name, or the word none>
WHY: <one sentence, quoting the phrase in the description that decided it>
"""


def main():
    if "--list" in sys.argv:
        for qid, q, exp, why in QUERIES:
            print(f"{qid:<8}{exp:<16}{q}\n{'':8}{'':16}# {why}")
        return 0
    if "--choices" in sys.argv:
        for name, d in choices():
            print(f"{name:<18}{len(d):>5} chars")
        return 0
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    qid = sys.argv[1]
    row = next((r for r in QUERIES if r[0] == qid), None)
    if row is None:
        print(f"unknown query id {qid}; --list to see them", file=sys.stderr)
        return 2
    cat = "\n".join(f"- **{name}** — {d}" for name, d in choices())
    print(PROMPT.format(catalogue=cat, query=row[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
