#!/usr/bin/env python3
"""Fixtures for the stage-7 release gate — plugins/task-pipeline/hooks/release-gate.sh.

The gate refuses an outward, irreversible act while the run ledger records no
passing stage 6. Three properties carry this file, and each one is a way the gate
could be worse than useless:

  * a MISS lets a tag go public with the suite red, which is the whole defect;
  * a FALSE BLOCK stops an ordinary commit, and a gate that fights stage 5's own
    build loop is removed within the day;
  * a SILENT PASS in a project with no ledger would make every repository on the
    machine answer to a pipeline it is not running.

The hook is run as a process, with real JSON on stdin, because that is the layer
that repeats. Exit 2 blocks in Claude Code; every other code does not.
"""

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GATE = os.path.join(ROOT, "plugins", "task-pipeline", "hooks", "release-gate.sh")

BLOCK = 2
ALLOW = 0

checks = 0
failures = []

PASSED_LEDGER = (
    "Run: `something` · 2026-08-12\n"
    "stage: 5 build — gate auto — verdict pass — 2026-08-12T10:00:00Z\n"
    "stage: 6 tests — gate manual — verdict pass — 2026-08-12T10:30:00Z\n"
)
FAILED_LEDGER = (
    "Run: `something` · 2026-08-12\n"
    "stage: 5 build — gate auto — verdict pass — 2026-08-12T10:00:00Z\n"
    "stage: 6 tests — gate manual — verdict fail — 2026-08-12T10:30:00Z\n"
)
NO_STAGE6_LEDGER = (
    "Run: `something` · 2026-08-12\n"
    "stage: 5 build — gate auto — verdict pass — 2026-08-12T10:00:00Z\n"
)


def run(command, ledger):
    """Run the gate the way Claude Code runs it. `ledger=None` means no run."""
    with tempfile.TemporaryDirectory() as project:
        if ledger is not None:
            os.makedirs(os.path.join(project, ".task-pipeline"))
            with open(os.path.join(project, ".task-pipeline", "run.md"), "w") as fh:
                fh.write(ledger)
        env = dict(os.environ, CLAUDE_PROJECT_DIR=project)
        payload = json.dumps({
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command},
        })
        proc = subprocess.run(["bash", GATE], input=payload, env=env,
                              capture_output=True, text=True)
        return proc.returncode, (proc.stderr or "")


def it(name, fn):
    global checks
    checks += 1
    try:
        fn()
    except AssertionError as exc:
        failures.append("%s: %s" % (name, exc))


def expect(command, ledger, code, why):
    got, err = run(command, ledger)
    assert got == code, "%s\n  command: %s\n  expected exit %d, got %d\n  stderr: %s" % (
        why, command, code, got, err.strip()[:300])


# --- the acts that must be refused ------------------------------------------

it("a tag with the suite red is refused",
   lambda: expect("git tag v1.2.3", FAILED_LEDGER, BLOCK,
                  "a tag went out over a failing stage 6"))

it("a tag with no stage 6 at all is refused",
   lambda: expect("git tag v1.2.3", NO_STAGE6_LEDGER, BLOCK,
                  "a tag went out before the suite was ever run"))

it("pushing tags is refused",
   lambda: expect("git push --tags", NO_STAGE6_LEDGER, BLOCK, "a tag push slipped through"))

it("pushing a version refspec is refused",
   lambda: expect("git push origin v1.2.3", NO_STAGE6_LEDGER, BLOCK,
                  "pushing the tag by name slipped through"))

it("gh release create is refused",
   lambda: expect("gh release create v1.2.3 --notes x", NO_STAGE6_LEDGER, BLOCK,
                  "a GitHub release slipped through"))

it("npm publish is refused",
   lambda: expect("npm publish --access public", NO_STAGE6_LEDGER, BLOCK,
                  "a publish slipped through"))

it("git -C elsewhere tag is still a tag",
   lambda: expect("git -C ../other tag v9.9.9", NO_STAGE6_LEDGER, BLOCK,
                  "the `-C` spelling skipped the gate, exactly as it once did in agent-sync"))

def refusal_is_a_redirection():
    """A refusal with no next step is how an operator learns to remove a gate."""
    _, err = run("git tag v1", NO_STAGE6_LEDGER)
    assert "stage 6" in err, "the reason does not say what is missing"
    assert "run.md" in err, "the reason does not name the ledger"
    assert "без пайплайна" in err, "the reason does not name the opt-out"


it("the refusal names the act, the ledger and the opt-out", refusal_is_a_redirection)


# --- the acts that must NOT be touched --------------------------------------

it("an ordinary commit is not a release",
   lambda: expect("git commit -m 'wip'", NO_STAGE6_LEDGER, ALLOW,
                  "the gate fought stage 5's own build loop"))

it("a branch push is not a release",
   lambda: expect("git push origin main", NO_STAGE6_LEDGER, ALLOW,
                  "an ordinary push was gated"))

it("listing and deleting tags are not releasing",
   lambda: [expect(c, NO_STAGE6_LEDGER, ALLOW, "a read was gated")
            for c in ("git tag", "git tag -l 'v1.*'", "git tag -d v1.0.0")])

it("the word tag in another command is not a tag",
   lambda: [expect(c, NO_STAGE6_LEDGER, ALLOW, "a substring was read as a subcommand")
            for c in ("git log --grep=tag", "echo 'git tag v1'", "grep -r tag docs/")])

it("npm test is not npm publish",
   lambda: expect("npm test", NO_STAGE6_LEDGER, ALLOW, "the suite itself was gated"))

# --- and the whole thing is inert where no pipeline runs ---------------------

it("with NO ledger the gate is silent, even for a tag",
   lambda: expect("git tag v1.2.3", None, ALLOW,
                  "installing this plugin changed a repository that runs no pipeline"))

it("with stage 6 passed the release proceeds",
   lambda: expect("git tag v1.2.3", PASSED_LEDGER, ALLOW,
                  "a legitimate release was blocked — the gate must open, not only close"))

it("a passing stage 6 recorded later in the file still counts",
   lambda: expect("npm publish", PASSED_LEDGER + "stage: 7 deploy — gate manual — verdict pass — x\n",
                  ALLOW, "the gate stopped reading at the first stage line"))

if failures:
    for f in failures:
        print("FAIL: " + f)
    print("%d failure(s) out of %d checks" % (len(failures), checks))
    sys.exit(1)
print("OK (%d checks)" % checks)
