#!/usr/bin/env bash
# PreToolUse — the stage-7 gate, made mechanical.
#
# `stages.md` already says a release does not leave stage 7 until the full suite
# is green at the tests stage. Until now that was a sentence an agent reads and a
# person hopes was obeyed; the tag is public before anybody can check. This
# refuses the irreversible act while the run's own ledger says otherwise.
#
# THREE DELIBERATE NARROWNESSES, each one the difference between a gate people
# keep and a gate people rip out:
#
#   1. Only OUTWARD acts. `git tag`, a tag push, `gh release create`, `npm
#      publish`. Ordinary commits are how stage 5 works — gating them would fight
#      the pipeline's own build loop and be gone within a day.
#   2. Only in a project that is running a pipeline. No `.task-pipeline/run.md`
#      means exit 0 before anything else is read, so installing this plugin
#      changes nothing anywhere else.
#   3. Only what the ledger SAYS, plus what a hook OBSERVED. Nothing here reruns a
#      suite.
#
# WHICH STAGE IS THE TESTS STAGE IS NOT A CONSTANT, and v1.50.0 shipped it as one.
# It matched `stage: 6` literally, so a project whose flow has six stages — tests
# at stage 4, everything green — could never tag anything again. The pipeline's own
# `progress.md` says the rail "is computed, never eleven" because a host project
# replaces the flow; a gate keyed to a stage number is the same error with worse
# consequences, because a wrong rail misinforms and a wrong gate stops the work.
# The stage is now resolved from `pipeline.json` (a stage whose `state` is `tests`,
# or one declaring `gate.command`), and failing that from the ledger by name. When
# it cannot be resolved at all the gate still REFUSES — a run is in flight and
# nothing in it reports a suite passing, and "we could not tell, so we let it go"
# is exactly what a release gate exists to refuse — but the reason says how to make
# the flow readable, because a refusal with no next step is one that gets removed.
#
# AND THE CLAIM IS CORROBORATED. `stage: … verdict pass` is typed by the agent this
# gate constrains, so on its own the gate confirms an assertion with itself. Where
# the stage declares `gate.command`, `hooks/gate-observer.sh` records the OBSERVED
# exit code of that command as a `gate:` line, and both must agree. Declare no
# command and the gate degrades to the claim alone — stated here rather than
# discovered.
#
# Exit 2 blocks the call and shows stderr as the reason. Any other non-zero code
# is NON-blocking in Claude Code, so an internal failure exits 2 as well: a
# crashing gate that fails open is worse than no gate, because it reads as one.
set -uo pipefail

input=$(cat 2>/dev/null || true)

project="${CLAUDE_PROJECT_DIR:-$PWD}"
ledger="$project/.task-pipeline/run.md"

decide() {
  # The payload travels in the environment, NOT on stdin: the heredoc below IS
  # stdin for `python3 -`, so a script fed that way can never also read the hook's
  # JSON from there. Watched failing — the gate allowed every release, silently,
  # because `sys.stdin.read()` came back empty and an empty payload is a skip.
  HOOK_INPUT="$input" python3 - "$ledger" "$project" <<'PY'
import json, shlex, sys, os, re

ledger, project = sys.argv[1], sys.argv[2]
raw = os.environ.get("HOOK_INPUT", "")
try:
    data = json.loads(raw)
except Exception:
    print("skip"); raise SystemExit(0)

cmd = ((data.get("tool_input") or {}).get("command") or "")
try:
    tokens = shlex.split(cmd)
except ValueError:
    tokens = cmd.split()


def outward(tokens):
    """Is this an act that other people can see the moment it succeeds?"""
    low = [t.lower() for t in tokens]
    for i, t in enumerate(low):
        rest = low[i + 1:]
        # `git -C dir -c k=v tag v1` — the subcommand is the first token after
        # git that is not a flag or a flag's value. Tokenised rather than matched
        # as a substring: `git log --grep=tag` must not count.
        if t.endswith("git"):
            j = 0
            while j < len(rest):
                if rest[j] in ("-C", "-c", "--git-dir", "--work-tree"):
                    j += 2; continue
                if rest[j].startswith("-"):
                    j += 1; continue
                break
            if j < len(rest):
                sub = rest[j]
                args = rest[j + 1:]
                if sub == "tag" and not any(a in ("-d", "--delete", "-l", "--list") for a in args):
                    if any(not a.startswith("-") for a in args):
                        return "git tag"
                if sub == "push":
                    if any(a in ("--tags", "--follow-tags") for a in args):
                        return "git push --tags"
                    if any(a.startswith("refs/tags/") or re.fullmatch(r"v?\d+\.\d+\.\d+.*", a) for a in args):
                        return "git push <tag>"
        if t.endswith("gh") and rest[:2] == ["release", "create"]:
            return "gh release create"
        if t.endswith("npm") and "publish" in rest:
            return "npm publish"
    return None


act = outward(tokens)
if not act:
    print("skip"); raise SystemExit(0)

if not os.path.exists(ledger):
    print("skip"); raise SystemExit(0)

try:
    text = open(ledger, encoding="utf-8").read()
except Exception:
    # The ledger exists and cannot be read: this project IS governed and the
    # gate cannot tell. Fail closed, and say which file to look at.
    print("block\t%s\tthe run ledger could not be read" % act); raise SystemExit(0)

stage_lines = [l.strip() for l in text.splitlines() if l.strip().startswith("stage:")]


def declared_test_stage():
    """The tests stage, from the project's own flow. `(id, command)` or None."""
    try:
        cfg = json.load(open(os.path.join(project, "pipeline.json"), encoding="utf-8"))
    except Exception:
        return None
    for s in cfg.get("stages") or []:
        if not isinstance(s, dict):
            continue
        gate = s.get("gate") or {}
        if s.get("state") == "tests" or gate.get("command"):
            return (str(s.get("id")), gate.get("command"))
    return None


def ledger_test_stage():
    """Failing a declaration, the stage the ledger itself calls the tests one."""
    for l in stage_lines:
        m = re.match(r"stage:\s*(\S+)\s+([^—]*)", l)
        if m and re.search(r"test", m.group(2), re.I):
            return (m.group(1), None)
    return None


found = declared_test_stage() or ledger_test_stage()
if not found:
    # A run is in flight and NOTHING in it reports a suite passing. Blocking is
    # right — the alternative reads as "we could not tell, so we let it go", which
    # is what a release gate exists to refuse. The reason says how to be readable.
    print("block\t%s\tno stage in this run reports the suite passing; declare "
          "the tests stage as `\"state\": \"tests\"` in pipeline.json, or record "
          "it in the ledger with `test` in its name" % act)
    raise SystemExit(0)

stage_id, command = found

claimed_at = None
for i, l in enumerate(stage_lines):
    if re.match(r"stage:\s*%s\b" % re.escape(stage_id), l) and re.search(r"verdict\s+pass", l):
        claimed_at = i
        break

if claimed_at is None:
    print("block\t%s\tno `stage: %s … verdict pass` line in the ledger" % (act, stage_id))
    raise SystemExit(0)

# The claim is the agent's. Where the project declared the command, an observation
# by a hook must agree with it — otherwise the gate corroborates an assertion with
# the same assertion.
if command:
    observed = [l.strip() for l in text.splitlines()
                if re.match(r"gate:\s*%s\b" % re.escape(stage_id), l.strip())]
    if not observed:
        print("block\t%s\tthe ledger claims stage %s passed, and no hook observed "
              "`%s` running — the claim is the agent's own" % (act, stage_id, command))
        raise SystemExit(0)
    # THE LAST observation, not any of them. "Some run of the suite was green" is
    # true of almost every repository that has ever been red, and a gate satisfied
    # by history rather than by the current state is satisfied permanently. Found
    # by running the observer against this pipeline's own ledger, where an earlier
    # green sat above a later red and the gate waved it through.
    if not re.search(r"—\s*exit\s+0\b", observed[-1]):
        print("block\t%s\tthe most recent observed run of `%s` did not exit 0"
              % (act, command))
        raise SystemExit(0)

print("ok\t%s" % act)
PY
}

verdict=$(decide 2>/dev/null)
status=$?

# A gate that cannot reach its own decision must not wave the release through.
if [ $status -ne 0 ] || [ -z "$verdict" ]; then
  [ -f "$ledger" ] || exit 0
  echo "task-pipeline: the stage-7 gate could not run (python3 missing or failed), and this project has a run in flight ($ledger). Refusing an outward act rather than failing open." >&2
  exit 2
fi

state=$(printf '%s' "$verdict" | cut -f1)
act=$(printf '%s' "$verdict" | cut -f2)
why=$(printf '%s' "$verdict" | cut -f3)

case "$state" in
  skip|ok) exit 0 ;;
  block)
    cat >&2 <<EOF
task-pipeline: \`$act\` is an outward, irreversible act and the tests gate has not
passed in this run — $why.

The tag is public the moment it lands; reading the verdict afterwards is not a
gate. Run the full suite, record the tests stage in $ledger, then release.

To release deliberately without the pipeline, remove the ledger or say
«без пайплайна» and take the route by hand.
EOF
    exit 2 ;;
  *) exit 0 ;;
esac
