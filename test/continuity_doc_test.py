#!/usr/bin/env python3
"""The loop doctrine and the wait rule agree (`references/continuity.md`; CHANGELOG, Unreleased) — stdlib only.

continuity.md said loop mode was "Default off … Ask once at preflight" and listed
opening a PR among the acts that always need their own authorization, while a host's
standing instruction ("a free agent takes the next task") already armed the loop and let a
watcher merge. And the doctrine named only session-bound watchers, which die with the
session. These cases read the doctrine the way an agent does — by section — and fail on the
sentences that made the two rules contradict:

  * the always-gated list no longer carries "opening a PR"; a PR is armed by a specific
    standing authorization, the way build.md and gates.md already said;
  * a standing instruction the host carries is one of the named arming sources, cited in the
    ledger, and silence still arms nothing;
  * the acts a watcher may take unasked are named, and the outward ones stay gated;
  * a wait that can outlive the session goes on a durable trigger;
  * at the compaction signal the next task is written down, not started;
  * the rationalization row no longer makes "ask at preflight" the only arming;
  * Part 3 says where Observatory comes from.

Run bare: prints PASS and exits non-zero on the first failure.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = ROOT / "plugins" / "task-pipeline" / "skills" / "task-pipeline" / "references" / "continuity.md"
CASES = 0


def ok(cond, what):
    global CASES
    CASES += 1
    if not cond:
        print(f"FAIL: {what}")
        sys.exit(1)


def section(text, heading):
    m = re.search(rf"^## {re.escape(heading)}\s*$", text, re.M)
    ok(m is not None, f"continuity.md has the section '{heading}'")
    rest = text[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    return rest[:nxt.start()] if nxt else rest


def main():
    text = DOC.read_text(encoding="utf-8")
    limit = section(text, "The limit, before the capability")
    gated = [ln for ln in limit.splitlines() if "outward or irreversible" in ln.lower()]
    ok(gated, "the limit names the outward or irreversible acts")
    first = limit[limit.lower().index("outward or irreversible"):]
    first = first[:first.find("\n- ")] if "\n- " in first else first
    ok("opening a pr" not in first.lower(),
       "opening a PR is not among the acts that always need their own authorization")
    ok(re.search(r"standing instruction", limit, re.I), "a standing instruction is named as an arming source")
    ok("loop: armed by" in limit, "the ledger cites what armed the loop (`loop: armed by <source>`)")
    ok(re.search(r"[Ss]ilence (still )?arms nothing", limit), "silence still arms nothing")
    for act in ("merge", "release a lease", "rebase", "notify"):
        ok(act in limit.lower(), f"the acts a watcher may take unasked name '{act}'")
    for act in ("deploy", "publish", "tag", "send"):
        ok(act in limit.lower(), f"'{act}' stays named among the gated acts")
    ok("pull request" in limit.lower() or "a pr" in limit.lower(),
       "the limit says what arms opening a PR")
    ok(re.search(r"durable", text) and re.search(r"launchd|systemd|\bat\b one-shot", text),
       "a wait that outlives the session goes on a durable trigger")
    ok(re.search(r"outlive", text), "the doctrine names a wait that can outlive the session")
    ok(re.search(r"compaction signal", text, re.I) and re.search(r"next task", text),
       "at the compaction signal the next task is written down, not started")
    rows = [ln for ln in text.splitlines() if ln.startswith("| \"The operator obviously wants it to keep going")]
    ok(rows and "Ask once at preflight, or read `run.loop`." not in rows[0],
       "the rationalization row no longer makes asking at preflight the only arming")
    part3 = section(text, "Part 3 — workflow memory at the stage boundary")
    ok("project-observatory-dashboard" in part3, "Part 3 says where Observatory comes from")
    print(f"PASS: continuity.md — {CASES} cases")


if __name__ == "__main__":
    main()
