#!/usr/bin/env bash
# PreToolUse — the stage-7 gate, made mechanical.
#
# `stages.md` already says a release does not leave stage 7 until the full suite
# is green at stage 6. Until now that was a sentence an agent reads and a person
# hopes was obeyed; the tag is public before anybody can check. This refuses the
# irreversible act while the run's own ledger records no passing stage 6.
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
#   3. Only what the ledger SAYS. Nothing here reruns a suite or believes a
#      claim; `progress.md` makes the ledger append-only, and this reads it.
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
  HOOK_INPUT="$input" python3 - "$ledger" <<'PY'
import json, shlex, sys, os, re

ledger = sys.argv[1]
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
                    # A bare `git tag` lists; a tag with a name creates one.
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

passed = False
for line in text.splitlines():
    line = line.strip()
    if not line.startswith("stage:"):
        continue
    m = re.match(r"stage:\s*6\b", line)
    if m and re.search(r"verdict\s+pass", line):
        passed = True
        break

print("ok\t%s" % act if passed else "block\t%s\tno `stage: 6 … verdict pass` line in the ledger" % act)
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
task-pipeline: \`$act\` is an outward, irreversible act and stage 6 has not passed
in this run — $why.

The tag is public the moment it lands; reading the verdict afterwards is not a
gate. Run the full suite, record stage 6 in $ledger, then release.

To release deliberately without the pipeline, remove the ledger or say
«без пайплайна» and take the route by hand.
EOF
    exit 2 ;;
  *) exit 0 ;;
esac
