# Hooks — agent-time enforcement, and the limit first

**One job: stop a bad edit before it lands, and never claim protection you do not
have.** A hook is rung 5 of [`gates.md`](gates.md)'s ladder — the only mechanism
that acts *while the agent is working* rather than after the commit.

## Contents

- The limit, before the capability
- The events
- The `PreToolUse` contract
- What the hook receives
- Where it lives
- Matchers
- Performance
- What belongs in a hook, and what does not
- A worked example
- Debugging
- Removing them
- The one this skill ships
- Leases are not reimplemented here
- Rationalizations

## The limit, before the capability

**Hooks exist only in Claude Code.** On Cursor, Codex and the other agents a skill
can be installed and read, but there is no `PreToolUse`, so nothing blocks anything.
On those agents the same rules run as a self-check written into the skill body, and
the run is recorded **`ungated`**.

**Never describe a project as protected when its agents run outside Claude Code.**
The gap between "the rule exists" and "the rule is enforced" is invisible from
inside a transcript, and a false guarantee is worse than a stated absence: everyone
downstream stops checking.

> **Provenance.** Every contract below is quoted from the Claude Code hooks
> reference (`code.claude.com/docs/en/hooks`), fetched **2026-08-03**. Re-fetch
> before relying on it: this is an external API, and stage 1 of this very pipeline
> exists because a contract recalled from memory is a contract that has already
> moved. Where the reference and this file disagree, the reference wins and this
> file is the bug.

## The events

There are **35** hook events. These are the ones this pipeline reaches for; the
reference has the rest, grouped as session lifecycle, per-turn, tool execution,
subagents and tasks, file and config changes, compaction, worktrees, display, and
MCP elicitation.

| Event | Fires | Used for |
|---|---|---|
| `SessionStart` | session opens (matcher `startup\|resume`) | register the run, print the board, name the one next action |
| `PreToolUse` | before a tool call | **block** — the event that can refuse |
| `PostToolUse` | after a tool call | bookkeeping: renew a lease, stamp a marker |
| `Stop` | the turn ends | a last-word check — the run's own gate, not the repo's |
| `SubagentStart` · `SubagentStop` | a subagent starts or finishes | stage 5 runs implementers as subagents; this is where a per-agent identity or ledger line belongs |
| `WorktreeCreate` · `WorktreeRemove` | a worktree appears or goes | stage 5 isolates in worktrees; a guard that must not fire inside one can key off these |
| `PreCompact` · `PostCompact` | context is compacted | flush anything that only lives in context — the ledger exists because this happens |
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

`permissionDecision` takes **four** values, not one: `allow` (permit it), `deny`
(block it), `ask` (escalate to the user), `defer` (fall through to the normal
permission flow). Exit 0 with empty stdout means `defer` by omission. A hook may
also rewrite the call instead of judging it, by returning `updatedInput` in the
same block — which is a different power from blocking and worth knowing before you
reach for it.

**Any other exit code is a non-blocking error**: execution continues and stderr is
shown in the transcript. The reference is explicit that **exit 1 is treated as
non-blocking, "even though 1 is the conventional Unix failure code"** — so the
single most likely way to write a guard, `command || exit 1`, is the one that does
not guard. And on exit 2 Claude Code **ignores stdout and any JSON in it**; only
stderr is read back.

So **a crashing guard fails open** — it stops guarding and nothing announces that
it has. Write the guard to `exit 2` on its own internal errors, or accept that a
typo in it silently removes the protection everyone believes is there.

That asymmetry is the whole reason this file leads with the limit: a hook is the
strongest rung and the one whose failure is quietest.

## What the hook receives

JSON on stdin. Common to every event: `session_id`, `transcript_path`, `cwd`,
`permission_mode` (`default` · `plan` · `acceptEdits` · `auto` · `dontAsk` ·
`bypassPermissions`), `effort` (an object with `level`), `hook_event_name`, and —
inside a subagent — `agent_id` and `agent_type`. `prompt_id` is present from a
recent version onward, so treat it as optional unless you pin one.

Tool events add `tool_name`, `tool_input` and `tool_use_id`. **`tool_input` is
where the target lives** — `file_path` for an edit, `command` for a Bash call.
Parse it; do not infer the target from anything else in the environment
([`learned.md`](learned.md) rule 15: a heuristic over strings the environment also
produces matched the throwaway shell of every tool call).

`agent_id` matters more here than it looks: stage 5 runs implementers as subagents
in worktrees, and a guard that must behave differently for the orchestrator and for
an implementer has exactly one honest way to tell them apart.

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

`if` uses **permission-rule syntax** (`Bash(git *)`, `Edit(*.ts)`) and is evaluated
**only on tool events** — `PreToolUse`, `PostToolUse`, `PostToolUseFailure`,
`PermissionRequest`, `PermissionDenied`. Anywhere else it is inert, which is a
silent way to write a guard that never fires.

**For Bash the match is best-effort — the reference's own word.** It inspects
subcommands, `$()` expansions and backticks, and strips leading `FOO=bar`
assignments before matching. So `if` is a good **filter** and a bad **boundary**:
narrow with it to keep the hook cheap, then re-check the real target inside the
script before refusing anything.

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

## The one this skill ships

Since v1.50.0 the plugin carries hooks of its own. `hooks/release-gate.sh`
(`PreToolUse` on `Bash`) refuses an **outward, irreversible act** — `git tag`, a
tag push, `gh release create`, `npm publish` — while the run says the suite has not
passed. `hooks/gate-observer.sh` (`PostToolUse` and `PostToolUseFailure`) records
what the declared gate command actually did.

**Two lessons from v1.50.0, both shipped as defects and both fixed in v1.51.0.**

*A gate keyed to a stage NUMBER is the rail's mistake with worse consequences.*
The first version matched `stage: 6` literally. `progress.md` says the rail "is
computed, never eleven" because a host project replaces the flow — and a project
whose flow has six stages, tests green at stage 4, could never tag anything again.
A wrong rail misinforms; a wrong gate stops the work. The stage is resolved from
`pipeline.json` (`state: "tests"`, or a stage declaring `gate.command`), and
failing that from the ledger by name.

*A gate that reads a claim written by the party it constrains confirms an
assertion with itself.* `stage: … verdict pass` is typed by the agent. Where the
stage declares `gate.command`, the observer writes the **observed** exit code as a
`gate:` line and the release gate requires both. Declare no command and it
degrades to the claim alone — which is stated here rather than discovered.

It is the worked example above, made real, and its three narrownesses are the
reusable part:

| Narrowness | Why it is not a smaller feature |
|---|---|
| Only outward acts, never ordinary commits | stage 5 commits per task by design; a gate that fights the build loop is removed within a day |
| Silent where no `.task-pipeline/run.md` exists | enabling the plugin must change nothing in a repository that runs no pipeline |
| Reads the ledger, never reruns a suite | `progress.md` already makes the ledger append-only; a second source of truth about "did stage 6 pass" is the failure this file warns about below |

**Fail-closed, deliberately.** Every non-zero exit code other than `2` is
non-blocking, so an internal failure exits `2` as well. A crashing gate that fails
open is worse than no gate: it reads as one.

**The defect worth remembering** — the first implementation fed its own python
source to `python3 -` through a heredoc *and* read the payload from stdin. The
heredoc **is** stdin, so the payload came back empty, every act classified as "not
a release", and the gate allowed everything while looking installed. Eight fixtures
caught it. A hook that cannot see its own input is indistinguishable, from the
outside, from a hook that approves.

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
