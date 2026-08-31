# Brief — the plants stop promising that the tree will not change

**Run** `2026-08-31-b113-derived-anchors`
**Requested by** the board. `B-113` was the highest-priority open row (prio 12, filed
2026-08-22, four confirmations) and the scope of this run is that row and what closing
it forces — nothing else.

**The row, in its own words:** *negative-test anchors are pinned to literals that the
releases they guard move, so a release disarms its own checks.* What makes it worth a
release rather than a patch is the pattern in the confirmations. The board re-derived
its ages and `bd5`'s needle stopped existing. The first blind eval runs shipped and
`pf1`'s guard went dormant. A release finally carried an honest run stamp and `gap1`'s
precondition emptied. **Three of the four instances were caused by the repository
getting healthier**, which is exactly why nobody noticed: nothing about the change that
disarmed the plant looked like a regression, and the plant reported green until a
35-minute suite ran at release time, one release later.

So the deliverable is not three repairs. It is a census of the class, a derivation for
every member of it, and a check in the **cheap** gate that refuses the next one.

## Source ledger

| Source | What it gave |
|---|---|
| `docs/evidence/backlog.md` → B-113 | the row's own question — *is the number the plant WRITES or the number it LOOKS FOR?* — and its first count, 27 of 412 |
| `1179339` (`test(negatives): three plants stop inheriting their preconditions`) | the three v1.80.0 instances repaired individually: `bd5`, `pf1`, `gap1`. This run's regression cases |
| `docs/evidence/retro.md` → 2026-08-30 `wave1-gate-fixes` | the root cause already written down: *a plant that inherits its precondition is a check that switches itself off when the repository gets healthier* |
| `test/negatives.py` | the runner: `parse_steps`, the `BROKEN` no-op detector, `MIN_EXPECTED`/`MIN_PROPS`, and the aggregate line that counted a `SKIP` inside *all N guards provably reject* |
| `test/probe.py` | the three assertions a plant owes, and assertion 3 — *the guard that fired is the guard under test* — which is why a `validate.py \| grep 'message'` is not a needle |
| `references/probing.md` | the plant/run/restore doctrine and the landed-mutation rule the census mechanises |
| `references/learned.md` → rules 5, 8, 10, 22 | doubt the probe first; compute never restate; measure a detector before trusting it; an operation that changes nothing reports the same as one that changed everything |
| `.github/workflows/validate.yml` | the corpus: 419 negative self-tests and 14 property checks at the start of this run |

## Autonomy

| Question | Answer, recorded so stages 1–10 do not re-ask |
|---|---|
| Scope | B-113 only. Other board rows are out of scope even where the census brushes them |
| May the shipped doctrine change? | No. This run touches the test corpus, the validator and the ledgers; `plugins/**` is edited only where a plant's needle forced a re-read, and no doctrine sentence moves |
| May plants be deleted? | No. A plant that cannot be derived is **declared** in its own body, never removed |
| Release | Minor. The behaviour of the test corpus changes and a new suite joins `test:all` |
| Blocked-on-human | None |

## The REQ table

Frozen. Adding is free; removing needs the operator.

| REQ | What must be true | How it's verified |
|---|---|---|
| REQ-054 | Every negative self-test is classified by whether it **reads** a value a release can move, from the AST rather than by grep — provenance from `open(...).read()`, read-backs per path, regex shape stripped, validator-output greps excluded | `test/anchors_test.py` — 18 whole-workflow fixtures, 8 of them watched firing; four are retractions of the detector's own first draft |
| REQ-055 | The census is **printed as a measurement**, not asserted: how many plants, how many needles they read off disk, how many pin a value, how many declare, how many can decline to run, and how many read no file at all | the `negative-test anchors:` disclosure beside the verdict, plus a property check that requires it to print |
| REQ-056 | No plant pins a value a release can move unless it declares, in its own body, why the value cannot be derived and what would falsify the declaration | `test/validate.py` refuses an undeclared anchor and a declaration that resolves to nothing; both watched red as negative self-tests |
| REQ-057 | A check that can decline to run is **never counted as one that passed** — plants and property checks alike, named in the runner's own summary, subtracted from its claim, and required to declare the state it cannot construct | `test/negatives.py` prints a `DORMANT` block and says *N of M*; `test/validate.py` refuses a `SKIP` branch with no `# dormant-when:`, watched red |
| REQ-058 | The three v1.80.0 instances stay covered: `bd5` (a re-derived board), `pf1` (a guard gone dormant), `gap1` (a precondition emptied) — and the two live-board plants beside them | each plant re-run through `test/negatives.py -k`; the census reports zero pinned needles in the live-board plants |
| REQ-059 | The widened check gets an independent reader before merge (R-005), and every blocking finding is closed with its own fixture | the reader's report, replayed: each blind spot becomes a case in `test/anchors_test.py` and each false number is re-derived by running the detector against the branch point |

## Knowledge sources

| Source | Read at | What stage 9 owes it |
|---|---|---|
| `docs/evidence/backlog.md` | stage 0 | B-113 closed with the counted census, not with a claim |
| `docs/evidence/retro.md` | stage 0, in full | one entry, one stamp, the prune |
| `docs/evidence/verification.md` | stage 0 | one row per REQ above |
| `CHANGELOG.md` | stage 0 | the entry, and the guard count the gate compares against the workflow |
| `test/negatives.py`, `test/probe.py`, `references/probing.md` | stage 0 | the runner's floors moved with the corpus; the probe doctrine is unchanged and cited rather than restated |
