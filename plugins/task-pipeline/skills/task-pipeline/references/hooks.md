# Hooks — agent-time enforcement, and the limit first

**One job: stop a bad edit before it lands, and never claim protection you do not
have.** A hook is rung 5 of [`gates.md`](gates.md)'s ladder — the only mechanism
that acts *while the agent is working* rather than after the commit.

## The limit, before the capability

**Hooks exist only in Claude Code.** On Cursor, Codex and the other agents a skill
can be installed and read, but there is no `PreToolUse`, so nothing blocks anything.
On those agents the same rules run as a self-check written into the skill body, and
the run is recorded **`ungated`**.

**Never describe a project as protected when its agents run outside Claude Code.**
The gap between "the rule exists" and "the rule is enforced" is invisible from
inside a transcript, and a false guarantee is worse than a stated absence: everyone
downstream stops checking.

## The events

| Event | Fires | Used for |
|---|---|---|
| `SessionStart` | session opens (matcher `startup\|resume`) | register the run, print the board, name the one next action |
| `PreToolUse` | before a tool call | **block** — the only event that can refuse |
| `PostToolUse` | after every tool call | bookkeeping: renew a lease, stamp a marker |
| `SessionEnd` | session closes | release leases, flush the journal |

## The `PreToolUse` contract

A hook blocks a call in **either** of two ways:

- **exit 2**, with the reason on **stderr** (stdout is ignored); or
- **exit 0** with this on stdout:

```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse",
 "permissionDecision":"deny",
 "permissionDecisionReason":"docs gate failed: 2 undefined ids in docs/ARCHITECTURE.md"}}
```

**Any other exit code is a non-blocking error**: execution continues and stderr is
shown in the transcript. So **a crashing guard fails open** — it stops guarding and
nothing announces that it has. Write the guard to `exit 2` on its own internal
errors, or accept that a typo in it silently removes the protection everyone
believes is there.

That asymmetry is the whole reason this file leads with the limit: a hook is the
strongest rung and the one whose failure is quietest.

## What the hook receives

JSON on stdin: `session_id`, `prompt_id`, `transcript_path`, `cwd`,
`permission_mode`, `hook_event_name`, `tool_name`, `tool_input`, `tool_use_id`.

`tool_input` is where the target lives — `file_path` for an edit, `command` for a
Bash call. Parse it; do not infer the target from anything else in the environment.

## Where it lives

| Placement | Scope | Use when |
|---|---|---|
| the project's `.claude/settings.json` | this repository | the rule is this project's |
| a plugin's `hooks/hooks.json`, paths via `${CLAUDE_PLUGIN_ROOT}` | every project the plugin is installed in | the rule travels with a tool |

**A globally installed plugin must exit 0 immediately when the project has no
config for it.** Otherwise installing it once changes every other repository on the
machine, and the first surprising denial is debugged in the wrong project.

## Matchers

```json
{ "matcher": "Edit|Write|MultiEdit|NotebookEdit",
  "hooks": [{ "type": "command", "command": "…/guard.sh", "timeout": 20 }] }
```

- a tool-name pattern (`Edit|Write|…`), or `"*"` for every call;
- for a specific shell command, add `"if": "Bash(git commit *)"` beside
  `"matcher": "Bash"`.

Match as **narrowly** as the rule allows. A `"*"` matcher on a blocking event puts
your script in the path of every tool call the agent makes.

## Performance

A `PostToolUse` hook on `"*"` runs after **every** call, so it must be a no-op in
the common case: read one timestamp file, return. Touch the network at most once
per throttle interval. If it becomes slower than that, the throttle is broken —
**fix the throttle, never remove the hook**, because a hook removed for latency is
a protection removed permanently for a reason that had a fix.

## What belongs in a hook, and what does not

**Belongs:** cheap, deterministic, and about an edit happening *right now* — a
guarded path, a staged file, a lease that is not held, a command with a shape the
project forbids.

**Does not belong:** the full test suite; anything needing the network on every
call; anything whose answer requires a human. Those are rungs 3 and 4
([`gates.md`](gates.md)) — CI is late, and late is the correct trade for slow.

The test is one question: *if this fires, can the agent fix it in the next ten
seconds without asking anybody?* If not, blocking here only converts a review
comment into a dead end.

## A worked example

The one hook this skill ships — run the documentation gate before a commit, and
refuse the commit if it fails. It is
[`../templates/hooks.example.json`](../templates/hooks.example.json); copy it into
the project's `.claude/settings.json`.

```json
{ "hooks": { "PreToolUse": [
  { "matcher": "Bash", "if": "Bash(git commit *)",
    "hooks": [{ "type": "command", "shell": "bash", "timeout": 60,
      "command": "bash scripts/check-docs.sh >&2 || exit 2" }] } ] } }
```

`|| exit 2` is the contract, not a flourish: without it the gate's own `exit 1`
lands in the "non-blocking error" branch and the commit proceeds.

## Debugging

| Symptom | Cause |
|---|---|
| Guarded edits go through | the guard crashed — any exit code other than 2 is non-blocking. Run it by hand |
| Everything is denied | no config, or no lease. The tool's `status` says which |
| Session start is slow | the backend is unreachable; it must time out and degrade, never hang |
| The renew hook floods the log | the throttle file is not being written — check the path is writable |

Run the guard directly and see what it decides:

```bash
echo '{"tool_name":"Edit","tool_input":{"file_path":"docs/DECISIONS.md"},"cwd":"'"$PWD"'"}' \
  | bash .claude/hooks/guard.sh; echo "exit=$?"
```

## Removing them

Delete the `hooks` block from the project's `.claude/settings.json`. Everything the
hooks enforced is still available as a command and still stated in the doctrine —
and the run is **`ungated`** from then on, which is a thing to say out loud rather
than a detail to omit.

## Leases are not reimplemented here

Guarded registers and lease arbitration belong to a coordination tool
([`companion-skills.md`](companion-skills.md) names the optional one). This skill
ships the **doctrine** and the one example above.

Two implementations of one lease will disagree, and the disagreement is invisible:
each believes it holds the lock, both write, and the register ends up with two
entries carrying one id — which is the exact failure the lease existed to prevent.

## Rationalizations

| Excuse | Reality |
|---|---|
| "The hook is installed, so the repo is protected" | Only in Claude Code, and only while the guard exits 2. Any other exit code fails open silently. |
| "It's fine, the guard can't crash" | Then it costs one line to make crashing block instead of pass. Write the line. |
| "I'll match `*` and filter inside the script" | Now every tool call pays your script's startup. Match narrowly; the matcher is free and the script is not. |
| "The hook is slow, I'll disable it for now" | "For now" survives the session and the memory of why. Fix the throttle. |
| "I'll put the test suite in the hook, it's the strongest gate" | It is the strongest and the most expensive. A rule that takes two minutes to answer belongs in CI. |
| "Other agents will follow the doctrine anyway" | They might. What they will not do is *block*, and the run must say `ungated` so nobody mistakes intention for enforcement. |
