# Knowledge sources — harvest before the grill, update after the build

Stage 0 has two phases. This file is **phase 1**: before the first question is
asked, find and read what the project already knows about this task. The interview
([`grill.md`](grill.md)) is phase 2, and it runs *against* what was harvested here.

The same source list closes the loop at **stage 9**: what was read at the start is
what gets updated at the end. A source good enough to answer a question is a source
that goes stale when the answer changes.

## Contents

- Why this is a phase and not "explore a bit first"
- The sources, in the order to try them
- The retro's standing instructions — an instruction source, not background
- The code graph — recommended
- The knowledge wiki — recommended
- How to harvest — retrieval, not reading
- Record it — the source ledger
- The source is not the copy you have
- Carried-in claims — measured or recalled
- Phase 2 — validate the answers against the harvest
- Close the loop — stage 9 updates what stage 0 read
- Rationalizations

## Why this is a phase and not "explore a bit first"

An agent that starts asking without harvesting spends the operator's turns on
questions the project already answered — in an ADR, in a runbook, in a wiki page
written three months ago by the same person now being asked. That is the expensive
failure, but not the worst one.

The worst one is silent: **the operator misremembers, the agent believes them, and
the run builds on it.** People answer from memory about systems they wrote a year
ago. Without the documents in hand you cannot tell a decision from a recollection,
so every later gate passes honestly on a false premise. Harvesting first is what
makes the grill's answers *checkable* instead of merely confident.

## The sources, in the order to try them

| # | Source | How to find it | What it's good for |
|---|---|---|---|
| 1 | **The code** | the repo you're in | what actually runs — the tiebreaker |
| 2 | **The code graph** | `graphify-out/graph.json` — see below | *reach*: what calls this, what breaks if it moves, what every change passes through |
| 3 | **Host agent docs** | `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/` | conventions, commands, deploy path, house rules |
| 4 | **Domain docs** | `CONTEXT.md` / `CONTEXT-MAP.md`, `docs/adr/` | the glossary and the decisions with their reasons |
| 4a | **The decision register and the doc map** | `docs/DECISIONS.md` **or** `docs/adr/` — `docs/DOCMAP.md` says which ([`documentation.md`](documentation.md)) | what is already settled, what it superseded, and which documents this run will owe |
| 4b | **The task register, for its *state*** | `docs/ROADMAP.md`, a board, a backlog, the tracker `CLAUDE.md` names | **what is open right now** — read with a command, never from memory; see *Carried-in claims* |
| 5 | **Product/UX docs** | `docs/ux/` (super-ux chain), `README`, runbooks | user-facing behavior that is already specified |
| 6 | **Pipeline history** | `docs/superpowers/specs/`, `plans/`, past `-carryover.md` | what a previous run of this pipeline decided or deferred |
| 7 | **The retro, in force** | `docs/superpowers/retro.md` ([`retrospective.md`](retrospective.md)) | what previous runs got wrong here — **read in full**: standing instructions (capped at ten), run stamps and the recent-log window, all bounded by construction |
| 7a | **The retro archive** | `docs/superpowers/retro/YYYY-QN.md` | *have we been bitten by this class before?* — **queried** by the task's nouns, never read end to end |
| 8 | **The knowledge wiki** | see below | distilled cross-project knowledge, prior sessions, why decisions were made |
| 9 | **Other doc repos the project names** | a docs repo URL or submodule in `CLAUDE.md`/`README`, a sibling checkout, a `docs/` monorepo package | specs, contracts and runbooks that live outside this repo |
| 10 | **Hosted doc systems the project names** | Notion / Confluence / Google Docs referenced in the project | the same, when the team keeps them there |

Rules for the list:

- **Never invent a source.** A doc repo is in scope because the project names it,
  not because it plausibly exists. Nothing is cloned or fetched on a guess.
- **Sources 9–10 are read-only at this stage**, and reading a hosted system needs a
  connected tool — if there's no tool, record the gap and ask the operator to paste
  what matters rather than pretending the source was covered.
- **The wiki and the graph are optional; the harvest is not.** With no wiki, no
  graph and no doc repos, the harvest is sources 1 and 3–7 and takes two minutes.
  Skipping it is never the answer.
- **Source 7 is read in full where it is bounded, and queried where it is not.** The
  standing instructions (capped at ten) and the run stamps (one line each) are read;
  the *Recent log* is queried by the task's nouns like the archive. Measured on the
  file this doctrine was written for, the log was **74% of it** — and it is the one
  section nothing caps. Source 7 is still the source that *binds* the run rather than
  informing it; that is why the part which binds must stay cheap enough to read.

## The retro's standing instructions — an instruction source, not background

`docs/superpowers/retro.md` ([`retrospective.md`](retrospective.md)) is the one
harvested source whose binding part is **read in full rather than queried**: the
standing instructions are capped at ten precisely so that this is cheap, and the run
stamps are one line each. Its narrative log is queried, not read — an uncapped section
inside a source that binds is how the capped part stops being read. They are what
previous runs of this pipeline got wrong *in this project* — the rules no check
could decide — and they bind this run.

Two obligations that come with reading them:

- **Stamp an instruction the moment it fires.** That date is the only evidence
  behind the cold-retirement rule at stage 10; without it "hasn't fired in five
  runs" is a guess and the prune becomes a mood.
- **Record the file as a ledger row**, like any other source. It is also the row
  stage 10 writes back to, which is what closes this particular loop.

## The code graph — recommended

Full doctrine: [`knowledge-graph.md`](knowledge-graph.md). In one paragraph: a grep
finds a **name**, a graph finds **reach** — what calls this, what breaks if it
moves, which module every change passes through. That is the class of question the
harvest most needs answered and the class documents answer least reliably, because a
document records the reach its author remembered.

**Detect it** — `graphify-out/graph.json` exists (built), or `graphify` resolves but
the directory doesn't (installed, not built).

- **Built → query it** during the harvest: `graphify query "<the task, as a
  question>"`, `graphify affected "<the thing being changed>"`, `graphify god-nodes`.
  Record the row **with the graph's measured lag** — how far behind `HEAD` it is and
  which signal said so — because a graph is a source and goes stale like one, and a
  build date is the graph's own reply about itself rather than a measurement of it.
  The three commands and the three states:
  [`knowledge-graph.md`](knowledge-graph.md) → *Measure the lag*.
- **Not installed → recommend it once**, in the preflight block, with the lines:

  ```bash
  uv tool install graphifyy      # the CLI
  graphify install               # add the /graphify skill to this agent
  ```

  then `/graphify .` in the project root. Then continue — it is a
  **recommendation, never a gate**, exactly like the wiki.

The graph **points; the code decides.** Retrieval order puts it right after the
code, never as the tiebreaker.

## The knowledge wiki — recommended

The wiki this pipeline is built to work with is
**[obsidian-wiki](https://github.com/ar9av/obsidian-wiki)** (Karpathy's LLM-wiki
pattern: raw sources → distilled wiki → schema). It is the one source that carries
*why* across projects and across months, which is exactly what a fresh context lacks.

**Detect it** — any of: `~/.obsidian-wiki/config` exists; the `wiki-query` /
`wiki-update` skills resolve.

- **Installed → use it.** Query it during the harvest (`wiki-query`, or the vault's
  `index.md` + a targeted grep when the skill isn't loaded), and sync back at stage
  9 (`wiki-update`).
- **Not installed → recommend it once, in the preflight block, with the line:**

  ```
  pip install obsidian-wiki
  obsidian-wiki setup --vault /path/to/your/vault
  ```

  Then continue without it. It is a **recommendation, never a gate** — no stage
  blocks on a missing wiki, and the pipeline never nags twice in a run.

## How to harvest — retrieval, not reading

The harvest is bounded by the *task*, not by the size of the sources. You are not
reading the wiki; you are asking it about this task.

1. **Take the task's nouns** — the entities, the feature name, the subsystem, the
   file paths the operator mentioned — plus their obvious synonyms.
2. **Query each source with those terms**: `wiki-query` for the wiki; `grep`/`Read`
   for repo docs; the tracker/hosted-doc tool if one is connected.
3. **Follow one hop, not ten.** A hit that names an ADR, a scenario id or a module
   is worth opening. A page three links away is context, not evidence.
4. **Stop when the terms stop returning anything new.** Same rule as the interview:
   no grinding past diminishing returns.

## Record it — the source ledger

Write what you found into the brief's **Knowledge sources** section
([`templates/brief.md`](../templates/brief.md)) before the first question. One row
per source actually consulted:

| Source | What it says about this task | Fresh? | Authority |
|---|---|---|---|
| `docs/adr/0007-single-write-model.md` | orders are written only through the command handler | 2026-03 | decision |
| wiki: `projects/x/concepts/billing-seams` | why invoicing was split out; the retry rule | 2026-06 | context |
| `CLAUDE.md` | test = `npm test`, deploy from `main` only | current | convention |
| (none for the export UI) | — | — | — |

The ledger is what makes phase 2 work: during the interview you cite rows from it,
and at stage 9 you update the same rows. A source consulted but not recorded is a
source nobody will update.

**"No sources found" is a valid, recorded outcome.** Write the row. An empty ledger
tells the next run that the search happened and came back empty — silence doesn't.

## The source is not the copy you have

`learned.md` rule 17. The harvest reads the project's own files, and one property of them is
invisible to reading: **whether this checkout is the one that ships.** A working copy two commits
behind its upstream looks exactly like a current one — clean tree, no conflict, `git status` says
nothing is wrong — and an edit on top of it deletes the newer work by fast-forward rather than by
collision.

Before the first edit, in any repository that has an upstream:

```bash
git fetch -q && git rev-list --count HEAD..@{u}     # 0, or stop and pull
```

Print the number. `0` is the measurement; the absence of a complaint is not.

This matters most where it is least suspected — a skill, a plugin, a fork, a vendored library —
because those are the repositories a machine keeps **twice**, once to publish from and once to run,
and the one a person opens is chosen by a path in some documentation rather than by which is
current.

## Carried-in claims — measured or recalled

The harvest exists because *the operator misremembers*. This section exists because
**the agent does too**, and it is the harder case: a run that resumes from a
summary, a handoff note or a compacted context inherits a pile of statements that
read exactly like findings and have no source attached.

They are not lies and they were not wrong when they were written. They are **stale
by construction** — a filtered subset that lost its filter, a status true two weeks
ago, a blocker that cleared while nobody was looking. And unlike a wrong number,
stale state **does not throw**. It narrows what the run considers, and every gate
after it passes honestly on the smaller world ([`learned.md`](learned.md) rule 16).

**Every inherited claim starts as `recalled`.** Before it is acted on *or reported
to the operator*, it is either re-derived from its source and marked `measured`, or
it is not stated. Add the column to the ledger and use it:

| Claim | Whence | State | Re-derived by |
|---|---|---|---|
| 36 of 99 rows open; 4 blocked | `docs/ROADMAP.md` | measured | `bash scripts/board.sh` |
| the suite is green | prior session | measured | `npm test` → 601 pass |
| `NBA-046` has no producer | prior session | **recalled** | not checked — do not report |

Three claims that go stale most reliably, and all three are cheap to re-derive:

- **The work-list.** What is open, what is blocked, and *on what*. If the project
  has a register, the harvest reads it with a command and records the counts. A run
  that says *"what remains is X"* without this is guessing out loud.
- **Green.** A suite, a gate, a deploy. Run it; the answer is a minute old, not a
  session old.
- **A blocker or a premise.** *"Blocked on Y"*, *"nothing produces this"*,
  *"that endpoint doesn't exist"*. These clear silently — somebody else's work
  lands and no signal reaches this run.

**Where the command comes from.** The grill's autonomy sweep settles it once, at
stage 0: which register holds task state and what reads it. A project without one
records the row empty and the rule costs nothing.

**And it is per iteration, not per session.** In loop mode ([`continuity.md`](continuity.md))
the harvest's documents may be carried between iterations — they did not change.
**The work-list line may not.** It is the one row the previous iteration's own work
invalidates.

## Phase 2 — validate the answers against the harvest

This is the payoff, and it belongs to the grill loop
([`grill.md`](grill.md) → *Domain awareness*). Every operator answer that touches a
harvested source gets checked against it, on the spot:

> "The ADR from March says orders are written only through the command handler —
> you just described a direct write. Has that changed, or should the export go
> through the handler?"

Three shapes and what to do with each:

| The answer… | Do |
|---|---|
| **agrees** with the source | nothing — note it, move on |
| **contradicts** a source | quote the source, name the conflict, ask which governs. The answer is either "the doc is stale" (→ it gets updated at stage 9, log it now) or "I misremembered" (→ the doc stands). Both are cheap here and expensive at stage 6 |
| **goes beyond** every source | this is new knowledge — it belongs in the brief, and usually in `CONTEXT.md` or an ADR as it lands |

**The operator outranks the docs — but only out loud.** A person may overrule any
document; they may not do it by accident. The point of quoting the source is that
the override becomes a recorded decision instead of an undetected divergence.

**Precedence — and it splits in two, because two different questions are being
asked.**

*For what **is**:* code, then host docs and ADRs, then the wiki, then anyone's
memory. The wiki is *distilled* knowledge and can lag the repo by months; the code
is what runs.

*For what **should be**:* the **register outranks the code**
([`documentation.md`](documentation.md)). A decision that is accepted and not yet
built is still the decision, and code that contradicts it is a finding — a bug, or
an unrecorded reversal — never a tie-break in the code's favour. Getting this
backwards is how a run "discovers" that the system does not work the way the
project decided, and quietly builds the version it found.

Either way a disagreement is a grill question, never a silent pick, and it is
usually a sign that something is due an update.

## Close the loop — stage 9 updates what stage 0 read

The ledger is the stage-9 work list. For each row:

- **Host repo docs, ADRs, runbooks, `docs/ux/`** — updated in the **same change**,
  per the host's own rules ([`conventions.md`](conventions.md)).
- **The register and the doc map** — every decision this run settled gets an entry
  with an id; every question it answered is flipped; the doc map gains any new
  document class or ratchet. Note that this list and the **propagation matrix** are
  different lists on purpose: the ledger is what you *read*, the matrix is what you
  *owe* ([`documentation.md`](documentation.md)), and stage 9 walks both.
- **The retro** — stamp, prune, entry, and rotate what aged out into the archive
  ([`retrospective.md`](retrospective.md)).
- **Anything the run proved stale** — including a doc that was "wrong but nobody
  had time": that's why the conflict was logged in phase 2 instead of only being
  resolved verbally.
- **The wiki** — `wiki-update` syncs what this run learned. Distil the *knowledge*
  (decisions, seams, gotchas, why), never a diff summary.
- **The graph** — `/graphify . --update` re-extracts what this run changed
  ([`knowledge-graph.md`](knowledge-graph.md)). It is a **peer of the docs, not an
  afterthought**: the next run's harvest queries it first, and a stale graph is a
  false premise delivered with the authority of a machine. A wrong doc gets argued
  with; a wrong graph gets believed. Refreshing it also enables the cheap half of
  the **divergence check** — a hub no doc names, an edge the docs deny, a doc naming
  a module the graph no longer has.
- **Another repository's docs** — writing to a repo the operator didn't ask you to
  touch is **outward**: propose the change, get an explicit go, then open a PR
  there. Absent a go, it goes in the carry-over ledger with the exact edit needed.

A source that was worth reading at stage 0 and is wrong at stage 9 is the next
run's false premise. Closing that loop is the whole point of harvesting from a
written list instead of from whatever the search happened to surface.

## Rationalizations

| Excuse | Reality |
|---|---|
| "I'll just ask them, it's faster" | You'll ask about things a doc already answers, and you'll believe an answer you can't check. Retrieval is cheaper than a turn. |
| "The wiki's probably stale" | Then say so with the page in hand and get it corrected. "Probably stale" unread is an assumption; read, it's a finding. |
| "No docs in this repo" | Check `CLAUDE.md` for the repo that has them, and the wiki for the last time anyone touched this. Then record the empty ledger. |
| "The operator knows their own system" | They do — a year ago, before three other people changed it. That's the exact case where quoting the doc pays. |
| "Reading the whole wiki costs too much" | The harvest is a query per task noun, not a read. If it feels expensive, you're reading instead of retrieving. |
| "I'll update the docs at the end from memory" | The ledger exists because the end is exactly when you no longer remember which sources you leaned on. |
| "The summary said what's left, that's the same list" | It was a list *once*, under a filter nobody wrote down. Re-deriving it costs one command; being wrong about it costs every iteration after. |
| "Nothing changed since last iteration" | The previous iteration changed it. That is what an iteration is. |
| "Re-measuring every cycle is overhead" | It is one command against a file you already have open. The overhead is the eleven cycles spent working from a list that was wrong at cycle one. |
