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
| R-001 | 2026-08-03 · `documentation-track` | `dbe4f43` | When a check stays silent against a planted defect, **prove the plant landed in the text the check actually parses before touching the check.** | Two silent probes in one run: one was a bad probe (§9 correctly skips outside a git tree), one was a real bug (`$((0009))` is octal). The split is 50/50 here and was 4-of-5 probe-fault on the source project — guessing wrong costs a real bug or a false fix. | a probe harness exists that asserts the plant changed the parsed text, making this mechanical | 2026-08-03 | `dbe4f43` |

Retire on **any** of: it became a check · every path/command it names is gone · it
has not fired in the last five run stamps. At eleven rows, the oldest never-fired
row goes — the cap is not negotiable, ranking is.

## Recent log — entries from the last five run stamps (newest first)

Older entries and every retirement **move** to `docs/superpowers/retro/YYYY-QN.md`
at the prune. Moving is not deleting: the archive is append-only and holds the
incident forever, so pruning the in-force list costs no knowledge.

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
| 2026-08-03 | `documentation-track` | `0ddd4e3` | 17/17 contracts · 12/12 findings verified | 2 entries · 1 standing (was 0) · retired 0 · added 1 |

The `Commit` column is what turns a stamp from a date into a navigable point in
history: `git show <sha>` is the run, and `git log <sha>..HEAD` is everything that
happened since a rule last fired.
