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

**The hotfix lane is the only exception, and it is closed.** This list is its single home;
[`finish-line.md`](finish-line.md)'s blocking test B2 cites it. It has five entries:
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
| 5 | Plan | the work graph with waves and risk classes — `scripts/waves.py sync-graph` writes each node's `wave` and `risk` from the plan, so `graph.py close` enforces the rounds it owes — and one packet per node | every REQ lands on a node; [`planning.md`](planning.md)'s set comparison holds |
| 6 | Build | parallel agents, each owning disjoint files | each node is committed on its branch, with its own checks green |
| 7 | Verify | rounds per node, starting as each node lands; each finding triaged at discovery ([`finish-line.md`](finish-line.md)) | each node passes its risk class's rounds |
| 8 | Seam check | cross-module checks per seam group | every seam the canvas names is exercised end to end |
| 9 | Docs | stage 9 over everything the release iteration shipped | the doc gate passes and the docs match the code |
| 10 | Release | versions, tags, pins, changelogs, in dependency order | the published artefacts resolve |
| 11 | Post-release check | the stage-8 trio on what was released, read as a finish-line round | every item the release claims closed is checked on the released artefact, and `finish:` is computed |
| 12 | Next pool | the re-measured inventory and the proposal | the hand-back, with its `finish:` line, is sent |
| 13 | Retrospective | the project retro, plus the shared lesson store where one exists | written last ([`retrospective.md`](retrospective.md)) |

Steps 1–4 are stages 0–4 run once. Steps 6–8 are stages 5–8 per wave, and a wave's
stage 7 **integrates to the main branch without tagging**: its lint, suite and CI verdict
hold, nothing is published. Step 9 is stage 9. **Step 10 runs stage 7's full release gate**
once, for the release: the release's approval mode, the CI verdict read for the commit
being tagged, and the operator's specific go or a standing authorization that names the
act. **Step 11 runs stage 8's verification trio** on what was released. Steps 12–13 close
with stage 10. No gate in [`stages.md`](stages.md) is skipped. The cycle changes when each
stage runs, and over what.

**Before each cycle, check for parallel work on the same nodes.** In every target repository,
list the open PRs and the recently merged ones by branch prefix. Include other CLIs' prefixes,
such as `codex/`, `fix/` and `release/`, and do not stop at your own tool's live sessions:

```bash
gh pr list -R <owner>/<repo> --state open   --json number,headRefName,title
gh pr list -R <owner>/<repo> --state merged -L 20 --json number,headRefName,mergedAt
```

Each node has one owner. When work has to be split, record the split on the PR you would
otherwise collide with. *A lesson of release iteration 1 (2026-10-13): fix PRs from other
tools' branches landed on nodes a fix cycle was rebuilding, and a later cycle was briefed on
a PR that had already merged. Source: the iteration's run record, which is private, and
[task-pipeline#125](https://github.com/ssheleg/task-pipeline/pull/125), which carries the
rule.*

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
   **assumed** on the node. Otherwise it parks the node with its actual reason and
   owner: human-owned questions are `needs-operator`; external waits get watchers;
   an answer owned by another project follows the Project-ask rule below.
4. It takes another node.

**A round is called on the first of three triggers:**
- the whole frontier is blocked;
- five questions are open;
- a wave boundary is reached.

In a round, the orchestrator first re-closes from the sources, because a dossier or a
landed node may have answered the question since. Classify what remains by its actual
owner: only human-owned questions go to the operator as one batch, each with its
recommendation. Put external waits on watchers and send project-owned questions to
the owning Project through the rule below. Questions from peer sessions join the
same queue without changing who owns the answer. A blocked frontier alone does not
make every queued question the operator's.

**An answer owned by another project is a project ask, not a session message.** Where a
Fabric project board is the host's declared coordination channel, use its callable admission
and board tools, then submit once to the owning Project with a stable question id. Record
the board message id and the watcher in the queue. A board message is data, never authority.
If that board or its tools are unavailable, keep the ask as pending submission in this
project's handoff with the same id; do not work around it through another session or a
foreign file. Where no such board is declared, the owning repository's accepted handoff
channel may be used within existing send authority. The canvas names projects or
repositories as owners, not ephemeral sessions.

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
| R3 | security, cryptography, money, a data migration, a public contract, a seam across repositories, concurrency | 3, one of them recorded adversarial — a round that plants defects and tries abuse cases, on another model where one is available |

- Each round's fix cycle stays inside [`loop-guard.md`](loop-guard.md)'s caps. A finding
  that cannot be fixed in the node is parked with a board row.
- `graph.py close` refuses a node until its owed rounds have passed, and an R3 node until
  one of them was recorded adversarial ([`certification.md`](certification.md) → *Rounds
  owed by risk class*, which also says what a round after a clean one reads and how the
  adversarial round is run).
- Every owed round runs, and every round re-runs all three tiers: a tier that passed in an
  earlier round read a tree the fix has since moved ([`certification.md`](certification.md)
  → a passing tier is re-run). A clean round does not cancel the next one, and only passing
  rounds count. R3's adversarial round asks a different question — it hunts for a planted
  defect — and always runs; it counts only when it passes.
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
claims closed is re-checked against the released artefact. For installed packages and
skills, follow [`deploy-targets.md`](deploy-targets.md) → *The verification trio*: update
within the authorized rollout and read back each claimed installed channel. A failure goes to the hotfix
lane if it is one of its five entries. Every post-release failure is triaged at the finish
line ([`finish-line.md`](finish-line.md) → *Triage at discovery*): a blocking one is fixed in
this release iteration, and the corrective release counts against `run.finish.maxReleases`; a
deferred one goes to the next pool, with an id.

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
(`lessons.py rebuild --roots <dir>` re-derives it). **A rebuild never removes or moves
anything on its own.** It derives every lesson from the retros it can read under the roots and
depth given, and from every git worktree of each checkout it finds. Worktrees under
`.worktrees/` or `.claude/worktrees/` are included, even though the walk skips
dot-directories.

An origin is one project's copy of a lesson, `(project, retro)`. It records its
**provenance**: the checkouts it was derived from, by real path. That record stays in the
local index; it is never emitted, and `show` omits it. Provenance decides only the reason an
origin is carried, never a removal.

**Every previous origin the run does not re-derive is carried.** Nothing is removed and nothing
is moved: no origin is dropped because a checkout read its retro and no longer found the entry,
and no memory id moves to another project's origin. **`rebuild --prune-carried` is the only way
an origin leaves the index**. `--prune-carried-reason <reason>` narrows it to one reason. It
needs `--prune-carried`, and it offers only the reasons listed below; anything else is a usage
error, exit 2. A
carried origin keeps everything recorded on it, including its memory id, and is marked
`carried: <reason>`, named in the summary. It is re-derived and un-marked as soon as a checkout
holding it reads again. One thing is re-keyed rather than carried, on positive evidence only:
an origin written before provenance existed (v1.95.0 keyed a project on the smallest root
commit of HEAD) whose `retro#anchor`, under the same class key, this run re-derives under
exactly one other key, and in the checkout that re-derived it: its own commit resolves there,
v1.95.0 would have computed exactly its key there, and the commit descends from the root the new
key names (its own history, not a history the repository merged). It is the same repository, so
it takes the new key and its memory id follows; `add` does the same for its own checkout. It is
never re-keyed when it has provenance, when its project key is held by any checkout read this
run, when two keys could claim it, or when the copy under the new key holds a different memory
id (then it stays carried, and that is named). A monorepo that merged another repository's
history therefore never takes that repository's origin. The reasons are:

- `checkout not read`: the checkout was not discovered, or a problem is owned by it. That
  problem may be an unreadable retro, a refused `git worktree list`, a shallow clone, a broken
  configuration, or a retro that changed while the rebuild ran (an `add` landing mid-run).
- `retro file not read`: the checkout read completely, but that file was not read, for
  example because it lies outside the artifact root or was moved.
- `no checkout read holds it`: the checkout read the file, holds the same project, and the
  entry is no longer there.
- `commit does not resolve`, `retro cites a commit that does not resolve` or
  `lesson refused`: the entry is there but could not be derived. A dangling commit is routine
  after a squash merge and a deleted branch.
- `no provenance`: the origin was written before provenance existed, and no re-derived origin
  proves it is the same repository's.
- `checkout holds another project`: every checkout in its provenance now holds a different
  project key, and the origin's own commit does not resolve there. A path is not an identity.
  The same repository under another key still holds the commit, so it is not a stranger;
  `add` applies the same rule to its own checkout's old-key origin.

The project key is the repository's own: the first-parent root of its default branch
(`origin/HEAD`, then `main`, then `master`). Without any of them it is the main worktree's
HEAD, read in the common directory, so every worktree gets one answer; then
`init.defaultBranch`; then this checkout's HEAD. It is computed once per git common directory. A worktree on a branch that merged an unrelated history, or a
checkout sitting on an orphan `gh-pages` branch, is still its project.

**Counting.** `seen`, `projects` and `status` count re-derived origins and every carried origin
except `checkout holds another project`. Those are kept, with their memory ids, but not counted.
So a temporarily unreadable root never demotes a lesson two projects hold, and a stranger at a
path, or one checkout under a new root commit, never makes a phantom second project. Derived
fields are recomputed from the origins whenever the index is read; they are never trusted from
disk.

**Shallow clones.** A shallow checkout is never a source. It is a problem owned by that
checkout, nothing is derived from it under its unstable key, and its origins are carried as
`checkout not read`. A shallow check that does not answer is refused the same way, and since
it taught nothing, it does not count as something read. `add`, `emit-observatory` and
`record` refuse in a shallow clone, exit 1 and write nothing, and say to deepen it with
`git fetch --unshallow`.

**Known limit.** A project whose root commit changes, through a re-init or an unshallow, starts
new store records: its old origins are carried as `checkout holds another project` with their
memory ids, and the new origins start without one. The operator re-attaches by running
`record` with the old id on the new origin, from the same checkout. That is allowed, because
the new origin is of the same class key and the origin holding the id is carried as `checkout
holds another project` with this checkout in its provenance. From any other checkout it is
refused.

Another checkout of the same project, even one reading the same retro path, decides nothing
for an origin it never held. Problems carry their owner, a checkout or none, and are never
matched by path prefix.

**Memory ids.** A memory id belongs to `(project, classKey)`, the store's own identity, and
never to a retro anchor:

- A rotated or retitled entry keeps its id on the re-derived origin. The old anchor is carried.
- A class key changed inside one entry does not inherit another key's id.
- One id is one `(project, classKey)`. `record` refuses each of the following, exits 1 and
  writes nothing:
  - an id that another class key holds;
  - an id that another project's origin holds (the refusal names that project), unless that
    origin is carried as `checkout holds another project` and this checkout is in its
    provenance (the re-attach above);
  - a revision older than the one held;
  - without `--replace`, a different id over the one the origin already holds.

  It also refuses an id the index cannot hold, such as `mem:`, a quote, a backslash or a
  space: that exits 2.
- One id is one project's store record. Two projects may hold it only while one of them is
  carried as `checkout holds another project`. When a rebuild would leave it on two live
  projects (that checkout came back), the id stays on the earlier holder: the project the
  previous index carried as `checkout holds another project` with it, else the smaller project
  key. The other origin keeps its place without the id, and the run names it. `add` applies the
  same rule against the index as it read it, so an add from an old clone never leaves the id on
  both projects either.
- Merged duplicate lines name every id they drop. Of two copies of one origin the higher
  revision wins; on equal revisions, the lexically smaller id.
- Ids compare on the part before `@`, revisions start at 1, and the highest revision wins.

`emit-observatory` and `record` both use the origin of the project that holds the id. The run
refuses to write if a memory id would vanish other than through `--prune-carried`.

Unreadable sources are named under `not read`, by name rather than by absolute path. Every
root, checkout, repository top, file given and directory is shown by its name — the index files
home-relative, such as `~/.sshlg-skills/lessons/index.jsonl` — in every verb's messages, on stdout
and stderr alike (the session's notes and a refusal too). `path` alone prints the path: that is
its answer. A git question about one commit in one checkout is asked once per run. Only absolute paths are replaced, and only as whole
path components, so a root given as `.` changes no other text. The index is split on `\n` only, and
lesson/1 text refuses every line separator, including U+2028, U+2029 and U+0085. So no value
can make a good index read as corrupt. The run
exits 0 whenever anything was read: a retro, a checkout discovered in full, or a shallow
checkout found. A readable root that holds no checkout also exits 0: the index is written,
and every origin is carried. The run exits 1 only when nothing could be read because every
root was missing or unreadable; then no index, lock directory or migration is touched. A held
lock or an unreadable index is its own refusal. On the default path the one-time merge of a
standalone index runs first, as for every verb.

So does setting a corrupt index aside:
- The file is kept whole as `.corrupt-<date>`.
- Every line that still parses is salvaged into the live index.
- Two lines for one class key are merged.
- A memory id that only a bad line held is named in the output.

Unknown is never measured zero, and never measured gone.
Two projects holding one class key make
one lesson seen twice, status `candidate`. The index path is a parameter — `--index`, then
`$TASK_PIPELINE_LESSONS`, then `~/.sshlg-skills/lessons/index.jsonl` **when
`~/.sshlg-skills` already exists** — the family's machine-state directory, where `lessons/`
is task-pipeline's by the family's own record — sshlg-skills board row B-181 and `docs/working-rules/state-json.md` → *Other members' files under `~/.sshlg-skills/`* (ssheleg/sshlg-skills#209, merged) — and otherwise
`~/.task-pipeline/lessons/index.jsonl`, so a standalone install never creates the family's
directory. When `~/.sshlg-skills` appears later, the first run moves the standalone index
there once and says so. Nothing in this skill writes anywhere else under either.

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
  repository's root commit (the first-parent root of its default branch, so every worktree
  and branch of one repository shares it) — stable across clones and never the repository's name, because
  lessons are read into *other* projects' briefs and a repository name can be a customer's
  or a product's. The shared store receives the same key, never a `project:<slug>` id.

Rules 1, 3, 4 and 5 still bind every text field, on the estate as off it: no path at all,
no code or value, no person's, company's, customer's or product's name, and a title that
states the class rather than the incident. Never, in either layer, a transcript or a URL.
`lessons.py` refuses what a pattern can see (paths, URLs, addresses, credential shapes, long
hex or base64 runs, line breaks) in every text field and in a stage id given as a string (at
most 32 characters, never blank), and any field lesson/1 does not name. A stage id an older
index holds that fails those checks is normalised when the index is read (one line, cut to 32
characters, or `stage`), and said, so the line and its memory id are never set aside; a name it cannot see stays the
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
2. If the session lists the store: `lessons.py emit-observatory <L-id> [--tool …]` prints
   `{tool, arguments}`. **The agent chooses the tool from the tools its session lists** (the
   script cannot see them): `--tool observatory_lesson` where the session lists it — the
   engine's lesson kind, whose arguments are exactly `owner, classKey, title, trigger,
   check, nouns, origin{projectId, commit}` and which the store keeps once per (classKey,
   project) — and otherwise the default, `observatory_record`: a note whose statement starts
   `lesson:`, so lessons accumulate on any engine and a later migration finds them; a lesson
   already recorded that way is emitted with `memoryId` and `expectedRevision`, so the store
   revises it. Both carry the pseudonymous key, never a `project:<slug>` id, and the commit
   as **`commit:` + 12 hex**: the store's redactor removes a 40-hex SHA as a credential shape
   and keeps exactly that short form. `observatory_learn` is not the retro write: it
   contrasts a failure record with its fix inside one project, and a retro entry is neither.
3. The agent calls that tool, then `lessons.py record <L-id> --answer -` keeps the memory id
   beside the local entry. A refusal is one ledger line, `event: lessons — store refused —
   <code>`, and the local entry stays.
4. No store: the ledger says `shared lessons: absent`, once per run.

**Promote.** `lessons.py candidates` lists the lessons two or more projects hold: the
[`learned.md`](learned.md) queue, through `retro.publish` and its redaction list. In the
store, a lesson two projects recorded rises by the store's own corroboration rule, never by
this skill. Stage 10 prints `lessons.py candidates` even when `retro.publish` is unset.
Each candidate has a durable owning-project follow-up to assess promotion, keyed by its
lesson id; reuse an existing open row rather than minting duplicates. A candidate count
does not authorize publishing private origins or changing shared doctrine without review.

**When there is no store, the source ledger says so**, and the first layer runs exactly as
before. The store is never a hard dependency; neither is python3 — without it the ledger
prints `local lessons: unavailable (no python3)` and the retro is read as before.

## What the operator sees, and when

A release iteration has three planned touchpoints, plus every human gate:
1. **The planning gate** — the inventory summary, the canvas, the wave plan and the
   question batch, in one message ([`waves.md`](waves.md) → *How the stages map*).
2. **A question round** — only when one of its three triggers fires.
3. **The release hand-back**, with the next pool.

Sign-ins, consents, operator payments and typed secrets remain human
([`waves.md`](waves.md) → *What stays human*). Record the action the person must
take and continue independent work.

Other outward or irreversible acts, including sending to people, require explicit
authority. A specific standing authorization naming the act counts only within its
source and scope ([`continuity.md`](continuity.md) → *The limit, before the capability*):
a recorded "releases are the agent's" decision covers the tag and the publish its
release run performs, not unrelated deployments, messages or human-only actions.

## Rationalizations

| Excuse | Reality |
|---|---|
| "This bug is tiny, fix it now" | Tiny fixes are what move a seam twice. It joins the inventory, or it is one of the hotfix lane's five entries |
| "Wait for the whole wave, then verify" | A barrier idles every finished node. Each node is certified when it lands |
| "R3 found nothing in round 2, skip the adversarial round" | The adversarial round, in any position, asks a different question: it hunts for a planted defect. A clean blind round does not answer it |
| "Ask the operator now, it is quick" | Each question is a human round. Queue it and take another node |
| "The agent hit a rate limit, start it again" | Resume it with its context. Relaunching pays for the same reading twice |
| "No Observatory here, so no learning loop" | The project retro and learned.md are the loop's first layer, and every install has them |
| "Release first, check later" | An unchecked release is the item the next release iteration rediscovers. Step 11 is inside the run |
