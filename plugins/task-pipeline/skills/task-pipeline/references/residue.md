# Residue — what a run leaves running, and what it leaves behind

A run does not only produce a diff. It starts background processes, arms
monitors, schedules wake-ups, takes leases, creates worktrees, brings up
containers and writes scratch files. Every one of those outlives the stage that
created it unless something ends it.

**Two shapes, one class.** *Residue in flight* is what is still running while the
run continues — it corrupts the work, because a stale monitor fires into a run
that has moved on and a lease held by a finished stage blocks the next one.
*Residue at rest* is what is still there when the run ends — it corrupts the next
run, which inherits a dirty environment it did not create and cannot explain.

Both are checked the same way and this file covers both.

## Contents

- The measured reason this file exists
- The inventory — eight classes
- Where the check fires: every gate
- The teardown, at the end of the run
- What must **not** be torn down
- Three owners, not two — and the third is where cleanup actually happens
- Rationalizations

---

## The measured reason this file exists

On 2026-08-11, mid-run, a monitor was armed to watch CI. One minute later the
harness task inventory was queried:

```
TaskList              →  "No tasks found"
ps -eo pid,etime,cmd  →  52693  03:12  /bin/zsh -c … gh pr checks …
```

The monitor was **alive and polling**, and the inventory tool reported nothing.

This is the class this whole doctrine exists to catch: **a check answered by
something that is not its subject.** An inventory that does not enumerate the
thing that leaks is not an inventory — it is a green light with no lamp behind
it. A residue check that calls one tool and trusts its silence will report clean
over a process that is still making network calls.

**So: enumerate by class, never by tool.** Each class below names its own
enumeration. Silence from one tool is evidence about that tool, not about the
environment.

---

## The inventory — eight classes

Run the enumeration for every class that the run could have created. A class the
run provably never touched is skipped **by name**, not by omission.

| Class | What leaks | How to enumerate |
|---|---|---|
| **Background shells** | a task started detached and never exited | the harness's background-task list **and** `ps -eo pid,ppid,etime,command` filtered to this session's shell |
| **Monitors / watchers** | a poll loop still hitting a remote API | `ps` for the poll command; the harness list may not contain it — see above |
| **Scheduled wake-ups / loops** | a loop that fires into a finished run | the harness's schedule list; a dynamic loop ends by an explicit stop, never by falling silent |
| **Coordination leases** | a lease held on a shared register blocks every other agent | `agent-sync status` where `.claude/agent-sync.json` exists |
| **Worktrees / branches** | an isolated build workspace, and the branch under it | `git worktree list`, `git branch --merged` |
| **Containers / services** | a database or app brought up for a test | `docker ps`, `docker compose ls`, plus whatever the project's own runbook started |
| **Scratch files** | temp output, planted-defect copies, generated fixtures | `git status --porcelain` for the tree; the scratch directory for the rest |
| **Remote state** | a draft PR, a test tag, an uploaded artifact, a feature flag flipped for a check | the tracker and forge; the deploy target's own listing |

Two of these bite hardest and are worth naming separately.

**A lease is the one that blocks someone else.** Every other class costs this run
or the next one. A held lease costs a *different agent*, right now, and it looks
to them like the register is permanently unavailable rather than briefly held.
Release it at the stage that took it — not at the end.

**A container is the one that is invisible and expensive.** Nothing in the diff
mentions it, no test fails because of it, and it will still be running tomorrow.

---

## Where the check fires: every gate

**The residue check is a criterion of every gate, not a stage of its own.** A
cleanup stage at the end is the design that fails, because the damage from
residue in flight has already happened by the time the end arrives.

Every gate verdict carries the count, in the same line as the rest:

```
GATE 5 build: PASS — reviews 3 · findings 0 open · holds: 2 (worktree, container)
  abstained: 0 · unlooked: 0
GATE 6 tests: PASS — suite green · holds: 1 (container: pg-test, this run)
  abstained: 0 · unlooked: 0
```

Read the line the way the other disclosures on it are read:

- **`holds: 0`** — every class enumerated, nothing found.
- **`holds: N (…)`** — N things are live, each named. This is a **disclosure,
  not a failure**. A build stage that legitimately holds a worktree and a database
  reports `holds: 2` and passes; the count exists so nobody has to remember.
- **`holds: unlooked (…)`** — a class could not be enumerated, named. A run
  without container tooling says so rather than printing `0`.

**Why the field is `holds:` and not `residue:`.** `gates.md` already prints `unmarked residue: 0` for a different thing — documentation items left unmarked — and `residue: 0` is a substring of it. A check written for this field would have been answered by that line. The word stays in the prose because it is the right word; the **field** is `holds:`, which is free and joins `stage:`, `iter:`, `hand:` and `touch:` in the run ledger.

**Its sibling, one file over.** `tdd.md`'s *The green from residue* is the same class on the test axis — state left over from an earlier run making a case pass that would fail fresh. That rule is about residue **faking a result**; this one is about residue **outliving the run**. Neither overrides the other.

**`holds: 0` is never a target.** A run that tears down its database to make a
number look tidy, and then brings it back up next stage, has spent time to make a
measurement lie. The number describes; it does not instruct.

**Only stage 10 requires the count to reach zero** — or every remaining item to
carry a named owner and a reason, in writing.

---

## The teardown, at the end of the run

Stage 10 does not close while this run's residue is live. Walk the inventory once
more, and for each item either end it or account for it:

1. **Enumerate every class.** Not the ones you remember using — all eight, because
   the one you forgot is the one still running.
2. **End what this run started**, in dependency order: remote state first (a draft
   PR or a flipped flag is visible to other people), then services, then
   worktrees, then leases, then scratch files.
3. **Verify each teardown by re-reading, not by the reply.** A cancel, delete or
   teardown call will happily accept an id that was never scheduled and return
   success. Enumerate again after tearing down; the second enumeration is the
   evidence, the first reply is not.
4. **Write what remains into the run ledger**, with its owner:

```
holds: 10 — none — enumerated 8/8 classes
holds: 10 — 1 (container: pg-test, operator asked for it to stay) — enumerated 8/8 classes
```

An item left standing on purpose is fine. An item left standing silently is how
the next run starts against a database somebody else's test seeded.

---

## What must **not** be torn down

**Tear down what this run started. Report what it did not.**

The inventory is machine-wide; the authority is not. Another session's monitor,
another agent's lease, a container that was up before this run began — killing
any of those is a run reaching outside its own boundary to make its own number
look better, and it will break work that is going fine.

- **If the run did not start it, it does not end it.** Name it in the ledger as
  *foreign*, with whatever identifies its owner.
- **A lease held by another agent is never released by this run**, no matter how
  stale it looks. Stale is a judgment; the holder is a fact.
- **Ambiguous ownership is reported, not resolved.** A worktree with no obvious
  creator is `holds: 1 (worktree, owner unknown)` — which is honest — rather
  than deleted, which is irreversible.

The asymmetry is deliberate: leaving something running costs a little, and killing
something someone else owns costs a lot.

---

## Three owners, not two — and the third is where cleanup actually happens

The rule above splits the world in two: what this run started, and what it did not.
**Dry-running this doctrine on its own project found the state it has no slot for.**

Measured 2026-08-11, enumerating the eight classes on a live run:

```
worktrees/branches : 3 feature branches, all merged into main, from earlier runs
containers         : 18 running, none started by this run, oldest 3 days,
                     across four unrelated projects
```

The branches are not this run's, so *end what you started* does not reach them. They
are not foreign either — the project owns them, and reporting them every run forever
is how a report becomes wallpaper. So:

| Owner | What to do | Why |
|---|---|---|
| **this run** | end it, in dependency order | it exists because of work that is now finished |
| **an earlier run of this project** | end it **when it is provably spent**, and say you did — a branch merged into the default branch, a worktree with no diff, a scratch file from a completed run. Otherwise report it | this is the accumulation nobody is otherwise responsible for, and *provably spent* is a fact rather than a judgement |
| **anything else** | **report, never end** | see the section above; the asymmetry is not negotiable |

**"Provably spent" is the whole load-bearing phrase.** A branch merged into the
default branch is spent — `git merge-base --is-ancestor` says so, and nothing is lost
by removing it. A branch that merely *looks* abandoned is not spent, and the run that
deletes it is guessing about someone's work in progress. **If the proof needs a
judgement, the item is reported, not ended** — which puts it back under the rule
above rather than creating an exception to it.

**A foreign item never becomes spent.** The 18 containers above belong to other
projects; that they have been up for three days is information for whoever owns them,
not permission. The third owner state widens what a run may clean **inside its own
project** and widens nothing at all outside it.

## Rationalizations

| The excuse | What it actually means |
|---|---|
| "The task list is empty, so nothing is running." | The measured case above: the list was empty and the process was polling. Silence from one tool is evidence about that tool. |
| "It will exit on its own." | Some do. The ones that leak are exactly the ones that do not, and you cannot tell which is which without enumerating. |
| "I will clean up at the end." | Residue in flight has already corrupted the run by then. That is why this is a gate criterion, not a final stage. |
| "The container is tiny." | Its cost is not its size. It is invisible, it holds state, and it will still be there tomorrow. |
| "I did not start any background work this stage." | Then the enumeration takes ten seconds and prints `holds: 0`. The cheap case is not the reason to skip the check. |
| "The lease is obviously stale." | Stale is your judgment about someone else's work. Report it; do not release it. |
| "Tearing it down returned success." | So does tearing down an id that never existed. Verify by re-enumerating. |
| "`holds: 0` looks better in the ledger." | Then the number has become a target and has stopped being a measurement. A legitimate 2 is worth more than a manufactured 0. |
