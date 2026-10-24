#!/usr/bin/env python3
"""release_impact.py: the release impact card as a stage 7 gate and a stage 8 record.
Every refusal is planted and must fail with its own message; every pass is a real card,
including the shipped template once its TODOs are filled. Standard library only."""
import json
import pathlib
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "plugins/task-pipeline/skills/task-pipeline"
RI = SK / "scripts/release_impact.py"
count, failures = 0, []


def ok(cond, msg):
    global count
    count += 1
    if not cond:
        failures.append(msg)
        print("FAIL  " + msg)


def run(*args):
    r = subprocess.run([sys.executable, str(RI), *map(str, args)], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


WHO = """## 1. Who is affected and how

- **Segments:** npm installers (about 900 weekly downloads) and the operator's three machines
- **What changes:** a new optional field in pipeline.json; nothing renamed
- **Breaks for existing users:** no
- **Rollout:** all at once on the tag
- **Timing:** Tuesday morning, so the watch window falls in working hours
"""
TRACKING = """## 2. Tracking

- **Signals:** registry version readback, clean-directory install, new issues
- **Baseline:** 4 open issues; the last install smoke test passed
- **Where:** `npm view task-pipeline-skill version`, the release workflow, the issue list
- **Watch window:** 72 h after the tag
"""
ALERTING = """## 3. Alerting

- **Fires when:** the release workflow's install smoke test fails, or an issue is filed
- **Receives:** the maintainer, by mail from GitHub
- **Seen firing:** yes, the smoke test failed a release once
"""
ROLLBACK = """## 4. Rollback or hotfix

- **Rollback:** re-pin the previous version in every consumer, then `npm deprecate` the bad one
- **Time to roll back:** about 15 minutes
- **Data reversible:** yes, nothing is stored
- **Kill switch:** n/a: a package has no runtime flag
- **Hotfix path:** a patch release through the same pipeline
- **Decision trigger:** roll back if an install fails or a breaking issue is filed within 72 h
"""
HEAD = "# Release impact: v1.2.3\n\nschema: release-impact/1\nrelease: v1.2.3\nusers: %s\ndate: 2026-10-24\n\n"


def card(users="external", who=WHO, tracking=TRACKING, alerting=ALERTING, rollback=ROLLBACK, extra=""):
    return HEAD % users + "\n".join(s for s in (who, tracking, alerting, rollback) if s) + extra


with tempfile.TemporaryDirectory() as d:
    d = pathlib.Path(d)
    n = [0]

    def check(text, *args):
        n[0] += 1
        p = d / ("card%d.md" % n[0])
        p.write_text(text, encoding="utf-8")
        return run("check", p, *args)

    # --- positives -----------------------------------------------------------------------
    rc, out, _ = check(card(), "--users", "external")
    ok(rc == 0 and "PASS" in out, f"a full card passes ({rc} {out!r})")
    rc, out, _ = check(card(who="## 1. Who is affected and how\n\nn/a: a build-only change, no shipped byte differs\n"),
                       "--users", "external")
    ok(rc == 0 and "n/a: a build-only change" in out, f"section 1 as n/a with a reason passes, its reason printed ({rc} {out!r})")
    rc, out, _ = check(card(alerting=ALERTING.replace("yes, the smoke test failed a release once", "never")))
    ok(rc == 0 and "never been seen firing" in out, f"an alert never seen firing passes and is said to be untested ({rc} {out!r})")
    rc, out, _ = check(card(rollback=ROLLBACK.replace("roll back if an install fails", "откатить, если установка падает")))
    ok(rc == 0, f"a decision trigger in Russian states its condition ({rc} {out!r})")
    rc, out, _ = run("check", d / "absent.md", "--users", "none")
    ok(rc == 0 and "not owed" in out, f"users none and no card: PASS, the card is not owed ({rc} {out!r})")
    pj = d / "pipeline.json"
    pj.write_text(json.dumps({"release": {"enabled": True, "users": "internal"}}))
    rc, out, _ = check(card(users="internal"), "--pipeline", pj)
    ok(rc == 0, f"--pipeline reads release.users and agrees with the card ({rc} {out!r})")
    rc, out, _ = check(card(extra="\n## Outcome\n\n- **Read:** installs clean, no new issue\n- **Result:** held\n"), "--outcome")
    ok(rc == 0, f"stage 8: an Outcome with Result held passes ({rc} {out!r})")
    rc, out, _ = check(card(extra="\n## Outcome\n\n- **Result:** watching until 2026-10-27, a scheduled job reads it\n"), "--outcome")
    ok(rc == 0 and "still open" in out, f"stage 8: watching passes and says the window is open ({rc} {out!r})")
    rc, out, _ = check(card(), "--json")
    js = json.loads(out) if out.strip().startswith("{") else {}
    ok(js.get("verdict") == "PASS" and js.get("users") == "external"
       and set(js.get("sections", {}).values()) == {"answered"}, f"--json carries verdict, users and section states ({rc} {out!r})")
    rc, out, _ = check(card(users=""), "--json")
    js = json.loads(out) if out.strip().startswith("{") else {}
    ok(rc == 0 and js.get("users") == "external" and any("unknown" in x for x in js.get("notes", [])),
       f"unknown users are treated as external and said so ({rc} {out!r})")

    # The shipped template, its TODOs filled with the field values above, passes: the
    # template and the checker describe one shape.
    tpl = (SK / "templates/release-impact.md").read_text(encoding="utf-8")
    values = {}
    for block in (WHO, TRACKING, ALERTING, ROLLBACK):
        for m in re.finditer(r"^- \*\*([^*]+?):\*\* (.+)$", block, re.M):
            values[m.group(1)] = m.group(2)
    filled = []
    for line in tpl.splitlines():
        m = re.match(r"^- \*\*([^*]+?):\*\* TODO", line)
        if m:
            line = "- **%s:** %s" % (m.group(1), values[m.group(1)])
        elif line.startswith("# Release impact: TODO"):
            line = "# Release impact: v1.2.3"
        elif re.match(r"^(release|users|date): TODO", line):
            line = {"release": "release: v1.2.3", "users": "users: external", "date": "date: 2026-10-24"}[line.split(":")[0]]
        filled.append(line)
    rc, out, _ = check("\n".join(filled) + "\n", "--users", "external")
    ok(rc == 0, f"the shipped template, filled, passes ({rc} {out!r})")
    rc, out, _ = check(tpl, "--users", "external")
    ok(rc == 1 and "TODO" in out, f"the shipped template as seeded fails on its TODOs ({rc} {out!r})")

    # --- planted negatives: each must fail, with its own message -------------------------
    rc, out, _ = run("check", d / "absent.md", "--users", "external")
    ok(rc == 3 and "NOT_RUN" in out and "owed" in out, f"no card where one is owed is NOT_RUN, never PASS ({rc} {out!r})")
    rc, out, _ = run("check", d / "absent.md")
    ok(rc == 3 and "unknown" in out, f"no card and unknown users is NOT_RUN, the unknown said ({rc} {out!r})")
    rc, out, _ = check(card(alerting=""))
    ok(rc == 1 and "no section '3. Alerting'" in out, f"a missing section fails, named ({rc} {out!r})")
    rc, out, _ = check(card(tracking="## 2. Tracking\n\n<!-- signals, baseline, where, watch window -->\n"))
    ok(rc == 1 and "'2. Tracking' is empty" in out, f"a section holding only a comment is empty ({rc} {out!r})")
    rc, out, _ = check(card(who="## 1. Who is affected and how\n\nn/a\n"))
    ok(rc == 1 and "n/a with no reason" in out, f"a section n/a without its reason fails ({rc} {out!r})")
    rc, out, _ = check(card(who="## 1. Who is affected and how\n\nn/a:\n"))
    ok(rc == 1 and "n/a with no reason" in out, f"`n/a:` with nothing after it fails ({rc} {out!r})")
    rc, out, _ = check(card(rollback=ROLLBACK.replace("n/a: a package has no runtime flag", "n/a")))
    ok(rc == 1 and "`kill switch` is n/a with no reason" in out, f"a field n/a without its reason fails ({rc} {out!r})")
    rc, out, _ = check(card(who=WHO.replace("- **Breaks for existing users:** no", "- **Breaks for existing users:** TODO")))
    ok(rc == 1 and "TODO left" in out, f"a TODO left in the card fails ({rc} {out!r})")
    rc, out, _ = check(card(tracking=TRACKING.replace("- **Watch window:** 72 h after the tag\n", "")))
    ok(rc == 1 and "no watch window" in out, f"tracking without a watch window fails ({rc} {out!r})")
    rc, out, _ = check(card(tracking=TRACKING.replace("72 h after the tag", "n/a: we do not watch")))
    ok(rc == 1 and "no watch window" in out, f"a watch window answered n/a fails ({rc} {out!r})")
    rc, out, _ = check(card(tracking="## 2. Tracking\n\nn/a: nothing to watch\n"))
    ok(rc == 1 and "cannot be n/a" in out, f"tracking n/a on a release with users fails ({rc} {out!r})")
    rc, out, _ = check(card(alerting="## 3. Alerting\n\nn/a: we would hear about it\n"))
    ok(rc == 1 and "cannot be n/a" in out, f"alerting n/a on a release with users fails ({rc} {out!r})")
    rc, out, _ = check(card(rollback="## 4. Rollback or hotfix\n\nn/a: it will not need one\n"))
    ok(rc == 1 and "cannot be n/a" in out, f"rollback n/a on a release with users fails ({rc} {out!r})")
    rc, out, _ = check(card(rollback=ROLLBACK.replace(
        "- **Decision trigger:** roll back if an install fails or a breaking issue is filed within 72 h\n", "")))
    ok(rc == 1 and "no decision trigger" in out, f"rollback without a decision trigger fails ({rc} {out!r})")
    rc, out, _ = check(card(rollback=ROLLBACK.replace(
        "roll back if an install fails or a breaking issue is filed within 72 h", "to be decided")))
    ok(rc == 1 and "no decision trigger" in out, f"a decision trigger that states no condition fails ({rc} {out!r})")
    rc, out, _ = check(card(alerting=ALERTING.replace("- **Seen firing:** yes, the smoke test failed a release once\n", "")))
    ok(rc == 1 and "ever seen firing" in out, f"alerting that does not say whether it ever fired fails ({rc} {out!r})")
    rc, out, _ = check(card().replace("schema: release-impact/1", "schema: release-impact/0"))
    ok(rc == 1 and "not release-impact/1" in out, f"a card of another schema fails ({rc} {out!r})")
    rc, out, _ = check(card(users="nobody"))
    ok(rc == 1 and "users is one of" in out, f"a users value outside the three fails ({rc} {out!r})")
    rc, out, _ = check(card(users="none"), "--users", "external")
    ok(rc == 1 and "card says users: none" in out, f"a card disagreeing with the project about users fails ({rc} {out!r})")
    rc, out, _ = check(card(extra="\n" + TRACKING))
    ok(rc == 1 and "appears twice" in out, f"a section written twice fails ({rc} {out!r})")
    rc, out, _ = check(card(), "--outcome")
    ok(rc == 1 and "no `## Outcome`" in out, f"stage 8 without an Outcome fails ({rc} {out!r})")
    rc, out, _ = check(card(extra="\n## Outcome\n\n- **Result:** looks fine\n"), "--outcome")
    ok(rc == 1 and "`Result:` is one of" in out, f"stage 8 with a Result outside the four fails ({rc} {out!r})")
    rc, out, _ = check(card(extra="\n<!--\n## Outcome\n\n- **Result:** held\n-->\n"), "--outcome")
    ok(rc == 1 and "no `## Outcome`" in out, f"an Outcome inside a comment is not an Outcome ({rc} {out!r})")
    rc, _, err = run("check", d, "--users", "external")
    ok(rc == 2 and "cannot read" in err, f"an unreadable card is a usage error, exit 2 ({rc} {err!r})")
    bad = d / "bad.json"
    bad.write_text("{not json")
    rc, _, err = run("check", d / "absent.md", "--pipeline", bad)
    ok(rc == 2 and "bad.json" in err, f"a pipeline.json that is not JSON is exit 2 ({rc} {err!r})")
    bad.write_text(json.dumps({"release": {"enabled": True, "users": "everyone"}}))
    rc, _, err = run("check", d / "absent.md", "--pipeline", bad)
    ok(rc == 2 and "release.users" in err, f"a release.users outside the three is exit 2 ({rc} {err!r})")
    rc, _, _ = run()
    ok(rc == 2, f"no subcommand is a usage error, exit 2 ({rc})")
    rc, _, _ = run("check", d / "absent.md", "--users", "everyone")
    ok(rc == 2, f"--users outside the three is a usage error, exit 2 ({rc})")

# --- the wiring: the doctrine names the gate where a run will read it --------------------
stages = (SK / "references/stages.md").read_text(encoding="utf-8")
s7 = re.sub(r"\s+", " ", stages[stages.index("## 7 "):stages.index("## 8 ")])
s8 = re.sub(r"\s+", " ", stages[stages.index("## 8 "):stages.index("## 9 ")])
ok("release-impact.md" in s7 and "release_impact.py check" in s7, "stages.md stage 7 GATE owes the card and names its command")
ok("release-impact.md" in s8 and "decision trigger" in s8 and "--outcome" in s8,
   "stages.md stage 8 watches the card's signals, acts on its trigger and records the outcome")
for f in ("stage-07-lint-deploy.md", "stage-08-post-deploy.md"):
    ok("release-impact.md" in (SK / "references" / f).read_text(encoding="utf-8"), f"references/{f} carries the card's step")
schema = json.loads((SK / "pipeline.schema.json").read_text(encoding="utf-8"))
users = schema["definitions"]["release"]["properties"].get("users", {})
ok(users.get("enum") == ["external", "internal", "none"], f"pipeline.schema.json declares release.users ({users.get('enum')})")
ex = json.loads((SK / "pipeline.example.json").read_text(encoding="utf-8"))
ok(ex.get("release", {}).get("users") in ("external", "internal", "none"), "pipeline.example.json shows release.users")
doc = (SK / "references/release-impact.md").read_text(encoding="utf-8")
ok("\u2014" not in doc and "\u2014" not in tpl, "the doctrine and the template carry no em dash")

if failures:
    print("FAIL: %d of %d release impact checks" % (len(failures), count))
    sys.exit(1)
print("PASS: release_impact.py, %d cases" % count)
