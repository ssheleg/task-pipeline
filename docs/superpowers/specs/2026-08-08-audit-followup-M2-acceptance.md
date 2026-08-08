# Acceptance — `audit-followup` · M2 `claim-registry`

**Branch:** `feat/claim-registry` → PR #11 · **Version:** `v1.25.0`
**REQ:** REQ-005, plus carry-over row 7.

## Ladder walk

| Seam | Finding | Became |
|---|---|---|
| L1→L2 | The decision *"a class seen twice belongs in a script"* (`audit.md`) had never reached the file that enforces it. Six instances of one class were each fixed as an instance | the registry |
| L3→L4 | The registry's contract said *"compare a stated number against a computed one"* and its implementation read only **digits** — while the founding incident was the word *"fifteen"* | word forms added; four live claims surfaced that had been skipped in silence |
| L5→L6 | Three of six classes had no negative self-test; the invariant requires one per guard | four more self-tests + a second positive control; floor 126 → 130 |
| L6→L7 | `docs/DOCMAP.md` still described this guard as *"guard-count comparison"* — a reader would have believed one number was covered | matrix row and ratchet table rewritten |

**Two passes. New findings: 5 · self-inflicted: 0.** Every one came from the PR review; the
module's own probes found none of them.

## REQ coverage

| ID | Status | Evidence |
|---|---|---|
| REQ-005 | `verified` | `npm run test:all` exit **0** — `PASS: all 130 guards provably reject their planted defect`. Six classes, each armed with its own planted-defect test; two positive controls (a quoted citation, and a citation split across a line break) assert the exemptions do **not** over-fire |
| row 7 | `verified` | `CLAUDE.md`'s *"nine surfaces"* above a list of ten is deleted, with the reason recorded in place: a count of an enumeration inside one sentence is not computable from outside it |

## What the registry actually reports

```
PASS: task-pipeline structure valid
  claim registry — negative self-tests: dormant (truth 130) · rules in learned.md: dormant (truth 21)
                 · dated eval runs: ok 1 (truth 1) · standing instructions: dormant (truth 5)
                 · evidence canons: ok 4 (truth 10) · reference files: dormant (truth 28)
```

**Four of six dormant, and that is measured, not assumed.** `v1.23.1` and `v1.24.0` deleted
those numbers rather than correcting them — confirmed against git history, not inferred from
the absence of a failure. The registry is a **ratchet against re-introduction** more than a
finder of present drift, and the verdict line says which it is on every run.

## What the operator should look at

**The review found five issues; the module's own five probes found none of them.** That is
the second consecutive module where this held, and it is what `R-005` was added for one
release ago. The instruction is already in force and already firing — what it cannot do is
make the probes better, because a probe is written from the same model of the problem as
the check.

**Two findings were the same class in new clothes:**

- *A per-line predicate in a corpus that wraps at ~80 characters.* The quote exemption
  checked one line, so a citation split by a line break stopped being a citation. This is
  the **third** occurrence — v1.24.0's marker guard was the second. The unit is now written
  into the code with the reason, rather than rediscovered a fourth time.
- *A silent ceiling.* The number-word map stopped in the forties while the guard count was
  already 130, so a word form above the ceiling would have been **skipped without a word**.
  Skipping is acceptable; skipping in silence is what canon 9 forbids. Unread tokens now
  print beside the verdict.

**And one correction to this run's own prose.** The first draft of the release note claimed
every dormant class was dormant *because its number had been deleted*. For the canons class
that was untrue — it was dormant because the check could not read word forms. A dormant
state is a claim about the corpus and needs the same evidence as any other; that one was
plausible, unverified and wrong.

## Gate verdict

```
GATE 10 acceptance (M2): PASS — 1/1 REQ verified + carry-over row 7 closed
  carry-over: 9 rows · 6 open · 0 unresolved (row 7 closed by this module)
  guards: 130 negative self-tests (floor 126 → 130) · registry classes: 6, two armed
  abstained: 0 · unmeasured: behavioural evidence — still 0 blind runs on 0 of 3 models
```
