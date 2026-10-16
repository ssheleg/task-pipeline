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
    # L3 review: inspect the paragraph that governs each decision, not keyword
    # presence elsewhere. These are bounded doctrine checks, not model behavior.
    refs = DOC.parent
    stages = (refs / "stages.md").read_text()
    gates = (refs / "gates.md").read_text()
    waves = (refs / "waves.md").read_text()
    iteration = (refs / "iteration.md").read_text()
    def paragraph(source, marker):
        return next(p for p in source.split("\n\n") if marker in p)
    for source, marker, label in (
        (stages, "Each gate is tagged", "stage type definition"),
        (text, "What arming does NOT change", "loop arming limit"),
        (gates, "This never licenses skipping a gate", "gate floor"),
    ):
        scope = paragraph(source, marker)
        ok("specific standing authorization" in scope and "act" in scope,
           label + " preserves existing act-specific authority")
    for source, marker, label in (
        (waves, "Sign-ins, consents", "waves human boundary"),
        (iteration, "Sign-ins, consents", "iteration human boundary"),
    ):
        scope = paragraph(source, marker)
        ok(all(term in scope for term in ("operator payments", "typed secrets", "remain human")),
           label + " keeps sign-ins, consents, operator payments and typed secrets human")
        ok("unless" not in scope and "standing authorization" not in scope,
           label + " does not exempt human-only acts through an outward-act grant")
    questions = paragraph(iteration, "In a round, the orchestrator")
    ok("human-owned questions" in questions and "batch" in questions,
       "question batch is restricted to human-owned questions")
    ok("external waits" in questions and "watchers" in questions and "owning Project" in questions,
       "question round routes external waits and Project asks separately")
    blocked = paragraph(text, "A block or an ambiguity stops")
    ok("owning Project" in blocked and "external waits" in blocked,
       "continuity does not label every unresolved node needs-operator")
    # Round 7 (N5): a fully blocked frontier names both of graph.py next's codes — `6` for
    # recorded watched waits only, `4` for any other barrier — here and in waves.md.
    flat = " ".join(blocked.split())
    ok("Exit `6` means every remaining dependency leaf is a recorded watched wait" in flat
       and "Exit `4` means a mixed, unclassified, running or parked barrier remains" in flat,
       "continuity names exit 6 (watched waits only) beside exit 4 for a blocked frontier")
    wave_next = " ".join(paragraph(waves, "`graph.py next --wave N` prints").split())
    ok("`6` that only recorded watched waits hold it" in wave_next and "`4`" in wave_next,
       "waves.md lists exit 6 for next --wave N")
    print(f"PASS: continuity.md — {CASES} cases")


if __name__ == "__main__":
    main()
