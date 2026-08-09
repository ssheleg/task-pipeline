# M5 — the sixth rotation axis, and the enumeration that had already drifted

Module of the `audit-followup` programme. Branch `m5-re-derive-axis`, ships as a
minor.

## The premise, re-measured at the moment of use

The module was written down as *"add a sixth rotation axis to `audit.md`"*. Measuring
before building changed its shape, which is now the fourth time in six modules:

| Surface | Axes enumerated | Missing |
|---|---|---|
| `references/audit.md` §*Every pass changes the axis* | **5** | — (this is the definition) |
| `cursor/rules/task-pipeline.mdc` | **4** | *False success* |
| `README.md` | **3** | *The graph against the docs*, *False success* |

Nobody noticed, because each summary reads as complete on its own: a list of three
orthogonal things is a perfectly convincing list of three orthogonal things. This is
the repository's own rule 20 — *when a thing exists twice, ask which one is used* —
and rule 2's both-directions clause, at the scale of a bulleted list.

So M5 does two things, not one:

1. adds the sixth axis, and
2. makes an enumeration that drifted **unable to drift silently again**.

## REQ

| # | Requirement | Verified by |
|---|---|---|
| R1 | `audit.md` gains a sixth axis, **Re-derivation**: a number the audit already produced is re-produced by a command of a *different shape*, and the exit criterion is **the pair printed**, never agreement asserted | the axis exists in the numbered list; `npm test` green |
| R2 | The axis carries a worked example that shows **two differently-shaped commands and both outputs** — a doctrine that only asserts re-derivation cannot teach it | guard: the axis body must contain a fenced block with two distinct commands |
| R3 | Every surface that enumerates the axes enumerates **all** of them | guard, both directions: a surface naming ≥2 axis keywords must name all of them; keywords derived from `audit.md` at check time, never hand-listed |
| R4 | The axis count is registered as a claim class, so no document can restate a stale one | claim registry entry, computed from `audit.md` |
| R5 | Each new guard is proven against a planted defect, and one of the plants lands in `audit.md` itself — the file that *defines* the axes | `npm run test:negatives` |

## Why this axis and not another

Four applications of the technique are on the record in this repository, and **two of
them refuted a belief that had already been written down as fact**:

| # | The first number | The differently-shaped second command | Outcome |
|---|---|---|---|
| 1 | The version invariant, called *four-way* in two living documents | grep the version string across the repo instead of reading the sentence | **refuted** — five surfaces (`CONTRIBUTING.md:74`, `CHANGELOG.md:155`) |
| 2 | Graph node count 864 → 839, believed to be tightening | per-file node counts instead of the total | confirmed — a real tightening |
| 3 | The same procedure, 839 → 798 | the same per-file shape | **refuted** — erosion, not tightening (carry-over row 11) |
| 4 | `learned.md` growth, believed to be *rules accumulating* | count words as well as rows, across tags | refuted the fix that was planned for M6 — rows were flat while words grew |

Row 2 and row 3 are the argument for the axis in one line: **same procedure, opposite
answers.** A re-derivation is not a second opinion, it is a second *shape*; and its
value is that it can come back disagreeing.

## Out of scope

- Re-deriving anything automatically. The axis is a rotation an auditor takes, not a
  job. A check that re-runs commands and compares them is a different (and much
  larger) thing, and it would need to know which numbers matter.
- The `README.md` enumeration is not completed to six. It stops enumerating and names
  the doctrine file instead — a summary that restates a list is the drift, and
  deleting a restatement is how this repository has fixed every count it got wrong.
  The Cursor rule *does* get all six, because it is self-contained by contract and
  cannot point anywhere.
