# Design — the documentation track, the gate doctrine, and the learning loop

**Status:** approved design, not yet implemented. Plan:
[`../plans/2026-08-03-documentation-track.md`](../plans/2026-08-03-documentation-track.md).
**Target release:** `v1.7.0`.

**One job.** Port a proven, four-repository documentation practice into
`task-pipeline` so that *any* agent, on *any* project, runs it identically: what to
read before work, what a decision obliges, what to update after, what proves it,
and how the proof itself is built, probed and kept honest. Plus the self-learning
loop — a retrospective that is read before the work, pruned after it, evidential,
and traceable to the commit where each lesson was earned.

---

## 1. Where this comes from, and what is already here

The practice being ported was built on a 260-decision, 72-document specification
across four git repositories with several agents editing at once. Two pieces of it
already reached this skill and are **not** in scope here:

| Already ported | Lives in |
|---|---|
| The fourteen mechanical rules (axis rotation, absence, probes, ratchets, compute-never-restate) | [`references/learned.md`](../../../plugins/task-pipeline/skills/task-pipeline/references/learned.md) |
| The audit ladder, the seams, the exhaustion crossover | [`references/audit.md`](../../../plugins/task-pipeline/skills/task-pipeline/references/audit.md) |

What did **not** port is the part that produced them: documentation as a governed
system with registers, identifiers, a single home per fact, an obligation matrix,
supersede semantics, and a gate the project owns. The pipeline currently says
*"docs in sync with code"* at stage 9 and names no artefact that could make that
sentence false.

### 1.1 The gap, stated precisely

| # | Missing capability | Today's behaviour | Consequence |
|---|---|---|---|
| G1 | A **register** of decisions with stable ids | ADRs written "lazily" at stage 0 only ([`grill.md`](../../../plugins/task-pipeline/skills/task-pipeline/references/grill.md)) | A decision settled at stage 2, 3 or 5 lives in the spec and evaporates |
| G2 | **SSOT** — one home per fact | unstated | The same fact is restated in three docs and drifts |
| G3 | A **propagation obligation** | stage 9 updates the *harvest ledger* — the docs that were **read** | A doc nobody read and must still change is never touched |
| G4 | **Supersede semantics** | unstated | A reversed decision keeps a live status and a reader gets an answer that is no longer true |
| G5 | The **Doc Loop** as a cross-cutting protocol | stage 9 only | Decisions made mid-run reach no register |
| G6 | **Intent vs as-built** reconcile before work | unstated | The run builds against a system that does not exist |
| G7 | **How to build a gate** | [`audit.md`](../../../plugins/task-pipeline/skills/task-pipeline/references/audit.md) says a class seen twice "belongs in a script" and stops there | Every agent invents a different script, or none |
| G8 | **Hooks** | unmentioned | Agent-time enforcement is unavailable and its portability limit is unstated |
| G9 | Registers are **shared state** | unmentioned | Two agents mint the same id |
| G10 | Retro **traceability** and unbounded log | `file:line` evidence; the Log grows without limit inside a file stage 0 reads "in full" | Evidence rots with the next edit; the file stops being read |

### 1.2 Decisions taken with the operator (2026-08-03)

| # | Question | Decision |
|---|---|---|
| D1 | Doc regime for a small project | **Always governed.** Every project gets registers, a doc map, a propagation matrix and a gate. Governed scales by **volume**, never by dropping rules: a register with three decisions is a register |
| D2 | How the gate travels | **A portable skeleton script plus doctrine.** `templates/docgate.sh` is seeded into the host project and extended there |
| D3 | Retro storage | **In-force file plus archive folder.** `retro.md` stays readable in full; `docs/superpowers/retro/` holds the full history, queried by term |
| D4 | Hooks | **Doctrine plus one worked example.** Lease guards stay with `agent-sync` (optional companion) — never reimplemented here |

#### D1's risk, and the design that answers it

A full register on a three-file repository reads as overhead, and an overhead
nobody believes in gets bypassed. **Tiers were the obvious answer and they are the
wrong one** — a tier is a switch, and the switch gets set to "minimal" by whoever
is in a hurry, which is the same bypass with paperwork.

The better answer is to remove the *separate step*, not to weaken the rule:
**governance is a by-product of artefacts the run already produces.** Three
mechanisms, all binding:

1. **The register is fed, not authored.** The brief already carries
   `## Decisions locked (the grill's output)`; the spec already locks contracts;
   the grill already writes ADRs for hard-to-reverse calls. The Doc Loop's *record*
   step is therefore **transcription plus a stable id**, not new thinking. Nothing
   is decided twice, so nothing feels like ceremony.
2. **The gate arms progressively.** A section whose input artefact does not exist
   yet prints `dormant: <name> — no <artefact> yet` and does **not** fail. Dormant
   is *visible* (so it is not forgotten) and *green* (so day one is not red), and
   the section arms by itself the moment the artefact appears. This is the ratchet
   run backwards, and it is what makes "always governed" survivable at three files.
3. **The propagation matrix is derived, not invented.** Stage 0 already lists the
   project's doc classes for the harvest; the matrix rows are generated from that
   list with `Checked by` defaulting to `review` until a check exists. Authoring
   cost is near zero, and the row exists — so the obligation exists.

Two supporting rules: the seeded gate **must exit zero on the seeds it ships with**
(learned rule 9, and this is the one guard in the repo that executes), and the gate
**prints the register size** on every run (`3 decisions · 0 open questions`) so an
empty register reads as *checked and empty* rather than *never set up*.

---

## 2. Shape of the change

Nothing about the ten stages, their order, their ids or their gate **types**
changes. This is a **track** — like the UX track — that binds at three points, plus
two new cross-cutting doctrines.

```
stage 0  ── phase 1b: DOC INVENTORY ─────► docs/DOCMAP.md   (registers, SSOT, matrix, gate)
         ── phase 1c: RECONCILE  ────────► intent vs as-built, divergences resolved
         ── the retro: in force read in full + archive QUERIED by the task's nouns

any stage ─ a decision is settled ───────► THE DOC LOOP (cross-cutting, new)

stage 9  ── the propagation sweep ───────► every doc the matrix names, not only those read
         ── registers updated, gate run, ratchets printed

stage 10 ── doc-gate evidence ───────────► every check probed once against a planted defect
         ── the retro: prune (with commits) → stamp → entry → archive rotation
```

### 2.1 New files

| Path | Kind | Size target | Purpose |
|---|---|---|---|
| `references/documentation.md` | doctrine | 260–320 lines | Registers, SSOT, the Doc Loop, supersede semantics, the propagation matrix, navigation, intent-vs-as-built, shared-state rules |
| `references/gates.md` | doctrine | 240–300 lines | The two axes, the promotion ladder, gate anatomy, probing, false-positive budget, ratchets, where a gate runs, what to do *before* running one |
| `references/hooks.md` | doctrine | 150–200 lines | Claude Code hook contract, events, placement, fail-open hazard, portability limit, debugging, removal |
| `templates/docmap.md` | template | 90–130 lines | Seeded to `docs/DOCMAP.md` |
| `templates/decisions.md` | template | 60–90 lines | Seeded to `docs/DECISIONS.md` |
| `templates/open-questions.md` | template | 40–60 lines | Seeded to `docs/OPEN_QUESTIONS.md` |
| `templates/docgate.sh` | template (bash) | 220–300 lines | Seeded to `scripts/check-docs.sh` |
| `templates/hooks.example.json` | template | 30–50 lines | Copied into `.claude/settings.json` |
| `templates/retro-archive.md` | template | 40–60 lines | Seeded to `docs/superpowers/retro/YYYY-QN.md` |

### 2.1.1 Boundaries — what each new file does *not* own

Measured, not assumed: every concept below was swept across all 21 existing
references before a line was written. **Zero pre-existence** (safe to own outright):
`single source of truth` · `SSOT` · `supersede` · `as-built` · `ungated` ·
`doc map` · `pre-commit` · `propagation` *in the documentation sense* (its only hit
is `review.md`'s "wrong error propagation") · `reconcile` *in the intent/as-built
sense* (its only hit is the grill reconciling contradictions).

**Strong pre-existence — must be linked, never restated:**

| Concept | Already owned by | `gates.md` may own |
|---|---|---|
| Probing a check (plant → watch it fail → restore) | `audit.md` *Exit criterion*, `learned.md` rules 4–5 | the **executable recipe**: the commands, and asserting on `$?` rather than on a `FAIL` line |
| Ratchets | `audit.md` §3, `learned.md` rule 7, `retrospective.md`, `stages.md` | **floor variables** and where the count is printed inside a gate script |
| A gate's exit code | `learned.md` rule 11 | the **verdict-block placement rule** — nothing may run after it |
| False positives | `learned.md` rule 10 | the **measurement procedure** before shipping a check |
| A generator seeds green | `learned.md` rule 9 | the **seeded-gate execution guard** that enforces it here |
| "A class twice becomes a script" | `audit.md` §1 | the **six-step recipe** for writing that script |

The split is **law versus procedure**: `audit.md` and `learned.md` state *that* a
check must be proven and *why*; `gates.md` states *how* to write, place, arm, probe
and own one. Each side names the other in one line. A second statement of the same
law would be the exact defect this release ports a rule against.

`hooks.md` owns nothing that exists here today: `hook` appears once in the whole
`references/` tree, in `retrospective.md`'s list of grade-1 fixes, where it is named
and never explained.

### 2.2 Files edited

`SKILL.md` · `references/stages.md` · `references/knowledge-sources.md` ·
`references/conventions.md` · `references/companion-skills.md` ·
`references/audit.md` · `references/learned.md` · `references/grill.md` ·
`references/retrospective.md` · `references/artifacts.md` · `templates/brief.md` ·
`templates/retro.md` · `templates/adr.md` · `templates/README.md` ·
`pipeline.example.json` ·
`cursor/rules/task-pipeline.mdc` · `test/validate.py` ·
`.github/workflows/validate.yml` · `test/negatives.py` · `README.md` ·
`CHANGELOG.md` · `CLAUDE.md` · `CONTRIBUTING.md` · four version manifests.

---

## 3. Locked contracts

Everything in this section is a **contract**: a downstream task, a validator guard
or a seeded gate depends on the exact string. Change one here, walk every consumer.

### 3.1 The doc map — `docs/DOCMAP.md`

One per project, durable (not per run), committed. Seeded from
`templates/docmap.md` **only when absent** — never overwritten.

Required top-level sections, in this order and with these exact headings:

```markdown
## Regime
## Registers
## Single source of truth
## Propagation matrix
## Gates
## Ratchets
## Navigation
```

- `## Regime` — one line: `governed` (D1: the only value the pipeline seeds) plus
  the date and the run that established it.
- `## Registers` — table `| Register | File | ID scheme | Append-only? | Guarded? |`.
- `## Single source of truth` — table `| Fact | Home | Everything else |`. One row
  per fact class the project actually has; three rows on day one is correct.
- `## Propagation matrix` — table `| Change type | Update these | Checked by |`.
  The third column names the gate section that enforces the row, or `review` when
  no check can decide it. **A row with an empty third column is a finding**, not a
  blank.
- `## Gates` — table `| Gate | Command | When | Blocking? |`.
- `## Ratchets` — table `| Ratchet | Floor variable | Current | Set on |`.
- `## Navigation` — the anchor/deep-link rule and the index rule.

**SSOT applies to the doc map itself.** When the project already states a section's
content elsewhere (an `AGENTS.md`, a `CONTRIBUTING.md`), the section holds a
**pointer line** — `See AGENTS.md §5 (../AGENTS.md#5-propagation-matrix)` — and no
copy. A doc map that duplicates `AGENTS.md` is the first violation of the rule it
publishes.

### 3.2 The decision register — one home, two permitted shapes

**The skill already seeds ADRs** (`templates/adr.md` → `docs/adr/NNNN-<slug>.md`,
written lazily by the grill). Adding a second decision home beside it would fork the
register in the very change that publishes the SSOT rule. So:

> **A project has exactly one decision home. The doc map names it. The pipeline
> never creates a second one.**

Two shapes satisfy the contract; the difference is physical, not semantic:

| Shape | Home | Id | Use when |
|---|---|---|---|
| **Register** | `docs/DECISIONS.md`, append-only | `DEC-####` | default for a new project; many small decisions, read as a list |
| **ADR set** | `docs/adr/NNNN-<slug>.md`, one file per decision | `ADR-NNNN` (the file number) | the project already has `docs/adr/`; decisions are long and each wants its own page |

Both shapes owe the same six things, and every rule below applies to whichever is
in use: a **stable id**, an **append-only** history, a **status line** with the
supersede semantics of §3.2.2, a **`Consequences / affects:`** line, a **`Source:`**
line carrying the commit, and the **edge markers**.

**Detection, in order:** `docs/adr/` holds at least one `NNNN-*.md` → ADR set, and
the doc map records it. Otherwise → seed the register. **An existing `docs/adr/`
is never migrated** as a side effect of this track; migrating is its own decision,
with its own entry.

The rest of §3.2 states the **register** shape, because that is what is seeded. The
ADR shape carries the same fields as a front-matter block; `templates/adr.md` is
updated in the same change so the two agree field for field.

#### 3.2.1 Register format

Header (exact, the gate parses it):

```markdown
**Next free ID:** `DEC-0001`
```

Entry format (exact heading shape — the gate counts `### DEC-` headings):

```markdown
### DEC-0007 — Sessions are encrypted per organisation

- **Date:** 2026-08-03
- **Status:** Accepted
- **Context:** …
- **Decision:** …
- **Consequences / affects:** `docs/SECURITY.md`, `docs/DATA_MODEL.md`
- **Source:** run `2026-08-03-session-vault` · commit `a1b2c3d`
- **Supersedes:** DEC-0004
```

| Field | Rule |
|---|---|
| `Status` | one of `Accepted` · `Superseded by DEC-####` · `Reversed` · `Accepted · **Partially superseded by DEC-####** — <one line>` · `Accepted · **Refined by DEC-####**` |
| `Consequences / affects` | every doc that must change. **Each named doc must cite this id**, and the gate checks it |
| `Source` | the run/brief that produced it **and the commit** — the commit is what survives a file rename |
| edge markers | at most the ones that apply: `Refines:` (additive — target needs **no** annotation) · `Contradicts:` (a named clause of the target falls — target **must** be annotated) · `Supersedes:` (the whole target retires — target **must** be annotated) |

#### 3.2.2 Append-only, and the three edge markers

**Append-only.** To reverse: add a new entry, edit **only the status line** of the
old one, leave its body intact. Never renumber, never delete.

**Partial supersede annotates both sides.** Most reversals are partial — a later
decision replaces one clause and leaves the rest standing. If the old entry keeps a
bare `Accepted`, a reader who opens only that entry gets an answer that is no longer
true. So the new entry names which clause it replaces, and the old entry's status
line gains `· **Partially superseded by DEC-####** — <one line>`.

The three markers exist because one word for "adds to" and "replaces a clause of"
is unenforceable — on the source project, 204 of 275 refine/supersede edges pointed
at an unannotated target, and *neither a reader nor a script could tell which of the
204 should have been annotated*:

| Marker | Meaning | Target's status line annotated? |
|---|---|---|
| `Refines:` | **additive only** — every clause of the target still holds | no |
| `Contradicts:` | a **named clause** of the target no longer holds | **yes** |
| `Supersedes:` | the whole target is retired | **yes** |

Existing edges in a host project are **not** retro-classified: each needs a
judgement about what its author meant, and a bulk pass would guess.

### 3.3 The open-question register — `docs/OPEN_QUESTIONS.md`

Header: `**Next free ID:** \`OQ-0001\``. Rows:

```markdown
| ID | Question | Owner | Blocks | Status |
|---|---|---|---|---|
| OQ-0001 | … | Product | ROADMAP v1 | Open |
| OQ-0002 | … | Backend | — | Resolved→DEC-0007 |
```

Status vocabulary is closed: `Open` · `Resolved→DEC-####` · `Dropped (<why>)`. A
resolved question is **never deleted** — the question is the history of the answer.

### 3.4 The Doc Loop — the seven steps, in order

Fires whenever a decision is settled, **at any stage**, and it is not finished
until step 7:

1. **Orient and reconcile.** Read the registers and the topic doc. Run the
   as-built reconcile (§3.7). Do not contradict an `Accepted` decision without
   superseding it.
2. **Reserve the id, then record.** *Reading* "Next free ID" is not reserving it
   (§3.8). Then write the entry.
3. **Resolve.** Flip every answered `OQ-####` to `Resolved→DEC-####`.
4. **Propagate.** Walk the matrix row for this change type; update every doc it
   names, in the **same** change; keep SSOT — detail in one home, links elsewhere.
5. **Adjust scope.** Roadmap / MVP / module map if scope moved.
6. **Record as-built.** What was actually built, with the ids and the files, then
   reconcile again.
7. **Commit.** One focused commit, conventional message, **ids in the subject**.

**Finishing the chat answer is not finishing the task.** The loop is.

### 3.5 The propagation matrix — how a project builds its own

Not shipped as content (every project's is different) but as a **procedure**, run
at stage 0 and extended whenever a new doc class appears:

1. List the doc classes the project has (one line each: what it is the home of).
2. For each *change type* the project can undergo, name every doc that must move.
3. For each row, name the check that would notice if it did not — or write
   `review` and say why no check can decide it.
4. Seed the rows into `docs/DOCMAP.md` → `## Propagation matrix`.
5. The gate's propagation section enforces the mechanical half: **a doc named in a
   decision's `Consequences / affects:` line must cite that decision.**

**The ratchet is part of the design, not a concession.** Turning this check on in
an existing repository finds a large backlog (162 missing propagations across 73
decisions, on the project this comes from). Failing on all of them makes the gate
something people switch off. So: decisions from a floor id onward **fail**;
everything older is a **counted backlog that may only shrink**, printed on every
run. The floor is a variable at the top of the gate, and raising it is a decision.

### 3.6 The gate — `scripts/check-docs.sh` (seeded skeleton)

| Property | Contract |
|---|---|
| Exit code | non-zero on **any** failure. The exit code is part of the output — a gate that prints `FAIL` and exits `0` has been observed in the wild and CI stayed green over it |
| Portability | POSIX + bash 3.2 (macOS). **No `grep -P`, no `sed -i`, no `readarray`** |
| Verdict | last thing printed; **no check may run after it** |
| Ratchets | `<NAME>_FLOOR` variables at the top, current counts printed beside `OK` |
| Skips | a check that could not run (a submodule not checked out, a tool absent) **prints that it skipped**. Silent skips are the failure mode the gate exists to prevent |
| Scope | a header comment states what the gate does **not** cover |
| Seeds green | on a freshly seeded project the script exits `0` — asserted by the skill's own validator |

Sections shipped in the skeleton (each independently removable, each with the
project-agnostic half implemented and the project-specific half marked):

```
1  relative links resolve
2  every DEC-####/OQ-#### referenced is defined
3  "Next free ID" == max defined + 1
4  register counts stated in prose == computed
5  consequences propagation (ratcheted)
6  supersede/contradict annotations on the target
7  retired-decision residue — a doc citing a retired id must say so
8  status vocabulary (decisions and open questions)
9  every commit SHA named in the docs resolves
10 orphan check, both directions (the project fills in the two layers)
```

Section 9 is new relative to the source practice and exists because of D3: retro
entries now carry commits, and **a document may not send a reader to something
absent** (learned rule 14) applies to a SHA exactly as to a path.

### 3.7 Intent versus as-built

Two records, deliberately not merged:

| Record | Says | Written by |
|---|---|---|
| **Intent** — git: the registers, the specs, the plan | how it *should* be | the Doc Loop |
| **As-built** — the run record | how it *turned out* | stage 9's record step |

**Reconcile both before starting and after finishing.** The gap between them is
the finding — the doc is stale, the record is wrong, or they genuinely disagree and
that is a decision to make. Starting on an unresolved divergence means building
against a system that does not exist.

Where `agent-sync` is installed, `/agent-sync reconcile` and `record` do this.
Where it is not, the as-built record is a section of the run's carry-over ledger
and the reconcile is a read of it — **the discipline is not optional; the tool is**.

### 3.8 Registers are shared state

A register is the one file two agents will write in the same minute.

- **Reserve the id before minting it.** "Next free ID" is a *reading*; a second
  agent reading it in the same minute gets the same answer.
- **Take a lease before writing a guarded register**, where a lease mechanism
  exists.
- **When no mechanism can arbitrate, the run is `ungated`** — say so. A run that
  describes the project as protected while nothing enforces it is the failure this
  paragraph exists to prevent.
- `agent-sync` is the reference implementation and an **optional** companion:
  absent, the pipeline states `ungated` and continues.

### 3.9 Gate types — the two axes, never conflated

**Axis A — the stage gate type** (already in `pipeline.schema.json`):

| Type | Meaning |
|---|---|
| `auto` | the orchestrator verifies `check` itself, pass/fail |
| `manual` | wait for the operator's explicit go |

**Axis B — the enforcement mechanism**, a promotion ladder:

| Rung | Mechanism | Promote to the next rung when |
|---|---|---|
| 1 | **Doctrine line** — a rule in a reference file | it was violated once |
| 2 | **Review question** — asked at a named gate | no check can decide it (say why, in one line) |
| 3 | **Script check** — a section of the project's gate | the class has occurred **twice** |
| 4 | **CI step** | the check must hold for people who never run it locally |
| 5 | **Hook** — agent-time, blocks the edit | the failure is cheaper to prevent than to detect, and the target is an edit an agent makes |

A rule may live at more than one rung, but a rule that *pretends* to be enforced
and is not is the same failure as a gate that exits `0` on failure.

### 3.10 The learning loop — retro contract (D3)

| Artefact | Contents | Read |
|---|---|---|
| `docs/superpowers/retro.md` | Standing instructions (≤10) · Run stamps · **Recent log** — entries from the last **5** run stamps | stage 0, **in full**, every run |
| `docs/superpowers/retro/YYYY-QN.md` | the full archive: every entry and every retirement ever written | **queried** by the task's nouns at stage 0; never read in full |

Standing-instruction table (exact columns):

```markdown
| id | Born | Commit | Instruction | Because | Retire when | Last fired | Fired at |
```

- `Born` — date · run topic. `Commit` — the short SHA of the commit that
  introduced the rule. `Fired at` — the short SHA of the commit of the **last**
  run in which it fired.
- Every SHA in either file must resolve (`git rev-parse --verify --quiet <sha>^{commit}`)
  — gate section 9.

Log entry (archive and recent window share the format), required fields:
**Symptom** (with evidence) · **Surfaced at** · **Owned by** · **Root cause** ·
**Fix** (grade 1/2/3) · **The check** · **Commit** · **Upstream?**

Run stamps gain a `Commit` column — the run's final commit, so a stamp is a
navigable point in history rather than a date.

**Rotation.** At the prune, entries older than the last five stamps move to the
archive file for their quarter. Moving is not deleting: the archive is append-only
and every retirement is logged in it with its trigger and its commit.

**Why the commit is not decoration.** `file:line` evidence rots at the next edit,
and the entry then describes a line that has moved or gone. A SHA is immutable, it
carries the diff, the message and the parent, and `git show <sha>` reconstructs the
whole incident — which is exactly what an agent needs when the same class returns
two months later.

---

## 4. Stage bindings — exact gate additions

### 4.1 Stage 0 — inventory, reconcile, retro

Added to the stage-0 gate check (type stays `manual`):

- the **doc-system inventory** ran and `docs/DOCMAP.md` exists (seeded if absent)
  with every section of §3.1 present and its propagation matrix non-empty;
- the **regime** is recorded (`governed`) with the registers named;
- **intent and as-built were reconciled** and every divergence has a resolution;
- the retro's **standing instructions were read in full** and the **archive was
  queried** by the task's nouns;
- the autonomy sweep answers the documentation row (registers, gate commands,
  ratchet floors, who may write which register).

### 4.2 Stage 9 — the propagation sweep

Added to the stage-9 gate check (type stays `auto`):

- the **propagation matrix** was walked for **every** change type this run
  produced, not only the sources the harvest read;
- every settled decision has a `DEC-####`, every answered question is flipped, and
  every doc named in a `Consequences / affects:` line cites its decision;
- **the docs gate is green**, its ratchet counts printed, and any check that
  skipped said so;
- the as-built record is written and reconciled.

### 4.3 Stage 10 — evidence for the gate itself

Added to the stage-10 gate check (type stays `manual`):

- every check the close-out leans on has been **probed once against a planted
  defect**, with the probe recorded — this already exists in prose and now names
  the docs gate explicitly;
- **ratchet counts printed beside the verdict**, and a ratchet that grew carries a
  sentence saying why;
- the retro ran in order — **prune (with the commit of every retirement logged) →
  stamp (with the run's commit) → entry → archive rotation** — and the standing
  list is at or under its cap.

---

## 5. Validator guards (each needs a negative self-test)

| # | Guard | Rationale |
|---|---|---|
| V1 | `references/{documentation,gates,hooks}.md` exist and are ≥1500 bytes | A stub silently turns built-in doctrine back into a dependency |
| V2 | Stage 0 `gate.check` names the doc inventory **and** the doc map | Declared where it is not enforced is inert |
| V3 | Stage 9 `gate.check` names the propagation matrix **and** the docs gate | The stage-9 promise is otherwise unfalsifiable |
| V4 | Stage 10 `gate.check` requires the docs gate **probed** and the ratchets **printed** | "Green" must never read as "verified" |
| V5 | `templates/docmap.md` carries every §3.1 heading | A seeded map missing the matrix seeds a project with no obligation |
| V6 | `templates/retro.md` standing table carries `Commit` and `Fired at`; `templates/retro-archive.md` exists | D3's traceability is otherwise a suggestion |
| V7 | `references/retrospective.md` and `templates/retro.md` agree on the standing-instruction column set | Same drift class as the autonomy sweep: one is what the agent reads, the other what it writes |
| V8 | `templates/docgate.sh` contains no `grep -P`, no `sed -i`, no `readarray`, and prints its verdict last | Portability, and the exit-code-after-verdict failure |
| V9 | `templates/docgate.sh` exits `0` against the seeded templates | learned rule 9 — a generator seeds green |
| V10 | The SKILL.md anchor guard extended with `propagation` and `doc map` | The stage-10/9 close-out concept must reach `stages.md`, the config **and** `documentation.md` |
| V11 | `templates/adr.md` and `templates/decisions.md` carry the same field set (`Status`, `Consequences / affects`, `Source`, and the three edge markers) | Two permitted shapes of one register that disagree on fields is a fork with extra steps |

V9 is the only guard that executes anything; it runs the seeded gate over a
scratch directory built from the templates and asserts `0`.

---

## 6. Findings from reviewing the current skill

Recorded here because they are in scope for the same release ("nothing forgotten,
missed or half-done"). Each becomes a task in the plan.

| # | Finding | Where | Grade |
|---|---|---|---|
| F1 | **The "read in full" justification covers one of three parts.** `knowledge-sources.md` says `docs/superpowers/retro.md` is "the one harvested source read in full rather than queried: the standing instructions are capped at ten precisely so that this is cheap" — but the same file also holds the Log, which is unbounded, and `artifacts.md` repeats "in full" for the whole file. The cap justifies reading one part and is used to justify reading all three | `knowledge-sources.md:55-57`, `stages.md:44`, `artifacts.md:65` | fixed by D3 + wording |
| F2 | **A self-containment claim the same file contradicts 42 lines later.** `SKILL.md:41` promises "no stage that can fail because a dependency is missing"; `SKILL.md:83` says "For UI tasks the spec gate **requires** it — install before stage 3, otherwise stop and ask". `companion-skills.md:117` states the true rule: *"Never gate any stage on an install **except** the stage-3 UX track on a UI task."* The overclaim is `SKILL.md`'s alone | `SKILL.md:41` vs `SKILL.md:83` | reword to the enforced claim; name stage 1's web-search fallback |
| F3 | **Stage 9's gate is unfalsifiable.** "docs in sync with code" names no artefact and no check | `stages.md:281` | fixed by §4.2 |
| F4 | **`audit.md` rule 1 dead-ends.** "A category belongs in a script" and no doctrine says how to write, place, probe or own one | `audit.md:188` | fixed by `gates.md`; add the pointer |
| F5 | **Source precedence is stated for facts but not for decisions.** `code > host docs and ADRs > the wiki > memory` is right for *what is* and wrong for *what should be* — a decision not yet built still governs | `knowledge-sources.md:176` | add the two-question split |
| F6 | **The incident is narrated; the rule is missing.** `learned.md:121` already cites *"a coordination plugin reporting a lease held by an identity that belonged to a different session"* as one of four examples under *the one instruction that would have prevented the most* — but there is no row in the table, although the file's own preamble says a rule belongs there **once it has a check**, and this one does | `learned.md:121` vs the table | add rule 15 **cross-referencing** the existing narration, never repeating it |
| F7 | **`conventions.md` has no doc-regime detection.** It reads the host's test/lint/deploy/docs commands but never asks where decisions live | `conventions.md:35` | add a *Documentation regime* section |
| F8 | **The carry-over ratchet is specified as printed "at every gate" but no gate criterion requires it** except stage 10 | `audit.md:228`, `stages.md` | make the print an explicit line in the stage 6/7/9 gate text |
| F9 | **`companion-skills.md` never mentions `agent-sync`**, while `SKILL.md` and `stages.md` both reference `/agent-sync finish` in the stage-10 close-out — a companion used in doctrine and absent from the companion matrix and the preflight | `companion-skills.md:31` | add the row and the preflight line |
| F10 | **`templates/README.md` will be stale** the moment templates are added; it is not covered by any guard | `templates/README.md` | list every template; add a guard that the directory and the list agree |
| F11 | **A stated invariant that the shipped artefact violates.** `CONTRIBUTING.md` invariant 6 reads *"`pipeline.example.json`'s `skills[]` may not name an external provider"*; the shipped config names **eleven** across four stages (`wiki-query`, `graphify`, `context7`, `context7-docs`, five `super-ux:*`, `figma`, `wiki-update`). The enforced rule is narrower and correct — `validate.py` forbids only `superpowers:`/`grill-me`/`grilling`, i.e. providers that would *substitute for built-in doctrine* | `CONTRIBUTING.md:95`, `validate.py:512` | reword the invariant to what is enforced, and enumerate the permitted optional tools |
| F12 | **`agent-sync` is doctrine in three files and absent from the preflight.** It is named in `SKILL.md`, `stages.md`, `acceptance.md` and the README as the thing that runs the stage-10 multi-repository close-out, and appears **zero** times in `companion-skills.md` — the one file that decides what gets detected and offered before stage 0 | grep: 4 files vs `companion-skills.md` | same fix as F9; recorded separately because it is measured, not inferred |

F2, F5, F6, F9, F10, F11 and F12 are pre-existing defects independent of this
feature; they ship in the same release because they touch the same files. F9 and
F12 are the same fix from two directions — F9 was inferred from reading, F12 was
measured with a grep, and both are listed because *the measurement is the evidence*.

---

## 7. Out of scope, stated so it is not mistaken for missed

- **Reimplementing leases or a guard hook.** `agent-sync` owns it (D4).
- **Shipping a project's propagation matrix content.** The procedure ships; the
  rows are the project's (§3.5).
- **A second wiki/graph integration.** Unchanged.
- **Changing the stage list, ids, order or gate types.** Explicitly not touched, so
  the three mechanically-compared surfaces keep their current shape.
- **Retro-classifying existing `Refines:` edges** in any host project. Same rule as
  the source practice: an edge is reclassified when someone touches it for another
  reason; a bulk pass would guess.

---

## 8. Definition of done for the release

1. `npm test` prints `PASS`, `npm run test:all` green, every new guard proven by a
   negative self-test that was watched failing.
2. `templates/docgate.sh` run over a scratch project seeded from the templates
   exits `0` — and, with a planted defect in each of its ten sections, exits
   non-zero for each; the probe log is committed in the CHANGELOG entry.
3. Every surface that enumerates the flow still names the final stage last.
4. Every `references/*.md` reachable from `SKILL.md`.
5. Four-way version sync at `1.7.0`, CHANGELOG section written as *what changed
   and why it mattered*.
5a. **The release reaches the catalogue.** `sshlg-skills` pins every family member's
   version in its own `skills.json`; a release that does not bump that pin is
   invisible — `npx sshlg-skills list` keeps reporting the old number and `update`
   keeps installing it. The release is finished when `npx --yes sshlg-skills@latest
   list` prints `1.7.0`, not when `npm publish` returns.
6. **Every** finding in §6 is closed with evidence or explicitly carried with a
   home — counted from the table at close-out, never restated here (learned rule 8).
