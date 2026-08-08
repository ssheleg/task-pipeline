# Pipeline retrospective — task-pipeline

One file per project, not per run. Written as the **last act of stage 10**:
**stamp first, then prune, then write** an entry **only if the run diverged**.
The order is not style — the cold-retirement trigger reads the stamp this stage
writes, so a prune placed ahead of it can never run on real data
(`learned.md` rule 21). Doctrine: `references/retrospective.md`.

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
| R-001 | 2026-08-03 · `documentation-track` | `dbe4f43` | When a check stays silent against a planted defect, **prove the plant landed in the text the check actually parses before touching the check.** | Two silent probes in one run: one was a bad probe (§9 correctly skips outside a git tree), one was a real bug (`$((0009))` is octal). The split is 50/50 here and was 4-of-5 probe-fault on the source project — guessing wrong costs a real bug or a false fix. | a probe harness exists that asserts the plant changed the parsed text, making this mechanical | 2026-08-08 | `68b4428` |
| R-002 | 2026-08-03 · `doc-track-audit` | `096f0f0` | When a batch of edits returns **any** error, re-verify **every** edit in that batch before reporting the batch done — not only the one that errored. | Two edits were issued together; the second failed the read-before-write check and was retried, the first was silently never applied. It was reported as done, shipped in v1.7.0, and surfaced only in a post-release audit as a question the grill never asks with a field in the brief waiting for the answer. | the harness reports per-edit outcomes in a form a check can read, or the edits are issued one per message | 2026-08-08 | `68b4428` |
| R-003 | 2026-08-05 · `artifact-hygiene` | `13028e9` | When you fix a defect in one check, guard or detector, **immediately run that defect's definition against its siblings** before moving on — the same file's other checks, and the other files that do the same job. | `learned.md` rule 6 says *sweep the class, not the instance*, and this is its **third** recorded failure to be applied to itself. 2026-08-03 `enforcement-audit`: a fix scoped to references→README while the same class lived in six other places. 2026-08-03 `root-cause`: nine findings, one missing matrix row. 2026-08-05: check 2's false-positive class was solved, and check 4 — its immediate sibling, in the same file, written in the same hour — shipped with the identical bug and fired on this run's own documents. Two instances were worth notes; `audit.md` says a class seen twice becomes a mechanism rather than a third ledger row. | a check can compare sibling detectors for a shared false-positive class — which needs the classes to be named in a machine-readable form first | 2026-08-08 | `68b4428` |
| R-004 | 2026-08-06 · `graph-staleness` | `2ce6ecc` | When a gate runs, the **next command must be conditional on its exit code** — never a gate and a commit in one block separated by newlines. | The hygiene gate returned FAIL and the `git commit` and `git push` beneath it ran anyway, because they were separate lines rather than a chain. The gate was read and not obeyed, which is indistinguishable in the transcript from a gate that passed. `learned.md` rule 11 makes the gate *return* the right code; nothing made the caller *use* it. | a harness or wrapper refuses to run a mutating command after a non-zero gate in the same block | 2026-08-08 | `68b4428` |
| R-005 | 2026-08-08 · `audit-followup`/M8 | `5726f7f` | When a change adds or widens a **check**, get an independent reader on it before merge — your own probes only exercise the shapes you already thought of. | M8 probed its new guard in four shapes and shipped it with a proven false-negative path: the ordered-list branch scanned the whole file and compared only the first pair, so a violation after a correct list was never examined. Two PR review passes found that, plus a live defect in the shipped `evidence-docs` navigator that **no pairwise shape could see by construction** — a table cell naming one act. Five probes written by the author found neither. This is not R-001 (that one doubts a silent probe); this is the probe being confident and complete about the wrong set. | a second reader — human or agent — is dispatched by a stage rather than by the repository happening to run a bot on PRs | 2026-08-08 | `5726f7f` |
| R-006 | 2026-08-08 · `audit-followup`/M2 | `44bdf53` | A finding is closed when the **behaviour** changes. Reporting the gap — a `dormant` line, a printed `skip`, a note beside the verdict — is honest and is **not** a fix; say which one you did. | The claim registry's number-word map stopped at forty-nine while the guard count was 130, so a word form above the ceiling was skipped **in silence**. The fix shipped was: print the unread tokens. That is a real improvement and the gap was untouched — a word-form claim above fifty was still skipped, now with a note. It was recorded as addressed and the next review round reopened it, correctly. `gates.md` already says a `dormant` state must be printed; nothing said that printing it does not discharge the finding. | a close-out records, per finding, whether the behaviour or only the reporting changed — and a check can read that field | 2026-08-08 | `44bdf53` |

Retire on **any** of: it became a check · every path/command it names is gone · it
has not fired in the last five run stamps, or in the last sixty days. At eleven
rows, the oldest never-fired
row goes — the cap is not negotiable, ranking is.

## Recent log — entries from the last five run stamps (newest first)

### 2026-08-08 · `audit-followup`/M7 · a one-directional check, in the repository whose rule 2 is both directions

**Symptom.** The module added a guard comparing the companion **matrix** against the
**preflight block** — the two places `companion-skills.md` states the same list. It
checked matrix → preflight and stopped.

`learned.md` rule 2 is *absence needs its own check: compute the mapping in **both**
directions*, and its incident is four fully-specified entities with no schema anywhere,
found only by the direction that felt redundant. The reverse here is a real failure with
its own shape: a preflight line whose companion the matrix never explains, so the operator
is asked to install something nobody told them the purpose of. It would have passed in
silence.

Three smaller ones in the same review, all in this change: a suffix strip that could never
match (the capture stopped at a space before the token it was meant to strip, so the code
looked like it handled *"Figma MCP"* and did nothing); `SKILL-CARD.md`'s **risk disclosure**
not naming the MCP this release adds — the page a reviewer reads *before* deciding to trust
the skill; and a stray space before a comma from appending a clause to a line that already
ended in a bold marker.

**Surfaced at:** stage 7, all four, by the review.

**Owned by:** stage 6 for the guard, stage 9 for the disclosure — that is a propagation
row, and the matrix in `docs/DOCMAP.md` names `SKILL-CARD.md` for a user-visible change but
not for a new **capability reference**, which is what an added MCP is.

**Root cause.** Writing a check exercises the parts of the doctrine you are thinking about.
This one was written while thinking about rule 20 — *a thing that exists twice* — which it
gets right. Rule 2 was not in view, and nothing brings it into view: `learned.md`'s table
is read at the stage that *binds* it, not at the moment a new check is being written.

**Fix, by grade.**
1. *(mechanical)* Both directions now computed and both probed — the reverse plant fails,
   which it did not before. The suffix strip is live. `SKILL-CARD.md` names
   `chrome-devtools` **with what makes it different**: it drives a real browser, opens
   pages, runs scripts in them and reads console and network traffic. A reviewer deciding
   whether to trust the skill needs that, not the bare name.
2. *(note, expires in two runs)* `docs/DOCMAP.md`'s propagation matrix has no row for
   *adding a capability reference* (an MCP, a tool the doctrine names) as distinct from a
   user-visible capability. That is why `SKILL-CARD.md` was not walked.

**Standing instruction: none added, deliberately.** R-005 already requires an independent
reader on a change that adds or widens a check, it fired, and the reader is what found all
four. The gap is not that the rule went unread — it is that `learned.md`'s own table is not
consulted **while writing** a check, and that is one instance of rule 2 rather than a new
class. A seventh row for a variant of an existing rule is how a capped list stops being
read.

**The check that catches it next time:** nothing mechanical for the general case. For this
instance, the guard's own bidirectional probe, and the matrix note above.


### 2026-08-08 · `audit-followup`/M2 · a limit made visible, reported as a limit removed

**Symptom.** Review round two found that the claim registry's number-word map stopped at
forty-nine while the guard count it checks was already 130 — so any claim written as a word
above the ceiling would be **skipped without a word**. The fix shipped was to collect
unparseable tokens and print them beside the verdict, and the finding was recorded as
addressed.

It was not. A word-form claim of *"fifty-two files under `references/`"* was still skipped;
it now merely said so. Review round three reopened it, and the probe settled it: that exact
string is caught today and was not caught then.

**Surfaced at:** stage 7, by the review, twice — once to open it and once to reject the fix.

**Owned by:** stage 6. That is where a fix is supposed to be proven, and where "proven" was
allowed to mean *the gap is now visible* rather than *the gap is gone*.

**Root cause.** `gates.md` is emphatic that a `dormant` or `skip` state must be **printed** —
a mechanism that reports nothing when it looked at nothing is the false success the whole
file is about. That doctrine is correct and it was followed. What no line said is that
printing the gap does not **discharge** the finding. Having done the honest thing, it was
easy to record it as the whole thing.

The three review rounds together found thirteen issues; the module's own five probes found
none of them. That is the second consecutive module with that count, and it is exactly what
`R-005` was added for one release ago — it fired, it was followed, and it does not make the
probes better, because a probe is written from the same model of the problem as the check.

**Fix, by grade.**
1. *(mechanical)* The map now runs through ninety, and the lift was probed against the case
   that exposed it. The eval-runs row was the only one of six bypassing the shared
   digit-and-word matcher — a false negative on the very incident the registry is named
   after — and now uses it.
2. *(mechanical)* `CONTRIBUTING.md` invariant 13 still described the pre-registry single
   check while invariant 35 described the registry: two invariants over one guard, one
   stale. 13 now points at 35 and names no surfaces of its own.
3. *(standing instruction)* **R-006** — a finding is closed when the behaviour changes;
   reporting the gap is honest and is not a fix, and the close-out says which one happened.

**The check that catches it next time:** none, yet — and that is the retirement condition
written into R-006. When a close-out records per finding whether behaviour or only reporting
changed, a check can read that field and the instruction leaves.


### 2026-08-08 · `audit-followup`/M8 · five probes that all passed, and the two defects they could not see

**Symptom.** The change that widens rule 21's guard from one file to the class shipped to
review with two defects its own verification could not detect.

(a) **A proven false-negative path.** The ordered-list branch scanned the whole file and
compared only the *first* prune/stamp pair. A violating list placed after a correct one
was never examined. Four planted-defect probes passed, because every one of them planted
its defect as the first pair.

(b) **A shape with no pair at all.** `evidence-docs/SKILL.md` still taught *"prune first,
cap of ten"* in a table cell. Every shape written so far compares **two** act words;
a cell that
names one is invisible to all of them **by construction**, not by oversight. It was live
in the shipped skill and no probe could have found it, because a probe tests the predicate
you wrote.

**Surfaced at:** stage 7, both — by the PR review bot, on two separate passes.

**Owned by:** stage 6. That is where a new check is supposed to be proven, and where
"proven" was defined as *the probes I wrote pass*.

**Root cause.** A probe is written by whoever wrote the check, from the same model of the
problem. It proves the check catches what its author imagined and is silent about the rest
— which is exactly the failure mode `gates.md` names for a green nobody watched fail,
one level up: here the check *was* watched failing, five times, on five shapes its author
had thought of.

The run also produced three defects in its own **prose** — a surface count stated five
different ways, a 225-character line against this repo's own ~80 rule, and an acceptance
verdict contradicting the ledger it summarised. Those are the same class this release
fixes, committed while describing the fix.

**Fix, by grade.**
1. *(mechanical)* P3 moved inside the paragraph loop — scoped to one list block, **every**
   adjacent pair compared, history exemption computed once per paragraph including the
   preceding one. P5 added for the lone directive. Four negative self-tests; floor 120 → 124.
2. *(mechanical)* Every count deleted rather than corrected. The guard's `SCOPE` comment
   now states what it does **not** cover, and invariant 34 points at that comment instead
   of restating the shape count, so the two cannot disagree.
3. *(standing instruction)* **R-005** — an independent reader on any change that adds or
   widens a check. This is the one thing above that no check can decide.

**Axis, measured rather than felt.** `test/validate.py` was edited three times for the
same reason, which is the loop guard's trigger. Split, the two axes disagree: the guard's
shapes gave 5 new findings and 0 self-inflicted (still paying); the run's own prose gave 3
findings and 3 self-inflicted (exhausted). Lumping them would have stopped the half that
was working and continued the half that was not.

**The check that catches it next time:** for (a) and (b), the four new negative self-tests
plus the stated scope. For the class — a check written from its author's own model — there
is none, and that is what R-005 is for.


### 2026-08-08 · `audit-followup` / M1 · a rule fixed in one file of nine, and the wrong copy edited while fixing it

**Symptom.** Three, and the ordering between them is the finding.

(a) **Rule 21 shipped in `v1.23.0` and reached one file.** It changed the retro's act
order to *stamp first* in `references/retrospective.md`; `SKILL.md` (twice),
`acceptance.md` (three places), `stages.md` (three places), `templates/retro.md`,
`templates/README.md` and this repository's own `retro.md` header still said *prune
first* — the exact deadlock the rule defines. `SKILL.md` is what an agent loads first,
so the shipped skill's most-read surface taught the failure its newest rule documents.
The rule-21 guard exists and checks **one file**.

(b) **The version-sync invariant was named `four-way` on four surfaces while
`test/validate.py` enforced five.** `CONTRIBUTING.md` was substantively right — it named
`SKILL-CARD.md` in a following sentence — and still called the set four. `CLAUDE.md` did
not know the fifth surface at all. It surfaced when the release bump failed the guard.

(c) **While fixing (b), the run edited the wrong copy** — `~/CLAUDE.md` instead of
`./CLAUDE.md` — in a change whose subject is *a rule written in two documents is two
rules*.

**Surfaced at:** (a) stage 5, by R-003's sibling sweep, triggered by reading rule 21's
guard to learn where rules 17–21 bind. (b) stage 7, by the validator, on the version
bump. (c) immediately, as a failed edit.

**Owned by:** stage 9 for (a) and (b) — both are propagation. The `DOCMAP.md` matrix has
a row for *"a new document, rule or guard"* naming `SKILL.md`, the README, the manifest
and the Cursor rule; it has **no row for a change to an existing rule's ordering or
contract**, which is why v1.23.0 walked a matrix that did not ask about `acceptance.md`
or `stages.md`. (c) is stage 5 and cost nothing.

**Root cause.** A guard written *per rule* rather than *per class*. Rules 16–21 each got
a bespoke guard naming its consumer files by literal string. That catches a consumer
dropping a citation and cannot catch **a consumer that keeps the citation and contradicts
it** — which is exactly (a): every one of those eight surfaces still cites
`retrospective.md`, and every one states the opposite of what it says.

(c) is different in kind and worth separating: it failed *loudly*. `~/CLAUDE.md` did not
contain the string, so the edit errored instead of landing. Had both files contained it,
the run would have edited the wrong one and reported success — the silent half of the
same class, and the one R-002 exists for.

**Fix, by grade.**
1. *(mechanical, deferred to M8 with its own branch)* Widen the rule-21 guard from one
   file to the class: any surface stating the retro's three acts must state them in the
   order `retrospective.md` states them, compared **mechanically against that file**
   rather than against a literal, so the guard cannot drift from the doctrine it guards.
2. *(mechanical, this change)* Every counted name that undercounts its own list, removed
   rather than corrected — `four-way` and `fifteen rules` both became descriptions. A
   name that counts is a number, and it drifts like one.
3. *(note, expires in two runs)* `docs/DOCMAP.md`'s propagation matrix has no row for
   *changing an existing rule's ordering or contract*, as opposed to adding one. M8 adds it.

**Standing instruction:** none added. R-003 already names this class and **fired
correctly** — it is what found (a). The failure was not that the rule went unread; it was
that the *guard* for rules 17–21 was built per-instance. That is a mechanical fix, so it
belongs in a script (grade 1), not as a fifth row on a capped list.

**The check that catches it next time:** M8's class-comparison guard for (a); the
existing version-sync guard already caught (b) and is why it was found at all; (c) stays
`learned.md` rule 20's territory — *read the consumer to learn which copy ships* — and
`R-002`'s, both stamped as fired.

### 2026-08-06 · `carried-in-claims` · an exit code read through a pipe, and an edit that failed silently

**Symptom.** Two slips inside the change that adds rule 16, both of them the shape
rule 16 is about — believing a report instead of measuring.
(a) A planted-defect run was piped to `tail -2` and `$?` was read afterwards, so the
recorded status was `tail`'s. It printed `planted rc=0 (want non-zero)` while the
validator had in fact returned `1`; the guard was working and the measurement of it
was not.
(b) A python heredoc that inserted the new workflow step raised `ValueError` and
wrote nothing. The step count printed `119` — unchanged — and the failure was
visible only because the next command grepped for the inserted text.

**Surfaced at:** stage 6, both — (a) by re-running the same command without the pipe,
(b) by `grep -c` on the string that was supposed to have landed.

**Owned by:** stage 6. Both were verification steps that reported on themselves.

**Root cause.** `$?` after a pipeline is the last element's status, and a heredoc
that throws still exits the surrounding block cleanly enough to look like a write.
Neither is obscure; both are invisible unless the *result* is checked rather than the
*command*.

**Fix.** (a) Re-measured with `cmd >/dev/null 2>&1; echo $?` — `1` planted, `0` clean.
(b) Re-inserted with `cat >>` and confirmed by grep and by `yaml.safe_load`.

**Standing instruction:** none added. `R-004` already carries this class — *a gate's
exit code must govern what runs next* — and (a) is the same rule one step earlier:
the code you read must be the one you meant. Adding a fifth row for a variant of an
existing rule is how a capped list stops being read. Stamped `R-004` as fired.

**The check that catches it next time:** for (b), the negative self-test added in
this release fails when a consumer file loses its citation, which is what a silently
skipped insertion produces. For (a), nothing mechanical — it is `R-004`'s territory
and stays a review question.

### 2026-08-06 · `graph-staleness` · a guard green because it never looked, and a marker with four spellings

**Symptom.** Two independent failures, both inside the release that names their class.
(a) The new guard requiring the canonical distrust marker compared **per line**; this
doctrine wraps at ~80 columns, so in `README.md` and `stages.md` — where the marker is
split across two lines — it matched nothing and printed `PASS`. (b) The marker itself
was written four ways in one PR: absent from the doctrine's own three worked examples,
a second spelling (*"treat as stale until refreshed"*) in the `unresolvable` row, and
the sigil dropped in the Cursor rule and the config.

**Surfaced at:** stage 5 — (a) by probing the guard with a planted wrapped defect,
(b) by the PR review, which found one instance.

**Owned by:** stage 5 for both. (a) is the guard's own construction; (b) is the edit
that introduced the marker and did not sweep its own siblings unprompted.

**Root cause.** (a) A check whose predicate is *"the needle is on this line"* silently
assumes the source is not wrapped — and the one thing certain about this repository's
prose is that it wraps at ~80. The guard's own green was the only evidence anyone had
that it worked, which is the definition in `gates.md` → *False success*. (b) A marker
is a **string**, and its value is entirely that one grep finds every occurrence; four
spellings is not four styles, it is zero markers.

**Fix, by grade.**
1. *(mechanical)* The marker guard now normalises whitespace before counting — probed
   with a planted wrapped defect and watched rejecting it.
2. *(mechanical)* Hygiene **check 7** — a blank line inside a GFM table. The class hit
   **five** times in this run, and on the check's first armed pass it found three more
   in the v1.12.0 and v1.13.0 carry-over ledgers, which had been rendering broken since
   the day they were written. All eight fixed, none baselined behind a floor.
3. *(mechanical)* An undeclared hygiene floor is a failure rather than a zero: check 7
   shipped without `HYGIENE_FLOOR_7` and printed `ok … (floor )` over three real hits.
4. *(mechanical)* The guard count stopped being restated in prose at all — third
   hand-correction in one run, and the guard's message had always offered *derive or
   delete*.
5. *(standing instruction)* **R-004** — a gate's exit code must gate the next command.

**The check that catches each from now on:** negatives *"the distrust marker keeps its
sigil, even wrapped"*, *"the distrust marker gets no second spelling"*, *"the hygiene
gate catches a blank line inside a table"*, *"the hygiene gate refuses an undeclared
floor"*.

**What R-003 was worth, measured:** review found **1** of the four marker spellings.
Running its definition against the siblings found the other **3**. The instruction did
three quarters of the work on this run.


## Releases that carry no stamp — stated, not stamped

Ten consecutive releases, **`v1.16.0` through `v1.23.0`**, shipped without a run of this
pipeline: no brief, no spec, no acceptance, no stamp. Measured, not recalled —

```bash
git tag -l 'v1.*' --sort=-v:refname | while read -r t; do
  s=$(git rev-list -n1 "$t" | cut -c1-7)
  grep -q "$s" docs/superpowers/retro.md || echo "$t $s no stamp"
done
```

**No stamps were written for them, deliberately.** A stamp asserts that a run happened and
that its gates were walked. Writing ten to make the table look continuous would be the exact
defect this file exists to catch, on the file that catches it. The gap is recorded here
instead, which is the honest form of the same information.

Two consequences worth stating rather than leaving to be rediscovered:

- **The cold-retirement trigger was unreadable across that stretch.** It counts firings
  across the last five run stamps, and the counter moved four times in fourteen releases. It
  was not strict or lenient — there was nothing to read. That is why the condition now carries
  a second unit, sixty days, which nothing can stall
([`references/retrospective.md`](../../plugins/task-pipeline/skills/task-pipeline/references/retrospective.md)).
- **The lessons of those ten releases are in `CHANGELOG.md` and nowhere else.** They are not
  lost, and they are not where the next run's stage 0 looks. Rules 17–21 of `learned.md` were
  all earned in that stretch and reached the shipped doctrine directly, without passing
  through a retro — which is why five of them sat outside the *Where these bind* map until
  `v1.23.1` found it.

## Run stamps

One line per run, appended at stage 10. This is what makes "five runs" countable
— without it the cold-rule is a guess and the prune becomes a mood.

| Date | Topic | Commit | Verdict | Retro |
|---|---|---|---|---|
| 2026-08-08 | `audit-followup` / M7 `rendered-surface-check` | `b524680` | 1 REQ · a companion wired into stages 5–6 and 8 · **one review round, 4 findings, all mine, none found by my own probes** · carry-over 9 rows, 6 open, 0 unresolved | 1 entry · 6 standing · retired 0 · added 0 · R-005 and R-006 both fired · guards 130 → 131 |
| 2026-08-08 | `audit-followup` / M2 `claim-registry` | `44bdf53` | 1 REQ + carry-over row 7 · six claim classes, each armed · **three review rounds, 13 findings, none of them found by the module's own probes** · carry-over 9 rows, 6 open, 0 unresolved | 1 entry · **6 standing (was 5)** · retired 0 · added 1 (R-006) · R-001, R-002, R-003, R-004, R-005 all fired · guards 124 → 130 |
| 2026-08-08 | `audit-followup` / M8 `prune-order-sweep` | `5726f7f` | 1 REQ · verified against a check seen failing **five** ways · PR #10, two review passes, 6 findings confirmed of which 3 new · carry-over 9 rows, 0 unresolved, row 4 closed | 1 entry · **5 standing (was 4)** · retired 0 · added 1 (R-005) · R-001 fired 5× · R-002, R-003, R-004 all fired · guards 120 → 124 |
| 2026-08-08 | `audit-followup` / M1 `truth-restore` | `68b4428` | 7 REQ · 6 verified by a proven check · 1 deferred to M8 (REQ-013, added mid-run) · carry-over 6 rows, 0 unresolved, 1 resolved · graph 27 commits stale → 0 | 1 entry · 4 standing · retired 0 · added 0 · **all four fired** · guards 120 |
| 2026-08-06 | `graph-staleness` | `2ce6ecc` | 13 REQ · 12 verified · 1 deferred (tag, by operator decision) | 1 entry · 4 standing (was 3) · retired 0 · added 1 · R-001, R-002, R-003 all fired |
| 2026-08-05 | `false-success` | `348357e` | 10 REQ · 9 verified by a proven check · 1 `review` (the Cursor rule, per the matrix) · carry-over 1 row, 0 unresolved | 2 entries · 3 standing · retired 0 · added 0 · **R-001, R-002 and R-003 all fired** · guards 80 → 95 |
| 2026-08-05 | `spec-plan-quality` | `e9123c6` | 11 REQ · 8 verified by a proven check · 3 carrying an explicit `review` half · carry-over 5 rows, 0 unresolved, 1 printed exclusion | **no divergence** · 3 standing · retired 0 · added 0 · **R-003 fired on its first run** (asked of `planning.md`, answered "no", recorded) · guards 76 → 80 |
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
