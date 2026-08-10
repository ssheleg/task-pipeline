# Acceptance — findings-shaped work gets an entry (v1.39.0)

Closed 2026-08-10 on branch `findings-entry`. Board at open: **23**; at close: **26**
(three added, none closed — B-047 was rewritten rather than closed, see REQ-007).

## 1. The ladder walk — run BEFORE the table

Ordered by seam, not by file.

| Seam | Absence found | Where it went |
|---|---|---|
| **L1→L2** | `перевести` was locked by the v1.9.0 design and never reached the shipped description. It existed in exactly one place in the repository: the design that locked it | REQ-004, fixed, with a guard that reads the locked list out of that design |
| **L5→L6** | `REQ-003` (v1.9.0) was accepted **verified** against a list it never checked — the evidence recorded was the clause's shape and its character count | named here; the new guard is the check that decision should have had |
| **L6→L7** | Nine guards shipped with nine probes for **ten** fail sites. The unmapped-alias branch had none, and `MIN_EXPECTED` counts steps, so the missing probe was invisible to the count as well | six probes added; 227 → 233 |
| **L6** | An independent reader defeated the nine new guards **fifteen ways**, each verified by planting the text and watching `npm test` print `PASS`. Author-written probes had exercised only the shapes the author already had in mind — which is the sentence R-005 is written in | all fifteen fixed in `0df1e7a` |
| **L6** | Adding those probes found a **sixteenth** the reader had not: the reading check filtered the routing section to lines containing "not", and an exclusion list's bullets do not repeat the word | fixed; the whole section is checked |
| **L7→L0** | The shipped surface does **not** satisfy the requirement's statement for one class of four: a production check still does not route | REQ-005 records it; `B-047` rewritten, `B-053` filed |
| **L2→L3** | The brief said the boundary lives on four surfaces. It lives on **three** — `README.md` does not carry it | corrected in REQ-002 below rather than silently narrowed |
| **—** | This release **disarmed a guard with prose**: `Guards **218 → 226**` without the colon made the CHANGELOG count check stop matching, and `npm test` was green over a number it never read | fixed, plus an anti-dormancy sentinel — which the reader then showed was itself one synonym from dormant |

## 2. Coverage — one row per REQ, with evidence

| REQ | Status | Evidence |
|---|---|---|
| REQ-001 boundary restated as *answer vs finding that lands* | **verified** | description 1008/1024; guards for both halves, each with a probe (`rt01`, `rt02`) |
| REQ-002 classes named on every surface carrying the boundary | **verified, scope corrected** | three surfaces, not four — `README.md` carries no boundary clause. Guards are scoped to each file's `## Routing` section after the reader showed a file-wide test proves only that a word exists (`rt06`, `rt07`) |
| REQ-003 exclusions do not drift from the `NOTRIG` evals | **verified** | all three locked exclusions guarded; `reading` cannot return on any of the three surfaces (`rt03`, `rt10`, `rt15`) |
| REQ-004 `перевести` restored, locked list guarded | **verified** | guard reads the list from the 2026-08-03 design and fails loudly if that list stops being readable (`rt05`, `rt12`) |
| REQ-005 routing measured before and after | **verified** | `evals/routing/RESULTS.md` — three runs, 7/10 → 9/10 → 8/10, with the variance stated rather than the best run quoted |
| REQ-006 an eval case per findings class | **verified** | 28 cases; coverage counts `should_trigger` queries only after the reader showed a negative control was certifying "named and untested" as covered (`rt08`, `rt09`, `rt13`) |
| REQ-007 the close-out says **behaviour** or **reporting**, per finding | **verified** | this section, below |
| REQ-008 independent reader before merge | **verified** | dispatched; fifteen findings, all fixed; verdict in `0df1e7a` |

## 3. Behaviour or reporting — R-006, per finding

| Finding | What changed |
|---|---|
| bug hunt, PR review unreachable | **behaviour** — `none` → routed in both after-runs, for the stated reason |
| audit routed on a stretched `hardening` | **behaviour** — the answer held, its ground changed; the reason now quotes the clause |
| production check unreachable | **reporting only** — the class is named on three surfaces and still does not route, 0 of 2. `B-047` says so; `B-053` owns the fix |
| the fifteen guard defects | **behaviour** — each verified by planting the defeating text and watching the fixed guard fail |
| the harness cannot separate effect from noise | **reporting only** — stated in `RESULTS.md` §3 and filed as `B-052`. Rebuilding it mid-run would have measured the before and after with different instruments |

## 4. Disclosures

- `unlooked` at close: the routing guards now register four skip points, so a missing
  `SKILL.md`, an unreadable design doc, a reshaped clause or an unparseable eval suite
  print rather than vanish.
- **Not measured:** whether Claude Code's own selection machinery behaves as these
  descriptions predict. The measurement is of description text, by subagents fresh in
  context and not blind in disposition. `B-002` remains at zero blind runs on zero of
  three models, and nothing here may be quoted as one.
- **Not touched:** the operator's global `~/.claude/CLAUDE.md`, which carries its own
  copy of the boundary. Outside this repository; asked separately.

## 5. The closing question — what is missing?

The measurement proves the *description* moved three classes of four. It does not prove
a run started that way ends well: no eval exercises what stage 3 actually produces when
the task is an audit rather than a feature. `audit.md:350` says stages 3–5 produce
findings and fixes — nothing checks that they do.
