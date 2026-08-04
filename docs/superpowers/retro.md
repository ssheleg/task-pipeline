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
| R-001 | 2026-08-03 · `documentation-track` | `dbe4f43` | When a check stays silent against a planted defect, **prove the plant landed in the text the check actually parses before touching the check.** | Two silent probes in one run: one was a bad probe (§9 correctly skips outside a git tree), one was a real bug (`$((0009))` is octal). The split is 50/50 here and was 4-of-5 probe-fault on the source project — guessing wrong costs a real bug or a false fix. | a probe harness exists that asserts the plant changed the parsed text, making this mechanical | 2026-08-03 | `096f0f0` |
| R-002 | 2026-08-03 · `doc-track-audit` | `096f0f0` | When a batch of edits returns **any** error, re-verify **every** edit in that batch before reporting the batch done — not only the one that errored. | Two edits were issued together; the second failed the read-before-write check and was retried, the first was silently never applied. It was reported as done, shipped in v1.7.0, and surfaced only in a post-release audit as a question the grill never asks with a field in the brief waiting for the answer. | the harness reports per-edit outcomes in a form a check can read, or the edits are issued one per message | 2026-08-03 | `096f0f0` |

Retire on **any** of: it became a check · every path/command it names is gone · it
has not fired in the last five run stamps. At eleven rows, the oldest never-fired
row goes — the cap is not negotiable, ranking is.

## Recent log — entries from the last five run stamps (newest first)

Older entries and every retirement **move** to `docs/superpowers/retro/YYYY-QN.md`
at the prune. Moving is not deleting: the archive is append-only and holds the
incident forever, so pruning the in-force list costs no knowledge.

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

### 2026-08-03 · `code-audit` · a citation whose file resolves and whose section does not

- **Symptom:** fifteen section-qualified cross-references pointed at nothing. Eleven
  of them — every per-stage freedom label — cited `gates.md` → *Axis B*, which is the
  enforcement ladder and contains zero mentions of degrees of freedom. Evidence: a
  sweep of all 33 such citations; `grep -ci "degrees of freedom" references/gates.md`
  → 0.
- **Surfaced at:** a third-axis audit · **Owned by:** the release that wrote the
  labels — the concept had no home, and rather than noticing that, the citation was
  pointed at the nearest plausible section.
- **Root cause:** the link checker proves a *file* resolves, and that green was read
  as the pointer being right. `learned.md` names this exact failure and deliberately
  keeps it as a review question because "only a reader can prove it is the right
  one" — which was true until the sweep showed the section name is machine-checkable.
- **Fix:** grade 1 — `gates.md` gained the two sections the citations were reaching
  for, and a guard now compares every pointer against the target's real headings.
- **The check:** the citation guard, measured for false positives (whitespace
  normalised — a wrapped citation is not a defect and six were reported as such).
- **Commit:** `270bc2c`
- **Upstream?** Already upstream: `learned.md`'s review question can be promoted to a
  rule with a check, and this release is the evidence.

### 2026-08-03 · `code-audit` · the installer built the thing its own family prunes

- **Symptom:** `install.sh` and `bin/task-pipeline.js` write a plain copy to
  `~/.claude/skills/task-pipeline`; `sshlg-skills` deletes exactly those, and its
  README says Claude Code gets the plugin "never as a plain copy". `CLAUDE.md`
  documented `./install.sh --force` as the local install path.
- **Surfaced at:** reading the installers as code — the first pass on them in three
  audits · **Owned by:** whichever release added the launcher's prune rule without
  walking back to the installers it contradicts.
- **Root cause:** the rule lived in the family repo and the violation lived in a
  member repo, so no single repository's checks could see both.
- **Fix:** grade 1 — both installers refuse when a plugin install is detected.
- **The check:** none mechanical; the honest state is that this is a cross-repository
  invariant with no cross-repository gate. Recorded rather than pretended.
- **Commit:** `270bc2c`
- **Upstream?** Worth an issue on `sshlg-skills`: the family owns the rule, so it
  should own the check.

### 2026-08-03 · `doc-track-audit` · a gate that read one of the two shapes it promised

- **Symptom:** on a project using the ADR shape — which `documentation.md` permits
  explicitly — `scripts/check-docs.sh` printed **eight `dormant` lines out of ten
  sections** and exited 0, with a planted propagation violation uncaught. Evidence:
  the ADR seed run, and `templates/docgate.sh` parsing only `$DEC_FILE`.
- **Surfaced at:** a post-release audit · **Owned by:** the release that wrote both
  the doctrine and the gate in one change and tested only the shape it had seeded.
- **Root cause:** `dormant` was designed so a *fresh* project is green on day one,
  and it was never bounded to that case — so it also covered a *populated* register
  the gate could not read. Green from a check that did not look is the failure the
  whole file is written against, reproduced by its own author.
- **Fix:** grade 1 — a normalised entry index, so no section knows which shape it
  reads; plus the validator asserting the seeded run **reports the shape it found**
  and **ran at least N live checks**. Exit 0 alone can no longer stand in for
  having looked.
- **The check:** two seeded projects executed on every `npm test`, one per shape,
  each asserting live-check counts; seven planted defects on the ADR shape.
- **Commit:** `096f0f0`
- **Upstream?** Already upstream. The generalised rule — *a skip is not a pass, and
  a gate must report what it looked at* — went into `references/gates.md`.

### 2026-08-03 · `doc-track-audit` · a cross-cutting protocol that no stage had heard of

- **Symptom:** `grep -c "doc loop\|documentation.md"` over `brainstorm.md`,
  `spec.md`, `planning.md`, `build.md`, `review.md`, `acceptance.md` → **0 each**,
  while SKILL.md, stages.md and documentation.md all called the Doc Loop
  cross-cutting.
- **Surfaced at:** the same audit · **Owned by:** the release, which wired the track
  into the orchestration layer and stopped there.
- **Root cause:** the orchestrator's view was mistaken for the executor's. An agent
  running stage 5 opens `build.md`; it never re-reads SKILL.md to discover that a
  protocol applies. Declaring a thing cross-cutting does not distribute it.
- **Fix:** grade 1 — five stage doctrines now name it, held by a guard; and stage 5
  gets the rule its architecture demanded (a subagent never writes the register).
- **The check:** the doc-loop reach guard, with its negative self-test.
- **Commit:** `096f0f0`
- **Upstream?** n/a — this repo is the skill.

### 2026-08-03 · `documentation-track` · a new gate passed for every id ending 8 or 9

- **Symptom:** `templates/docgate.sh` §3 (*next free id*) printed `ok` against a
  planted `DEC-0009` while the highest defined id was `DEC-0001`. Probe output:
  `SILENT §3 next-free — planted defect did NOT fail the gate`.
- **Surfaced at:** the probe pass · **Owned by:** the same change that wrote §3 —
  it was never exercised against a two-digit-ending id before the probe.
- **Root cause:** `$((0009))` — bash reads a leading-zero literal as **octal**, `9`
  is not an octal digit, the arithmetic expansion errors, the enclosing `if` takes
  its **else** branch, and the section reports success. Zero-padded ids are the
  normal case in this register, so the check was silent for two digits out of ten.
- **Fix:** grade 1 (mechanical) — strip leading zeros before any arithmetic, with
  the cause written into the code comment so the next reader does not re-derive it.
- **The check:** the probe itself, now part of the release procedure: every gate
  section planted, run, restored, asserted on `$?`. 10/10 fire.
- **Commit:** `dbe4f43`
- **Upstream?** Already upstream — this **is** the skill. The generalised rule is
  `references/gates.md` → *Probing*, and the judgement half became `R-001`.

### 2026-08-03 · `documentation-track` · two guards fired on the change that wrote them

- **Symptom:** the new portability guard rejected `docgate.sh` for containing
  `grep -P`, `sed -i` and `readarray` — all three inside the header comment that
  **forbids** them. Separately, the workflow's pre-existing `sed -i` guard rejected
  the negative test that plants `sed -i`.
- **Surfaced at:** the first `npm test` after each was written ·
  **Owned by:** the same change.
- **Root cause:** a detector that reads prose about a construct as an instance of
  it — `learned.md` rule 10's false-positive class, seen from the inside.
- **Fix:** grade 1 — the guard scans code lines only; the negative test builds the
  construct at runtime, the pattern the merge-conflict test already used.
- **The check:** both are now covered by their own negative self-tests.
- **Commit:** `dbe4f43` and `45e26f0`
- **Upstream?** The rule already exists (`learned.md` 10); the *procedure* for
  measuring a detector before shipping it is now `gates.md` → *The false-positive
  budget*.

## Run stamps

One line per run, appended at stage 10. This is what makes "five runs" countable
— without it the cold-rule is a guess and the prune becomes a mood.

| Date | Topic | Commit | Verdict | Retro |
|---|---|---|---|---|
| 2026-08-03 | `default-routing-adoption` | `d76ff5e` | 9 REQ · 9 verified (one check revised mid-run, revision agreed) | 1 entry · 2 standing · retired 0 · added 0 · R-001 and R-002 both fired |
| 2026-08-03 | `setup-and-autonomy` | `7569dd6` | 11 REQ · 11 verified | no divergence · 2 standing · retired 0 · added 0 |
| 2026-08-03 | `code-audit` | `270bc2c` | 8/8 findings fixed, each proven before and after | 2 entries · 2 standing · retired 0 · added 0 · R-001 and R-002 both fired |
| 2026-08-03 | `doc-track-audit` | `096f0f0` | 9/9 findings fixed, each proven before and after | 2 entries · 2 standing (was 1) · retired 0 · added 1 · R-001 fired |
| 2026-08-03 | `documentation-track` | `0ddd4e3` | 17/17 contracts · 12/12 findings verified | 2 entries · 1 standing (was 0) · retired 0 · added 1 |

The `Commit` column is what turns a stamp from a date into a navigable point in
history: `git show <sha>` is the run, and `git log <sha>..HEAD` is everything that
happened since a rule last fired.
