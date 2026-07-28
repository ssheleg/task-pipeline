# Knowledge sources — harvest before the grill, update after the build

Stage 0 has two phases. This file is **phase 1**: before the first question is
asked, find and read what the project already knows about this task. The interview
([`grill.md`](grill.md)) is phase 2, and it runs *against* what was harvested here.

The same source list closes the loop at **stage 9**: what was read at the start is
what gets updated at the end. A source good enough to answer a question is a source
that goes stale when the answer changes.

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
| 2 | **Host agent docs** | `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/` | conventions, commands, deploy path, house rules |
| 3 | **Domain docs** | `CONTEXT.md` / `CONTEXT-MAP.md`, `docs/adr/` | the glossary and the decisions with their reasons |
| 4 | **Product/UX docs** | `docs/ux/` (super-ux chain), `README`, runbooks | user-facing behavior that is already specified |
| 5 | **Pipeline history** | `docs/superpowers/specs/`, `plans/`, past `-carryover.md` | what a previous run of this pipeline decided or deferred |
| 6 | **The knowledge wiki** | see below | distilled cross-project knowledge, prior sessions, why decisions were made |
| 7 | **Other doc repos the project names** | a docs repo URL or submodule in `CLAUDE.md`/`README`, a sibling checkout, a `docs/` monorepo package | specs, contracts and runbooks that live outside this repo |
| 8 | **Hosted doc systems the project names** | Notion / Confluence / Google Docs referenced in the project | the same, when the team keeps them there |

Rules for the list:

- **Never invent a source.** A doc repo is in scope because the project names it,
  not because it plausibly exists. Nothing is cloned or fetched on a guess.
- **Sources 7–8 are read-only at this stage**, and reading a hosted system needs a
  connected tool — if there's no tool, record the gap and ask the operator to paste
  what matters rather than pretending the source was covered.
- **The wiki is optional; the harvest is not.** With no wiki and no doc repos, the
  harvest is sources 1–5 and takes two minutes. Skipping it is never the answer.

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

**Precedence when two sources disagree with each other:** code > host docs and ADRs
> the wiki > anyone's memory. The wiki is *distilled* knowledge and can lag the
repo by months; the code is what runs. A disagreement between them is a grill
question, never a silent pick — and it is usually a sign the doc is due an update.

## Close the loop — stage 9 updates what stage 0 read

The ledger is the stage-9 work list. For each row:

- **Host repo docs, ADRs, runbooks, `docs/ux/`** — updated in the **same change**,
  per the host's own rules ([`conventions.md`](conventions.md)).
- **Anything the run proved stale** — including a doc that was "wrong but nobody
  had time": that's why the conflict was logged in phase 2 instead of only being
  resolved verbally.
- **The wiki** — `wiki-update` syncs what this run learned. Distil the *knowledge*
  (decisions, seams, gotchas, why), never a diff summary.
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
