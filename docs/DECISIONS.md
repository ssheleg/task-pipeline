# Decisions — task-pipeline

**Append-only.** Every settled thing that shapes the product, the architecture, the
scope, security, data, pricing or process. Doctrine:
`plugins/task-pipeline/skills/task-pipeline/references/documentation.md`.

Established 2026-08-11. The skill tells every host project to keep this register and
this repository did not — the same gap `B-009` found for open questions, and it
surfaced the same way: a status vocabulary (`Resolved→DEC-####`) pointing at a file
that was not there.

**Next free ID:** `DEC-0004`

Reading *"Next free ID"* is **not** reserving it — a second agent reading it in the
same minute gets the same answer. Reserve it, then write.

**To change your mind:** add a new entry, edit **only the status line** of the old
one, leave its body intact. Never renumber. Never delete.

---

### DEC-0001 — `SURFACED` is checked for contradiction, never for completeness

- **Date:** 2026-08-11
- **Status:** Accepted
- **Context:** `OQ-0001` asked whether the hand-back's `SURFACED` section can be
  checked at all. It is defined as what a run learned by accident — recoverable from
  no artefact — so *"nothing surfaced"* is a quiet decision by construction, and the
  `hand:` line records that a hand-back happened, never that it was complete.
- **Decision:** `SURFACED` gets a **contradiction** check and no completeness check.
  A run that filed a board row, a carry-over row, an open question or a retro entry
  has provably surfaced something; if its hand-back reports zero, the two disagree
  and the disagreement is computable. The doctrine states the residual **in the same
  sentence**: a run can surface something, file it nowhere, report zero, and nothing
  will notice.
- **The measurement it rests on:** `docs/superpowers/backlog.md` carries a
  `Source` column naming the run or document that filed each row — **0 with an
  empty Source**. The join from *run* to *rows this run filed* exists today with
  no new bookkeeping.
- **What it deliberately does not buy:** coverage. The check must never require a
  minimum, or a run will file a throwaway row to make the numbers agree.
- **Consequences / affects:** `references/progress.md` (the hand-back section),
  `references/acceptance.md` (criterion 12), `docs/OPEN_QUESTIONS.md` (`OQ-0001`).
- **Source:** run `2026-08-11-residue-and-honesty` · commit `e063b29`

---

### DEC-0002 — the neighbour-probe work-list is computable, and it is a population rather than a debt

- **Date:** 2026-08-11
- **Status:** Accepted
- **Context:** `OQ-0002` recorded that the list of guards reading a **scoped span**
  "cannot be computed from the code as written", which left `B-057`'s remaining half
  with no work-list. The claim was written from a reading, not a measurement.
- **Decision:** the premise is **withdrawn**. A guard is exposed to this class
  exactly when its needle is matched against a *derived* string rather than raw file
  text, and that derivation is syntax. `B-057` takes the static pass as its
  work-list.
- **The measurement it rests on:** a static pass over `test/validate.py` —

  | scoping shape | sites |
  |---|---|
  | named helper (`_section` / `_gate_bullet`) | 10 |
  | inline slice `text[a:b]` | 4 |
  | `re.split` into parts | 8 |
  | `partition`/`split` then index | 27 |
  | `search` then `.end()`/`.start()` offset | 6 |
  | **total** | **55** |

  against 350 `fail()` calls — a lower bound on the number of checks.
- **The distinction that must travel with the number:** these are **candidates, not
  findings**. Scoping is usually correct and necessary. Published as a defect count
  the figure produces busywork and reads as debt; published as the population to
  sample from, it is a work-list. The row must say which.
- **Consequences / affects:** `docs/superpowers/backlog.md` (`B-057`, which carries the
  neighbour-probe coverage figure and must keep it honest — it read *three guards of
  253* when this decision was written, and the corpus has grown since),
  `docs/OPEN_QUESTIONS.md` (`OQ-0002`). An earlier draft of this line cited a figure in
  `references/gates.md` that has never existed there; the reviewer caught it, in the
  register whose subject is hand-written counts.
- **Source:** run `2026-08-11-residue-and-honesty` · commit `e063b29`

---

### DEC-0003 — this project keeps an addressable decisions register, reversing DOCMAP's rule against one

- **Date:** 2026-08-12
- **Status:** Accepted
- **Context:** `docs/DOCMAP.md` stated that no `docs/DECISIONS.md` is created here,
  deliberately — one decision home per project, the CHANGELOG already carries every
  decision with its reason and its commit, and a second register would be the fork the
  SSOT rule exists to prevent. That reasoning was sound when written. It predates
  `docs/OPEN_QUESTIONS.md`, whose closed status vocabulary is `Resolved→DEC-####`.
- **Decision:** the register exists. A CHANGELOG version heading **cannot serve as the
  target of `Resolved→DEC-####`**: two decisions shipped in one release collapse to a
  single pointer, and the path from a question back to its answer is lost. The SSOT rule
  is kept by **direction** instead of by absence — the reason lives in `DECISIONS.md`,
  and the CHANGELOG points at the id rather than restating it.
- **What made this visible:** the reviewer on PR #37, which created the register and left
  DOCMAP's prohibition untouched. A register that appears without a decision is the fork
  the old rule feared, so the reversal is written down rather than performed.
- **Consequences / affects:** `docs/DOCMAP.md` (the Registers row and the paragraph that
  forbade this file), `docs/OPEN_QUESTIONS.md` (its status vocabulary now resolves),
  `docs/DECISIONS.md` (this entry).
- **Source:** run `2026-08-11-residue-and-honesty` · commit `0756b0f`
- **Supersedes:** the unnumbered rule in `docs/DOCMAP.md`, which predates this register
