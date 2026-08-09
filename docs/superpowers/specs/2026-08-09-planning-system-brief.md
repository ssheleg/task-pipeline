# Brief — the planning system: a board, a verification ledger, and an exposure index

Locked at stage 0 on 2026-08-09. Operator: sshlg. Standing authorization for the
programme (manual gates 0 / 2 / 7 / 10 closed by the runner).

## The request, in one line

Make the pipeline's planning explicit: a place where the work-list lives between runs,
a record of what shipped and whether a human ever confirmed it works, and a printed
number that says how much unverified change has piled up — with the list of what to
check.

## Source ledger (stage 0 harvest)

| Source | What it gave |
|---|---|
| `references/artifacts.md` | both maps already exist (stage → reads, stage → writes) and a single-home table. **No home for anything that outlives a run.** |
| `templates/carryover.md` | append-only, any stage adds, stage 10 reads in full. Its `Where it lives now` column points at `backlog` — **a file the pipeline does not own** |
| `references/continuity.md` | *"Each iteration re-measures the work-list"* and *"'Next up is X' is a claim about the board, and it is the one sentence no gate reads"* — **the doctrine exists, the board does not** |
| `references/stages.md` §8 | the verification trio, the CI verdict, the rendered page. All **per run**; nothing accumulates |
| `docs/superpowers/retro.md` | six standing instructions, read in full: R-001 doubt the probe · R-002 re-verify the whole batch · R-003 sweep the detector's siblings · R-004 next command conditional on exit code · R-005 independent reader on any new check · R-006 reporting a gap is not fixing it |
| checkout | `behind upstream: 0` |
| code graph | present, 839 nodes, **11 commits stale** (carry-over row 11 — stated, not closed) |

## Decisions taken at the grill

| # | Question | Answer |
|---|---|---|
| D1 | one file or two | **two** — `backlog.md` is mutable (a queue), `verification.md` is append-only (a history). One file would put an append-only rule inside a file edited every iteration, which is where such rules stop being obeyed |
| D2 | the unit of a verification row | **one row per REQ** — the REQ spine already carries a name and a verification method, so *"check these"* comes out human-readable without translating commits |
| D3 | autonomy | **standing for the programme** |
| D4 | branch policy | the repo's own `CLAUDE.md`: structural change → branch + PR + its own minor. Not re-asked; it is written down |

## The correction I am making to the request, out loud

The request says *"подсчитывать вероятность ошибки"*. A probability of defect is not
computable from these inputs, and a number that presents itself as `P(defect)` is the
false-success class this repository spent eight releases removing.

What ships is an **exposure index with its inputs printed** — never a percentage, never
a target. It becomes a real probability only if a project accumulates its own defect
data, and `verification.md` is precisely the journal that would make that possible
later. Named honestly today.

## REQ table (frozen — adding is free, removing needs the operator)

| REQ | Requirement | Verified by | Module |
|---|---|---|---|
| REQ-001 | `artifacts.md` names both new files in **both** maps and in the single-home table | the map's own reachability guard + `npm test` | N1, N2 |
| REQ-002 | `docs/superpowers/backlog.md` — seeded at stage 0 when absent, picked up when present | template exists; doctrine states both paths; guard | N1 |
| REQ-003 | Any stage may append a row mid-run, same rule as the ledger: *deferred out loud or lost* | doctrine + guard on row shape | N1 |
| REQ-004 | Each loop iteration reads the board at the top and re-prioritises at the bottom; *"next up"* cites the measurement | `continuity.md` states it; the claim is checkable against the file | N5 |
| REQ-005 | Every carry-over row homed `backlog` resolves to a real board id — **both directions** | guard, both ways, with a planted defect each way | N1 |
| REQ-006 | `docs/superpowers/verification.md` — one row per REQ: shipped-in, auto verdict, human-confirmed date or `never` | template + guard | N2 |
| REQ-007 | Stage 8 writes the row; stage 10 refuses a REQ with no row | `stages.md` + guard | N2 |
| REQ-008 | The exposure index is computed and printed beside the verdict as a **disclosure** — inputs visible, plus the list of what to check | printed by the gate; claim-registry class so it cannot be restated | N3 |
| REQ-009 | `/task-pipeline checkup` runs **standalone**, with no task in flight | command doc + the mode's own doctrine | N4 |
| REQ-010 | The index is never rendered as a probability or a percentage | doctrine says so; guard rejects a `%` on that line | N3 |

**Definition of done, every module** (not a REQ row — a gate criterion): each new guard
is watched failing against a planted defect (`npm run test:negatives`), R-005's
independent reader runs before merge, and R-006 is honoured — a gap reported is said to
be reported, not claimed as fixed.

## Module map (stage 2)

Walking skeleton first: without a board there is nowhere for anything else to write.

| # | Module | REQ | Ships as |
|---|---|---|---|
| **N1** | **the board** — `backlog.md`, its template, both artifact-map rows, and the carry-over resolution in both directions | REQ-001·REQ-002·REQ-003·REQ-005 | v1.31.0 |
| N2 | the verification ledger — `verification.md`, its template, stage 8 writes, stage 10 requires | REQ-001·REQ-006·REQ-007 | v1.32.0 |
| N3 | the exposure index — computed, printed as a disclosure with its inputs and the check-list | REQ-008·REQ-010 | v1.33.0 |
| N4 | the checkup mode — `/task-pipeline checkup`, standalone | REQ-009 | v1.34.0 |
| N5 | the loop wiring — the iteration reads and re-prioritises, and *"next up"* cites the board | REQ-004 | v1.35.0 |

## Out of scope

- A tracker integration. The board is a file in the repo; a project with Linear or Jira
  keeps using it, and the board's `home` column points there — exactly as the carry-over
  ledger already does.
- Automatic verification of anything. The whole point of the ledger is the column a
  machine **cannot** fill.
- Re-deriving the exposure index into a calibrated probability. Stated as future work
  the ledger makes possible, not promised.
