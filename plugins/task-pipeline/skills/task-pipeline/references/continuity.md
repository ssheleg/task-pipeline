# Continuity — how a run keeps going

Two rules about pacing, in one file because they are two halves of one mechanism.
The loop is what lets a run walk a task list without asking permission between
items. The context budget is what stops that loop from starting an item it cannot
finish. **Neither is useful without the other**, and a run that has the first
without the second fails in a specific, expensive way: it begins task nine with
almost no window left, loses the middle of it, and re-derives what it already did.

## Contents

- The limit, before the capability
- Part 1 — the loop
- Part 1a — the queue is stage 2's, and the loop arms on it
- Arming it on Claude Code
- Other harnesses, and honest degradation
- What one iteration means
- Parked at a manual gate
- Part 2 — the context budget
- The evidence rule
- What happens at the signal
- The flush is not a new document
- Part 3 — workflow memory at the stage boundary
- Rationalizations

## The limit, before the capability

**The loop mode collapses discretionary check-ins. It collapses nothing else.**

- A `manual` gate requires the operator's explicit go. A specific standing authorization
  naming that gate's act is such a go; cite its source and scope in the gate record.
  Without it, the gate waits. A generic instruction to continue is not authorization.
- An outward or irreversible act — deploy, publish, a tag or a release, sending to a
  person, spending money, creating or editing a shared design file — still needs its own
  **specific** authorization. A recorded loop mode is a **generic** flag, and a generic
  flag is not a specific authorization; that floor is set in [`grill.md`](grill.md) and
  this file does not lower it.
- **Pushing this repository's work and opening its pull request** is armed by a specific
  standing authorization that names it — a recorded instruction to push the requested work
  to the repository's own remote ([`build.md`](build.md) → *6. Integrate, then finish*).
  Without one it waits for the go like the acts above. Another repository's PR is outward
  every time ([`conventions.md`](conventions.md)).

**What arms the loop — exactly three sources, and the ledger says which.**
1. `run.loop` in `pipeline.json` (Part 1);
2. the operator's answer at preflight;
3. **a standing instruction the host already carries** — an organisation's principle that
   a free agent takes the next task, a global instruction file, a recorded decision.

The run cites its source once, in the ledger: `loop: armed by <source:line>`.
**Silence still arms nothing**: absent all three, the mode is off, exactly as silence authorizes no
deploy. A project with no such instruction behaves as it always did.

**What a watcher may do unasked.** A wait is not a stop: while a review, CI, a peer's
answer or a release run is pending, the run starts a watcher and takes the next independent
item (*Waits outlive turns*, below). When the wait clears, the watcher may take — **only
where a standing instruction names that class of act** — these steps: merge under the
repository's own integration policy, release a lease, rebase a stacked branch onto what
landed, notify. Deploy, publish, tag and sending to people stay gated unless a *specific*
standing authorization names them. A recorded "releases are the agent's" decision is one:
it names the act class — the tag, and the publish its release run performs — and, when it
names no repositories, it covers every repository its owner governs. It does not stretch to
a deploy or a message it does not name.

**Work that depends on a pending change is not blocked by it**: start it on a branch
stacked on the pending one, open its PR against that branch, and rebase or merge when the
pending change lands. **A watcher polls at the pace its wait changes** — a PR or a peer's
answer every one to two minutes, a release run while it runs, a scheduled time at that time
— and that pace is separate from the loop's `/loop` interval below, which paces items, not
waits.

The mode's whole content is the removal of *"should I continue?"* between items
the operator already asked for. Anything beyond that is a different decision,
taken separately.

### Waits outlive turns

A watcher started inside a session — a background loop, a monitor, a session cron —
dies with the session. **A wait that can outlive the session goes on a durable trigger**: a
launchd or systemd job, an `at` one-shot, a CI schedule, or a board row with a due time that
a session-start hook surfaces, where the host has one. Its one line — what it waits on and which trigger acts on it —
goes into the handoff or the board ([`backlog.md`](backlog.md)), not only into the chat,
because the chat is the one place the next session will not read. On Claude Code the
session-bound primitives are a `run_in_background` loop, a Monitor and `/loop`; on other
harnesses, a background process or the host's own scheduler.

## Part 1 — the loop

**On, the run advances one item per iteration and does not ask between items.**
This spans the whole run, not one stage:

- the plan's tasks at stage 5;
- the boundary between stages whose gate is `auto`;
- the per-module program loop when the brief was a platform, and the waves when
  the request was the whole board ([`waves.md`](waves.md));
- the acceptance → retro tail, which is where runs most often stall one step from
  finished.

It stops for exactly four things: an unmet `manual` gate, a block it cannot resolve, a
genuine ambiguity the brief does not answer, and completion — the iteration's finish line
reached ([`finish-line.md`](finish-line.md)), never a search that ran dry.

**A block or an ambiguity stops its node, not the run.** An ambiguity whose answer is
internal and reversible is not a stop at all: the run takes the recommended answer, records
it as **assumed** on the node, and continues ([`iteration.md`](iteration.md) → *Question
rounds*). Otherwise park the node with its actual reason and owner: only human-owned
questions are marked `needs-operator` and made answerable without context
([`prioritisation.md`](prioritisation.md) → *5. Where the human goes*); external waits
get watchers, and project-owned questions go to the owning Project under
[`iteration.md`](iteration.md)'s board rule. The run continues on every node it does
not block. When the whole frontier is blocked, `graph.py next` says which kind of block it
is. Exit `6` means every remaining dependency leaf is a recorded watched wait: keep those
watchers armed and take independent work ([`work-graph.md`](work-graph.md) → *Watched
external waits*). Exit `4` means a mixed, unclassified, running or parked barrier remains:
classify the recorded reasons, put external waits on watchers and human decisions into the
question batch ([`waves.md`](waves.md)). Neither code proves a human gate or completion. A watcher keeps the recorded
next action alive while no independent node is runnable. **When the board is empty, say so once**, and do not invent work to fill it.

**Stop is not idle.** A finish line reached closes that iteration — stages 9–10, the
hand-back, the retro — and on an armed loop the highest-priority board row starts a new
iteration with its own contract. Re-opening the closed one to polish it is not continuing
([`finish-line.md`](finish-line.md) → *Stop is not idle*).

**This extends [`build.md`](build.md); it does not replace it.** That file's
*Continuous execution* rule governs the inside of a stage-5 execution — do not
check in between the tasks of a plan you were told to execute. It is unconditional
and stays that way. What it cannot do is reach the other nine stages, or survive
the boundary between one agent turn and the next. This file is that reach.

**Where it is recorded:** `pipeline.json` → `run.loop`. A project sets it once and
is never asked again — which is the entire point. A mode that has to be requested
every run is not a mode, it is a habit the operator maintains by hand.

## Part 1a — the queue is stage 2's, and the loop arms on it

**A loop with no queue is a timer.** Until this section existed, `run.loop` said *how
often* to continue and never said *what the next item is*, so the mode could be armed
and still leave the run picking its next move by recollection — which is the failure
[`learned.md`](learned.md) rule 16 is about, running once per fire.

**Where a work graph exists it is the queue** ([`work-graph.md`](work-graph.md)):
`.task-pipeline/graph.json`, walked by `scripts/graph.py next`, which prints the runnable
nodes and nothing else. It is preferred over the two below for one measured reason — a
400-node graph and a 4-node graph produce the same 27-byte frontier, so the cost of knowing
what is next does not grow with the programme. `run.loop.queue: work-graph` records it, and
`next`'s exit codes are what the loop branches on: `3` is *every node is terminal*
(including deliberately parked nodes), `4` retains another unresolved barrier, and
`6` means recorded watched waits hold every remaining dependency leaf. On 6, keep
the recorded watchers armed and take independent work; it is neither completion
nor a new human gate. `graph.py wait` records the locator and `resume --wait-id`
resolves that exact wait; neither executes a watcher or grants authority. See
[`work-graph.md`](work-graph.md) → *Watched external waits*.

**Otherwise the queue is the module map** ([`decomposition.md`](decomposition.md)) when the brief
was a platform, and the plan's task list otherwise. Both already exist and both are
already ordered; neither was ever named as the thing the loop walks.

**Arming is the execution of a recorded decision, not a fresh request.** Where the mode
is **recorded** and the queue has more than one item, the loop arms **at the close of
stage 2** and the run says so in one line. It is not asked for at that point, for the
same reason the mode is recorded rather than requested: re-asking would rebuild the habit
the config exists to retire.

**A standing instruction the host carries counts as recorded** (*The limit, before the
capability*, source 3): it arms at the close of stage 2 like `run.loop`, unless the
instruction itself says otherwise, and the ledger cites it.

**Where nothing is recorded, nothing arms.** Silence arms nothing here too — this section
moves *where* a recorded mode is armed, from preflight to the close of stage 2. It does
not make arming unconditional, and a reader who takes it that way would arm a loop in a
project with no `pipeline.json` at all. That reading was in this section's first draft;
an independent reader found it before it shipped.

**What arming does NOT change, and this is load-bearing:** the four stops are the four
stops. A `manual` gate waits unless a specific standing authorization already names
its act, cited with its source and scope. An outward or irreversible act still needs its own
specific authorization — *a generic flag is not a specific authorization*, and arming a
queue is the most generic flag there is. Arming decides only that the run does not stop
to ask *"shall I take the next one?"*.

**`mode: dynamic` — when the harness paces itself.** `interval` was the only mode while
the only primitive was a fixed tick. A harness that can schedule its own next turn
should: the run picks the delay from what it is waiting for, and a wait on nothing is a
wait of minutes rather than a fixed tick nobody chose. On a harness with neither
primitive the mode degrades to prose discipline plus the build ledger, and **the run
says which one it is running** — the rule below about claiming a capability you do not
have is unchanged and applies to `dynamic` first.

### The goal is re-read between items, not only the board

Each iteration already re-measures the work-list. That answers *what is open*. It does
not answer *whether the open thing still serves what this run was for* — and a queue
built at stage 2 outlives the reason it was built, because the operator learns things
between items and says so.

So at the bottom of an iteration, beside the re-derived `prio`:

1. re-read the brief's goal — one line, quoted, not recalled;
2. state whether the next item still serves it;
3. if it does not, **re-order or re-scope the queue and say what moved and why.** A row
   that stops serving the goal leaves for the board with its reason
   ([`backlog.md`](backlog.md)), it does not get worked because it was next. On a work
   graph the move is a committed `revisions` entry — `park`, `add`, or `wave` between
   waves — never an untracked edit.

A queue re-derived only by `age` and `sev` is a queue that is honest about priority and
silent about purpose. Both numbers can be right while the run is finishing something the
operator stopped wanting two items ago.

## Arming it on Claude Code

```
/loop <interval> <the invocation that continues the run>
```

The interval **must divide its unit cleanly** — `5m`, `10m`, `2h` are fine; `7m`
gives uneven gaps and `90m` cannot be expressed at all. A value that does not
divide cleanly is rounded to the nearest one that does, **and the rounding is said
out loud** before it is used.

Pick **the shortest interval that is longer than a typical item.** Shorter buys
nothing: the scheduler cannot deliver faster than the item finishes.

Two properties of the armed job must be stated when arming it, because both are
silent failures otherwise:

- **The job is session-only.** It is not written to disk and it dies with the
  session.
- **It auto-expires after seven days**, firing one last time. A loop that quietly
  stops on day eight is worse than one that was never armed, because the operator
  believes work is still moving.

**Where it arms is `run.loop.arm`,** and there are two points because there are two
kinds of run:

- `preflight` — the top of the run. Right when the loop walks stage boundaries rather
  than a list, and the only option before Part 1a existed.
- `after-decomposition` — the close of stage 2, once the queue exists and holds more
  than one item. Arming earlier would arm a loop with nothing to walk.

Either way the run **prints the job id and the cancel command**, and arming is not a new
decision at that point — the config is the recorded authorization, and re-asking would
rebuild the habit the config exists to retire.

Under `mode: dynamic` there is no job id: the run schedules its own next turn each time
and prints **the delay it chose and why**, which is the same disclosure in the form that
mode has. A dynamic run that says nothing about its pacing is indistinguishable from a
run that quietly stopped.

## Other harnesses, and honest degradation

`/loop` is **Claude Code only**, in the same way the `PreToolUse` contract in
[`hooks.md`](hooks.md) is. This file names the limit rather than pretending the
mechanism is universal.

On a harness with no loop primitive, the mode degrades to what prose can do: the
discipline in [`build.md`](build.md) plus the build ledger, which is genuinely
useful and genuinely weaker. **Say which one you are running.** A run that reports
itself as looping while nothing is scheduled is claiming a capability it does not
have, and the operator finds out by discovering that nothing happened.

## What one iteration means

One item, taken to its gate.

**A fixed interval cannot interrupt an unfinished item.** The scheduler enqueues
only while the harness is idle — never mid-query. This is the reason the interval
form is safe, and it is worth stating precisely, because the plausible-sounding
alternative explanation is wrong.

**The build ledger is the second line, not the first.** It covers a different
case: a fire that lands after a context loss, where the controller no longer
remembers what it finished. There, `Task <N>: complete` in
`.task-pipeline/build/<plan>/progress.md` is the only DONE marker that counts, and
a task carrying one is never re-dispatched ([`build.md`](build.md)).

Do not write, and do not believe, that the ledger is what makes the interval safe.
Someone will eventually remove the ledger on the strength of that sentence, and
the protection they think they are keeping is in the scheduler.

**Each iteration re-measures the work-list.** The harvest's *documents* may be
carried across iterations — an ADR did not change while you worked. The line that
says **what is still open** may not: the previous iteration is precisely what
invalidated it, and a loop that picks its next item from the list it started with
works a stale board for as long as the loop runs. One command, at the top of the
iteration, recorded ([`knowledge-sources.md`](knowledge-sources.md) → *Carried-in
claims*; [`learned.md`](learned.md) rule 16).

**The work-list is `<artifacts>/backlog.md`** ([`backlog.md`](backlog.md)), and the
other half of the same measurement is the exposure line ([`exposure.md`](exposure.md)).
Counted at the top of the iteration, re-derived at the bottom — `age` moves on its own,
so the re-derivation is the only moment the board stops being stale.

This is also where a loop's report goes wrong most quietly. *"Next up is X"* at the
end of an iteration is a claim about the board, and it is the one sentence in the
whole cycle that no gate reads. It cites the measurement or it is not written — **a
`B-NNN`, not a description**: *"next up: B-014"* can be checked against the file,
*"next up: the export fix"* cannot.

**And it is printed, in one fixed shape** ([`progress.md`](progress.md)):

```
▶ <topic> · <module> (N/M) · <id> <stage> <gate> · iter <N> · gates <N/M> · next B-NNN
```

The iteration number is a count of `iter:` lines in `.task-pipeline/run.md`, not a
number the agent is carrying. After a compaction the agent's count is gone and the
file's is not — which is the argument the build ledger already won one stage down.

## Parked at a manual gate

A fixed interval firing into a `manual` gate is a nag. Five minutes later it fires
again, and again, and the operator — who is reading the thing the gate asked them
to read — learns to ignore the loop. That is the same failure as a rule nobody
reads to the end: everyone believes it is covered.

**So the run cancels its own loop job when it parks**, and prints the re-arm
command beside the gate. The go and the re-arm are then one act. This is also the
honest accounting: while the run waits for a person, nothing is looping, and the
job list should agree with that.

**Verify the cancel by listing the jobs, never by the cancel's own reply.** A
teardown call will happily accept an id that was never scheduled and report
success, which leaves the real job running while the transcript says it stopped.
List afterwards and read the list. This is one instance of a named class —
[`gates.md`](gates.md) → *False success*, rule 1 — and a loop is
exactly where breaking it goes unnoticed, because the symptom is a message
arriving on time.

## Part 2 — the context budget

Near the end of the context window, the run does **not** stop and it does not
start anything new:

1. **Finish the item in flight.** A half-finished item is the expensive state.
2. **Start no new item.** An item begun in this window loses its own middle.
3. **Make the ledgers true** (below).
4. **Continue.** Compaction is a normal event, not the end of the run.

The failure this prevents is not running out of room — that is survivable. It is
crossing the boundary *in the middle of something*, so the work either vanishes or
gets done twice.

## The evidence rule

**The rule fires only on evidence**, and there are exactly two admissible kinds:

- **A signal from the harness** — a warning that compaction is near, a `PreCompact`
  hook firing, an explicit low-context notice.
- **The operator saying so.**

Absent both, the threshold has not been observed, and you **never announce that
the context is nearly spent without one of those signals**. No tool returns the
remaining percentage. An estimate from transcript length or how much has been read
is a guess, and presenting a guess as a measurement is precisely the failure
[`learned.md`](learned.md) names — compute, never restate.

This cuts both ways, and the second direction is the one that actually goes wrong:
a run that keeps volunteering *"context is nearly exhausted, start a new session"*
against a mostly-empty window trains the operator to disregard the one time it is
true.

## What happens at the signal

The four acts above, in order, and one prohibition: **no new item starts.** This is the one
carve-out from "take the next task in the same turn": **at the compaction signal, finish the
current unit and write the next task into the handoff** — the ledger's next line, the board
row — **instead of starting it.** Until compaction, the only writes are to what already
exists: the ledger, the plan, the decisions already settled, the REQ statuses. The next
turn, after compaction, takes the written task from there.

If the project has recorded that it must not cross a compaction mid-stage, stop at
the stage boundary instead and hand off. That is a project answer, not a default:
the default is to continue.

## The flush is not a new document

Flushing means **making the artifacts that already exist true**:

- the build ledger — every completed task carrying its `complete` line;
- the carry-over ledger — everything deferred, dropped or half-done;
- the brief's REQ statuses;
- the task list.

It does **not** mean writing a summary for the compactor. A summary is a fourth
copy of the truth, it is written once, nobody updates it, and the next run reads
it as current. The artifacts above are read by later stages anyway; making them
right costs nothing extra and pays twice.

## Part 3 — workflow memory at the stage boundary

Project Observatory is a separately installed, public engine:
[passioncode-ai/project-observatory-dashboard](https://github.com/passioncode-ai/project-observatory-dashboard)
— its README's *Install* and *MCP* sections say how to run it and connect it. Without it,
everything below degrades to one ledger line and the run continues.

Which of the five handoff mechanisms carries what — the Git record, Observatory's lease
and checkpoint, a host's launch context, the inbound queue — and the order a successor
reads them in, has one home:
[sshlg-skills `docs/working-rules/handoff-layers.md`](https://github.com/ssheleg/sshlg-skills/blob/main/docs/working-rules/handoff-layers.md).
This part is the checkpoint and lease half of it.

The ledger survives a compaction. It does not survive a quota that ran out on another
account, or a run picked up by a different agent on another machine. When the host has
Project Observatory's memory tools, **every gate that returns also writes a workflow
checkpoint**, and the next executor continues from the last finished stage.

- **When.** After the `stage:` line is appended, every time a gate returns, whatever the verdict. A failed gate's checkpoint says `blocked` and keeps the stage open. Acceptance closes the workflow.
- **How.** `scripts/stage_checkpoint.py emit` prints the tool's arguments, built from the ledger and selected project profile: the topic, observed verdicts, next declared stage, operator's constraints and key names. Pass them to `observatory_checkpoint_write`, or to `memory.checkpoint.write` under memory/0.1. Then hand the answer to `stage_checkpoint.py record --answer -`.
- **Profile authority.** `pipeline.json` at the project root owns stage order; only genuinely absent config selects the bundled default. Unreadable/malformed config, ambiguous numeric ledger ids, unsupported mandatory capabilities or a ledger stage outside the selected profile refuse before producing tool arguments. Optional ids use array ordinals, optional names use stable state labels; explicit ids retain declared array order. This reader does not execute gates or replace full preflight/schema validation. A final skipped stage stays open for confirmation, never inventing a successor or closing by inference.
- **Root and recovery.** The usual ledger stays `.task-pipeline/run.md`; `paths.artifacts` relocates project documents, not this run state. For a relocated ledger use `emit --ledger <path> --project-root <project>` (an enclosing Git root can also establish the project). The first emit saves the selected profile's source/digest and run identity beside the ledger; record retains them. Same-run profile changes, a missing formerly selected config, or a different run reusing that state refuse. Restore the selected source and retry, or reconcile the old workflow and start a distinct ledger/state for the new run; never delete a lease to make the check green. A pre-existing custom workflow with no profile binding also needs reconciliation. Ledger file symlinks and state-file links refuse without migration or overwrite; accepted directory aliases resolve consistently for emit, record, state and handoff. Profile, ledger and existing state inputs must be regular files, so a FIFO is refused before reading. No live checkpoint or read-attestation is proved by a locally emitted payload.
- **The constraints.** Give the brief's restrictive rules once, as `--constraint`. They are carried to every later boundary, and a successor reads them first.
- **Keys.** Pass keys by name, as `--credential PROJECT/ENV/NAME`, never as a value.
- **Without the tools.** `stage_checkpoint.py record --unavailable "<why>"` appends one `event: memory — unavailable` line, and the run continues exactly as before. Missing memory is a state the ledger names, not a failure. When the tools are absent for the whole run — no Observatory on this machine — say it **once**: `record --unavailable "<why>" --for-run` appends one `unavailable for this run` line and leaves a marker in `.task-pipeline/memory.json`; no later gate is nudged or needs a line. Any later `record --answer` (the tools came back) clears the marker.
- **A planned change of executor** — a quota running out, a route moving the work to another model or account. `stage_checkpoint.py handoff --to-provider <p> [--to-model <m>] --reason limit|plan_route|operator` prints `observatory_handoff_create`'s arguments; `record --answer -` keeps the offer as one ledger line, and the lease stays with this run until the successor accepts. The successor runs `stage_checkpoint.py accept --handoff-id <id>` → `observatory_handoff_accept` → `record --answer -` **before its first write**, and obeys the constraints the answer carries first. `LeaseLost` is then left for the race nobody planned. A retried offer keeps its idempotency key until a memory event (a checkpoint, a refusal, a recorded offer — never `unavailable`) is appended, so a `gate:` or `stage:` line between retries does not turn it into a new offer that replaces the unaccepted one.
- **The reminder.** `hooks/memory-nudge.sh` (PostToolUse) reads the ledger after each tool call and, once per `stage:` line with no `event: memory` line after it, puts one sentence in front of the model naming the two commands above — unless the run-level marker says memory is unavailable for this run, in which case it stays silent. The first reminder of a run also says where Observatory comes from, once. It decides nothing and blocks nothing; adoption measured before it was one write in 293 sessions.
- **A refusal.** `LeaseLost` means another executor holds the workflow now. The script drops the token. Read the workflow (`observatory_checkpoint_latest` with `stage_checkpoint.py state`'s id) before doing anything else. A stale writer stops after one refusal.
- **The lease token.** It lives in `.task-pipeline/memory.json` (mode 0600, git-ignored) and never in the ledger, a reply or a commit.
- **What this is not.** Not a second ledger and not the narrative. The checkpoint is the work's state for the next executor. The wiki and the ledger keep everything else.

## Rationalizations

| Excuse | Reality |
|---|---|
| "The operator obviously wants it to keep going, I'll just loop" | Default off. Silence arms nothing — the same floor deploy authorization uses. Arm from `run.loop`, the preflight answer, or a standing instruction the host carries, and cite which in the ledger. |
| "The watcher can push the release through when CI goes green" | A watcher takes only the act classes a standing instruction names — merge, release a lease, rebase, notify. A tag or a deploy needs its own specific authorization. |
| "My background loop will catch it tomorrow" | It dies with the session. A wait that can outlive it goes on a durable trigger, and its line goes into the handoff. |
| "The mode is on, so I can push the deploy through" | The mode collapses check-ins, never gates or outward acts. A generic flag is not a specific authorization. |
| "I'll tell it to keep going and it will" | On Claude Code, prose does not survive the turn boundary. Either a job is scheduled or the run stops; say which. |
| "A one-minute interval is closest to no pause" | The interval must be longer than a typical item, or every fire lands on work already in progress and buys nothing. |
| "The ledger protects me from mid-task fires" | The scheduler not firing mid-query protects you. The ledger covers context loss. Confusing them is how the real protection gets deleted. |
| "It's still looping while we wait for approval" | A loop firing into a manual gate is a nag, and a nagged operator stops reading. Cancel on parking, re-arm with the go. |
| "Context feels tight, I should warn them" | Feels is not evidence. Without a harness signal or the operator's word, the warning is a guess wearing the clothes of a measurement. |
| "I'll write a handoff summary before compaction" | Update the ledgers instead. A summary is a copy of the truth that nobody maintains. |
| "One more task will fit" | If it does not fit, its middle is what you lose — and half a task is the most expensive state there is. |
