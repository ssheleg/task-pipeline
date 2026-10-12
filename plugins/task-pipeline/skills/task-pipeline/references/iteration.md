# Release iteration — the loop around the waves

*Release iteration* here is the whole loop, survey to next pool. It is not the loop
iteration of [`progress.md`](progress.md) and [`continuity.md`](continuity.md) — one item
taken to its gate — and this file never shortens it to "iteration".

[`waves.md`](waves.md) closes one board in one release. This file is the loop around it:
**survey → design the next version → build in parallel → verify as each part lands →
document → release → check the release → show the operator the next pool → repeat.** A
project moves forward in whole releases. It does not move fix by fix.

Decided by the operator on 2026-10-12. The reason, in their words: a fix made alone
reproduces new defects and breaks earlier ones, and some fixes are already obsolete by the
time they land. Seeing every problem at once lets the next version solve them together.

## Contents

- No fix travels alone
- The cycle
- Module dossiers
- Integration, until it converges
- Question rounds — asked in batches, never blocking
- Verification starts when a node lands
- The token budget
- Release, then check the release
- The next pool
- The learning loop — every run reads what earlier runs learned
- What the operator sees, and when
- Rationalizations

## No fix travels alone

**A finding made mid-release-iteration joins the inventory. It is not fixed where it was found.**
A fix designed against today's state is the intermediate state that
[`waves.md`](waves.md) → *The rule it exists for* refuses: the next version moves the
seam, and the fix is then paid for twice. The finding gets an id in its owning register
and lands on a canvas node. Its wave decides when it is built.

**The hotfix lane is the only exception, and it is closed.** It has five entries:
- production is down;
- data is being lost or corrupted;
- a credential has leaked;
- a security hole is open to someone outside;
- money or a legal obligation is failing.

A hotfix is minimal and ships alone. Within the same hour its node joins the canvas. The
release iteration then either designs the real fix or records the hotfix as final, with the
reason. "It is quick" is not one of the five entries.

## The cycle

| # | Step | Produces | Done when |
|---|---|---|---|
| 1 | Survey (wave 0) | audit agents per area, plus a harvest of every board → `<topic>-inventory.json` | every source in the ledger was read, and every finding has evidence and an id |
| 2 | Module dossiers | one dossier per cluster of items, written in parallel | every inventory item sits in exactly one dossier |
| 3 | Integration | the canvas of the next version ([`waves.md`](waves.md) → *The canvas*) | a pass changes no dossier, or the remaining conflict became a question |
| 4 | Question round | answers from the sources, then one batch to the operator | every question is answered, assumed, or blocks a named node |
| 5 | Plan | the work graph with waves, and one packet per node | every REQ lands on a node; [`planning.md`](planning.md)'s set comparison holds |
| 6 | Build | parallel agents, each owning disjoint files | each node is committed on its branch, with its own checks green |
| 7 | Verify | rounds per node, starting as each node lands | each node passes its risk class's rounds |
| 8 | Seam check | cross-module checks per seam group | every seam the canvas names is exercised end to end |
| 9 | Docs | stage 9 over everything the release iteration shipped | the doc gate passes and the docs match the code |
| 10 | Release | versions, tags, pins, changelogs, in dependency order | the published artefacts resolve |
| 11 | Post-release check | the stage-8 trio on what was released | every item the release claims closed is checked on the released artefact |
| 12 | Next pool | the re-measured inventory and the proposal | the hand-back is sent |
| 13 | Retrospective | the project retro, plus the shared lesson store where one exists | written last ([`retrospective.md`](retrospective.md)) |

Steps 1–4 are stages 0–4 run once. Steps 6–8 are stages 5–8 per wave, and a wave's
stage 7 **integrates to the main branch without tagging**: its lint, suite and CI verdict
hold, nothing is published. Step 9 is stage 9. **Step 10 runs stage 7's full release gate**
once, for the release: the release's approval mode, the CI verdict read for the commit
being tagged, and the operator's specific go or a standing authorization that names the
act. **Step 11 runs stage 8's verification trio** on what was released. Steps 12–13 close
with stage 10. No gate in [`stages.md`](stages.md) is skipped. The cycle changes when each
stage runs, and over what.

## Module dossiers

**One dossier per cluster.** The inventory is grouped by the part of the system each item
touches, not by where it was found. One agent writes each dossier, all in parallel. A
dossier carries:
- the items it answers, by id;
- each module and contract as-is, and to-be;
- the options considered, with the choice and its reason;
- the contracts it changes, and who owns each side;
- the tests that will prove it, including one that fails today;
- the migration;
- what it deletes ([`waves.md`](waves.md) → *The canvas*, item 4);
- its open questions;
- the nodes it proposes, each with **its own** risk class (*Verification starts when a node
  lands*, below). A dossier has no risk class: one R3 node beside four R1 nodes is five
  classes, and a dossier-wide class either over-checks the four or under-checks the one.

The shape is [`templates/dossier.md`](../templates/dossier.md).

**A dossier is a design, not a plan.** It does not cut waves. That is step 5, made once
over all the dossiers together.

## Integration, until it converges

The orchestrator lays every dossier onto the canvas and looks for two dossiers that change
one seam, one contract or one file. Each such pair is re-designed together: the two
agents, or one agent holding both dossiers.

**The pass repeats until it changes nothing**, capped at three passes. At the cap, the
conflict that remains becomes a question with both designs attached. Two designs left to
"meet in the build" are the intermediate state again.

## Question rounds — asked in batches, never blocking

**One queue:** `<artifacts>/specs/<topic>-questions.md`. Each row carries:
- an id;
- the node or nodes it blocks;
- who raised it;
- the sources tried, with citations;
- the recommended answer;
- the consequence of each answer.

**An agent that meets a question never waits on it:**
1. It closes the question from the sources if it can ([`waves.md`](waves.md) → *The
   questions*).
2. Otherwise it writes a row.
3. If the answer is internal and reversible, it proceeds on the recommendation, marked
   **assumed** on the node. Otherwise it parks the node `needs-operator`.
4. It takes another node.

**A round is called on the first of three triggers:**
- the whole frontier is blocked;
- five questions are open;
- a wave boundary is reached.

In a round, the orchestrator first re-closes from the sources, because a dossier or a
landed node may have answered the question since. The rest go to the operator as one
batch, each with its recommendation. Questions from peer sessions join the same queue.

## Verification starts when a node lands

**The checks are a pipeline, not a barrier.** A node is built when it is committed on its
branch with its own checks green. Its certification ([`certification.md`](certification.md))
starts at that moment, while other nodes are still being built. A wave never waits for
its slowest node before checking its fastest.

**The number of rounds follows the node's risk class.** The class is recorded on the node
as `risk` (R1–R3, [`work-graph.md`](work-graph.md)), computed from what the node touches.
It is never lowered to save time. **A round is the three blind tiers of
[`certification.md`](certification.md) plus one fix cycle**, and the first round is always
the full three tiers — there is no lighter first reading. The class sets how many rounds
the node owes:

| Class | Touches | Rounds |
|---|---|---|
| R1 | docs, config, a mechanical change, one isolated file | 1: that first round |
| R2 | an ordinary feature or fix inside one module | 2: the first round, then a second over the fix diff with its regression tests |
| R3 | security, cryptography, money, a data migration, a public contract, a seam across repositories, concurrency | 3: the first two, then an adversarial round that plants defects and tries abuse cases, on another model where one is available |

- Each round's fix cycle stays inside [`loop-guard.md`](loop-guard.md)'s caps. A finding
  that cannot be fixed in the node is parked with a board row.
- `graph.py close` refuses a node until its owed rounds have passed, and an R3 node until
  one of them was recorded adversarial ([`certification.md`](certification.md) → *Rounds
  owed by risk class*, which also says what a round after a clean one reads and how the
  adversarial round is run).
- Every owed round runs, and every round re-runs all three tiers: a tier that passed in an
  earlier round read a tree the fix has since moved ([`certification.md`](certification.md)
  → a passing tier is re-run). A clean round does not cancel the next one; R3's third round
  asks a different question — it hunts for a planted defect — and always runs.
- Readers stay blind ([`certification.md`](certification.md) → *Blind*). Each reads the
  diff, the packet and the contract, never the builder's reasoning.

**Seam checks wait only for their seam group.** Nodes that share a seam are checked
together once the last of them lands. Nodes on other seams do not wait.

## The token budget

The method is cheap by construction. These rules keep it cheap:

- **The orchestrator holds the plan, not the work.** It reads each agent's structured
  output — findings JSON, eight-key verdicts — and never a transcript.
- **A packet is all the context an agent gets** ([`planning.md`](planning.md)): the node,
  the files it owns, the contracts, the exit criteria and the output schema. It gets no
  conversation history.
- **Diffs and their files, not repositories.** Ask the graph for reach
  ([`knowledge-graph.md`](knowledge-graph.md)) instead of sweeping with grep.
- **Machines first.** Tests, validators, schemas and linters run before any model reads
  anything. A model reviews only what they cannot decide.
- **An axis ends when its findings become restatements** ([`audit.md`](audit.md) → *Exit criterion — the part usually
  skipped*).
- **One agent per seam, not per file.** Keep the number in flight within the harness's
  size guideline and queue the rest.
- **An agent cut off by a rate limit or an outage is resumed with its context**, not
  relaunched from zero. Its output file is its checkpoint.

## Release, then check the release

**One release per release iteration** carries every repository it touched:
- versions, changelogs and tags;
- every pin moved, in dependency order — a contract before its consumers;
- every parent's submodule pointer ([`stages.md`](stages.md), stage 10).

**The release is checked in the same run.** Run stage 8's verification trio on what was
actually published, installed or deployed — never on the branch. Each item the release
claims closed is re-checked against the released artefact. A failure goes to the hotfix
lane if it is one of its five entries. Otherwise it goes to the next pool, with an id.

## The next pool

1. **Re-measure the inventory.** Items closed stay closed. Items open are re-checked
   against the code. New items join with ids: the post-release check's findings, peer
   requests, the operator's new asks.
2. **Re-prioritise** ([`prioritisation.md`](prioritisation.md)), then group by module the
   way the dossiers were grouped.
3. **Hand back once** ([`progress.md`](progress.md) → *The hand-back*). The message holds:
   - what the release shipped, with evidence;
   - what is still open, by module;
   - the proposed scope of the next release iteration and its question batch.

The proposal is a recommendation. The next release iteration starts on the operator's go, unless
a standing instruction arms the loop ([`continuity.md`](continuity.md) → *The limit, before
the capability*: the ledger then cites it as `loop: armed by <source>`). Its outward acts —
a release, a tag, a deploy — still need their own specific authorization.

**On an armed loop the run does not stand still at the sign-off.** Stage 10's sign-off
of the release is the operator's; it goes on a watcher or a board row
([`continuity.md`](continuity.md) → *Waits outlive turns*), and the next release
iteration's survey may start meanwhile. **Nothing the unsigned release claims counts as
closed** until the sign-off lands: the survey reads those items as open, with the release
named beside them.

## The learning loop — every run reads what earlier runs learned

**One lesson format, two layers, one read recipe.** A *lesson* is a retro entry's class,
stated so an agent on another project can use it: lesson/1,
[`templates/lesson.schema.json`](../templates/lesson.schema.json). The project retro stays
canonical ([`retrospective.md`](retrospective.md)); everything below is a projection of it
that can be lost and rebuilt. A retro entry becomes a lesson when its author gives it a
`**Lesson:**` line — the class key, the class in one sentence, when it applies, and 3–8
search nouns ([`templates/retro.md`](../templates/retro.md)). An entry without one is
private to its project and never leaves it.

**Layer 1 — every install, no service.** The project retro and [`learned.md`](learned.md),
as before, plus a **local index** of every project's lessons on this machine:
`scripts/lessons.py`, one JSON line per class, a pure function of the retros
(`lessons.py rebuild --roots <dir>` re-derives it). Two projects holding one class key make
one lesson seen twice, status `candidate`. The index path is a parameter — `--index`, then
`$TASK_PIPELINE_LESSONS`, then `~/.sshlg-skills/lessons/index.jsonl` **when
`~/.sshlg-skills` already exists** — the family's machine-state directory, where the family
accepted `lessons/` as task-pipeline's on 2026-10-12 ("state-json.md gets the entry when it
ships"; until it ships, that agreement is the contract) — and otherwise
`~/.task-pipeline/lessons/index.jsonl`, so a standalone install never creates the family's
directory. Nothing in this skill writes anywhere else under either.

**Layer 2 — where the session lists a shared store.** An Observatory (the public engine,
[passioncode-ai/project-observatory-dashboard](https://github.com/passioncode-ai/project-observatory-dashboard)),
detected by the tools the session lists, never by a path. Lessons there are the agents'
work memory, written as proposals below full confidence; the store's own rules decide who
promotes one.

**What a lesson may carry — one rule list, one relaxation.** The redaction list in
[`retrospective.md`](retrospective.md) → *What may leave the project* binds every lesson.
A lesson kept **on this machine or estate** — the local index, the shared store — relaxes
rule 2 (no host identifiers) for exactly two fields, and nothing else:
- **`origin.commit`, the evidence commit**, as a SHA: the only way a later reader, or the
  store's corroboration, can check the lesson against the change that taught it. A private
  repository's SHA names nothing to someone without the clone; **a public repository's SHA
  is searchable** and leads to the repository, so it stays in this field and never in text;
- **`origin.project`, the pseudonymous project key** — `p-` and 12 hex digits of the
  repository's root commit — stable across clones and never the repository's name, because
  lessons are read into *other* projects' briefs and a repository name can be a customer's
  or a product's. The shared store receives the same key, never a `project:<slug>` id.

Rules 1, 3, 4 and 5 still bind every text field, on the estate as off it: no path at all,
no code or value, no person's, company's, customer's or product's name, and a title that
states the class rather than the incident. Never, in either layer, a transcript or a URL.
`lessons.py` refuses what a pattern can see (paths, URLs, addresses, credential shapes, long
hex or base64 runs) and any field lesson/1 does not name; a name it cannot see stays the
writer's duty. Off the estate (`retro.publish`) the relaxation ends: the whole origin is
stripped.

**Read, at stage 0 — source 7b of [`knowledge-sources.md`](knowledge-sources.md).**
1. Always: `lessons.py query <the task's 3–6 nouns> --limit 5`. The source ledger prints
   one of three local states: `local lessons: <N> match`, `local lessons: absent` (no index
   yet), or `local lessons: unavailable (no python3)`.
2. If the session lists `observatory_search`: **the first call is the probe** —
   `observatory_search(query=<the same nouns>, kinds=["lesson","learning"], limit=5)`, with
   no project id, because the question is what *other* projects learned. Its answer decides
   the state:
   - hits that carry a `kind` field: the filter works — cite the lessons that fire, and print
     `shared lessons: <N> match`;
   - hits without `kind`: an engine with no kind filter, where turn records crowd lessons out
     of the match window — do not read them, print `shared lessons: unfilterable (no kind
     filter)`;
   - no hits at all: nothing says whether the filter ran — print `shared lessons: 0 match
     (filter unknown)` and read nothing more.
   No such tool: `shared lessons: absent`.
3. Cite a lesson that fires as `[lesson L-<12 hex>]` (local) or
   `[lesson mem:<id>@<rev> · proposed|observed]` (store). A `proposed` lesson is advisory and
   the brief says so; an `observed` one binds like a standing instruction of the retro.
4. Budget: at most ten lines from both layers together. The brief carries only the lessons
   that fire.

**Write, at step 13 (stage 10's retro).** For each entry that carries a `**Lesson:**` line:
1. `lessons.py add --retro <retro file> --entry <anchor>` — always. It validates lesson/1,
   checks that the commit resolves here, and merges; a repeat from the same project revises,
   never mints.
2. If the session lists the store: `lessons.py emit-observatory <L-id>` prints
   `{tool, arguments}` for `observatory_record` — a note whose statement starts `lesson:`, so
   lessons accumulate today and a later migration finds them. It carries the pseudonymous
   key, never a `project:<slug>` id, and the commit as **`commit:` + 12 hex**: the store's
   redactor removes a 40-hex SHA as a credential shape and keeps exactly that short form. A
   lesson already recorded from this origin is emitted with `memoryId` and
   `expectedRevision`, so the store revises it instead of minting a second one. **The lesson
   tool and the kind filter arrive with the engine's lesson kind** (an `observatory_lesson`
   tool, `kinds` on search); until the session lists them this skill offers neither.
   `observatory_learn` is not the retro write: it contrasts a failure record with its fix
   inside one project, and a retro entry is neither.
3. The agent calls that tool, then `lessons.py record <L-id> --answer -` keeps the memory id
   beside the local entry. A refusal is one ledger line, `event: lessons — store refused —
   <code>`, and the local entry stays.
4. No store: the ledger says `shared lessons: absent`, once per run.

**Promote.** `lessons.py candidates` lists the lessons two or more projects hold: the
[`learned.md`](learned.md) queue, through `retro.publish` and its redaction list. In the
store, a lesson two projects recorded rises by the store's own corroboration rule, never by
this skill.

**When there is no store, the source ledger says so**, and the first layer runs exactly as
before. The store is never a hard dependency; neither is python3 — without it the ledger
prints `local lessons: unavailable (no python3)` and the retro is read as before.

## What the operator sees, and when

A release iteration has three planned touchpoints, plus every human gate:
1. **The planning gate** — the inventory summary, the canvas, the wave plan and the
   question batch, in one message ([`waves.md`](waves.md) → *How the stages map*).
2. **A question round** — only when one of its three triggers fires.
3. **The release hand-back**, with the next pool.

Sign-ins, consents, payments, sending to people and every outward or irreversible act stay
the operator's ([`waves.md`](waves.md) → *What stays human*) — unless a specific standing
authorization names the act ([`continuity.md`](continuity.md) → *The limit, before the
capability*): a recorded "releases are the agent's" decision is such a record for the tag
and the publish its release run performs.

## Rationalizations

| Excuse | Reality |
|---|---|
| "This bug is tiny, fix it now" | Tiny fixes are what move a seam twice. It joins the inventory, or it is one of the hotfix lane's five entries |
| "Wait for the whole wave, then verify" | A barrier idles every finished node. Each node is certified when it lands |
| "R3 found nothing in round 2, skip the adversarial round" | Round 3 asks a different question: it hunts for a planted defect. A clean round 2 does not answer it |
| "Ask the operator now, it is quick" | Each question is a human round. Queue it and take another node |
| "The agent hit a rate limit, start it again" | Resume it with its context. Relaunching pays for the same reading twice |
| "No Observatory here, so no learning loop" | The project retro and learned.md are the loop's first layer, and every install has them |
| "Release first, check later" | An unchecked release is the item the next release iteration rediscovers. Step 11 is inside the run |
