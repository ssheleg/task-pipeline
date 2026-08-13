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
    assert "suite passing" in err, "the reason does not say what is missing"
    assert "pipeline.json" in err, "the reason does not say how to make the flow readable"
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

# --- the stage is not a constant (the v1.50.0 defect) -----------------------

SIX_STAGE_LEDGER = (
    "stage: 3 build — gate auto — verdict pass — 2026-08-13T01:00:00Z\n"
    "stage: 4 tests — gate manual — verdict pass — 2026-08-13T01:10:00Z\n"
)


def run_with(command, ledger, pipeline=None):
    """Like `run`, but the project may declare its own flow."""
    with tempfile.TemporaryDirectory() as project:
        if ledger is not None:
            os.makedirs(os.path.join(project, ".task-pipeline"))
            with open(os.path.join(project, ".task-pipeline", "run.md"), "w") as fh:
                fh.write(ledger)
        if pipeline is not None:
            with open(os.path.join(project, "pipeline.json"), "w") as fh:
                json.dump(pipeline, fh)
        env = dict(os.environ, CLAUDE_PROJECT_DIR=project)
        payload = json.dumps({
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command},
        })
        proc = subprocess.run(["bash", GATE], input=payload, env=env,
                              capture_output=True, text=True)
        return proc.returncode, (proc.stderr or "")


def six_stage_project_can_release():
    """v1.50.0 matched `stage: 6` literally, so a six-stage flow could never tag."""
    code, err = run_with("git tag v1.0.0", SIX_STAGE_LEDGER,
                         {"stages": [{"id": i} for i in range(6)]})
    assert code == ALLOW, (
        "a six-stage project with a green tests stage at 4 was blocked — "
        "the gate is keyed to a stage NUMBER again. stderr: %s" % err.strip()[:200])


def declared_tests_stage_is_used():
    code, err = run_with("git tag v1.0.0",
                         "stage: 2 checks — gate auto — verdict pass — 2026-08-13T01:00:00Z\n",
                         {"stages": [{"id": 2, "state": "tests"}]})
    assert code == ALLOW, "the declared tests stage was ignored: %s" % err.strip()[:200]


def declared_tests_stage_not_passed_blocks():
    code, _ = run_with("git tag v1.0.0",
                       "stage: 2 checks — gate auto — verdict fail — 2026-08-13T01:00:00Z\n",
                       {"stages": [{"id": 2, "state": "tests"}]})
    assert code == BLOCK, "a failing declared tests stage let a tag through"


def unreadable_flow_still_refuses():
    """A run in flight with nothing reporting a suite is still a refusal."""
    code, err = run_with("git tag v1.0.0",
                         "stage: 5 build — gate auto — verdict pass — 2026-08-13T01:00:00Z\n")
    assert code == BLOCK, "the gate let a tag through because it could not read the flow"
    assert "pipeline.json" in err, "the refusal does not say how to become readable"


it("a six-stage project with green tests can release", six_stage_project_can_release)
it("the declared tests stage is the one that counts", declared_tests_stage_is_used)
it("a declared tests stage that failed still blocks", declared_tests_stage_not_passed_blocks)
it("an unreadable flow refuses, and says how to be readable", unreadable_flow_still_refuses)


# --- the claim must be corroborated ----------------------------------------

OBSERVED = {"stages": [{"id": 6, "state": "tests", "gate": {"command": "npm test"}}]}
CLAIM = "stage: 6 tests — gate manual — verdict pass — 2026-08-13T01:00:00Z\n"


def claim_alone_is_not_enough():
    code, err = run_with("git tag v1.0.0", CLAIM, OBSERVED)
    assert code == BLOCK, "the agent's own claim released the tag with nothing observing it"
    assert "the claim is the agent's own" in err, err.strip()[:200]


def observation_that_failed_blocks():
    led = CLAIM + 'gate:  6 — command "npm test" — exit 1 — 2026-08-13T01:05:00Z\n'
    code, err = run_with("git tag v1.0.0", led, OBSERVED)
    assert code == BLOCK, "a red observed run released the tag"
    assert "did not exit 0" in err, err.strip()[:200]


def claim_and_observation_agreeing_releases():
    led = CLAIM + 'gate:  6 — command "npm test" — exit 0 — 2026-08-13T01:05:00Z\n'
    code, err = run_with("git tag v1.0.0", led, OBSERVED)
    assert code == ALLOW, "a corroborated claim was blocked: %s" % err.strip()[:200]


def no_declared_command_degrades_to_the_claim():
    """Stated behaviour, not discovered: no command declared, no corroboration."""
    code, _ = run_with("git tag v1.0.0", CLAIM, {"stages": [{"id": 6, "state": "tests"}]})
    assert code == ALLOW, "a project declaring no gate command was blocked for not observing one"


it("the agent's claim alone does not release", claim_alone_is_not_enough)
it("an observed failure blocks even when the claim says pass", observation_that_failed_blocks)
it("claim and observation agreeing releases", claim_and_observation_agreeing_releases)
it("no declared command degrades to the claim, deliberately", no_declared_command_degrades_to_the_claim)

# --- the observer: what actually ran, written down --------------------------

OBSERVER = os.path.join(ROOT, "plugins", "task-pipeline", "hooks", "gate-observer.sh")


def observe(command, pipeline, ledger="", event="PostToolUse", error=None):
    """Run the observer the way Claude Code does, and return the ledger after."""
    with tempfile.TemporaryDirectory() as project:
        os.makedirs(os.path.join(project, ".task-pipeline"))
        path = os.path.join(project, ".task-pipeline", "run.md")
        with open(path, "w") as fh:
            fh.write(ledger)
        if pipeline is not None:
            with open(os.path.join(project, "pipeline.json"), "w") as fh:
                json.dump(pipeline, fh)
        payload = {"hook_event_name": event, "tool_name": "Bash",
                   "tool_input": {"command": command}}
        if error is not None:
            payload["error"] = error
        subprocess.run(["bash", OBSERVER], input=json.dumps(payload),
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=project),
                       capture_output=True, text=True)
        return open(path, encoding="utf-8").read()


def observer_records_a_green_run():
    out = observe("npm test", OBSERVED)
    assert 'gate:  6 — command "npm test" — exit 0' in out, "nothing was recorded: %r" % out


def observer_records_a_red_run():
    """It records, it never judges. A hook that hid a red result would read as
    'the suite was never run', which is the opposite of what happened."""
    out = observe("npm test", OBSERVED, event="PostToolUseFailure", error="exit 1")
    assert "exit 1" in out, "a failing run was not recorded: %r" % out


def observer_ignores_anything_not_declared():
    for cmd in ("npm test --watch", 'echo "npm test"', "npm run build", "git status"):
        out = observe(cmd, OBSERVED)
        assert "gate:" not in out, "a fabricated observation from %r: %r" % (cmd, out)


def observer_is_silent_without_a_declaration():
    out = observe("npm test", {"stages": [{"id": 6, "state": "tests"}]})
    assert "gate:" not in out, "recorded an observation nobody asked for: %r" % out
    out = observe("npm test", None)
    assert "gate:" not in out, "recorded without a pipeline.json: %r" % out


def observer_appends_and_never_rewrites():
    led = "stage: 0 intake — gate manual — verdict pass — 2026-08-13T01:00:00Z\n"
    out = observe("npm test", OBSERVED, ledger=led)
    assert out.startswith(led), "the ledger was rewritten rather than appended to"


it("the observer records a green run", observer_records_a_green_run)
it("the observer records a red run too — it never judges", observer_records_a_red_run)
it("only the declared command is observed, exactly", observer_ignores_anything_not_declared)
it("no declaration, no observation", observer_is_silent_without_a_declaration)
it("the ledger is appended to, never rewritten", observer_appends_and_never_rewrites)

def a_later_red_beats_an_earlier_green():
    """"Some run was green" is true of every repository that has ever been red."""
    led = (CLAIM
           + 'gate:  6 — command "npm test" — exit 0 — 2026-08-13T01:05:00Z\n'
           + 'gate:  6 — command "npm test" — exit 1 — 2026-08-13T01:20:00Z\n')
    code, err = run_with("git tag v1.0.0", led, OBSERVED)
    assert code == BLOCK, "an earlier green satisfied the gate over a later red"
    assert "most recent" in err, err.strip()[:200]


def a_later_green_clears_an_earlier_red():
    led = (CLAIM
           + 'gate:  6 — command "npm test" — exit 1 — 2026-08-13T01:05:00Z\n'
           + 'gate:  6 — command "npm test" — exit 0 — 2026-08-13T01:20:00Z\n')
    code, err = run_with("git tag v1.0.0", led, OBSERVED)
    assert code == ALLOW, "a fixed suite could not release: %s" % err.strip()[:200]


it("a later red beats an earlier green", a_later_red_beats_an_earlier_green)
it("a later green clears an earlier red", a_later_green_clears_an_earlier_red)

# --- the run's own lifecycle, written down as it happens --------------------

LIFECYCLE = os.path.join(ROOT, "plugins", "task-pipeline", "hooks", "run-lifecycle.sh")
BUILDGATE = os.path.join(ROOT, "plugins", "task-pipeline", "hooks", "build-gate.sh")


def lifecycle(payload, ledger, pipeline=None):
    with tempfile.TemporaryDirectory() as project:
        os.makedirs(os.path.join(project, ".task-pipeline"))
        path = os.path.join(project, ".task-pipeline", "run.md")
        open(path, "w").write(ledger)
        if pipeline is not None:
            json.dump(pipeline, open(os.path.join(project, "pipeline.json"), "w"))
        subprocess.run(["bash", LIFECYCLE], input=json.dumps(payload),
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=project),
                       capture_output=True, text=True)
        return open(path, encoding="utf-8").read()


OPEN_RUN = "stage: 3 spec — gate auto — verdict pass — 2026-08-13T01:00:00Z\n"
CLOSED_RUN = OPEN_RUN + "stage: 10 acceptance — gate manual — verdict pass — 2026-08-13T02:00:00Z\n"


def compaction_is_recorded():
    """The ledger exists because compaction happens, and could not show it."""
    out = lifecycle({"hook_event_name": "PreCompact", "trigger": "auto"}, OPEN_RUN)
    assert "event: compact — auto" in out, out


def an_abandoned_run_is_recorded():
    out = lifecycle({"hook_event_name": "SessionEnd", "reason": "logout"}, OPEN_RUN)
    assert "event: session-end" in out, out
    assert "not closed" in out, out


def a_finished_run_is_not_called_abandoned():
    """Recording an end for a run that reached acceptance fills checkup with noise."""
    out = lifecycle({"hook_event_name": "SessionEnd", "reason": "logout"}, CLOSED_RUN)
    assert "session-end" not in out, "a run that closed as intended was filed as abandoned"


def a_subagent_stop_is_observed():
    out = lifecycle({"hook_event_name": "SubagentStop", "agent_type": "general-purpose"}, OPEN_RUN)
    assert "event: subagent — general-purpose" in out, out


def it_never_writes_a_hand_line():
    """`hand:` carries judgements only the agent holds; a hook filling them in
    would fabricate the very evidence the line exists to provide."""
    out = lifecycle({"hook_event_name": "SubagentStop", "agent_type": "x"}, OPEN_RUN)
    assert "hand:" not in out, "a hook fabricated a hand-back accounting"


def separators_in_input_cannot_break_the_grammar():
    out = lifecycle({"hook_event_name": "SubagentStop", "agent_type": "a — b\nc"}, OPEN_RUN)
    lines = [l for l in out.splitlines() if l.startswith("event:")]
    assert len(lines) == 1, "one event became %d lines" % len(lines)
    assert lines[0].count("—") == 2, "an em dash from the payload broke the shape: %s" % lines[0]


def no_ledger_no_lifecycle():
    with tempfile.TemporaryDirectory() as project:
        r = subprocess.run(["bash", LIFECYCLE],
                           input=json.dumps({"hook_event_name": "PreCompact", "trigger": "auto"}),
                           env=dict(os.environ, CLAUDE_PROJECT_DIR=project),
                           capture_output=True, text=True)
        assert r.returncode == 0
        assert not os.path.exists(os.path.join(project, ".task-pipeline"))


it("a compaction is recorded at the boundary", compaction_is_recorded)
it("a run whose session ended unclosed is recorded", an_abandoned_run_is_recorded)
it("a run that reached acceptance is not called abandoned", a_finished_run_is_not_called_abandoned)
it("a subagent stopping is observed", a_subagent_stop_is_observed)
it("it never writes a hand: line — those are judgements it does not have", it_never_writes_a_hand_line)
it("payload text cannot break the ledger's grammar", separators_in_input_cannot_break_the_grammar)
it("no ledger, no lifecycle", no_ledger_no_lifecycle)


# --- editing the product before the plan is agreed --------------------------

def build_gate(path, ledger, pipeline=None):
    with tempfile.TemporaryDirectory() as project:
        os.makedirs(os.path.join(project, ".task-pipeline"))
        open(os.path.join(project, ".task-pipeline", "run.md"), "w").write(ledger)
        if pipeline is not None:
            json.dump(pipeline, open(os.path.join(project, "pipeline.json"), "w"))
        r = subprocess.run(["bash", BUILDGATE], input=json.dumps({
            "hook_event_name": "PreToolUse", "tool_name": "Edit",
            "tool_input": {"file_path": os.path.join(project, path)}}),
            env=dict(os.environ, CLAUDE_PROJECT_DIR=project), capture_output=True, text=True)
        out = (r.stdout or "").strip()
        return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out else None


BUILD_FLOW = {"stages": [{"id": 5, "state": "build"}]}


def editing_source_before_build_asks():
    assert build_gate("src/app.js", OPEN_RUN, BUILD_FLOW) == "ask"


def the_pipelines_own_artefacts_are_never_gated():
    for p in ("docs/ux/scenarios.md", "docs/superpowers/brief.md",
              ".task-pipeline/run.md", "README.md", "CHANGELOG.md"):
        assert build_gate(p, OPEN_RUN, BUILD_FLOW) is None, \
            "%s is what stages 0-4 are FOR, and the gate asked about it" % p


def once_the_build_stage_is_entered_it_is_silent():
    led = OPEN_RUN + "stage: 5 build — gate auto — 2026-08-13T01:30:00Z\n"
    assert build_gate("src/app.js", led, BUILD_FLOW) is None, \
        "the gate fought stage 5, which is where code is written"


def an_unresolvable_flow_is_silent():
    """A question nobody can act on is worse than none — and keying it to a stage
    NUMBER is the defect v1.50.0 shipped in the release gate."""
    assert build_gate("src/app.js", "stage: 1 docs — gate auto — verdict pass — x\n") is None


def no_run_no_gate():
    with tempfile.TemporaryDirectory() as project:
        r = subprocess.run(["bash", BUILDGATE], input=json.dumps({
            "hook_event_name": "PreToolUse", "tool_name": "Edit",
            "tool_input": {"file_path": os.path.join(project, "src/app.js")}}),
            env=dict(os.environ, CLAUDE_PROJECT_DIR=project), capture_output=True, text=True)
        assert (r.stdout or "").strip() == "", "gated a repository running no pipeline"


it("editing source before the build stage asks", editing_source_before_build_asks)
it("the pipeline's own artefacts are never gated", the_pipelines_own_artefacts_are_never_gated)
it("once the build stage is entered the gate is silent", once_the_build_stage_is_entered_it_is_silent)
it("an unresolvable flow is silent", an_unresolvable_flow_is_silent)
it("no run, no gate", no_run_no_gate)

if failures:
    for f in failures:
        print("FAIL: " + f)
    print("%d failure(s) out of %d checks" % (len(failures), checks))
    sys.exit(1)
print("OK (%d checks)" % checks)
