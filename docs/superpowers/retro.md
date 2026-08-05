# Pipeline retrospective — task-pipeline

One file per project, not per run. Written as the **last act of stage 10**:
prune first, then stamp, then write an entry **only if the run diverged**.
Doctrine: `references/retrospective.md`.

**What stage 0 reads in full:** *Standing instructions*, *Run stamps* and *Recent
log* — all three are bounded by construction, which is why the cap is not
negotiable. The **archive** (`docs/superpowers/retro/YYYY-QN.md`) is *queried* by
the task's nouns and never read end to end.

## Standing instructions (max 10 — in force right now)

Every row is a rule an agent must follow, that **no check can decide**. A rule a
check *can* decide is not written here: it is written as the check (grade 1).
No row is accepted without its **retire-when** trigger, written at birth.

Every SHA here must resolve — the documentation gate runs `git rev-parse --verify`
over all of them.

| id | Born | Commit | Instruction | Because | Retire when | Last fired | Fired at |
|---|---|---|---|---|---|---|---|
| R-001 | 2026-08-03 · `documentation-track` | `dbe4f43` | When a check stays silent against a planted defect, **prove the plant landed in the text the check actually parses before touching the check.** | Two silent probes in one run: one was a bad probe (§9 correctly skips outside a git tree), one was a real bug (`$((0009))` is octal). The split is 50/50 here and was 4-of-5 probe-fault on the source project — guessing wrong costs a real bug or a false fix. | a probe harness exists that asserts the plant changed the parsed text, making this mechanical | 2026-08-04 | `7155c98` |
| R-002 | 2026-08-03 · `doc-track-audit` | `096f0f0` | When a batch of edits returns **any** error, re-verify **every** edit in that batch before reporting the batch done — not only the one that errored. | Two edits were issued together; the second failed the read-before-write check and was retried, the first was silently never applied. It was reported as done, shipped in v1.7.0, and surfaced only in a post-release audit as a question the grill never asks with a field in the brief waiting for the answer. | the harness reports per-edit outcomes in a form a check can read, or the edits are issued one per message | 2026-08-04 | `7155c98` |
| R-003 | 2026-08-05 · `artifact-hygiene` | `13028e9` | When you fix a defect in one check, guard or detector, **immediately run that defect's definition against its siblings** before moving on — the same file's other checks, and the other files that do the same job. | `learned.md` rule 6 says *sweep the class, not the instance*, and this is its **third** recorded failure to be applied to itself. 2026-08-03 `enforcement-audit`: a fix scoped to references→README while the same class lived in six other places. 2026-08-03 `root-cause`: nine findings, one missing matrix row. 2026-08-05: check 2's false-positive class was solved, and check 4 — its immediate sibling, in the same file, written in the same hour — shipped with the identical bug and fired on this run's own documents. Two instances were worth notes; `audit.md` says a class seen twice becomes a mechanism rather than a third ledger row. | a check can compare sibling detectors for a shared false-positive class — which needs the classes to be named in a machine-readable form first | 2026-08-05 | `13028e9` |

Retire on **any** of: it became a check · every path/command it names is gone · it
has not fired in the last five run stamps. At eleven rows, the oldest never-fired
row goes — the cap is not negotiable, ranking is.

## Recent log — entries from the last five run stamps (newest first)

Older entries and every retirement **move** to `docs/superpowers/retro/YYYY-QN.md`
at the prune. Moving is not deleting: the archive is append-only and holds the
incident forever, so pruning the in-force list costs no knowledge.

### 2026-08-05 · `artifact-hygiene` · a guard that had been decorative for nine releases

- **Symptom:** the VERDICT-last contract guard passed against a gate script whose
  verdict marker had been renamed. It split the file on the **word** `VERDICT` —
  which also appears in the header sentence forbidding anything after it — so its
  "tail after the verdict" was most of the script, exit lines included, and it
  matched `exit 0` / `exit 1` no matter what. Green since it shipped, on
  `docgate.sh` as well as the new file.
- **Surfaced at:** stage 6, on the first probe ever written for it ·
  **Owned by:** the release that shipped the guard without one.
- **Root cause:** the guard's own subject matter was its blind spot. A file that
  *documents* a rule contains the rule's keyword, so anchoring on the keyword
  anchors on the documentation. Same shape as check 2's placeholder problem, one
  layer up — and nobody noticed because a guard nobody probes is indistinguishable
  from a guard that works.
- **Fix:** grade 1 — split on the `# ---------- VERDICT` section marker and require
  the marker to exist.
- **The check:** its own negative self-test, watched failing on a renamed marker
  after the rename was asserted to have landed.
- **Commit:** `13028e9`
- **Upstream?** n/a — this repo is the skill; both gate scripts ship with the fix.

### 2026-08-05 · `artifact-hygiene` · two self-tests sharing one scratch directory

- **Symptom:** CI failed on `cp: cannot create regular file
  '/tmp/verdict-copy/./.git/objects/pack/…': Permission denied`. A new negative
  self-test reused a scratch directory an existing one already owned, so the second
  copy landed in a populated tree and git's read-only pack files refused to be
  overwritten. A guard written in reaction then found **four more collisions that
  predated the branch**.
- **Surfaced at:** stage 7, by CI · **Owned by:** every release that added a
  self-test without checking the name was free.
- **Root cause:** loud failure was the *lucky* outcome. Two tests sharing a scratch
  directory can also succeed — against the first test's corruption instead of their
  own — and a test that passes for the wrong reason is worse than one that fails.
  Nothing in the suite could see the collision, because each test only ever looks at
  itself.
- **Fix:** grade 1 — a guard requiring every `cp -R . /tmp/…` destination in the
  workflow to be unique, plus `rm -rf` before all 35 copies so a leftover directory
  cannot fail a probe for an unrelated reason.
- **The check:** its own negative self-test. Building it produced two more instances
  of the same day's lessons: the guard was first placed **after** `validate.py`'s own
  `if errors: … sys.exit(1)` — the nothing-runs-after-the-verdict defect, committed
  while writing the guard against it — and it then fired on its own self-test,
  because the step that *plants* a duplicate contains the string being scanned for.
  Heredoc bodies are stripped now, the same treatment markdown fences already get.
- **Commit:** `13028e9`
- **Upstream?** No — the collision is this repository's CI shape, not the skill's.

### 2026-08-04 · `run-continuity` · a checker that resolves from the file's home

- **Symptom:** seeding `templates/carryover.md` to the path its own doctrine names
  (`docs/superpowers/specs/`) turned `npm test` red on the first try:
  `broken relative link … ../references/audit.md`. Present since `2a6ff89` (v1.1.0),
  nine minor releases. Two prior runs wrote a carry-over ledger and neither hit it,
  because neither copied the template verbatim.
- **Surfaced at:** stage 1, by following the instruction · **Owned by:** the release
  that put a relative link in a file whose whole purpose is to be copied elsewhere.
- **Root cause:** the link checker resolves every link **from the file's home**, and
  a template's home is the one place it is never read. Green from a check looking in
  the wrong direction — the `surface-audit` shape, one axis over.
- **Fix:** grade 1 — a seeded template carries **no** relative links at all and
  names files in code spans instead.
- **The check:** the seeded-template guard, watched failing on a planted link.
- **Commit:** `17b35de`
- **Upstream?** n/a — this repo is the skill; the rule ships in the bundle, and it
  is the same requirement the Cursor rule has always had.

### 2026-08-04 · `run-continuity` · the spec locked a contract that cannot exist

- **Symptom:** stage 5 started building the guard stage 3 had specified and the
  first measurement showed it could never go green. The spec required a template's
  relative links to resolve **from the destination**; the same file also sits in
  `templates/`, where the existing checker resolves them **from there**. One link,
  two required bases, no satisfying value.
- **Surfaced at:** stage 5, before the guard shipped · **Owned by:** stage 3.
- **Root cause:** the contract was written from the *defect's* shape rather than
  from the constraint system the defect lives in. The finding said "this breaks at
  the destination", so the spec said "make it work at the destination", and nobody
  asked what else resolves that link today.
- **Fix:** grade 3 — a note. `gates.md` already demands a detector be measured
  before it ships, and that demand is exactly what caught this. The spec was amended
  in place and the amendment says why, rather than being quietly rewritten.
- **The check:** none added; the mechanism worked. Recorded so the seam is visible.
- **Commit:** `17b35de`
- **Upstream?** No — `learned.md` rule 6 (sweep the class, not the instance) covers
  it. A second instance of that rule not being applied to itself: worth recording,
  still not worth a new rule.

### 2026-08-04 · `run-continuity` · the loop fired into the decision it was waiting on

- **Symptom:** the run armed `/loop 5m` — the mechanism this change was adding — and
  then parked on a task needing the operator's word. The timer fired into that wall,
  twice: a generic scheduled prompt arriving where a specific answer was owed.
- **Surfaced at:** stages 2 and 5, by using the feature · **Owned by:** the design,
  which had not asked what a fire does when the run is parked.
- **Root cause:** two failure modes, one cause. A loop firing into a `manual` gate
  is a **nag**, and a nagged operator learns to ignore it — the same death as a rule
  nobody reads to the end. And a tick is not consent: reading it as authorization
  would have written to the operator's private config on the strength of a cron
  schedule.
- **Fix:** grade 1 — the run cancels its own loop job on parking and prints the
  re-arm command; the mode never collapses a gate. Both applied in this run before
  they were written down.
- **Reopened after acceptance, pre-tag:** the first cancel was issued against an id
  that had never been scheduled, and the teardown call **reported success anyway** —
  so the real job kept firing for another forty minutes while the transcript said it
  had stopped. The doctrine as first written said *cancel* and not *verify the
  cancel*, which would have reproduced this in every project that followed it.
  `continuity.md` now requires listing the jobs afterwards. Caught by the very tick
  that should not have existed.
- **The check:** the continuity clause guard covers the file. **No check can decide
  whether a tick was read as consent** — that half is doctrine, and it ships.
- **Commit:** `17b35de`
- **Upstream?** Already upstream, in `references/continuity.md`.

### 2026-08-03 · `root-cause` · five audits, one missing row

- **Symptom:** five audit passes produced roughly thirty findings. Grouped by shape,
  **nine were the same missing propagation row** — this repository ships a matrix to
  every project it touches and its own had no row for *adding a document*. Evidence:
  `adoption.md`, `setup.md`, `portability.md`, `learned.md` absent from the README map;
  the manifest at 14 of 26; the Cursor rule two releases stale; `CONTRIBUTING` eight
  guards behind; `agent-sync` doctrine in four files and absent from the companion
  matrix; `templates/README.md` stale.
- **Surfaced at:** a question about why the audits keep finding things · **Owned by:**
  the release that dogfooded the doc map and wrote six matrix rows, none of them the
  one for its own most frequent change.
- **Root cause:** a check can only walk the list it was given. Every guard was green
  through all nine, because none of them was told the list should have that row on it.
  The matrix is the list, and the row about adding to the list is the row nobody
  writes.
- **Fix:** grade 1 — the meta-row is step 0 of the matrix procedure, a guarded row in
  the seeded template, a pass of the entry audit, a row here, and a named release step
  whose one `review` cell (the Cursor rule) is called out by name. It earned its keep
  on the first walk: it is what said this change alters agent behaviour elsewhere, so
  the Cursor rule was part of it.
- **The check:** the meta-row guard, probed by removing the row from a copy.
- **Commit:** `17d53ba`
- **Upstream?** Already upstream — the meta-row ships in the template and the doctrine,
  so the next project starts with the row this one learned the hard way.

### 2026-08-03 · `enforcement-audit` · the previous fix was scoped to its instance

- **Symptom:** `CONTRIBUTING.md` states its invariants are *"what the validator
  enforces"* and listed sixteen while the validator enforced eight more concepts —
  adoption, the exclusion clause, the opt-out, the input map, portability, the routing
  template, the README-reach rule, the seeded-template Contents rule. Measured: each
  `grep -ci` in CONTRIBUTING → 0, in validate.py → 1–11.
- **Surfaced at:** a fifth audit, on the enforcement-claim axis · **Owned by:** the
  release *before* it, which fixed exactly this class for references → README and
  manifest and did not ask where else the class lived.
- **Root cause:** the fix was written against the finding rather than the class.
  `learned.md` rule 6 says sweep the class — and it was not applied to the sweep that
  was applying it.
- **Fix:** grade 1 — the invariant list is self-verifying: every invariant that cites
  a guard cites a literal this validator actually prints, checked on every commit.
- **The check:** the invariant-citation guard, probed both ways (a false citation, and
  the list ceasing to cite at all).
- **Commit:** `a34e5ff`
- **Upstream?** No — `learned.md` rule 6 already covers it. This is an instance of the
  rule failing to be applied to itself, which is worth recording and not worth a rule.

### 2026-08-03 · `surface-audit` · nine of nine verified, and four surfaces did not know

- **Symptom:** one release after an acceptance that read *11/11 verified*, a fourth
  audit found four shipped files whose readers were never told they exist — the Cursor
  rule two releases behind (0 hits for adoption, the entry audit, portability, the
  routing boundary, the opt-out phrase), the README map missing three references, the
  portability manifest covering 14 of 26, and two seeded templates over 100 lines with
  no Contents.
- **Surfaced at:** a standalone audit · **Owned by:** stage 10 of the two releases
  before it. The acceptance verified every REQ, and *"the surfaces know"* was never a
  REQ.
- **Root cause:** reachability from `SKILL.md` is the check that exists, and it stayed
  green the whole time — it proves an agent can **find** a file, not that a reader was
  **told** about it. Two different questions wearing one green.
- **Fix:** grade 1 — every reference must now appear in the README map and in the
  portability manifest, and every seeded template over 100 lines carries its own
  Contents. Both check the direction that finds absences.
- **The check:** the reach guard and the template-Contents guard, both watched failing.
- **Commit:** `86bcad1`
- **Upstream?** No — but the lesson generalises and is already in `audit.md`: a
  comparison needs two sides, so a check that only walks the list you have cannot see
  the entry you never made.

### 2026-08-03 · `default-routing-adoption` · the work contradicted the spec, and the loop caught it

- **Symptom:** stage 5 was about to seed `scripts/check-docs.sh` into this repository
  because the spec said so. Step 1 of the adoption walkthrough being written in the
  same run — *inventory what is already there* — showed `npm test` already resolves
  links, checks citations and computes counts over the same markdown. Seeding a
  second gate would have made the doc map's first act a breach of the SSOT rule it
  publishes.
- **Surfaced at:** stage 5 · **Owned by:** stage 3 — the spec assumed the template
  applied without running the walkthrough's own first step against this repo.
- **Root cause:** writing a tutorial and applying it in one run is exactly when the
  author is least likely to *follow* it. The spec was written from the template's
  shape rather than from the inventory the tutorial demands.
- **Fix:** grade 3 — a note, not a rule. The pipeline already handles this: the
  finding went back to stage 3, the spec was revised in place, and the changed check
  was raised in the carry-over ledger for the operator instead of being swapped
  silently. No new instruction is owed; the mechanism worked.
- **The check:** none added. This is the loop behaving as designed, recorded so the
  next run knows the seam exists.
- **Commit:** `d76ff5e`
- **Upstream?** No — it is an instance of doctrine already in `audit.md` ("a finding
  that contradicts the spec goes back to stage 3").

## Run stamps

One line per run, appended at stage 10. This is what makes "five runs" countable
— without it the cold-rule is a guess and the prune becomes a mood.

| Date | Topic | Commit | Verdict | Retro |
|---|---|---|---|---|
| 2026-08-05 | `spec-plan-quality` | `PENDING` | 11 REQ · 8 verified by a proven check · 3 carrying an explicit `review` half · carry-over 5 rows, 0 unresolved, 1 printed exclusion | **no divergence** · 3 standing · retired 0 · added 0 · **R-003 fired on its first run** (asked of `planning.md`, answered "no", recorded) · guards 76 → 80 |
| 2026-08-05 | `artifact-hygiene` | `13028e9` | 15 REQ · 13 verified by a proven check · 2 marked `review` out loud (the agent-fixes obligation, the Cursor rule) · 1 new REQ from the ladder walk carried as printed backlog · carry-over 7 rows, 0 unresolved | 2 entries · **3 standing (was 2)** · retired 0 · added 1 (R-003) · R-001 fired twice, R-002 did not fire · guards 68 → 76 |
| 2026-08-04 | `run-continuity` | `7155c98` | 13 REQ · 13 verified (12 by a proven check, 1 by eye — outside the repo) · carry-over 4 rows, 0 unresolved | 3 entries · 2 standing · retired 0 · added 0 · **archived 6** · R-001 and R-002 both fired |
| 2026-08-03 | `default-routing-adoption` | `d76ff5e` | 9 REQ · 9 verified (one check revised mid-run, revision agreed) | 1 entry · 2 standing · retired 0 · added 0 · R-001 and R-002 both fired |
| 2026-08-03 | `root-cause` | `17d53ba` | 1 cause behind 9 findings, fixed as doctrine | 1 entry · 2 standing · retired 0 · added 0 |
| 2026-08-03 | `enforcement-audit` | `a34e5ff` | 1 finding, fixed as a class | 1 entry · 2 standing · retired 0 · added 0 |
| 2026-08-03 | `surface-audit` | `86bcad1` | 4 findings, all fixed | 1 entry · 2 standing · retired 0 · added 0 |
| 2026-08-03 | `setup-and-autonomy` | `7569dd6` | 11 REQ · 11 verified | no divergence · 2 standing · retired 0 · added 0 |
| 2026-08-03 | `code-audit` | `270bc2c` | 8/8 findings fixed, each proven before and after | 2 entries · 2 standing · retired 0 · added 0 · R-001 and R-002 both fired |
| 2026-08-03 | `doc-track-audit` | `096f0f0` | 9/9 findings fixed, each proven before and after | 2 entries · 2 standing (was 1) · retired 0 · added 1 · R-001 fired |
| 2026-08-03 | `documentation-track` | `0ddd4e3` | 17/17 contracts · 12/12 findings verified | 2 entries · 1 standing (was 0) · retired 0 · added 1 |

The `Commit` column is what turns a stamp from a date into a navigable point in
history: `git show <sha>` is the run, and `git log <sha>..HEAD` is everything that
happened since a rule last fired.
