# Intake split: one prompt, several asks

Stage 0, phase 1a. Read when the request carries more than one ask: a long message, a
dictated list, several features named in one go. Every run reads §1, which finds the
board; a single ask skips §2 to §5.

The operator's rule (2026-11-06): a big request is cut into modules first; each module is
researched separately and in parallel; the findings merge into one plan, which is run
through once more; the highest-priority item goes first and every other item lands on the
project's backlog, found and kept the way that project keeps it. A simple single task gets
none of this. Until 1.103.0 a run read every prompt as one task: `grill.md` expands "a
one-line request" into one brief, and the module cut (`decomposition.md`) waited until
stage 2 and fired only for a platform build (task-pipeline board row B-097).

## Contents

- 1. Find the board first
- 2. List the asks
- 3. The threshold: fan out or not
- 4. Modules, parallel research, one merged plan, a second pass
- 5. Rank, run the top, file the rest

## 1. Find the board first

Before anything is filed, find where the project already keeps its open work, every run:

```
python3 scripts/backlog_sources.py --root . --discover --artifacts <artifacts>
```

It prints `home`, the other `candidates`, the `trackers` the instruction files name
(with `negated` for a rule such as "not Linear"), the `agentSync` registers (a `remote`
backend means the local file is a mirror), the paths a filing rule `negated` and `weak` signals (plan folders, handoff pages:
input, never the board). Exit 4 means nothing at all: seed the printed `seed` path from
`templates/backlog.md`; it is left for a tree with none of `CLAUDE.md`, `AGENTS.md`, `.claude/CLAUDE.md`,
`.github/copilot-instructions.md` or a README (a symlink of any kind counts) and nothing else. Exit 5 means no home but `signals` (a frozen or negated board, a
tracked file named as a board elsewhere in the tree, an instruction line about where work lives
that names no file here, such as a sibling data folder or another repository, a file its own clause calls the place of
work, a tracker named in any words, a directory or agent-sync config that could not be read,
and always
the project's instruction files themselves):
read them before seeding. A `seed-path-taken` signal is the seed path itself, already occupied
(a link, a frozen copy, another letter case): read it, never write over it; if it names no live
board, say so in the brief and ask once where to seed. The listed lines rank what to read first; the rule that a project
which wrote instructions is read before a board is seeded is what prevents the duplicate,
because no vocabulary is complete. Exit 5 is conservative by design: a false signal costs one line read, a
false exit 4 starts a second board; one that names
the live board is the home, and only when none does is `<artifacts>/backlog.md` seeded, the
signals quoted in the brief. Exit 0 means **use the home and seed nothing**: a second board beside `docs/backlog.md` is the duplicate this step exists
to prevent. A home with `via: tracker` (Linear, Jira, GitHub issues, the Fabric board, named
on a line about where work is tracked) is where an item is filed, through that tracker's
tool; a file beside it is a funnel or mirror with the tracker id in its `Home` column. Then
read the lines the output cites: the script finds, the rule on that line decides.
`ambiguous: true` is a finding to put to the operator once, with a draft
`docs/backlog-sources.json`. Record the home and the command that reads it in the brief's
`0 Work-list` row ([`grill.md`](grill.md)).

## 2. List the asks

Write each independent ask as `ASK-n` with the operator's phrase quoted beside it. Two asks
are one when neither can ship without the other. Context, motivation and examples are not
asks. Then run the short-path triage (`scripts/short_path.py`, five answers) **per ask**.

## 3. The threshold: fan out or not

| What the list holds | What happens |
|---|---|
| one ask, whatever its size | no split: the normal stage 0; a platform is cut at stage 2 ([`decomposition.md`](decomposition.md)) |
| several asks, every one *small* | no research fan-out: rank them (§5), run the top one, file the rest |
| several asks, any one not small | §4 |

[`prioritisation.md`](prioritisation.md) → *Research before scoring, not after* says it:
*"Do not fan out to score two rows. The dispatch costs more than reading them."* So the
fan-out never runs below this line. Phase 1d then runs on the kept item only, reusing its
triage line.

## 4. Modules, parallel research, one merged plan, a second pass

1. **Cut modules** by capability, not by file or layer, with the brick criteria of
   `decomposition.md`. An ask may become several modules; several asks may share one.
2. **One read-only researcher per module, dispatched together** (one message, many agent
   calls). Each gets its module and nothing else, writes nothing, and returns the dossier
   shape of [`../templates/dossier.md`](../templates/dossier.md) plus the four fields of
   `prioritisation.md` §4: what it touches (`file:line`), what it depends on and what depends
   on it, what is already measured, what would make it wrong. **At most six at once**: a
   wave of subagents ran out of the weekly quota mid-release on 2026-10-28 (hub retro); more
   modules queue behind the first six. No subagent tool: research them in turn and say so.
3. **Merge** with [`iteration.md`](iteration.md) → *Integration, until it converges*: lay the
   dossiers side by side; a pair that changes one seam, contract or file is redesigned
   together; repeat until a pass changes nothing, three passes at most; what still conflicts
   becomes one question in the stage-0 batch.
4. **The second pass** is a fresh reader over the merged plan alone (no dossiers): duplicated
   work, an order that breaks a dependency, a seam no module owns, an ask the plan no longer
   serves. Its findings are fixed in the merged plan, never appended beside it.

Each dossier is saved under `<artifacts>/specs/<date>-<topic>-dossiers/` so a filed item
keeps its research and the next run does not repeat it.

## 5. Rank, run the top, file the rest

An order the operator states is kept as stated (*"first X, then Y"*). The impact ladder
(`prioritisation.md` §1 to §3) orders only what they left unordered, and drops nothing: they
named every item. Asks that cannot ship apart were merged into one item in §2. The top item
becomes this run's brief and the stages continue with it. **Every other item gets a row on the home board before stage 1**: its id, the quoted
phrase, the dossier link, the rank and why. A board a lease guards is written under the
lease. Print the split once:

```
split: 4 asks → 6 modules · researched 6 in parallel · merged in 2 passes · second pass 1 fix
now: ASK-2 (rung 2, checkout errors) · filed: B-41 ASK-1, B-42 ASK-3, B-43 ASK-4 → docs/backlog.md
```

**Waves instead.** When the operator asks for all of it now ("all of it", «всё сразу», «до
конца»), or §4's merge found items that share a seam no cut separates, the inventory is
already built: hand it to `/task-pipeline waves` ([`waves.md`](waves.md)) instead of running
one item and filing the rest. Otherwise the single run, with the rest on the board.
