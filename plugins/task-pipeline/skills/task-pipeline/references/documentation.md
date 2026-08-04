# Documentation — the system, not the by-product

**One job: make documentation a deliverable with an address, an obligation and a
gate.** Not "write docs at the end" — a *system*: every settled thing has an id,
every fact has one home, every kind of change names the documents it owes, and a
script can say no.

This file is the **what and why**. [`gates.md`](gates.md) is how the script that
enforces it gets written; [`stages.md`](stages.md) says where each piece binds.

**Governance is a by-product here, never a separate step.** The run already
produces decisions — the brief's *Decisions locked*, the spec's locked contracts,
the ADRs the grill writes. Recording one is **transcription plus a stable id**, not
new thinking. Anything below that feels like ceremony is a sign the register is
being written twice; write it once, here.

---

## Contents

- The inventory — four questions, answered before the first line of work
- Registers and ids
- Single source of truth
- The Doc Loop
- Changing your mind
- The propagation matrix
- Navigation
- Intent and as-built
- Registers are shared state
- Where this binds in the pipeline
- Rationalizations

## The inventory — four questions, answered before the first line of work

Stage 0 answers these before the interview, and writes the answers to
`docs/DOCMAP.md` (seeded from [`../templates/docmap.md`](../templates/docmap.md),
**only when absent** — never overwritten):

1. **Where do settled things live?** The decision home, and its id scheme.
2. **What is each fact's single home?** One place per fact; everything else links.
3. **What does a change of type X oblige?** The propagation matrix.
4. **What proves it?** The gate command, and what it does *not* cover.

A project with no answers gets them seeded. The seeding is itself recorded as the
first entry in the register, which is the cheapest possible demonstration that the
register works.

**There is no "we don't document" answer.** The four questions have answers in every
repository — the smallest one still decides *somewhere* that a thing is true — and
the only choice is whether that answer is written down or re-derived by each new
reader. What scales down is **volume**, never the rules: a register with three
entries is a register, and the seeded gate is green on exactly those three
([`gates.md`](gates.md) → *Progressive arming*).

---

## Registers and ids

**One decision home per project. The doc map names it. Never create a second.**

Two shapes satisfy the contract; the difference is physical, not semantic:

| Shape | Home | Id | Use when |
|---|---|---|---|
| **Register** | `docs/DECISIONS.md`, append-only | `DEC-####` | default; many small decisions, read as a list |
| **ADR set** | `docs/adr/NNNN-<slug>.md` | `ADR-NNNN` | the project already has `docs/adr/`; decisions are long and each wants a page |

**Detect, don't assume:** `docs/adr/` holds at least one `NNNN-*.md` → that is the
register, record it in the doc map and use it. Otherwise seed
[`../templates/decisions.md`](../templates/decisions.md). An existing ADR set is
**never migrated** as a side effect of some other task — migrating is its own
decision, with its own entry.

Both shapes owe the same six things: a **stable id**, an **append-only** history, a
**status line** with the supersede semantics below, a **`Consequences / affects:`**
line, a **`Source:`** line carrying the run and the **commit**, and the **edge
markers**.

Open questions get their own register (`docs/OPEN_QUESTIONS.md`, `OQ-####`) with a
closed status vocabulary: `Open` · `Resolved→DEC-####` · `Dropped (<why>)`.

**Two rules that look like formatting and are not:**

- **Reference facts by id, never by copying the text.** A copy is a second source
  that nobody will update, and the reader cannot tell which one is current.
- **Ids are never renumbered and resolved questions are never deleted.** The
  question is the history of the answer; without it the next reader re-litigates a
  settled thing from scratch.

---

## Single source of truth

**Every fact has exactly one home. Everything else links to it.**

If the same fact is stated in two places, that is a **bug** — collapse it to one
home and link from the other. Not because duplication is untidy: because the two
copies will disagree, and at that moment both become unusable, since nobody can
tell which one moved.

- The *decision* lives in the register. Topic docs describe the *current design*
  and cite the id.
- Each topic (architecture, data model, security, …) has one canonical document.
- Indexes and summaries **link**; they never restate a rule.

### Across repositories

**The owning repository decides; a consumer repository describes.** Where a
consumer document disagrees with the owner, the consumer is wrong — stated rather
than adjudicated case by case, because case-by-case is how a consumer repo starts
legislating.

The boundary is worth writing out, because an unqualified "the owner always wins"
is false in one direction: **build state and task status belong to the repository
doing the work**. A submodule is cloned alone, and a status update must not require
two repositories.

Changing a consumer repo's documentation: compare against the owner's canonical
doc → look for a contradiction with it *and* with any accepted decision → if the
consumer document is wrong, fix it in place; if the **owner** is wrong or stale, it
is corrected there, by a decision entry, through a pull request — and the consumer
document stays divergent and marked until that lands. Quietly aligning a consumer
doc to its own view is the failure this paragraph exists to prevent.

---

## The Doc Loop

**Fires whenever something is settled — at any stage.** Scope, a contract, a name,
a policy, a status vocabulary, a price, a retention window. Not only at stage 9.

1. **Orient and reconcile.** Read the register and the topic doc. Run the
   intent/as-built reconcile (below). Do not contradict an accepted decision
   without superseding it. *Skipping this is how a run spends a day building
   against a system that does not exist.*
2. **Reserve the id, then record.** Reading "Next free ID" is **not** reserving it
   (see *Registers are shared state*). Then write the entry: date, status, context,
   decision, consequences, source with the commit.
3. **Resolve.** Flip every answered question to `Resolved→<id>`. Never delete it.
4. **Propagate.** Walk the matrix row for this change type and update every
   document it names, **in the same change**. Keep SSOT: the detail in one home,
   links from the rest.
5. **Adjust scope.** Roadmap, MVP, module map — if scope moved.
6. **Record as-built.** What was actually built, with the ids and the files. Then
   reconcile again.
7. **Commit.** One focused commit, conventional message, **the ids in the subject**.

**Finishing the chat answer is not finishing the task.** Closing the loop is. A
decision that lives only in a spec dies with that spec; one that lives only in the
conversation was never made.

---

## Changing your mind

The register is **append-only**. To reverse or replace:

- add a **new** entry stating the new decision and naming what it replaces;
- edit **only the status line** of the old entry;
- leave the old body intact as history.

**A partial supersede annotates both sides.** Most reversals are partial — a later
decision replaces one clause and leaves the rest standing. If the old entry keeps a
bare `Accepted`, a reader who opens only that entry gets an answer that is no longer
true. So the new entry names which clause it replaces, and the old entry's status
line gains `· **Partially superseded by <id>** — <one line>`.

**Three markers, and they mean different things:**

| Marker | Meaning | Target's status line annotated? |
|---|---|---|
| `Refines:` | **additive only** — every clause of the target still holds | no |
| `Contradicts:` | a **named clause** of the target no longer holds | **yes** |
| `Supersedes:` | the whole target is retired | **yes** |

One word for "adds to" and "replaces a clause of" is unenforceable. Measured on the
project this practice comes from: across **275** refine/supersede edges, **204**
pointed at a target with no annotation — which is not 204 violations, because most
were additive. *That ambiguity is the defect*: neither a reader nor a script could
tell which of the 204 should have been annotated, so the rule could not be gated at
all.

**Existing edges are not retro-classified.** Each needs a judgement about what its
author meant, and a bulk pass would guess. An edge is reclassified when someone
touches it for another reason.

---

## The propagation matrix

The harvest ledger ([`knowledge-sources.md`](knowledge-sources.md)) names the
documents you **read**. The matrix names the documents you **owe**. They are not
the same list, and the gap between them is where documentation rots: the document
nobody read is exactly the document nobody updated.

**Build it in five steps** (stage 0; extend it whenever a new doc class appears):

0. **Write the meta-row first: *a new document or rule*.** The most frequent change
   in any documented project is adding a document, and it is the row nobody writes —
   so the matrix ends up unable to catch the class it will meet most often. Its
   *Update these* column is every surface that must **learn the thing exists**: the
   index a reader opens, the map, any manifest, the agent-facing rules file.
   Measured on the project this practice comes from: **nine findings across five
   audits were that one missing row**, and the checks were green throughout, because
   a check can only walk the list it was given.
1. List the project's doc classes — one line each: what is this the home of?
2. For each **change type** the project can undergo, name every document that must
   move.
3. For each row, name the **check** that would notice if it did not — or write
   `review` *with a one-line reason why no check can decide it*.
4. Write the rows into `docs/DOCMAP.md` → *Propagation matrix*.
5. Arm the mechanical half in the gate: **a document named in an entry's
   `Consequences / affects:` line must cite that entry.**

A row with an empty third column is a **finding**, not a blank. Either a check
exists, or somebody has said out loud that none can.

**The backlog is ratcheted, and that is the design.** Turning this check on in an
existing repository finds a lot: **162** missing propagations across **73**
decisions, on the project this comes from — not the four the audit had reported.
Failing on all of them makes the gate something people switch off, and bulk-fixing
them blind adds 162 citations nobody verified. So: entries from a **floor** id
onward fail; everything older is a counted backlog that may only shrink, printed on
every run. Raising the floor is a decision, and it belongs in the register.

---

## Navigation

**One definition per entity, and a mention links to the definition.**

- Every definition carries an explicit anchor.
- A mention links to the **anchor**, not the file. A file link makes the reader
  search; a deep link that rots is caught by the gate.
- **Indexes never restate a rule.** They fall behind and then they lie with
  authority — a navigation aid that omits an entry is worse than none, because a
  reader concludes the entry does not exist.

A deep link is worth more than a file link *and* fails harder, so it only pays with
a check behind it. Land the anchor check with the first rewritten link, not after
the sweep.

---

## Intent and as-built

Two records, deliberately not merged:

| Record | Says | Written by |
|---|---|---|
| **Intent** — the registers, the spec, the plan | how it *should* be | the Doc Loop |
| **As-built** — the run record | how it *turned out* | step 6, at the end |

**Reconcile both before starting and after finishing.** Every divergence has one of
three resolutions: the document is stale, the record is wrong, or they genuinely
disagree and that is a decision to make. There is no fourth, and "I'll keep it in
mind" is not one of them.

Where a coordination tool is installed it does this for you. Where it is not, the
as-built record is a section of the carry-over ledger and the reconcile is a read
of it — **the tool is optional, the discipline is not**.

---

## Registers are shared state

A register is the one file two agents will write in the same minute.

- **Reserve the id before minting it.** "Next free ID" is a *reading*; a second
  agent reading it in the same minute gets the same answer, and now two entries
  carry one number.
- **Take a lease before writing a guarded register**, where a lease mechanism
  exists. [`hooks.md`](hooks.md) is how such a guard blocks the edit;
  [`companion-skills.md`](companion-skills.md) names the optional companion that
  implements one.
- **Ask what two instances with the same identity would do**, and make the tool
  answer it. This is [`learned.md`](learned.md) rule 15, and it is in that table
  because it cost an entire day of work performed under another session's identity.
- **When nothing can arbitrate, the run is `ungated` — say so out loud.** That is
  a real state, not a formality. Describing a project as protected while nothing
  enforces it is worse than having no protection, because everyone downstream
  believes the guarantee.

---

## Where this binds in the pipeline

| Point | What happens | Gate |
|---|---|---|
| **Stage 0**, phase 1b | the inventory — the four questions, into `docs/DOCMAP.md`; the regime recorded | manual |
| **Stage 0**, phase 1c | intent vs as-built reconciled; every divergence resolved | manual |
| **Any stage** | something is settled → the Doc Loop, all seven steps | the stage's own |
| **Stage 9** | the propagation sweep, the registers, the gate green with its ratchets printed | auto |
| **Stage 10** | the gate itself proven — every check seen failing once against a planted defect | manual |

---

## Rationalizations

| Excuse | Reality |
|---|---|
| "It's a small project, a register is overkill" | A register with three entries costs three minutes and is the only reason the fourth decision can be found. What people mean by overhead is *ceremony*, and none is required here — the entries are transcribed from artefacts the run already produced. |
| "I'll write the decision up at the end" | At the end you remember the outcome and not the alternatives you rejected, which is the only part with any value later. |
| "The spec already says it" | A spec is per-run and the next one supersedes it. A decision outlives every artefact that mentions it. |
| "I updated the docs I touched" | The matrix names the documents you did **not** touch. That is the entire reason it exists. |
| "Two docs saying the same thing is harmless" | Until they disagree — and then both are unusable, because nobody can tell which one moved. |
| "I'll just fix the old decision's text" | Then the reason someone chose it is gone and the next person re-litigates it from scratch. Supersede; never edit the body. |
| "It's obviously additive, no need to mark it" | 204 of 275 edges were left unmarked on exactly that reasoning, and afterwards nobody could tell which of them should have been. The marker costs one word. |
| "Nobody else is working in this repo right now" | You cannot know that from inside your session, and being wrong means two entries with one id. |
| "The gate is green, so the docs are fine" | The gate proves what it checks. Read its scope header before quoting it as evidence. |
| "The doc is stale but that's not this task" | Then it is a row in the carry-over ledger with the exact edit, right now. A staleness noticed and unrecorded is the next run's false premise. |
