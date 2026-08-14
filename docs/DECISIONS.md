# Decisions — task-pipeline

**Append-only.** Every settled thing that shapes the product, the architecture, the
scope, security, data, pricing or process. Doctrine:
`plugins/task-pipeline/skills/task-pipeline/references/documentation.md`.

Established 2026-08-11. The skill tells every host project to keep this register and
this repository did not — the same gap `B-009` found for open questions, and it
surfaced the same way: a status vocabulary (`Resolved→DEC-####`) pointing at a file
that was not there.

**Next free ID:** `DEC-0005`

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
- **The measurement it rests on:** `docs/evidence/backlog.md` carries a
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
- **Consequences / affects:** `docs/evidence/backlog.md` (`B-057`, which carries the
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

---

### DEC-0004 — two browser channels, ranked by nothing, and a browser test suite is not the look

- **Date:** 2026-08-14
- **Status:** Accepted
- **Context:** `OQ-0003` / `B-056` asked three things at once: is Playwright a *second*
  browser companion or *the* one where a project already runs it in CI; what stage 6's
  *checked in a browser, not in the diff* means when the check is a Playwright spec CI
  runs rather than an agent driving a page; and whether structured accessibility
  snapshots change what the rendered-surface claim is worth. Since v1.36.0 the bundle
  had named exactly one channel — the `chrome-devtools` MCP, behind a plugin install —
  for a step it asks for at three stages.
- **Decision, in three parts.**
  1. **Playwright joins as a second channel and neither is ranked.** The operator asked
     for Playwright *in priority* and then, asked directly, chose equal footing. The
     rows describe capability instead of quality: `playwright` needs no plugin, and its
     CLI half puts no tool schema in the context window — upstream's own comparison,
     and it compares that CLI to an MCP rather than to `chrome-devtools`;
     `chrome-devtools` alone reaches `lighthouse_audit` and a heap snapshot, and alone
     analyses a performance trace, which `playwright-cli tracing-start` can record.
     The first draft of this entry stated the trace leg as an absolute and was wrong;
     the reader R-005 dispatched measured it against the CLI's own `--help`. **A run that ranks them has invented a fact the matrix does not carry.**
  2. **A green browser test suite is the other half of the gate, never a substitute for
     the look.** `playwright test` in CI proves what someone thought to assert, on the
     paths someone thought to write; it cannot report the console error nobody asserted
     on, the bundle that 404s past an unvisited route, or the element that moved under a
     fixed header. The suite is counted as coverage; the look is still a page opened and
     read. The two fail differently, which is the whole reason to keep both.
  3. **The browser step stays `recommended`, never a gate.** Hardening it was offered
     and declined: a gate an environment cannot satisfy is a gate an agent learns to
     report around, and the honest-degradation sentence — *verified by reading the
     diff* — already prices the absence correctly.
- **What made this visible:** the operator's report that `chrome-devtools` lags, against
  a matrix that offered no alternative.
- **Consequences / affects:** `references/companion-skills.md` (two rows, one shared
  detection rule, the tie-breaker, the preflight block), `references/stages.md`
  (stages 5, 6, 8), `references/tdd.md`, `SKILL.md` (stage 6 and 8 gate rows),
  `README.md`, `cursor/rules/task-pipeline.mdc`, `SKILL-CARD.md` (the MCP-reference
  risk row), `docs/OPEN_QUESTIONS.md` (`OQ-0003` resolves here),
  `docs/evidence/backlog.md` (`B-056` closes).
- **Source:** run `2026-08-14-playwright-browser-channel` · v1.55.0
- **Id allocation:** by hand under lease `B-056`. `agent-sync reserve DEC` refused —
  the `fs` backend cannot append atomically and said so rather than handing out an id
  it could not guarantee.
