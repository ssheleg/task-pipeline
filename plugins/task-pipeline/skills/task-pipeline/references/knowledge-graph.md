# The code graph — an index of reach, refreshed with the docs

A grep finds a **name**. A graph finds **reach**: what actually calls this, what
breaks if it moves, which module every change passes through. That is the question
stage 0 needs answered before it asks the operator anything, and it is the question
no document answers reliably — documents describe the reach the author remembered.

The graph this pipeline is built to work with is
**[graphify](https://github.com/Graphify-Labs/graphify)** — it turns a folder of
code and docs into a persistent knowledge graph (`graphify-out/graph.json`, an HTML
view and a plain-language `GRAPH_REPORT.md`), with community detection and
query / path / explain / affected traversals.

It is **recommended, never required**. No stage blocks on a missing graph; the
harvest simply runs on the sources it has
([`knowledge-sources.md`](knowledge-sources.md)).

## Detect it, and install it once

Detect, in this order:

- `graphify-out/graph.json` exists → the graph is **built**; use it.
- `command -v graphify` resolves but there is no `graphify-out/` → the tool is
  installed, the graph is not built. Offer to build it (one command, below).
- Neither → recommend it **once**, in the preflight block
  ([`companion-skills.md`](companion-skills.md)), with the lines:

  ```bash
  uv tool install graphifyy      # the CLI
  graphify install               # add the /graphify skill to this agent
  ```

  then, in the project root:

  ```
  /graphify .
  ```

  Then continue. Never ask twice in a run, and never hold a gate on it.

`graphify-out/` is **derived**, so it is git-ignored by default — add it to the
host's `.gitignore` in the same change that builds it. A team that wants the graph
shared commits it instead and installs graphify's own git merge driver; that is the
project's call, recorded in its `CLAUDE.md`, not this pipeline's default.

## Stage 0 — query the graph before you ask the person

The graph is a **source in the ledger**, read like any other, and it is the fastest
one: it answers structural questions in a single call that would otherwise be a
dozen greps.

| Ask | Command |
|---|---|
| How does this work / where does this live? | `graphify query "how does session reach the API layer"` |
| What is this thing? | `graphify explain "AuthModule"` |
| What breaks if I change it? | `graphify affected "AuthModule"` |
| How do these two connect? | `graphify path "AuthModule" "Database"` |
| What is architecturally central? | `graphify god-nodes` |

**What you get depends on what the repo is made of.** Code is extracted
structurally, so `affected` and `path` are sharp on a code repo and return nothing
useful on one that is mostly prose — there, the nodes are documents and headings,
and the *divergence check* below is the half that pays. Say which one you are
looking at rather than reporting an empty traversal as an absence of coupling.

Two rules keep it honest:

- **The graph points, the code decides.** It is an index built at a moment in time;
  a graph from two weeks ago is exactly as stale as a doc from two weeks ago. It
  belongs in the retrieval order right after the code, and never as the tiebreaker.
  Precedence, reflowed so it reads in one direction: code first, then host docs and
  ADRs, then the graph, then the wiki, then anyone's memory.
- **Record it in the ledger with its build date** — source
  `graphify-out/graph.json`, what it said about this task, how fresh, and therefore
  whether stage 9 owes it a refresh. A source consulted but not recorded is a source
  nobody will update.

## Stage 9 — the close-out has three artifacts, not two

The run is not written up until all three describe the same system:

1. **The docs** — host module docs and runbooks, in the same change.
2. **The wiki** — `wiki-update`, the distilled *why*.
3. **The graph** — re-extracted from what this run just changed. **Two forms, and
   the difference is the whole point of doing it at stage 9:**

   ```
   /graphify . --update      # in the agent: code AND docs, incremental — use this
   ```

   ```bash
   graphify update .         # CLI shortcut: code ONLY, structural, no model, no key
   ```

   Stage 9 is the stage that *changed the docs*, so the CLI shortcut is the wrong
   default here: it re-extracts code and leaves every edited document at its old
   text, which produces the most expensive kind of stale graph — one that was
   refreshed. The CLI's own last line says as much (*"for doc/paper/image changes
   run `/graphify --update` in your AI assistant"*). Use the CLI form only when the
   change was code-only.

   Incremental either way: only new and changed files are re-extracted. On a run
   that deleted code the rebuild legitimately has fewer nodes, and refuses to
   overwrite until you say so — that is what `--force` is for.

**Why it is a peer of the docs and not an afterthought:** the next run's stage-0
harvest queries this graph *first*, and a stale graph is a false premise delivered
with the authority of a machine. A wrong doc gets argued with. A wrong graph gets
believed.

Gate wording (stage 9, `auto`): where a graph exists, it is refreshed in this
change, or the reason it wasn't is written in the carry-over ledger.

## The divergence check — the graph against the docs

Refreshing the graph is bookkeeping. The **check** is the payoff: two independent
statements of the same system, so where they disagree, one of them is wrong and
nobody had a way to notice. Run it as a pass, not as a linter — every close-out for
the cheap half, the full sweep whenever the audit rotates onto this axis
([`audit.md`](audit.md) → *Every pass changes the axis*).

| Ask the graph | Command | A disagreement means |
|---|---|---|
| What are the hubs? | `graphify god-nodes` | a hub **no doc names** is an undocumented seam — the thing every change passes through and nothing explains |
| What reaches what? | `graphify path "A" "B"` | an edge the docs **deny** ("these layers don't touch") is either a leak in the code or a lie in the docs — both are findings, and which one is a decision, not a guess |
| What does this change touch? | `graphify affected "X"` | callers the docs never mention → the documented blast radius is smaller than the real one |
| What is weakly connected? | `GRAPH_REPORT.md` communities + low-degree nodes | code that nothing — no doc, no test, no caller — reaches |

And the reverse direction, which is the one that catches rot: **a doc that names a
module, file or command the graph has no node for** describes something that no
longer exists. That is a stale row in the stage-0 ledger, found mechanically instead
of by remembering.

Where the findings go:

- **At stage 9** — a doc that is wrong about reach is fixed in this change, like
  any other stale ledger row.
- **At stage 10** — a seam nobody documented is an *absence*, and absences are what
  the ladder walk exists to convert into REQ rows with their checks
  ([`audit.md`](audit.md), [`acceptance.md`](acceptance.md)). It goes in **before**
  the coverage table, never after.
- **Never "fixed" in the graph.** The graph is derived. You fix the doc or you fix
  the code, then re-run the extraction and the disagreement disappears on its own.
  A hand-edited graph is a third statement, and now nothing is authoritative.

**Cadence.** The refresh is every stage-9 close-out. The full sweep is periodic —
stage 10, or whenever a pass on another axis stops finding anything new. Running the
sweep on every commit turns an audit axis into noise and it stops being read.

## Rationalizations

| Excuse | Reality |
|---|---|
| "I'll just grep, it's faster" | Grep answers "where is this name". The questions that stop a run are "what reaches this" and "what breaks if it moves" — that is one query against a graph and an afternoon with grep. |
| "The graph is probably stale" | Then it has a build date and you can say so. Stale-and-dated is a finding; stale-and-unknown is what you get by not building one. |
| "Docs and wiki are updated, we're done" | The graph is the source the *next* harvest reads first. Leaving it behind is leaving a false premise where a machine will quote it back. |
| "The divergence check found nothing, skip it next time" | It found nothing **on this axis, this pass**. Rotate the axis; that is the rule this check belongs to, not an exemption from it. |
| "A hub with no doc is fine, everyone knows it" | Everyone currently on the team. The graph found it in one command; the person who joins next month will find it in a postmortem. |
| "Building the graph costs an LLM run" | Code is extracted structurally, with no model and no API key. The cost you are avoiding is a rebuild you already paid for. |
